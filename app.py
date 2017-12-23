from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello my friend.'


@app.route('/data')
def names():
    data = {"names":["NootNoot"]}
    return jsonify(data)



if __name__ == '__main__':
    app.run()


