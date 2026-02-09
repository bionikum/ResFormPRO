from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "ResFormPRO работает!"

@app.route('/login')
def login():
    return "Страница входа"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
