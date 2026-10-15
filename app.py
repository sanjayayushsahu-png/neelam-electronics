import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render पर सही पाथ और डेटाबेस सेटिंग्स
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'neelam.db')
app.config['SECRET_KEY'] = 'neelam_electronics_secret_key_2026'

# सुनिश्चित करें कि static और uploads फोल्डर मौजूद हों
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# 1. उत्पाद (Product) डेटाबेस मॉडल
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True)

# 2. ग्राहक और रिवॉर्ड्स (Customer) डेटाबेस मॉडल
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    reward_points = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

# 1. ग्राहकों के लिए होम पेज
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# 2. एडमिन पैनल
@app.route('/admin')
def admin():
    products = Product.query.all()
    customers = Customer.query.all()
    edit_product = request.args.get('edit_product_id', type=int)
    edit_customer = request.args.get('edit_customer_id', type=int)
    
    prod_to_edit = Product.query.get(edit_product) if edit_product else None
    cust_to_edit = Customer.query.get(edit_customer) if edit_customer else None

    return render_template('admin.html', products=products, customers=customers, prod_to_edit=prod_to_edit, cust_to_edit=cust_to_edit)

# 3. उत्पाद जोड़ने या अपडेट करने का रूट
@app.route('/add_product', methods=['POST'])
def add_product():
    prod_id = request.form.get('product_id')
    name = request.form['name']
    price = float(request.form['price'])
    discount_price = float(request.form['discount_price']) if request.form['discount_price'] else None
    category = request.form['category']
    file = request.files.get('image')
    
    if prod_id:
        p = Product.query.get(prod_id)
        p.name = name
        p.price = price
        p.discount_price = discount_price
        p.category = category
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            p.image = filename
        flash('उत्पाद सफलतापूर्वक अपडेट कर दिया गया!', 'success')
    else:
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_prod = Product(name=name, price=price, discount_price=discount_price, image=filename, category=category)
            db.session.add(new_prod)
            flash('नया उत्पाद सफलतापूर्वक जोड़ा गया!', 'success')
        else:
            flash('कृपया उत्पाद की फोटो चुनें!', 'danger')
            
    db.session.commit()
    return redirect(url_for('admin'))

# 4. उत्पाद हटाने का रूट
@app.route('/delete_product/<int:id>')
def delete_product(id):
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('उत्पाद को हटा दिया गया है!', 'info')
    return redirect(url_for('admin'))

# 5. ग्राहक और रिवॉर्ड पॉइंट जोड़ने या अपडेट करने का रूट
@app.route('/add_customer', methods=['POST'])
def add_customer():
    cust_id = request.form.get('customer_id')
    name = request.form['name']
    phone = request.form['phone']
    points = int(request.form['points'])
    
    if cust_id:
        c = Customer.query.get(cust_id)
        c.name = name
        c.phone = phone
        c.reward_points = points
        flash('ग्राहक का विवरण अपडेट कर दिया गया!', 'success')
    else:
        existing_cust = Customer.query.filter_by(phone=phone).first()
        if existing_cust:
            existing_cust.reward_points += points
            flash(f'{name} के रिवॉर्ड पॉइंट्स अपडेट कर दिए गए हैं!', 'info')
        else:
            new_cust = Customer(name=name, phone=phone, reward_points=points)
            db.session.add(new_cust)
            flash('नया ग्राहक और रिवॉर्ड पॉइंट्स दर्ज किए गए!', 'success')
            
    db.session.commit()
    return redirect(url_for('admin'))

# 6. ग्राहक डेटा हटाने का रूट
@app.route('/delete_customer/<int:id>')
def delete_customer(id):
    c = Customer.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('ग्राहक का डेटा हटा दिया गया है!', 'info')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)