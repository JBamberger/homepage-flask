from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return 'Want a flask?'


@app.route('/data')
def names():
    data = {"names":["Noot", "Noot!"]}
    return jsonify(data)


if __name__ == '__main__':
    app.run()
