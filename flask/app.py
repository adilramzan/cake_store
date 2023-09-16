from flask import Flask, render_template, request, redirect, url_for , session ,jsonify
import sqlite3
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)

def create_tables():
    conn = sqlite3.connect('cake_store.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            username TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_price REAL NOT NULL,
            item_description TEXT NOT NULL,
            item_quantity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(username, password, first_name, last_name, email, address):
    conn = sqlite3.connect('cake_store.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (username, password, first_name, last_name, email, address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, password, first_name, last_name, email, address))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = sqlite3.connect('cake_store.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def create_cart(username):
    conn = sqlite3.connect('cake_store.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username TEXT NOT NULL,
            item_name TEXT NOT NULL,
            item_price REAL NOT NULL,
            item_description TEXT NOT NULL,
            item_quantity INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_item_to_cart(username, item_name, item_price, item_description):
    conn = sqlite3.connect('cake_store.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO carts (username, item_name, item_price, item_description)
        VALUES (?, ?, ?, ?)
    ''', (username, item_name, item_price, item_description))
    conn.commit()
    conn.close()

#create_tables()

def initialize_database():
    create_tables()  # Create tables if they don't exist

    # Check if any user exists; if not, insert dummy user data
    if not get_user_by_username('example_user'):
        insert_user('example_user', 'password123', 'John', 'Doe', 'john@example.com', '123 Main St')

@app.route('/')
def main_menu(  ):
    try:
        found_user = session["found_user"]
        user_firstname = found_user[3]
    except:
        
        user_firstname = ""

    cakes_list = pd.read_csv("./cakes.csv").values
    return render_template('main_menu.html' , user_firstname = user_firstname , cakes_list = cakes_list, item=cakes_list)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']  #email
        email = username
        password = request.form['password']
        address = ""
        
        found_user = get_user_by_username(username)
        print( found_user )
        #  If fields are not empty, email is correct, user does not exsit, password is acceptable
        if (found_user==None) and (username.strip()!="") and (password.strip()!=""):  # user[2] is the password field
            print(f"User Data:\nfirstname: {firstname}\nlastname: {lastname}\nUsername: {username}\nPassword: {password}")
            insert_user(username, password, firstname, lastname, email, address)
            return redirect('/login')
        else:
            error_message = "Some Problem with user information."
            return render_template('signup.html', error_message=error_message)
    
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        found_user = get_user_by_username(username)
        print( found_user )
        if found_user and found_user[2] == password:  # user[2] is the password field
            print(f"Login successful:\nUsername: {username}\nPassword: {password}")
            user_firstname = found_user[3]
            session["found_user"] = found_user
            #return main_menu( user_firstname )
            return redirect('/')
        else:
            error_message = "Invalid credentials. Please try again."
            return render_template('login.html', error_message=error_message)
      
    return render_template('login.html')



import csv

# Function to read cake data from CSV file
def read_cakes_from_csv():
    cakes = []
    with open('cakes.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cakes.append({
                'cake_name': row['cake_name'],
                'cake_price': float(row['cake_price']),  # Assuming price is a floating-point number in the CSV
                'cake_description':row['cake_description']
            })
    return cakes

import csv

# Function to read cake data from CSV file
def read_cakes_from_csv():
    cakes = []
    with open('cakes.csv', mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cakes.append({
                'cake_name': row['cake_name'].strip() ,
                'cake_price': float(row['cake_price']),  # Assuming price is a floating-point number in the CSV
                'cake_description': row['cake_description'].strip()
            })
    return cakes

# Route to add a cake to the cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    print( "add_to_cart called" )
    if request.method == 'POST':
        print( "add_to_cart post called" )
        cake_name = request.form['cake_name'].strip()  # Get the selected cake_name from the form
        print( "cake_name :", cake_name )
        # Read cake data from the CSV file
        cakes = read_cakes_from_csv()
        print( cakes )
        # Replace with the actual logged-in user's username (you can implement user sessions for this)
        try:
            found_user = session["found_user"]
        except:
            return redirect('/login')
        
        username = found_user[1]

        # Ensure the user has a cart
        create_cart(username)

        # Insert the selected cake into the user's cart
        for cake in cakes:
            if cake['cake_name'] == cake_name:
                insert_item_to_cart(username, cake['cake_name'], cake['cake_price'], cake['cake_description'])
                break  # Stop searching after finding and adding the selected cake

    return redirect('/')




@app.route('/get_cart_data')
def get_cart_data():
    try:
        found_user = session["found_user"]
        username = found_user[1]
    except:
        return jsonify({"cart_items": [], "cart_total": 0})
    
    print( "found_user : " , found_user  )

    # Query your database to fetch the user's cart data
    conn = sqlite3.connect('cake_store.db')
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, item_price FROM carts WHERE username = ?', (username,))
    cart_items = [{"item_name": row[0], "item_price": row[1]} for row in cursor.fetchall()]
    conn.close()

    print( cart_items )

    cart_total = sum(item["item_price"] for item in cart_items)

    return jsonify({"cart_items": cart_items, "cart_total": cart_total})


# Route to remove an item from the cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'found_user' not in session:
        return jsonify({'error': 'User not logged in'})

    if request.method == 'POST':
        data = request.get_json()
        itemName = data.get('itemName').strip()  # Get the item_id from the AJAX request

        # Get the username from the session
        found_user = session['found_user']
        username = found_user[1]

        print( "Delete from cart:" , itemName )
        # Implement code to remove the item from the cart based on item_id and username
        # You'll need to connect to your database and perform the removal operation here

        # Example code to remove the item from a SQLite database
        conn = sqlite3.connect('cake_store.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carts WHERE username = ? AND item_name = ?', (username, itemName))
        conn.commit()
        conn.close()

        # You can send a success response or any additional data you need
        return jsonify({'success': 'Item removed from cart'})

    # Handle invalid requests
    return jsonify({'error': 'Invalid request'})



if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)

