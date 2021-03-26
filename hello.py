from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from time import time
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_migrate import Migrate
import os
import re
import bcrypt

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__ , static_folder = 'static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)

class users(UserMixin , db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(255), unique=True)
    hash = db.Column(db.String(50))

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    created = db.Column(db.DateTime, default=datetime.now())
    subtitle = db.Column(db.String(140))
    authore = db.Column(db.String(140))
    message = db.Column(db.Text)

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.generate_slug()
    def generate_slug(self):
        if self.title:
            self.slug= slugify(self.title)
        else:
            self.slug = str(int(time()))
    def __repr__(self):
        return f'<Post id:{self.id}, title:{self.title}>'

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home/<p>')
@login_required
def home(p):
    name = p
    posts = Post.query.filter(Post.authore.contains(p))
    page =request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page=1

    pages = posts.paginate(page = page, per_page=3)
    return render_template('home.html',posts=posts, pages= pages, p = name)

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.query.filter_by(email = email).first()
        if user:
            if bcrypt.checkpw(password.encode('utf-8') , user.hash ):
                login_user(user)
                return redirect(url_for('home',p = user.name))
    return render_template('login.html')

@app.route('/blog1/<p>')
@login_required
def blog1(p):
    q = request.args.get('q')

    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.message.contains(q))
    else:
        posts = Post.query.order_by(Post.id.desc())
    
    page =request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page=1

    pages = posts.paginate(page = page, per_page=3)
    
    return render_template('blog1.html',posts=posts, pages= pages , p = p)

@app.route('/blog')
def blog():
    q = request.args.get('q')

    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.message.contains(q))
    else:
        posts = Post.query.order_by(Post.id.desc())
    
    page =request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page=1

    pages = posts.paginate(page = page, per_page=3)
    
    return render_template('blog.html',posts=posts, pages= pages)

@app.route('/<slug>')
def view1(slug):
    post = Post.query.filter(Post.slug == slug).first()
    return render_template('view1.html',post=post)

@app.route('/<p>/<slug>')
@login_required
def view(p,slug):
    post = Post.query.filter(Post.slug == slug).first()
    return render_template('view.html',post=post,p=p)

@app.route('/write/<p>',methods=["POST","GET"])
@login_required
def write(p):
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        authore = request.form['authore']
        message = request.form['message']
        post = Post(title = title,subtitle = subtitle , authore = authore,message = message)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('view',p=p,slug=post.slug))
    return render_template('write.html',p=p)

@app.route('/sign_up',methods=["POST","GET"])
def sign_up():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = users(name = name, email = email, hash = hashed)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('sign_up.html')

@app.route('/contact_us')
def contact():
    return render_template('contact_us.html')

@app.route('/contact_us/<p>')
@login_required
def contact1(p):
    return render_template('contact_us1.html',p=p)

@app.route('/about/<p>')
@login_required
def about1(p):
    return render_template('about1.html',p=p)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)