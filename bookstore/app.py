from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3

# instantiate the app
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('bookstore.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return categories

# set up routes
@app.route('/')
def home():
    categories = get_categories()
    return render_template('index.html', categories=categories)

@app.route('/category')
def category():
    category_id = request.args.get('category', type=int)

    conn = get_db_connection()

    books = conn.execute(
        'SELECT * FROM books WHERE categoryId = ?', 
        (category_id,)
    ).fetchall()
    
    conn.close()

    categories = get_categories()

    return render_template(
        'category.html',
        categories=categories,      
        books=books,               
        selectedCategory=category_id
    )

@app.route('/search', methods=['GET', 'POST'])
def search():
    term = request.form.get("search") or request.args.get("search")
    
    if not term:
        term = ""
        
    term = term.strip()

    conn = get_db_connection()

    sql = "SELECT * FROM books WHERE lower(title) LIKE lower(?)"
    books = conn.execute(sql, (f"%{term}%",)).fetchall()
    
    conn.close()

    categories = get_categories()

    return render_template(
        "search.html",
        categories=categories,
        books=books,
        term=term
    )

@app.errorhandler(Exception)
def handle_error(e):
    """
    Output any errors - good for debugging.
    """
    return render_template('error.html', error=e) # render the edit template


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = get_db_connection()
    sql = """
        SELECT books.*, categories.name AS categoryName
        FROM books
        JOIN categories ON books.categoryId = categories.id
        WHERE books.id = ?
    """
    book = conn.execute(sql, (book_id,)).fetchone()
    
    conn.close()
    categories = get_categories()

    if book is None:
        return render_template('error.html', error="Book not found")

    return render_template('book_detail.html', book=book, categories=categories)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)

