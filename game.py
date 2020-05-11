import os
from datetime import datetime
from random import randint

from flask import make_response, request, render_template, redirect, Response

from typing import Union, List, Tuple

import glob
import authorisation
from authorisation import update_status, profile_path
from my_utility import read_info, write_info, redirect_to_root, get_time

need_in_room = 2
time_to_think = 10


def room_path(number: Union[str, int]) -> str:
    number = str(number)
    return 'rooms/' + number


def add_in_queue(email: str) -> Union['in_queue', Response]:
    queue_info = read_info('queue_file')
    player_status = read_info(profile_path(email)).get('status')
    if ('queue' in queue_info):
        players_in_queue = queue_info['queue'].split()
        if (email not in players_in_queue):
            if (player_status == 'in_menu'):
                players_in_queue.append(email)
                print(email, ' get in queue')
                queue_info['queue'] = ' '.join(players_in_queue)
                write_info('queue_file', queue_info)
                update_status(email, 'in_queue')
                return 'in_queue'
            else:
                return redirect_to_root()
        else:
            if (player_status != 'in_queue'):
                raise Exception('Something go wrong, player in queue but '
                                'with wrong status')
                pass
            return 'in_queue'
    players_in_queue = [email]
    print(email, ' get in queue')
    queue_info['queue'] = ' '.join(players_in_queue)
    write_info('queue_file', queue_info)
    update_status(email, 'in_queue')
    return 'in_queue'


def create_room(members: List[str]):
    room_number = str(randint(1, 1000000))
    room_info = dict()
    open(room_path(room_number), 'w', encoding='utf-8')
    for member in members:
        player_info = read_info(profile_path(member))
        player_info['room'] = room_number
        player_info['status'] = 'playing'
        write_info(profile_path(player_info.get('email')), player_info)
        room_info[player_info.get('email') + '_bullet_count'] = 0
        room_info[player_info.get('email') + '_action'] = 'defence'
    room_info['members'] = ' '.join(members)
    room_info['number'] = room_number
    room_info['round_started'] = get_time()
    write_info(room_path(room_number), room_info)


def check_queue_len(email: str) -> bool:
    """
    Returns:
         bool: True if email removed from queue and added to room
    """
    queue_info = read_info('queue_file')
    players_in_queue = queue_info.get('queue').split()
    ans = False
    room_capacity = min(max(need_in_room, 2), 50)
    while (len(players_in_queue) >= room_capacity):
        if email in players_in_queue[:room_capacity]:
            ans = True
        create_room(players_in_queue[:room_capacity])
        players_in_queue = players_in_queue[room_capacity:]
    queue_info['queue'] = ' '.join(players_in_queue)
    write_info('queue_file', queue_info)
    return ans


@glob.app.route(glob.game_prefix + 'queue/')
def queue():
    check = authorisation.authorisation_check(request)
    if check is not True:
        if (check is False):
            return redirect_to_root()
        return check
    email = request.cookies.get('email')
    check = add_in_queue(email)
    if (not isinstance(check, str)):
        return check
    if (check_queue_len(email)):
        return redirect(glob.game_prefix + 'play/')
    return render_template('queue.html', root=glob.game_prefix)


@glob.app.route(glob.game_prefix + 'leave_queue/')
def leave_queue():
    check = authorisation.authorisation_check(request)
    if check is not True:
        if (check is False):
            return redirect_to_root()
        return check
    email = request.cookies.get('email')
    if (authorisation.get_status(email) != 'in_queue'):
        redirect_to_root()
    queue_info = read_info('queue_file')
    queue_info['queue'].remove(email)
    write_info('queue_file', queue_info)
    update_status(email, 'in_menu')
    return redirect_to_root()


@glob.app.route(glob.game_prefix + 'leave_room/')
def leave_room():
    check = authorisation.authorisation_check(request)
    if check is not True:
        if (check is False):
            return redirect_to_root()
        return check
    email = request.cookies.get('email')
    if (authorisation.get_status(email) != 'playing'):
        redirect_to_root()
    player_info = read_info(profile_path(email))
    room_info = read_info(room_path(player_info.get('room')))
    room_members = room_info['members'].split()
    room_members.remove(email)
    if (len(room_members)):
        room_info['members'] = ' '.join(room_members)
        write_info(room_path(player_info.get('room')), room_info)
    else:
        os.remove(room_path(player_info.get('room')))
    player_info['status'] = 'in_menu'
    player_info.pop('room')
    write_info(profile_path(email), player_info)
    return redirect_to_root()


