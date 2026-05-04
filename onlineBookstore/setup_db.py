# setup_db.py - Run this FIRST before starting the app
from app import app, db
from models import User, Book, Category, Order, OrderItem

def setup_database():
    with app.app_context():
        # Drop all existing tables and recreate them
        print("📦 Dropping existing tables...")
        db.drop_all()
        
        print("🏗️ Creating fresh tables...")
        db.create_all()
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Tables created: {tables}")
        
        # Create admin user
        print("\n👤 Creating admin user...")
        admin = User(
            username='admin',
            email='admin@bookstore.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create categories
        print("📚 Creating categories...")
        categories = [
            'Fiction', 'Non-Fiction', 'Science', 'Technology', 
            'History', 'Biography', 'Fantasy', 'Mystery'
        ]
        for cat_name in categories:
            category = Category(name=cat_name)
            db.session.add(category)
        
        # Create sample books
        print("📖 Creating sample books...")
        sample_books = [
            Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                category="Fiction",
                price=12.99,
                language="English",
                stock=10,
                description="A classic novel about the American dream in the Jazz Age.",
                available=True
            ),
            Book(
                title="To Kill a Mockingbird",
                author="Harper Lee",
                category="Fiction",
                price=14.99,
                language="English",
                stock=8,
                description="A story of racial injustice and loss of innocence.",
                available=True
            ),
            Book(
                title="1984",
                author="George Orwell",
                category="Fiction",
                price=11.99,
                language="English",
                stock=15,
                description="A dystopian social science fiction novel.",
                available=True
            ),
            Book(
                title="Python Crash Course",
                author="Eric Matthes",
                category="Technology",
                price=39.99,
                language="English",
                stock=5,
                description="A hands-on introduction to Python programming.",
                available=True
            ),
            Book(
                title="A Brief History of Time",
                author="Stephen Hawking",
                category="Science",
                price=18.99,
                language="English",
                stock=3,
                description="Exploring the universe's most profound questions.",
                available=True
            ),
            Book(
                title="Sapiens",
                author="Yuval Noah Harari",
                category="History",
                price=19.99,
                language="English",
                stock=12,
                description="A brief history of humankind.",
                available=True
            ),
        ]
        
        for book in sample_books:
            db.session.add(book)
        
        # Commit all changes
        db.session.commit()
        
        # Display summary
        print("\n" + "="*50)
        print("✅ DATABASE SETUP COMPLETE!")
        print("="*50)
        print(f"👤 Admin user: admin / admin123")
        print(f"📚 Categories: {Category.query.count()}")
        print(f"📖 Books: {Book.query.count()}")
        print(f"👥 Users: {User.query.count()}")
        print("="*50)
        print("\n🎉 You can now run: python app.py")
        print("🌐 Open http://127.0.0.1:5000 in your browser")

if __name__ == '__main__':
    setup_database()