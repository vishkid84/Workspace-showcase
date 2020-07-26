import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_paginate import Pagination, get_page_args
import math
import bcrypt

from os import path
if path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = 'workspace_database'
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost')
app.config["SECRET_KEY"] = os.urandom(24)

mongo = PyMongo(app)

# Number of workspaces to be displayed per page for pagination
page_limit = 9


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/get_workspaces', methods=['POST', 'GET'])
def get_workspaces():
    # get current page for pagination
    current_page = int(request.args.get('current_page', 1))
    # get total of all the workspaces in db
    total = mongo.db.workspaces.count()
    # Add current_position of the current page set at 0
    current_position = (current_page - 1)
    # Show the maximum number of pages
    max_pages = int(math.ceil(total / page_limit))

    workspaces = mongo.db.workspaces.find().sort(
        "_id", -1).limit(page_limit).skip(current_position * page_limit)
    return render_template("workspaces.html", workspaces=workspaces,
                           current_page=current_page, page_limit=page_limit,
                           total=total, current_position=current_position,
                           max_pages=max_pages, page='get_workspaces')


@app.route('/filter', methods=['POST', 'GET'])
def filter():
    result = request.form.get('filter_results')
    filtered_result = {'workspace_room': result}

    # get current page for pagination
    current_page = int(request.args.get('current_page', 1))
    # get total of all the workspaces in db
    total = mongo.db.workspaces.count({'workspace_room': result})
    # Add current_position of the current page set at 0
    current_position = int(request.args.get('current_position', 0))
    # Show the maximum number of pages
    max_pages = int(math.ceil(total / page_limit))

    '''
    Get workspace name from 'filter_results' form,
    assigned it as variable result.
    If result is none, return all the workspaces.
    Else return all the workspaces where the result
    is the same as workspace_room in mongodb.
    Assigned this to a variable named filter
    '''
    if result is None:
        workspaces = mongo.db.workspaces.find().sort(
            "_id", -1).limit(page_limit).skip(current_position)
        return render_template("workspaces.html",
                               workspaces=workspaces,
                               current_page=current_page,
                               page_limit=page_limit, total=total,
                               current_position=current_position,
                               max_pages=max_pages, page='get_workspaces')

    workspaces = mongo.db.workspaces.find({'workspace_room': result}).sort(
        "_id", -1).limit(page_limit).skip(current_position)
    return render_template('workspaces.html', workspaces=workspaces,
                           current_page=current_page, page_limit=page_limit,
                           total=total, current_position=current_position,
                           max_pages=max_pages, page='filter', result=result)


@app.route('/profile')
def profile():
    '''
    If user is not logged in, redirect to login page.
    if user is logged in, find all workspaces added by user.
    This is done by 'username' key in mongodb and session username.
    Return profile.html to take to the My Profile page.
    '''

    if 'username' not in session:
        flash('You need to be logged in to add workspace', 'warning')
        return redirect(url_for('login'))
    workspaces = mongo.db.workspaces.find(
        {'username': session['username']}).sort("_id", -1)
    return render_template("profile.html", workspaces=workspaces,
                           session_username=session['username'],
                           page='profile')


@app.route('/sort_ascending')
def sort_ascending():
    # get current page for pagination
    current_page = int(request.args.get('current_page', 1))
    # get total of all the workspaces in db
    total = mongo.db.workspaces.count({})
    # Add current_position of the current page set at 0
    current_position = int(request.args.get('current_position', 0))
    # Show the maximum number of pages
    max_pages = int(math.ceil(total / page_limit))

    '''
    If user is logged in, check if page name is profile.
        If it is, that means they are in the 'My profile' page.
        Sort ascending based on workspace rating.
    If user is not logged in, redirect to login page
    '''
    page = request.args.get('page')
    if 'username' in session:
        if page == 'profile':
            workspaces = mongo.db.workspaces.find(
                {'username': session['username']}).sort("workspace_rating", 1)
            return render_template("profile.html", workspaces=workspaces,
                                   session_username=session['username'],
                                   page='profile')

    return redirect(url_for('login'))


