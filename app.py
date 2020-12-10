from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
from bokeh.embed import components
from bokeh.plotting import figure


app = Flask(__name__)

def plot_stock(ticker):
	key = '1TYLQ0WKLRDCB29V' # is there a proper way to hide the key? 
	url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}'.format(ticker, key)
	response = requests.get(url).json()
	error_message,month,year = '','',''
	month_dict = dict(zip(range(1,12),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']))
	if 'Error Message' in response:
		error_message = 'Error: Ticker Symbol Not Found!'
		p = figure(x_axis_type="datetime", title=ticker+' (NOT FOUND!)', plot_height=350, plot_width=800)
	else:
		df = pd.DataFrame(response['Time Series (Daily)']).T
		df.index = pd.to_datetime(df.index)
		month = month_dict[df.index[30].month] # get month
		print(month)
		year = df.index[30].year
		plot_title = ticker.upper()+': '+'('+month + ' ' + str(year)+')'
		s = pd.to_numeric(df['5. adjusted close'][(df.index.month==df.index[30].month) & (df.index.year==year)])
		p = figure(x_axis_type="datetime", title=plot_title, plot_height=350, plot_width=800)
		p.xgrid.grid_line_color=None
		p.ygrid.grid_line_alpha=0.5
		p.xaxis.axis_label = 'Time'
		p.yaxis.axis_label = 'Value'
		p.line(s.index, s)
	return p,error_message,month,year

@app.route('/')
def index():
	return render_template('stock.html')

		
@app.route('/graph',methods=['GET','POST'])
def graph():
	ticker = request.form['stock_pick']
	p,error_message,month,year = plot_stock(ticker)
	script, div =components(p)
	kwargs = {'script':script,'div':div}
	kwargs['title'] = 'Stock Display'
	kwargs['error_message'] = error_message
	return render_template('graph.html',**kwargs)



if __name__ == '__main__':
  app.run(port=33507,debug=False)
