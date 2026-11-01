from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
from database import init_db, add_order, get_all_orders, claim_order, get_ledger_stats

app = Flask(__name__)

# Ensure database is initialized on startup
init_db()

# Mock Rider Fleet for dropdown
RUNNER_FLEET = [
    {"name": "Brian Ochieng", "zone": "Westlands / CBD"},
    {"name": "Kevin Maina", "zone": "Kilimani / Lavington"},
    {"name": "Mercy Wangari", "zone": "Upperhill / CBD"},
    {"name": "David Kiprono", "zone": "Karen / Gigiri"}
]

@app.route("/", methods=['GET', 'POST'])
def customer_portal():
    response_msg = ""
    if request.method == 'POST':
        description = request.form.get('message', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if description and phone:
            # Standard pricing: KES 100 base + 50/km (mock 5km standard run)
            distance = 5
            total_fare = 100 + (50 * distance)
            runner_pay = int(total_fare * 0.8)
            net_profit = total_fare - runner_pay
            
            # Save to SQLite Database
            add_order(description, "Westlands", "CBD", phone, total_fare, runner_pay, net_profit)
            response_msg = f"🎯 Errand Dispatched! Total Fare: KES {total_fare}. M-Pesa STK push sent to {phone}."

    profit, count = get_ledger_stats()
    orders = get_all_orders()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Taskora - Customer Portal</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            h1 { color: #FF4500; margin-top: 0; }
            .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
            .nav-tabs a { padding: 10px 20px; text-decoration: none; background: #ddd; color: #333; font-weight: bold; border-radius: 4px; }
            .nav-tabs a.active { background: #FF4500; color: white; }
            textarea, input { width: 100%; padding: 10px; margin-top: 8px; margin-bottom: 15px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }
            button.action-btn { background: #FF4500; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; }
            .card { background: #f8f9fa; border-left: 4px solid #FF4500; padding: 15px; margin-bottom: 12px; border-radius: 4px; }
            .ledger-box { background: #fff3e6; padding: 15px; border-radius: 6px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ Taskora Nairobi</h1>
            <p>Autonomous Errand & Logistics Platform (SQLite Persistent Backend)</p>

            <div class="nav-tabs">
                <a href="/" class="active">Customer Portal</a>
                <a href="/rider">Rider Fleet Portal</a>
            </div>

            <h2>🚀 Request an Errand</h2>
            <form method="POST">
                <label>Errand Description:</label>
                <textarea name="message" rows="3" placeholder="e.g., Deliver signed contracts from Westlands to CBD" required></textarea>
                
                <label>Safaricom Phone Number (for M-Pesa STK Push):</label>
                <input type="text" name="phone" placeholder="e.g., 0712345678" required>

                <button type="submit" class="action-btn">Dispatch Errand & Trigger M-Pesa</button>
            </form>

            {% if response_msg %}
                <div style="margin-top: 20px; padding: 15px; background: #e9ffe9; border-left: 5px solid #25D366;">
                    {{ response_msg }}
                </div>
            {% endif %}

            <div class="ledger-box">
                <h3>📊 Taskora Profit & System Ledger (Persistent DB)</h3>
                <p>System Status: <b style="color: green;">ALIVE (SQLite Active)</b></p>
                <p>Net Profit Balance: <b>KES {{ profit }}</b></p>
                <p>Total Dispatches: <b>{{ count }}</b></p>
            </div>
        </div>
    </body>
    </html>
    ''', response_msg=response_msg, profit=profit, count=count)

@app.route("/rider", methods=['GET', 'POST'])
def rider_portal():
    msg = ""
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        runner_name = request.form.get('runner_name')
        if order_id and runner_name:
            claim_order(int(order_id), runner_name)
            msg = f"✅ Successfully claimed Errand #{order_id}!"

    orders = get_all_orders()
    profit, count = get_ledger_stats()

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Taskora - Rider Portal</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            h1 { color: #25D366; margin-top: 0; }
            .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
            .nav-tabs a { padding: 10px 20px; text-decoration: none; background: #ddd; color: #333; font-weight: bold; border-radius: 4px; }
            .nav-tabs a.active { background: #25D366; color: white; }
            .card { background: #f8f9fa; border: 1px solid #ddd; padding: 15px; margin-bottom: 12px; border-radius: 6px; }
            select { padding: 6px; margin-right: 10px; }
            button.claim-btn { background: #25D366; color: white; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛵 Taskora Rider Dashboard</h1>
            <p>Active Nairobi couriers: claim orders and track your 80% payout split.</p>

            <div class="nav-tabs">
                <a href="/">Customer Portal</a>
                <a href="/rider" class="active">Rider Fleet Portal</a>
            </div>

            {% if msg %}
                <div style="margin-bottom: 15px; padding: 12px; background: #e9ffe9; border-left: 5px solid #25D366;">
                    {{ msg }}
                </div>
            {% endif %}

            <h3>📦 Available & Active Errand Queue (From SQLite)</h3>
            {% if orders %}
                {% for order in orders %}
                <div class="card">
                    <b>Errand #{{ order.id }}</b> [{{ order.timestamp }}]<br>
                    📍 <b>Request:</b> {{ order.description }}<br>
                    💰 <b>Your Payout (80%):</b> KES {{ order.runner_pay }} (Total: KES {{ order.total_fare }})<br>
                    👤 <b>Assigned Rider:</b> {{ order.assigned_runner }}<br>
                    📊 <b>Status:</b> <span style="color: {% if 'In Progress' in order.status %}green{% else %}orange{% endif %};">{{ order.status }}</span><br><br>
                    
                    {% if 'Pending' in order.status %}
                    <form method="POST">
                        <input type="hidden" name="order_id" value="{{ order.id }}">
                        <select name="runner_name">
                            {% for r in fleet %}
                            <option value="{{ r.name }}">{{ r.name }} ({{ r.zone }})</option>
                            {% endfor %}
                        </select>
                        <button type="submit" class="claim-btn">Accept Errand 🛵</button>
                    </form>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #888;">No orders in the database yet. Submit one on the Customer Portal!</p>
            {% endif %}
        </div>
    </body>
    </html>
    ''', orders=orders, fleet=RUNNER_FLEET, msg=msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
