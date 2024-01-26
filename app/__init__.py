from flask import Flask, render_template
from config import Config
from app.extensions import db
from app.models.stock import Stock
from app.models.category import Category
from app.models.staff import Staff

# app = Flask(__name__)

# import app.views

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #Initialize Flask extensions here
    from app.extensions import init_extensions
    init_extensions(app)
 

    
    # Register blueprints her

    from app.category import bp as category_bp
    app.register_blueprint(category_bp,url_prefix='/category')

    from app.stock import bp as stock_bp
    app.register_blueprint(stock_bp, url_prefix='/stocks')

    from app.staff import bp as staff_bp
    app.register_blueprint(staff_bp, url_prefix='/staff')


    @app.route('/test/')
    def test_page():
        return '<h1>Testing the flask Application Factory Pattern</h1>'
    
    @app.route('/')
    def dashboard():
        return render_template('index.html')
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)