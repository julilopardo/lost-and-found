import os, datetime, sqlite3, requests, urllib.parse

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lostfound.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")

def move_lost():
    return render_template("lost.html")

def move_found():
    return render_template("found.html")

@app.route("/lost", methods=["GET", "POST"])
@login_required
def lost():

    if request.method == "GET":
        return render_template("lost.html")

    if request.method == "POST":
        pet_type = request.form.get("inputtype").upper()
        pet_name = request.form.get("inputname").upper()
        user_id= session.get("user_id")
        color = request.form.get("inputcolor").upper()
        breed = request.form.get("inputbreed").upper()
        gender = request.form.get("inputgender")
        size = request.form.get("inputsize")
        date = request.form.get("inputdate")
        country = request.form.get("inputcountry").upper()
        state = request.form.get("inputstate").upper()
        city = request.form.get("inputcity").upper()
        age = request.form.get("inputage")
        mail = request.form.get("inputmail")
        phone = request.form.get("inputphone")
        special  = request.form.get("inputfeatures")
        photo = request.form.get("inputimage")

        db.execute("INSERT INTO pets (user_id, pet_name, type, color, breed, gender, size, date, lost_found, country, state, city, age, mail, phone, special) VALUES (:user_id, :pet_name, :pet_type, :color, :breed, :gender, :size, :date, 'LOST', :country, :state, :city, :age, :mail, :phone, :special)",
                        user_id=user_id, pet_name=pet_name, pet_type=pet_type, color=color, breed=breed, gender=gender, size=size, date=date, country=country, state=state, city=city, age=age, mail=mail, phone=phone, special=special)

        #Load image to folder in static/photos. Named after pet_id
        current_pet = db.execute("SELECT pet_id FROM pets WHERE user_id =:user_id AND pet_name=:pet_name AND type=:pet_type AND color=:color AND breed=:breed AND gender=:gender AND size=:size AND date=:date AND lost_found='LOST' AND country=:country AND state=:state AND city=:city AND age=:age AND mail=:mail AND phone=:phone",
                        user_id=user_id, pet_name=pet_name, pet_type=pet_type, color=color, breed=breed, gender=gender, size=size, date=date, country=country, state=state, city=city, age=age, mail=mail, phone=phone)

        pet_id = current_pet[0]["pet_id"]

        f = request.files['inputimage']
        sfname = 'static/photos/'+ str(pet_id) + ".jpg"
        f.save(sfname)


        found_table = db.execute("SELECT pet_id, type, color, breed, gender, size, lost_found, age, city, special, photo, mail, phone FROM pets WHERE type=:pet_type AND color=:color AND breed=:breed AND gender=:gender AND size=:size AND lost_found='FOUND' AND age=:age AND country=:country", pet_type=pet_type, color=color, breed=breed, gender=gender, size=size, country=country, age=age)


        if len(found_table) == 0:
            return render_template("results.html", results="No results in our database that matches your search. We keep your pet's information and your contact data, and if we find a match, someone will contact you soon!")

        else:
            return render_template("results.html", found_table = found_table)

