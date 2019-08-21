from flask import Flask
from src.facade.app_facade import AppFacade

flask_app = Flask(__name__)


@flask_app.route("/", methods=["GET"])
def hello_world():
    return "<h1>hello world</h1>"


if __name__ == '__main__':
    AppFacade.get_instance().init_server(flask_app)
    AppFacade.get_instance().app_ready()

    flask_app.run()
