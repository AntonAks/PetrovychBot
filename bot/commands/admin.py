from db import User


def get_users():
    users = User.get_all_users()
    str_result = f"First 20 users. All quantity: {len(users)}\n"
    for user in users[:20]:
        str_result += f"{user['user_name']} - {user['user_id']} \n"

    return str_result
