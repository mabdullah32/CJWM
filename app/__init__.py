from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

#Flask routes home page
@app.route("/", methods=['GET','POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    sorted_blogs = c.execute("SELECT blog_id, blog_name FROM blogs ORDER BY timestamp DESC")
    sorted_blogs_list = [x for x in sorted_blogs]
    return render_template('home.html', sorted_blogs_list = sorted_blogs_list, users_list = [])

@app.route("/handle_search_query", methods=['GET', 'POST'])
def handle_search_query():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    search_req = request.args['searched_item']
    searched_blogs_list = [x for x in c.execute(f"SELECT blog_id, blog_name FROM blogs WHERE blog_name LIKE '%{search_req}%' ORDER BY timestamp DESC")]
    searched_blogs_list += [x for x in c.execute(f"SELECT blog_id, blog_name FROM blogs WHERE content LIKE '%{search_req}%' ORDER BY timestamp DESC") if x not in searched_blogs_list]

    searched_users_list = [x[0] for x in c.execute(f"SELECT username FROM users WHERE username LIKE '%{search_req}%'")]
    return render_template('home.html', sorted_blogs_list = searched_blogs_list, users_list = searched_users_list)

@app.route("/create_account", methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if " " in username:
            return "Username cannot contain spaces."

        if c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone():
            return "Username already exists."

        c.execute("INSERT INTO users (username, password, creation_date, last_login) VALUES (?, ?, ?, ?)",
                  (username, password, datetime.now(), None))
        db.commit()

        return redirect(url_for('login'))
    
    return render_template("create_account.html")



@app.route("/login", methods=['GET', 'POST'])
def login():

    if(request.method == 'POST'):
        username = request.form['username']  
        password = request.form['password']

        user = c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if not user:
            return "invalid username/password"
        
        session['username'] = username
        c.execute("UPDATE users SET last_login=? WHERE username=?", (datetime.now(), username))
        db.commit()
        return redirect(url_for('home'))

    return render_template('login.html')


#Flask routes blogs.html
@app.route("/blogs/<blog_id>.html", methods=['GET','POST'])
@app.route("/blogs/<blog_id>", methods=['GET','POST']) #Chrome and Librewolf handle urls differently, requiring both routes
def blogs(blog_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if blog_id == None:
        return "Page Not Found 404" #doesn't seem to do anything?
    else:
        try:
            blog_db_info = c.execute("SELECT * FROM blogs WHERE blog_id = ?", (blog_id))
            blog_info = [x for x in blog_db_info][0]
        except Exception:
            return f"Page Not Found 404 <br><br>No blog has ID {blog_id}"
        return render_template('blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], author_name = blog_info[2], content = blog_info[3], timestamp = blog_info[4])

#Flask routes edit_blogs.html
@app.route("/blogs/<blog_id>/edit", methods=['GET','POST'])
def edit_blog(blog_id):

    if 'username' not in session:
        return redirect(url_for('login'))
    

    if request.method == 'POST':
        new_blog_name = request.form.get('blog_name')
        new_content = request.form.get('content')

        blog_info = c.execute("SELECT content FROM blogs WHERE blog_id = ?", (blog_id)).fetchone()
        old_content = blog_info[0]
        # author_name = 

        c.execute("INSERT INTO edits (blog_id, old_content, new_content, timestamp) VALUES (?, ?, ?, ?)",
                  (blog_id, old_content, new_content, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        c.execute("UPDATE blogs SET blog_name = ?, content = ?, timestamp = ? WHERE blog_id = ?",
                  (new_blog_name, new_content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), blog_id))

        db.commit()
        return redirect(f'/blogs/{blog_id}')
    try:
        blog_db_info = c.execute(f"SELECT * FROM blogs WHERE blog_id = {blog_id}")
        blog_info = [x for x in blog_db_info][0]
    except Exception:
        return f"Page Not Found 404 <br><br>No blog has ID {blog_id}"
    return render_template('edit_blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], content = blog_info[3])

@app.route("/new_blog", methods=['GET', 'POST'])
def create_blog():
    if request.method == "POST":
        blog_id = [x[0] for x in c.execute("SELECT MAX(blog_id) + 1 FROM blogs")][0]
        blog_name = request.form.get('blog_name')
        author_name = session['username']
        content = request.form.get('content')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (?, ?, ?, ?, ?)", 
                    (blog_id, blog_name, author_name, content, timestamp))
        
        db.commit()
        return redirect(f'/blogs/{blog_id}')
    
    blog_id = [x[0] for x in c.execute("SELECT MAX(blog_id) + 1 FROM blogs")][0]
    return render_template('edit_blogs.html', blog_id = blog_id, blog_name = "", content = "")
    

@app.route("/profile", methods=["GET"])
def profile():
    username = request.args.get("u")

    if not username:
        return "No username provided. Try /profile?u=HarryPotter"

    try:
        user_row = c.execute(
            "SELECT username, creation_date, last_login FROM users WHERE username = ?",(username,)).fetchone()

        if user_row is None:
            return f"No such user: {username}"

        # Select both blog title and content
        blog_rows = c.execute(
            "SELECT blog_name, blog_id FROM blogs WHERE author_name = ? ORDER BY timestamp DESC",(username,)).fetchall()

        # Pass the session as well for navbar
        return render_template("profile.html", user=username, blogs=blog_rows, session=session)

    except Exception as e:
        return f"Error loading profile: {e}"


#==========================================================
#SQLITE3 DATABASE LIES BENEATH HERE
#==========================================================

#users (username, password, creation_date, last_login)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    creation_date TEXT,
    last_login TEXT
)""")

c.execute("""
CREATE TABLE IF NOT EXISTS blogs (
    blog_id INTEGER PRIMARY KEY,
    blog_name STRING,
    author_name STRING,
    content STRING,
    timestamp TEXT,
    FOREIGN KEY (author_name) REFERENCES users(username)
)""")

c.execute("""
CREATE TABLE IF NOT EXISTS edits (
    edit_id INTEGER PRIMARY KEY,
    blog_id INTEGER,
    old_content STRING,
    new_content STRING,
    timestamp DATE,
    FOREIGN KEY (blog_id) REFERENCES blogs(blog_id)
)""")

#Generates example users for testing purposes
c.execute("INSERT OR REPLACE INTO users (username, password, creation_date, last_login) VALUES ('HarryPotter', 'boywholived', datetime('1980-07-31 05:30:00'), datetime('2022-06-05 14:52:00'))")
c.execute("INSERT OR REPLACE INTO users (username, password, creation_date, last_login) VALUES ('KermitTheFrog', 'idkwhour', datetime('2000-01-01 00:00:00'), datetime('2024-10-04 09:51:00'))")
c.execute("INSERT OR REPLACE INTO users (username, password, creation_date, last_login) VALUES ('Jeff', 'blogger123', datetime('2008-05-23 20:00:00'), datetime('2025-11-05 10:52:00'))")

#Generates example blogs for testing purposes
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (1, 'Magic', 'HarryPotter', 'Theres no need to call me sir, professor', datetime('1998-05-02 12:00:00'))")
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (3, 'Magical Wands', 'HarryPotter', 'Avada Kedavra', datetime('1991-08-01 12:00:00'))")
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (4, 'Voldemort', 'HarryPotter', 'He is a magical guy doing bad stuff', datetime('1981-10-31 20:00:00'))")
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (2, 'Frogs', 'KermitTheFrog', 'I AM FROG FROG IS AWESOME', datetime('2025-10-30 10:40:15'))")

db.commit() #save changes

if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()

db.close()  #close database
