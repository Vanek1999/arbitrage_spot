# -----Разраб: ento_Vanek-----
import eel
import aiohttp
import asyncio
from os import system
from json import loads
from requests import post
from itertools import product


urls = ["https://api.binance.com/api/v3/ticker/bookTicker", "https://api.bybit.com/spot/quote/v1/ticker/book_ticker",
	"https://api.huobi.pro/market/tickers", "https://sapi.xt.com/v4/public/ticker", "https://www.okx.com/api/v5/market/tickers?instType=SPOT",
	"https://www.binance.com/api/v3/exchangeInfo", "https://sapi.xt.com/v4/public/symbol"]

# -----Вычисление неактуальных связок binance-----
async def get_not_valid_pairs_binance(resp) -> list:
	return [pair["symbol"] for pair in resp["symbols"] if pair["status"] == "BREAK"]

async def get_not_valid_pairs_xt(resp) -> list:
	return [pair["symbol"].upper().replace("_", "") for pair in resp["result"]["symbols"] if pair["state"] == "DELISTED"]

# -----Проверка монет-----
async def desired_coins(answer_dict: dict, name_symbol: str, bidPrice: str, bidQty: str, askPrice: str, askQty: str) -> list:
	return [({"symbol": pair[name_symbol].upper().replace("-", "").replace("_", ""), "bidPrice": pair[bidPrice], "bidQty": pair[bidQty],
			"askPrice": pair[askPrice], "askQty": pair[askQty]}) for pair in answer_dict]

# -----Рассчитываем валидность-----
async def get_validity(price_1: float, price_2: float, bidQty: float, askQty: float, wallet: int = 400) -> float:
	# пиздят апи с объёмом
	if (price_1 != 0 and price_2 != 0 and wallet <= float(price_2) * float(bidQty) and wallet <= float(price_1) * float(askQty)):
		amount_coin = wallet / price_1 * price_2
		if amount_coin > wallet:
			return round((amount_coin - wallet) / wallet * 100, 3)

async def get_valid(pair1: dict, pair2: dict, pair_name: str, name_ex_first: str, name_ex_second: str, spred: dict, deposit: int):
	calc_spred = await get_validity(float(pair1["askPrice"]), float(pair2["bidPrice"]), pair1["bidQty"], pair2["askQty"], deposit)
	if (calc_spred):
		if (calc_spred < 15):
			spred[calc_spred] = f"Pair: {pair_name}<br>{name_ex_first}➡{name_ex_second}<br>{pair1['askPrice']}➡{pair2['bidPrice']}<br>Spred: ≈{calc_spred}%"
	
	calc_spred2 = await get_validity(float(pair2["askPrice"]), float(pair1["bidPrice"]), pair2["bidQty"], pair1["askQty"], deposit)
	if (calc_spred2):
		if (calc_spred2 < 15):
			spred[calc_spred2] = f"Pair: {pair_name}<br>{name_ex_second}➡{name_ex_first}<br>{pair2['askPrice']}➡{pair1['bidPrice']}<br>Spred: ≈{calc_spred2}%"

# -----Разница бирж-----
async def stock_exchange(pairs_first: dict, pairs_second: dict, name_ex_first: str, name_ex_second: str, spred: dict, deposit: int) -> None:	
	for pair1, pair2 in product(pairs_first, pairs_second):
		if (pair1["symbol"] == pair2["symbol"]):
			await get_valid(pair1, pair2, pair1["symbol"], name_ex_first, name_ex_second, spred, deposit)

