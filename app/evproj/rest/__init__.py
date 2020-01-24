from .. import cfg
from ..core import auth
from . import api as restful_api

from flask import Flask
from gevent.pywsgi import WSGIServer
from gevent import monkey
from flask_cors import CORS

import logging


app = Flask(__name__)
app.config.update(
    DEBUG=cfg.DEBUG,
    CSRF_ENABLED=cfg.CSRF_ENABLED,
    SECRET_KEY=cfg.SECRET_KEY,
    TEMPLATES_AUTO_RELOAD=True,
)

app.register_blueprint(restful_api.mod)
app.register_error_handler(404, restful_api.route_not_found)

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    level=logging.INFO)

CORS(app)

def run():
    monkey.patch_all(ssl=False)
    http_server = WSGIServer((cfg.HOST, cfg.PORT), app)
    logging.info('Started server')
    http_server.serve_forever()
