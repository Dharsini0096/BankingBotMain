from flask import Flask, request, jsonify,render_template
import json
from github import Github
import sqlite3
from bot2 import chatwithbot, getbankname

app = Flask(__name__)

bank = ''
@app.route('/chat', methods=['GET', 'POST'])
def chatBot():
    chatInput = request.form['chatInput']
    bankname = request.form["bankname"]
    getbankname(bankname)
    return jsonify(chatBotReply=chatwithbot(chatInput))



def dbconnection(email,pwd):

    conn = sqlite3.connect('bank.db')
    if conn:
        print("Database connected successfully")
    else:
        print("Cannot connect to DB")
        return "error"

    cur = conn.cursor()

    cur.execute('SELECT bankname FROM banklist WHERE email = ? and password= ?', (email, pwd))
    result = cur.fetchall()

    conn.close()
    if len(result) <=0 :
        return "error"
    else:
        return result[0]


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/admin',  methods=['POST', 'GET'])
def admin():
    user = request.form['username']
    pwd = request.form['password']
    res = dbconnection(user,pwd)
    if res == 'error':
        return render_template('login.html', msg='Invalid Login')
    #if (request.form['username'] == 'admin' and request.form['password'] == 'admin'):
    else:
        global bank
        bank = res
        return render_template('index.html', result=bank)


@app.route('/admin/processInfo', methods=['POST'])
def processInfo():
    output = request.json
    print(bank)
    jsonObject = []

    for w in output['intents']:
        jsonObject.append(w)

    jsonObject1 = {
        "intents": jsonObject
    }

    output = json.dumps(jsonObject1, indent=2)
    #with open("canara bank.json", "w") as f:
    #   print("File opened")
    #  f.write(output)

    username = "Dharsini0096"
    passsword ="Dharshpapu@0096"

    g = Github('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')

    user = g.get_user()
 #   for repo in user.get_repos():
  #      print(repo)


    repo = g.search_repositories("Dharsini0096/BankingBotMain")[0]

    contents = repo.get_contents(bank + ".json")
    repo.delete_file(contents.path, "Removed" + bank + ".json", contents.sha)
    print("Json File Deleted in repo")

    repo.create_file(bank + ".json","Committing",output)
    print("File created in repo")

    contents = repo.get_contents(bank + "chatbotmodel.h5")
    repo.delete_file(contents.path, "Removed" + bank + "chatbotmodel.h5", contents.sha)
    print("H5 File Deleted in repo")

    contents = repo.get_contents(bank + "chatbotmodel.json")
    repo.delete_file(contents.path, "Removed" + bank + "chatbotmodel.json", contents.sha)
    print("Model json File Deleted in repo")

    contents = repo.get_contents(bank + "data.pickle")
    repo.delete_file(contents.path, "Removed" + bank + "data.pickle", contents.sha)
    print("Pickle File Deleted in repo")

    getbankname(bank)

    return render_template('index.html')

if __name__ == '__main__':
    #app.run(host="192.168.43.90", debug=True)
    app.run(host='0.0.0.0', debug=True)
