from itertools import product
from data_collector import BeerCollection
from multilang import beer_card_text, no_beer

_abv = ["No Alco", "Low", "Mid", "High"]
_ibu = ["Low", "Mid", "High"]
beer_combinations_list = []
for c in list(product(_abv, _ibu)):
    beer_combinations_list.append(f"{c[0]}-{c[1]}")


def get_beer_card(abv, ibu, language):

    if abv != 'No Alco':
        result = BeerCollection.get_random_beer(abv, ibu)
    else:
        result = BeerCollection.get_non_acl_beer()

    if result is not None:
        beer_card = f"{result['beer_url']}\n" \
                    f"<b>{beer_card_text['beer_name'][language]}:</b> {result['beer_name']}\n" \
                    f"<b>{beer_card_text['brewery_name'][language]}:</b> {result['brewery_name']}\n" \
                    f"<b>{beer_card_text['beer_type'][language]}:</b> {result['beer_type']}\n" \
                    f"<b>{beer_card_text['beer_abv'][language]}:</b> {result['beer_abv']}\n" \
                    f"<b>{beer_card_text['beer_ibu'][language]}:</b> {result['beer_ibu']}\n" \
                    f"<b>{beer_card_text['global_rating_score'][language]}:</b> {result['global_rating_score']}"
    else:
        beer_card = no_beer[language]

    return beer_card
