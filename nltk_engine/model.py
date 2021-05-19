import json
import os
import numpy as np
import torch
import torch.nn as nn
import boto3
import settings
from random import choice
from torch.utils.data import Dataset, DataLoader
from nltk_engine import tokenize, stem, bag_of_words

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "train_data.pth")

data = torch.load(DATA_FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
model_state = data["model_state"]
all_words = data['all_words']
tags = data['tags']


class NeuralNet(nn.Module):

    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out


def train(short_talk_dict):

    all_words = []
    tags = []
    xy = []

    for key in short_talk_dict.keys():
        tags.append(key)

        for phrase in short_talk_dict[key]['phrase']:
            w = tokenize(phrase)
            all_words.extend(w)
            xy.append((w, key))

    ignore_words = ['?', '!', '.', ',']
    all_words = [stem(w) for w in all_words if w not in ignore_words]
    all_words = sorted(set(all_words))
    tags = sorted(set(tags))

    x_train = []
    y_train = []

    for (pattern_sentence, tag) in xy:
        bag = bag_of_words(pattern_sentence, all_words)
        x_train.append(bag)

        label = tags.index(tag)
        y_train.append(label)

    x_train = np.array(x_train)
    y_train = np.array(y_train)

    class ChatDataset(Dataset):

        def __init__(self):
            self.n_samples = len(x_train)
            self.x_data = x_train
            self.y_data = y_train

        def __getitem__(self, index):
            return self.x_data[index], self.y_data[index]

        def __len__(self):
            return self.n_samples

    # Hyper-parameters
    num_epochs = 1000
    learning_rate = 0.001
    batch_size = 8
    hidden_size = 8
    output_size = len(tags)
    input_size = len(x_train[0])

    dataset = ChatDataset()
    train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = NeuralNet(input_size, hidden_size, output_size).to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Train the model
    for epoch in range(num_epochs):
        for (words, labels) in train_loader:
            words = words.to(device)
            labels = labels.to(dtype=torch.long).to(device)

            # Forward pass
            outputs = model(words)
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    print(f'final loss: {loss.item():.4f}')

    data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "all_words": all_words,
        "tags": tags
    }


    torch.save(data, DATA_FILE)

    print(f'training complete. file saved to {DATA_FILE}')


def get_answer(message_text):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    s3 = boto3.resource('s3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                        )

    short_talks_obj = s3.Object(settings.AWS_S3_BUCKET_NAME, "short_talks.json")
    body = short_talks_obj.get()['Body'].read().decode("utf-8")
    intents = json.loads(body)

    sentence = tokenize(message_text)
    x = bag_of_words(sentence, all_words)
    x = x.reshape(1, x.shape[0])
    x = torch.from_numpy(x).to(device)

    output = model(x)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        return choice(intents[tag]['answer'])
    else:
        return choice(intents['Unknown']['answer'])

