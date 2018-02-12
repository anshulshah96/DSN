from flask import Flask
from flask import request
import sqlite3
from flask import jsonify
from flask import g
from flask import request
import pose 
from contract import Contract

DATABASE = '/tmp/test.db'

app = Flask(__name__)
c_obj = Contract('http://localhost:8545', 'DSN.sol')

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

@app.route("/list")
def list():
    list = []
    for provider in query_db('select * from challenge'):
        dic = {'address': provider[0], 'challenge': provider[1], 'size': provider[2]}
        list.append(dic)
    return jsonify(users=list)

@app.route("/challenge")
def get_challenge():
    address = request.args.get('adds')
    size = request.args.get('size')
    chal = pose.gen_challenge(size)
    exec_db("INSERT INTO challenge VALUES (?,?,?)",(address,chal,size)) # ensure only one
    return jsonify(challenge=chal)

@app.route("/issue")
def issue():
    address = request.args.get('adds')
    solution = request.args.get('sol')
    provider = query_db("SELECT * FROM challenge WHERE address = ?",[address], one=True)
    rec = pose.verify(provider[1], provider[2], solution)
    if(rec):
        c_obj.issueToken(provider[0], provider[2], request.remote_addr, 0, 440000)
    return jsonify(receipt=rec)

@app.route("/contract")
def contract():
    contract_address = c_obj.get_contract_address()
    contract_abi = c_obj.get_contract_abi()
    return jsonify(address=contract_address, abi=contract_abi)

if __name__ == "__main__":
    # c_obj.issueToken('0xd3CDA913deB6f67967B99D67aCDFa1712C293601', 10, "192.168.12.1", 0, 440000)
    # print c_obj.getSToken('0xd3CDA913deB6f67967B99D67aCDFa1712C293601')
    init_db()
    app.run(host='0.0.0.0', port=8900)
    print('end')
