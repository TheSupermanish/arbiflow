from exchange_config import *
from asyncio import gather, run, sleep
import time
import ccxt.pro
import ccxt
import sys
from colorama import Fore, Back, Style, init
import threading
init()
bid_prices = {}
ask_prices = {}
total_change_usd = 0
prec_ask_price = 0
prec_bid_price = 0
i = 0
z = 0

stop_requested = False


def listen_for_exit():
    global stop_requested
    input("")
    stop_requested = True


if len(sys.argv) != 6:
    print(
        f" \nIncorrect usage, this is what it has to look like: $ {python_command} bot-classic.py [pair] [total_usdt_investment] [stop.delay.minutes] [tlgrm.msg.title] [ex_list]\n ")
    print(f" \n This is the list of args you wrote: {sys.argv}")
    sys.exit(1)
print(" ")
if first_orders_fill_timeout <= 0:
    first_orders_fill_timeout = 3600  # 2.5 days

for e in sys.argv[5].split(','):
    if e not in list(ex.keys()):
        ex[e] = getattr(ccxt, e)()
echanges = [ex[sys.argv[5].split(',')[i]]
            for i in range(len(sys.argv[5].split(',')))]
echanges_str = [sys.argv[5].split(',')[i]
                for i in range(len(sys.argv[5].split(',')))]
currentPair = str(sys.argv[1]).upper()
criteria_usd = str(criteria_usd)
howmuchusd = float(sys.argv[2])
inputtimeout = int(sys.argv[3])*60
indicatif = str(sys.argv[4])
endPair = currentPair.split('/')[1]

fees = {n: 0 for n in echanges_str}

for ech in fees:
    markets = ex[ech].load_markets()
    fees[ech] = {'base': (0 if markets['BTC/USDT']['feeSide'] != 'base' else markets['BTC/USDT']['taker']) if list(markets['BTC/USDT'].keys()).count('feeSide') != 0 else 0, 'quote': (
        markets['BTC/USDT']['taker'] if markets['BTC/USDT']['feeSide'] != 'base' else 0) if list(markets['BTC/USDT'].keys()).count('feeSide') != 0 else markets['BTC/USDT']['taker']}


async def fetch_orderbook(exchange_instance, pair):
    try:
        orderbook = await exchange_instance.watch_order_book(pair)
    except Exception as e:
        printerror(
            m=f"Error while fetching orderbook on {exchange_instance.id}. {e}")
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        id_ = exchange_instance.id
        await exchange_instance.close()
        new_instance = getattr(ccxt.pro, id_)({'enableRateLimit': True})
        try:
            orderbook = await new_instance.watch_order_book(pair)
        except Exception as e:
            printerror(
                m=f"Error while fetching orderbook on {exchange_instance.id}. {e}")
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            sys.exit()
    return orderbook


def emergency_convert(pair_to_sell):
    i = 0
    for echange in echanges_str:
        try:
            if ex[echange].has['cancelAllOrders'] and ex[echange].fetchOpenOrders(pair_to_sell) != []:
                ex[echange].cancelAllOrders(pair_to_sell)
                print(
                    f"{Style.DIM}{get_time()}{Style.RESET_ALL} Successfully canceled all orders on {echange}.")
            bal = get_balance(echange, pair_to_sell)
            if bal > (float(10)/float(ex[echange].fetch_ticker(pair_to_sell)['last'])):
                ex[echange].createMarketSellOrder(
                    pair=pair_to_sell, amount=bal)
                print(
                    f"{Style.DIM}{get_time()}{Style.RESET_ALL} Successfully sold {bal} {pair_to_sell[:len(pair_to_sell)-5]} on {echange}.")
            else:
                print(
                    f"Not enough {pair_to_sell[:len(pair_to_sell)-5]} on {echange}.")
            i += 1
        except Exception as e:
            print(
                f'{Style.DIM}[{time.strftime("%H:%M:%S", time.gmtime(time.time()))}]{Style.RESET_ALL} Problem on {echange}. Error:    {e}')