@app.route('/sort_descending')
def sort_descending():
    # get current page for pagination
    current_page = int(request.args.get('current_page', 1))
    # get total of all the workspaces in db
    total = mongo.db.workspaces.count({})
    # Add current_position of the current page set at 0
    current_position = int(request.args.get('current_position', 0))
    # Show the maximum number of pages
    max_pages = int(math.ceil(total / page_limit))

    '''
    If user is logged in, check if page name is profile.
        If it is, that means they are in the 'My profile' page.
        Sort descending based on workspace rating.
    If user is not logged in, redirect to login page
    '''

    page = request.args.get('page')
    if 'username' in session:
        if page == 'profile':
            workspaces = mongo.db.workspaces.find(
                {'username': session['username']}).sort("workspace_rating", -1)
            return render_template("profile.html", workspaces=workspaces,
                                   session_username=session['username'],
                                   page='profile')

    return redirect(url_for('login'))


@app.route('/one_workspace/<workspace_id>')
def one_workspace(workspace_id):
    current_workspace = mongo.db.workspaces.find_one(
        {'_id': ObjectId(workspace_id)})
    return render_template('oneworkspace.html', workspace=current_workspace)


@app.route('/register', methods=['POST', 'GET'])
def register():
    '''
    Check if method is POST. If not, render template for Register.
    If yes, create collection named  users.
    Check if user is exist by using username in form.
        If no existing user, hash password and insert into users.
        into the users collection and redirect to workspaces page.
        If user exist, return render template for register.
    '''

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                       request.form['password'].encode('utf-8'),
                       bcrypt.gensalt())
            users.insert({'name': request.form['username'],
                         'password': hashpass})
            session['username'] = request.form['username']
            session['logged_in'] = True
            flash('Hello ' + session['username'] +
                  ', you have been successfully registered and logged in',
                  'success')
            return redirect(url_for('get_workspaces'))

        else:
            flash('This username is taken, please use another one', 'warning')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    '''
    Check if method is POST. If not, render template for Login.
    If yes, create collection named users and
    another named login_user to find the username from the form.
        If there is login_user, check if password entered
        is the same as the hashed password in the database,
        create session username with and login username,
        set session logged in to True and redirect
        to My Profile page with flash logged in message.
        If there is no login_user, flash message and
        return render template for Login.
    '''

    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})

        if login_user:
            if bcrypt.checkpw(
              request.form['password'].encode('utf-8'),
              login_user['password']):
                session['username'] = login_user['name']
                flash('Hello ' + session['username'] +
                      ', you have been logged in', 'success')
                session['logged_in'] = True
                return redirect(url_for('profile'))
            else:
                flash('Invalid username or password', 'danger')
                return render_template('login.html')

    return render_template('login.html')


@app.route('/add_workspaces')
def add_workspaces():
    if 'username' not in session:
        flash('You need to be logged in to add workspace', 'warning')
        return redirect(url_for('login'))
    return render_template('addworkspaces.html',
                           rooms=mongo.db.rooms.find(),
                           ratings=mongo.db.ratings.find(),
                           preferences=mongo.db.preferences.find(),
                           indexes=mongo.db.indexes.find(),
                           session_username=session['username'])


@app.route('/insert_workspaces', methods=['POST'])
def insert_workspaces():
    '''
    Check if user is logged in. If not redirect to login page
    If user is logged in, check if method is POST.
    If not, return to add workspaces page.
    If method is post get the workspaces collection.
    Insert from form as dict. Show flash message and redirect to profile page.
    '''
    if 'username' in session:
        if request.method == 'POST':
            workspaces = mongo.db.workspaces
            workspaces.insert(request.form.to_dict())
            flash('You have added a new workspace', 'success')
            return redirect(url_for('profile'))
        return render_template('addworkspaces.html',
                               rooms=mongo.db.rooms.find(),
                               ratings=mongo.db.ratings.find(),
                               preferences=mongo.db.preferences.find(),
                               indexes=mongo.db.indexes.find(),
                               session_username=session['username'])
    flash('You need to be logged in to add workspace', 'warning')
    return redirect(url_for('login'))


