import mysql.connector as m

con = m.connect(host = "localhost", user = "root", password = "root1234",
                 database = "car_Rental")
cursor = con.cursor()

def user_exists(email_id):
    cursor.execute('SELECT * FROM customer_details WHERE email_id = %s', (email_id,))
    if cursor.fetchone():
        return cursor.fetchone()
    return None

def create_account(dlno, fname, lname, phone_no, email_id, pwd, street, city, state, pincode):
    cursor.execute('INSERT INTO customer_details VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                   (dlno, fname, lname, phone_no, email_id, pwd, street, city, state, pincode))
    con.commit()

def login_check(email_id, password):
    cursor.execute('SELECT email_id FROM customer_details WHERE email_id = %s AND pwd = %s', (email_id, password))
    return cursor.fetchone()

def car_info_full():
    cursor.execute('SELECT * FROM car_category')
    return cursor.fetchall()

def show_bookings(email_id):
    cursor.execute('SELECT  DL_NUMBER FROM customer_details WHERE email_id = %s', (email_id,))
    dlno = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM booking_details WHERE DL_NUMBER = %s AND booking_status != 'R'", (dlno,))
    data = cursor.fetchall()

    locations_pick = []
    locations_drop = []
    cars = []

    for i in data:
            # the location is stored as location_id in booking_details table, so we need to join it with location_details table to get the location name
            cursor.execute('SELECT * FROM location_details where location_id = %s', (i[5],))
            locations_pick.append(cursor.fetchone()[1])

            cursor.execute('SELECT * FROM location_details where location_id = %s', (i[6],))
            locations_drop.append(cursor.fetchone()[1])

            cursor.execute('SELECT * FROM car where registration_number = %s', (i[7],))
            cars.append(cursor.fetchone()[1])

    data = [data[i] + (locations_pick[i], locations_drop[i], cars[i]) for i in range(len(data))]
    return data

def find_available_cars(car_type, pick_up):
    if pick_up and car_type:
        cursor.execute('SELECT location_id FROM location_details WHERE city = %s', (pick_up,))
        pick_up = cursor.fetchall()

        cars = []

        for centre in pick_up:
            loc = centre[0]
            # get all cars that satisfy the constraints
            cursor.execute('SELECT * FROM car WHERE category_name = %s AND location_id = %s AND availability_flag="Y"', (car_type, loc))
            cars.extend(cursor.fetchall())
    elif pick_up:
        cursor.execute('SELECT location_id FROM location_details WHERE city = %s', (pick_up,))
        pick_up = cursor.fetchall()

        cars = []

        for centre in pick_up:
            loc = centre[0]
            # get all cars that satisfy the constraints
            cursor.execute('SELECT * FROM car WHERE location_id = %s AND availability_flag="Y"', (loc,))
            cars.extend(cursor.fetchall())
    elif car_type:
        cursor.execute('SELECT * FROM car WHERE category_name = %s AND availability_flag="Y"', (car_type,))
        cars = cursor.fetchall()
    else:
        cursor.execute('SELECT * FROM car WHERE availability_flag="Y"')
        cars = cursor.fetchall()


    # replace the location_id with the location name
    locations = []
    for i in cars:
        cursor.execute('SELECT * FROM location_details WHERE location_id = %s', (i[-2],))
        locations.append(cursor.fetchone()[1])

    cars = [cars[i] + (locations[i],) for i in range(len(cars))]
        
    return cars

def retrieve_car_info(registration_number):
    cursor.execute('SELECT * FROM car WHERE registration_number = %s', (registration_number,))
    car = cursor.fetchone()

    cursor.execute('SELECT * FROM location_details where location_id = %s', (car[6],))
    loc = cursor.fetchone()

    addr = ' '.join(loc[2:])

    return car + (loc[1],) + (addr,)

def cost_details(registration_number):
    cursor.execute('SELECT category_name FROM car WHERE registration_number = %s', (registration_number,))
    car = cursor.fetchone()

    cursor.execute('SELECT * FROM car_category WHERE category_name = %s', (car[0],))
    cost = cursor.fetchall()

    return cost[0]

import datetime 
def convert(date_time):
    format = '%Y-%m-%d'
    datetime_str = datetime.datetime.strptime(date_time, format)
 
    return datetime_str

def find_next_booking_id():
    cursor.execute('SELECT max(booking_id) FROM booking_details')
    cur_id = cursor.fetchone()[0][1:]
    next = int(cur_id) + 1

    return 'B' + str(next)

def make_booking(regno, start_date, end_date, email_id):
    start_date = convert(start_date)
    end_date = convert(end_date)

    cursor.execute('SELECT  DL_NUMBER FROM customer_details WHERE email_id = %s', (email_id,))
    dlno = cursor.fetchone()[0]

    cursor.execute('SELECT  location_id FROM car WHERE registration_number = %s', (regno,))
    loc = cursor.fetchone()[0]

    cost_per_day = cost_details(regno)[3]
    late_fee_per_day = cost_details(regno)[4]

    cost = (end_date - start_date).days * cost_per_day

    booking_id = find_next_booking_id()


    query = """
            INSERT INTO booking_details (BOOKING_ID, FROM_DT_TIME, RET_DT_TIME, AMOUNT, 
            BOOKING_STATUS, PICKUP_LOC, DROP_LOC, REGISTRATION_NUMBER, DL_NUMBER)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

    cursor.execute(query, (booking_id, start_date, end_date, cost, 'B', loc, loc, regno, dlno))
    con.commit()

    return (booking_id, start_date, end_date, cost, loc, regno, dlno, late_fee_per_day)

def payment_details(booking_id, actual_return_date):
    # cursor.execute('SELECT * FROM booking_details WHERE booking_id = %s', (booking_id,))
    if actual_return_date:
        cursor.callproc("calculate_late_fee_and_tax", args=(actual_return_date, booking_id))
        con.commit()

    else:
        cursor.callproc("calculate_late_fee_and_tax", args=(None, booking_id))
        con.commit()

def booking_bill_details(booking_id):
    cursor.execute('SELECT * FROM booking_details WHERE booking_id = %s', (booking_id,))
    data = cursor.fetchone()

    cursor.execute('SELECT * FROM billing_details where booking_id = %s', (booking_id,))
    bill = cursor.fetchone()

    cursor.fetchall()

    return data + bill

def update_bill(bill_id):
    query = "UPDATE billing_details SET bill_status = 'P' WHERE bill_id = %s"
    cursor.execute(query, (bill_id,))
    con.commit()

def show_bills(email_id, year=None):
    if year:
        query = """
            SELECT * FROM billing_details bill 
            JOIN booking_details book ON bill.booking_id = book.booking_id
            JOIN customer_details cust ON book.DL_NUMBER = cust.DL_NUMBER
            WHERE cust.email_id = %s AND YEAR(book.RET_DT_TIME) = %s"""
        cursor.execute(query, (email_id, year))
    else:
        query = """
                SELECT * FROM billing_details bill 
                JOIN booking_details book ON bill.booking_id = book.booking_id
                JOIN customer_details cust ON book.DL_NUMBER = cust.DL_NUMBER
                WHERE cust.email_id = %s"""
        cursor.execute(query, (email_id,))
    data = cursor.fetchall()
    return data