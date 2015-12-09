symbols = ['600848']
start = '2015-01-01'
end = '2015-07-01'
period = '1D'

def handle(highlength=20,lowlength=10):
	symbol = symbols[0]
	if marketposition[symbol] == 0:
		 if high[0]>high[:length]