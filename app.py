# In app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User
from routes import home, login, register, logout, student_management, course_management, grade_management, dashboard

def create_app(*args, **kwargs):
    app = Flask(__name__)

    # Load environment variables from the .env file
    load_dotenv()

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://chege:kanjurihigh@254@chege.mariadb.database.azure.com:3306/STUDENT_MANAGEMENT'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy after initializing app
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Set a secret key for session management
    app.secret_key = 'media'  # Replace with a secure method for production

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) if user_id else None

    # Specify the login view
    login_manager.login_view = 'login.login_page'

    # Configure Flask to serve static files from the `templates/static` directory
    app.static_url_path = '/static'
    app.static_folder = 'static'

    # Import Blueprints directly and register them
    app.register_blueprint(home)
    app.register_blueprint(login)
    app.register_blueprint(register)
    app.register_blueprint(logout)
    app.register_blueprint(student_management)
    app.register_blueprint(course_management)
    app.register_blueprint(grade_management)
    app.register_blueprint(dashboard)

    return app

# Entry point of the application
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
