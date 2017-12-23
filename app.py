from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'dynamic content?! Fancy...'


@app.route('/data')
def names():
    data = {"names":["Karl","Heinz","Jörg"]}
    return jsonify(data)



if __name__ == '__main__':
    app.run()


