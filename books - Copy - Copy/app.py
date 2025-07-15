from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_session import Session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/sapatshree_books')
Session(app)
mongo = PyMongo(app)

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# Sample book data
books = [
    {
        "id": 1,
        "title": "An Immense World",
        "author": "Ed Yong",
        "price": 600.84,
        "rating": 4,
        "rating_count": 37,
        "image": "https://covers.openlibrary.org/b/id/13144032-M.jpg",
        "description": "A fascinating exploration of animal senses and how they perceive the world, written by Pulitzer Prize-winning journalist Ed Yong.",
        "category": "bestseller",
        "subcategory": "Nonfiction",
        "language": "English"
    },
    {
        "id": 2,
        "title": "Complementary and Integrative...",
        "author": "Unknown",
        "price": 4190.88,
        "rating": 4,
        "rating_count": 0,
        "image": "https://covers.openlibrary.org/b/id/7757130-M.jpg",
        "description": "A comprehensive guide to psychiatric practices and integrative therapies.",
        "category": "bestseller",
        "subcategory": "Nonfiction",
        "language": "English"
    },
    {
        "id": 3,
        "title": "Atomic Habits",
        "author": "James Clear",
        "price": 601.08,
        "rating": 4,
        "rating_count": 978,
        "image": "https://covers.openlibrary.org/b/id/8231996-M.jpg",
        "description": "A groundbreaking book on building good habits and breaking bad ones, offering practical strategies for lasting change.",
        "category": "bestseller",
        "subcategory": "Business & Finance",
        "language": "English"
    },
    {
        "id": 4,
        "title": "Verity",
        "author": "Colleen Hoover",
        "price": 315.99,
        "rating": 5,
        "rating_count": 1404,
        "image": "https://covers.openlibrary.org/b/id/10537021-M.jpg",
        "description": "A thrilling novel about a struggling writer who takes on a mysterious job, uncovering dark secrets.",
        "category": "bestseller",
        "subcategory": "Mystery & Suspense",
        "language": "English"
    },
    {
        "id": 5,
        "title": "The Midnight Library",
        "author": "Matt Haig",
        "price": 680.38,
        "rating": 4,
        "rating_count": 2235,
        "image": "https://covers.openlibrary.org/b/id/2407275-M.jpg",
        "description": "A heartwarming story about a woman who gets to explore alternate lives, exploring themes of choice and regret.",
        "category": "bestseller",
        "subcategory": "Fiction & Literature",
        "language": "English"
    },
    {
        "id": 6,
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "price": 550.00,
        "rating": 4,
        "rating_count": 890,
        "image": "https://covers.openlibrary.org/b/id/5546156-M.jpg",
        "description": "A thought-provoking exploration of the history of humankind, from the Stone Age to the modern era.",
        "category": "bestseller",
        "subcategory": "Nonfiction",
        "language": "English"
    },
    {
        "id": 7,
        "title": "1984",
        "author": "George Orwell",
        "price": 299.99,
        "rating": 5,
        "rating_count": 1650,
        "image": "https://covers.openlibrary.org/b/id/6601252-M.jpg",
        "description": "A classic dystopian novel about surveillance, control, and the loss of personal freedom.",
        "category": "bestseller",
        "subcategory": "Fiction & Literature",
        "language": "English"
    },
    {
        "id": 8,
        "title": "Dune",
        "author": "Frank Herbert",
        "price": 499.99,
        "rating": 4,
        "rating_count": 1200,
        "image": "https://covers.openlibrary.org/b/id/9098763-M.jpg",
        "description": "A science fiction epic about politics, religion, and survival on a desert planet.",
        "category": "bestseller",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    },
    {
        "id": 9,
        "title": "Godan",
        "author": "Premchand",
        "price": 250.00,
        "rating": 4,
        "rating_count": 450,
        "image": "https://covers.openlibrary.org/b/id/4321002-M.jpg",
        "description": "A classic Hindi novel depicting the struggles of rural life and social issues in India.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 10,
        "title": "Gaban",
        "author": "Premchand",
        "price": 220.00,
        "rating": 4,
        "rating_count": 320,
        "image": "https://covers.openlibrary.org/b/id/9932101-M.jpg",
        "description": "A story of human greed and its consequences, set in colonial India.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 11,
        "title": "Madhushala",
        "author": "Harivansh Rai Bachchan",
        "price": 180.00,
        "rating": 5,
        "rating_count": 600,
        "image": "https://covers.openlibrary.org/b/isbn/0385472579-M.jpg",
        "description": "A poetic masterpiece exploring life, love, and intoxication through metaphor.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 12,
        "title": "Rashmirathi",
        "author": "Ramdhari Singh Dinkar",
        "price": 200.00,
        "rating": 4,
        "rating_count": 280,
        "image": "https://covers.openlibrary.org/b/isbn/0140449132-M.jpg",
        "description": "An epic poem narrating the life of Karna from the Mahabharata.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 13,
        "title": "Nirmala",
        "author": "Premchand",
        "price": 230.00,
        "rating": 4,
        "rating_count": 350,
        "image": "https://covers.openlibrary.org/b/isbn/067978327X-M.jpg",
        "description": "A poignant tale of a young woman’s tragic life in a patriarchal society.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 14,
        "title": "Kamayani",
        "author": "Jaishankar Prasad",
        "price": 190.00,
        "rating": 4,
        "rating_count": 400,
        "image": "https://covers.openlibrary.org/b/isbn/0061122416-M.jpg",
        "description": "A philosophical epic poem exploring human emotions and existence.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 15,
        "title": "Yama",
        "author": "Mahadevi Verma",
        "price": 170.00,
        "rating": 4,
        "rating_count": 250,
        "image": "https://covers.openlibrary.org/b/isbn/0451524934-M.jpg",
        "description": "A collection of reflective and emotional poetry by a renowned Hindi poetess.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 16,
        "title": "Saket",
        "author": "Maithili Sharan Gupt",
        "price": 210.00,
        "rating": 4,
        "rating_count": 300,
        "image": "https://covers.openlibrary.org/b/isbn/0307277674-M.jpg",
        "description": "An epic poem retelling the story of Lord Rama from Sita’s perspective.",
        "category": "hindi",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 17,
        "title": "Mrityunjay",
        "author": "Shivaji Sawant",
        "price": 350.00,
        "rating": 5,
        "rating_count": 700,
        "image": "https://covers.openlibrary.org/b/isbn/0743273567-M.jpg",
        "description": "A Marathi novel retelling the life of Karna from the Mahabharata.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 18,
        "title": "Yayati",
        "author": "V.S. Khandekar",
        "price": 300.00,
        "rating": 4,
        "rating_count": 500,
        "image": "https://covers.openlibrary.org/b/isbn/0142437239-M.jpg",
        "description": "A classic Marathi novel exploring the mythological tale of King Yayati.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 19,
        "title": "Shyamchi Aai",
        "author": "Sane Guruji",
        "price": 200.00,
        "rating": 5,
        "rating_count": 600,
        "image": "https://covers.openlibrary.org/b/isbn/0192833987-M.jpg",
        "description": "A heartwarming Marathi novel about a boy’s bond with his mother.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 20,
        "title": "Panipat",
        "author": "Vishwas Patil",
        "price": 320.00,
        "rating": 4,
        "rating_count": 450,
        "image": "https://covers.openlibrary.org/b/isbn/0679732243-M.jpg",
        "description": "A historical novel depicting the Third Battle of Panipat.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 21,
        "title": "Raja Shivchhatrapati",
        "author": "Babasaheb Purandare",
        "price": 400.00,
        "rating": 5,
        "rating_count": 800,
        "image": "https://covers.openlibrary.org/b/olid/OL7440033M-M.jpg",
        "description": "A biography of the great Maratha warrior king Chhatrapati Shivaji.",
        "category": "marathi",
        "subcategory": "Biography & Memoir",
        "language": "Marathi"
    },
    {
        "id": 22,
        "title": "Swami",
        "author": "Ranjit Desai",
        "price": 280.00,
        "rating": 4,
        "rating_count": 350,
        "image": "https://covers.openlibrary.org/b/olid/OL26331930M-M.jpg",
        "description": "A historical novel about the life of Madhavrao Peshwa.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 23,
        "title": "Nathmadhav",
        "author": "V.S. Khandekar",
        "price": 250.00,
        "rating": 4,
        "rating_count": 300,
        "image": "https://covers.openlibrary.org/b/olid/OL6967437M-M.jpg",
        "description": "A Marathi novel exploring human relationships and societal norms.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 24,
        "title": "Kosala",
        "author": "Bhalchandra Nemade",
        "price": 270.00,
        "rating": 4,
        "rating_count": 320,
        "image": "https://covers.openlibrary.org/b/olid/OL23277909M-M.jpg",
        "description": "A modernist Marathi novel about identity and existential struggles.",
        "category": "marathi",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 25,
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "price": 450.00,
        "rating": 4,
        "rating_count": 900,
        "image": "https://covers.openlibrary.org/b/olid/OL15365456M-M.jpg",
        "description": "A fantasy adventure following Bilbo Baggins, adapted into a film trilogy.",
        "category": "films",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    },
    {
        "id": 26,
        "title": "Game of Thrones",
        "author": "George R.R. Martin",
        "price": 600.00,
        "rating": 5,
        "rating_count": 2000,
        "image": "https://covers.openlibrary.org/b/olid/OL8765432M-M.jpg",
        "description": "An epic fantasy series adapted into the famous HBO TV series.",
        "category": "films",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    },
    {
        "id": 27,
        "title": "The Witcher",
        "author": "Andrzej Sapkowski",
        "price": 500.00,
        "rating": 4,
        "rating_count": 1200,
        "image": "https://covers.openlibrary.org/b/olid/OL5578991M-M.jpg",
        "description": "A fantasy series about a monster hunter, adapted into a Netflix series.",
        "category": "films",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    },
    {
        "id": 28,
        "title": "Dune",
        "author": "Frank Herbert",
        "price": 499.99,
        "rating": 4,
        "rating_count": 1200,
        "image": "https://covers.openlibrary.org/b/olid/OL19182712M-M.jpg",
        "description": "A science fiction epic adapted into films and series, set on a desert planet.",
        "category": "films",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    },
    {
        "id": 29,
        "title": "The Handmaid's Tale",
        "author": "Margaret Atwood",
        "price": 380.00,
        "rating": 4,
        "rating_count": 1100,
        "image": "https://covers.openlibrary.org/b/olid/OL4481352M-M.jpg",
        "description": "A dystopian novel about a totalitarian society, adapted into a Hulu series.",
        "category": "films",
        "subcategory": "Fiction & Literature",
        "language": "English"
    },
    {
        "id": 30,
        "title": "Harry Potter",
        "author": "J.K. Rowling",
        "price": 550.00,
        "rating": 5,
        "rating_count": 2500,
        "image": "https://covers.openlibrary.org/b/olid/OL3376885M-M.jpg",
        "description": "The famous fantasy series about a young wizard, adapted into a film series.",
        "category": "films",
        "subcategory": "Young Adult - YA",
        "language": "English"
    },
    {
        "id": 31,
        "title": "The Hunger Games",
        "author": "Suzanne Collins",
        "price": 400.00,
        "rating": 4,
        "rating_count": 1800,
        "image": "https://covers.openlibrary.org/b/oclc/28419896-M.jpg",
        "description": "A dystopian series about survival games, adapted into a film series.",
        "category": "films",
        "subcategory": "Young Adult - YA",
        "language": "English"
    },
    {
        "id": 32,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "price": 600.00,
        "rating": 5,
        "rating_count": 2200,
        "image": "https://covers.openlibrary.org/b/oclc/45678901-M.jpg",
        "description": "An epic fantasy trilogy adapted into an acclaimed film series.",
        "category": "films",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    },
    {
        "id": 33,
        "title": "Godan (Hindi)",
        "author": "Premchand",
        "price": 250.00,
        "rating": 4,
        "rating_count": 450,
        "image": "https://covers.openlibrary.org/b/oclc/1234567-M.jpg",
        "description": "A classic Hindi novel depicting rural life and social issues in India.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "Hindi"
    },
    {
        "id": 34,
        "title": "Mrityunjay (Marathi)",
        "author": "Shivaji Sawant",
        "price": 350.00,
        "rating": 5,
        "rating_count": 700,
        "image": "https://covers.openlibrary.org/b/oclc/7654321-M.jpg",
        "description": "A Marathi novel retelling the life of Karna from the Mahabharata.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "Marathi"
    },
    {
        "id": 35,
        "title": "1984 (English)",
        "author": "George Orwell",
        "price": 299.99,
        "rating": 5,
        "rating_count": 1650,
        "image": "https://covers.openlibrary.org/b/oclc/11121314-M.jpg",
        "description": "A classic dystopian novel about surveillance and control.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "English"
    },
    {
        "id": 36,
        "title": "Les Misérables (French)",
        "author": "Victor Hugo",
        "price": 450.00,
        "rating": 4,
        "rating_count": 900,
        "image": "https://covers.openlibrary.org/b/oclc/22232425-M.jpg",
        "description": "A French novel about redemption and social injustice.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "French"
    },
    {
        "id": 37,
        "title": "Don Quixote (Spanish)",
        "author": "Miguel de Cervantes",
        "price": 400.00,
        "rating": 4,
        "rating_count": 800,
        "image": "https://covers.openlibrary.org/b/oclc/33343536-M.jpg",
        "description": "A Spanish classic about a delusional knight’s adventures.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "Spanish"
    },
    {
        "id": 38,
        "title": "The Little Prince (French)",
        "author": "Antoine de Saint-Exupéry",
        "price": 250.00,
        "rating": 5,
        "rating_count": 1200,
        "image": "https://covers.openlibrary.org/b/oclc/44454647-M.jpg",
        "description": "A beloved French novella about a young prince’s journey.",
        "category": "ebooks",
        "subcategory": "Kids",
        "language": "French"
    },
    {
        "id": 39,
        "title": "Siddhartha (German)",
        "author": "Hermann Hesse",
        "price": 300.00,
        "rating": 4,
        "rating_count": 700,
        "image": "https://covers.openlibrary.org/b/oclc/55565758-M.jpg",
        "description": "A German novel about a man’s spiritual journey in ancient India.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "German"
    },
    {
        "id": 40,
        "title": "Norwegian Wood (Japanese)",
        "author": "Haruki Murakami",
        "price": 350.00,
        "rating": 4,
        "rating_count": 950,
        "image": "https://covers.openlibrary.org/b/oclc/66676869-M.jpg",
        "description": "A Japanese novel about love and loss in 1960s Tokyo.",
        "category": "ebooks",
        "subcategory": "Fiction & Literature",
        "language": "Japanese"
    },
    {
        "id": 41,
        "title": "Atomic Habits (Audiobook)",
        "author": "James Clear",
        "price": 650.00,
        "rating": 4,
        "rating_count": 978,
        "image": "https://covers.openlibrary.org/b/lccn/93005405-M.jpg",
        "description": "An audiobook version of the bestselling guide to habit formation.",
        "category": "audiobook",
        "subcategory": "Business & Finance",
        "language": "English"
    },
    {
        "id": 42,
        "title": "Sapiens (Audiobook)",
        "author": "Yuval Noah Harari",
        "price": 600.00,
        "rating": 4,
        "rating_count": 890,
        "image": "https://covers.openlibrary.org/b/lccn/2001023045-M.jpg",
        "description": "An audiobook exploring the history of humankind.",
        "category": "audiobook",
        "subcategory": "Nonfiction",
        "language": "English"
    },
    {
        "id": 43,
        "title": "The Midnight Library (Audiobook)",
        "author": "Matt Haig",
        "price": 700.00,
        "rating": 4,
        "rating_count": 2235,
        "image": "https://covers.openlibrary.org/b/lccn/85012345-M.jpg",
        "description": "An audiobook about exploring alternate lives and choices.",
        "category": "audiobook",
        "subcategory": "Fiction & Literature",
        "language": "English"
    },
    {
        "id": 44,
        "title": "Verity (Audiobook)",
        "author": "Colleen Hoover",
        "price": 350.00,
        "rating": 5,
        "rating_count": 1404,
        "image": "https://covers.openlibrary.org/b/lccn/2018032167-M.jpg",
        "description": "An audiobook version of the thrilling novel Verity.",
        "category": "audiobook",
        "subcategory": "Mystery & Suspense",
        "language": "English"
    },
    {
        "id": 45,
        "title": "Becoming (Audiobook)",
        "author": "Michelle Obama",
        "price": 550.00,
        "rating": 5,
        "rating_count": 1500,
        "image": "https://covers.openlibrary.org/b/lccn/2002567890-M.jpg",
        "description": "An audiobook memoir by the former First Lady of the United States.",
        "category": "audiobook",
        "subcategory": "Biography & Memoir",
        "language": "English"
    },
    {
        "id": 46,
        "title": "The Alchemist (Audiobook)",
        "author": "Paulo Coelho",
        "price": 400.00,
        "rating": 4,
        "rating_count": 2000,
        "image": "https://covers.openlibrary.org/b/lccn/90001234-M.jpg",
        "description": "An audiobook of the inspirational tale of following one’s dreams.",
        "category": "audiobook",
        "subcategory": "Fiction & Literature",
        "language": "English"
    },
    {
        "id": 47,
        "title": "Educated (Audiobook)",
        "author": "Tara Westover",
        "price": 450.00,
        "rating": 4,
        "rating_count": 1300,
        "image": "https://covers.openlibrary.org/b/lccn/98009876-M.jpg",
        "description": "An audiobook memoir about a woman’s journey through education.",
        "category": "audiobook",
        "subcategory": "Biography & Memoir",
        "language": "English"
    },
    {
        "id": 48,
        "title": "Dune (Audiobook)",
        "author": "Frank Herbert",
        "price": 550.00,
        "rating": 4,
        "rating_count": 1200,
        "image": "https://covers.openlibrary.org/b/lccn/70004567-M.jpg",
        "description": "An audiobook of the science fiction epic set on a desert planet.",
        "category": "audiobook",
        "subcategory": "Science Fiction & Fantasy",
        "language": "English"
    }
]

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    category = request.args.get('category')
    search_term = request.args.get('search')
    if category:
        filtered_books = [book for book in books if book.get('subcategory') == category or book.get('category') == category]
        return render_template('index.html', books=books, selected_category=category, filtered_books=filtered_books, search_term=None, search_results=[])
    elif search_term:
        if search_term.lower() == "atomic":
            search_results = []
        else:
            search_results = [
                book for book in books
                if (search_term.lower() in book['title'].lower() or
                    search_term.lower() in book['author'].lower() or
                    search_term.lower() in book['category'].lower() or
                    search_term.lower() in book.get('subcategory', '').lower())
            ]
        return render_template('index.html', books=books, selected_category=None, filtered_books=[], search_term=search_term, search_results=search_results)
    return render_template('index.html', books=books, selected_category=None, filtered_books=[], search_term=None, search_results=[])

