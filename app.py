from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import razorpay
import hmac
import hashlib
import json
import io
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, redirect, url_for
from flask import Flask, render_template, request, jsonify, session, send_file, abort
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from dotenv import load_dotenv
import os
import razorpay



RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    print("❌ Razorpay keys not loaded. Check .env file")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "siddhi_secret_key")

ORDERS = {}
# ================= MYSQL CONFIG =================
app.config['MYSQL_HOST'] = os.getenv("DB_HOST")
app.config['MYSQL_USER'] = os.getenv("DB_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("DB_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("DB_NAME")
app.config['MYSQL_PORT'] = int(os.getenv("DB_PORT", 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Upload Folder
# Upload Folder
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # your XAMPP password (usually empty)
        database="siddhi_diy_store"   # 🔥 IMPORTANT LINE
	)
    
def check_connection(conn, redirect_url='/'):
    if conn is None:
        flash("Database Connection Failed")
        return redirect(redirect_url)
    return None
# ================= HOME =================
@app.route('/')
def home():
    return render_template('index.html')

# ================= WISHLIST PAGE =================

@app.route('/wishlist')
def wishlist():

    return render_template('wishlist.html')

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")



@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route('/cart')
def cart():

    if 'user_id' not in session:
        flash('Please login to view your cart')
        return redirect('/login')

    user_id = session['user_id']

    conn = get_db_connection()
    error = check_connection(conn, '/')
    if error:
        return error

    cursor = conn.cursor(buffered=True)

    cursor.execute("""
        SELECT c.id, p.id AS product_id, p.name, p.category, p.price, p.image, p.description, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (user_id,))

    cart_items = cursor.fetchall()

    cursor.close()
    conn.close()

    cart_total = sum(float(item[4]) * int(item[7]) for item in cart_items)

    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total)


@app.route('/remove-from-cart/<int:cart_id>')
def remove_from_cart(cart_id):

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM cart WHERE id=%s AND user_id=%s", (cart_id, session['user_id']))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Item Removed From Cart')
    return redirect('/cart')


@app.route('/update-cart-qty/<int:cart_id>/<action>')
def update_cart_qty(cart_id, action):

    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    cursor.execute("SELECT quantity FROM cart WHERE id=%s AND user_id=%s", (cart_id, session['user_id']))
    row = cursor.fetchone()

    if row:
        qty = row[0]

        if action == 'increase':
            qty += 1
        elif action == 'decrease' and qty > 1:
            qty -= 1

        cursor.execute("UPDATE cart SET quantity=%s WHERE id=%s", (qty, cart_id))
        conn.commit()

    cursor.close()
    conn.close()

    return redirect('/cart')
# ================= PRODUCTS =================
@app.route('/products')
def products():

    conn = get_db_connection()

    error = check_connection(conn, '/')
    if error:
        return error

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('products.html', products=products)
# ================= PRODUCT DETAIL =================
@app.route('/product/<int:id>')
def product_detail(id):

    conn = get_db_connection()

    error = check_connection(conn, '/products')
    if error:
        return error

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))

    product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('product_detail.html', product=product)

# ================= UPDATE PRODUCT =================
@app.route('/update-product/<int:id>', methods=['POST'])
def update_product(id):

    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    description = request.form['description']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name=%s,
            category=%s,
            price=%s,
            description=%s
        WHERE id=%s
    """, (
        name,
        category,
        price,
        description,
        id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/admin-products')
# ================= profile =================
@app.route('/profile')
def profile():

    if 'user_id' not in session:
        flash('Please login to view your account')
        return redirect('/login')

    user_id = session['user_id']

    conn = get_db_connection()
    error = check_connection(conn, '/profile')
    if error:
        return error

    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY id DESC", (user_id,))
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('profile.html', user=user, orders=orders)
# ================= EDIT PRODUCT =================
@app.route('/edit-product/<int:id>')
def edit_product(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE id=%s",
        (id,)
    )

    product = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        'edit-product.html',
        product=product
    )
# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # ADMIN LOGIN
        if email == "admin" and password == "admin123":

            session['admin'] = True

            flash('Admin Login Successful')

            return redirect('/admin')

        conn = get_db_connection()

        error = check_connection(conn, '/login')
        if error:
            return error

        cursor = conn.cursor(buffered=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:

            session['user_id'] = user[0]
            session['user_name'] = user[1]

            flash('Login Successful')

            return redirect('/')

        else:

            flash('Invalid Credentials')

            return redirect('/login')

    return render_template('login.html')
       # ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        conn = None
        cursor = None

        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            conn = get_db_connection()

            if conn is None:
                return "Database Connection Failed"

            cursor = conn.cursor(buffered=True)

            # check duplicate email
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            existing = cursor.fetchone()

            if existing:
                flash("Email already registered")
                return redirect('/register')

            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
                (name, email, password)
            )

            conn.commit()

            print("✅ USER REGISTERED SUCCESSFULLY")

            flash('Registration Successful')
            return redirect('/login')

        except Exception as e:
            print("❌ REGISTER ERROR:", str(e))
            return f"Register Failed: {str(e)}", 500

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
                print("🔒 REGISTER DB CLOSED")

    return render_template('register.html')
# ================= LOGOUT =================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/welcome')

# ================= ADD TO CART =================

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):

    print("===== ADD TO CART STARTED =====")

    # CHECK LOGIN
    if 'user_id' not in session:

        print("❌ USER NOT LOGGED IN")

        return redirect('/login')

    user_id = session['user_id']

    print("✅ USER ID:", user_id)
    print("✅ PRODUCT ID:", product_id)

    # DATABASE CONNECTION
    conn = get_db_connection()

    if conn is None:

        print("❌ DATABASE FAILED")

        return "DATABASE CONNECTION FAILED"

    try:

        cursor = conn.cursor()

        print("✅ DATABASE CONNECTED")

        # CHECK EXISTING PRODUCT
        cursor.execute(
            "SELECT * FROM cart WHERE user_id=%s AND product_id=%s",
            (user_id, product_id)
        )

        existing = cursor.fetchone()

        print("EXISTING:", existing)

        # UPDATE OR INSERT
        if existing:

            cursor.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s",
                (user_id, product_id)
            )

            print("✅ CART UPDATED")

        else:

            cursor.execute(
                "INSERT INTO cart(user_id, product_id, quantity) VALUES(%s,%s,%s)",
                (user_id, product_id, 1)
            )

            print("✅ NEW ITEM INSERTED")

        conn.commit()

        print("✅ COMMIT SUCCESSFUL")

        cursor.close()
        conn.close()

        flash('Added To Cart Successfully')

        return redirect('/products')

    except Exception as e:

        print("❌ ERROR:", str(e))

        return f"ADD TO CART ERROR: {str(e)}"

# ================= ABOUT =================
@app.route('/about')
def about():
    return render_template('about.html')

# ================= CONTACT =================
@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO contacts(name,email,message) VALUES(%s,%s,%s)",
            (name, email, message)
        )

        conn.commit()

        flash('Message Sent Successfully')

    return render_template('contact.html')

