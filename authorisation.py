import datetime
import os.path
import random

from flask import make_response, request, render_template, Response

from typing import Union

import send_mail
import glob
from my_utility import write_info, read_info, redirect_to_root, get_time


def contains(container: dict, elements: tuple) -> bool:
    for x in elements:
        if x in container:
            return True
    return False


def profile_path(profile_email: str) -> str:
    return 'profiles/' + profile_email + '.profile'


def temp_profile_path(profile_email: str) -> str:
    return 'temp_profiles/' + profile_email + '.temp_profile'


@glob.app.route(glob.game_prefix + 'leave/')
def leave():
    return clear_all()


@glob.app.route(glob.game_prefix + 'sign_in/', methods=['POST', 'GET'])
def sign_in():
    if contains(request.cookies, ('email', 'password', 'login')):
        return clear_all()
    if request.method == 'POST':
        if 'email' not in request.form or 'password' not in request.form:
            return redirect_to_root()
        if os.path.isfile(profile_path(request.form.get('email'))):
            data = read_info(profile_path(request.form.get('email')))
            if data.get('password') != request.form.get('password'):
                return render_template('sign_in.html', root=glob.game_prefix,
                                       error='Wrong password')
            else:
                res = make_response('')
                res.set_cookie('email', data.get('email'))
                res.set_cookie('password', data.get('password'))
                res.set_cookie('login', data.get('login'))
                res.headers['location'] = glob.game_prefix
                update_status(data.get('email'), 'in_menu')
                return res, 302
        else:
            return render_template('sign_in.html', root=glob.game_prefix,
                                   error='Wrong email')
    return render_template('sign_in.html', root=glob.game_prefix, error='')


@glob.app.route(glob.game_prefix + 'registration/', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        ans = registration_data_check(request.form)
        if ans == "OK":
            secret_invite_code = random.randint(0, 10000 - 1)
            res = make_response("")
            ans = send_mail.send_mail(
                request.form.get('email'),
                'Welcome to the club buddy!!\n\n'
                ' Your secret invite code is: ' +
                str(secret_invite_code) +
                '\n Your password is: ' +
                request.form.get('password') + '\n')

            if ans is not None:
                return render_template('registration.html',
                                       root=glob.game_prefix, error=ans)

            res.set_cookie("login", request.form.get('login'))
            res.set_cookie("email", request.form.get('email'))
            res.set_cookie("password", request.form.get('password'))

            new_profile_info = dict(request.form)
            new_profile_info['secret_invite_code'] = secret_invite_code
            new_profile_info['create_time'] = get_time()#datetime.datetime.now()
            write_info(temp_profile_path(
                request.form.get('email')), new_profile_info)

            res.headers['location'] = glob.game_prefix + 'verification/'
            return res, 302
        else:
            return render_template('registration.html', root=glob.game_prefix,
                                   error=ans)
    return render_template('registration.html', root=glob.game_prefix,
                           error="")


def move_to_normal_profile(email: str):
    profile = read_info(temp_profile_path(email))
    profile.pop('secret_invite_code', None)
    profile['create_time'] = get_time()
    write_info(profile_path(email), profile)
    update_status(email, 'in_menu')
    os.remove(temp_profile_path(email))


def check_invite_code(req: Response) -> Response:
    if 'secret_invite_code' in req.form:
        try:
            int(req.form.get('secret_invite_code'))
        except ValueError:
            return render_template('verification.html',
                                   root=glob.game_prefix,
                                   error='Wrong secret code, you get on '
                                         'my nerves!')
        if 'email' not in req.cookies:
            return redirect_to_root()
        path = temp_profile_path(req.cookies.get('email'))
        if os.path.isfile(path):
            data = read_info(path)
            if data.get('secret_invite_code') != \
                    req.form.get('secret_invite_code'):
                return render_template('verification.html',
                                       root=glob.game_prefix,
                                       error='Wrong secret code, you get on '
                                             'my nerves!')
            else:
                if data.get('password') != req.cookies.get('password'):
                    return clear_all()
                else:
                    move_to_normal_profile(req.cookies.get('email'))
                return redirect_to_root()

        else:
            return redirect_to_root()

    if 'give_new_secret_code' in req.form:
        pass
    return render_template('verification.html',
                           root=glob.game_prefix,
                           error='Wrong secret code, you get on my nerves!')


@glob.app.route(glob.game_prefix + 'verification/', methods=['POST', 'GET'])
def verification():
    if request.method == 'POST':
        return check_invite_code(request)
    return render_template('verification.html', root=glob.game_prefix,
                           error='')


def registration_data_check(data: dict) -> str:
    if len(data.get('login')) < 2:
        return 'Too short name'
    if len(data.get('password')) < 6:
        return 'Too short secret word'
    path = 'temp_profiles/' + data.get('email') + '.temp_profile'
    if os.path.isfile(path):
        return "This email has already hold"
    path = 'profiles/' + data.get('email') + '.profile'
    if os.path.isfile(path):
        return "This email has already hold"
    return 'OK'


def clear_all():
    res = make_response("")
    res.set_cookie('email', max_age=0)
    res.set_cookie('password', max_age=0)
    res.set_cookie('login', max_age=0)
    res.headers['location'] = glob.game_prefix
    return res, 302


def authorisation_check(req: Response) -> Union[bool, Response]:
    if 'email' not in req.cookies:
        if contains(req.cookies, ('password', 'login')):
            print('No email')
            return clear_all()
        return False
    path = 'profiles/' + req.cookies.get('email') + '.profile'
    if not os.path.isfile(path):
        print('No file')
        return clear_all()
    data = read_info(path)
    if data.get('password') != req.cookies.get('password'):
        print('No match')
        return clear_all()
    return True


def get_status(email: str) -> str:
    info = read_info(profile_path(email))
    return info.get('status')


def update_status(email: str, new_stats: str) -> None:
    info = read_info(profile_path(email))
    if (info.get('status') != new_stats):
        info['status'] = new_stats
        write_info(profile_path(email), info)
