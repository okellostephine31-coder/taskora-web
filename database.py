import sqlite3

DB_NAME = "taskora.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table 1: Errand Dispatches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            pickup TEXT,
            dropoff TEXT,
            customer_phone TEXT NOT NULL,
            total_fare INTEGER NOT NULL,
            runner_pay INTEGER NOT NULL,
            net_profit INTEGER NOT NULL,
            assigned_runner TEXT DEFAULT 'Unassigned',
            status TEXT DEFAULT 'Pending Rider 🟡'
        )
    ''')

    # Table 2: Registered Rider Fleet
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS riders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            zone TEXT NOT NULL,
            status TEXT DEFAULT 'Available'
        )
    ''')

    # Populate default Nairobi riders if empty
    cursor.execute('SELECT COUNT(*) FROM riders')
    if cursor.fetchone()[0] == 0:
        default_riders = [
            ("Brian Ochieng", "+254 712 345678", "Westlands / CBD"),
            ("Kevin Maina", "+254 722 987654", "Kilimani / Lavington"),
            ("Mercy Wangari", "+254 733 456789", "Upperhill / CBD"),
            ("David Kiprono", "+254 701 112233", "Karen / Gigiri")
        ]
        cursor.executemany('INSERT INTO riders (name, phone, zone) VALUES (?, ?, ?)', default_riders)

    conn.commit()
    conn.close()

def add_order(description, pickup, dropoff, phone, total_fare, runner_pay, net_profit):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (description, pickup, dropoff, customer_phone, total_fare, runner_pay, net_profit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (description, pickup, dropoff, phone, total_fare, runner_pay, net_profit))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_all_orders():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY id DESC')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def claim_order(order_id, runner_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE orders 
        SET assigned_runner = ?, status = 'In Progress / En Route 🟢' 
        WHERE id = ?
    ''', (runner_name, order_id))
    conn.commit()
    conn.close()

def get_ledger_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(net_profit), COUNT(id) FROM orders')
    profit, count = cursor.fetchone()
    conn.close()
    return profit or 210, count or 3

if __name__ == "__main__":
    init_db()
    print("Taskora SQLite database initialized successfully!")
