import requests

class XWingAPI:

    def __init__(self, base_url):
        self.cache = {}
        self.cards = []
        self.base_url = base_url

    def get_card(self, tag):
        filters = {
            'type': ('get_upgrade_type', 'name'),
            'faction': ('get_faction', 'canonical')
        }
        cards = filter(lambda c: self.compare(tag['card'], c), self.get_cards())
        filtered_cards = cards

        for filter_type, (getter, cmp_prop) in filters.iteritems():
            if tag[filter_type]:
                def filter_func(c):
                    if filter_type in c:
                        obj = None
                        if type(c[filter_type]) == dict:
                            obj = c[filter_type]
                        else:
                            obj = getattr(self, getter)(c[filter_type])
                        if obj:
                            return self.compare(tag[filter_type], obj, cmp_prop)

                    return False

                filtered_cards = filter(filter_func, filtered_cards)
            
        if len(filtered_cards) > 0:
            return filtered_cards

        return cards

    def get_cards(self):
        if len(self.cards) == 0:
            self.cards = self.get_pilots() + self.get_upgrades()
        return self.cards

    def get_objs(self, obj_type, url = None):
        url = url if url else obj_type
        if obj_type not in self.cache:
            r = requests.get(self.base_url + url)
            self.cache[obj_type] = r.json()
        return self.cache[obj_type]

    def get_pilots(self):
        return self.get_objs('pilot')

    def get_ships(self):
        return self.get_objs('ship')

    def get_ship(self, id):
        ships = filter(lambda s: s['id'] == id, self.get_ships())
        if len(ships) > 0:
            return ships[0]
        else:
            return False

    def get_upgrade_types(self):
        return self.get_objs('upgrade/type')

    def get_upgrade_type(self, id):
        types = filter(lambda s: s['id'] == id, self.get_upgrade_types())
        if len(types) > 0:
            return types[0]
        else:
            return False

    def get_factions(self):
        return self.get_objs('faction')

    def get_faction(self, id):
        factions = filter(lambda f: f['id'] == id, self.get_factions())
        if len(factions) > 0:
            return factions[0]
        else:
            return False

    def get_upgrades(self):
        return self.get_objs('upgrade')

    def compare(self, name, card, prop = 'name'):
        return card[prop].lower() == name.lower()
