# Author: Christopher Garcia
# 11/20/2019
# Course Name: CST205
# Testing for the dropdown/text field module for the SoundBites app

# Imports
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import os

# Creates the app for Flask
app = Flask(__name__)

# Home Page
@app.route("/", methods=['GET', 'POST'])
def home():
    option_list = ['option1', 'option2', 'option3', 'option4']
    option=""
    if request.method == "POST":
        option = request.form['option']
    return render_template("home.html", option_list=option_list, option=option)


# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# RUNS THE APP!
if __name__ == "__main__":
    app.run(debug=True)

Bootstrap = Bootstrap(app)