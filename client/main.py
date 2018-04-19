from flask import Flask
from flask import request
import sqlite3
from flask import jsonify
from flask import g
from flask import request
from flask import render_template

from contract import remote_contract


app = Flask(__name__)

DATABASE = '/tmp/test.db'

c_obj = RemoteContract('http://172.25.12.128:8545', 'http://172.25.12.128:8900/contract')

@app.route("/")
def main():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()