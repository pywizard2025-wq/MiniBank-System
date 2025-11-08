import sqlite3
from passlib.hash import bcrypt
import datetime
import random

DB_FILE = "bank.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            card_number TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pin TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            type TEXT,
            amount REAL,
            target_account TEXT,
            timestamp TEXT,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        """)
        conn.commit()

def generate_card_number():
    while True:
        number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM accounts WHERE card_number=?", (number,))
            if not cur.fetchone():
                return number

def create_account(name, email, password, pin):
    hashed = bcrypt.hash(password)
    card_number = generate_card_number()
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO accounts (name, email, password, card_number, pin, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed, card_number, pin, 0, created_at))
            conn.commit()
        return True, card_number
    except sqlite3.IntegrityError:
        return False, None

def login(email, password):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE email=?", (email,))
        user = cur.fetchone()
        if user and bcrypt.verify(password, user[4]):
            return user
    return None

def deposit(user_id, amount):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id=?", (user_id,))
        balance = cur.fetchone()[0]
        new_balance = balance + amount
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, user_id))
        cur.execute("INSERT INTO transactions (account_id, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                    (user_id, "deposit", amount, datetime.datetime.now()))
        conn.commit()
    return new_balance

def withdraw(user_id, amount, pin):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance, pin FROM accounts WHERE id=?", (user_id,))
        balance, stored_pin = cur.fetchone()
        if pin != stored_pin:
            return False, "Invalid PIN"
        if amount > balance:
            return False, "Insufficient funds"
        new_balance = balance - amount
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, user_id))
        cur.execute("INSERT INTO transactions (account_id, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                    (user_id, "withdraw", amount, datetime.datetime.now()))
        conn.commit()
    return True, new_balance

def transfer(sender_id, target_card, amount, pin):
    target_card = target_card.strip().replace(" ", "")
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE card_number=?", (target_card,))
        target = cur.fetchone()
        cur.execute("SELECT balance, pin FROM accounts WHERE id=?", (sender_id,))
        balance, stored_pin = cur.fetchone()
        if pin != stored_pin:
            return False, "Invalid PIN"
        if not target:
            return False, "Target account not found"
        if amount > balance:
            return False, "Insufficient funds"
        new_balance_sender = balance - amount
        new_balance_receiver = float(target[6]) + amount
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance_sender, sender_id))
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance_receiver, target[0]))
        cur.execute("INSERT INTO transactions (account_id, type, amount, target_account, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (sender_id, "transfer", amount, target_card, datetime.datetime.now()))
        cur.execute("INSERT INTO transactions (account_id, type, amount, target_account, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (target[0], "received", amount, target_card, datetime.datetime.now()))
        conn.commit()
    return True, new_balance_sender

def check_balance(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id=?", (user_id,))
        return cur.fetchone()[0]

def transaction_history(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT type, amount, target_account, timestamp
            FROM transactions
            WHERE account_id=?
            ORDER BY id DESC
        """, (user_id,))
        return cur.fetchall()

def show_all_users():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, card_number, balance, created_at FROM accounts ORDER BY id")
        return cur.fetchall()
