import os
import flask
import numpy
import cv2
import time
import json
import subprocess
from flask_cors import CORS

DEFAULT_APP_NAME = __name__

def load_json_from_path(path):
    files = {}

    for file_name in os.listdir(path):

        try:
            with open(f"{path}/{file_name}", "r") as input_file:
                files[file_name] = json.load(input_file)

        except Exception as e:
            print(f"Trouble reading file {file_name} {e}")

    return files




def create_app(name=DEFAULT_APP_NAME, 
               default_log_level="INFO"):

    app = flask.Flask(name)
    CORS(app)

    log_level = os.environ.get(f"{app.name.upper()}_LOG_LEVEL", default_log_level)
    app.logger.setLevel(log_level)

    app.logger.info(f"Creating App {name}...")

    @app.route("/get_difference_files")
    def get_difference_file():
        return json.dumps(load_json_from_path("device_files/difference_files"))
    
    @app.route("/get_day_files")
    def get_today_file():
        return json.dumps(load_json_from_path("device_files/day_files"))


    return app



if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=2204,)
