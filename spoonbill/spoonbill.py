"""Spoonbill: Web front-end for static site generator Pelican."""
# -*- coding: utf-8 -*-
import logging
import os
import sys
import argparse
import subprocess
import socketserver
import bottle
from git import Repo, InvalidGitRepositoryError
from pathlib import Path
from bottle import (Bottle, redirect, request,
                    static_file, auth_basic, template)

app = Bottle()
log = logging.getLogger('spoonbill')
root = os.path.abspath(os.path.dirname(__file__))

CONTENT_PATH = '{0}/{1}'.format(root, '../content')
FILE_EXTENSION = '.md'  # .md for MarkDown, .rst for reStructuredText etc.
USERNAME = 'username'
PASSWORD = 'password'
PELICAN_DEPLOY = 'pelican content -s publishconf.py -t'
GIT = False
GIT_AUTHOR = 'Spoonbill <spoonbill@nasa.com>'


def list_documents():
    """Get the list of files in the content directory."""
    try:
        file_list = []
        for root, dirs, files in os.walk(CONTENT_PATH):
            if files:
                for file in files:
                    if file.endswith(FILE_EXTENSION):
                        tag = os.path.relpath(root, CONTENT_PATH).lstrip('.')
                        if tag:
                            tag = '{0}{1}'.format(tag, '/')
                        file_list.append(tag + file)
        return file_list
    except Exception as error:
        log.error(error)


def open_document(file_name):
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
            return read_document(file_contents)
        else:
            log.info("File %s does not exist.", file_name)
            return False
    except Exception as error:
        log.error(error)


def read_document(doc):
    """Parse document, extract meta data and content."""
    document = doc.split('\n\n', 1)
    metadata = document[0]
    content = document[1].lstrip()
    return metadata, content


def save_document(file_name, file_metadata, file_contents):
    """Save the contents to file. If file does not exist, create it."""
    try:
        content = '{0}\n\n{1}'.format(file_metadata, file_contents)
        fo = open(os.path.join(CONTENT_PATH, file_name), 'w',
                  newline='\n', encoding='utf8')
        fo.write(content)
        fo.close()
        log.info("File %s saved.", file_name)
        commit_changes(file_name)
    except Exception as error:
        log.error(error)


def delete_document(file_name):
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


def default_document():
    """Boilerplate for the new markdown file."""
    metadata = ("title: Lorem Ipsum\n"
                "slug: lorem-ipsum\n"
                "date: 1939-09-01 11:00\n")
    content = "Lorem Ipsum"
    return metadata, content


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
    document = default_document()
    data = {'file_name': '{0}{1}'.format('lorem-ipsum', FILE_EXTENSION),
            'metadata': document[0],
            'content': document[1],
            'document_list': list_documents(),
            'site_url': '{0}://{1}'.format(request.urlparts.scheme,
                                           request.urlparts.netloc)}

    return template('default', data)


@app.route('/edit/<file_name:path>')
@auth_basic(credentials)
def edit(file_name):
    """Editing route."""
    document = open_document(file_name)
    if not document:
        document = default_document()
    data = {'file_name': file_name,
            'metadata': document[0],
            'content': document[1],
            'document_list': list_documents(),
            'site_url': '{0}://{1}'.format(request.urlparts.scheme,
                                           request.urlparts.netloc)}
    return template('default', data)


@app.route('/delete/<file_name:path>')
@auth_basic(credentials)
def delete(file_name):
    """Editing route."""
    delete_document(file_name)
    redirect('/')


@app.route('/save/', method='POST')
@auth_basic(credentials)
def save():
    """Save the file contents and redirect."""
    file_name = request.forms.decode().get('file_name')
    metadata = request.forms.decode().get('metadata')
    content = request.forms.decode().get('content')
    if request.forms.get('save'):
        save_document(file_name, metadata, content)
        redirect('/{0}/{1}'.format('edit', file_name))
    if request.forms.get('save_and_build'):
        save_document(file_name, metadata, content)
        if PELICAN_DEPLOY:
            log.info("Deploying Pelican.")
            # Subprocess is non-blocking and will run in the background.
            subprocess.Popen(PELICAN_DEPLOY,
                             shell=True, stderr=subprocess.STDOUT)
        redirect('/{0}/{1}'.format('edit', file_name))


@app.route('/static/<filename>', name='static')
def server_static(filename):
    """Everything in static directory is accessible."""
    return static_file(filename, root='{0}/{1}'.format(root, 'static'))


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


def settings():
    """Check for Python version and set Bottle settings."""
    global CONTENT_PATH
    CONTENT_PATH = CONTENT_PATH or cli_args().path

    # Give an absolute path for views if Spoonbill
    # is not executed from working directory.
    bottle.TEMPLATE_PATH.insert(0, '{0}/{1}'.format(root, 'views'))

    # Allow the server to reuse an address if the program crashes.
    socketserver.TCPServer.allow_reuse_address = True

    if sys.version_info[0] < 3:
        log.critical("Python 3 or newer in necessary.")
        sys.exit(1)

    if cli_args().debug:
        logging.basicConfig(level=logging.INFO)
        log.warning("Debugging is enabled but should be " +
                    "switched off for public applications.")


def main():
    """Start Bottle."""
    settings()
    if CONTENT_PATH:
        app.run(host=cli_args().host,
                port=cli_args().port,
                debug=cli_args().debug,
                reloader=cli_args().debug)
    else:
        log.critical("Please specify the path of the content.")

if __name__ == '__main__':
    main()
