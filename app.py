#Import Libraries
from __future__ import annotations
from flask import Flask, render_template, request, redirect, url_for, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Text, Boolean, ForeignKey, create_engine
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

# bot.py
import os

#from dotenv import load_dotenv
from flask import jsonify
##load_dotenv()
import csv
import pandas as pd


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('Flask_Key')
Bootstrap5(app)
login_manager = LoginManager()
login_manager.init_app(app)


#
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
db.init_app(app )


#forms for Login, Register, Log, Book, Comment, Pages
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
    comment = CKEditorField("Thoughts?", validators=[DataRequired()])
    name = StringField("Username", validators=[DataRequired()])
    submit = SubmitField("Add Comment")
class PageForm(FlaskForm):
    pages= StringField('Pages Read')
    submit = SubmitField("Add")

#tables for books, users, logs, comments, pages
class Books(db.Model):
    __tablename__ = "bookshelves"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    complete: Mapped[str] = mapped_column(String(250), nullable=False)
    isbn: Mapped[str] = mapped_column(String(250), nullable=False)
    #book to logs
    logs: Mapped[List["Logs"]] = relationship(back_populates="book")
    #user to books
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("readers.id"))
    reader = relationship("User", back_populates="books")
    comments: Mapped[List["Comments"]] = relationship(back_populates="book")

class User(UserMixin, db.Model):
    __tablename__ = "readers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    #user to logs
    logs: Mapped[List["Logs"]] = relationship(back_populates="reader")
    #book to logs
    books: Mapped[List["Books"]] = relationship(back_populates="reader")
    #comments to user
    comments:  Mapped[List["Comments"]] = relationship(back_populates="reader")

class Logs(db.Model):
    __tablename__ = "book_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    log_text: Mapped[str] = mapped_column(Text, nullable=False)
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

    book_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("bookshelves.id"))
    book = relationship("Books", back_populates="comments")

class Pages(db.Model):
    __tablename__ = "Pages_2025"
    Jan: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Feb: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Mar: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Apr: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    May: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Jun: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Jul: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Aug: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Sep: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Oct: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Nov: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    Dec: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    id: Mapped[int] = mapped_column(primary_key=True)

#initialize database
try:
    with app.app_context():
        db.create_all()
except:
    #load csv
    print("Database Error")

#switch function for updating the pages table
#
def switch_add(value_update, value):
    month=int(datetime.now().strftime('%m')) #today's day for comparison to row in table
    if month==1:
        value_update.Jan=value
        return value_update
    elif month==2:
        value_update.Feb=value
        return value_update
    elif month==3:
        value_update.Mar=value
        return value_update
    elif month==4:
        value_update.Apr=value
        return value_update
    elif month==5:
        value_update.May=value
        return value_update
    elif month==6:
        value_update.Jun=value
        return value_update
    elif month==7:
        value_update.Jul=value
        return value_update
    elif month==8:
        value_update.Aug=value
        return value_update    
    elif month==9:
        value_update.Sep=value
        return value_update
    elif month==10:
        value_update.Oct=value
        return value_update
    elif month==11:
        value_update.Nov=value
        return value_update
    elif month==12:
        value_update.Dec=value 
        return value_update

#home page displays my books in database
@app.route('/', methods=["GET"])
def home():
    print(data)
    print(port)
    with app.app_context():
        try:
            book_list=[]
            result = db.session.execute(db.select(Books).order_by(Books.title).where(Books.user_id==2))
            for row in result.scalars():
                books=[row.id, row.title, row.author, row.rating, row.complete, row.user_id]
                book_list.append(books)
            all_books = pd.DataFrame(book_list, columns=['id', 'title', 'author', 'rating', 'complete', 'user_id'])
            message=''
            result.close()
           
        except:
            message='Database Error: Cannot login at this time. Please try again later.'
            all_books=pd.read_csv('books.csv')
            all_books=all_books[all_books['user_id']==2]
            print('Database Error')

        
        
        return render_template("index.html", shelf=all_books,message=message)

# show list of books for specific user
@app.route('/<int:user>', methods=["GET"])
@login_required
def show_books(user):
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.title).where(Books.user_id == user))
        book_list = []
        for row in result.scalars():
                books=[row.id, row.title, row.author, row.rating, row.complete, row.user_id]
                book_list.append(books)
        all_books = pd.DataFrame(book_list, columns=['id', 'title', 'author', 'rating', 'complete', 'user_id'])
        result.close()
        return render_template("books.html", shelf=all_books)

