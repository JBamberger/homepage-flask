from flask import Flask, jsonify, request, render_template
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError

import db
from github import handle_github_hook
from static_data import name_data, static_stream

github_secret = "***REMOVED***"
api_key = "***REMOVED***" \
          "***REMOVED***"

app = Flask(__name__)
db.open()
push_service = FCMNotification(api_key=api_key)


@app.route('/')
def index():
    return render_template("landing_page.html")


@app.route('/data')
def names():
    return jsonify(name_data())


@app.route('/data/stream')
def stream_content():
    return jsonify(static_stream())


@app.route("/v1/github/hook", methods=['POST'])
def github_hook():
    user, event, repo = handle_github_hook(request.headers, request.get_json())

    result = send_message(
        message="{} has performed {} on repo {}".format(user, event, repo),
        title="Git update [{}]".format(event)
    )
    print(result)
    return "success"


@app.route('/v1/fcm/ping/all')
@app.route('/v1/fcm/ping/device/<string:reg_id>')
def ping_all(reg_id=None):
    if reg_id is None:
        print(send_message("Ping", "Ping to all devices"))
    else:
        print(push_service.notify_single_device(reg_id, "Ping", "Ping to single device."))
    return jsonify({"status": "success"})


@app.route('/error')
def error():
    raise ValueError()


@app.route('/v1/fcm/register')
def register():
    if request.args is None:
        return jsonify({"status": "failure", "error": "Missing arguments."})

    new = request.args.get("new_id", default=None)
    old = request.args.get("old_id", default=None)
    if new is None:
        return jsonify({"status": "failure", "error": "New id is empty."})
    if old is None:
        db.insert_fcm_id(new)
    else:
        db.update_fcm_id(old, new)

    result = push_service.notify_single_device(new, "Registered successfully.", "Fcm registration")

    if result["success"] == 1:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure", "error": "Error from upstream server."})


@app.errorhandler(AuthenticationError)
@app.errorhandler(FCMServerError)
@app.errorhandler(InvalidDataError)
@app.errorhandler(InternalPackageError)
def handle_error(error):
    response = jsonify({'status': 'failure', 'error': str(type(error))})
    response.status_code = 500
    return response


@app.route("/v1/fcm/ids")
def get_ids():
    return jsonify(db.get_all_ids())


def send_message(message, title):
    ids = []
    id_tuples = db.get_all_ids()
    for x in id_tuples:
        ids.append(x[0])
    return push_service.notify_multiple_devices(registration_ids=ids, message_body=message, message_title=title)


if __name__ == '__main__':
    app.run(debug=True)