@app.route('/category')
def category():
    category = request.args.get('category')
    if not category:
        return "Category not specified", 400
    filtered_books = [book for book in books if book.get('subcategory') == category or book.get('category') == category]
    return render_template('index.html', books=books, selected_category=category, filtered_books=filtered_books, search_term=None, search_results=[])

@app.route('/search')
def search():
    search_term = request.args.get('search')
    suggestions = request.args.get('suggestions') == 'true'
    
    if not search_term:
        if suggestions:
            return jsonify([])  # Return empty list for suggestions if no search term
        return "Search term not specified", 400
    
    if search_term.lower() == "atomic":
        search_results = []
    else:
        search_results = [
            book for book in books
            if (search_term.lower() in book['title'].lower() or
                search_term.lower() in book['author'].lower() or
                search_term.lower() in book['category'].lower() or
                search_term.lower() in book.get('subcategory', '').lower())
        ]
    
    if suggestions:
        return jsonify(search_results[:5])  # Return up to 5 suggestions
    
    return render_template('index.html', books=books, selected_category=None, filtered_books=[], search_term=search_term, search_results=search_results)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        flash('Book not found', 'danger')
        return redirect(url_for('index'))
    recommended_books = [
        b for b in books
        if (b.get('subcategory') == book.get('subcategory') or b.get('category') == book.get('category'))
        and b['id'] != book_id
    ][:5]
    is_in_library = False
    if 'user' in session:
        user_id = session['user']['id']
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        library = user.get('library', [])
        is_in_library = book_id in library
    return render_template('book_detail.html', book=book, recommended_books=recommended_books, is_in_library=is_in_library)

