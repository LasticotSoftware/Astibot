import cbpro
from cbpro.public_client import PublicClient

class GDAXCurrencies:

    @staticmethod
    def get_all_pairs():
        clientPublic = cbpro.PublicClient()
        products = clientPublic.get_products()
        return sorted(list(map(lambda x: x["id"], products)))

    @staticmethod
    def get_currencies_list():
        pairs = GDAXCurrencies.get_all_pairs()
        product_map = []

        for pair in pairs:
            pieces = pair.split('-')
            product_map.append({
                "full": pair,
                "coin": pieces[0],
                "fiat": pieces[1]
            })

        return product_map

    @staticmethod
    def get_index_for_currency_pair(pair):
        return GDAXCurrencies.get_all_pairs().index(pair)
