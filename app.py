from flask import Flask, render_template, redirect, url_for, request, flash,session, jsonify
from database import get_db, init_db
from werkzeug.security import generate_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = "my_strong_secret_key_12345"
init_db()

@app.route('/')
def home():
    return redirect(url_for('login_page'))


@app.route("/login.html", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()
        print(email, password, role)
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=? AND password=? AND role=?", (email, password, role))
            user = cur.fetchone()
            session['full_name'] = user['full_name']
            session['email'] = user['email']
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            if user is None:
                flash("No account found with this email!", "error")
            if user["role"] == "admin":
                flash("Login Successful!", "success")
                return redirect(url_for("admin_dashboard"))
            
            if user["role"] == "user":
                flash("Login Successful!", "success")
                return redirect(url_for("user_dashboard"))
        finally:
            conn.close()
    return render_template("login.html")



@app.route("/register.html", methods=["GET","POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()
        print(full_name, email, password, role)

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (full_name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (full_name, email, password, role))

            conn.commit()
            conn.close()

            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login_page"))

        except sqlite3.IntegrityError:
            flash("Email already exists. Try another one.", "error")
            
        finally:
            conn.close()
    return render_template("register.html")



@app.route('/user/dashboard', methods=['GET', 'POST'])
def user_dashboard():

    # User must be logged in
    if "user_id" not in session:
        flash("Please login first!", "error")
        return redirect(url_for("login_page"))

    # Handle POST (form submit)
    if request.method == 'POST':
        title = request.form['item_name']
        category = request.form['category']
        description = request.form['description']
        location = request.form['location']
        date = request.form['date']
        contact = request.form['contact']
        status = 'Pending'

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO items (user_id, title, category, description, location, date, contact, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], title, category, description, location, date, contact, status))

        conn.commit()
        conn.close()

        flash("Item reported successfully!", "success")
        return redirect(url_for("user_dashboard"))

    # ============ GET REQUEST (Dashboard Data) ============
    conn = get_db()
    cur = conn.cursor()

    # Fetch user items
    cur.execute("SELECT * FROM items WHERE user_id=?", (session['user_id'],))
    items = cur.fetchall()

    # Total user reports
    cur.execute("SELECT COUNT(*) FROM items WHERE user_id=?", (session['user_id'],))
    total_reports = cur.fetchone()[0]

    # Pending requests
    cur.execute("SELECT COUNT(*) FROM items WHERE user_id=? AND status='Pending'",
                (session['user_id'],))
    pending_count = cur.fetchone()[0]

    # Verified requests
    cur.execute("SELECT COUNT(*) FROM items WHERE user_id=? AND status='Verified'",
                (session['user_id'],))
    verified_count = cur.fetchone()[0]

    conn.close()

    # Pass values to HTML
    return render_template(
        'user_dashboard.html',
        items=items,
        total_reports=total_reports,
        pending_count=pending_count,
        verified_count=verified_count,
        user_name=session["full_name"]
    )

# ---------- ADMIN DASHBOARD PAGE ----------
@app.route('/admin/dashboard')
def admin_dashboard():
    # Only admin can access
    if "user_id" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("login_page"))

    conn = get_db()
    cur = conn.cursor()

    # Stats
    cur.execute("SELECT COUNT(*) FROM items")
    total_reports = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM items WHERE status='Pending'")
    pending_reports = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM items WHERE status='Verified'")
    verified_reports = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM items WHERE status='Rejected'")
    rejected_reports = cur.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_reports=total_reports,
        pending_reports=pending_reports,
        verified_reports=verified_reports,
        rejected_reports=rejected_reports,
        admin_name=session.get("full_name")
    )


# ---------- API: GET ITEMS BY STATUS ----------
@app.route('/admin/api/items')
def admin_get_items():
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    status = request.args.get("status", "Pending")  # Pending / Verified / Rejected / All

    conn = get_db()
    cur = conn.cursor()

    if status == "All":
        cur.execute("""
            SELECT items.*, users.full_name, users.email
            FROM items
            JOIN users ON items.user_id = users.user_id
            ORDER BY items.id DESC
        """)
    else:
        cur.execute("""
            SELECT items.*, users.full_name, users.email
            FROM items
            JOIN users ON items.user_id = users.user_id
            WHERE items.status = ?
            ORDER BY items.id DESC
        """, (status,))

    rows = cur.fetchall()
    conn.close()

    items = [dict(row) for row in rows]
    return jsonify(items)


# ---------- API: UPDATE ITEM STATUS (Verify / Reject) ----------
@app.route('/admin/api/items/<int:item_id>/status', methods=['POST'])
def admin_update_item_status(item_id):
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_status = data.get("status")

    if new_status not in ("Pending", "Verified", "Rejected"):
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE items SET status=? WHERE id=?", (new_status, item_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Status updated", "status": new_status})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
