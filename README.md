💳 MiniBank — A Simple Banking System with Streamlit UI
🏦 Overview

MiniBank is a lightweight banking system built with Python, Streamlit, and SQLite3.
It allows users to securely create accounts, log in, deposit, withdraw, transfer money, and view transaction history — all inside a modern web interface.

🚀 Features

🔐 Secure Login — Passwords are hashed using bcrypt.

💰 Deposit & Withdraw — Manage your account balance easily.

💱 Money Transfer — Transfer money securely between accounts.

🧾 Transaction History — View all your deposits, withdrawals, and transfers.

💳 Unique Card Numbers — Automatically generated 16-digit virtual cards.

🌐 Streamlit UI — Clean and user-friendly interface.

🪶 SQLite Database — No external setup needed, works locally.

🧠 Tech Stack

Frontend: Streamlit

Backend: Python

Database: SQLite3

Security: bcrypt (for password hashing)

⚙️ Installation

Clone the repository

git clone https://github.com/<pywizard2025-wq>/MiniBank.git
cd MiniBank


Create a virtual environment (optional but recommended)

python -m venv venv
source venv/bin/activate    # (For Mac/Linux)
venv\Scripts\activate       # (For Windows)


Install dependencies

pip install -r requirements.txt


Run the app

streamlit run bank_ui.py

📁 Project Structure
MiniBank/
│
├── bank_system.py       # Backend logic (database, authentication, transactions)
├── bank_ui.py           # Streamlit frontend interface
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation

💾 Database Info

The project automatically creates a local bank.db SQLite file.

You don’t need to upload it to GitHub — it’s generated when you first run the app.

🌍 Deployment

You can deploy your Streamlit app for free using:

Streamlit Community Cloud

Just upload your repo, set the main file as bank_ui.py, and you’re live 🚀

🎯 **Live App:** (https://minibank-system.streamlit.app)


🧑‍💻 Author

Shubh Srivastava
2nd year Engineering student 
Passionate about AI, data, and full-stack projects.

📜 License

This project is licensed under the MIT License — you’re free to use, modify, and share it with credit.
