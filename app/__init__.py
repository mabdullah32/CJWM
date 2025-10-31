from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__) #initializes flask

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False) #initializes sqlite3
c = db.cursor()

#Flask routes home.html
@app.route("/", methods=['GET','POST'])
def home():
    sorted_blogs = c.execute("SELECT blog_id, blog_name FROM blogs ORDER BY timestamp DESC")
    sorted_blogs_list = [x for x in sorted_blogs]
    return render_template('home.html', sorted_blogs_list = sorted_blogs_list)


@app.route("/handle_search_query", methods=['GET', 'POST'])
def handle_search_query():
    blog_req = request.args['searched_blog']
    print(blog_req)
    return render_template('home.html', sorted_blogs_list = sorted_blogs_list)

#Flask routes profile.html
@app.route("/profile", methods=['GET','POST'])
def profile():
    return render_template('profile.html')

#Flask routes blogs.html
@app.route("/blogs/<blog_id>.html", methods=['GET','POST'])
@app.route("/blogs/<blog_id>", methods=['GET','POST']) #Chrome and Librewolf handle urls differently, requiring both routes
def blogs(blog_id):
    if blog_id == None:
        return "Page Not Found 404" #doesn't seem to do anything?
    else:
        try:
            blog_db_info = c.execute(f"SELECT * FROM blogs WHERE blog_id = {blog_id}")
        except Exception:
            return f"Page Not Found 404 <br><br>No blog has ID {blog_id}"
        blog_info = [x for x in blog_db_info][0]
        return render_template('blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], author_name = blog_info[2], content = blog_info[3], timestamp = blog_info[4])

#Flask routes edit_blogs.html
@app.route("/blogs/<blog_id>/edit", methods=['GET','POST'])
def edit_blog(blog_id):
    if request.method == 'POST':
        new_blog_name = request.form.get('blog_name')
        new_content = request.form.get('content')

        blog_info = c.execute(f"SELECT content FROM blogs WHERE blog_id = {blog_id}").fetchone()
        old_content = blog_info[0]

        c.execute("INSERT INTO edits (blog_id, old_content, new_content, timestamp) VALUES (?, ?, ?, ?)",
                  (blog_id, old_content, new_content, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        c.execute("UPDATE blogs SET blog_name = ?, content = ?, timestamp = ? WHERE blog_id = ?",
                  (new_blog_name, new_content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), blog_id))

        db.commit()
        return redirect(f'/blogs/{blog_id}')

    blog_db_info = c.execute(f"SELECT * FROM blogs WHERE blog_id = {blog_id}")
    blog_info = [x for x in blog_db_info][0]
    return render_template('edit_blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], content = blog_info[3])

#==========================================================
#SQLITE3 DATABASE LIES BENEATH HERE
#==========================================================

#users (username, password, creation_date, last_login)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    creation_date DATE,
    last_login DATE
)""")

#blogs (blog_id, blog_name, author_name, content, timestamp)
c.execute("""
CREATE TABLE IF NOT EXISTS blogs (
    blog_id INTEGER PRIMARY KEY,
    blog_name STRING,
    author_name STRING,
    content STRING,
    timestamp TEXT,
    FOREIGN KEY (author_name) REFERENCES users(username)
)""")

#edits (edit_id, blog_id, old_content, new_content, timestamp)
c.execute("""
CREATE TABLE IF NOT EXISTS edits (
    edit_id INTEGER PRIMARY KEY,
    blog_id INTEGER,
    old_content STRING,
    new_content STRING,
    timestamp DATE,
    FOREIGN KEY (blog_id) REFERENCES blogs(blog_id)
)""")

#Generates Blog 1 and 2 for testing purposes
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (1, 'Magic', 'Harry Potter', 'Theres no need to call me sir, professor', datetime('1998-05-02 12:00:00'))")
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (2, 'Frogs', 'Kermit the Frog', 'I AM FROG FROG IS AWESOME', datetime('2025-10-30 10:40:15'))")

db.commit() #save changes

if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()

db.close()  #close database
