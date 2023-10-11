from flask import render_template, request, redirect, url_for ,flash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_bcrypt import check_password_hash
from datetime import datetime

app=Flask(__name__)



app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def loader_user(user_id):
    return User.query.get(user_id)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    password=db.Column(db.String(80),nullable=False)
    
    
class Todo(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    text = db.Column(db.String(200)) 
    complete = db.Column(db.Boolean) 


db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/todo') 
def index(): 
	incomplete = Todo.query.filter_by(complete=False).all() 
	complete = Todo.query.filter_by(complete=True).all() 

	return render_template('index.html', incomplete=incomplete, complete=complete) 


@app.route('/add', methods=['POST']) 
def add(): 
	todo = Todo(text=request.form['todoitem'], complete=False) 
	db.session.add(todo) 
	db.session.commit() 

	return redirect(url_for('index')) 


@app.route('/complete/<id>') 
def complete(id): 
    todo = Todo.query.filter_by(id=int(id)).first() 
    todo.complete = True
    db.session.commit() 
    return redirect(url_for('index')) 

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and password==user.password:
            login_user(user)
            flash("Login successful", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "danger")
   
    return render_template("login.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=="POST":
        passw=request.form.get('password')
        uname=request.form.get('username')
        user=User(username=uname, password=passw)
        print(user)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route('/update/<int:id>') 
def update(id): 
    todo = Todo.query.filter_by(id=id).first() 
    todo.complete = not todo.complete
    db.session.commit() 
    return redirect(url_for('home')) 



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    todo = Todo.query.get(id)
    if request.method == 'POST':
        new_text = request.form.get('new_text')
        todo.text = new_text
        db.session.commit()
        flash("Todo item updated successfully", "success")
        return redirect(url_for('index'))
    return render_template('edit.html', todo=todo)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    todo = Todo.query.get(id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash("Todo item deleted successfully", "success")
    else:
        flash("Todo item not found", "danger")
    return redirect(url_for('index'))


if __name__=="__main__":
    app.run(debug=True)
    
    
#<a href="/delete/{{todo.id}}">delete</a>