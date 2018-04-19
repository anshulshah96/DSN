from flask import Flask
from flask import request
import sqlite3
from flask import jsonify
from flask import g
from flask import render_template

from remote_contract import RemoteContract
from db_utils import *

app = Flask(__name__)

DATABASE = '/tmp/test.db'

c_obj = RemoteContract('http://172.25.12.128:8545', 'http://172.25.12.128:8900/contract')

@app.route("/", methods=['GET', 'OPTIONS'])
def main():
    return render_template('index.html', selfAddress = c_obj.get_eth_address())

@app.route("/upload", methods=['GET', 'OPTIONS'])
def upload():
	file_path = request.args.get('path')
	provider = request.args.get()
	provider_path = request.args.get('provider_path')
	r = requests.post(provider_path + "/upload", 
		files = {'upload_file': open(path,'rb')},
		client = c_obj.get_eth_address())
	exec_db("INSERT INTO UPLOADS VALUES (?,?,?)",(file_path, provider_path, size))
	service_num = r.json()['service_num']
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
def download():
	provider = request.args.get('provider')
	provider_ip = request.args.get('provider_ip')
	service_num = request.args.get('service_num')
	file_path = request.args.get('path')

	# chal = encode(file)
	# request answer
	# verify

	return jsonify(result = True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True