# Spoonbill for Pelican

Spoonbill a is web front-end editor for [Pelican][0] and other static site generators, heavily inspired by [Shoebill][1].  
It uses [SimpleMDE][4] as a simple JS markdown editor and [Bottle][2] as a lightweight WSGI web-framework.

![Spoonbill screenshot](docs/screenshots/screenshot-1.png?raw=true)

## Run Spoonbill

* `$ python3 ./shoebill.py /path/to/the/pelican/content`

* Default username is `username` and password `password`.  
  The credentials are hard-coded to spoonbill.py and HTTP basic auth is probably not sufficient for production.

* Open in your browser: [http://localhost:8080/][5]

Optionally, you can specify:

    optional arguments:
     -path PATH            path of the content
     -p PORT, --port PORT  port (default: 8080)
     --host HOST           hostname (default: localhost)
     -D, --debug           enable debugging (default: false)
     
## Features

* Create, edit and delete files.
* Deploy site.
* Commit changes with git.
* Authentication (HTTP basic auth).

## Dependecies

* [Bottle][2] `pip install bottle`
* [GitPython][3] `pip install gitpython`

[0]:http://docs.getpelican.com/en/stable/
[1]:https://github.com/FedericoCeratto/shoebill
[2]:https://bottlepy.org/docs/dev/
[3]:https://gitpython.readthedocs.io/en/stable/
[4]:https://simplemde.com/
[5]:http://localhost:8080/