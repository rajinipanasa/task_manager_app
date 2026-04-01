from flask import Flask, render_template, request, redirect, session
from models import db, User, Task
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------- AUTH ----------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed = generate_password_hash(request.form["password"])

        user = User(
            username=request.form["username"],
            password=hashed
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------- DASHBOARD ----------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    user = User.query.get(session["user_id"])   # 🔥 FIX ADDED
    tasks = Task.query.filter_by(user_id=session["user_id"]).all()

    return render_template("dashboard.html", tasks=tasks, user=user)  # 🔥 FIX


# ---------- TASK CRUD ----------

@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/")

    task = Task(
        task=request.form["task"],
        status="Todo",
        due_date=request.form.get("due_date"),   # 🔥 NEW (calendar support)
        user_id=session["user_id"]
    )

    db.session.add(task)
    db.session.commit()
    return redirect("/dashboard")


@app.route("/delete/<int:id>")
def delete(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/dashboard")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    task = Task.query.get(id)

    if request.method == "POST":
        task.task = request.form["task"]
        db.session.commit()
        return redirect("/dashboard")

    return render_template("edit.html", task=task)


@app.route("/status/<int:id>/<status>")
def status(id, status):
    task = Task.query.get(id)
    task.status = status
    db.session.commit()
    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)