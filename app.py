import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-secret-key-you-should-change')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' # With instance_relative_config, this goes to instance/blog.db

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# --- Models ---

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Database Initialization ---
def init_database():
    """Create database tables and a default user if they don't exist."""
    from sqlalchemy import inspect

    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("user"):
            print("First run detected: Initializing the database...")
            # Ensure the instance folder exists
            try:
                os.makedirs(app.instance_path)
            except OSError:
                pass
            db.create_all()
            # Create a default admin user
            admin_user = User(username='admin', password='password')
            db.session.add(admin_user)
            db.session.commit()
            print("Database initialized.")
        else:
            print("Database already initialized.")

# Run the initialization check when the app starts
init_database()


# --- Routes ---

@app.route('/')
def index():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']: # In a real app, use hashed passwords!
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('admin.html', posts=posts)

@app.route('/admin/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('admin'))
    return render_template('new_post.html')

@app.route("/admin/edit/<int:post_id>", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('admin'))
    return render_template('edit_post.html', post=post)

@app.route("/admin/delete/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
