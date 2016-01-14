#!/usr/bin/env python
# -*- coding=utf8

import json
import urllib2
import argparse
import time
import xml.etree.ElementTree as et
import socket

def get_url(url):
  headers = {"User-Agent": "quotes-bot-toomyem"}
  for tries in range(3):
    try:
      req = urllib2.Request(url, None, headers)
      conn = urllib2.urlopen(req, timeout=20)
      data = conn.read()
      return json.loads(data)
    except Exception:
      time.sleep(1)
  return {"error": "request cannot be fulfilled"}

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--btc", type=float, help="amount of btc to sell/buy")
  parser.add_argument("--pln", type=float, help="amount of pln to sell/buy")
  return parser.parse_args()
  
def sort(asks, bids):
  return {"asks": sorted(asks, cmp=lambda a,b: cmp(a[0], b[0])),
          "bids": sorted(bids, cmp=lambda a,b: cmp(b[0], a[0]))}
  
def get_fiat_values(currencies):
  url = 'http://www.nbp.pl/kursy/xml/LastA.xml'
  try:
    req = urllib2.Request(url)
    conn = urllib2.urlopen(req, timeout=20)
    data = conn.read()
  except socket.error as ex:
    print ex
    data = "<empty/>"
  root = et.fromstring(data)
  d = {"pln": 1.0}
  for p in root.iter('pozycja'):
    cur = p.find("kod_waluty").text.lower()
    if cur in currencies:
      div = float(p.find('przelicznik').text)
      d[cur] = float(p.find('kurs_sredni').text.replace(",",".")) / div
  return d

###########################################################
  
class Bitcurex:
  URL = "https://bitcurex.com/api/pln/"

  def get_name(self):
    return "Bitcurex"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0.48

  def get_last(self):
    data = get_url(self.URL + "ticker.json")
    return data['last_tx_price'] / 10000.0
    
  def get_book(self):
    data = get_url(self.URL + "orderbook.json")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))
    
  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class BitcurexEur(Bitcurex):
  URL = "https://bitcurex.com/api/eur/"

  def get_currency(self):
    return "eur"


class Bitmarket:
  URL = "https://www.bitmarket.pl/json/BTCPLN/"
  
  def get_name(self):
    return "Bitmarket"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0.29

  def get_last(self):
    data = get_url(self.URL + "ticker.json")
    return data['last']
    
  def get_book(self):
    data = get_url(self.URL + "orderbook.json")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class Bitmarket24:
  URL = "https://bitmarket24.pl/api/BTC_PLN/"
  
  def get_name(self):
    return "Bitmarket24"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0

  def get_last(self):
    data = get_url(self.URL + "status.json")
    return float(data['last'])
    
  def get_book(self):
    data = get_url(self.URL + "offers.json")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class Bitorado:
  URL = "https://www.bitorado.com/api/market/BTC-PLN/"
  
  def get_name(self):
    return "Bitorado"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0

  def get_last(self):
    data = get_url(self.URL + "ticker")
    return data['result']['last']
    
  def get_book(self):
    data = get_url(self.URL + "orders-sell")
    asks = map(self._map_book, data['result'])
    data = get_url(self.URL + "orders-buy")
    bids = map(self._map_book, data['result'])
    return sort(asks, bids)

  def _map_book(self, o):
    return [float(o['price']), float(o['amount'])]


class Bitbay:
  URL = "https://market.bitbay.pl/API/Public/BTCPLN/"
  
  def get_name(self):
    return "Bitbay"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0.5

  def get_last(self):
    data = get_url(self.URL + "ticker.json")
    return float(data['last'])
    
  def get_book(self):
    data = get_url(self.URL + "orderbook.json")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class Bitmaszyna:
  URL = "https://bitmaszyna.pl/api/BTCPLN/"

  def get_name(self):
    return "Bitmaszyna"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0

  def get_last(self):
    data = get_url(self.URL + "transactions.json")
    return data['transactionsbtcpln'][0]['kurs']
    
  def get_book(self):
    data = get_url(self.URL + "depth.json")
    return sort(map(self._map_book, data['offersbtcpln']["asks"]),
                map(self._map_book, data['offersbtcpln']["bids"]))
    
  def _map_book(self, o):
    return [float(o[2]), float(o[1])]


class NevBit:
  URL = "https://nevbit.com/data/"

  def get_name(self):
    return "NevBit"
      
  def get_currency(self):
    return "pln"

  def get_fee(self):
    return 0

  def get_last(self):
    data = get_url(self.URL + "ticker.json")
    return data['last']
    
  def get_book(self):
    data = get_url(self.URL + "orderbook.json")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))
    
  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class Bitstamp:
  URL = "https://www.bitstamp.net/api/"
  
  def get_name(self):
    return "Bitstamp"
      
  def get_currency(self):
    return "usd"

  def get_fee(self):
    return 0.5

  def get_last(self):
    data = get_url(self.URL + "ticker/")
    return float(data['last'])
    
  def get_book(self):
    data = get_url(self.URL + "order_book/")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class Bitfinex:
  URL = "https://api.bitfinex.com/v1/"

  def get_name(self):
    return "Bitfinex"

  def get_currency(self):
    return "usd"

  def get_fee(self):
    return 0.2

  def get_last(self):
    data = get_url(self.URL + "pubticker/BTCUSD")
    return float(data['last_price'])

  def get_book(self):
    data = get_url(self.URL + "book/BTCUSD")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o["price"]), float(o["amount"])]