# ================= CUSTOM ORDER =================
@app.route('/custom-order', methods=['GET', 'POST'])
def custom_order():

    if request.method == 'POST':

        customer_name = request.form['customer_name']
        phone = request.form['phone']
        details = request.form['details']

        image = request.files['image']

        filename = secure_filename(image.filename)

        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        image.save(upload_path)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO custom_orders(customer_name,phone,details,image) VALUES(%s,%s,%s,%s)",
            (customer_name, phone, details, filename)
        )

        conn.commit()

        flash('Custom Order Submitted Successfully')

        return redirect('/')

    return render_template('custom_order.html')

# ================= ADMIN DASHBOARD =================

@app.route('/admin')
def admin_dashboard():

    if 'admin' not in session:

        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()

    return render_template(
        'admin_dashboard.html',
        products=products,
        orders=orders,
        contacts=contacts
    )
# ================= ADD PRODUCT =================
@app.route('/add-product', methods=['POST'])
def add_product():

    name = request.form['name']
    category = request.form['category']
    price = request.form['price']
    description = request.form['description']

    image = request.files['image']

    filename = secure_filename(image.filename)

    image_path = os.path.join('static/images', filename)
    image.save(image_path)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO products(name,category,price,description,image) VALUES(%s,%s,%s,%s,%s)",
        (name, category, price, description, filename)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash('Product Added Successfully')

    return redirect('/admin-products')
