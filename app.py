from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello. This site has no content. Sorry.'


@app.route('/data')
def names():
    data = {"names": ["Jannik"],
            "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "alphabet": [chr(x) for x in range(65, 65 + 26)]}
    return jsonify(data)


if __name__ == '__main__':
    app.run()
