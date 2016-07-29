from flask import Flask, render_template, request, redirect
import requests, json
from bs4 import BeautifulSoup
import math


app = Flask(__name__)

@app.route("/")
def homepage(name='', body='', balance='', second_body=''):
    author = "Geoffrey"
    return render_template('index.html', author=author, name=name, body=body, balance=str(balance), second_body=second_body)

def get_prices():
    
    response = requests.get('https://poloniex.com/public?command=returnTicker')
    tickers = json.loads(response.text)
    last_price_steem = float(tickers[u'BTC_STEEM'][u'last'])
    last_price_usd = float(tickers[u'USDT_BTC'][u'last'])
    return last_price_usd, last_price_steem


@app.route("/account_balance_num/<path:account_name>")
def balance_num(account_name):

    account_info = requests.get('https://steemit.com/' + account_name + '/transfers')
    soup = BeautifulSoup(account_info.text,'html.parser')
    steem_tags = soup.findAll('div',{'class':'UserWallet__balance row'})
    steem_balance_str = steem_tags[1].select('div.column')[1].string
    steem_balance = float(steem_balance_str.split(' ')[0].replace(',',''))
    
    return str(steem_balance)
    
    
@app.route("/account_balance/<path:account_name>")
def balance(account_name):

    account_info = requests.get('https://steemit.com/' + account_name + '/transfers')
    soup = BeautifulSoup(account_info.text,'html.parser')
    steem_tags = soup.findAll('div',{'class':'UserWallet__balance row'})
    steem_balance_str = steem_tags[1].select('div.column')[1].string
    steem_balance = float(steem_balance_str.split(' ')[0].replace(',',''))
    
    return 'Account: ' + account_name + ', Balance: ' + str(steem_balance) + ' Steem'
    
    
@app.route("/daily_reward/<path:account_name>")
def daily_reward(account_name):
    
    curation_info = requests.get('https://steemit.com/' + account_name + '/curation-rewards')
    soup = BeautifulSoup(curation_info.text,'html.parser')
    
    full_balance = balance_num(account_name)
    
    steem_tags = soup.findAll('div',{'class':'UserWallet__balance row'})
    steem_balance_str = steem_tags[2].select('div.column')[1].string
    steem_balance = float(steem_balance_str.split(' ')[0].replace(',',''))
    
    last_price_usd, last_price_steem = get_prices()
    
    steem_value = "{0:.2f}".format(steem_balance * last_price_steem * last_price_usd / 7)
    
    return_str = ('<p>Account: <u>' + account_name + '</u>, balance: <u>' + str(full_balance) + '</u> STEEM POWER</p><p>Last week\'s average reward: <u>' + str(steem_balance / 7) + '</u> STEEM POWER / day.</p><p>' + 'Average daily value of last week''s reward: $<u>' + steem_value + '</u></p>')
    
    return return_str
    
    
@app.route("/daily_reward_num/<path:account_name>")
def daily_reward_num(account_name):
    
    curation_info = requests.get('https://steemit.com/' + account_name + '/curation-rewards')
    soup = BeautifulSoup(curation_info.text,'html.parser')
    steem_tags = soup.findAll('div',{'class':'UserWallet__balance row'})
    steem_balance_str = steem_tags[2].select('div.column')[1].string
    steem_balance = float(steem_balance_str.split(' ')[0].replace(',',''))
    
    last_price_usd, last_price_steem = get_prices()
    
    steem_value = "{0:.2f}".format(steem_balance * last_price_steem * last_price_usd / 7)
    
    return str(steem_balance * last_price_steem * last_price_usd / 7)
    
    
@app.route("/approximate_reward/<path:identifier>")
def approximate_reward(identifier):
    
    idpath = str(identifier).split('/')
    account_name = idpath[0]
    new_balance = float(idpath[1])
    
    present_daily_reward = float(daily_reward_num(account_name))
    present_balance = float(balance_num(account_name))
    balance_difference = new_balance - present_balance
    
    reward_increase = (balance_difference / present_balance) ** 2
    
    new_reward = math.copysign(1,balance_difference) * present_daily_reward * reward_increase + present_daily_reward

        
    last_price_usd, last_price_steem = get_prices()

    steem_value = "{0:.2f}".format(new_reward * last_price_steem * last_price_usd)
    
    true_steem_value = new_reward / last_price_steem / last_price_usd

    new_reward = "{0:.2f}".format(new_reward)

    return str('<p>New daily reward: <u>' + str(true_steem_value) + '</u> STEEM POWER, worth: $<u>' + new_reward + '</u></p>')
    
    
@app.route("/approximate_reward_num/<path:identifier>")
def approximate_reward_num(identifier):
    
    idpath = str(identifier).split('/')
    account_name = idpath[0]
    new_balance = float(idpath[1])
    
    present_daily_reward = float(daily_reward_num(account_name))
    present_balance = float(balance_num(account_name))
    balance_difference = new_balance - present_balance
    
    reward_increase = (balance_difference / present_balance)*2
    
    new_reward = math.copysign(1,balance_difference) * present_daily_reward * reward_increase + present_daily_reward
    
    return str(new_reward)


@app.route('/submit_form', methods = ['POST'])
def get_account_form():
    
    account_name = request.form['Account Name']
    
    output = daily_reward(account_name)
    
    if account_name:
        print(output)
        return homepage(account_name,output)
    else:
        redirect('/');
    
    
@app.route('/submit_form2', methods = ['POST'])
def est_new_balance_form():
    
    account_name = request.form['Account Name']
    
    oldbody = daily_reward(account_name)
    
    new_balance = request.form['New Steem Balance']
    
    output = approximate_reward(account_name + '/' + str(new_balance))
    
    if account_name:
        print(output)
        return homepage(account_name, oldbody, new_balance, output)
    else:
        redirect('/');


if __name__ == "__main__":
	 # Bind to PORT if defined, otherwise default to 5000.
	 port = int(os.environ.get('PORT', 5000))
	 app.run(host='0.0.0.0', port=port)