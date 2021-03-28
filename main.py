from flask import Flask, render_template, url_for, redirect, request, flash
from forms import EditForm, SubjectForm, LoginForm
import db_schema
from db_schema import Subject, Article, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from functools import wraps

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, current_user, login_user, logout_user
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# DB CONNECTION
engine = create_engine('sqlite:///data.db')
db_schema.BaseORM.metadata.create_all(engine)
db_session = scoped_session(sessionmaker(bind=engine))

# USER MANAGEMENT
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


# GENERAL PROGRAM
def logged_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


@app.route("/")
@app.route("/<s_id>")
def home(s_id=0):
    subjects = db_session.query(Subject).all()

    if type(s_id) == str and s_id.isdigit() and int(s_id) != 0:
        current_subject = db_session.query(Subject).get(s_id)
        current_subject_name = current_subject.name
        articles = db_session.query(Article).filter(Article.subject_id == s_id)
    else:
        current_subject_name = 'All fields'
        articles = db_session.query(Article).all()

    featured_articles = db_session.query(Article).filter(Article.is_featured == True)

    nav_class = {
        'home': 'current-section-color',
        'about': '',
        'contact': '',
        'admin': ''
    }
    return render_template("index.html", articles=articles, featured_articles=featured_articles, subjects=subjects, current_subject_name=current_subject_name, nav_class=nav_class)


@app.route("/admin")
@logged_only
def admin():
    nav_class = {
        'home': '',
        'about': '',
        'contact': '',
        'admin': 'current-section-color'
    }
    articles = db_session.query(Article).all()
    return render_template("admin.html", articles=articles, nav_class=nav_class)


@app.route("/edit", methods=['GET', 'POST'])
@app.route("/edit/<a_id>", methods=['GET', 'POST'])
@logged_only
def edit(a_id=0):
    edit_form = EditForm()

    if a_id != 0 and request.method == 'GET':
        art = db_session.query(Article).get(a_id)
        edit_form.title.data = art.title
        edit_form.preview.data = art.preview
        edit_form.is_featured.data = art.is_featured
        edit_form.subject.data = str(art.subject_id)
        edit_form.contents.data = art.contents

    if edit_form.validate_on_submit():
        if int(a_id) == 0:
            art = Article()
        else:
            art = db_session.query(Article).get(a_id)

        art.title = edit_form.title.data
        art.preview = edit_form.preview.data
        art.is_featured = edit_form.is_featured.data
        art.subject_id = edit_form.subject.data
        art.contents = edit_form.contents.data

        db_session.add(art)
        db_session.commit()

        return redirect(url_for('admin'))

    edit_form.subject.choices = [(s.id, s.name) for s in db_session.query(Subject).all()]
    nav_class = {
        'home': '',
        'about': '',
        'contact': '',
        'admin': 'current-section-color'
    }
    return render_template("edit.html", edit_form=edit_form, a_id=a_id, nav_class=nav_class)


@app.route("/add_subject", methods=['GET', 'POST'])
@logged_only
def add_subject():
    subject_form = SubjectForm()
    nav_class = {
        'home': '',
        'about': '',
        'contact': '',
        'admin': 'current-section-color'
    }
    if subject_form.validate_on_submit():
        name = subject_form.name.data
        subject = Subject()
        subject.name = name
        db_session.add(subject)
        db_session.commit()
        return redirect(url_for('home'))
    return render_template("add_subject.html", subject_form=subject_form, nav_class=nav_class)


@app.route("/article/<a_id>")
def article(a_id):
    art = db_session.query(Article).get(a_id)
    nav_class = {
        'home': '',
        'about': '',
        'contact': '',
        'admin': ''
    }
    return render_template("article.html", article=art, nav_class=nav_class)


@app.route("/about")
def about():
    nav_class = {
        'home': '',
        'about': 'current-section-color',
        'contact': '',
        'admin': ''
    }
    return render_template("about.html", nav_class=nav_class)


@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if len(db_session.query(User).all()) == 0:
            new_user = User()
            new_user.username = login_form.login.data
            new_user.password = generate_password_hash(login_form.password.data, method='pbkdf2:sha256', salt_length=8)
            db_session.add(new_user)
            db_session.commit()
            login_user(new_user)
            return redirect('admin')
        else:
            user = db_session.query(User).filter(User.username == login_form.login.data).first()
            if user is not None:
                if check_password_hash(user.password, login_form.password.data):
                    login_user(user)
                    return redirect('admin')
                else:
                    flash('Wrong password')
            else:
                flash('User not found')
    nav_class = {
        'home': '',
        'about': '',
        'contact': '',
        'admin': 'current-section-color'
    }
    return render_template("login.html", login_form=login_form, nav_class=nav_class)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('home')

if __name__ == '__main__':
    app.run(debug=True)