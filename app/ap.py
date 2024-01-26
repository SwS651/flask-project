from flask import Flask,render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

# create the extension
db = SQLAlchemy()
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///F:\\python project\\project2\\project.db"
# initialize the app with the extension
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable = False)
    email = db.Column(db.String)

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return "<p>Hello, Worlds!sssa</p>"


@app.route("/login", methods=["GET","POST"])
def user_list():
    info_message = None
    url_direction = "users/login.html"
    if request.method == "POST":
        # users = db.session.execute(db.select(User).order_by(User.username)).scalars()
        user = db.session.execute(db.select(User).filter_by(username=request.form["username"],password=request.form["password"])).scalar()
        if not user:
            info_message = "Username or Password incorrect"
        else:
            url_direction = "index.html"
    return render_template(f"{url_direction}", info_message = info_message)


@app.route("/register", methods=["GET", "POST"])
def user_create():
    error = None
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password = request.form["password"],
            email=request.form["email"]
        )
        db.session.add(user)
        db.session.commit()
        # return redirect(url_for("user_detail", id=user.id))
        return render_template("users/register.html",error = "register successfully" )

    return render_template("users/register.html",error = error )




@app.route("/user/<int:id>")
def user_detail(id):
    user = db.get_or_404(User, id)
    return render_template("user/detail.html", user=user)

@app.route("/user/<int:id>/delete", methods=["GET", "POST"])
def user_delete(id):
    user = db.get_or_404(User, id)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))

    return render_template("user/delete.html", user=user)