def emergency_convert_list(pair_to_sell, exlist):
    i = 0
    for echange in exlist:
        try:
            if ex[echange].has['cancelAllOrders'] and ex[echange].fetchOpenOrders(pair_to_sell) != []:
                ex[echange].cancelAllOrders(pair_to_sell)
                print(
                    f"{Style.DIM}{get_time()}{Style.RESET_ALL} Successfully canceled all orders on {echange}.")
            bal = get_balance(echange, pair_to_sell)
            if bal > (float(10)/float(ex[echange].fetch_ticker(pair_to_sell)['last'])):
                ex[echange].createMarketSellOrder(
                    pair=pair_to_sell, amount=bal)
                print(
                    f"{Style.DIM}{get_time()}{Style.RESET_ALL} Successfully sold {bal} {pair_to_sell[:len(pair_to_sell)-5]} on {echange}.")
            else:
                print(
                    f"{Style.DIM}{get_time()}{Style.RESET_ALL} Not enough {pair_to_sell[:len(pair_to_sell)-5]} on {echange}.")
            i += 1
        except Exception as e:
            print(
                f'{Style.DIM}[{time.strftime("%H:%M:%S", time.gmtime(time.time()))}]{Style.RESET_ALL} Problem on {echange}. Error:    {e}')


s = 0

ordersFilled = 0

while ordersFilled != len(echanges):

    if s == 1:
        sys.exit(1)
    usd = {exchange: (howmuchusd/2)/len(echanges) for exchange in echanges_str}

    total_usd = 0
    for exc in echanges_str:
        total_usd += usd[exc]

    all_tickers = []

    try:
        printandtelegram(
            f"{Style.DIM}{get_time()}{Style.RESET_ALL} Fetching the global average price for {currentPair}...")
        for n in echanges:
            ticker = n.fetch_ticker(currentPair)
            all_tickers.append(ticker['last'])
        average_first_buy_price = moy(all_tickers)
        total_crypto = (howmuchusd/2)/average_first_buy_price
        printandtelegram(
            f"{Style.DIM}{get_time()}{Style.RESET_ALL} Average {currentPair} price in {endPair}: {average_first_buy_price}")

    except Exception as e:
        print(
            f"{Style.DIM}{get_time()}{Style.RESET_ALL} Error while fetching average prices. Error: {e}")
        for exc in echanges_str:
            ex[exc].close()

    crypto = {exchange: total_crypto/len(echanges)
              for exchange in echanges_str}

    crypto_per_transaction = (total_crypto/len(echanges_str))

    i = 0
    for n in echanges:
        time.sleep(0.7)
        printandtelegram(
            f'{Style.DIM}{get_time()}{Style.RESET_ALL} Buy limit order of {round(total_crypto/len(echanges),3)} {currentPair.split("/")[0]} at {average_first_buy_price} sent to {echanges_str[i]}.')
        i += 1

    printandtelegram(
        f"{Style.DIM}{get_time()}{Style.RESET_ALL} All orders sent.")

    already_filled = []
    for zz in range(len(echanges)):
        time.sleep(2.1)
        printandtelegram(
            f"{Style.DIM}{get_time()}{Style.RESET_ALL} {echanges_str[zz]} order filled.")
        ordersFilled += 1
        already_filled.append(exc)

time.sleep(1)
prec_time = '0000000'

min_ask_price = 0
timeout = time.time() + inputtimeout
total_change_usd = 0


