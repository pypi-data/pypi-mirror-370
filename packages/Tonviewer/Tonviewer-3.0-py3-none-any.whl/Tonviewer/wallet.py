from .Scraping import Scraping

class Wallet:
    def __init__(self, wallet: str):
        self.wallet = wallet
        self.scraper = Scraping()

    def balance(self):
        print(self.scraper.get_tonviewer(self.wallet))

    def transactions(self , limit: int=1):
        print(self.scraper.get_transactions(self.wallet , limit))





