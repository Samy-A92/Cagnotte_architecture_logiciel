import os
from flask import Flask
from archilog.views import web_ui


def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv("ARCHILOG_SECRET_KEY", "dev_secret_key")

    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y à %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)

    app.register_blueprint(web_ui, url_prefix="/")

    return app

app = create_app()