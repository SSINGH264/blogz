from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blog:blog@localhost:8889/blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Blog %r>' % self.title

def get_all_blogs():
    return Blog.query.all()

@app.route("/blog")
def index():
    post_id = request.args.get('id')
    if post_id:
        post = Blog.query.get(post_id)
        return render_template('post.html', title=post.title, body=post.body)
    else:
        return render_template('blog.html', blogs=get_all_blogs())

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

        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id='+ str(new_post.id))
    else:
        return render_template('newpost.html')

if __name__ == "__main__":
    app.run()
