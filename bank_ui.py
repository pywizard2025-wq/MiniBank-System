import streamlit as st
import bank_system as bank
import sqlite3
import pandas as pd

# Initialize the database once
bank.init_db()

st.set_page_config(page_title="MiniBank", page_icon="💳", layout="centered")

# --- SESSION MANAGEMENT ---
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None


# --- FRONT PAGE UI ---
def main_page():
    st.title("💳 Welcome to MiniBank")
    st.write("Your secure mini banking system with card generation and PIN protection.")

    choice = st.radio("Select an option:", ["Login", "Create Account"], horizontal=True)

    if choice == "Login":
        st.subheader("🔐 Login to your account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", use_container_width=True, key="login_btn"):
            user = bank.login(email, password)
            if user:
                st.session_state.user = user
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")

    elif choice == "Create Account":
        st.subheader("📝 Create a new account")
        name = st.text_input("Full Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        pin = st.text_input("Set 4-digit PIN", type="password", max_chars=4, key="reg_pin")

        if st.button("Create Account", use_container_width=True, key="create_btn"):
            if not (name and email and password and pin):
                st.warning("⚠️ Please fill all fields.")
            elif len(pin) != 4 or not pin.isdigit():
                st.warning("⚠️ PIN must be 4 digits.")
            else:
                created = bank.create_account(name, email, password, pin)
                if created:
                    st.success("✅ Account created successfully! You can now log in.")
                else:
                    st.error("❌ Email already exists.")


# --- TRANSACTION HISTORY UI ---
def show_transaction_history(user):
    st.subheader("📜 Transaction History")

    conn = sqlite3.connect("bank.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT type, amount, target_account, timestamp
        FROM transactions
        WHERE account_id = ?
        ORDER BY id DESC
    """, (user[0],))
    transactions = cur.fetchall()
    conn.close()

    if not transactions:
        st.info("No transactions yet.")
        return

    df = pd.DataFrame(transactions, columns=["Type", "Amount", "Target", "Timestamp"])

    # Apply color formatting
    def highlight_row(row):
        if row["Type"] in ["withdraw", "transfer"]:
            color = "background-color: #ffe6e6; color: #cc0000"  # red
        elif row["Type"] in ["deposit", "received"]:
            color = "background-color: #e6ffe6; color: #006600"  # green
        else:
            color = ""
        return [color] * len(row)

    st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)


# --- DASHBOARD ---
def dashboard():
    user = st.session_state.user
    st.title(f"🏦 Welcome, {user[1]}!")
    st.write(f"**Card Number:** {user[3]}")
    st.write(f"💰 **Balance:** ₹{float(user[6]):.2f}")

    action = st.radio("Choose an action:", ["Deposit", "Withdraw", "Transfer", "History", "Logout"], horizontal=True)

    if action == "Deposit":
        st.subheader("💸 Deposit Money")
        amt = st.number_input("Enter amount to deposit", min_value=1.0, step=1.0, key="deposit_amt")
        if st.button("Deposit", use_container_width=True, key="deposit_btn"):
            bank.deposit(user[0], amt)
            st.success(f"✅ ₹{amt:.2f} deposited successfully!")
            st.rerun()

    elif action == "Withdraw":
        st.subheader("🏧 Withdraw Money")
        amt = st.number_input("Enter amount to withdraw", min_value=1.0, step=1.0, key="withdraw_amt")
        pin = st.text_input("Enter your Bank PIN", type="password", max_chars=4, key="withdraw_pin")
        if st.button("Withdraw", use_container_width=True, key="withdraw_btn"):
            bank.withdraw(user[0], amt, pin)
            st.success(f"✅ ₹{amt:.2f} withdrawn successfully!")
            st.rerun()

    elif action == "Transfer":
        st.subheader("💱 Transfer Money")
        target = st.text_input("Enter target card number", key="transfer_card")
        amt = st.number_input("Enter amount to transfer", min_value=1.0, step=1.0, key="transfer_amt")
        pin = st.text_input("Enter your Bank PIN", type="password", max_chars=4, key="transfer_pin")
        if st.button("Transfer", use_container_width=True, key="transfer_btn"):
            bank.transfer(user[0], target, amt, pin)
            st.success(f"✅ ₹{amt:.2f} transferred successfully!")
            st.rerun()

    elif action == "History":
        show_transaction_history(user)

    elif action == "Logout":
        st.session_state.user = None
        st.session_state.page = "login"
        st.success("🔒 Logged out successfully.")
        st.rerun()


# --- PAGE CONTROLLER ---
if st.session_state.page == "login":
    main_page()
else:
    dashboard()
