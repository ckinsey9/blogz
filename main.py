from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:truffles@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "mysecretkey"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    #added time mark for each post

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def index():
    adventures = Blog.query.all()
    return render_template('home.html', adventures=adventures)

@app.route('/newpost', methods=["POST", "GET"])
def new_post():
    #if user submits blog post form
    if request.method == "POST":
        title = request.form["title"]
        blog_post = request.form["blog_post"]
        #check to make sure fields aren't blank, todo = double check escaping on these
        if title and blog_post:
            new_post = Blog(title, blog_post)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/blog")
        else:
            #flash error if user does not fill out both form fields
            flash("Please fill out both the Title and Post before submitting", "error")
        
    return render_template("new-post.html")


if __name__ == '__main__':
    app.run()

"""(for home.html page) 
<form method="POST" action="/blog?{{0}}" style="display:inline-block;">.format(adventure.id)
                    <input type="hidden" name="adventure-id" value="{{adventure.id}}" />
                    <input type="submit" value="Go To!" />"""