# ================= DELETE PRODUCT =================
@app.route('/delete-product/<int:id>')
def delete_product(id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id=%s", (id,))

    conn.commit()

    flash('Product Deleted Successfully')

    return redirect('/admin')
# ================= ADMIN LOGIN =================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # CHANGE THESE VALUES
        admin_username = "admin"
        admin_password = "admin123"

        if username == admin_username and password == admin_password:

            session['admin'] = True

            flash('Admin Login Successful')

            return redirect('/admin')

        else:

            flash('Invalid Admin Credentials')

            return redirect('/admin-login')

    return render_template('admin_login.html')
# ================= ADMIN PRODUCTS =================

@app.route('/admin-products')
def admin_products():

    if 'admin' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template(
        'admin-products.html',
        products=products
    )


# ================= ADMIN ORDERS =================

@app.route('/admin-orders')
def admin_orders():

    if 'admin' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders ORDER BY id DESC")

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin-orders.html',
        orders=orders
    )


# ================= ADMIN CONTACTS =================

@app.route('/admin-contacts')
def admin_contacts():

    if 'admin' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contacts")

    contacts = cursor.fetchall()

    return render_template(
        'admin-contacts.html',
        contacts=contacts
    )
@app.route('/testdb')
def testdb():

    conn = get_db_connection()

    if conn is None:
        return "❌ DATABASE CONNECTION FAILED"

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return f"✅ DATABASE CONNECTED PERFECTLY {result}"

    except Exception as e:

        return f"❌ TESTDB ERROR: {str(e)}"

@app.route('/api/create-order', methods=['POST'])
def create_order():

    try:
        data = request.get_json(force=True)
        print("DATA:", data)

        amount = int(data.get("amount", 0))

        if amount <= 0:
            return {"error": "Invalid amount"}, 400

        if amount < 100:
            return {"error": "Minimum amount is 100 paise"}, 400

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        print("ORDER CREATED:", order)

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": RAZORPAY_KEY_ID
        }

    except Exception as e:
        print("ORDER ERROR:", str(e))
        return {"error": str(e)}, 500


@app.route('/debug-razorpay')
def debug():
    return {
        "key_id": RAZORPAY_KEY_ID,
        "key_secret_loaded": bool(RAZORPAY_KEY_SECRET)
     }


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():

    if 'user_id' not in session:
        flash('Please login to checkout')
        return redirect('/login')

    if request.method == 'POST':

        session['fullname'] = request.form['fullname']
        session['phone'] = request.form['phone']
        session['address'] = request.form['address']
        session['total'] = request.form['total']

        return redirect('/review')

    user_id = session['user_id']

    conn = get_db_connection()
    error = check_connection(conn, '/cart')
    if error:
        return error

    cursor = conn.cursor(buffered=True)

    cursor.execute("""
        SELECT p.id, p.name, p.price, p.image, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id=%s
    """, (user_id,))

    cart_items = cursor.fetchall()

    cursor.close()
    conn.close()

    cart_total = sum(item[2] * item[4] for item in cart_items)

    return render_template('checkout.html', cart_total=cart_total)

    return render_template('checkout.html')
@app.route('/review')
def review():

    if 'total' not in session:
        return redirect('/checkout')

    return render_template(
        'review.html',
        fullname=session['fullname'],
        phone=session['phone'],
        address=session['address'],
        total=session['total']
    )
    

@app.route('/payment')
def payment():

    if 'total' not in session:
        return redirect('/checkout')

    return render_template('payment.html', total=session['total'])


