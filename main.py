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
    blog_id = request.args.get("id")
    #this allows the user to click on the single blog post link and go to
    #it's individual page with the base boilerplate
    if blog_id:
        blogger = int(blog_id)
        single_blog = Blog.query.filter_by(id=blogger).first()
        single_blog_page = "<h3>" + single_blog.title + " | " + str(single_blog.time) + "</h3><p>" + single_blog.body + "</p><hr />"
        return render_template("base.html") + single_blog_page
    adventures = Blog.query.all()
    return render_template('home.html', adventures=adventures, id=Blog.id)

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
            new_post_id = new_post.id
            return redirect("/blog?id={0}".format(new_post_id))
        else:
            #flash error if user does not fill out both form fields
            flash("Please fill out both the Title and Post before submitting", "error")
        
    return render_template("new-post.html")


if __name__ == '__main__':
    app.run()

"""                 
db.drop_all()
db.create_all()
"""

