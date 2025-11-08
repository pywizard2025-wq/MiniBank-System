import sqlite3
import bcrypt
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
            password BLOB NOT NULL,
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
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    card_number = generate_card_number()
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO accounts (name, email, password, card_number, pin, balance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, email, hashed, card_number, pin, 0.0, created_at))
            conn.commit()
        print(f"\n✅ Account created! Your card number: {card_number}")
        return True
    except sqlite3.IntegrityError:
        print("\n❌ Email already exists.")
        return False

def login(email, password):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts WHERE email=?", (email,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password.encode(), user[4]):
            return user
    return None

def deposit(user_id, amount):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id=?", (user_id,))
        balance = float(cur.fetchone()[0])
        new_balance = balance + float(amount)
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, user_id))
        cur.execute("INSERT INTO transactions (account_id, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                    (user_id, "deposit", amount, datetime.datetime.now()))
        conn.commit()
    print(f"✅ Deposited ₹{amount:.2f}. New balance: ₹{new_balance:.2f}")

def withdraw(user_id, amount, pin):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance, pin FROM accounts WHERE id=?", (user_id,))
        balance, stored_pin = cur.fetchone()
        balance = float(balance)
        if pin != stored_pin:
            print("❌ Invalid PIN.")
            return
        if amount > balance:
            print("❌ Insufficient funds.")
            return
        new_balance = balance - float(amount)
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, user_id))
        cur.execute("INSERT INTO transactions (account_id, type, amount, timestamp) VALUES (?, ?, ?, ?)",
                    (user_id, "withdraw", amount, datetime.datetime.now()))
        conn.commit()
    print(f"✅ Withdrawn ₹{amount:.2f}. New balance: ₹{new_balance:.2f}")

def transfer(sender_id, target_card, amount, pin):
    target_card = target_card.strip().replace(" ", "")
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        # Fetch target and sender details
        cur.execute("SELECT * FROM accounts WHERE card_number=?", (target_card,))
        target = cur.fetchone()
        cur.execute("SELECT balance, pin FROM accounts WHERE id=?", (sender_id,))
        result = cur.fetchone()

        if not result:
            print("❌ Sender not found.")
            return

        balance, stored_pin = result
        balance = float(balance)

        # Validate
        if pin != stored_pin:
            print("❌ Invalid PIN.")
            return
        if not target:
            print("❌ Target account not found.")
            return
        if amount > balance:
            print("❌ Insufficient funds.")
            return

        # Convert target balance to float and update both
        new_balance_sender = balance - float(amount)
        new_balance_receiver = float(target[6]) + float(amount)

        # Update both accounts
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance_sender, sender_id))
        cur.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance_receiver, target[0]))

        # Record both transactions
        now = datetime.datetime.now()
        cur.execute("INSERT INTO transactions (account_id, type, amount, target_account, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (sender_id, "transfer", amount, target_card, now))
        cur.execute("INSERT INTO transactions (account_id, type, amount, target_account, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (target[0], "received", amount, target_card, now))
        conn.commit()

    print(f"✅ Transferred ₹{amount:.2f} to card {target_card}. New balance: ₹{new_balance_sender:.2f}")

def check_balance(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE id=?", (user_id,))
        balance = float(cur.fetchone()[0])
    print(f"💰 Current Balance: ₹{balance:.2f}")

def transaction_history(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT type, amount, target_account, timestamp
            FROM transactions
            WHERE account_id=?
            ORDER BY id DESC
        """, (user_id,))
        txns = cur.fetchall()
    if txns:
        print("\n📜 Transaction History:")
        for t in txns:
            print(f"{t[3]} | {t[0].capitalize()} | ₹{t[1]:.2f} | Target: {t[2] or '-'}")
    else:
        print("No transactions yet.")

def show_all_users():
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, card_number, balance, created_at FROM accounts ORDER BY id")
        users = cur.fetchall()
    if users:
        print(f"\n📊 Total Users: {len(users)}\n")
        print(f"{'ID':<3} {'Name':<20} {'Email':<25} {'Card':<20} {'Balance':<10} {'Created At'}")
        print("-"*90)
        for u in users:
            print(f"{u[0]:<3} {u[1]:<20} {u[2]:<25} {u[3]:<20} ₹{u[4]:<10.2f} {u[5]}")
    else:
        print("No users in the system yet.")

def main():
    init_db()
    while True:
        print("\n--- MiniBank CLI ---")
        print("1. Login")
        print("2. Create Account")
        print("3. Show All Users")
        print("4. Exit")
        choice = input("Choose: ")
        if choice == "1":
            email = input("Enter Email: ")
            password = input("Enter Password: ")
            user = login(email, password)
            if user:
                print(f"\n✅ Welcome {user[1]}!")
                while True:
                    print("\n1. Deposit\n2. Withdraw\n3. Transfer\n4. Check Balance\n5. Transaction History\n6. Logout")
                    action = input("Choose: ")
                    if action == "1":
                        amt = float(input("Enter amount to deposit: "))
                        deposit(user[0], amt)
                    elif action == "2":
                        amt = float(input("Enter amount to withdraw: "))
                        pin = input("Enter your bank PIN: ")
                        withdraw(user[0], amt, pin)
                    elif action == "3":
                        target = input("Enter target card number: ")
                        amt = float(input("Enter amount to transfer: "))
                        pin = input("Enter your bank PIN: ")
                        transfer(user[0], target, amt, pin)
                    elif action == "4":
                        check_balance(user[0])
                    elif action == "5":
                        transaction_history(user[0])
                    elif action == "6":
                        print("Logging out...")
                        break
                    else:
                        print("❌ Invalid choice.")
            else:
                print("❌ Invalid email or password.")
        elif choice == "2":
            name = input("Enter Name: ")
            email = input("Enter Email: ")
            password = input("Enter Password: ")
            pin = input("Set your bank PIN (4 digits): ").strip()
            create_account(name, email, password, pin)
        elif choice == "3":
            show_all_users()
        elif choice == "4":
            print("Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
