# -*- coding: utf-8 -*-

from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, request, session, url_for, redirect, render_template, g

a = None
b = None
c = None
cal = None

# configuration
DATABASE = 'exam.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('exam_SETTINGS', silent=True)


def connect_db():
    """Returns a new connection to the database."""
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.before_request
def before_request():
    """Make sure we are connected to the database each request and look
    up the current user so that we know he's there.
    """
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.subject = query_db('select * from subject where subject_id = ?',
                          [session['subject_id']], one=True)


@app.teardown_request
def teardown_request(exception):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def layout():
    return render_template('layout.html')


@app.route('/memo1')
def memo1():
    return render_template('memo1.html')


@app.route('/memo2')
def memo2():
    return render_template('memo2.html')


@app.route('/memo3')
def memo3():
    return render_template('memo3.html')


@app.route('/sessions')
def sessions():
    global a
    global b
    global c
    global cal

    if a is not None:
        if b is not None:
            if cal == '+':
                c = str(float(a) + float(b))
            elif cal == '-':
                c = str(float(a) - float(b))
            elif cal == '*':
                c = str(float(a) * float(b))
            elif cal == '/':
                c = str(float(a) / float(b))
            else:
                cal = None
    return render_template('sessions.html', num=a, num2=b, num3=c, cal=cal)


@app.route('/calculate', methods=['POST'])
def calculate2():
    global a
    global b
    global cal

    if 'plus' in request.form:
        cal = '+'
    elif 'minus' in request.form:
        cal = '-'
    elif 'prod' in request.form:
        cal = '*'
    elif 'div' in request.form:
        cal = '/'
    else:
        cal = None

    if request.method == 'POST':
        if request.form['num'] != '' and request.form['num2'] != '':
            a = request.form['num']
            b = request.form['num2']
            return redirect(url_for('sessions'))
        else:
            a = request.form['num']
            b = request.form['num2']
            if a == '':
                if b == '':
                    a = None
                    b = None
                else:
                    a = None
            else:
                b = None
            return redirect(url_for('sessions'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)