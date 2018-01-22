from flask import Flask, jsonify, request
from pyfcm import FCMNotification
import db


github_secret = "***REMOVED***"
api_key = "***REMOVED***" \
          "***REMOVED***"

# ids = ["cA_XAmKxW0c:APA91bH9fl_N8R62iiqlu2Atn_7cd9dfffMLQfX7YljD0UIwVZoMzHjPAM0PcSVc4qBn2atWcKGrLZ9haTozi9Kx3dZVonr2YKhbvVD7qxnZrJsgIzmB3WoG2h7ENV_hwbvhSYbjx_Yn"]

app = Flask(__name__)
push_service = FCMNotification(api_key=api_key)


@app.route('/')
def index():
    return 'Hello. This site has no content. Sorry.'


@app.route('/data')
def names():
    data = {"names": ["Jannik"],
            "numbers": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "alphabet": [chr(x) for x in range(65, 65 + 26)]}
    return jsonify(data)


@app.route("/v1/github/hook", methods=['POST'])
def githup_hook():
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
        if "action" in json:
            action = json["action"]
        else:
            action = "unknown"

        result = send_message("{} has performed {} on repo {}".format(user, action, repo), "Git update [{}]".format(action))
        print(result)
        return str(result)
    else:
        print("failed")


@app.route('/v1/fcm/ping/all')
@app.route('/v1/fcm/ping/device/<string:reg_id>')
def ping_all(reg_id=None):
    if reg_id is None:
        print(send_message("Ping", "Ping to all devices"))
    else:
        print(push_service.notify_single_device(reg_id, "Ping", "Ping to single device."))
    return jsonify({"status": "success"})


@app.route('/v1/fcm/register')
def register():
    if request.args is None:
        return jsonify({"status": "failure"})

    new = request.args.get("new_id", default=None)
    old = request.args.get("old_id", default=None)
    if new is None:
        return jsonify({"status": "failure"})
    if old is None:
        db.insert_fcm_id(new)
    else:
        db.update_fcm_id(old, new)
    push_service.notify_single_device(new, "Registered successfully.", "Fcm registration")
    return jsonify({"status": "success"})


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
    db.open()
    app.run()
    db.close()
