from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, run_async
from config import __LOCALE_BILLION__, __ADMINS__
from json import dump, load
from datetime import datetime
import tzlocal
import random
import requests
import sys

class Commands():
    def __init__(self, user_agent):
        self.user_agent = user_agent


    # Define a few command handlers. These usually take the two arguments bot and
    # update. Error handlers also receive the raised TelegramError object in error.
    def start(self, bot, update):
        '''Send a message when the command /start is issued.'''
        update.message.reply_text('Ready!')


    def help(self, bot, update):
        '''Sends a link to the command list'''
        update.message.reply_text('A list of all commands can be found here: ')


    @run_async
    def coin(self, bot, update, args):
        '''Shows the current price of one given cryptocurrency'''
        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
        with open('tmp/pairings.json', 'r') as f:
            pairings = load(f)
        with open('tmp/exchange_price_cache.json', 'r') as f:
            exchange_rate = load(f)
        coin = '-'.join(args)
        try:
            coin = pairings[coin.upper()].lower().replace(' ', '-')
        except KeyError:
            coin = coin.lower().replace(' ', '-')
        api = f'https://api.coinmarketcap.com/v1/ticker/{coin}/?convert=EUR'
        link = f'https://coinmarketcap.com/currencies/{coin}/'

        r = requests.get(api, headers=self.user_agent)
        json = r.json()
        try:
            euro = float(json[0]["price_eur"])
            sat = int(float(json[0]["price_btc"]) * 100000000)
        except KeyError:
            bot.send_message(chat_id=update.message.chat_id, text=f'Couldn\'t find coin {coin}!')
            return
        if json[0]["market_cap_eur"] == None:
            marketCap = 0.0
        else:
            marketCap = float(json[0]["market_cap_eur"]) / 1000000000
        eth = (sat / 100000000) * exchange_rate['exchange_btc_eth']
        volume = float(json[0]["24h_volume_eur"]) / 1000000
        timestamp = int(json[0]["last_updated"])
        local_timezone = tzlocal.get_localzone()
        last_update = datetime.fromtimestamp(timestamp, local_timezone)

        msg = f'Current {json[0]["name"]} ({json[0]["symbol"]}) Price:\n'
        msg += f'{euro:.6f} €\n'
        msg += f'{sat} Sat\n'
        msg += f'{eth:.8f} ETH\n\n'
        msg += f'1 hour change: {json[0]["percent_change_1h"]}%\n'
        msg += f'24 hour change: {json[0]["percent_change_24h"]}%\n'
        msg += f'7 days change: {json[0]["percent_change_7d"]}%\n\n'
        msg += f'Rank: {json[0]["rank"]}\n'
        msg += f'Market Cap: {marketCap:.3f} {__LOCALE_BILLION__} €\n'
        msg += f'Volume (24 hours): {volume:.3f} Mio. €\n'
        msg += f'Last Update: {last_update.strftime("%H:%M:%S %x")}\n'
        msg += link
        bot.send_message(chat_id=update.message.chat_id, text=msg)


    @run_async
#    def eth(self, bot, update, args):
#        '''Converts a given Ethereum amount to Bitcoin'''
#       api = 'https://api.coinmarketcap.com/v1/ticker/spacegrime/?convert=EUR'
#        ether = float(''.join(args).replace(',', '.'))
#
#        r = requests.get(api, headers=self.user_agent)
#        json = r.json()
#        exchange_rate = float(json[0]['price_btc'])
#        exchange_rate_euro = float(json[0]['price_eur'])
#        btc = exchange_rate * ether
#        euro = exchange_rate_euro * ether
#        msg = f'{ether} Ether are {btc:.8f} ฿\n'
#        msg += f'Current price: {euro:.2f} €'
#        update.message.reply_text(msg)


    @run_async
    def coinflip(self, bot, update, args):
        '''Flips a coin'''
        if len(args) == 2:
            coin = [args[0], args[1]]
        else:
            coin = ['Head', 'Tails']
        update.message.reply_text(f'🔄 {random.choice(coin)}')

    # def quit(bot, update):
    #     '''Quits the bot'''
    #     update.message.reply_text('Shutting down!')
    #     bot.updater.stop()
    #     sys.exit(0)