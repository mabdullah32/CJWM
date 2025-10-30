from flask import Flask, render_template
import sqlite3

app = Flask(__name__) #initializes flask

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False) #initializes sqlite3
c = db.cursor()

#Flask routes home.html
@app.route("/", methods=['GET','POST'])
def home():
    return render_template('home.html')

#Flask routes profile.html
@app.route("/profile", methods=['GET','POST'])
def profile():
    return render_template('profile.html')

#Flask routes blogs.html
@app.route("/blogs/<blog_id>.html", methods=['GET','POST'])
def blogs(blog_id):
    if blog_id == None:
        return "Page Not Found 404"
    else:
        blog_db_info = c.execute(f"SELECT * FROM blogs WHERE blog_id = {blog_id}")
        blog_info = [x for x in blog_db_info][0]
        return render_template('blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], author_name = blog_info[2], content = blog_info[3], timestamp = blog_info[4])


if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()



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
    timestamp INTEGER,
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

#Generates Blog 1 for testing purposes
c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (1, 'Frogs', 'Harry Potter', 'I AM FROG FROG IS AWESOME', 125234532)")

db.commit() #save changes
db.close()  #close database
