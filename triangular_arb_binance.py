import asyncio
import json
import websockets
import keyboard
import pandas as pd
import time
########################################################################################################################
#Code for detecting triangular arbitrage opportunities in Binance crypto exchange.
#The overall algorithm first gets the bid and ask prices for each currency pairs,
#if a change of price is detected from the previous records, algorithm goes on to search for
#possible arbitrage possibilties using the formula given in the PDF
#(i.e P(ask)AB *P(ask)BC / P(ask)AC < 1 or  P(bid)AB *P(bid)BC / P(bid)AC > 1)
#the code saves the detected arbs as an array of dicts and upon closing, it saves the data in an excel file.

#all the edge cases in the code are tested and also its functionning is manually verified 
########################################################################################################################


#obtained using https://api.binance.com/api/v3/exchangeInfo
pairs = ['ethbtc', 'ltcbtc', 'bnteth', 'btcusdt', 'ethusdt', 'iotabtc', 'linkbtc', 'zecbtc', 'bntbtc', 'xrpeth', 'bnbusdt', 'neousdt', 'manabtc', 'ltcusdt', 'rlcbtc', 'iostbtc', 'blzbtc', 'adausdt', 'xrpusdt', 'ethtusd', 'zeneth', 'tusdusdt', 'iotausdt', 'xlmusdt', 'iotxbtc', 'etcusdt', 'vetusdt', 'btcusdc', 'ethusdc', 'xrpusdc', 'usdcusdt', 'wavesusdt', 'ongusdt', 'zilusdt', 'zrxusdt', 'fetbnb', 'fetbtc', 'fetusdt', 'xmrusdt', 'zecusdt', 'celrusdt', 'thetausdt', 'maticusdt', 'atombnb', 'atombtc', 'atomusdt', 'algobnb', 'dogeusdt', 'ankrusdt', 'cosusdt', 'mtlusdt', 'rvnusdt', 'hbarusdt', 'stxbtc', 'stxusdt', 'kavausdt', 'arpausdt', 'iotxusdt', 'rlcusdt', 'bchusdt', 'viteusdt', 'xrptry', 'usdttry', 'btceur', 'etheur', 'wrxusdt', 'cotibtc', 'cotiusdt', 'stptusdt', 'btczar', 'solbtc', 'solusdt', 'chrusdt', 'zenusdt', 'ethupusdt', 'ethdownusdt', 'mkrusdt', 'bnbupusdt', 'manausdt', 'blzusdt', 'ethdai', 'jstusdt', 'crvbtc', 'sandusdt', 'dotusdt', 'lunausdt', 'sushiusdt', 'ksmusdt', 'belbtc', 'belusdt', 'avaxbtc', 'flmbtc', 'cakebnb', 'aavebnb', 'btcbrl', 'aaveeth', 'nearusdt', 'injbnb', 'injbtc', 'injusdt', 'akrousdt', 'axsbtc', 'axsusdt', 'slpeth', 'roseusdt', 'grtbtc', 'grteth', 'grtusdt', '1inchusdt', 'rifusdt', 'grteur', 'ckbusdt', 'fxsbtc', 'cakebtc', 'adabrl', 'badgerbtc', 'badgerusdt', 'fisusdt', 'omusdt', 'maticeur', 'neotry', 'superbtc', 'superusdt', 'cfxusdt', 'pundixusdt', 'slpusdt', 'shibusdt', 'icpusdt', 'arusdt', 'mdxusdt', 'maskusdt', 'lptusdt', 'shibtry', 'soltry', 'klayusdt', 'bondusdt', 'grttry', 'c98usdt', 'qntusdt', 'flowusdt', 'farmbtc', 'farmusdt', 'requsdt', 'gnousdt', 'dydxusdt', 'dydxbnb', 'dydxbtc', 'idexusdt', 'galausdt', 'sysusdt', 'solusdc', 'betausdt', 'lazioeur', 'laziousdt', 'auctionusdt', 'movrbtc', 'movrusdt', 'ensusdt', 'chreth', 'vgxusdt', 'pyrusdt', 'rndrbtc', 'rndrusdt', 'bicobtc', 'bicousdt', 'galatry', 'peopleusdt', 'roseeth', 'api3btc', 'api3usdt', 'xnousdt', 'costry', 'dartry', 'neartry', 'injtry', 'api3try', 'apeusdt', 'bswusdt', 'runeeth', 'ziltry', 'bswtry', 'mobusdt', 'galusdt', 'galbtc', 'ldousdt', 'opbtc', 'opusdt', 'opbnb', 'snxeth', 'fileth', 'luncusdt', 'gmxusdt', 'aptbtc', 'aptusdt', 'hookbtc', 'magicusdt', 'prosusdt', 'fettry', 'agixusdt', 'vibusdt', 'ambusdt', 'ustcusdt', 'idbtc', 'idusdt', 'loomusdt', 'idtusd', 'dogetusd', 'eduusdt', 'suiusdt', 'suibnb', 'suieur', 'suitry', 'rndrtry', 'pepeusdt', 'pepetusd', 'pepetry', 'flokitry', 'mavusdt', 'pendleusdt', 'mavtry', 'oceantry',  'arkmusdt', 'arkmtusd', 'arkmtry', 'arkmbnb', 'avaxtusd', 'wldusdt', 'wldbtc', 'fdusdusdt', 'btcfdusd', 'ethfdusd', 'seibnb', 'seibtc', 'seifdusd', 'seitry', 'seiusdt', 'cyberbnb', 'cybertusd', 'seitusd', 'lpttry', 'solfdusd', 'xrpfdusd', 'cybereth', 'gftusdt', 'suifdusd', 'adafdusd', 'atomfdusd', 'maticfdusd', 'ftmfdusd', 'tiatry', 'memebnb', 'memeusdt', 'memefdusd', 'ordiusdt', 'egldfdusd', 'fetfdusd', 'injeth', 'injtusd', 'ordifdusd', 'orditusd', 'rndrfdusd', 'beamxusdt', 'beamxtry', 'blurtry', 'superfdusd', 'ustcfdusd', 'ustctry', 'lunctry', 'supertry', 'jtousdt', 'jtotry', '1000satsusdt', '1000satstry', 'shibfdusd', 'injfdusd', 'bonkusdt', 'blzfdusd', 'nfpbtc', 'nfpusdt', 'dotusdc', 'injusdc', 'maticusdc', 'ordiusdc', 'aibtc', 'aiusdt', 'aibnb', 'aifdusd', 'aitusd', 'aitry', 'icpfdusd', 'ldofdusd', 'movrtry', 'xaibtc', 'stxfdusd', 'mantausdt', 'mantafdusd', 'mantatry', 'ensfdusd', 'altbtc', 'altusdt', 'altbnb', 'alttry', 'juptry', 'altusdc', 'magicfdusd', 'seiusdc', 'pythfdusd', 'roninusdt', 'ronintry', 'dymusdt', 'dymfdusd', 'dymtry', ]
single_tickers = ['ETH', 'BTC', 'LTC', 'BNB', 'NEO', 'QTUM', 'EOS', 'SNT', 'BNT', 'BCC', 'GAS', 'USDT', 'HSR', 'OAX', 'DNT', 'MCO', 'ICN', 'WTC', 'LRC', 'YOYO', 'OMG', 'ZRX', 'STRAT', 'SNGLS', 'BQX', 'KNC', 'FUN', 'SNM', 'IOTA', 'LINK', 'XVG', 'SALT', 'MDA', 'MTL', 'SUB', 'ETC', 'MTH', 'ENG', 'ZEC', 'AST', 'DASH', 'BTG', 'EVX', 'REQ', 'VIB', 'TRX', 'POWR', 'ARK', 'XRP', 'MOD', 'ENJ', 'STORJ', 'VEN', 'KMD', 'NULS', 'RCN', 'RDN', 'XMR', 'DLT', 'AMB', 'BAT', 'BCPT', 'ARN', 'GVT', 'CDT', 'GXS', 'POE', 'QSP', 'BTS', 'XZC', 'LSK', 'TNT', 'FUEL', 'MANA', 'BCD', 'DGD', 'ADX', 'ADA', 'PPT', 'CMT', 'XLM', 'CND', 'LEND', 'WABI', 'TNB', 'WAVES', 'GTO', 'ICX', 'OST', 'ELF', 'AION', 'NEBL', 'BRD', 'EDO', 'WINGS', 'NAV', 'LUN', 'TRIG', 'APPC', 'VIBE', 'RLC', 'INS', 'PIVX', 'IOST', 'CHAT', 'STEEM', 'NANO', 'VIA', 'BLZ', 'AE', 'RPX', 'NCASH', 'POA', 'ZIL', 'ONT', 'STORM', 'XEM', 'WAN', 'WPR', 'QLC', 'SYS', 'GRS', 'CLOAK', 'GNT', 'LOOM', 'BCN', 'REP', 'TUSD', 'ZEN', 'SKY', 'CVC', 'THETA', 'IOTX', 'QKC', 'AGI', 'NXS', 'DATA', 'SC', 'NPXS', 'KEY', 'NAS', 'MFT', 'DENT', 'ARDR', 'HOT', 'VET', 'DOCK', 'POLY', 'PHX', 'HC', 'GO', 'PAX', 'RVN', 'DCR', 'USDC', 'MITH', 'BCHABC', 'BCHSV', 'REN', 'BTT', 'USDS', 'ONG', 'FET', 'CELR', 'MATIC', 'ATOM', 'PHB', 'TFUEL', 'ONE', 'FTM', 'BTCB', 'ALGO', 'USDSB', 'ERD', 'DOGE', 'DUSK', 'BGBP', 'ANKR', 'WIN', 'COS', 'TUSDB', 'COCOS', 'TOMO', 'PERL', 'CHZ', 'BAND', 'BUSD', 'BEAM', 'XTZ', 'HBAR', 'NKN', 'STX', 'KAVA', 'NGN', 'ARPA', 'CTXC', 'BCH', 'RUB', 'TROY', 'VITE', 'FTT', 'TRY', 'EUR', 'OGN', 'DREP', 'BULL', 'BEAR', 'ETHBULL', 'ETHBEAR', 'TCT', 'WRX', 'LTO', 'EOSBULL', 'EOSBEAR', 'XRPBULL', 'XRPBEAR', 'MBL', 'COTI', 'BNBBULL', 'BNBBEAR', 'STPT', 'ZAR', 'BKRW', 'SOL', 'IDRT', 'CTSI', 'HIVE', 'CHR', 'BTCUP', 'BTCDOWN', 'MDT', 'STMX', 'IQ', 'PNT', 'GBP', 'DGB', 'UAH', 'COMP', 'BIDR', 'SXP', 'SNX', 'ETHUP', 'ETHDOWN', 'ADAUP', 'ADADOWN', 'LINKUP', 'LINKDOWN', 'VTHO', 'IRIS', 'MKR', 'DAI', 'RUNE', 'AUD', 'FIO', 'BNBUP', 'BNBDOWN', 'XTZUP', 'XTZDOWN', 'AVA', 'BAL', 'YFI', 'JST', 'SRM', 'ANT', 'CRV', 'SAND', 'OCEAN', 'NMR', 'DOT', 'LUNA', 'IDEX', 'RSR', 'PAXG', 'WNXM', 'TRB', 'BZRX', 'WBTC', 'SUSHI', 'YFII', 'KSM', 'EGLD', 'DIA', 'UMA', 'EOSUP', 'EOSDOWN', 'TRXUP', 'TRXDOWN', 'XRPUP', 'XRPDOWN', 'DOTUP', 'DOTDOWN', 'BEL', 'WING', 'SWRV', 'LTCUP', 'LTCDOWN', 'CREAM', 'UNI', 'NBS', 'OXT', 'SUN', 'AVAX', 'HNT', 'BAKE', 'BURGER', 'FLM', 'SCRT', 'CAKE', 'SPARTA', 'UNIUP', 'UNIDOWN', 'ORN', 'UTK', 'XVS', 'ALPHA', 'VIDT', 'AAVE', 'BRL', 'NEAR', 'SXPUP', 'SXPDOWN', 'FIL', 'FILUP', 'FILDOWN', 'YFIUP', 'YFIDOWN', 'INJ', 'AERGO', 'EASY', 'AUDIO', 'CTK', 'BCHUP', 'BCHDOWN', 'BOT', 'AKRO', 'KP3R', 'AXS', 'HARD', 'RENBTC', 'SLP', 'CVP', 'STRAX', 'FOR', 'UNFI', 'FRONT', 'BCHA', 'ROSE', 'HEGIC', 'AAVEUP', 'AAVEDOWN', 'PROM', 'SKL', 'SUSD', 'COVER', 'GLM', 'GHST', 'SUSHIUP', 'SUSHIDOWN', 'XLMUP', 'XLMDOWN', 'DF', 'GRT', 'JUV', 'PSG', 'BVND', '1INCH', 'REEF', 'OG', 'ATM', 'ASR', 'CELO', 'RIF', 'BTCST', 'TRU', 'DEXE', 'CKB', 'TWT', 'FIRO', 'BETH', 'PROS', 'LIT', 'VAI', 'SFP', 'FXS', 'DODO', 'UFT', 'ACM', 'AUCTION', 'PHA', 'TVK', 'BADGER', 'FIS', 'OM', 'POND', 'DEGO', 'ALICE', 'BIFI', 'LINA', 'PERP', 'RAMP', 'SUPER', 'CFX', 'EPS', 'AUTO', 'TKO', 'PUNDIX', 'TLM', '1INCHUP', '1INCHDOWN', 'MIR', 'BAR', 'FORTH', 'EZ', 'SHIB', 'ICP', 'AR', 'POLS', 'MDX', 'MASK', 'LPT', 'AGIX', 'NU', 'ATA', 'GTC', 'TORN', 'KEEP', 'ERN', 'KLAY', 'BOND', 'MLN', 'QUICK', 'C98', 'CLV', 'QNT', 'FLOW', 'XEC', 'MINA', 'RAY', 'FARM', 'ALPACA', 'MBOX', 'VGX', 'WAXP', 'TRIBE', 'GNO', 'DYDX', 'USDP', 'GALA', 'ILV', 'YGG', 'FIDA', 'AGLD', 'RAD', 'BETA', 'RARE', 'SSV', 'LAZIO', 'CHESS', 'DAR', 'BNX', 'RGT', 'MOVR', 'CITY', 'ENS', 'QI', 'PORTO', 'JASMY', 'AMP', 'PLA', 'PYR', 'RNDR', 'ALCX', 'SANTOS', 'MC', 'ANY', 'BICO', 'FLUX', 'VOXEL', 'HIGH', 'CVX', 'PEOPLE', 'OOKI', 'SPELL', 'UST', 'JOE', 'ACH', 'IMX', 'GLMR', 'LOKA', 'API3', 'BTTC', 'ACA', 'ANC', 'BDOT', 'XNO', 'WOO', 'ALPINE', 'T', 'ASTR', 'GMT', 'KDA', 'APE', 'BSW', 'MULTI', 'MOB', 'NEXO', 'REI', 'GAL', 'LDO', 'EPX', 'LUNC', 'USTC', 'OP', 'LEVER', 'STG', 'GMX', 'POLYX', 'APT', 'PLN', 'OSMO', 'HFT', 'HOOK', 'MAGIC', 'RON', 'HIFI', 'RPL', 'GFT', 'GNS', 'SYN', 'LQTY', 'ID', 'ARB', 'RDNT', 'ARS', 'EDU', 'SUI', 'PEPE', 'FLOKI', 'WBETH', 'COMBO', 'MAV', 'PENDLE', 'ARKM', 'WLD', 'FDUSD', 'SEI', 'CYBER', 'NTRN', 'TIA', 'MEME', 'ORDI', 'BEAMX', 'VIC', 'BLUR', 'VANRY', 'AEUR', 'JTO', '1000SATS', 'BONK', 'ACE', 'NFP', 'AI', 'XAI', 'MANTA', 'ALT', 'JUP', 'PYTH', 'RONIN', 'DYM', ]

