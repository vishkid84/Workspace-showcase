import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId 

from os import path  
if path.exists("env.py"):      
     import env 

app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'workspace_database'
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost')

mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/get_workspaces')
def get_workspaces():
    return render_template("workspaces.html", workspaces=mongo.db.workspaces.find())


@app.errorhandler(404)
def error_404(error):
    return render_template('error_pages/404.html', error=error)


@app.errorhandler(500)
def error_500(error):
    return render_template('error_pages/500.html', error=error)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)