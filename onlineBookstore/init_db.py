# init_db.py
from app import app, db
from models import User, Book, Order, OrderItem, Category

def init_database():
    with app.app_context():
        # Drop all existing tables (clean slate)
        print("Dropping all existing tables...")
        db.drop_all()
        
        # Create all tables fresh
        print("Creating all tables...")
        db.create_all()
        print("✓ Tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Tables in database: {tables}")
        
        # Create admin user
        print("\nCreating admin user...")
        admin = User(
            username='admin',
            email='admin@bookstore.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Add categories
        print("Adding categories...")
        categories = ['Fiction', 'Non-Fiction', 'Science', 'Technology', 'History', 'Biography', 'Fantasy', 'Mystery']
        for cat_name in categories:
            category = Category(name=cat_name)
            db.session.add(category)
        
        # Add sample books
        print("Adding sample books...")
        sample_books = [
            Book(
                title="The Great Gatsby", 
                author="F. Scott Fitzgerald", 
                category="Fiction", 
                price=12.99, 
                language="English", 
                stock=10, 
                description="A classic novel about the American dream",
                available=True
            ),
            Book(
                title="To Kill a Mockingbird", 
                author="Harper Lee", 
                category="Fiction", 
                price=14.99, 
                language="English", 
                stock=8, 
                description="A story of racial injustice and the loss of innocence",
                available=True
            ),
            Book(
                title="1984", 
                author="George Orwell", 
                category="Fiction", 
                price=11.99, 
                language="English", 
                stock=15, 
                description="Dystopian social science fiction and cautionary tale",
                available=True
            ),
            Book(
                title="Python Crash Course", 
                author="Eric Matthes", 
                category="Technology", 
                price=29.99, 
                language="English", 
                stock=7, 
                description="A hands-on, project-based introduction to Python programming",
                available=True
            ),
            Book(
                title="A Brief History of Time", 
                author="Stephen Hawking", 
                category="Science", 
                price=18.99, 
                language="English", 
                stock=5, 
                description="Cosmology for everyone from the famous physicist",
                available=True
            ),
            Book(
                title="Sapiens", 
                author="Yuval Noah Harari", 
                category="History", 
                price=19.99, 
                language="English", 
                stock=12, 
                description="A brief history of humankind",
                available=True
            ),
        ]
        for book in sample_books:
            db.session.add(book)
        
        # Commit all changes
        db.session.commit()
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*50)
        print(f"✓ Admin user created (username: admin, password: admin123)")
        print(f"✓ {len(categories)} categories added")
        print(f"✓ {len(sample_books)} sample books added")
        print(f"✓ Total users: {User.query.count()}")
        print(f"✓ Total categories: {Category.query.count()}")
        print(f"✓ Total books: {Book.query.count()}")
        print("="*50)
        print("\nYou can now run: python app.py")
        print("Then login with: admin / admin123")

if __name__ == '__main__':
    init_database()