from datetime import datetime

from werkzeug.utils import redirect

import glob


def write_info(filename: str, params: dict) -> None:
    with open(filename, 'w', encoding='utf-8') as file:
        for key, val in params.items():
            file.write(str(key))
            file.write(' ')
            file.write(str(val))
            file.write('\n')


def read_info(filename: str) -> dict:
    ans = dict()
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            ans[line.strip('\n').split(' ', 1)[0]] = line.strip(
                '\n').split(' ', 1)[1]
    return ans


def redirect_to_root():
    return redirect(glob.game_prefix)


def get_time() -> float:
    return (datetime.now() - datetime(1970, 1, 1)).total_seconds()