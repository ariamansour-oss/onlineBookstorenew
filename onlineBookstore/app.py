from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Book, Order, OrderItem, Category
from forms import LoginForm, RegistrationForm, BookForm, SearchForm, UserEditForm
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Helper function for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function for admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if user and user.role != 'admin':
            flash('Admin access required!', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    books = Book.query.filter_by(available=True).limit(12).all()
    categories = db.session.query(Category.name).distinct().all()
    return render_template('index.html', books=books, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='customer'  # Default role
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/books/search', methods=['GET', 'POST'])
def search_books():
    form = SearchForm()
    books = []
    search_performed = False
    
    # Populate category choices
    categories = db.session.query(Category.name).distinct().all()
    category_choices = [('', 'All Categories')] + [(c[0], c[0]) for c in categories]
    form.category.choices = category_choices
    
    if form.validate_on_submit():
        search_performed = True
        query = Book.query.filter_by(available=True)
        
        if form.title.data:
            query = query.filter(Book.title.contains(form.title.data))
        if form.author.data:
            query = query.filter(Book.author.contains(form.author.data))
        if form.category.data and form.category.data != '':
            query = query.filter(Book.category == form.category.data)
        if form.language.data:
            query = query.filter(Book.language.contains(form.language.data))
        if form.min_price.data:
            query = query.filter(Book.price >= form.min_price.data)
        if form.max_price.data:
            query = query.filter(Book.price <= form.max_price.data)
        
        books = query.all()
        
        if not books:
            flash('No books found matching your criteria.', 'info')
    
    return render_template('search_books.html', form=form, books=books, search_performed=search_performed)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

@app.route('/admin/add_book', methods=['GET', 'POST'])
@admin_required
def add_book():
    form = BookForm()
    
    # Populate category choices
    categories = Category.query.all()
    form.category.choices = [(c.name, c.name) for c in categories]
    
    if form.validate_on_submit():
        # Check if category exists, if not create it
        category = Category.query.filter_by(name=form.category.data).first()
        if not category:
            category = Category(name=form.category.data)
            db.session.add(category)
            db.session.flush()
        
        book = Book(
            title=form.title.data,
            author=form.author.data,
            category=form.category.data,
            price=form.price.data,
            language=form.language.data,
            stock=form.stock.data,
            description=form.description.data,
            available=form.available.data
        )
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_book.html', form=form)

@app.route('/admin/edit_book/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    
    categories = Category.query.all()
    form.category.choices = [(c.name, c.name) for c in categories]
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.category = form.category.data
        book.price = form.price.data
        book.language = form.language.data
        book.stock = form.stock.data
        book.description = form.description.data
        book.available = form.available.data
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('book_detail', book_id=book.id))
    
    return render_template('edit_book.html', form=form, book=book)

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    books = []
    total = 0
    
    for book_id, quantity in cart_items.items():
        book = Book.query.get(int(book_id))
        if book and book.available and book.stock >= quantity:
            subtotal = book.price * quantity
            total += subtotal
            books.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('cart.html', books=books, total=total)

@app.route('/add_to_cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.available or book.stock <= 0:
        flash('This book is not available!', 'danger')
        return redirect(url_for('book_detail', book_id=book_id))
    
    cart = session.get('cart', {})
    cart[str(book_id)] = cart.get(str(book_id), 0) + 1
    session['cart'] = cart
    
    flash(f'{book.title} added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:book_id>')
@login_required
def remove_from_cart(book_id):
    cart = session.get('cart', {})
    if str(book_id) in cart:
        del cart[str(book_id)]
        session['cart'] = cart
        flash('Item removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/update_cart/<int:book_id>', methods=['POST'])
@login_required
def update_cart(book_id):
    quantity = int(request.form.get('quantity', 0))
    cart = session.get('cart', {})
    
    if quantity <= 0:
        if str(book_id) in cart:
            del cart[str(book_id)]
    else:
        cart[str(book_id)] = quantity
    
    session['cart'] = cart
    flash('Cart updated!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    user = User.query.get(session['user_id'])
    total_amount = 0
    order_items = []
    
    # Verify stock and calculate total
    for book_id, quantity in cart_items.items():
        book = Book.query.get(int(book_id))
        if not book or not book.available or book.stock < quantity:
            flash(f'{book.title if book else "Book"} is out of stock or insufficient quantity!', 'danger')
            return redirect(url_for('cart'))
        total_amount += book.price * quantity
        order_items.append((book, quantity))
    
    # Create order
    order = Order(
        user_id=user.id,
        total_amount=total_amount,
        status='pending'
    )
    db.session.add(order)
    db.session.flush()
    
    # Create order items and update stock
    for book, quantity in order_items:
        order_item = OrderItem(
            order_id=order.id,
            book_id=book.id,
            quantity=quantity,
            price=book.price
        )
        db.session.add(order_item)
        book.stock -= quantity
    
    db.session.commit()
    
    # Clear cart
    session['cart'] = {}
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/orders')
@login_required
def orders():
    user = User.query.get(session['user_id'])
    if user.role == 'admin':
        orders = Order.query.order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_date.desc()).all()
    
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    user = User.query.get(session['user_id'])
    
    # Check authorization
    if user.role != 'admin' and order.user_id != user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('orders'))
    
    return render_template('order_detail.html', order=order)

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash('Order status updated!', 'success')
    
    return redirect(url_for('order_detail', order_id=order.id))

@app.route('/admin/manage_users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', form=form, user=user)

@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == session['user_id']:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_books = Book.query.count()
    total_users = User.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status != 'cancelled').scalar() or 0
    
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    low_stock_books = Book.query.filter(Book.stock < 10, Book.available == True).all()
    
    return render_template('admin_dashboard.html', 
                         total_books=total_books,
                         total_users=total_users,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         low_stock_books=low_stock_books)

if __name__ == '__main__':
    # Just run the app without creating tables (they should already exist)
    print("\n✓ Starting Flask application...")
    print("✓ Open http://127.0.0.1:5000 in your browser")
    print("✓ Login with: admin / admin123")
    print("="*50)
    app.run(debug=True, host='127.0.0.1', port=5000)