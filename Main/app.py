from helper import *
from flask import Flask, render_template, redirect, url_for, request, session
import mysql.connector as m

# connect to database
con = m.connect(host = "localhost", user = "root", password = "root1234",
                 database = "car_Rental")
cursor = con.cursor()

app = Flask(__name__)
app.secret_key = 'your secret key'

@app.route('/')
def index():
    # home page for car rental management system
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # for new user registration
    msg = ''
    if request.method == 'POST':
        # create variables for easy access
        dlno = request.form['dlno']
        fname = request.form['fname']
        lname = request.form['lname']
        phone_no = request.form['phone_no']
        email_id = request.form['email_id']
        pwd = request.form['password']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        pincode = request.form['pincode']

        account = user_exists(email_id)

        if account:
            msg = 'Account already exists!'
        else:
            create_account(dlno, fname, lname, phone_no, email_id, pwd, street, city, state, pincode)
            msg = 'You have successfully registered!'

            session ['loggedin'] = True
            session ['email_id'] = email_id

            return redirect(url_for('home'))
    
    return render_template('register.html', msg=msg)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        # create variables for easy access
        email = request.form['email_id']
        password = request.form['password']

        account = login_check(email, password)

        if account:
            # create session data, we can access this data in other routes
            session['loggedin'] = True
            session['email_id'] = account[0]

            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    
    # show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/home', methods=['GET', 'POST'])
def home():
    # get constraints from form, redirect to new page displaying available cars

    if request.method == 'POST':
        # collect car type, pick up location, drop off location, pick up date, drop off date
        car_type = request.form['car_type']
        pick_up = request.form  ['pick_up']
        
        cars = find_available_cars(car_type, pick_up)

        return render_template('available_cars.html', data=cars)
    else:
        # if constraints are not provided, show the home page
        return render_template('home.html')

@app.route('/car_info', methods=['GET', 'POST'])
def car_info():
    data = car_info_full()
    return render_template('car_info.html', data=data)

@app.route('/book_car_hidden', methods=['GET', 'POST'])
def book_car_hidden():
    # Query the database to get information about the selected car
    # You should retrieve this information from your database based on the registration_number
    if request.method == 'POST':
        registration_number = request.form['registration_number']
        session['registration_number'] = registration_number
        return redirect(url_for('book_car'))
    else:
        return redirect(url_for('available_cars'))

@app.route('/book_car', methods=['GET', 'POST'])
def book_car():
    # Retrieve the registration_number from the session
    registration_number = session.get('registration_number')

    car_info = retrieve_car_info(registration_number)
    cost_info = cost_details(registration_number)
    total_cost = 0
    start_date = end_date = ''

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        cost_per_day = float(request.form['cost_per_day'])

        end = convert(end_date)
        start = convert(start_date)

        total_cost = (end - start).days * cost_per_day
    
    return render_template('book_car.html', registration_number=registration_number, 
                           car_info=car_info, cost_info=cost_info, total_cost=total_cost,
                           start_date=start_date, end_date=end_date)

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    registration_number = request.form['registration_number']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    
    all_info = make_booking(registration_number, start_date, end_date, session.get('email_id'))
    all_info += retrieve_car_info(registration_number)

    return render_template('confirmation_book.html', all_info=all_info)

@app.route('/bookings', methods=['GET', 'POST'])
def bookings():
    if 'loggedin' in session:
        data = show_bookings(session.get('email_id'))     
        if request.method == "POST":
            actual_return_date = request.form["actual_return_date"]
            booking_id = request.form["booking_id"]

            payment_details(booking_id, actual_return_date)

            data = booking_bill_details(booking_id)

            return render_template('payment_details.html', data=data) 
        
        return render_template('bookings.html', signedin=session["loggedin"], data=data)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/payment_hidden', methods=['GET', 'POST'])
def payment_hidden():
    if request.method == 'POST':
        bill_id = request.form['bill_id']
        update_bill(bill_id)
        return redirect(url_for('payment'))
    else:
        return redirect(url_for('bookings'))

@app.route('/payment')
def payment():
    return render_template('payment.html')

@app.route('/bills', methods=['GET', 'POST'])
def bills():
    if request.method == 'POST':
        try:
            bill_id = request.form['bill_id']
            update_bill(bill_id)
            data = show_bills(email_id=session.get('email_id'))
            return render_template('bills.html', data=data)
        except:
            year = request.form['year']
            data = show_bills(email_id=session.get('email_id'), year=year)
            return render_template('bills.html', data=data)
    
    data = show_bills(session.get('email_id'))
    return render_template('bills.html', data=data)

@app.route('/bill_year', methods=['GET', 'POST'])
def bill_year():
        year = request.form["year"]
        if year == '':
            return redirect(url_for('bills'))
        data = show_bills(email_id=session.get('email_id'), year=year)
        return render_template('bill_year.html', data=data, year=year)


if __name__ == '__main__':
    app.run(port=8000, debug=True)


con.close()
session.clear()