import requests

class XWingAPI:

    def __init__(self, base_url):
        self.pilots = []
        self.upgrades = []
        self.cards = []
        self.ships = []
        self.types = []
        self.base_url = base_url
    
    def get_card(self, tag):
        cards = filter(lambda c: self.compare(tag[0], c), self.get_cards())
        if len(cards) > 0:
            if tag[1] != '':
               uCards = filter(lambda c: self.compare(tag[1], self.get_upgrade_type(c['type'])) if 'type' in c else False, cards)
               if len(uCards) > 0:
                   return uCards[0]
            
            return cards[0]
        else:
            return False
    
    def get_cards(self):
        if len(self.cards) == 0:
            self.cards = self.get_pilots() + self.get_upgrades()
        return self.cards
    
    def get_pilots(self):
        if len(self.pilots) == 0:
            r = requests.get(self.base_url + '/pilot')
            self.pilots = r.json()
        return self.pilots
    
    def get_ships(self):
        if len(self.ships) == 0:
            r = requests.get(self.base_url + '/ship')
            self.ships = r.json()
        return self.ships
    
    def get_ship(self, id):
        ships = filter(lambda s: s['id'] == id, self.get_ships())
        if len(ships) > 0:
            return ships[0]
        else:
            return False
    def get_upgrade_types(self):
        if len(self.types) == 0:
            r = requests.get(self.base_url + '/upgrade/type')
            self.types = r.json()
        return self.types

    def get_upgrade_type(self, id):
        types = filter(lambda s: s['id'] == id, self.get_upgrade_types())
        if len(types) > 0:
            return types[0]
        else:
            return False
    def get_upgrades(self):
        if len(self.upgrades) == 0:
            r = requests.get(self.base_url + '/upgrade')
            self.upgrades = r.json()
        return self.upgrades
    
    def compare(self, name, card):
        return card['name'].lower() == name.lower()
