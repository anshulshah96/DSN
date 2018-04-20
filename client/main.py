from flask import Flask
from flask import request
import sqlite3
from flask import jsonify
from flask import g
from flask import render_template
import os
import json
import heartbeat
import hashlib

from remote_contract import RemoteContract
import requests

app = Flask(__name__)
DATABASE = '/tmp/clienttest.db'
ORACLE_URL = 'http://localhost:8900'
c_obj = RemoteContract('http://localhost:8545', 'http://localhost:8900/contract')
beatMap = {}

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route("/", methods=['GET', 'OPTIONS'])
def main():
    uploads = []
    for row in query_db('select * from UPLOADS'):
        dic = { 'file_path': row[0], 'provider_url': row[1],
            'provider': row[2], 'rate': row[3],
            'service_num': row[4]}
        uploads.append(dic)
    r = requests.get(ORACLE_URL + "/list")
    providerlist = r.json()['users']
    # clientpath = os.getcwd()
    clientpath = "/Users/anshul/test.txt"
    return render_template('index.html', selfAddress = c_obj.get_eth_address(), uploads = uploads, 
        rpc_address = 'http://localhost:8545',
        providerlist = providerlist, cwd = clientpath, balance = c_obj.get_eth_balance(c_obj.get_eth_address()))

@app.route("/upload", methods=['GET', 'OPTIONS'])
def upload():
    file_path = request.args.get('path')
    r = requests.get(ORACLE_URL + "/list")
    providerlist = r.json()['users']
    best_provider = providerlist[0]['provider']
    best_provider_url = providerlist[0]['providerurl']
    min_rate = 1000000000
    for provider in providerlist:
        r_rate = requests.get(provider['providerurl'] + "/status")
        rate = r_rate.json()['rate']
        if(rate < min_rate):
            min_rate = rate
            best_provider = provider['provider']
            best_provider_url = provider['providerurl']

    beat = heartbeat.PySwizzle.PySwizzle()
    with open(file_path,'rb') as f:
        (tag,state) = beat.encode(f)
    global beatMap
    fhash = md5(file_path)
    beatMap[file_path] = (beat,tag,state,fhash)
    print(file_path)
    file_size = os.path.getsize(file_path)

    # send file, tag, state to provider
    r = requests.post(best_provider_url + "/upload/",
        data = {
            "name": file_path,
            "client": c_obj.get_eth_address(),
            "size": file_size,
            "tag": json.dumps(tag.todict()),
            "state": json.dumps(state.todict())
        },
        files = {"file": open(file_path, 'rb').read()}
    )
    service_num = r.json()['service_num']
    exec_db("INSERT INTO UPLOADS VALUES (?,?,?,?,?)",(file_path, best_provider_url, 
        best_provider, rate, service_num))
    return jsonify({"status": r.status_code, "reason": r.reason, "service_num": service_num})

@app.route("/download", methods=['GET', 'OPTIONS'])
def download():
    provider = request.args.get('provider')
    provider_ip = request.args.get('provider_ip')
    service_num = request.args.get('service_num')
    
    # get the download URL
    url = provider_ip # update
    
    return jsonify(url = url)

@app.route("/revoke", methods=['GET', 'OPTIONS'])
def revoke():
    provider = request.args.get('provider')
    servicenum = request.args.get('servicenum')
    exec_db("DELETE FROM UPLOADS WHERE provider = ? AND servicenum = ?",(provider, servicenum))
    return jsonify(response = True)

@app.route("/challenge", methods=['GET', 'OPTIONS'])
def challenge():
    provider = request.args.get('provider')
    provider_url = request.args.get('providerurl')
    service_num = request.args.get('servicenum')
    file_path = request.args.get('path')
    rate = request.args.get('rate')

    global beatMap
    (beat,tag,state,fhash) = beatMap[file_path]
    print(json.dumps(beat.todict()))
    print(json.dumps(tag.todict()))
    print(json.dumps(state.todict()))
    chal =  beat.gen_challenge(state)
    payload = {
        'client': c_obj.get_eth_address(),
        'servicenum': service_num,
        'challenge': json.dumps(chal.todict()),
    }
    r = requests.post(provider_url + "/challenge/", data=payload)
    proof = r.json()['proof']
    proof = json.loads(proof)
    phash = r.json()['hash']
    # proof = heartbeat.PySwizzle.Proof.fromdict(proof)
    # result = beat.verify(proof, chal, state)
    # rate = c_obj.get_service(provider, service_num)[3]
    # rate = int(rate)
    # if result:
    #     c_obj.pay_service(provider, service_num, rate)
    result = False
    if phash == fhash:
        result = True
    else:
        print(phash)
        print(fhash)
    print("The proof is: " + str(result))
    return jsonify(result = result)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[len(rv)-1] if rv else None) if one else rv
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
