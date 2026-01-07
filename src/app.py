from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecreto'

# Configuración de Base de Datos Simulada (SQLite)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'sigr.db')

def init_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabla Usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    # Tabla Platos
    c.execute('''CREATE TABLE IF NOT EXISTS platos (id INTEGER PRIMARY KEY, nombre TEXT, precio REAL, categoria TEXT)''')
    # Tabla Pedidos
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY, mesa INTEGER, total REAL, estado TEXT)''')
    
    c.execute('SELECT count(*) FROM usuarios')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO usuarios (username, password, role) VALUES ('admin', '1234', 'admin')")
        c.execute("INSERT INTO usuarios (username, password, role) VALUES ('mesero', '1234', 'mesero')")
        c.execute("INSERT INTO platos (nombre, precio, categoria) VALUES ('Hamburguesa', 15.00, 'Principal')")
        c.execute("INSERT INTO platos (nombre, precio, categoria) VALUES ('Coca Cola', 3.00, 'Bebida')")
        conn.commit()
    conn.close()

# RUTAS 

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['user'] = user[1]
        session['role'] = user[3]
        return redirect(url_for('dashboard'))
    flash('Credenciales incorrectas')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM platos")
    platos = c.fetchall()
    c.execute("SELECT * FROM pedidos")
    pedidos = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', user=session['user'], role=session['role'], platos=platos, pedidos=pedidos)

@app.route('/add_order', methods=['POST'])
def add_order():
    mesa = request.form['mesa']
    total = request.form['total']
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO pedidos (mesa, total, estado) VALUES (?, ?, 'Pendiente')", (mesa, total))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)