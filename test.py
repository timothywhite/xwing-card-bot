from bot import XWingTMGCardBot
import config

import threading

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def mash_go():
    bot = XWingTMGCardBot(config)
    bot.mash_go()

set_interval(mash_go, 60)
