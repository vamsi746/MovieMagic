from flask import Flask, render_template, request, redirect, session, url_for, flash
import uuid
from pymongo import MongoClient

# 🔗 MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://Vamsi:Vamsi123@cluster0.kxrk338.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["moviemagic"]
users_collection = db["users"]
bookings_collection = db["bookings"]

app = Flask(__name__)
app.secret_key = "secret123"

# === Sample Movies ===
movies = [
    {
        "id": "1",
        "title": "Inception",
        "banner": "/static/inception.jpg",
        "theater": "PVR Cinemas",
        "price": "200",
        "description": "A mind-bending thriller by Christopher Nolan.",
        "genre": "Sci-Fi",
        "rating": "⭐ 4.8",
        "release": "2010",
        "trending": True
    },
    {
        "id": "2",
        "title": "Interstellar",
        "banner": "/static/interstellar.jpg",
        "theater": "INOX",
        "price": "250",
        "description": "A space epic exploring time and love.",
        "genre": "Adventure",
        "rating": "⭐ 4.7",
        "release": "2014",
        "trending": True
    },
    {
        "id": "3",
        "title": "The Dark Knight",
        "banner": "/static/dark_knight.jpg",
        "theater": "Carnival",
        "price": "180",
        "description": "Batman faces the Joker in this masterpiece.",
        "genre": "Action",
        "rating": "⭐ 4.9",
        "release": "2008",
        "trending": True
    },
    {
        "id": "4",
        "title": "Avatar: The Way of Water",
        "banner": "/static/avatar.jpg",
        "theater": "PVR",
        "price": "300",
        "description": "Return to Pandora in a visually stunning sequel.",
        "genre": "Fantasy",
        "rating": "⭐ 4.6",
        "release": "2022",
        "trending": True
    },
    {
        "id": "5",
        "title": "Top Gun: Maverick",
        "banner": "/static/topgun.jpg",
        "theater": "INOX",
        "price": "220",
        "description": "Tom Cruise returns to the skies in this blockbuster.",
        "genre": "Action",
        "rating": "⭐ 4.5",
        "release": "2022",
        "trending": False
    },
    {
        "id": "6",
        "title": "Spider-Man: No Way Home",
        "banner": "/static/spiderman.jpg",
        "theater": "Cinepolis",
        "price": "240",
        "description": "Multiverse adventure with your favorite Spider-Men.",
        "genre": "Superhero",
        "rating": "⭐ 4.7",
        "release": "2021",
        "trending": True
    }
]


# === Theatre Data ===
theatres = {
    "1": [
        {"id": "t1", "name": "PVR Cinemas - Andheri", "timings": ["10:00 AM", "1:00 PM", "7:00 PM"]},
        {"id": "t2", "name": "Carnival - Borivali", "timings": ["11:30 AM", "3:00 PM", "9:00 PM"]}
    ],
    "2": [
        {"id": "t3", "name": "Cinepolis - Malad", "timings": ["9:00 AM", "12:30 PM", "6:30 PM"]},
        {"id": "t4", "name": "INOX - Ghatkopar", "timings": ["2:00 PM", "5:30 PM", "8:45 PM"]}
    ],
    "3": [
        {"id": "t5", "name": "PVR Icon - Lower Parel", "timings": ["10:15 AM", "2:15 PM", "7:45 PM"]},
        {"id": "t6", "name": "Miraj Cinemas - Chembur", "timings": ["1:00 PM", "4:00 PM", "10:00 PM"]}
    ],
    "4": [
        {"id": "t7", "name": "Movietime - Kandivali", "timings": ["9:30 AM", "1:30 PM", "6:00 PM"]},
        {"id": "t8", "name": "MAXUS Cinemas - Bhayandar", "timings": ["11:00 AM", "3:00 PM", "9:00 PM"]}
    ],
    "5": [
        {"id": "t9", "name": "Gold Cinema - Mulund", "timings": ["10:45 AM", "2:45 PM", "8:15 PM"]},
        {"id": "t10", "name": "PVR Phoenix - Kurla", "timings": ["12:00 PM", "4:00 PM", "10:30 PM"]}
    ],
    "6": [
        {"id": "t11", "name": "Carnival - Dahisar", "timings": ["9:00 AM", "1:00 PM", "7:00 PM"]},
        {"id": "t12", "name": "Cinepolis - Thane", "timings": ["11:15 AM", "3:15 PM", "9:15 PM"]}
    ]
    # (keep your other theatres here)
}

