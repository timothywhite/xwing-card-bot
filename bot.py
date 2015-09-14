import praw
import requests
import re

import config

class XWingAPI:

    def __init__(self, base_url):
        self.pilots = []
        self.upgrades = []
        self.cards = []
        self.base_url = base_url
    
    def get_card(self, name):
        cards = filter(lambda c: self.compare(name, c), self.get_cards())
        if len(cards) > 0:
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
    
    def get_upgrades(self):
        if len(self.upgrades) == 0:
            r = requests.get(self.base_url + '/upgrade')
            self.upgrades = r.json()
        return self.upgrades
    
    def compare(self, name, card):
        return card['name'].lower() == name.lower()
    
class XWingTMGCardBot:
    
    def __init__(self, config):
        self.reddit = praw.Reddit(config.user_agent)
        self.reddit.login(config.username, config.password, disable_warning=True)
        
        self.api = XWingAPI(config.api_base_url)
        
        self.sub = self.reddit.get_subreddit(config.subreddit)
        self.posts = self.sub.get_hot(limit=config.post_limit)
        
    def replied_to(self, obj):
        replies = []
        if type(obj) == praw.objects.Comment:
            replies = obj.replies
        elif type(obj) == praw.objects.Submission:
            obj.comments
        else:
            raise TypeException('Object not submission or comment')
            
        return any(reply.author.name == config.username for reply in replies)
    
    def own_comment(self, comment):
        return comment.author.name == config.username
    
    def parse_text(self, text):
        r = re.compile('\[\[[^\]]+\]\]')
        return [s.strip('[]').strip() for s in r.findall(text)]
    
    def mash_go(self):
        for post in self.posts:
            if not self.replied_to(post):
                card_names = self.parse_text(post.selftext)
                for name in card_names:
                    print self.api.get_card(name)['text']
            
            for comment in praw.helpers.flatten_tree(post.comments):
                if not self.replied_to(comment) and not self.own_comment(comment):
                    card_names = self.parse_text(comment.body)
                    for name in card_names:
                        print self.api.get_card(name)['text']

bot = XWingTMGCardBot(config)
bot.mash_go()

