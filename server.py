from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin
import psycopg2
import json
import os
import base64
from io import BytesIO
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'AAAAABOBA'
manager = LoginManager(app)
connection = psycopg2.connect(
    dbname='Tests', user="postgres", password="123", host="127.0.0.1", port="5432")


class CustomUser(UserMixin):
    def __init__(self, id):
        self.id = id


@app.route("/", methods=['GET'])
def main_page():
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM tests order by id desc')
    all_tests = cursor.fetchall()
    cursor.execute('SELECT * FROM Categoty')
    all_cat = cursor.fetchall()
    cursor.close()
    isA = False
    if current_user.is_authenticated:
        isA = True
    else:
        isA = False
    return render_template("Home.html", tests=all_tests, categories=all_cat, isA=isA)


@app.route("/", methods=['POST'])
def main_page_with_searche():
    cursor = connection.cursor()
    all_tests = []
    if request.form['randomInput'] == "randomFalse":
        useCat = (" AND fkCategory=" + request.form['catId']) if request.form['catId'] != "1" else "" 
        cursor.execute("SELECT * FROM tests WHERE testName like '%" + request.form['testName'] + "%'" + useCat)
        all_tests = cursor.fetchall()
    else:
        cursor.execute("SELECT id FROM tests order by id asc limit 1")
        cc = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM tests order by id desc limit 1")
        cc1 = cursor.fetchone()[0]
        if not cc is None:
            cc = random.randint(cc,cc1)
            cursor.execute("SELECT * FROM tests WHERE id=%s", (cc, ))
        else:
            cursor.execute("SELECT * FROM tests")
        all_tests = cursor.fetchall()
    cursor.execute('SELECT * FROM Categoty')
    all_cat = cursor.fetchall()
    cursor.close()
    isA = False
    if current_user.is_authenticated:
        isA = True
    else:
        isA = False
    return render_template("Home.html", tests=all_tests, categories=all_cat, isA=isA)


@app.route("/lk", methods=['GET'])
@login_required
def lk():
    cursor = connection.cursor()
    print(current_user.id)
    cursor.execute('SELECT * FROM tests WHERE fkUser=%s', (current_user.id, ))
    all_tests = cursor.fetchall()
    cursor.execute('SELECT userName FROM Users WHERE id=%s', (current_user.id, ))
    userName = cursor.fetchone()[0]
    cursor.close()
    isA = False
    if current_user.is_authenticated:
        isA = True
    else:
        isA = False
    return render_template("HomeProfile.html", tests=all_tests, userName=userName, isA=isA)

@app.route("/lk/<tid>", methods=['GET'])
@login_required
def del_test(tid):
    cursor = connection.cursor()
    cursor.execute('DELETE from tests WHERE fkUser=%s and id=%s', (current_user.id, int(tid)))
    connection.commit()
    cursor.execute('SELECT * FROM tests WHERE fkUser=%s', (current_user.id, ))
    all_tests = cursor.fetchall()
    cursor.execute('SELECT userName FROM Users WHERE id=%s', (current_user.id, ))
    userName = cursor.fetchone()[0]
    cursor.close()
    isA = False
    if current_user.is_authenticated:
        isA = True
    else:
        isA = False
    return render_template("HomeProfile.html", tests=all_tests, userName=userName, isA=isA)

@app.route("/like/<tid>", methods=['GET'])
@login_required
def like(tid):
    cursor = connection.cursor()
    cursor.execute('SELECT likeCount FROM tests WHERE id=%s', (tid,))
    colvo = cursor.fetchone()[0] + 1
    cursor.execute('UPDATE tests SET likeCount=%s WHERE id=%s', (colvo, tid))
    connection.commit()
    cursor.close()
    return str(colvo)

@app.route("/dislike/<tid>", methods=['GET'])
@login_required
def dislike(tid):
    cursor = connection.cursor()
    cursor.execute('SELECT dislikeCount FROM tests WHERE id=%s', (tid,))
    colvo = cursor.fetchone()[0] + 1
    cursor.execute('UPDATE tests SET dislikeCount=%s WHERE id=%s', (colvo, tid))
    connection.commit()
    cursor.close()
    return str(colvo)

@manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@manager.user_loader
def load_user(id):
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM Users WHERE id=%s', (id,))
    res = cursor.fetchone()
    if res != None:
        res = res[0]
        user = CustomUser(res)
        return user
    return None


@app.route("/login", methods=['GET'])
def login():
    return render_template("Authorization.html")

@app.route("/edit", methods = ['GET'])
def edit():
    return render_template("ProfileEdit.html")

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def signout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/login", methods=['POST'])
def loginPost():
    login = request.form['login']
    password = request.form['password']
    cursor = connection.cursor()
    cursor.execute(
        'SELECT id FROM Users WHERE userName=%s AND userPassword=%s', (login, password))
    res = cursor.fetchone()[0]
    if res != None:
        user = CustomUser(res)
        login_user(user)
    else:
        return redirect(url_for('login'))
    cursor.close()
    return redirect(url_for('main_page'))


@app.route("/registration", methods=['GET'])
def registration():
    return render_template("Registration.html")


@app.route("/registration", methods=['POST'])
def registration_post():
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (userName, userPassword) VALUES (%s, %s) ON CONFLICT (userName) DO NOTHING",
                   (request.form['login'], request.form['password']))
    connection.commit()
    cursor.close()
    return redirect(url_for('login'))


@app.route("/openAddTest", methods=['GET'])
@login_required
def open_add_test():
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Categoty')
    all_cat = cursor.fetchall()
    cursor.close()
    return render_template("CreateTest.html", categories=all_cat)


@app.route("/addTest", methods=['POST'])
@login_required
def add_test():
    print('gg')
    am = request.files['testPic']
    am.save('static/img/' + am.filename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tests (testName, discribtion, pictureLink, likeCount, dislikeCount, fkUser, fkCategory) VALUES (%s, %s, %s, 0, 0, %s, %s) RETURNING id",
                   (request.form['testName'], request.form['testDesc'], '/img/' + am.filename, current_user.id, request.form['catId']))
    testId = cursor.fetchone()[0]
    testsRes = json.loads(request.form['testResults'])
    i = 0
    for tt in testsRes:
        am_am = request.files['testPicRes' + str(i)]
        am_am.save('static/img/' + am_am.filename)
        cursor.execute("INSERT INTO testResultPack (resId, resultName, imgResult, fkTest) VALUES (%s, %s, %s, %s)",
                    (tt['id'] + 1, tt['resName'], '/img/' + am_am.filename, testId))
        i+=1
    questions = json.loads(request.form['questions'])
    for qq in questions:
        cursor.execute("INSERT INTO questions (questionName, fkTest) VALUES (%s,%s) RETURNING id",
                       (qq['questionName'], testId))
        qid = cursor.fetchone()[0]
        for qqq in qq['answers']:
            cursor.execute("INSERT INTO answers (anserName, fkQuestion, rusult) VALUES (%s,%s, %s)",
                           (qqq['answer'], qid, qqq['resNum']))
    connection.commit()
    cursor.close()
    return 'success'


@app.route("/test/<id>", methods=['GET'])
def get_test(id):
    cursor = connection.cursor()
    cursor.execute('SELECT testName FROM tests WHERE id=%s', (id, ))
    test = cursor.fetchone()
    cursor.execute(
        'SELECT resId, resultName, imgResult FROM testResultPack WHERE fkTest=%s', (id, ))
    resultPack = cursor.fetchall()
    cursor.execute(
        'SELECT id, questionName FROM questions WHERE fkTest=%s', (id, ))
    questionsList = cursor.fetchall()
    qanL = []
    for ql in questionsList:
        cursor.execute(
            'SELECT rusult, anserName FROM answers WHERE fkQuestion=%s', (ql[0], ))
        answers = cursor.fetchall()
        qanL.append({'question': ql, 'answers': answers})
    cursor.close()
    jj = {'testName': test[0], 'results': resultPack, 'question': qanL}
    isA = False
    if current_user.is_authenticated:
        isA = True
    else:
        isA = False
    return render_template("ShowTest.html", tests=jj,isA=isA)


@app.route("/like/<id>", methods=['POST'])
@login_required
def like_test(id):
    return jsonify({'success': 'ok'})


@app.route("/dislike/<id>", methods=['POST'])
@login_required
def dislike_test(id):
    return jsonify({'success': 'ok'})


if __name__ == "__main__":
    app.run()
