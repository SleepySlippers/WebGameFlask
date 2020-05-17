import glob
from flask import Flask, make_response, request, render_template, url_for, \
    redirect, Response

glob.app = Flask(__name__)

import authorisation
import game


def status_redirection(email):
    status = authorisation.get_status(email)
    if (status == 'in_menu'):
        return None
    if (status == 'playing'):
        return redirect(glob.game_prefix + 'play/')
    if (status == 'in_queue'):
        return redirect(glob.game_prefix + 'queue/')
    return None


@glob.app.route('/')
def redirection_to_game():
    return redirect(glob.game_prefix + 'index/')


@glob.app.route(glob.game_prefix)
def redirection_to_index():
    return redirect(glob.game_prefix + 'index/')


@glob.app.route(glob.game_prefix + 'index/')
def index():
    check = authorisation.authorisation_check(request)
    if check not in (True, False):
        return check
    if (check is True):
        check = status_redirection(request.cookies.get('email'))
        if (check is not None):
            return check
    return make_response(render_template('index.html', root=glob.game_prefix))


if __name__ == '__main__':
    glob.app.run(debug=True)
