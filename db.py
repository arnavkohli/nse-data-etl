import mysql.connector
import pyodbc

def stringify(val):
	return '"' + val + '"'

def stringify(val):
	return "'" + val + "'"

class MSSQLDB:
	def __init__(self, conn_string, database, table, errored_table):
		self.database = database
		self.table = table
		self.errored_table = errored_table
		self.db = pyodbc.connect(conn_string)
		self.cursor = self.db.cursor()

	def insert_data(self, data):
		first = "insert into {}.{} (".format(self.database, self.table)
		second = "values ("
		for key, val in data.items():
			if val != '-':
				first += key.lower().replace(' ', '_') + ', '
				second += stringify(val) + ', '
		first = first.strip()[:-1] + ')'
		second = second.strip()[:-1] + ')'
		query = first + " " + second
		print (query)
		self.cursor.execute(query)
		self.db.commit()

	def get_active_stock_names(self):
		query = "select stockname from lkp_future_list where is_active = 1".format(self.database)
		self.cursor.execute(query)
		data = self.cursor.fetchall()
		return [i[0] for i in data]

	def insert_errored_stock(self, stock_name, created_date):
		query = "insert into {} (stock_name, created_date) values ('{}', '{}')".format(self.errored_table, stock_name, created_date)
		self.cursor.execute(query)
		self.db.commit()

class MySQLDB:

	def __init__(self, host, user, passwd, database, table, errored_table):
		self.table = table
		self.errored_table = errored_table
		self.db = mysql.connector.connect(
			host=host, 
			user=user, 
			passwd=passwd, 
			database=database)
		self.cursor = self.db.cursor()

	def insert_data(self, data):
		first = "insert into {} (".format(self.table)
		second = "values ("
		for key, val in data.items():
			if val != '-':
				first += key.lower().replace(' ', '_') + ', '
				second += stringify(val) + ', '
		first = first.strip()[:-1] + ')'
		second = second.strip()[:-1] + ')'
		query = first + " " + second
		self.cursor.execute(query)
		self.db.commit()

	def get_active_stock_names(self):
		query = "select stockname from lkp_future_list where is_active = 1"
		self.cursor.execute(query)
		data = self.cursor.fetchall()
		return [i[0] for i in data]

	def insert_errored_stock(self, stock_name, created_date):
		query = "insert into {} (stock_name, created_date) values ('{}', '{}')".format(self.errored_table, stock_name, created_date)
		self.cursor.execute(query)
		self.db.commit()

if __name__ == '__main__':
	pass
	# db = "stock_features"
	# table = "ebl_option_data"
	# data = {'OI': '300', 'Chng in OI': '-', 'Volume': '-', 'IV': '-', 'LTP': '780.05', 'Net Chng': '-', 'BidQty': '6,900', 'BidPrice': '657.95', 'AskPrice': '902.75', 'AskQty': '6,900', 'Strike Price': '2650.00', 'stock_name': 'HDFC', 'expiry_date': '30JUL2020', 'created_date': '2020-07-06', 'stock_price': '1871.55'}
	# db = MySQLDB(host="127.0.0.1", user="root", passwd="password", database=db, table=table, errored_table='tbl_errored_rows')
	# # db.insert_data(data)
	# # print (db.get_active_stock_names())
	# db.insert_errored_stock('HDFC', '2020-07-06')



