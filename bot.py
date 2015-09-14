import praw
import requests
import re

import config

reddit = praw.Reddit(config.user_agent)
reddit.login(config.username, config.password, disable_warning=True)
sub = reddit.get_subreddit(config.subreddit)
posts = sub.get_hot(limit=config.post_limit)

class XWingAPI:

    def __init__(self, base_url):
        self.pilots = []
        self.upgrades = []
        self.cards = []
        self.base_url = base_url
    
    def get_card(self):
        pass
    
    def get_cards(self):
        if len(self.cards) == 0:
            self
    def get_pilots(self):
        if len(self.pilots) == 0:
            r = requests.get(self.base_url + '/pilot')
            self.pilots = r.json()
        return self.pilots
    
    def get_upgrades():
        if len(self.upgrades) == 0:
            r = requests.get(self.base_url + '/upgrade')
            self.upgrades = r.json()
        return self.upgrades

def replied_to(obj):
    replies = []
    if type(obj) == praw.objects.Comment:
        replies = obj.replies
    elif type(obj) == praw.objects.Submission:
        obj.comments
    else:
        raise TypeException('Object not submission or comment')
        
    return any(reply.author.name == config.username for reply in replies)
    
def own_comment(comment):
    return comment.author.name == config.username

def parse_text(text):
    r = re.compile('\[\[[^\]]+\]\]')
    return [s.strip('[]').strip() for s in r.findall(text)]

upgrades = []

def get_card(name):
    pilots = get_pilots()
    cards = filter(lambda p: p.name == name, pilots)
    if len(cards) > 0:
        return cards[0]
    
    upgrades = get_upgrades()
    cards = filter(lambda u: u.name == name, upgrades)
    if len(cards) > 0:
        return cards[0]
    
    return null

for post in posts:
    if not replied_to(post):
        card_names = parse_text(post.selftext)
        for name in card_names:
            print get_card(name)
        
    for comment in praw.helpers.flatten_tree(post.comments):
        if not replied_to(comment) and not own_comment(comment):
            cards = parse_text(comment.body)
            for name in card_names:
                print get_card(name)
