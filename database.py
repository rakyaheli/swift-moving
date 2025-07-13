import sqlite3
from flask import g

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('swift_moving.db')
        db.row_factory = sqlite3.Row
    return db

def save_quote_request(name, email, phone, move_date, service_type, origin, destination, message):
    db = get_db()
    db.execute(
        'INSERT INTO quotes (name, email, phone, move_date, service_type, origin, destination, message) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (name, email, phone, move_date, service_type, origin, destination, message)
    )
    db.commit()

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()