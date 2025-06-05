import sqlite3

# Connect to SQLite database (creates loans.db if it doesn't exist)
conn = sqlite3.connect("loans.db")
cursor = conn.cursor()

# Create loan offers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS loan_offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_name TEXT,
    interest_rate TEXT,
    tenure TEXT,
    max_loan_amount INTEGER
)
""")

# Insert sample loan offers
loan_data = [
    ("HDFC Bank", "10.5%", "5 years", 5000000),
    ("SBI", "9.8%", "7 years", 4000000),
    ("ICICI Bank", "11.2%", "6 years", 3500000),
    ("Axis Bank", "10.9%", "5 years", 4500000),
    ("Kotak Mahindra", "9.5%", "8 years", 4800000)
]

cursor.executemany("INSERT INTO loan_offers (bank_name, interest_rate, tenure, max_loan_amount) VALUES (?, ?, ?, ?)", loan_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("✅ Loan database created successfully!")
