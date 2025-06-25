from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'reservations.db')


def init_db():
    """Create the reservation table if it does not exist."""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS reservation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                date TEXT,
                party_size INTEGER,
                notes TEXT
            )
            """
        )
        conn.commit()


@app.before_first_request
def setup():
    init_db()


def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute(query, args)
        rv = c.fetchall()
        conn.commit()
        return (rv[0] if rv else None) if one else rv


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reserve', methods=['POST'])
def reserve():
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    party_size = request.form.get('party_size', 1)
    notes = request.form.get('notes', '')
    query_db(
        'INSERT INTO reservation (name, email, date, party_size, notes) VALUES (?, ?, ?, ?, ?)',
        (name, email, date, party_size, notes),
    )
    return redirect(url_for('index'))


@app.route('/admin')
def admin():
    reservations = query_db(
        'SELECT id, name, email, date, party_size, notes FROM reservation ORDER BY date'
    )
    return render_template('admin.html', reservations=reservations)


@app.route('/delete/<int:res_id>', methods=['POST'])
def delete(res_id):
    query_db('DELETE FROM reservation WHERE id=?', (res_id,))
    return redirect(url_for('admin'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
