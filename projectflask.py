from flask import Flask, render_template, request, redirect, url_for, jsonify
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

# Decorator to call function if URL used
@app.route('/')
@app.route('/catagories/')
def catagoryList():
    catagory = session.query(Catagory).all()
    items = session.query(Item).all()
    return render_template('homepage.html', catagory = catagory, items = items)
    # output = ''
    # for i in catagory:
    #     output += i.name
    #     output += '</br>'

    # return output
    
# Decorator for routing individual Items
@app.route('/catagories/<int:catagory_id>/<int:item_id>/')
def catagoryItem(catagory_id, item_id):
    catagory = session.query(Catagory).filter_by(catagory_id = catagory.id).one()
    items = session.query(Item).filter_by(catagory_id = catagory.id)
    return render_template('catalog.html', catagory = catagory, items = items)

# Add new catagoryItem function
@app.route('/catagories/<int:catagory_id>/<int:item_id>/new/', methods = ['GET', 'POST'])
def newCatagoryItem(catagory_id, item_id):
    if request.method == 'POST':
        newItem = Item(name = request.form['name'], description = request.form['description'], catagory_id = catagory_id, item_id = item_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('catagoryItem', catagory_id = catagory_id, item_id = item_id))

    else:
        return render_template('newitem.html', catagory_id = catagory_id)

# Decorator for Viewing Item Description
@app.route('/catagories/<int:catagory_id>/<int:item_description>')
def itemDescription(catagory_id, item_description):
    description = session.query(Item).filter_by(catagory_id = catagory_id).all()
    output = ''
    for i in description:
         output += i.description
    return output

# Update catagoryItem function
@app.route('/catagories/<int:catagory_id>/<int:item_id>/update/', methods = ['GET', 'POST'])
def updateCatagoryItem(catagory_id, item_id):
    updatedItem = session.query(Item).filter_by (catagory_id = catagory_id).one()
    if request.method == 'POST':
        if request.form['name', 'description']:
            updatedItem.name = request.form['name']
            updatedItem.description = request.form['description']
        session.add(updatedItem)
        session.commit()
        return redirect(url_for('itemDescription', catagory_id = catagory_id))
    else:
        return render_template('updateitem.html', catagory_id = catagory_id, item_id = item_id)


# Delete catagoryItem function
@app.route('/catagories/<int:catagory_id>/<int:item_id>/delete/')
def deleteCatagoryItem(catagory_id, item_id):
    return "page to delete a Item"

# Run Server in Debug Mode
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000, threaded = False)




