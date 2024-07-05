
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Text, Boolean
#from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_wtf import FlaskForm

from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from functools import wraps
from wtforms import StringField, SubmitField, EmailField, PasswordField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField

import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('Flask_Key')
Bootstrap5(app)
login_manager=LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)
def admin_only(f):
    @wraps(f)
    def admin(*args, **kwargs):
        print("a")
        if current_user.is_authenticated==False or current_user.id!=1:
            return abort(403)
        return f(*args, **kwargs)
    return admin
class Base(DeclarativeBase):
  pass
db=SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", "sqlite:///new_books_collection.db")
db.init_app(app)

class LoginForm(FlaskForm):

    name = StringField("Username", validators=[DataRequired()])
    password=PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

class RegisterForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    password=PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")
class LogForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    log = CKEditorField("Book Log", validators=[DataRequired()])
    submit = SubmitField("Log")
class Books(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] =mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    complete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    #log:Mapped[str] = mapped_column(Text, nullable=False)
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
with app.app_context():
    db.create_all()
all_books = []


@app.route('/' , methods=["POST", "GET"])
def home():
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.title))
        all_books = list(result.scalars())
        return render_template("index.html", shelf=all_books)


@app.route("/add", methods=["POST", "GET"])
@admin_only
def add():
    if request.method== "POST":
        # book={'title': request.form['name'], 'author': request.form['author'], 'rating':request.form['rating']}
        # all_books.append(book)
        with app.app_context():
            book1=Books(
                title=request.form['name'],
                author=request.form['author'],
                rating=request.form['rating'])
            db.session.add(book1)
            db.session.commit()
            result = db.session.execute(db.select(Books).order_by(Books.title))
            all_books=result.scalars()
            print(all_books)
            return redirect(url_for('home'))

    return render_template("add.html")
@app.route('/edit', methods=["POST", "GET"])
@admin_only
def edit():


    if request.method == "POST":

        new_book = request.form['new_name']
        old_book = request.args.get('id')
        if request.form['choice']=="author_option":
            with app.app_context():

                book_update = db.session.execute(db.select(Books).where(Books.id == old_book)).scalar()
                book_update.author = new_book

                db.session.commit()
                return redirect(url_for('home'))
        if request.form['choice']=="title_option":
            with app.app_context():

                book_update = db.session.execute(db.select(Books).where(Books.id==old_book)).scalar()
                book_update.title=new_book

                db.session.commit()
                return redirect(url_for('home'))
        if request.form['choice']=="rating_option":
            with app.app_context():

                book_update = db.session.execute(db.select(Books).where(Books.id==old_book)).scalar()
                book_update.rating=new_book

                db.session.commit()
                return redirect(url_for('home'))
    old = request.args.get('id')
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.title))
        all_books = result.scalars()
        return render_template("edit.html", id=old, shelf=all_books)
@app.route('/delete')
@admin_only
def delete():
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.title))
        all_books = result.scalars()
    with app.app_context():
        book_id=request.args.get('id')
        book_del = db.get_or_404(Books, book_id)
        db.session.delete(book_del)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('home'))

@app.route('/login', methods=["POST","GET"])
def login():
    l_form=LoginForm()
    if l_form.validate_on_submit:
        name = request.form.get('name')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).where(User.name == name)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=l_form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
@app.route('/register', methods=["POST", "GET"])
def register():
    r_form=RegisterForm()
    if r_form.validate_on_submit():
        name=request.form.get('name')
        double=db.session.execute(db.select(User).where(User.name==name)).scalar()
        if double:
            return redirect(url_for('login'))
        else:
            secure = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
            new_user = User(
                password=secure,
                name=request.form.get('name'),
            )


            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("register.html", form=r_form)

if __name__ == "__main__":
    app.run(debug=True)