async def pair_loop(exchange, pair):
    global total_change_usd, crypto_per_transaction, i, z, prec_time, t, time1, bid_prices, ask_prices, min_ask_price, max_bid_price, prec_ask_price, prec_bid_price, timeout, profit_usd, total_crypto
    while time.time() <= timeout:
        await sleep(2)
        if stop_requested:
            print(f"{Style.DIM}{get_time()}{Style.RESET_ALL} Refreshing...")
            print(f"{get_time()} Manual rebalance requested. Breaking.")
            await exchange.close()
            append_new_line(
                'logs/logs.txt', f"{get_time_blank()} INFO: Manual rebalance requested. Breaking.")
            timeout -= 100000000000
            break
        orderbook = await fetch_orderbook(exchange, pair)
        now = exchange.milliseconds()
        bid_prices[exchange.id] = orderbook["bids"][0][0]
        ask_prices[exchange.id] = orderbook["asks"][0][0]
        min_ask_ex = min(ask_prices, key=ask_prices.get)
        max_bid_ex = max(bid_prices, key=bid_prices.get)
        for u in echanges_str:
            if crypto[u] < crypto_per_transaction:
                min_ask_ex = u
            if usd[u] <= 0:  # should not happen
                max_bid_ex = u
        min_ask_price = ask_prices[min_ask_ex]
        max_bid_price = bid_prices[max_bid_ex]

        # Corrected fee logic:
        ask_base_fee = fees[min_ask_ex]['base']
        ask_quote_fee = fees[min_ask_ex]['quote']
        bid_base_fee = fees[max_bid_ex]['base']
        bid_quote_fee = fees[max_bid_ex]['quote']

        # After buying, base currency received after base-fee:
        crypto_received = crypto_per_transaction * (1 - ask_base_fee)
        # Effective base sold after bid-side base-fee:
        effective_crypto_sold = crypto_received * (1 - bid_base_fee)

        # Total cost in quote currency (includes quote-fee on buy):
        cost_to_buy = crypto_per_transaction * \
            min_ask_price * (1 + ask_quote_fee)
        # Total revenue in quote currency (after quote-fee on sell):
        revenue_from_sell = effective_crypto_sold * \
            max_bid_price * (1 - bid_quote_fee)

        change_usd = revenue_from_sell - cost_to_buy

        spread_pct = (max_bid_price - min_ask_price) / min_ask_price * 100
        is_profitable = max_bid_ex != min_ask_ex and change_usd > float(
            criteria_usd) and spread_pct >= criteria_pct
        if is_profitable:
            i += 1

            # Optionally: log fee breakdown (for debugging)
            print(f"{Style.DIM}{get_time()}{Style.RESET_ALL} Fees breakdown: buy quote-fee {ask_quote_fee*100}%, buy base-fee {ask_base_fee*100}%, sell base-fee {bid_base_fee*100}%, sell quote-fee {bid_quote_fee*100}%")

            # Remove old fees_crypto and fees_usd calculation, but you may add a new breakdown if desired.
            fees_crypto = None  # Not used with corrected logic
            fees_usd = None     # Not used with corrected logic

            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            print("-----------------------------------------------------\n")

            ex_balances = ""
            for exc in echanges_str:
                ex_balances += f"\n➝ {exc}: {round(crypto[exc],3)} {currentPair.split('/')[0]} / {round(usd[exc],2)} {endPair}"
            print(
                f"{Style.RESET_ALL}Opportunity n°{i} detected! ({min_ask_ex} {min_ask_price}   ->   {max_bid_price} {max_bid_ex})\n \nExcepted profit: {Fore.GREEN}+{round(change_usd,4)} {endPair}{Style.RESET_ALL}\n \nSession total profit: {Fore.GREEN}+{round(total_change_usd,4)} {endPair}{Style.RESET_ALL}\n \n{Style.RESET_ALL}{Style.DIM} {ex_balances}\n \n{Style.RESET_ALL}Time elapsed since the beginning of the session: {time.strftime('%H:%M:%S', time.gmtime(time.time()-st))}\n \n{Style.RESET_ALL}-----------------------------------------------------\n \n")
            send_to_telegram(f"[{indicatif} Trade n°{i}]\n \nOpportunity detected!\n \nExcepted profit: {round(change_usd,4)} {endPair}\n \n{min_ask_ex} {min_ask_price}   ->   {max_bid_price} {max_bid_ex}\nTime elapsed: {time.strftime('%H:%M:%S', time.gmtime(time.time()-st))}\nSession total profit: {round(total_change_usd,4)} % ({round(total_change_usd,4)} {endPair})\n--------BALANCES---------\n \n {ex_balances}")

            if demo_fake_delay:
                ts = time.time()
                await sleep(demo_fake_delay_ms/1000)
                ob_min_ask = await fetch_orderbook(getattr(ccxt, min_ask_ex)(), pair)
                ob_max_bid = await fetch_orderbook(getattr(ccxt, max_bid_ex)(), pair)
                min_ask_price = ob_min_ask['asks'][0][0]
                max_bid_price = ob_max_bid['bids'][0][0]

                actual_min_ask_usd_bal = usd[min_ask_ex] - (crypto_per_transaction / (
                    1-fees[min_ask_ex]['quote'])) * min_ask_price * (1+fees[min_ask_ex]['base'])
                actual_max_bid_usd_bal = usd[max_bid_ex] + (crypto_per_transaction / (
                    1+fees[max_bid_ex]['base']) * max_bid_price * (1-fees[max_bid_ex]['quote']))

                change_usd = (actual_min_ask_usd_bal+actual_max_bid_usd_bal) - \
                    (usd[max_bid_ex]+usd[min_ask_ex])
                delay = 1000*(time.time() - ts)
                printandtelegram(
                    f"{Style.DIM}{get_time()}{Style.RESET_ALL} Now calculating P&L of the opportunity with an added (fake) delay of {int(round(delay,0))}ms")

            printandtelegram(
                f"{Style.DIM}{get_time()}{Style.RESET_ALL} Sell market order filled on {max_bid_ex} for {crypto_per_transaction} {currentPair.split('/')[0]} at {max_bid_price}.")
            printandtelegram(
                f"{Style.DIM}{get_time()}{Style.RESET_ALL} Buy market order filled on {min_ask_ex} for {crypto_per_transaction} {currentPair.split('/')[0]} at {min_ask_price}.")

            append_list_file('all_opportunities_profits.txt', change_usd)

            crypto[min_ask_ex] += crypto_per_transaction
            usd[min_ask_ex] -= cost_to_buy
            crypto[max_bid_ex] -= crypto_per_transaction
            usd[max_bid_ex] += revenue_from_sell

            total_change_usd += change_usd

            # Log profit booking
            append_new_line(
                "logs/logs.txt", f"{get_time_blank()} PROFIT BOOKED: +{round(change_usd, 4)} {endPair} from {min_ask_ex} → {max_bid_ex}")

            prec_ask_price = min_ask_price
            prec_bid_price = max_bid_price

            total_crypto = 0
            for exc in echanges_str:
                total_crypto += crypto[exc]
            crypto_per_transaction = total_crypto/len(echanges_str)

        else:
            # Clear screen and create dashboard layout
            print("\033[2J\033[H", end="")  # Clear screen, move to top

            # Header with session info
            print(f"{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}")
            print(
                f"{Fore.CYAN}  ArbiFlow - {currentPair} Trading Session{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}")

            # Time and session stats
            elapsed_time = time.strftime(
                '%H:%M:%S', time.gmtime(time.time() - st))
            print(f"\n⏱️  Session Time: {Fore.YELLOW}{elapsed_time}{Style.RESET_ALL} | "
                  f"💰 Total Profit: {Fore.GREEN if total_change_usd >= 0 else Fore.RED}${round(total_change_usd, 4)}{Style.RESET_ALL} | "
                  f"🔄 Opportunities: {Fore.BLUE}{i}{Style.RESET_ALL}")

            # Market data section
            print(
                f"\n{Fore.MAGENTA}{'─' * 40} MARKET DATA {'─' * 40}{Style.RESET_ALL}")

            # Best opportunity with color coding
            if change_usd < 0:
                profit_color = Fore.RED
                profit_icon = "📉"
            elif change_usd > 0:
                profit_color = Fore.GREEN
                profit_icon = "📈"
            else:
                profit_color = Fore.WHITE
                profit_icon = "➖"

            print(f"🎯 Best Opportunity: {profit_icon} {profit_color}${round(change_usd, 4)}{Style.RESET_ALL} "
                  f"(After Fees)")
            print(
                f"💸 Buy:  {Fore.GREEN}{min_ask_ex.upper():<10}{Style.RESET_ALL} @ {Fore.GREEN}${min_ask_price:>10.6f}{Style.RESET_ALL}")
            print(
                f"💰 Sell: {Fore.RED}{max_bid_ex.upper():<10}{Style.RESET_ALL} @ {Fore.RED}${max_bid_price:>10.6f}{Style.RESET_ALL}")
            print(f"📊 Spread: {Fore.YELLOW}${round(max_bid_price - min_ask_price, 6)}{Style.RESET_ALL} "
                  f"({Fore.YELLOW}{round(spread_pct, 4)}%{Style.RESET_ALL})")

            # Trading details
            print(
                f"\n{Fore.MAGENTA}{'─' * 40} TRADE DETAILS {'─' * 40}{Style.RESET_ALL}")
            print(
                f"📦 Trade Size: {Fore.CYAN}{crypto_per_transaction:.6f} {currentPair.split('/')[0]}{Style.RESET_ALL}")
            print(
                f"💵 Buy Cost:   {Fore.RED}${round(cost_to_buy, 4)}{Style.RESET_ALL}")
            print(
                f"💰 Sell Rev:   {Fore.GREEN}${round(revenue_from_sell, 4)}{Style.RESET_ALL}")
            print(
                f"🧮 Net P&L:    {profit_color}${round(change_usd, 6)}{Style.RESET_ALL}")

            # Exchange balances section
            print(
                f"\n{Fore.MAGENTA}{'─' * 40} BALANCES {'─' * 40}{Style.RESET_ALL}")
            for idx, exc in enumerate(echanges_str):
                crypto_bal = round(crypto[exc], 6)
                usd_bal = round(usd[exc], 2)

                # Color code based on balance levels
                crypto_color = Fore.GREEN if crypto_bal > crypto_per_transaction * \
                    0.8 else Fore.YELLOW if crypto_bal > crypto_per_transaction * 0.3 else Fore.RED
                usd_color = Fore.GREEN if usd_bal > (howmuchusd/2)/len(
                    echanges) * 0.8 else Fore.YELLOW if usd_bal > (howmuchusd/2)/len(echanges) * 0.3 else Fore.RED

                print(f"🏦 {exc.upper():<10}: {crypto_color}{crypto_bal:>10.6f} {currentPair.split('/')[0]}{Style.RESET_ALL} | "
                      f"{usd_color}${usd_bal:>8.2f} {endPair}{Style.RESET_ALL}")

            # Criteria and status
            print(
                f"\n{Fore.MAGENTA}{'─' * 40} CRITERIA {'─' * 40}{Style.RESET_ALL}")

            # Status indicators with emojis
            profit_status = "✅" if change_usd > float(criteria_usd) else "❌"
            spread_status = "✅" if spread_pct >= criteria_pct else "❌"
            exchange_status = "✅" if max_bid_ex != min_ask_ex else "❌"

            print(
                f"{profit_status} Profit > ${criteria_usd}: {profit_color}${round(change_usd, 4)}{Style.RESET_ALL}")
            print(
                f"{spread_status} Spread > {criteria_pct}%: {Fore.YELLOW}{round(spread_pct, 4)}%{Style.RESET_ALL}")
            print(
                f"{exchange_status} Different Exchanges: {Fore.CYAN}{min_ask_ex} ≠ {max_bid_ex}{Style.RESET_ALL}")

            # Live price updates
            print(
                f"\n{Fore.MAGENTA}{'─' * 40} LIVE PRICES {'─' * 40}{Style.RESET_ALL}")
            for exc_name in echanges_str:
                if exc_name in bid_prices and exc_name in ask_prices:
                    bid = bid_prices[exc_name]
                    ask = ask_prices[exc_name]
                    spread_local = ask - bid

                    # Highlight best exchanges
                    exc_display = f"{Fore.GREEN}{exc_name.upper()}{Style.RESET_ALL}" if exc_name == max_bid_ex else f"{Fore.RED}{exc_name.upper()}{Style.RESET_ALL}" if exc_name == min_ask_ex else exc_name.upper()

                    print(f"📊 {exc_display:<15}: Bid {Fore.GREEN}${bid:>10.6f}{Style.RESET_ALL} | "
                          f"Ask {Fore.RED}${ask:>10.6f}{Style.RESET_ALL} | "
                          f"Spread ${spread_local:>8.6f}")

            # Footer
            print(f"\n{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}")
            print(
                f"{Style.DIM}Last Update: {get_time()} | Press Enter to exit gracefully{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 90}{Style.RESET_ALL}")
        time1 = exchange.iso8601(exchange.milliseconds())
        if time1[17:19] == "00" and time1[14:16] != prec_time:
            prec_time = time1[11:13]
            await exchange.close()


