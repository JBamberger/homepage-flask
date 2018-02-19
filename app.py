from flask import Flask, jsonify, request, render_template
from pyfcm import FCMNotification
from pyfcm.errors import AuthenticationError, FCMServerError, InvalidDataError, InternalPackageError

import db

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
    data = {"names": ["Jannik"],
            "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "alphabet": [chr(x) for x in range(65, 65 + 26)]}
    return jsonify(data)


@app.route('/data/stream')
def stream_content():
    def item(
            content="Hello World",
            content_url="https://jbamberger.de/",
            order_date=1337,
            image_url="https://jbamberger.de/static/pig.jpg"):
        return {'content': content, 'content_url': content_url, 'order_date': order_date, 'image_url': image_url}

    data = [
        item("Good morning"),
        item(),
        item(),
        item(),
        item(),
        item(),
        item(),
        item(),
        item()
    ]

    return jsonify(data)


@app.route("/v1/github/hook", methods=['POST'])
def githup_hook():
    headers = request.headers

    event = "unknown"
    if headers is not None:
        if headers["X-GitHub-Event"] is not None:
            event = headers["X-GitHub-Event"]

    json = request.get_json()
    if json is not None:
        print(json)

        if "sender" in json:
            user = json["sender"]
            if "login" in user:
                user = user["login"]
            else:
                user = "unknown"
        else:
            user = "unknown"
        if "repository" in json:
            repo = json["repository"]
            if "full_name" in repo:
                repo = repo["full_name"]
            else:
                repo = "unknown"
        else:
            repo = "unknown"

        result = send_message("{} has performed {} on repo {}".format(user, event, repo),
                              "Git update [{}]".format(event))
        print(result)
        return "success"
    else:
        print("Hook failed, headers:")
        print(str(headers))
        raise ValueError()


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

    try:
        result = push_service.notify_single_device(new, "Registered successfully.", "Fcm registration")

        if result["success"] == 1:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "failure", "error": "Error from upstream server."})
    except AuthenticationError:
        return jsonify({"status": "failure", "error": "AuthenticationError"})
    except FCMServerError:
        return jsonify({"status": "failure", "error": "FCMServerError"})
    except InvalidDataError:
        return jsonify({"status": "failure", "error": "InvalidDataError"})
    except InternalPackageError:
        return jsonify({"status": "failure", "error": "InternalPackageError"})


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