# -----Берём нужные данные-----
def heandler(resp, url):
	if (url == "https://api.binance.com/api/v3/ticker/bookTicker"):
		return "pairs_binance", loads(resp)
	elif (url == "https://api.bybit.com/spot/quote/v1/ticker/book_ticker"):
		return "pairs_bybit", loads(resp)
	elif (url == "https://api.huobi.pro/market/tickers"):
		return "pairs_huobi", loads(resp)
	elif (url == "https://sapi.xt.com/v4/public/ticker"):
		return "pairs_xt", loads(resp)
	elif (url == "https://www.okx.com/api/v5/market/tickers?instType=SPOT"):
		return "pairs_okx", loads(resp)

	elif (url == "https://api.telegram.org/bot5709615986:AAEFinXei7NX-4DR_E1-OqslYgBLueYTplU/getUpdates"):
		return "deposit", loads(resp)
	elif (url == "https://sapi.xt.com/v4/public/symbol"):
		return "not_valid_pairs_xt", loads(resp)
	elif (url == "https://www.binance.com/api/v3/exchangeInfo"):
		return "not_valid_pairs_binance", loads(resp)

# -----Сравниваем данные-----
async def get_spred(resp, deposit) -> None:
	for requests in resp:
		if (requests[0] == "pairs_binance"):
			pairs_binance = await desired_coins(requests[1], "symbol", "bidPrice", "bidQty", "askPrice", "askQty")
		elif (requests[0] == "pairs_bybit"):
			pairs_bybit = await desired_coins(requests[1]["result"], "symbol", "bidPrice", "bidQty", "askPrice", "askQty")
		elif (requests[0] == "pairs_huobi"):
			pairs_huobi = await desired_coins(requests[1]["data"], "symbol", "bid", "bidSize", "ask", "askSize")
		elif (requests[0] == "pairs_xt"):
			pairs_xt = await desired_coins(requests[1]["result"], "s", "bp", "bq", "ap", "aq")
		elif (requests[0] == "pairs_okx"): 
			pairs_okx = await desired_coins(requests[1]["data"], "instId", "bidPx", "bidSz", "askPx", "askSz")
		elif (requests[0] == "not_valid_pairs_xt"):
			not_valid_pairs_xt = await get_not_valid_pairs_xt(requests[1])
		elif (requests[0] == "not_valid_pairs_binance"):
			not_valid_pairs_binance = await get_not_valid_pairs_binance(requests[1])
	# -----Убираем неактуальные связки-----
	pairs_binance = [pair for pair in pairs_binance if pair["symbol"] not in not_valid_pairs_binance]
	pairs_xt = [pair for pair in pairs_xt if pair["symbol"] not in not_valid_pairs_xt]
	spred = {}

	await stock_exchange(pairs_binance, pairs_bybit, "binance", "bybit", spred, deposit)
	await stock_exchange(pairs_binance, pairs_huobi, "binance", "huobi", spred, deposit)
	await stock_exchange(pairs_xt, pairs_binance, "xt", "binance", spred, deposit)
	await stock_exchange(pairs_okx, pairs_binance, "okx", "binance", spred, deposit)
	await stock_exchange(pairs_bybit, pairs_huobi, "bybit", "huobi", spred, deposit)
	await stock_exchange(pairs_xt, pairs_huobi, "xt", "huobi", spred, deposit)
	await stock_exchange(pairs_okx, pairs_huobi, "okx", "huobi", spred, deposit)
	await stock_exchange(pairs_xt, pairs_bybit, "xt", "bybit", spred, deposit)
	await stock_exchange(pairs_okx, pairs_bybit, "okx", "bybit", spred, deposit)
	await stock_exchange(pairs_okx, pairs_xt, "okx", "xt", spred, deposit)

	# -----Отправляем обновлённые данные-----
	message = ""
	if (spred):
		for value in sorted(spred.keys(), reverse=True):
			message += "\n" + spred[value]
	else:
		message = "There are no arbitrage situations!"
		
	spred.clear()
	return message

# -----Получаем инфу о каждой паре-----
async def get(url):
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			return heandler(await resp.read(), str(resp.url))

# -----Запуск анализа рынков-----
@eel.expose
def test(deposit):
	loop = asyncio.new_event_loop()
	coroutines = [loop.run_until_complete(get(url)) for url in urls]
	return asyncio.run(get_spred(coroutines, int(deposit)))

if __name__ == '__main__':
	# -----Запуск GUI-----
	eel.init('front')
	eel.start('index.html', mode="default", size=(760, 760))