async def exchange_loop(exchange_id, pairs):
    exchange = getattr(ccxt.pro, exchange_id)()
    loops = [pair_loop(exchange, pair) for pair in pairs]
    await gather(*loops)
    await exchange.close()


async def main():
    exchanges = {
        echanges_str[i]: [currentPair] for i in range(0, len(echanges))
    }
    loops = [
        exchange_loop(exchange_id, pairs)
        for exchange_id, pairs in exchanges.items()
    ]
    await gather(*loops)

st = time.time()
print(" \n")
listener_thread = threading.Thread(target=listen_for_exit)
listener_thread.start()
run(main())

for exc in crypto:
    ticker = ex[exc].fetchTicker(currentPair)
    price = ticker['last']
    if delta_neutral:
        usd[exc] += crypto[exc]*average_first_buy_price
    else:
        usd[exc] += crypto[exc]*price
    crypto[exc] = 0

total_usdt_balance = 0
for n in echanges_str:
    total_usdt_balance += usd[n]

with open('real_balance.txt', 'r+') as balance_file:
    old_balance = float(balance_file.read())
    balance_file.seek(0)
    balance_file.write(str(total_usdt_balance))

total_session_profit_usd = total_usdt_balance-old_balance
printandtelegram(f"{Style.DIM}{get_time()}{Style.RESET_ALL} Session with {currentPair} finished.\n{Style.DIM}{get_time()}{Style.RESET_ALL} Total profit: {total_session_profit_usd} {endPair}")
