from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


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
    time = db.Column(db.DateTime)
    #added time mark for each post

    def __init__(self, title, body, time):
        self.title = title
        self.body = body
        self.time = time

@app.route('/blog', methods=['POST', 'GET'])
def index():
    blog_id = request.args.get("id")
    time_format = "%m-%d-%Y, %H:%M"
    #this allows the user to click on the single blog post link and go to
    #it's individual page with the base boilerplate
    if blog_id:
        blogger = int(blog_id)
        single_blog = Blog.query.filter_by(id=blogger).first()
        return render_template("current-post.html", 
            title=single_blog.title, 
            time=single_blog.time.strftime(time_format),
            body=single_blog.body)
    adventures = Blog.query.all()
    return render_template('home.html', adventures=adventures, formatter=time_format)

@app.route('/newpost', methods=["POST", "GET"])
def new_post():
    #if user submits blog post form
    if request.method == "POST":
        title = request.form["title"]
        blog_post = request.form["blog_post"]
        #check to make sure fields aren't blank, todo = double check escaping on these
        if title and blog_post:
            new_post = Blog(title, blog_post, time=datetime.today())
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



