# App Url = https://flaskcrudtaskapp.herokuapp.com/
# Admin name = "******"
# Password = "#654321"

from flask import Flask, render_template, url_for, redirect, session
from sqlalchemy.sql.elements import Null
from  flask_session import Session
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

ADMIN_NAME = "admin"

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    added_by = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods=['GET', 'POST'])
def index():
    # if datetime.utcnow().strftime('%H:%M') == "12:01":
    #     session.clear()
    if not session.get("name"):
        return redirect('/login')
    else:
        if request.method == 'POST':
            task_content = request.form['content'].rstrip()
            if task_content:
                new_task = Todo(content=task_content, added_by=session["name"])
                # print(new_task)
                try:
                    db.session.add(new_task)
                    db.session.commit()
                    return redirect('/')
                except Exception as e:
                    # print(e)
                    return "There was an issue adding your task"
            else:
                return render_template("error.html", message="You haven't Enetered TAsk.. ;(")
        else:
            tasks = Todo.query.order_by(Todo.date_created).all()
            return render_template('index.html', tasks=tasks, admin=ADMIN_NAME)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Validate user's Name
        if not request.form.get("name"):
            return render_template("error.html", message="You man haven't entered your User Name yet..")
        # validate user
        if not request.form.get("pwd") == "#654321":
            return render_template("error.html", message="Incorrect password..")
        # Remember that user logged in
        session["name"] = request.form.get("name")
        
        # Redirected user to /
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    session.clear()
    return redirect("/")

@app.route('/delete/<int:id>')
def delete(id):
    if session["name"] == ADMIN_NAME: 
        task_to_delete = Todo.query.get_or_404(id)
        
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            # print(e)
            return "There was a problem deleting that task"
    else:
        return render_template("error.html", message="You Do not have permission to delete tasks,\n Only Admin has this permission")

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if session["name"] == ADMIN_NAME:
        task = Todo.query.get_or_404(id)
        if request.method == 'POST':
            task.content = request.form['content']
            
            try:
                db.session.commit()
                return redirect('/')
            except:
                return "There was an issue updating task"

        else:
            return render_template("update.html", task=task)
    
    else:
        return render_template("error.html", message="You Do not have permission to Update tasks,\n Only Admin has this permission")

if __name__ == "__main__":
    app.run(debug=False)