# === DB Helpers ===
def store_user(email, password):
    users_collection.insert_one({"email": email, "password": password})

def get_user(email):
    return users_collection.find_one({"email": email})

def store_booking(data):
    bookings_collection.insert_one(data)

def get_user_bookings(email):
    return list(bookings_collection.find({"user": email}))

def delete_booking(booking_id, email):
    return bookings_collection.delete_one({"booking_id": booking_id, "user": email})

def get_bookings_for_show(movie_id, theater_id, date, timing):
    return list(bookings_collection.find({
        "movie_id": movie_id,
        "theater_id": theater_id,
        "date": date,
        "timing": timing
    }))

def send_email_notification(booking):
    print(f"[SIMULATED EMAIL] Booking confirmation sent to {booking['user']}")

# === Routes ===
@app.route('/')
def index():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', movies=movies)

@app.route('/movie/<movie_id>')
def movie_details(movie_id):
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        flash("Movie not found!")
        return redirect(url_for('index'))
    movie_theatres = theatres.get(movie_id, [])
    return render_template('movie_details.html', movie=movie, theatres=movie_theatres)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if get_user(email):
            flash("User already exists!")
        elif password != confirm_password:
            flash("Passwords do not match!")
        else:
            store_user(email, password)
            flash("Registered successfully!")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user(email)
        if user and user['password'] == password:
            session['email'] = email
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!")

    return render_template('login.html')

@app.route('/select_seats/<movie_id>/<theatre_id>', methods=['GET', 'POST'])
def select_seats(movie_id, theatre_id):
    if 'email' not in session:
        flash("Please login to book seats.")
        return redirect(url_for('login'))

    movie = next((m for m in movies if m['id'] == movie_id), None)
    theatre_list = theatres.get(movie_id, [])
    theatre = next((t for t in theatre_list if t['id'] == theatre_id), None)

    timing = request.args.get('timing')
    date = request.args.get('date')

    booked_seats = []
    for booking in get_bookings_for_show(movie_id, theatre_id, date, timing):
        booked_seats.extend([s.strip() for s in booking.get("seat", "").split(",") if s.strip()])

    if request.method == 'POST':
        date = request.form.get('date', date)
        timing = request.form.get('timing', timing)
        selected_seats = request.form.getlist('seat')
        persons = request.form.get('persons')
        total_price = request.form.get('total_price', '0')

        for seat in selected_seats:
            if seat in booked_seats:
                flash(f"Seat {seat} is already sold out.")
                return redirect(request.url)

        if not selected_seats:
            flash("Please select at least one seat.")
            return redirect(request.url)

        booking_id = str(uuid.uuid4())[:8]
        booking_data = {
            "booking_id": booking_id,
            "user": session['email'],
            "movie": movie['title'],
            "movie_id": movie_id,
            "theater": theatre['name'],
            "theater_id": theatre_id,
            "timing": timing,
            "seat": ", ".join(selected_seats),
            "persons": persons,
            "date": date,
            "amount": total_price
        }
        store_booking(booking_data)
        send_email_notification(booking_data)
        return render_template("tickets.html", booking_id=booking_id, data=booking_data)

    return render_template("select_seats.html", movie=movie, theatre=theatre, timing=timing, date=date, booked_seats=booked_seats)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('index'))

@app.route('/my_bookings')
def my_bookings():
    if 'email' not in session:
        flash("Please log in to view your bookings.")
        return redirect(url_for('login'))
    user_bookings = get_user_bookings(session['email'])
    return render_template('my_bookings.html', bookings=user_bookings)

@app.route('/cancel_booking/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'email' not in session:
        flash("Please log in to cancel a booking.")
        return redirect(url_for('login'))
    result = delete_booking(booking_id, session['email'])
    if result.deleted_count > 0:
        flash("Your booking was successfully cancelled.")
    else:
        flash("Booking not found or access denied.")
    return redirect(url_for('my_bookings'))

@app.route('/developer', methods=['GET', 'POST'])
def developer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        if not name or not email or not message:
            flash("All fields are required!")
            return redirect(url_for('developer'))
        flash("Thank you for reaching out! I will get back to you soon.")
        return redirect(url_for('developer'))
    return render_template('developer.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True)
