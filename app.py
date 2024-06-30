from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
class Base(DeclarativeBase):
  pass
db=SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new_books_collection.db"
db.init_app(app)
class Books(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] =mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
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
def add():
    if request.method== "POST":
        # book={'title': request.form['name'], 'author': request.form['author'], 'rating':request.form['rating']}
        # all_books.append(book)
        with app.app_context():
            book1=Books(title=request.form['name'], author=request.form['author'], rating=request.form['rating'])
            db.session.add(book1)
            db.session.commit()
            result = db.session.execute(db.select(Books).order_by(Books.title))
            all_books=result.scalars()
            print(all_books)
            return redirect(url_for('home'))

    return render_template("add.html")
@app.route('/edit', methods=["POST", "GET"])
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


if __name__ == "__main__":
    app.run(debug=True)

