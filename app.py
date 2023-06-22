import re
from flask import Flask, json, redirect, render_template, request, session , jsonify
import requests
import json
import ibm_db
app = Flask(__name__)
cart = []
rows = []
app.secret_key = 'a'
conn = ibm_db.connect(
    "DATABASE= bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLCertificate=DigiCertificate.crt;UID=cqc31977;PWD=ImVje7lzKyapTC0b;", '', '')
print('connected')

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    global uid
    msg = ''
    if request.method == 'POST':
        # print("Haiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        email = request.form['email']
        password = request.form['password']
        print(email, "-------", password)
        sql = "SELECT * FROM PHARMACY WHERE email=? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:

            session['loggedin'] = True
            session['UID'] = account['UID']
            session['id'] = account['EMAIL']
            userid = account['EMAIL']
            session['EMAIL'] = account['EMAIL']
            msg = 'logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect email/password'
            return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        # print('hi----------------------')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print(username)
        sql = "SELECT * FROM PHARMACY WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email address !"
        else:
            sql = "SELECT count(*) FROM PHARMACY"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql = "INSERT INTO PHARMACY VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
            msg = 'you have registered !'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template('login.html')



@app.route('/index', methods=['GET', 'POST'])
def index1():
    output = []
    if request.method == 'POST':

        Search = request.form['search']

        url = "https://medicine-autocomplete-indian-brands.p.rapidapi.com/api/medicine/search"
        querystring = {"searchterm": Search}

        headers = {
            "X-RapidAPI-Key": "714250c24fmsh829f65c05932f01p1ad65cjsn43a39e64b3bb",
            "X-RapidAPI-Host": "medicine-autocomplete-indian-brands.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        output = response.json()
        return render_template('search.html', output=output)
    else:
        return render_template('index.html')




@app.route('/cart', methods=['GET', 'POST'])
def add_to_cart():
    cart = []
    sql = "SELECT * FROM PHARMACY WHERE UID = " + str(session['UID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    rows = []  # Define 'rows' with an initial empty list
    if request.method == 'POST':
        name = str(request.form['name'])
        content = str(request.form['content'])
        company = str(request.form['company'])
        price = request.form['price']
        quantity = int(request.form['quantity'])
        total = request.form['total']
        print(total)
        # Add the item to the cart
        if quantity > 0:
            item = {
                'name': name,
                'content': content,
                'company': company,
                'price': price,
                'quantity': quantity,
                'total': total
            }
            cart.append(item)
            print(cart)
            insert_sql = "INSERT INTO MYPRODUCT VALUES (?, ?, ?, ?, ?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, content)
            ibm_db.bind_param(prep_stmt, 3, company)
            ibm_db.bind_param(prep_stmt, 4, price)
            ibm_db.bind_param(prep_stmt, 5, account["UID"])
            ibm_db.bind_param(prep_stmt, 6, quantity)
            ibm_db.bind_param(prep_stmt, 7, total)
            ibm_db.execute(prep_stmt)
            select_sql = "SELECT * FROM MYPRODUCT WHERE UID=" + str(account["UID"])
            stmt = ibm_db.prepare(conn, select_sql)
            ibm_db.execute(stmt)
            data = ibm_db.fetch_tuple(stmt)
            print(data)
            print("hii")
            rows = []
            print("hello")

            while data != False:
                rows.append(data)
                data = ibm_db.fetch_tuple(stmt)
            print(rows)
    return render_template('cart.html', rows=rows)

        
       

@app.route('/remove', methods=['POST'])
def remove_from_cart():
    try:
        name = request.json['name']
        uid = session['UID']
        
        delete_sql = "DELETE FROM MYPRODUCT WHERE name = ? AND UID = ?"
        prep_stmt = ibm_db.prepare(conn, delete_sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.bind_param(prep_stmt, 2, uid)
        ibm_db.execute(prep_stmt)
        
        select_sql = "SELECT * FROM MYPRODUCT WHERE UID = ?"
        prep_stmt = ibm_db.prepare(conn, select_sql)
        ibm_db.bind_param(prep_stmt, 1, uid)
        ibm_db.execute(prep_stmt)
        
        rows = []
        while True:
            data = ibm_db.fetch_assoc(prep_stmt)
            if not data:
                break
            else:
                data['UID'] = str(data['UID'])
                rows.append(data)

        return jsonify({'success': True, 'rows': rows})
        
    except Exception as e:
        # Return a JSON response indicating the error
        return jsonify({'success': False, 'error': str(e)})


@app.route('/total_amount', methods=['GET'])
def calculate_total_amount():
    sql = 'SELECT * FROM MYPRODUCT WHERE UID = ' + str(session['UID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    
    total_sum = 0.0
    row = ibm_db.fetch_assoc(stmt)
    while row:
        total_sum += float(row['total'])
        row = ibm_db.fetch_assoc(stmt)

    return jsonify({'total_amount': total_sum})




@app.route('/payment', methods=['POST'])
def payment():
    if request.method == 'POST':
        totalAmount = request.form.get('totalAmount', 0.0)
        
        return render_template('payment.html', totalAmount=totalAmount)


@app.route('/thankyou', methods=['POST'])
def thankyou():

    cname = request.form['cname']
    cnum = request.form['cnum']
    exp = request.form['exp']
    cvv = request.form['cvv']
    fname = request.form['fname']
    pnum = request.form['pnum']
    address = request.form['address']
    city = request.form['city']
    state = request.form['state']
    pincode = request.form['pincode']

    return render_template('thankyou.html')


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
