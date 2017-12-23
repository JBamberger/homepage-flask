from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return 'Dynamic content? content?! Fancy...'


@app.route('/data')
def names():
    data = {"names":["NootNoot"]}
    return jsonify(data)



if __name__ == '__main__':
    app.run()


