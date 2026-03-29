from flask import Flask, request, redirect, render_template_string, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# ---------- STYLE ----------
style = '''
<style>
body {
    font-family: Arial;
    margin: 0;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}
.navbar {
    background: rgba(0,0,0,0.7);
    padding: 15px;
    text-align: center;
}
.navbar a {
    color: #00c6ff;
    margin: 10px;
    text-decoration: none;
    font-weight: bold;
}
.container {
    width: 350px;
    margin: 80px auto;
    padding: 30px;
    background: rgba(0,0,0,0.6);
    border-radius: 15px;
    box-shadow: 0 0 20px black;
    text-align: center;
}
input {
    width: 90%;
    padding: 10px;
    margin: 10px;
    border-radius: 5px;
    border: none;
}
button {
    padding: 10px 20px;
    background: #00c6ff;
    border: none;
    border-radius: 5px;
    color: white;
    cursor: pointer;
}
button:hover {
    background: #0072ff;
}
.alert {
    padding: 10px;
    margin-bottom: 10px;
    background: #ff4d4d;
    border-radius: 5px;
}
.success {
    background: #28a745;
}
table {
    width: 100%;
    color: white;
}
</style>
'''

# ---------- NAVBAR ----------
navbar = '''
<div class="navbar">
<a href="/">Home</a>
<a href="/dashboard">Dashboard</a>
<a href="/profile">Profile</a>
<a href="/users">Users</a>
<a href="/logout">Logout</a>
</div>
'''

# ---------- HOME ----------
@app.route('/')
def home():
    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>Welcome to User System</h2>
    <a href="/register">Register</a><br><br>
    <a href="/login">Login</a>
    </div>
    ''')

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("All fields required")
        else:
            conn = get_db()
            try:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("Registered Successfully")
                return redirect('/login')
            except:
                flash("Username exists")
            finally:
                conn.close()

    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>Register</h2>
    {% for msg in get_flashed_messages() %}
        <div class="alert">{{msg}}</div>
    {% endfor %}
    <form method="post">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button>Register</button>
    </form>
    </div>
    ''')

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()

        if user:
            session['user'] = username
            flash("Login Successful")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")

    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>Login</h2>
    {% for msg in get_flashed_messages() %}
        <div class="alert">{{msg}}</div>
    {% endfor %}
    <form method="post">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button>Login</button>
    </form>
    </div>
    ''')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>Dashboard</h2>
    <p>Welcome {{user}}</p>
    <a href="/update">Update Password</a><br><br>
    <a href="/delete">Delete Account</a>
    </div>
    ''', user=session['user'])

# ---------- PROFILE ----------
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>Profile</h2>
    <p><b>Username:</b> {{user}}</p>
    </div>
    ''', user=session['user'])

# ---------- USERS LIST ----------
@app.route('/users')
def users():
    conn = get_db()
    data = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>All Users</h2>
    <table border="1">
        <tr><th>ID</th><th>Username</th></tr>
        {% for u in data %}
        <tr><td>{{u.id}}</td><td>{{u.username}}</td></tr>
        {% endfor %}
    </table>
    </div>
    ''', data=data)

# ---------- UPDATE ----------
@app.route('/update', methods=['GET', 'POST'])
def update():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        new_password = request.form['password']
        conn = get_db()
        conn.execute("UPDATE users SET password=? WHERE username=?", (new_password, session['user']))
        conn.commit()
        conn.close()
        flash("Password Updated")
        return redirect('/dashboard')

    return render_template_string(style + navbar + '''
    <div class="container">
    <h2>Update Password</h2>
    <form method="post">
        <input name="password" placeholder="New Password">
        <button>Update</button>
    </form>
    </div>
    ''')

# ---------- DELETE ----------
@app.route('/delete')
def delete():
    if 'user' in session:
        conn = get_db()
        conn.execute("DELETE FROM users WHERE username=?", (session['user'],))
        conn.commit()
        conn.close()
        session.pop('user')
        return redirect('/')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