#Global var initialization
arbitrage_data = []
item_count = 0

#Bid and ask prices of currency pairs are saved in 2d array. Base currency is represented by
#rows and quote by columns. Once a price change is recieved, all possible currency pairs
#in the format x->base, base->quote, quote->y are checked to check for a potential arb.
#The speed of the operation is optimized by the utilization of a dictionnary which stores the 
#index of each ticker.
triangle_array_ask = [[-1] * len(single_tickers) for _ in range(len(single_tickers))]
triangle_array_bid = [[-1] * len(single_tickers) for _ in range(len(single_tickers))]

ticker_dict = {}
pair_arr = []
#


for pair in pairs:
    pair_arr.append(pair+"@bookTicker")

def set_up_ticker_dict():
    for idx,elem in enumerate(single_tickers):
        ticker_dict[elem.upper()] = idx

#Setting up the WebSocket connection
async def fetch_book_ticker_data(symbols):
    uri = "wss://stream.binance.com:9443/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"method": "SUBSCRIBE", "params": pair_arr, "id": 1}))
        async for message in websocket:
            data = json.loads(message)
            if "s" in data.keys():
                process_data(data)


def process_data(data):
    symbol = data["s"]
    bid_price = float(data["b"])
    ask_price = float(data["a"])
    idx1 = -1
    idx2 = -1
    ticker1 = ""
    ticker2 = ""

    for length in range(2,len(symbol)):
        if symbol[:length] in ticker_dict and symbol[length:] in ticker_dict:
            idx1 = ticker_dict[symbol[:length]]
            idx2 = ticker_dict[symbol[length:]]
            ticker1 = symbol[:length]
            ticker2 = symbol[length:]
            break

    if idx1!=-1 and idx2 != -1:
        curr_ask = triangle_array_ask[idx1][idx2]
        if curr_ask != ask_price:
            triangle_array_ask[idx1][idx2] = ask_price
            check_arb_full_on_change(idx1,idx2,ticker1,ticker2,bid_ask = 1)

        curr_bid = triangle_array_bid[idx1][idx2]
        if curr_bid != bid_price:
            triangle_array_bid[idx1][idx2] = bid_price
            check_arb_full_on_change(idx1,idx2,ticker1,ticker2,bid_ask = 0)