@app.route("/found", methods=["GET", "POST"])
@login_required
def found():

    if request.method == "GET":
        return render_template("found.html")

    if request.method == "POST":
        pet_type = request.form.get("inputtype").upper()
        user_id= session.get("user_id")
        color = request.form.get("inputcolor").upper()
        breed = request.form.get("inputbreed").upper()
        gender = request.form.get("inputgender")
        size = request.form.get("inputsize")
        date = request.form.get("inputdate")
        country = request.form.get("inputcountry").upper()
        state = request.form.get("inputstate").upper()
        city = request.form.get("inputcity").upper()
        age = request.form.get("inputage")
        mail = request.form.get("inputmail")
        phone = request.form.get("inputphone")
        special  = request.form.get("inputfeatures")



        db.execute("INSERT INTO pets (user_id, type, color, breed, gender, size, date, lost_found, country, state, city, age, mail, phone, special) VALUES (:user_id, :pet_type, :color, :breed, :gender, :size, :date, 'FOUND', :country, :state, :city, :age, :mail, :phone, :special)",
                        user_id=user_id, pet_type=pet_type, color=color, breed=breed, gender=gender, size=size, date=date, country=country, state=state, city=city, age=age, mail=mail, phone=phone, special=special)

        #Load image to folder in static/photos. Named after pet_id
        current_pet = db.execute("SELECT pet_id FROM pets WHERE user_id =:user_id AND type=:pet_type AND color=:color AND breed=:breed AND gender=:gender AND size=:size AND date=:date AND lost_found='FOUND' AND country=:country AND state=:state AND city=:city AND age=:age AND mail=:mail AND phone=:phone",
                        user_id=user_id, pet_type=pet_type, color=color, breed=breed, gender=gender, size=size, date=date, country=country, state=state, city=city, age=age, mail=mail, phone=phone)

        pet_id = current_pet[0]["pet_id"]

        f = request.files['inputimage']
        sfname = 'static/photos/'+ str(pet_id) + ".jpg"
        f.save(sfname)

        lost_table = db.execute("SELECT pet_id, type, color, breed, gender, size, lost_found, age, city, special, photo, mail, phone FROM pets WHERE type=:pet_type AND color=:color AND breed=:breed AND gender=:gender AND size=:size AND lost_found='LOST' AND age=:age AND country=:country", pet_type=pet_type, color=color, breed=breed, gender=gender, size=size, country=country, age=age)

        if len(lost_table) == 0:
            return render_template("results.html", results = "No results in our database that matches your search. We keep your pet's information and your contact data, and if we find a match, someone will contact you soon!")

        else:
            return render_template("results.html", lost_table = lost_table)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", alert="Must provide a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", alert="Must provide a password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", alert="Incorrect user/password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    """Register user"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("register.html", alert=" ")

    # User reached route via POST (as by submitting a form via POST)
    else:

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Hash password
        passhash = generate_password_hash(password)
        special_char = ['$','#','@', '%']

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("register.html", alert="Must provide a username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("register.html", alert="Must provide a password")

        if password != confirmation:
            return render_template("register.html", alert="Passwords don't match")

        if len(password) < 6:
            return render_template("register.html", alert="Length should be at least 6 characters")

        if not any(char.isdigit() for char in password):
            return render_template("register.html", alert="Password must have at least one numerical character")

        if not any(char.isupper() for char in password):
            return render_template("register.html", alert="Password must have at least one uppercase letter")

        if not any(char.islower() for char in password):
            return render_template("register.html", alert="Password must have at least one lowercase letter")

        if not any(char in special_char for char in password):
            return render_template("register.html", alert="Password must have at least one of the symbols $@#%")


        # Ensure username does not exist already

        count = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if not len(count) == 0:
            return render_template("register.html", alert="Username already exists, choose another one")


        # Add user to table "users" in database

        db.execute("INSERT INTO users (username, hash) VALUES (:username, :passhash)", username=username, passhash=passhash)

        # Redirect user to log in
        return redirect("/login")

@app.route("/mypets")
@login_required
def mypets():
    if request.method == "GET":
        pets_table = db.execute("SELECT pet_id, type, pet_name, color, breed, gender, size, date, lost_found, country, state, city, age, special, photo FROM pets WHERE user_id = :user_id ORDER BY date DESC", user_id=session.get("user_id"))

        if len(pets_table) == 0:
            return render_template("mypets.html", alert = "You haven't found or lost any pets yet")

        else:
            return render_template("mypets.html", pets_table = pets_table, alert = "If pet and owner are already reunited, please click Found! buttom so we eliminate it from our data base")

    if request.method == "POST":
        delete_record()

@app.route("/delete", methods=['POST'])
def delete():
    db.execute("DELETE FROM pets WHERE pet_id = ?", [request.form['pet_id']])
    os.remove("static/photos/" + str(request.form['pet_id']) + ".jpg")

    return redirect("/mypets")

