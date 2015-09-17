import praw
import re

import config
from xwingapi import XWingAPI

class XWingTMGCardBot:

    def __init__(self, config):
        self.reddit = praw.Reddit(config.user_agent)
        self.reddit.set_oauth_app_info(client_id=config.client_id,
                                       client_secret=config.client_secret,
                                       redirect_uri=config.redirect_uri)
        access_information = self.reddit.refresh_access_information(config.refresh_token)
        self.reddit.set_access_credentials(**access_information)

        self.api = XWingAPI(config.api_base_url)

        self.sub = self.reddit.get_subreddit(config.subreddit)
        self.posts = self.sub.get_hot(limit=config.post_limit)

        self.stats =  ['skill', 'attack', 'energy', 'range', 'agility', 'hull', 'shield', 'points']

        self.card_limit = config.card_limit
        self.debug = config.debug

    def replied_to(self, obj):
        replies = []
        if type(obj) == praw.objects.Comment:
            replies = obj.replies
        elif type(obj) == praw.objects.Submission:
            replies = obj.comments
        else:
            raise TypeException('Object not submission or comment')

        return any(reply.author.name == config.username for reply in replies)

    def own_comment(self, comment):
        return comment.author.name == config.username

    def parse_text(self, text):
        tagRe = '\[\[([^\]]*)\]\]'
        def parse_tag(tag_text):
            subtags = {
                'type': '\(\(([^\)]*)\)\)',
                'faction': '\{\{([^\}]*)\}\}'
            }
            tag = {}
            card = re.sub(tagRe, r'\1', tag_text)
            card = reduce(lambda p, st: re.sub(subtags[st], '', p), subtags.keys(), card)
            card = card.strip()
            tag['card'] = card
            for subtag_type, r in subtags.iteritems():
                match = re.search(r, tag_text)
                if match:
                    tag[subtag_type] = re.sub(r, r'\1', match.group()).strip()
                else:
                    tag[subtag_type] = None

            return tag

        return [parse_tag(t) for t in re.findall(tagRe, text)]

    def get_statline(self, card):
        statline = {}
        for stat in self.stats:
            val = ''
            if stat in card and card[stat] is not None:
                val = str(card[stat])
            if val is '' and 'ship' in card:
                ship = self.api.get_ship(card['ship'])
                val = str(ship[stat])
            if val != '' and (stat != 'energy' or val != '0') and (stat != 'range' or val != '1-3'):
                statline[stat] = val

        return statline
    def render_card_text(self, card):
        replacements = { '{STRONG}|{/STRONG}' : '**', '{EM}|{/EM}' : '*', '{BR}' : '' }
        text = card['text']
        for pattern, repl in replacements.iteritems():
            text = re.sub(pattern, repl, text)

        return text

    def render_card(self, card):
        ret = '**Name:** ' + card['name'] + '\n\n'
        statline = self.get_statline(card)

        card_type = ''
        if type(card['type']) is dict:
            card_type = card['type']['name']
        else:
            card_type = self.api.get_upgrade_type(card['type'])['name']
        ret += '**Type:** ' + card_type.capitalize() + ' '

        for stat in self.stats:
            if stat in statline and (stat != 'energy' or statline[stat] != '0'):
                ret += '**' + stat.capitalize() + ':** ' + statline[stat] + ' '
        ret += '\n\n'

        ret += self.render_card_text(card)
        return ret

    def get_text(self, obj):
        if type(obj) == praw.objects.Comment:
            return obj.body
        elif type(obj) == praw.objects.Submission:
            return obj.selftext
        else:
            raise TypeException('Object not submission or comment')

    def get_cards(self, tags):
        cards = [self.api.get_card(t) for t in tags] #get cards
        cards = [c for ca in cards for c in ca] #flatten card list
        cards = [i for n,i in enumerate(cards) if i not in cards[n+1:]] #remove duplicates
        cards = sorted(cards, key=lambda c: c['name']) #sort by name

        return cards[:self.card_limit]

    def build_comment(self, post):
        comment = ''
        tags = self.parse_text(self.get_text(post))
        cards = self.get_cards(tags)

        for index, card in enumerate(cards):
            comment += self.render_card(card)
            if index != len(cards) - 1:
                comment += '\n\n&nbsp;\n\n---\n\n&nbsp;\n\n'

        if comment != '':
            comment += '\n\n&nbsp;\n\n Am I popping too much Glitterstim? Message /u/forkmonkey88'

        return comment

    def post_comment(self, obj, comment):
        if self.debug:
            print comment
            return

        if type(obj) == praw.objects.Comment:
            return obj.reply(comment)
        elif type(obj) == praw.objects.Submission:
            return obj.add_comment(comment)
        else:
            raise TypeException('Object not submission or comment')

    def mash_go(self):
        for post in self.posts:
            try:
                if not self.replied_to(post):
                    comment = self.build_comment(post)
                    if comment:
                        self.post_comment(post, comment)
            except Exception:
                print 'Unable to process post: ' + str(post)
            for comment in praw.helpers.flatten_tree(post.comments):
                try:
                    if not self.replied_to(comment) and not self.own_comment(comment):
                        reply = self.build_comment(comment)
                        if reply:
                            self.post_comment(comment, reply)
                except Exception:
                    print 'Unable to process comment: ' + str(comment)

if __name__ == '__main__':
    bot = XWingTMGCardBot(config)
    bot.mash_go()