@app.route('/edit_workspaces/<workspace_id>')
def edit_workspaces(workspace_id):
    '''
    Check if user is logged in:
      Get the workspace by id.
      Check if username in session is the same
      as the username in the workspace:
         Return editworkspaces page
      else redirect to login page
    If user not logged in, redirect to login page
    '''
    if 'username' in session:
        current_workspace = mongo.db.workspaces.find_one(
            {'_id': ObjectId(workspace_id)})
        if session['username'] == current_workspace['username']:
            current_workspace = mongo.db.workspaces.find_one(
                {'_id': ObjectId(workspace_id)})
            return render_template('editworkspaces.html',
                                   workspace=current_workspace,
                                   rooms=mongo.db.rooms.find(),
                                   ratings=mongo.db.ratings.find(),
                                   preferences=mongo.db.preferences.find(),
                                   indexes=mongo.db.indexes.find(),
                                   session_username=session['username'])
        flash('You need to be logged in to edit a workspace', 'danger')
        return redirect(url_for('login'))
    flash('You need to be logged in to edit a workspace', 'danger')
    return redirect(url_for('login'))


@app.route('/update_workspaces/<workspace_id>', methods=['POST'])
def update_workspaces(workspace_id):
    '''
    Check if user is logged in:
    If not logged in, redirect to login page.
      If yes, check if method is POST:
          If yes, get the workspace by id,
          update the workspace and redirect to workspaces page.
          If no, return to editworkspaces page.
    '''
    if 'username' in session:
        if request.method == 'POST':
            workspaces = mongo.db.workspaces
            workspaces.update({'_id': ObjectId(workspace_id)},
                              {
                                'workspace_room': request.form.get(
                                    'workspace_room'),
                                'workspace_rating': request.form.get(
                                    'workspace_rating'),
                                'workspace_preference': request.form.get(
                                    'workspace_preference'),
                                'happiness_index': request.form.get(
                                    'happiness_index'),
                                'image': request.form.get(
                                    'image'),
                                'comments': request.form.get(
                                    'comments'),
                                'username': session['username']
                              })
            return redirect(url_for('profile'))
        return render_template('editworkspaces.html',
                               workspace=current_workspace,
                               rooms=mongo.db.rooms.find(),
                               ratings=mongo.db.ratings.find(),
                               preferences=mongo.db.preferences.find(),
                               indexes=mongo.db.indexes.find(),
                               session_username=session['username'])
    flash('You need to be logged in to edit workspace', 'warning')
    return redirect(url_for('login'))


@app.route('/delete_workspaces/<workspace_id>')
def delete_workspaces(workspace_id):
    '''
    Check if user is logged in
    If not, redirect to login page.
    If logged in, create a current_workspace variable to get the workspace
    by workspace_id.
    Check if session username is the same as the username in the workspace.
        If yes, remove the workspace. If not, redirect to login page.
    '''
    if 'username' in session:
        current_workspace = mongo.db.workspaces.find_one(
            {'_id': ObjectId(workspace_id)})
        if session['username'] == current_workspace['username']:
            mongo.db.workspaces.remove({'_id': ObjectId(workspace_id)})
            return redirect(url_for('profile'))
        flash('You need to be logged in to edit a workspace', 'danger')
        return redirect(url_for('login'))
    flash('You need to be logged in to edit a workspace', 'danger')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    flash('You have been logged out', 'warning')
    session['logged_in'] = False
    return redirect(url_for('get_workspaces'))


@app.route('/charts')
def charts():
    return render_template('charts.html')


@app.errorhandler(404)
def error_404(error):
    return render_template('error_pages/404.html', error=error)


@app.errorhandler(500)
def error_500(error):
    return render_template("charts.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)
