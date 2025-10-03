from flask import Flask, app
from db_config import db
from routes import message_bp

def create_recipe():
    app=Flask(__name__)
    app.config['SECRET_KEY'] = 'not-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    db.init_app(app)
    app.register_blueprint(message_bp)
    with app.app_context():
        db.create_all()
    return app
if __name__ == '__main__':
    app=create_recipe()
    app.run(debug=True)