#page to add a book to database
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

#page to edit book in database
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
        result = db.session.execute(db.select(Books).where(Books.id==old))
        book = result.scalar()
        return render_template("edit.html", id=old, book=book)

#page to delete book from database
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

#page to login
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

#page to logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#page that allows users to register
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

#page to create a log for a book in the database
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
            date_created=datetime.now().strftime('%b. %d, %Y  %I:%M:%S%p'),
            id=db.session.query(Logs.id).count() + 1,
            user_id=current_user.id
        )
        db.session.add(new_log)
        db.session.commit()
        return redirect(url_for('show_log', book_id=book_id))
    return render_template('log.html', form=form, book_id=book_id, book_name=book)

#page to show the logs for a specific book
@app.route('/show_log/<int:book_id>', methods=["POST", "GET"])
def show_log(book_id):
    result = db.session.execute(db.select(Logs).where(Logs.book_id == book_id))
    logs = result.scalars().all()
    result1 = db.session.execute(db.select(Comments).where(Comments.book_id == book_id))
    comments = result1.scalars().all()
    result2 = db.session.execute(db.select(Books).where(Books.id == book_id))
    book = result2.scalar()
    return render_template('show_log.html', all_logs=logs, book_id=book_id, comments=comments, book=book)

#page to see and add comments to a book
@app.route('/comment/<int:book_id>', methods=["POST", "GET"])
def comment(book_id):
    form = CommentForm()
    result = db.session.execute(db.select(Books).where(Books.id == book_id))
    book = result.scalar()
    name="Guest"
    form.name.data=name
    if current_user.is_authenticated:
            form.name.data=current_user.name
    if request.method == "POST":
        with app.app_context():
            comment1 = Comments(
                comment_text = form.comment.data,
                date_created= datetime.now().strftime('%b. %d, %Y  %I:%M %p'),
                username= form.name.data,
                book_id= book_id,
                id=db.session.query(Comments.id).count() + 1
            )
            db.session.add(comment1)
            db.session.commit()
            return redirect(url_for('home'))
        
    return render_template("add_comment.html", form=form, book=book)

#graph
@app.route('/graph', methods=["POST", "GET"])
def graph():
    data=False
    day=int(datetime.now().strftime('%d'))
    month=(datetime.now().strftime('%b'))
    month_num=(datetime.now().strftime('%m'))
    print(type(datetime.now().strftime('%d')))
    form=PageForm()
    result = db.session.execute(db.select(Pages).order_by(Pages.id))
    pages = result.scalars()
    arr=[]
    
    months=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    
    for i in range(1, 13):
        result1 = db.session.execute(db.select(Pages).order_by(Pages.id))
        for x in result1.scalars():
            if i==1 and x.Jan!=-1:
                arr.append(x.Jan)
            elif i==2 and x.Feb!=-1:
                arr.append(x.Feb)
            elif i==3 and x.Mar!=-1:
                arr.append(x.Mar)
            elif i==4 and x.Apr!=-1:
                arr.append(x.Apr)
            elif i==5 and x.May!=-1:
                arr.append(x.May)
            elif i==6 and x.Jun!=-1:
                arr.append(x.Jun)
            elif i==7 and x.Jul!=-1:
                arr.append(x.Jul)
            elif i==8 and x.Aug!=-1:
                arr.append(x.Aug)
            elif i==9 and x.Sep!=-1:
                arr.append(x.Sep)
            elif i==10 and x.Oct!=-1:
                arr.append(x.Oct)
            elif i==11 and x.Nov!=-1:
                arr.append(x.Nov)
            elif i==12 and x.Dec!=-1:
                arr.append(x.Dec)

    if request.method=="POST":
        new_value = form.pages.data
        old_value = day
        print(day)
        with app.app_context():
            value_update = db.session.execute(db.select(Pages).where(Pages.id == day)).scalar()
            switch_add(value_update, new_value)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("graph.html", months=months, form=form, day=day, month=month, pages=pages, arr=arr)
port = os.getenv('port')
if __name__ == "__main__":
    app.run(debug=True, port=port)
    

