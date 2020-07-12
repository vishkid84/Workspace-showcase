import os
from flask import Flask, render_template, redirect, request, url_for, session
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
    return render_template("workspaces.html", workspaces=mongo.db.workspaces.find().sort("_id", -1))


@app.route('/add_workspaces')
def add_workspaces():
    return render_template('addworkspaces.html', rooms=mongo.db.rooms.find(), ratings=mongo.db.ratings.find(),
                            preferences=mongo.db.preferences.find(), indexes=mongo.db.indexes.find())

@app.route('/insert_workspaces', methods=['POST'])
def insert_workspaces():
    workspaces = mongo.db.workspaces
    workspaces.insert_one(request.form.to_dict())
    return redirect(url_for('get_workspaces'))


@app.route('/edit_workspaces/<workspace_id>')
def edit_workspaces(workspace_id):
    current_workspace = mongo.db.workspaces.find_one({'_id': ObjectId(workspace_id)})
    return render_template('editworkspaces.html', workspace=current_workspace, rooms=mongo.db.rooms.find(), 
                            ratings=mongo.db.ratings.find(), preferences=mongo.db.preferences.find(), indexes=mongo.db.indexes.find())


@app.route('/update_workspaces/<workspace_id>', methods=['POST'])
def update_workspaces(workspace_id):
    workspaces = mongo.db.workspaces
    workspaces.update({'_id': ObjectId(workspace_id)},
    {
        'workspace_room': request.form.get('workspace_room'),
        'workspace_rating': request.form.get('workspace_rating'),
        'workspace_preference': request.form.get('workspace_preference'),
        'happiness_index': request.form.get('happiness_index'),
        'image': request.form.get('image'),
        'comments': request.form.get('comments'),
    })
    return redirect(url_for('get_workspaces'))


@app.route('/delete_workspaces/<workspace_id>')
def delete_workspaces(workspace_id):
    mongo.db.workspaces.remove({'_id': ObjectId(workspace_id)})
    return redirect(url_for('get_workspaces'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')


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