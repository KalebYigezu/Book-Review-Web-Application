import os

from flask import Flask, session

app = Flask(__name__)

@app.route("/")
def index():
    return "Project 1: TODO"


if __name__ == "__main__":
    app.run()