#Upon price change, we check for the existance of a triangular arbitrage possibilty 
#by trying every possible currency pairs which fit into the following three structures:
#base->quote->other
#other->base->quote
#quote->other->base

def check_arb_full_on_change(base_curr, quote_curr,ticker1,ticker2,bid_ask = 0,):#0 for bid arb, 1 for ask arb
    base_leg_idx = base_curr
    quote_leg_idx = quote_curr
    base_to_quote = -1
    if bid_ask == 0:
        base_to_quote = triangle_array_bid[base_leg_idx][quote_leg_idx] 
    elif bid_ask == 1:
        base_to_quote = triangle_array_ask[base_leg_idx][quote_leg_idx] 

    for other_leg in single_tickers:
        third_leg_idx = ticker_dict[other_leg]
        quote_to_third = -1
        base_to_third = -1

        if bid_ask == 0:
            quote_to_third = triangle_array_bid[quote_leg_idx][third_leg_idx] 
            base_to_third = triangle_array_bid[base_leg_idx][third_leg_idx] 

        elif bid_ask == 1:
            quote_to_third = triangle_array_ask[quote_leg_idx][third_leg_idx] 
            base_to_third = triangle_array_ask[base_leg_idx][third_leg_idx] 
            

        if quote_to_third == -1 or base_to_third == -1:
            continue

        #base->quote->other
        #other->base->quote
        #quote->other->base
        implied_rate = base_to_quote * quote_to_third 
        effective_rate = base_to_third
        ratio = implied_rate/effective_rate
      
        if (ratio > 1 and bid_ask == 0) or (ratio < 1 and bid_ask == 1):
            arbitrage_data.append({
            "Type": "Bid Arb" if bid_ask == 0 else "Ask Arb",
            "Ratio": ratio,
            "Currency_Trio" : sorted([ticker1,ticker2,other_leg]),
            "First_to_Second": f"{ticker1}-{ticker2}",
            "Second_to_Third": f"{ticker2}-{other_leg}",
            "First_to_Third": f"{ticker1}-{other_leg}",
            "Base_to_Quote": base_to_quote,
            "Quote_to_Third": quote_to_third,
            "Base_to_Third": base_to_third,
            "Time":time.time(),
            })


#Below code initializes the async processes and sets up some 
#necessary variables..
async def wait_for_key(task2):
    while True:
        if keyboard.is_pressed('s'):
            task2.cancel()
            print("Data is being saved, please wait")
            break
        await asyncio.sleep(0.001) 

async def main():
    set_up_ticker_dict()    
    task2 = asyncio.create_task(fetch_book_ticker_data(pairs))  
    task1 = asyncio.create_task(wait_for_key(task2))  
    await asyncio.gather(task1, task2, return_exceptions=True) 

    if task1.done() and task2.done():  # Check if both tasks are done
        print("Both tasks completed.")
        return
    elif task2.done():
        task1.cancel()

print("Press 's' to cancel save and quit")
asyncio.run(main())
df = pd.DataFrame(arbitrage_data)
df.to_excel("arbitrage_data2.xlsx", index=False)
print("Data is saved to arbitrage_data.xlsx")
    
