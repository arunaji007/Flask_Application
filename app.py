import MySQLdb.cursors
from flask_mysqldb import MySQL
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)

app.debug = True

app.secret_key = 700007

app.config['MYSQL_HOST'] = 'localhost'

app.config['MYSQL_USER'] = 'root'

app.config['MYSQL_PASSWORD'] = '601msdZIVA'

app.config['MYSQL_DB'] = 'devops'

mysql = MySQL(app)


@app.route('/')
def main():
    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM question")
    total = cursor.fetchall()
    cursor.execute(
        'SELECT * FROM question order by q_date desc LIMIT %s OFFSET %s', (per_page, offset))
    question = cursor.fetchall()
    row = cursor.rowcount
    pagination = Pagination(page=page, per_page=per_page,
                            offset=offset, total=len(total))
    if question:
        return render_template('index.html', val_questions=question, pagination=pagination)
    return render_template('index.html', pagination=pagination)


@app.route('/', methods=('POST', 'GET'))
def index():
    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    q = request.args.get('q')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM question")
    total = cursor.fetchall()
    name = request.form.get('name')
    question = request.form.get('question')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'INSERT INTO question (Name,Question) VALUES ( % s, % s)', (name, question))
    mysql.connection.commit()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT * FROM question order by q_date desc LIMIT %s OFFSET %s', (per_page, offset))
    question = cursor.fetchall()
    pagination = Pagination(page=page, per_page=per_page,
                            offset=offset, total=len(total))
    return render_template('index.html', val_questions=question, pagination=pagination)


@app.route('/<name>/<qs>/', methods=('GET', 'POST'))
def delete_qs(name, qs):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT id from question where Name=%s and Question=%s', (name, qs))
    data = cursor.fetchone()
    id = data['id']
    cursor.execute(
        'DELETE FROM answers WHERE qid = %s', str(id))
    cursor.execute(
        'DELETE FROM question WHERE Name = %s and Question = %s', (name, qs))
    mysql.connection.commit()
    per_page = 3
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    q = request.args.get('q')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM question")
    total = cursor.fetchall()
    cursor.execute(
        'SELECT * FROM question order by q_date desc LIMIT %s OFFSET %s', (per_page, offset))
    question = cursor.fetchall()
    pagination = Pagination(page=page, per_page=per_page,
                            offset=offset, total=len(total))
    return render_template('index.html', val_questions=question, pagination=pagination)


@app.route('/<name>/<qs>/update', methods=('GET', 'POST'))
def update_qs(name, qs):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT Name, Question FROM question where Name = %s and Question = %s ', (name, qs))
    update_data = cursor.fetchone()
    if request.method == 'POST':
        per_page = 3
        page = request.args.get(get_page_parameter(), type=int, default=1)
        offset = (page - 1) * per_page
        q = request.args.get('q')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM question")
        total = cursor.fetchall()
        qs1 = request.form['question']
        cursor.execute(
            'UPDATE question SET  Question = %s where  Name = %s and Question = %s ', (qs1, update_data['Name'], update_data['Question']))
        mysql.connection.commit()
        cursor.execute(
            'SELECT * FROM question order by q_date desc LIMIT %s OFFSET %s', (per_page, offset))
        question = cursor.fetchall()
        pagination = Pagination(page=page, per_page=per_page,
                                offset=offset, total=len(total))
        return render_template('index.html', val_questions=question, pagination=pagination)
    return render_template('update.html', update_data=update_data)


@app.route("/<int:qid>/answer", methods=('POST', 'GET'))
def get_answers(qid):
    if request.method == 'POST':
        per_page = 3
        page = request.args.get(get_page_parameter(), type=int, default=1)
        offset = (page - 1) * per_page
        q = request.args.get('q')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM question")
        total = cursor.fetchall()
        answer = request.form.get('answer')
        name = request.form.get('name')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'INSERT INTO answers (Name, Answers, qid)VALUES(%s,%s,%s)', (name, answer, qid))
        mysql.connection.commit()
        cursor.execute(
            'SELECT * FROM question order by q_date desc LIMIT %s OFFSET %s', (per_page, offset))
        question = cursor.fetchall()
        pagination = Pagination(page=page, per_page=per_page,
                                offset=offset, total=len(total))
        return render_template('index.html', val_questions=question, pagination=pagination)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(type(qid))
    cursor.execute(
        'SELECT Name, Answers FROM answers where qid = %s order by a_date desc', str(qid))
    data = cursor.fetchall()
    print(data)
    return render_template('answer.html', data=data, qid=qid)


app.run(use_reloader=True)