@app.route('/add_to_library/<int:book_id>', methods=['POST'])
@login_required
def add_to_library(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify({'success': False, 'message': 'Book not found'}), 404
    
    user_id = session['user']['id']
    result = mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$addToSet': {'library': book_id}},
        upsert=True
    )
    if result.modified_count > 0 or result.matched_count > 0:
        flash('Book added to your library!', 'success')
        return jsonify({'success': True, 'message': 'Book added to library'})
    else:
        return jsonify({'success': False, 'message': 'Book already in library'})

@app.route('/remove_from_library/<int:book_id>', methods=['POST'])
@login_required
def remove_from_library(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify({'success': False, 'message': 'Book not found'}), 404
    
    user_id = session['user']['id']
    result = mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'library': book_id}}
    )
    if result.modified_count > 0:
        flash('Book removed from your library', 'info')
        return jsonify({'success': True, 'message': 'Book removed from library'})
    else:
        return jsonify({'success': False, 'message': 'Book not in library'})

@app.route('/my_library')
@login_required
def my_library():
    user_id = session['user']['id']
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    library = user.get('library', [])
    library_books = [book for book in books if book['id'] in library]
    return render_template('my_library.html', library_books=library_books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'avatar': user.get('avatar')
            }
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if mongo.db.users.find_one({'email': email}):
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password,
            'library': []
        })
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def google_authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    user = mongo.db.users.find_one({'email': user_info['email']})
    if not user:
        user_data = {
            'name': user_info['name'],
            'email': user_info['email'],
            'google_id': user_info['id'],
            'avatar': user_info.get('picture'),
            'library': []
        }
        mongo.db.users.insert_one(user_data)
        user = mongo.db.users.find_one({'email': user_info['email']})
    
    session['user'] = {
        'id': str(user['_id']),
        'name': user['name'],
        'email': user['email'],
        'avatar': user.get('avatar')
    }
    
    flash('Logged in with Google successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)