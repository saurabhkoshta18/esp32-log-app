from flask import Flask, render_template, redirect, url_for, request, flash, send_file, jsonify
from extensions import db, login_manager
from flask_login import login_user, login_required, logout_user, current_user
from models import User, Log
from forms import LoginForm, RegisterForm
from datetime import datetime
import io
import csv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Mastitime@18'  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =============================
#           ROUTES
# =============================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(100).all()
    return render_template('dashboard.html', logs=logs)



@app.route('/download', methods=['GET', 'POST'])
@login_required
def download():
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if not start_date_str or not end_date_str:
            flash('Please provide both start and end dates.')
            return redirect(url_for('download'))

        # Convert string to datetime
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # include the whole end day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.')
            return redirect(url_for('download'))

        # Query logs between those datetime objects
        logs = Log.query.filter(Log.timestamp.between(start_date, end_date)).order_by(Log.timestamp.desc()).all()

        if not logs:
            flash('No logs found for the selected date range.')
            return redirect(url_for('download'))

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['UID', 'Action', 'Date', 'Time'])
        for log in logs:
            writer.writerow([
                log.uid,
                log.action,
                log.timestamp.strftime('%Y-%m-%d'),
                log.timestamp.strftime('%H:%M:%S')
            ])
        output.seek(0)
        return send_file(
            io.BytesIO(output.read().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='logs.csv'
        )

    return render_template('download.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# =============================
#         ESP32 Webhook
# =============================

@app.route('/log', methods=['POST'])
def receive_log():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    uid = data.get('UID')
    action = data.get('Action')
    date_str = data.get('Date')
    time_str = data.get('Time')

    if not uid or not action or not date_str or not time_str:
        return jsonify({'error': 'Missing UID, Action, Date, or Time'}), 400

    # Combine date and time into a datetime object
    try:
        timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400

    new_log = Log(uid=uid, action=action, timestamp=timestamp)
    db.session.add(new_log)
    db.session.commit()

    return jsonify({'message': 'Log received successfully'}), 200
# =============================
# Run (For local testing only)
# =============================

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
