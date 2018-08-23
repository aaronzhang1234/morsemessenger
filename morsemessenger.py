'''
morse
'''

import pusher
import random
import datetime
import psycopg2 
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import json

app = Flask(__name__)
app.config.from_object(__name__)
conf = json.load(open('config.json', 'r'))
app.config.update(dict(
    SECRET_KEY=conf['secret_key'],
    USERNAME = conf['username'],
    PASSWORD = conf['password']
))
app.config.from_envvar('FLASKR_SETTINGS', silent= True)

@app.route('/')
def main_page():
    if session.get('channel') and session.get('event'):
        conn = psycopg2.connect("dbname=morsemessenger user=morse password="+conf['morse_pass']+"")
        cur = conn.cursor()
        cmd = 'SELECT message FROM message WHERE channel=%s AND event=%s ORDER BY id'
        cur.execute(cmd, (session['channel'], session['event']))
        morses = cur.fetchall()
        cur.close()
        conn.close()
        data = {'channel': session.get('channel'), 'event':session.get('event'), 'key':conf['pusher_key']}
        return render_template('morsemessenger.html', morses=morses, data = data)
    else:
        return render_template('morsemessenger.html')

@app.route('/join', methods=['POST'])
def joinchannel():
    session['channel'] = request.form['channel']
    session['event'] = request.form['event']
    session['intalks'] = True
    return redirect(url_for('main_page'))

@app.route('/send', methods=['POST'])
def send_morse():
    pusher_client = pusher.Pusher(
        app_id=conf['pusher_id'],
        key=conf['pusher_key'],
        secret=conf['pusher_secret'],
        cluster='mt1',
        ssl=True
    )
    conn = psycopg2.connect("dbname=morsemessenger user=morse password="+conf['morse_pass']+"")
    cur = conn.cursor()
    cmd = "insert into message(channel, event, message) values(%s, %s, %s)"
    cur.execute(cmd, (session['channel'], session['event'], request.form['message']))
    conn.commit()
    pusher_client.trigger(session['channel'], session['event'], {'message':request.form['message']})
    cur.close()
    conn.close()
    return redirect(url_for('main_page'))

@app.route('/leave')
def leaveroom():
    session.pop('channel', None)
    session.pop('event', None)
    session.pop('intalks', None)
    return redirect(url_for('main_page'))
 
if __name__ == "__main__":
    app.run(host='0.0.0.0')
