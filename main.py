from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv(stream=open('Shh.env'))
import os
from deta import Deta
import random
import string

# I'm sorry for the mess, I'm still learning please don't judge me to bad lol.


detatoken = os.environ.get('DETA_TOKEN')



deta = Deta(detatoken)
santa_lists = deta.Base("santa_lists")

app = Flask(__name__)


def send_sms(number, message):
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        messaging_service_sid='MGa7c75be6043b71ab2cad34bbcc1fd2e2',
        body=message,
        to=number
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list', methods=['GET'])
def santa_list():
    list_id = request.args.get('id')
    real_37list = santa_lists.get(list_id)
    name = real_37list['name']
    gift_list = real_37list['gifts']
    cookie_id = request.cookies.get('id')
    if cookie_id == list_id:
        editor = True
    else:
        editor = False
    return render_template('table.html', name=name, gift_list=gift_list, editor=editor, list_id=list_id)


@app.route('/create', methods=['GET'])
def create():
    return render_template('login.html')


@app.route('/api/create_list', methods=['POST', 'GET'])
def create_list():
    list_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    name = request.form.get('name')
    number = request.form.get('number')
    send_sms(number, f"Your list has been created! The id is {list_name}")
    gifts = []
    santa_lists.put({"list_name": list_name, "name": name, "number": number, "gifts": gifts}, key=list_name)
    resp = redirect(f"/list?id={list_name}")
    resp.set_cookie('id', list_name)
    return resp


@app.route('/api/claim_gift', methods=['POST'])
def add_gift():
    list_id = request.form.get('list_id')
    gift_name = request.form.get('gift_name')
    updated_gifts = santa_lists.get(list_id)['gifts']
    updated_gifts = [x for x in updated_gifts if x['name'] != gift_name]
    santa_lists.update({"gifts": updated_gifts}, key=list_id)
    send_sms(santa_lists.get(list_id)['number'], f"A gift off your list has been claimed!")
    return redirect(f"/list?id={list_id}")


@app.route('/api/add_gift', methods=['POST'])
def claim_gift():
    list_id = request.form.get('list_id')
    gift_name = request.form.get('gift_name')
    gift_link = request.form.get('link')
    gift_price = request.form.get('price')
    updated_gifts = santa_lists.get(list_id)
    updated_gifts['gifts'].append({"name": gift_name, "linkorlocation": gift_link, "price": gift_price})
    santa_lists.put(updated_gifts, key=list_id)
    return redirect(f"/list?id={list_id}")


if __name__ == '__main__':
    app.run()
