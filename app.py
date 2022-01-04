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


@app.route('/<name>/<qs>/delete', methods=('GET', 'POST'))
def delete_qs(name, qs):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT id from question where Name=%s and Question=%s', (name, qs))
    data = cursor.fetchone()
    id = data['id']
    cursor.execute('SELECT * FROM answers where qid=%s', [id])
    ans = cursor.fetchall()
    no_ans = len(ans)
    if no_ans > 0:
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
    return redirect('/')


@ app.route('/<name>/<qs>/update', methods=('GET', 'POST'))
def update_qs(name, qs):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT Name, Question FROM question where Name = %s and Question = %s ', (name, qs))
    update_data = cursor.fetchone()
    if request.method == 'POST':
        per_page = 3
        page = request.args.get(get_page_parameter(), type=int, default=1)
        offset = (page - 1) * per_page

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM question")
        total = cursor.fetchall()
        as1 = request.form['name']
        qs1 = request.form['question']
        cursor.execute(
            'UPDATE question SET  Question = %s, Name = %s where  Name = %s and Question = %s ', (qs1, as1, update_data['Name'], update_data['Question']))
        mysql.connection.commit()
        cursor.execute(
            'SELECT * FROM question order by q_date desc LIMIT %s OFFSET %s', (per_page, offset))
        question = cursor.fetchall()
        pagination = Pagination(page=page, per_page=per_page,
                                offset=offset, total=len(total))
        return redirect('/')
        return render_template('index.html', val_questions=question, pagination=pagination)
    return render_template('update.html', update_data=update_data)


@ app.route("/<int:qid>/answer", methods=('POST', 'GET'))
def get_answers(qid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT id,Name, Answers FROM answers where qid = %s', (str(qid)))
    update_data = cursor.fetchone()
    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        per_page = 4
        page = request.args.get(get_page_parameter(), type=int, default=1)
        offset = (page - 1) * per_page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM answers where qid = %s", [qid])
        total = cursor.fetchall()
        pagination = Pagination(page=page, per_page=per_page,
                                offset=offset, total=len(total))
        ns1 = request.form['name']
        as1 = request.form['answer']
        cursor.execute(
            'INSERT into answers(Name, Answers, qid) values(%s,%s,%s) ', (ns1, as1, qid))
        mysql.connection.commit()
        cursor.execute(
            'SELECT * FROM answers where qid = %s order by a_date desc LIMIT %s OFFSET %s', (qid, per_page, offset))
        answer = cursor.fetchall()
        cursor.execute(
            'SELECT Question FROM question where id = %s ', str(qid))
        ques = cursor.fetchone()

        if type(update_data) == None:
            update_data['qid'] = qid
        return render_template('answer.html', data=answer, qid=qid, pagination=pagination, ques=ques, update_data=update_data)

    if type(update_data) == None:
        update_data['qid'] = qid

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    per_page = 4
    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset = (page - 1) * per_page
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM answers where qid = %s", [qid])
    total = cursor.fetchall()
    pagination = Pagination(page=page, per_page=per_page,
                            offset=offset, total=len(total))
    cursor.execute(
        'SELECT * FROM answers where qid = %s order by a_date desc LIMIT %s OFFSET %s', (qid, per_page, offset))
    data = cursor.fetchall()
    data = list(data)

    cursor.execute(
        'SELECT Question,id FROM question where id = %s ', str(qid))
    ques = cursor.fetchone()
    for i in range(len(data)):
        data[i]['qid'] = qid

    return render_template('answer.html', data=data, update_data=update_data, qid=qid, ques=ques, pagination=pagination)


@ app.route('/<int:id>/<name>/<ans>/<int:qid>/ansupdate', methods=('GET', 'POST'))
def update_as(name, ans, id, qid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT * FROM answers where Name = %s and Answers = %s and qid = %s', (name, ans, (qid)))
    update_data = cursor.fetchone()

    cursor.execute(
        'SELECT Question FROM question where id = %s ', [id])
    dat_q = cursor.fetchone()
    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        as1 = request.form['name']
        qs1 = request.form['answer']
        cursor.execute(
            'UPDATE answers SET  Answers = %s, Name = %s where  Name = %s and Answers = %s and id=%s ', (qs1, as1, name, ans, [id]))
        mysql.connection.commit()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sid = str(id)
        cursor.execute(
            'SELECT qid FROM answers where id = %s ', [sid])
        ques = cursor.fetchall()
        cursor.execute(
            'SELECT * FROM answers where qid = %s order by a_date desc ', (str(qid)))
        update_data = cursor.fetchall()
        cursor.execute(
            'SELECT Question FROM question where id = %s ', [ques[0]['qid']])
        ques1 = cursor.fetchone()

        return redirect('/'+str(ques[0]['qid'])+'/answer')
        return render_template('answer.html', update_data=update_data, ques=ques1, qid=qid, data=update_data)
    sid = str(id)
    cursor.execute(
        'SELECT qid FROM answers where id = %s ', [sid])
    ques = cursor.fetchall()
    cursor.execute(
        'SELECT Question FROM question where id = %s ', [ques[0]['qid']])
    ques1 = cursor.fetchone()
    return render_template('update_ans.html', update_data=update_data, ques1=ques1, qid=qid)


@app.route("/<int:id>/delete_ans", methods=['GET', 'POST'])
def delete_as(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT qid FROM answers where id=%s', [id])
    qid_dic = cursor.fetchone()
    qid = qid_dic['qid']
    cursor.execute(
        'DELETE FROM answers WHERE id = %s', [id])
    mysql.connection.commit()
    cursor.execute(
        'SELECT * FROM answers where qid = %s order by a_date desc ', [qid])
    answer = cursor.fetchall()
    cursor.execute(
        'SELECT Question FROM question where id = %s ', str(qid))
    ques = cursor.fetchone()

    return redirect('/'+str(qid)+'/answer')
    # return render_template('answer.html', data=answer, qid=qid, ques=ques)


app.run(use_reloader=True)