def get_room_members_without_me_info(number: Union[str, int], my_email: str) \
        -> List[Tuple[str, str, str, bool]]:
    number = str(number)
    room_info = read_info(room_path(number))
    members = room_info.get('members').split()
    members.remove(my_email)
    members_without_me = []
    for member in members:
        member_info = read_info(profile_path(member))
        login = member_info.get('login')
        bullet_have = room_info.get(member_info.get('email') + '_bullet_count')
        is_dead = (member + '_is_dead') in room_info
        members_without_me.append((login,
                                   bullet_have,
                                   member,
                                   is_dead))
    return members_without_me


def change_choose(req: Response, email: str) -> Response:
    player_info = read_info(profile_path(email))
    room_number = player_info.get('room')
    room_info = read_info(room_path(room_number))
    action_type = req.form.get('type')
    if (action_type is not None):
        print(action_type)
        if (action_type == 'defence'):
            room_info[email + '_action'] = 'defence'
            room_info.pop(email + '_target', None)
            write_info(room_path(room_number), room_info)
            return make_response("OK", 200)
        if (action_type == 'reload'):
            if (int(room_info.get(email + '_bullet_count')) >= 6):
                return make_response("failed", 404)
            room_info[email + '_action'] = 'reload'
            room_info.pop(email + '_target', None)
            write_info(room_path(room_number), room_info)
            return make_response("OK", 200)
        target = req.form.get('target')
        print(target)
        if (target is None):
            return make_response("failed", 404)
        if (target not in room_info.get('members').split()):
            return make_response("failed", 404)

        if (action_type == 'attack'):
            if (int(room_info.get(email + '_bullet_count')) < 1):
                return make_response("failed", 404)
            room_info[email + '_action'] = 'attack'
            room_info[email + '_target'] = target
        if (action_type == 'super_attack'):
            if (int(room_info.get(email + '_bullet_count')) < 3):
                return make_response("failed", 404)
            room_info[email + '_action'] = 'super_attack'
            room_info[email + '_target'] = target
        write_info(room_path(room_number), room_info)
        return make_response("OK", 200)
    else:
        return make_response("failed", 404)


def produce_round_results(number: str) -> dict:
    room_info = read_info(room_path(number))
    members = room_info.get('members').split()
    for member in members:
        bullets_have = int(room_info.get(member + '_bullet_count'))
        action = room_info.get(member + '_action')
        #print(action)
        print(bullets_have)
        if (action == 'reload'):
            if (bullets_have < 6):
                bullets_have += 1

        target = room_info.get(member + '_target')
        if (action == 'attack'):
            bullets_have -= 1
            if (room_info.get(target + '_action') != 'defence'):
                room_info[target + '_is_dead'] = True

        if (action == 'super_attack'):
            bullets_have -= 3
            room_info[target + '_is_dead'] = True

        room_info[member + '_bullet_count'] = bullets_have
    for member in members:
        room_info[member + '_action'] = 'defence'
        room_info.pop(member + '_target', None)
    write_info(room_path(number), room_info)
    return room_info


def check_room_time(number: str) -> str:
    number = str(number)
    room_info = read_info(room_path(number))
    round_start = float(room_info.get('round_started'))
    now_time = get_time()
    time_left = round_start - now_time + time_to_think
    if (time_left < 0):
        while (time_left < 0):
            round_start += time_to_think
            room_info = produce_round_results(number)
            time_left = round_start - now_time + time_to_think
        room_info['round_started'] = round_start
        write_info(room_path(number), room_info)
    return str(time_left)


@glob.app.route(glob.game_prefix + 'play/', methods=['POST', 'GET'])
def play():
    check = authorisation.authorisation_check(request)
    if check is not True:
        if (check is False):
            return redirect_to_root()
        return check
    email = request.cookies.get('email')
    player_info = read_info(profile_path(email))
    room_number = player_info.get('room')
    room_info = read_info(room_path(room_number))
    if (player_info.get('status') != 'playing'):
        return redirect_to_root()
    if request.method == 'POST':
        return change_choose(request, email)
    time_left = check_room_time(room_number)
    print(time_left)
    room_members_without_me = get_room_members_without_me_info(room_number,
                                                               email)
    me = (player_info.get('login'),
          room_info.get(email + '_bullet_count'),
          email,
          (email + '_is_dead') in room_info)
    action = room_info.get(email + '_action')
    target = room_info.get(email + '_target')
    time_left = round(float(time_left), 1) + 0.1
    time_left = str(time_left).split('.')[0] + '.' + str(time_left).split('.')[
        1][0]
    return render_template('play.html',
                           root=glob.game_prefix,
                           room_members_without_me=room_members_without_me,
                           me=me,
                           action=action,
                           target=target,
                           time_left=time_left)