@app.route("/api/verify-payment", methods=["POST"])
def verify_payment():
    data = request.get_json()

    payment_verified = True  # replace with real verification result

    if not payment_verified:
        return jsonify({"status": "failed"})

    if 'user_id' not in session:
        return jsonify({"status": "failed", "error": "Not logged in"}), 401

    user_id = session['user_id']
    fullname = data.get("fullname", "Customer")
    phone = data.get("phone", "")
    address = data.get("address", "")
    total = data.get("total", "0")
    payment_id = data.get("razorpay_payment_id", "N/A")
    razorpay_order_id = data.get("razorpay_order_id", "N/A")

    order_id = "ORD-" + uuid.uuid4().hex[:8].upper()
    order_date = datetime.now()
    shipping_date = order_date + timedelta(days=5)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO orders
            (user_id, invoice_no, payment_id, razorpay_order_id, fullname, phone, address, total, delivery_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id, order_id, payment_id, razorpay_order_id,
        fullname, phone, address, total,
        shipping_date.date(), "Processing"
    ))

    conn.commit()
    cursor.close()
    conn.close()

    # Keep this for your existing /success and /invoice routes, which
    # currently read from the in-memory ORDERS dict
    order = {
        "order_id": order_id,
        "fullname": fullname,
        "phone": phone,
        "address": address,
        "total": total,
        "payment_id": payment_id,
        "order_date": order_date.strftime("%d %B %Y"),
        "shipping_date": shipping_date.strftime("%d %B %Y"),
    }
    ORDERS[order_id] = order
    session["last_order_id"] = order_id

    return jsonify({"status": "payment_verified", "order_id": order_id})
 
@app.route("/success")
def success():
    order_id = request.args.get("order_id") or session.get("last_order_id")
    order = ORDERS.get(order_id)
 
    if not order:
        abort(404, "Order not found")
 
    return render_template("success.html", order=order)
 
 
@app.route("/invoice/<order_id>/download")
def download_invoice(order_id):
    order = ORDERS.get(order_id)
    if not order:
        abort(404, "Order not found")
 
    buffer = generate_invoice_pdf(order)
 
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Invoice-{order['order_id']}.pdf",
        mimetype="application/pdf",
    )
 
 
def generate_invoice_pdf(order):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=25 * mm, bottomMargin=25 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )
 
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"],
        fontSize=22, textColor=colors.HexColor("#4a2e3a"), spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "SubStyle", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#8a8a8a"),
    )
    section_style = ParagraphStyle(
        "SectionStyle", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#4a2e3a"), spaceBefore=14, spaceAfter=8,
    )
 
    elements = []
 
    elements.append(Paragraph("Sivika Studio", title_style))
    elements.append(Paragraph("Sivika Art Studio &mdash; Handmade with Love", sub_style))
    elements.append(Spacer(1, 18))
 
    elements.append(Paragraph("TAX INVOICE", section_style))
 
    meta_table = Table(
        [
            ["Order ID", order["order_id"], "Order Date", order["order_date"]],
            ["Payment ID", order["payment_id"], "Expected Shipping", order["shipping_date"]],
        ],
        colWidths=[80, 140, 90, 140],
    )
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#8a8a8a")),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#8a8a8a")),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 16))
 
    elements.append(Paragraph("Billing & Shipping Details", section_style))
    ship_table = Table(
        [
            ["Name", order["fullname"]],
            ["Phone", order["phone"]],
            ["Address", order["address"]],
        ],
        colWidths=[80, 380],
    )
    ship_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#8a8a8a")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(ship_table)
    elements.append(Spacer(1, 16))
 
    elements.append(Paragraph("Payment Summary", section_style))
    summary_table = Table(
        [
            ["Description", "Amount (₹)"],
            ["Total Amount", order["total"]],
            ["Shipping", "Free"],
            ["Handling Fee", "0"],
            ["Total Paid", order["total"]],
        ],
        colWidths=[330, 130],
    )
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cf8fad")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.HexColor("#4a2e3a")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e8d5dd")),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 24))
 
    elements.append(Paragraph(
        "Thank you for shopping with Sivika Studio. For any queries regarding "
        "this order, please reach out with your Order ID.",
        sub_style,
    ))
 
    doc.build(elements)
    buffer.seek(0)
    return buffer
# ================= UPDATE ACCOUNT CREDENTIALS =================
@app.route('/update_account', methods=['POST'])
def update_account():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')

    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    conn = get_db_connection()
    error = check_connection(conn, '/profile')
    if error:
        return error

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET name=%s, email=%s, phone=%s, address=%s
        WHERE id=%s
    """, (name, email, phone, address, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash('Account details updated successfully')
    return redirect(url_for('profile'))
# ================= RUN APP =================
if __name__ == '__main__':
    app.run(debug=True)