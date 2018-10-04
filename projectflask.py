from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

# import CRUD Operations from Lesson 1 ##
from database_setup import Base, Catagory, Item
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB ##
engine = create_engine('sqlite:///catalogproject.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


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




