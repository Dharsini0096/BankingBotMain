from flask import Flask, request, jsonify

from bot2 import chatwithbot, getbankname

app = Flask(__name__)

@app.route('/chat', methods=['GET', 'POST'])
def chatBot():
    chatInput = request.form['chatInput']
    bankname = request.form["bankname"]
    getbankname(bankname)
    return jsonify(chatBotReply=chatwithbot(chatInput))


if __name__ == '__main__':
    #app.run(host="192.168.43.90", debug=True)
    app.run(host='0.0.0.0', debug=True)
