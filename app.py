# file: app.py
import base64
import datetime
import json
import threading

from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
import qrcode
from io import BytesIO
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"
domain = "https://localhost:5000/"

# Đường dẫn tới file database SQLite
DATABASE = os.path.join(os.path.dirname(__file__), 'party.db')
login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


admin_user = User(id=1, username='admin', password='Abc@1234')


@login_manager.user_loader
def load_user(user_id):
    if user_id == admin_user.id:
        return admin_user
    return None


# Hàm khởi tạo và kết nối tới database
def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Tạo bảng nếu chưa tồn tại
def create_table():
    with connect_db() as conn:
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            hometown TEXT, 
            num_attendees INTEGER, 
            email TEXT,
            phone TEXT,
            birthdate TEXT,
            hashed_data TEXT,
            time_checkin TEXT,
            num_checkin INTEGER)''')


create_table()


def hash_data(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    return sha256.hexdigest()


# Hàm tạo mã QR và mã hóa base64
def generate_qr_code(hashed_str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(hashed_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    return img


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == admin_user.username and password == admin_user.password:
            login_user(admin_user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for("scan"))
        else:
            error_message = "Invalid username or password"
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')


# Trang đăng ký tham gia Party
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        hometown = request.form['hometown']
        num_attendees = request.form['num_attendees']
        qr_data = f"{name}-{datetime.datetime.now()}-{app.secret_key}"
        birthdate = request.form['birdyear']
        email = request.form['email']
        phone = request.form['phone']
        hashed_data = hash_data(qr_data)

        with connect_db() as conn:
            conn.execute(
                '''INSERT INTO participants (
                name, 
                birthdate, 
                hometown, 
                num_attendees, 
                hashed_data,
                email,
                phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, birthdate, hometown, num_attendees, hashed_data, email, phone))
            conn.commit()

        # Tạo thông tin QR Code từ thông tin đăng ký
        qr_code = generate_qr_code(hashed_data)
        qr_code_buffer = BytesIO()
        qr_code.save(qr_code_buffer, kind='PNG')
        qr_code_buffer.seek(0)

        return {'qr_code': base64.b64encode(qr_code_buffer.getvalue()).decode(), 'hashed_data': hashed_data}

    return render_template('register.html')


# @app.route('/qr_code/<hashed_data>', methods=['GET'])
# @login_required
# def checkin(hashed_data):
#     with connect_db() as conn:
#         cursor = conn.cursor()
#
#         cursor.execute("SELECT * FROM participants WHERE hashed_data=?", (hashed_data,))
#         data = cursor.fetchone()
#
#         if data:
#             # Dữ liệu tồn tại, bạn có thể trả về nó cho template checkin.html
#             return render_template('checkin.html', data=data)
#         else:
#             # Dữ liệu không tồn tại, bạn có thể xử lý theo ý muốn, ví dụ: trả về thông báo lỗi
#             return render_template('error.html', message='Dữ liệu không tồn tại')


# @app.before_request
# def require_login():
#     # Kiểm tra nếu route bắt đầu bằng 'qr_check/' và người dùng chưa đăng nhập
#     if request.endpoint and request.endpoint.startswith('checkin') and not current_user.is_authenticated:
#         return redirect(url_for('login', next=request.url))  # Redirect đến trang đăng nhập


# Trang thống kê
@app.route('/statistics')
def statistics():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM participants')
        r = [dict((cur.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur.fetchall()]
    result = {'total': len(r), 'totalNotFiltered': len(r), 'rows': r}
    sum_attendees = 0
    for p in r:
        sum_attendees += p['num_attendees']

    return render_template('statistics.html', participants=result, sum_attendees=sum_attendees)


@app.route('/api/cancel/register/<hashed_data>', methods=["DELETE"])
def cancel_register(hashed_data):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM participants WHERE hashed_data=?", (hashed_data,))
    return render_template('register.html')


@app.route('/api/cancel/registers', methods=["DELETE"])
def cancel_registers():
    with connect_db() as conn:
        cursor = conn.cursor()
        hashed_data = json.loads(request.args.get('hashed_data'))
        query = f"DELETE FROM participants WHERE hashed_data in ({','.join(['?'] * len(hashed_data))})"
        cursor.execute(query, hashed_data)
    return render_template('register.html')


@app.route('/checkin', methods=['POST'])
def checkin():
    num_checkin = request.form.get('numCheckin')
    hashed_data = request.form.get('hashedValue')
    with connect_db() as conn:
        conn.execute(
            'UPDATE participants SET num_checkin = ?, time_checkin=? WHERE hashed_data = ?', (num_checkin, datetime.datetime.now(), hashed_data))
    return render_template('scan_qr.html', checkin_success='true')


@app.route('/scan', methods=['GET'])
def index():

    return render_template('scan_qr.html')


@app.route('/scan', methods=['POST'])
def scan_qr_code():
    hashed_data = request.data.decode('ascii')
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM participants WHERE hashed_data=?", (hashed_data,))
        columns = [column[0] for column in cursor.description]
        data = dict(zip(columns, cursor.fetchone()))
        print(data)
        if data:
            # Dữ liệu tồn tại, bạn có thể trả về nó cho template checkin.html
            return data
    return {'error': 'error'}


if __name__ == '__main__':
    print(os.environ.get('domain'))
    app.run(host='0.0.0.0')
