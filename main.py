from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash
#imported the necessary functions for password hashing


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:black_truffles@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "mysecretkey"


class User(db.Model):
#added hashing/salting technique to db here
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    pw_hash = db.Column(db.String(200))
    blogs = db.relationship("Blog", backref = "author")

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    time = db.Column(db.DateTime)
    #added author_id for Blogz / same as the owner_id from instructions
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, author, time):
        self.title = title
        self.body = body
        self.author = author
        self.time = time

#this requires the user to login or be logged in
@app.before_request
def require_login():
    allowed_routes = ["login", "signup", "blog_list", "index"]

    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/blog")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session["username"] = username
            return redirect('/newpost')
        elif user and not check_pw_hash(password, user.pw_hash):
            flash("Incorrect password, please try again.", "error")
        else:
            flash("Username does not exist. Please try again or click the 'Create Adventures' button to Sign Up.", "error")

    return render_template("login.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]

        existing_user = User.query.filter_by(username=username).first()
        if not username or not password or not verify:
            flash("All inputs are required.", "error")

        elif existing_user:
            flash("That username is already taken, please pick another.", "error")

        elif password != verify:
            flash("The passwords do not match.", "error")

        elif len(password) < 6 or len(password) > 20: 
            flash("Invalid Password: Must be between 6 and 20 characters.", "error")

        elif len(username) < 6 or len(username) > 20:
            flash("Invalid Username: Must be between 6 and 20 characters.", "error")

        elif not existing_user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/newpost")
    return render_template("register.html")

@app.route("/", methods=["POST", "GET"])
def index():
    user_list = User.query.all()       #todo - paginate attempt
    
    return render_template("index.html", users = user_list)

@app.route('/blog', methods=['POST', 'GET'])
def blog_list():
    blog_id = request.args.get("id")
    time_format = "%m-%d-%Y, %H:%M"
    user_info = request.args.get("user")
    #this allows the user to click on the single blog post link and go to
    #it's individual page with the base boilerplate
    if user_info:
        user = User.query.filter_by(username=user_info).first()
        user_blogs = Blog.query.filter_by(author_id=user.id).all()
        return render_template("user-posts.html",
            user = user,
            user_blogs=user_blogs,
            formatter= time_format)
    if blog_id:
        blogger = int(blog_id)
        single_blog = Blog.query.filter_by(id=blogger).first()
        return render_template("current-post.html", 
            title=single_blog.title, 
            time=single_blog.time.strftime(time_format),
            body=single_blog.body,
            author=single_blog.author.username)
    adventures = Blog.query.all()                       #todo - paginate attempt
    users = User.query.all() 
    return render_template('home.html', adventures=adventures, formatter=time_format, users= users)

@app.route('/newpost', methods=["POST", "GET"])
def new_post():
    #if user submits blog post form
    if request.method == "POST":
        title = request.form["title"]
        blog_post = request.form["blog_post"]
        #todo, double check that author is properly added here
        author = User.query.filter_by(username=session["username"]).first()

        if title and blog_post:
            new_post = Blog(title, blog_post, author, time=datetime.today())
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



