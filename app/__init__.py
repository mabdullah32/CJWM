from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

@app.route("/", methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route("/profile", methods=['GET','POST'])
def profile():
    return render_template('profile.html')

@app.route("/blogs/<blog_id>.html", methods=['GET','POST'])
def blogs(blog_id):
    if blog_id == None:
        return "Page Not Found 404"
    else:
        blog_db_info = c.execute(f"SELECT * FROM blogs WHERE blog_id = {blog_id}")
        blog_info = [x for x in blog_db_info][0]
        return render_template('blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], author_name = blog_info[2], content = blog_info[3], timestamp = blog_info[4])

@app.route("/edit_blogs/<int:blog_id>", methods=['GET','POST'])
def edit_blogs(blog_id):
    if request.method == 'POST':
        blog_name = request.form.get('blog_name')
        content = request.form.get('content')
        c.execute(f"UPDATE blogs SET blog_name = ?, content = ? WHERE blog_id = ?", (blog_name, content, blog_id))
        db.commit()
        return redirect(f"/blogs/{blog_id}.html")
    else:
        blog_db_info = c.execute(f"SELECT * FROM blogs WHERE blog_id = {blog_id}")
        blog_info = [x for x in blog_db_info][0]
        return render_template('edit_blogs.html', blog_id = blog_info[0], blog_name = blog_info[1], content = blog_info[3])

if __name__ == "__main__":
    app.debug = True
    app.run()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    creation_date DATE,
    last_login DATE
)""")

c.execute("""
CREATE TABLE IF NOT EXISTS blogs (
    blog_id INTEGER PRIMARY KEY,
    blog_name STRING,
    author_name STRING,
    content STRING,
    timestamp INTEGER,
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

c.execute("INSERT OR REPLACE INTO blogs (blog_id, blog_name, author_name, content, timestamp) VALUES (1, 'Frogs', 'Harry Potter', 'I AM FROG FROG IS AWESOME', 125234532)")

db.commit()
db.close()
