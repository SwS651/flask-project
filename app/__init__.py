from flask import Flask, render_template, request, redirect, url_for
from config import Config
from app.extensions import db
from app.models.stock import Stock
from app.models.category import Category
from app.models.staff import Staff

# from app.utils.import_.import_utils import*

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
    
    from app.utils import bp as utils_bp
    app.register_blueprint(utils_bp, url_prefix='/utils')

        
        
    @app.route('/')
    def dashboard():
        return render_template('index.html')
    
    @app.route('/login',methods=['GET','POST'])
    def login():
        info_message = ""
            
        if request.method == "POST":
            # users = db.session.execute(db.select(User).order_by(User.StaffName)).scalars()
            user = db.session.execute(db.select(Staff).filter_by(StaffEmail=request.form["email"],Password=request.form["password"])).scalar()
            if not user:
                info_message = "Invalid Email or Password!"
            else:
                
                return redirect(url_for('dashboard'))
            
        return render_template("login/login.html", info_message = info_message)


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)