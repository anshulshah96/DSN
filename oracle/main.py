from flask import Flask
import sqlite3
from flask import jsonify
from flask import g
from flask import request
import pose 

DATABASE = '/tmp/test.db'

app = Flask(__name__)

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

@app.route("/list")
def list():
    list = []
    for user in query_db('select * from challenge'):
        dic = {'address': user[0], 'challenge': user[1], 'size': user[2]}
        list.append(dic)
    return jsonify(users=list)

@app.route("/challenge")
def get_challenge():
    address = request.args.get('adds')
    size = request.args.get('size')
    chal = pose.gen_challenge(size)
    query_db("INSERT INTO challenge VALUES (?,?,?)",[address,chal,size]) # ensure only one
    return jsonify(challenge=chal)

@app.route("/issue")
def issue():
    address = request.args.get('adds')
    solution = request.args.get('sol')
    chal = query_db("SELECT * FROM challenge WHERE address = ?",[address], one=True)
    rec = pose.verify(chal, solution)
    return jsonify(receipt=rec)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=8900)
    print('end')
