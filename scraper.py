from bs4 import BeautifulSoup as bs
import requests
import datetime
import db

class NSEScraper:
	headers = {
		"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
	}

	base = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?instrument=OPTSTK&symbol={}&date={}"
	base_without_date = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?instrument=OPTSTK&symbol={}"

	'''
		DB creds here.
	'''
	#db = db.MSSQLDB(host="127.0.0.1", user="root", passwd="password", database="stock_features", table="ebl_option_data", errored_table="tbl_errored_rows")

	db = db.MSSQLDB(
			conn_string='',
			database='StockOptionAnalysis',
			table='ebl_option_data', 
			errored_table='tbl_errored_rows'
		)

	@classmethod
	def scrape_page_and_save_data(cls, page, symbol, expiry_date):
		soup = bs(page, 'html.parser')

		table = soup.find('table', attrs = {"id" : "octable"})
		rows = table.find_all('tr')

		column_headers_row = rows[1]
		column_headers = [i.text for i in column_headers_row.find_all('th')]

		price = soup.find_all('table')[0].find('tr').find_all('td')[1].find('span').text.split(symbol)[-1].strip()

		current_date = datetime.datetime.now().__str__().split(' ')[0]
		for row in rows[2:-1]:
			values = [i.text for i in row.find_all('td')]
			calls_data = {"calls_" + key: value.strip().replace('\n', '').replace('\t', '') for key, value in zip(column_headers, values[:11]) if key != 'Chart'}
			puts_data = {"puts_" + key: value.strip().replace('\n', '').replace('\t', '') for key, value in zip(column_headers, values[12:]) if key != 'Chart'}

			data = {}

			count = -1
			for key, value in zip(column_headers, values):
				count += 1
				if key == 'Chart':
					continue
				if count < 11:
					data["calls_" + key.lower().replace(' ', '_')] = value.strip().replace('\n', '').replace('\t', '')
				elif count == 11:
					data['strike_price'] = value.strip().replace('\n', '').replace('\t', '')
				else:
					data["puts_" + key.lower().replace(' ', '_')] = value.strip().replace('\n', '').replace('\t', '')
			data['stock_name'] = symbol
			data['expiry_date'] = expiry_date
			data['created_date'] = current_date
			data['stock_price'] = price
			cls.db.insert_data(data=data)

	@classmethod
	def get_expiry_date(cls, page):
		soup = bs(page, 'html.parser')
		options = soup.find('select', attrs = {"id" : "date"})
		for i in options.text.strip().split('\n'):
			if i.lower().strip() != 'select':
				return i
		return False

	@classmethod
	def get_active_stock_names(cls):
		return cls.db.get_active_stock_names()

	@classmethod
	def main(cls):
		symbols = cls.get_active_stock_names()
		try:
			url = cls.base_without_date.format(symbols[0])
			page = requests.get(url=url, headers=cls.headers).text
			expiry_date = cls.get_expiry_date(page)
		except Exception as err:
			exit('[ERROR] Unable to reach NSE site. Reason: {err}'.format(err))
	
		if expiry_date == False:
			exit('[ERROR] Not able to retrieve expiry date. Aborting.')

		today = datetime.datetime.now().__str__()
		for symbol in symbols:
			try:
				url = cls.base.format(symbol, expiry_date)
				page = requests.get(url=url, headers=cls.headers).text
				cls.scrape_page_and_save_data(page=page, symbol=symbol, expiry_date=expiry_date)
			except Exception as err:
				print ('[ERROR] {} errored out. Reason: {}'.format(symbol, err))
				cls.db.insert_errored_stock(stock_name=symbol, created_date=today)

if __name__ == '__main__':
	print ('[INFO] Initialising & Running Scraper...')
	NSEScraper.main()
	print ('[INFO] Done!')



