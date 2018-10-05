from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import session as login_session
import random, string
app = Flask(__name__)

# import CRUD Operations from Lesson 1 ##
from database_setup import Base, Catagory, Item
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogproject.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output



# Making an API Endpoint (GET Request)
@app.route('/catagories/<int:catagory_id>/JSON')
def catagoryItemsJSON(catagory_id):
    catagory = session.query(Catagory).filter_by(id = catagory_id).all()
    items = session.query(Item).filter_by(catagory_id = catagory_id).all()
    return jsonify(Items = [i.serialize for i in items])

# Decorator to call function if URL used
@app.route('/')
@app.route('/catagories/')
def catagoryList():
    catagories = session.query(Catagory).all()
    return render_template('homepage.html', catagories = catagories)

# Decorator for routing to All Items in Catagory
@app.route('/catagories/<int:catagory_id>/')
def catagoryItems(catagory_id):
    catagory = session.query(Catagory).filter_by(id = catagory_id).all()
    items = session.query(Item).filter_by(catagory_id = catagory_id).all()
    return render_template('catalogitems.html', items = items, catagory = catagory, catagory_id = catagory_id)


# Decorator for routing individual Item Descriptions
@app.route('/catagories/<int:catagory_id>/<int:item_id>/<string:description>')
def itemDescription(catagory_id, item_id, description):
    items = session.query(Item).filter_by(catagory_id = catagory_id, id = item_id)
    return render_template('catalog.html', items = items)

# Add new catagoryItem function
@app.route('/catagories/<int:catagory_id>/new/', methods = ['GET', 'POST'])
def newCatagoryItem(catagory_id):
    if request.method == 'POST':
        newItem = Item(name = request.form['name'], description = request.form['description'], catagory_id = catagory_id)
        session.add(newItem)
        session.commit()
        flash("New Item Successfuly Created !")
        return redirect(url_for('catagoryItems', catagory_id = catagory_id))
    else:
        return render_template('newitem.html', catagory_id = catagory_id)


# Update catagoryItem function
@app.route('/catagories/<int:catagory_id>/<int:item_id>/update/', methods = ['GET', 'POST'])
def updateCatagoryItem(catagory_id, item_id):
    updatedItem = session.query(Item).filter_by(catagory_id = catagory_id, id = item_id).one()
    if request.method == 'POST':
        updateItem = Item(name = request.form['name'], description = request.form['description'], catagory_id = catagory_id)
        session.add(updateItem)
        session.commit()
        flash("New Item Successfuly Updated !")
        return redirect(url_for('catagoryItems', catagory_id = catagory_id))
    else:
        return render_template('updateitem.html', catagory_id = catagory_id, i = updatedItem)


# Delete catagoryItem function
@app.route('/catagories/<int:catagory_id>/<int:item_id>/delete/', methods = ['GET','POST'])
def deleteCatagoryItem(catagory_id, item_id):
    deleteItem = session.query(Item).filter_by(catagory_id = catagory_id, id = item_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("New Item Successfuly Deleted !")
        return redirect(url_for('catagoryItems', catagory_id = catagory_id))
    else:
        return (render_template('deleteitem.html', removename = deleteItem.name, id = deleteItem.id, catagory_id = deleteItem.catagory_id))

# Run Server in Debug Mode
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000, threaded = False)




