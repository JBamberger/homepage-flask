from flask import Flask, jsonify, request, render_template, redirect, abort
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


class Page:
    def __init__(self, slug, template, title, params):
        self.slug = slug
        self.template = template
        self.title = title
        self.params = params


page_main = Page('main', 'landing_page.html', 'Main', {})
# page_about = Page('about', 'about_jannik.html', 'About Jannik', {})
page_privacyPolicy = Page('gdpr', 'privacy-policy.html', 'Privacy policy', {'address': 'Gustav-Troll-Straße 35, 78315 Radolfzell'})
error404 = Page('error404', '404.html', 'Error 404', {})
error500 = Page('error500', '500.html', 'Error 500', {})

head_menu = [page_main,
             # page_about,
             page_privacyPolicy]
foot_menu = []
all_pages = {
    'x': Page('x', 'layout.html', 'Hello World', {}),
    page_main.slug: page_main,
    # page_about.slug: page_about,
    page_privacyPolicy.slug: page_privacyPolicy,
    error404.slug: error404,
    error500.slug: error500
}

common_params = {
    'head_menu': head_menu,
    'foot_menu': foot_menu,
    'owner_mail': 'mail@jbamberger.de',
    'owner_full_name': 'Jannik Bamberger',
    'root_url': 'https://jbamberger.de'
}


@app.route('/')
def show_landing_page():
    return redirect("/page/" + page_main.slug, code=302)


def render_page(page):
    return render_template(page.template, current_page=page, **common_params, **page.params)


@app.route('/page/<string:slug>')
def show_page(slug):
    page = all_pages.get(slug, None)
    if page is None:
        return abort(404)
    else:
        return render_page(page)


@app.route('/data')
def names():
    return jsonify(name_data())


@app.route('/data/stream')
def stream_content():
    return jsonify(static_stream())


@app.route('/error')
@app.route('/error/<error_type>')
def error(error_type=None):
    if error_type is None:
        return abort(404)
    elif error_type == 'abort':
        return abort(500)
    else:
        raise ValueError()


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


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', request.path)
    return render_page(error404), 404


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', error)
    return render_page(error500), 500


@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return render_page(error500), 500


if __name__ == '__main__':
    app.run(debug=True)
