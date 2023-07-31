from flask import Flask, render_template, redirect, url_for, flash, request
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
import requests
import csv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APP_KEY")
Bootstrap5(app)

API_KEY = os.environ.get("STOCK_KEY")
market_url = "http://api.marketstack.com/v1/eod?"  # /intraday(with symbols) ,
# no symbols needed => /tickers, /exchanges, /currencies, /timezones
# ex: http://api.marketstack.com/v1/eod?access_key=YOUR_ACCESS_KEY&symbols=AAPL
''' // optional parameters: 
    & sort = DESC
    & date_from = YYYY-MM-DD
    & date_to = YYYY-MM-DD
    & limit = 100
    & offset = 0 '''

symbols = []
names = []
countries = []
with open("stocks.csv") as dt:
    data = csv.reader(dt)
    for n in data:
        if n[0] != "symbol" and n[1] != "name" and n[2] != "country":
            symbols.append(n[0])
            names.append(n[1])
            countries.append(n[2])

complete_stock = []
for nbr in range(len(symbols)):
    stock = [names[nbr], symbols[nbr], countries[nbr]]
    complete_stock.append(stock)


class Form(FlaskForm):  # list "symbols" in alphabetical order => sorted(symbols, key=str.swapcase)
    symbol = SelectField("Symbol", choices=sorted(symbols, key=str.swapcase), validators=[DataRequired()])
    date_from = DateField("Date From", validators=[DataRequired()])
    date_to = DateField("Date To", validators=[DataRequired()])
    submit = SubmitField("Confirm")


@app.route('/', methods=['GET', 'POST'])
def home():
    form = Form()
    if form.validate_on_submit():

        params = {
            "access_key": API_KEY,
            "symbols": form.symbol.data,
            "sort": "DESC",
            "date_from": form.date_from.data,
            "date_to": form.date_to.data,
            "offset": 0
        }

        try:
            response = requests.get(market_url, params=params)
        except requests.exceptions.ConnectionError:
            flash("No connection.\n Please check your internet and try again!")
            return redirect(url_for('home'))

        response.raise_for_status()
        data_raw = response.json()
        data_origin = data_raw['data']

        data_dic = {}
        for element in data_origin:
            data_dic['date'] = element['date'].split('T')[0]
            data_dic['symbol'] = element['symbol']
            data_dic['open'] = element['open']
            data_dic['adj_open'] = element['adj_open']
            data_dic['close'] = element['close']
            data_dic['adj_close'] = element['adj_close']
            data_dic['high'] = element['high']
            data_dic['adj_high'] = element['adj_high']
            data_dic['low'] = element['low']
            data_dic['adj_low'] = element['adj_low']
            data_dic['volume'] = element['volume']
            data_dic['adj_volume'] = element['adj_volume']

            data_dic['dividend'] = element['dividend']
            data_dic['exchange'] = element['exchange']

        data_list = []
        for name, value in data_dic.items():
            formatted_data = f'{name}: {value}'
            data_list.append(formatted_data)

        if not data_list:
            flash("The market is closed on weekend! \nPlease select a weekday, except today.")
            return redirect(url_for('home'))

        return render_template("index.html", data=data_list, form=form)
    return render_template("index.html", form=form)


@app.route("/check-stock")
def check_stock():
    complete_data = complete_stock
    return render_template("checker.html", complete_data=complete_data)


@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == 'POST':
        searched_stock = request.form["search"]
        all_stocks = complete_stock
        list_searched_stock = []
        for single_stock in all_stocks:
            if searched_stock.lower() in single_stock[0].lower() or searched_stock.lower() in single_stock[1].lower() \
                    or searched_stock.lower() in single_stock[2].lower():
                list_searched_stock.append(single_stock)

        if not list_searched_stock:
            flash(f'Sorry, we don\'t have any record for "{searched_stock}".')

        return render_template("checker.html", complete_data=list_searched_stock)


if __name__ == "__main__":
    app.run(debug=True)
