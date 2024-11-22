from flask import Flask, render_template, request, redirect, url_for
import mysql.connector  # type: ignore
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",       # Replace with your MySQL host
            user="root",            # Replace with your MySQL username
            password="ppgnmil",     # Replace with your MySQL password
            database="user_db"      # Replace with your database name
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Sign-up route
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Validate form data
        if not name or not email or not password:
            return "All fields are required. Please try again."

        # Hash password
        hashed_password = generate_password_hash(password)
        print(f"Sign-Up Data: Name={name}, Email={email}, Password={hashed_password}")

        # Connect to the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Insert user into database
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed_password)
                )
                connection.commit()
                print("User added successfully!")
                return redirect(url_for('index'))
            except mysql.connector.IntegrityError as err:
                # Handle duplicate email error
                if err.errno == 1062:  # Duplicate entry code
                    return "Email already exists. Please use a different email."
                else:
                    print(f"MySQL Integrity Error: {err}")
                    return "An error occurred while signing up. Please try again."
            except mysql.connector.Error as err:
                print(f"MySQL Error: {err}")
                return "Database operation failed. Please try again."
            finally:
                cursor.close()
                connection.close()
        else:
            return "Database connection failed. Please check your connection settings."

@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        # Fetch form data
        email = request.form['email']
        password = request.form['password']

        # Validate form data
        if not email or not password:
            return "Both email and password are required."

        # Connect to the database
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Fetch user from database
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user and check_password_hash(user[3], password):  # user[3] is the hashed password
                    # Successful login, redirect to the main page
                    return redirect(url_for('main'))
                else:
                    return "Invalid email or password."
            except mysql.connector.Error as err:
                print(f"MySQL Error: {err}")
                return "An error occurred while signing in. Please try again."
            finally:
                cursor.close()
                connection.close()
        else:
            return "Database connection failed. Please check your connection settings."


# Route for main.html
@app.route('/main')
def main():
    return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)

