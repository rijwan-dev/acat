from .routes import main
import os
from flask import Flask

def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__,
        static_folder="static",
        template_folder="templates"
    )
    app.config.from_object(config_class)

    upload_dir = os.path.join(app.root_path, "uploads")
    temp_dir = os.path.join(app.root_path, "temp")
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    app.config["directory_upload"] = upload_dir
    app.config["directory_temp"] = temp_dir
    app.config["max_content_length"] = 50 * 1024 * 1024

    app.register_blueprint(main)
    return app

