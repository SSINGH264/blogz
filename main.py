from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:paneer@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'Phu42ll&2yozk'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.title

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_all_blogs():
    return Blog.query.all()

def get_all_users():
    return User.query.all()

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/blog')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    return render_template('index.html', users=get_all_users())

@app.route("/blog")
def blog():
    post_id = request.args.get('id')
    username = request.args.get('user')
    if post_id:
        post = Blog.query.get(post_id)
        user = User.query.filter_by(username=session['username']).first()
        return render_template('post.html', title=post.title, body=post.body, username=user.username)
    elif username:
        user = User.query.filter_by(username=username).first()
        return render_template('blog.html', user=user)
    else:
        users = get_all_users()
        return render_template('blog.html', users=users)

@app.route("/newpost", methods=['POST', 'GET'])
def newPost():
    if request.method == 'POST':
        title = request.form['title']
        title_error = ''
        body = request.form['body']
        body_error = ''
        if not title:
            title_error = "Title is required"
        if not body:
            body_error = "Body is required"

        if title_error or body_error:
            return render_template('newpost.html', title=title, body=body, title_error=title_error, body_error=body_error)

        user = User.query.filter_by(username=session['username']).first()

        new_post = Blog(title, body, user)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id='+ str(new_post.id))
    else:
        return render_template('newpost.html')

if __name__ == "__main__":
    app.run()
