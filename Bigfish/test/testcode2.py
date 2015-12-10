symbols = ['600848']
start = '2015-01-01'
end = '2015-07-01'
period = '1D'

def handle(slowlength=20, fastlength=10):
	def max(price,len):
		max = 0
		for index in range(len):
			if price[len]>max:
				max = price[len+1]
	def min(price,len):
		min = 99999999
		for index in range(len):
			if price[len]<min:
				min = price[len+1]
	symbol = symbols[0]
	position = marketposition.get(symbol,None)
	if not position or position == 0:
		if close[0]>=max(high,slowlength):
			buy(symbol)
		if close[0]<=min(low,slowlength):
			short(symbol)
	elif marketposition[symbol] > 0:
		if close[0]<=min(low,fastlength):
			sell(symbol)
	elif marketposition[symbol] < 0:
		if close[0]>=max(high,fastlength):
			cover(symbol)
