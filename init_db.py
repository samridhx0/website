from app import app, db, User

with app.app_context():
    # Create all database tables
    db.create_all()

    # Create a default admin user if one doesn't exist
    if not User.query.filter_by(username='admin').first():
        print("Creating admin user...")
        user = User(username='admin', password='password') # IMPORTANT: Use a more secure password in a real application
        db.session.add(user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

print("Database initialized.")
