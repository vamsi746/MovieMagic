# 🔁 Uncomment these when AWS is ready
# from aws_helper import store_user_aws as store_user
# from aws_helper import get_user_aws as get_user
# from aws_helper import store_booking_aws as store_booking
# from aws_helper import send_email_notification_aws as send_email_notification

from flask import Flask, render_template, request, redirect, session, url_for, flash
import uuid

app = Flask(__name__)
app.secret_key = "secret123"  # For session security

# Sample movie catalog
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

# === Local Simulated Database ===
users = {}
bookings = {}

# === Helper Functions (Mock AWS Logic) ===

def store_user(email, password):
    """Store user in local mock DB"""
    users[email] = {'password': password}

def get_user(email):
    """Retrieve user from local mock DB"""
    return users.get(email)

def store_booking(data):
    """Store booking in local mock DB"""
    bookings[data['booking_id']] = data

def get_booking(booking_id):
    """Retrieve booking from local mock DB"""
    return bookings.get(booking_id)

def send_email_notification(booking):
    """Simulated AWS SNS Email Notification"""
    print(f"[SIMULATED EMAIL] Booking confirmation sent to {booking['user']}")
    # This will later use AWS SNS in cloud

# === Theatre Data per Movie ===
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
}


# === Routes ===

@app.route('/')
@app.route('/')
def index():
    if 'email' not in session:
        # User is not logged in, redirect to login
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
            flash('User already exists!')
        elif password != confirm_password:
            flash('Passwords do not match!')
        else:
            store_user(email, password)
            flash('Registered successfully!')
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
            flash('Login successful!')
            return redirect(url_for('index'))  # ✅ Changed to index
        else:
            flash('Invalid credentials!')

    return render_template('login.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'email' not in session:
        flash('Please login first!')
        return redirect(url_for('login'))

    movie_id = request.args.get('movie_id')
    selected_movie = None
    if movie_id:
        selected_movie = next((m for m in movies if m['id'] == movie_id), None)

    if request.method == 'POST':
        movie = request.form['movie']
        theater = request.form['theater']
        seat = request.form['seat']
        booking_id = str(uuid.uuid4())[:8]

        booking_data = {
            'booking_id': booking_id,
            'user': session['email'],
            'movie': movie,
            'movie_id': movie_id,           # new
            'theater': theater,
            'theater_id': theater_id,       # new
            'date': date,                   # new
            'time': time,                   # new
            'seats': selected_seats,        # this must be a list!
            'num_persons': num_persons
        }
        store_booking(booking_data)
        send_email_notification(booking_data)

        return render_template('tickets.html', booking_id=booking_id, data=booking_data)

    return render_template('booking.html', selected_movie=selected_movie)

@app.route('/select_seats/<movie_id>/<theatre_id>', methods=['GET', 'POST'])
def select_seats(movie_id, theatre_id):
    if 'email' not in session:
        flash('Please login to book seats.')
        return redirect(url_for('login'))

    movie = next((m for m in movies if m['id'] == movie_id), None)
    theatre_list = theatres.get(movie_id, [])
    theatre = next((t for t in theatre_list if t['id'] == theatre_id), None)

    # Get date and timing (these come from query params)
    timing = request.args.get('timing')
    date = request.args.get('date')

    if request.method == 'POST':
        # In POST, also retrieve date and timing from hidden fields
        date = request.form.get('date', date)
        timing = request.form.get('timing', timing)

        selected_seats = request.form.getlist('seat')
        persons = request.form.get('persons')
        total_price = request.form.get('total_price', '0')

        if not selected_seats:
            flash("Please select at least one seat.")
            return redirect(request.url)

        booking_id = str(uuid.uuid4())[:8]

        booking_data = {
            'booking_id': booking_id,
            'user': session['email'],
            'movie': movie['title'],
            'theater': theatre['name'],
            'timing': timing,
            'seat': ", ".join(selected_seats),
            'persons': persons,
            'date': date,
            'amount': total_price
        }

        store_booking(booking_data)
        send_email_notification(booking_data)

        return render_template('tickets.html', booking_id=booking_id, data=booking_data)

    return render_template('select_seats.html', movie=movie, theatre=theatre, timing=timing, date=date)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('index'))
@app.route('/my_bookings')
def my_bookings():
    if 'email' not in session:
        flash("Please log in to view your bookings.")
        return redirect(url_for('login'))

    user_email = session['email']
    user_bookings = [b for b in bookings.values() if b['user'] == user_email]

    return render_template('my_bookings.html', bookings=user_bookings)
@app.route('/cancel_booking/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'email' not in session:
        flash("Please log in to cancel a booking.")
        return redirect(url_for('login'))

    # Check if booking exists and belongs to user
    booking = bookings.get(booking_id)
    if booking and booking['user'] == session['email']:
        del bookings[booking_id]
        flash("Your booking was successfully cancelled.")
    else:
        flash("Booking not found or access denied.")

    return redirect(url_for('my_bookings'))
@app.route("/developer")
@app.route('/developer', methods=['GET', 'POST'])
def developer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if not name or not email or not message:
            flash('All fields are required!')
            return redirect(url_for('developer'))

        flash('Thank you for reaching out! I will get back to you soon.')
        return redirect(url_for('developer'))

    return render_template('developer.html')
@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    app.run(debug=True)
