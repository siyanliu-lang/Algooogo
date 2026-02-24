# This is a python example algorithm using REST API for the RIT ALGO2 Case

import signal
import requests
from time import sleep

# this class definition allows us to print error messages and stop the program when needed
class ApiException(Exception):
    pass

# this signal handler allows for a graceful shutdown when CTRL+C is pressed
def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    shutdown = True

# set your API key to authenticate to the RIT client
API_KEY = {'X-API-Key': '0L4L30PC'}
shutdown = False

# this helper method returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT â€“ User Guide â€“ REST API Documentation.pdf)')
    case = resp.json()
    return case['tick']

# this helper method returns the last close price for the given security, one tick ago
def ticker_close(session, ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = session.get('http://localhost:9999/v1/securities/history', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT â€“ User Guide â€“ REST API Documentation.pdf)')
    ticker_history = resp.json()
    if ticker_history:
        return ticker_history[0]['close']
    else:
        raise ApiException('Response error. Unexpected JSON response.')

# this helper method gets all the orders of a given type (OPEN/TRANSACTED/CANCELLED)
def get_orders(session, status):
    payload = {'status': status}
    resp = session.get('http://localhost:9999/v1/orders', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT â€“ User Guide â€“ REST API Documentation.pdf)')
    orders = resp.json()
    return orders

def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT â€“ User Guide â€“ REST API Documentation.pdf)')

def get_position(session, ticker):
    payload = {'ticker':ticker}
    resp = session.get('http://localhost:9999/v1/securities', params=payload)
    if resp.status_code == 401:
        raise ApiException('The API key provided in this Python code must match that in the RIT client (please refer to the API hyperlink in the client toolbar and/or the RIT – User Guide – REST API Documentation.pdf)')
    security = resp.json()
    return security[0]['position']

# this is the main method containing the actual market making strategy logic
def main():
    # creates a session to manage connections and requests to the RIT Client
    with requests.Session() as s:
        # add the API key to the session to authenticate during requests
        s.headers.update(API_KEY)
        # get the current time of the case
        tick = get_tick(s)

        # while the time is between 5 and 295, do the following
        while tick > 0 and tick < 299:
            # get the open order book and ALGO last tick's close price
            orders = get_orders(s, 'OPEN')

            # get the current best bid and best ask
            bid, ask = ticker_bid_ask(s, 'ALGO')

            # get the current position
            position = get_position(s, 'ALGO')
            if position > 50000:
                # submit a large market sell
                s.post('http://localhost:9999/v1/orders', params={'ticker': 'ALGO', 'type': 'MARKET', 'quantity': 5000, 'action': 'SELL'})
            elif position < -50000:
                # submit a large market buy
                s.post('http://localhost:9999/v1/orders', params={'ticker': 'ALGO', 'type': 'MARKET', 'quantity': 5000, 'action': 'BUY'})
            else:
                # cancel old orders when number of orders > 10
                if len(orders) > 18:
                    order_id = orders[-1]['order_id']
                    s.delete('http://localhost:9999/v1/orders/' + str(order_id))

                if len(orders) <= 18:
                    # dynamically adjust buy and sell volume
                    if position == 0:
                        buy_vol = 2500
                        sell_vol = 2500
                    else:
                        buy_vol = 2500*(1 - 0.1 * (position // 2000))
                        sell_vol = 2500*(1 + 0.1 * (position // 2000))

                    if buy_vol > 5000:
                        buy_vol = 5000
                        sell_vol = 500
                    if sell_vol > 5000:
                        buy_vol = 500
                        sell_vol = 5000
                    
                    # dynamically adjust buy and sell prices
                    buy_price = bid - 0.01
                    sell_price = ask + 0.01
                    if position > 0:
                        buy_price = buy_price - 0.01
                    elif position < 0:
                        sell_price = sell_price + 0.01

                    # submit the orders
                    s.post('http://localhost:9999/v1/orders', params={'ticker': 'ALGO', 'type': 'LIMIT', 'quantity': buy_vol, 'action': 'BUY', 'price': buy_price})
                    s.post('http://localhost:9999/v1/orders', params={'ticker': 'ALGO', 'type': 'LIMIT', 'quantity': sell_vol, 'action': 'SELL', 'price': sell_price})
                    sleep(0.3)

            # refresh the case time. THIS IS IMPORTANT FOR THE WHILE LOOP
            tick = get_tick(s)

# this calls the main() method when you type 'python algo2.py' into the command prompt
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()