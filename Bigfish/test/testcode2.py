symbols = ['600848']
start = '2015-01-01'
end = '2015-07-01'
period = '1D'

def handle(slowlength=20, fastlength=10):
	def max(price,len):
		max = 0
		for index in range(len):
			if price[index+1]>max:
				max = price[index+1]
		return(max)
	def min(price,len):
		min = 99999999
		for index in range(len):
			if price[index+1]<min:
				min = price[index+1]
		return(min)

	if barnum > slowlength+1:
		symbol = symbols[0]
		position = marketposition.get(symbol,None)
		print(barnum,position)
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
