from __future__ import annotations

import argparse
import configparser
import os
import stat
import subprocess
import sys
from pathlib import Path


GIT_DIR = Path('.git')
GIT_COMMIT_MSG_FILE = GIT_DIR / 'current_message.txt'
GIT_POST_COMMIT_FILE = GIT_DIR / 'hooks/post-commit'
GIT_CONFIG_FILE = GIT_DIR / 'config'

COMMIT_TYPES = [
    'feat',
    'fix',
    'docs',
    'style',
    'refactor',
    'perf',
    'test',
    'build',
    'ci',
    'chore',
    'revert',
]


def _write_post_commit_file() -> None:
    with open(GIT_POST_COMMIT_FILE, 'w') as f:
        f.write('#!/bin/env bash\ngitc --reset')

    os.chmod(GIT_POST_COMMIT_FILE, os.stat(GIT_POST_COMMIT_FILE).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _set_aliases() -> None:
    git_config = configparser.ConfigParser()
    git_config.read(GIT_CONFIG_FILE)

    if not git_config.has_section('alias'):
        git_config.add_section('alias')
    git_config.set('alias', 'addm', '!gitc-add')
    git_config.set('alias', 'show-messages', '!gitc-show-messages')

    if not git_config.has_section('commit'):
        git_config.add_section('commit')

    git_config.set('commit', 'template', str(GIT_COMMIT_MSG_FILE))

    with open(GIT_CONFIG_FILE, 'w') as f:
        git_config.write(f)


def _init() -> None:
    GIT_COMMIT_MSG_FILE.touch()
    _write_post_commit_file()
    _set_aliases()


def _add_msg_to_file(message: str, type: str) -> str:
    msg = f'[{type}] {message}'
    with open(GIT_COMMIT_MSG_FILE, 'a') as f:
        f.write(f'{msg}\n')

    return msg


def _print_commit_msg() -> None:
    with open(GIT_COMMIT_MSG_FILE, 'r') as f:
        print(f.read().strip() or 'No commit messages yet!.. To add new message run\ngit addm -m <message> [--type]')


def _reset_commit_msg_file() -> None:
    GIT_COMMIT_MSG_FILE.write_text('')


def _run_git_add(args: list[str]) -> int:
    git_add = subprocess.run(['git', 'add', *args])
    return git_add.returncode


def git_add() -> int:
    add_parser = argparse.ArgumentParser()
    add_parser.add_argument('-m', '--message', required=True, help='Message to add')
    add_parser.add_argument('--type', choices=COMMIT_TYPES, default='feat', help='The type of the change')

    args, rest = add_parser.parse_known_args()
    if args.message and (_run_git_add(rest) == 0):
        print(_add_msg_to_file(args.message, args.type))

    return 0


def show_messages() -> int:
    _print_commit_msg()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()

    grp = parser.add_mutually_exclusive_group()
    grp.add_argument('--init', action='store_true', help='Initialize everything')
    grp.add_argument('--reset', action='store_true', help='Reset commit messages')

    args = parser.parse_args()

    if not GIT_DIR.exists() or not GIT_DIR.is_dir():
        print('error: not a git repository', file=sys.stderr)
        return 1

    if args.init:
        _init()
        return 0

    if args.reset:
        _reset_commit_msg_file()
        return 0

    return 0
