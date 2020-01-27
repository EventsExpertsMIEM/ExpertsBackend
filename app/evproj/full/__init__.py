import logging

from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_with_reloader

from flask import Flask
from flask_login import LoginManager
from gevent.pywsgi import WSGIServer
from gevent import monkey

from .. import cfg, api, questions
from ..core import auth
from . import views

app = Flask(__name__)
app.config.update(
    CSRF_ENABLED=cfg.CSRF_ENABLED,
    SECRET_KEY=cfg.SECRET_KEY,
    TEMPLATES_AUTO_RELOAD=True,
)


app.register_blueprint(views.bp)
app.register_blueprint(api.bp)
app.register_blueprint(questions.bp)
app.register_error_handler(404, views.page_not_found)

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
                    level=logging.INFO)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.user_loader(auth.user_loader)
login_manager.blueprint_login_views = {
    'general': '/login',
}


def run(debug=False):
    monkey.patch_all(ssl=False)

    if debug:
        app_debug = DebuggedApplication(app)

        def run_debug():
            http_server = WSGIServer((cfg.HOST, cfg.PORT), app_debug)
            logging.info('Started server in debug mode')
            http_server.serve_forever()

        run_with_reloader(run_debug)
    else:
        http_server = WSGIServer((cfg.HOST, cfg.PORT), app)
        logging.info('Started server')
        http_server.serve_forever()
