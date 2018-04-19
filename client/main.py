from flask import Flask
from flask import request
import sqlite3
from flask import jsonify
from flask import g
from flask import render_template
import os
import json

from remote_contract import RemoteContract
from db_utils import *
import requests

app = Flask(__name__)
DATABASE = '/tmp/clienttest.db'

c_obj = RemoteContract('http://localhost:8545', 'http://172.25.12.128:8900/contract')

@app.route("/", methods=['GET', 'OPTIONS'])
def main():
    return render_template('index.html', selfAddress = c_obj.get_eth_address())

@app.route("/upload", methods=['GET', 'OPTIONS'])
def upload():
	file_path = request.args.get('path')
	provider = request.args.get('provider')
	provider_url = request.args.get('providerurl')
	r_rate = requests.get(provider_url + "/status")
	rate = r_rate.json()['rate']
	r = requests.post(provider_url + "/upload/",
		data = {
			"name": file_path,
			"client": c_obj.get_eth_address()
		},
		files = {"file": open(file_path, 'rb').read()}
	)
	service_num = r.json()['service_num']
	exec_db("INSERT INTO UPLOADS VALUES (?,?,?,?,?)",(file_path, provider_url, provider, rate, service_num))
	return jsonify({"status": r.status_code, "reason": r.reason})

@app.route("/download", methods=['GET', 'OPTIONS'])
def download():
	provider = request.args.get('provider')
	provider_ip = request.args.get('provider_ip')
	service_num = request.args.get('service_num')
	
	# get the download URL
	url = provider_ip # update
	
	return jsonify(url = url)

@app.route("/challenge", methods=['GET', 'OPTIONS'])
def challenge():
	provider = request.args.get('provider')
	provider_ip = request.args.get('provider_ip')
	service_num = request.args.get('service_num')
	file_path = request.args.get('path')

	# chal = encode(file)
	# request answer
	# verify

	return jsonify(result = True)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
def init_db():
    with app.app_context():
        db = get_db()    
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        print("DB Initialized")
def exec_db(query, args=(), one=False):
    cur = get_db()
    con = cur.cursor()
    cur.execute(query,args)
    cur.commit()

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=5500, debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
