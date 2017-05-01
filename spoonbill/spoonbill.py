"""Spoonbill: Web front-end for static site generator Pelican."""
# -*- coding: utf-8 -*-
import logging
import os
import sys
import argparse
import subprocess
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
from bottle import (Bottle, redirect, request,
                    static_file, auth_basic, template)

app = Bottle()
log = logging.getLogger('spoonbill')

CONTENT_PATH = '../content'
FILE_EXTENSION = '.md'  # .md for MarkDown, .rst for reStructuredText etc.
USERNAME = 'username'
PASSWORD = 'password'
PELICAN_DEPLOY = 'pelican content -s publishconf.py -t'
GIT = False
GIT_AUTHOR = "Spoonbill <spoonbill@nasa.com>"


def get_file_list():
    """Get the list of files in the content directory."""
    try:
        file_list = []
        for root, dirs, files in os.walk(CONTENT_PATH):
            if files:
                for file in files:
                    if file.endswith(FILE_EXTENSION):
                        tag = os.path.relpath(root, CONTENT_PATH).lstrip('.')
                        if tag:
                            tag = tag + '/'
                        file_list.append(tag + file)
        return file_list
    except Exception as error:
        log.error(error)


def open_file(file_name):
    """Open file for editing."""
    try:
        file_name = file_name.strip().lstrip('/')
        file_path = Path(os.path.join(CONTENT_PATH, file_name))
        if file_path.is_file():
            fo = open(os.path.join(CONTENT_PATH, file_name),
                      'r', encoding='utf8')
            file_contents = fo.read()
            fo.close()
            log.info("Opening existing file %s.", file_name)
            return file_contents
        else:
            log.info("File %s does not exist.", file_name)
            return False
    except Exception as error:
        log.error(error)


def save_file(file_name, file_contents):
    """Save the contents to file. If file does not exist, create it."""
    try:
        fo = open(os.path.join(CONTENT_PATH, file_name), 'w',
                  newline='\n', encoding='utf8')
        fo.write(file_contents)
        fo.close()
        log.info("File %s saved.", file_name)
        commit_changes(file_name)
    except Exception as error:
        log.error(error)


def delete_file(file_name):
    """Delete the requested file."""
    try:
        file_name = file_name.strip().lstrip('/')
        file_path = Path(os.path.join(CONTENT_PATH, file_name))
        if file_path.is_file():
            os.remove(os.path.join(CONTENT_PATH, file_name))
            log.info("File %s deleted.", file_name)
        else:
            log.info("File %s does not exist.", file_name)
    except Exception as error:
        log.error(error)


def commit_changes(filename):
    """Commit changes to git repository."""
    if GIT:
        try:
            repository = Repo(CONTENT_PATH)
            repository.git.add(CONTENT_PATH + filename)
            repository.git.commit(m='Updated ' + filename, author=GIT_AUTHOR)
            log.info("%s committed to git repository.", filename)
        except InvalidGitRepositoryError:
            log.info("%s is not a valid Git repository.", CONTENT_PATH)


def credentials(user, pswd):
    """Check for auth credentials."""
    if user == USERNAME and pswd == PASSWORD:
        return True
    return False


@app.route('/')
@auth_basic(credentials)
def index():
    """Index/home route."""
    data = {'file_name': '',
            'file_contents': '',
            'file_list': get_file_list(),
            'site_url': "{0}://{1}".format(request.urlparts.scheme,
                                           request.urlparts.netloc)}

    return template('default', data)


@app.route('/edit/<file_name:path>')
@auth_basic(credentials)
def edit(file_name):
    """Editing route."""
    file_contents = open_file(file_name)
    if not file_contents:
        file_contents = 'Hello World!'
    data = {'file_name': file_name,
            'file_contents': file_contents,
            'file_list': get_file_list(),
            'site_url': "{0}://{1}".format(request.urlparts.scheme,
                                           request.urlparts.netloc)}
    return template('default', data)


@app.route('/delete/<file_name:path>')
@auth_basic(credentials)
def delete(file_name):
    """Editing route."""
    delete_file(file_name)
    redirect('/')


@app.route('/save/', method='POST')
@auth_basic(credentials)
def save():
    """Save the file contents and redirect."""
    file_name = request.forms.decode().get('file_name')
    file_contents = request.forms.decode().get('file_contents')
    if request.forms.get('save'):
        save_file(file_name, file_contents)
        redirect('/edit/' + file_name)
    if request.forms.get('save_and_build'):
        save_file(file_name, file_contents)
        if PELICAN_DEPLOY:
            log.info("Deploying Pelican.")
            # Subprocess is non-blocking and will run in the background.
            subprocess.Popen(PELICAN_DEPLOY,
                             shell=True, stderr=subprocess.STDOUT)
        redirect('/edit/' + file_name)


@app.route('/static/<filename>', name='static')
def server_static(filename):
    """Everything in static directory is accessible."""
    return static_file(filename, root='./static')


def cli_args():
    """Parse CLI options and arguments.

    Returns: object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-path',
                        help="path of the content")
    parser.add_argument('-p', '--port',
                        default=8080,
                        help="port (default: 8080)")
    parser.add_argument('--host',
                        default='localhost',
                        help='hostname (default: localhost)')
    parser.add_argument('-D', '--debug',
                        action='store_true',
                        help='enable debugging, but make sure it\'s ' +
                        'switched off for public applications ' +
                        '(default: false)')

    return parser.parse_args()


def init():
    """Check for Python version and set default settings."""
    global CONTENT_PATH

    if sys.version_info[0] < 3:
        log.critical("Python 3 or newer in necessary.")
        sys.exit(1)

    if cli_args().debug:
        logging.basicConfig(level=logging.INFO)
        log.warning("Debugging is enabled but should be " +
                    "switched off for public applications.")

    CONTENT_PATH = CONTENT_PATH or cli_args().path

    if CONTENT_PATH:
        app.run(host=cli_args().host,
                port=cli_args().port,
                debug=cli_args().debug,
                reloader=cli_args().debug)
    else:
        log.critical("Please specify the path of the content.")


if __name__ == '__main__':

    init()