class Kraken:
  URL = "https://api.kraken.com/0/public/"
  
  def get_name(self):
    return "Kraken"
      
  def get_currency(self):
    return "eur"

  def get_fee(self):
    return 0.2

  def get_last(self):
    data = get_url(self.URL + "Ticker?pair=XBTEUR")
    return float(data['result']['XXBTZEUR']['c'][0])
    
  def get_book(self):
    data = get_url(self.URL + "Depth?pair=XBTEUR")
    return sort(map(self._map_book, data['result']['XXBTZEUR']["asks"]),
                map(self._map_book, data['result']['XXBTZEUR']["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]
 

class BtcChina:
  URL = "https://data.btcchina.com/data/"

  def get_name(self):
    return "BTCChina"

  def get_currency(self):
    return "cny"

  def get_fee(self):
    return 0.0

  def get_last(self):
    data = get_url(self.URL + "ticker")
    return float(data["ticker"]['last'])

  def get_book(self):
    data = get_url(self.URL + "orderbook")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class Huobi:
  URL = "https://api.huobi.com/staticmarket/"

  def get_name(self):
    return "Huobi"

  def get_currency(self):
    return "cny"

  def get_fee(self):
    return 0.0

  def get_last(self):
    data = get_url(self.URL + "ticker_btc_json.js")
    return float(data["ticker"]['last'])

  def get_book(self):
    data = get_url(self.URL + "depth_btc_json.js")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


class CexIO:
  URL = "https://cex.io/api/"

  def get_name(self):
    return "Cex.io"

  def get_currency(self):
    return "usd"

  def get_fee(self):
    return 0.2

  def get_last(self):
    data = get_url(self.URL + "last_price/BTC/USD")
    return float(data["lprice"])

  def get_book(self):
    data = get_url(self.URL + "order_book/BTC/USD")
    return sort(map(self._map_book, data["asks"]),
                map(self._map_book, data["bids"]))

  def _map_book(self, o):
    return [float(o[0]), float(o[1])]


all_exchanges =[ \
  Bitmarket(),
  Bitmaszyna(),
  Bitmarket24(),
  Bitcurex(),
  Bitbay(),
  Bitorado(),
  #NevBit(),
  Bitstamp(),
  Bitfinex(),
  CexIO(),
  Kraken(),
  BitcurexEur(),
  BtcChina(),
  Huobi()]

###########################################################

def calc_fiat_value(btc, offers):
  value = 0.0
  for x in offers:
    price, amount = x
    if amount >= btc:
      value += btc*price
      return value
    value += amount*price
    btc -= amount
  return 0
  
def calc_btc_value(fiat, offers):
  value = 0.0
  for x in offers:
    price, amount = x
    if price*amount >= fiat:
      value += fiat / price
      return value
    value += amount
    fiat -= price*amount
  return 0

def calc_quotes(exchange, fiat, btc=0, pln=0):
  last = 0.0
  try:
    last = exchange.get_last()
  except:
    pass
  book = {}
  try:
    book = exchange.get_book()
  except:
    pass
  asks = book.get('asks', [])
  bids = book.get('bids', [])
  fee = exchange.get_fee() / 100.0
  curr = fiat.get(exchange.get_currency(), 0)

  if pln > 0:
    btc += calc_btc_value(pln/curr, asks)

  buy = calc_fiat_value(btc, asks) * (1+fee)
  sell = calc_fiat_value(btc, bids) * (1-fee)

  buy_avg = buy / btc
  sell_avg = sell / btc
  spread = buy - sell

  print "%-15s| %s | fee: %02.1f | last: %7.2f (%7.2f)| buy: %7.2f (%7.2f) | sell: %7.2f (%7.2f) | spread: %0.2f" % \
    (exchange.get_name(), exchange.get_currency(), fee*100, last, last*curr, buy_avg, buy*curr, sell_avg, sell*curr, spread)
  
###########################################################

if __name__ == "__main__":
  args = parse_args()
  
  curr = set([e.get_currency() for e in all_exchanges])
  #curr.update(['aud', 'cad', 'chf', 'nok', 'jpy', 'gbp', 'nzd'])
  curr.update(['chf'])
  fiat = get_fiat_values(curr)
  for f in sorted(fiat.keys()):
    if f != "pln": print "%s: %0.4f zł" % (f, fiat[f])
  print

  if args.btc > 0:
    for ex in all_exchanges:
      calc_quotes(ex, fiat, btc=args.btc)

  if args.pln > 0:
    for ex in all_exchanges:
      calc_quotes(ex, fiat, pln=args.pln)

