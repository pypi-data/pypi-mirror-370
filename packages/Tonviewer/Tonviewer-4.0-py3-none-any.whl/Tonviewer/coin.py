from .Scraping import Scraping

class Coin:
    def __init__(self, coin: str):
        self.coin = coin
        self.scraper = Scraping()

    def price(self):
        print(self.scraper.get_coingecko_price(self.coin))

    def about(self):
        print(self.scraper.getCoingeckoAbout(self.coin))



            




