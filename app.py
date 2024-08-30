#Import Libraries
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Text, Boolean, ForeignKey
from typing import List
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from functools import wraps
from wtforms import StringField, SubmitField, EmailField, PasswordField, DateTimeField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from datetime import datetime
import os
import psycopg2

import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'#os.environ.get('Flask_Key')
Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(f):
    @wraps(f)
    def admin(*args, **kwargs):
        print("a")
        if not current_user.is_authenticated or current_user.name != 'admin':
            return abort(403)
        return f(*args, **kwargs)
    return admin


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)

data = os.getenv('Database_URL')
app.config["SQLALCHEMY_DATABASE_URI"] = data

db.init_app(app)


class LoginForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    password=PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegisterForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LogForm(FlaskForm):
    log = CKEditorField("Book Log", validators=[DataRequired()])
    submit = SubmitField("Log")


class BookForm(FlaskForm):
    name = StringField("Book Name", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    rating = StringField("Rating", validators=[DataRequired()])
    status = StringField("Finished?", validators=[DataRequired()])
    submit = SubmitField("Add Book")
class CommentForm(FlaskForm):
    name = StringField("Book Name", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    comment = CKEditorField("Thoughts?", validators=[DataRequired()])
    submit = SubmitField("Add Comment")

class Books(db.Model):
    __tablename__ = "bookshelves"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    complete: Mapped[str] = mapped_column(String(250), nullable=False)
    #book to logs
    logs: Mapped[List["Logs"]] = relationship(back_populates="book")
    #user to books
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("readers.id"))
    #user_name: Mapped[str] = mapped_column(String, db.ForeignKey("readers.name"))

    reader = relationship("User", back_populates="books")
    #readers: Mapped[List["User"]] = relationship(back_populates="readers")
    #user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("readers.id"))

class User(UserMixin, db.Model):
    __tablename__ = "readers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    #user to logs
    logs: Mapped[List["Logs"]] = relationship(back_populates="reader")
    #book to logs
    books: Mapped[List["Books"]] = relationship(back_populates="reader")

    comments:  Mapped[List["Comments"]] = relationship(back_populates="reader")



class Logs(db.Model):
    __tablename__ = "book_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    log: Mapped[str] = mapped_column(Text, nullable=False)
    date_created: Mapped[str] = mapped_column(String(250), nullable=False)
    #book to logs
    book_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("bookshelves.id"))
    book = relationship("Books", back_populates="logs")
    # user to logs
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("readers.id"))
    reader = relationship("User", back_populates="logs")

class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    date_created: Mapped[int] = mapped_column(String(250), nullable=False)
    username: Mapped[int] = mapped_column(String, db.ForeignKey("readers.name"))
    reader = relationship("User", back_populates="comments")

#     title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
#     author: Mapped[str] = mapped_column(String(250), nullable=False)
#     comment: Mapped[str] = mapped_column(String(250), nullable=False)
#     books: Mapped[List["Logs"]] = relationship(back_populates="book_log")
#     reader: Mapped[List["User"]] = relationship(back_populates="readers")


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET"])
def home():
    with app.app_context():
        #cursor= conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
        result = db.session.execute(db.select(Books).order_by(Books.title).where(Books.user_id==2))


        all_books = result.scalars()
        return render_template("index.html", shelf=all_books)


@app.route('/<int:user>', methods=["GET"])
def show_books(user):
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.title).where(Books.user_id == user))
        all_books = result.scalars()
        print(result)

        return render_template("books.html", shelf=all_books)


@app.route("/add", methods=["POST", "GET"])
@login_required
def add():
    form=BookForm()
    if request.method == "POST":
        with app.app_context():
            book1=Books(
                title=request.form['name'],
                author=request.form['author'],
                rating=request.form['rating'],
                complete=request.form['status'],
                id=db.session.query(Books.id).count() + 1,
                user_id=current_user.id
            )
            db.session.add(book1)
            db.session.commit()
            return redirect(url_for('home'))

    return render_template("add.html", form=form)


@app.route('/edit', methods=["POST", "GET"])
@login_required
def edit():
    if request.method == "POST":
        new_book = request.form['new_name']
        old_book = request.args.get('id')
        if request.form['choice'] == "author_option":
            with app.app_context():
                book_update = db.session.execute(db.select(Books).where(Books.id == old_book)).scalar()
                book_update.author = new_book
                db.session.commit()
                return redirect(url_for('home'))
        if request.form['choice'] == "title_option":
            with app.app_context():

                book_update = db.session.execute(db.select(Books).where(Books.id == old_book)).scalar()
                book_update.title = new_book

                db.session.commit()
                return redirect(url_for('home'))
        if request.form['choice'] == "rating_option":
            with app.app_context():

                book_update = db.session.execute(db.select(Books).where(Books.id == old_book)).scalar()
                book_update.rating = new_book

                db.session.commit()
                return redirect(url_for('home'))
    old = request.args.get('id')
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.title))
        all_books = result.scalars()
        return render_template("edit.html", id=old, shelf=all_books)


@app.route('/delete')
@login_required
def delete():
    with app.app_context():
        book_id = request.args.get('id')
        book_del = db.get_or_404(Books, book_id)
        db.session.delete(book_del)
        db.session.commit()
        return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/login', methods=["POST", "GET"])
def login():
    l_form=LoginForm()
    if l_form.validate_on_submit:
        name = request.form.get('name')
        password = request.form.get('password')
        user = db.session.execute(db.select(User).where(User.name == name)).scalar()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user =='admin':
                return redirect(url_for('home'))
            else:
                print(user.id)

                return redirect(url_for('show_books', user=user.id))

    return render_template("login.html", form=l_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=["POST", "GET"])
def register():
    r_form = RegisterForm()
    if r_form.validate_on_submit():
        name = request.form.get('name')
        double = db.session.execute(db.select(User).where(User.name == name)).scalar()
        if double:
            return redirect(url_for('login'))
        else:
            secure = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
            new_user = User(
                password=secure,
                name=request.form.get('name'),
                id=db.session.query(User.id).count()+1
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("register.html", form=r_form)


@app.route('/log/<int:book_id>', methods=["POST", "GET"])
@login_required
def post_log(book_id):
    form = LogForm()
    result = db.session.execute(db.select(Books).where(Books.id == book_id))
    book = result.scalar()
    if form.validate_on_submit():
        new_log = Logs(
            log=form.log.data,
            book=book,
            date=datetime.now().strftime('%b. %d, %Y  %I:%M:%S%p'),
            id=db.session.query(Logs.id).count() + 1,
            user_id=current_user.id
        )
        db.session.add(new_log)
        db.session.commit()
        return redirect(url_for('show_log', book_id=book_id))
    return render_template('log.html', form=form, book_id=book_id)


@app.route('/show_log/<int:book_id>', methods=["POST", "GET"])
def show_log(book_id):
    result = db.session.execute(db.select(Logs).where(Logs.book_id == book_id))
    logs = result.scalars().all()
    return render_template('show_log.html', all_logs=logs, book_id=book_id)


@app.route('/comment/<int:book_id>', methods=["POST", "GET"])
@admin_only
def comment(book_id):
    form = CommentForm()
    if request.method == "POST":
        with app.app_context():
            book1 = Books(
                title=request.form['name'],
                author=request.form['author'],
                rating=request.form['rating'],
                complete=request.form['status'],
                id=db.session.query(Books.id).count() + 1,
                user_id=current_user.id
            )
            db.session.add(book1)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("add_comment.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)

