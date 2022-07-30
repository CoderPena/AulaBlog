from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
import os

app = Flask("hello")

## Dicionário de configuração desta aplicação py flask. Opções de banco:
## "sqlite:///app.db"
## "mongodb:///app.db"
## "mysql:///app.db"
## Etc
## A 1a. '/' indica que o BD está LOCAL
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db_url = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
app.config["SQLALCHEMY_DATABASE_URI"] =  db_url.replace("postgres", "postgresql")


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "pudim" ## Chave para gerar o hash

db = SQLAlchemy(app)        ## Pluging para instanciar um banco de dados e relacionar à aplicação py flask
login = LoginManager(app)   ## Pluging para o gerenciamento de login

class Post(db.Model):   ## Post herdará a classe Model instanciado no objeto db
    __tablename__ = 'posts' ## Se não houver esta redefinição, é assumido o nome da classe como nome da tabela
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(70), nullable=False)
    body = db.Column(db.String(500))
    ## author = db.Column(db.String(20)) -- Referenciada via db.ForeignKey('users.id') na tabela User
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
   
""" Professor
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(70), nullable=False)
    body = db.Column(db.String(500))
    ## author = db.Column(db.String(20))
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
"""
class User(UserMixin, db.Model): ## Herança multiplica, com desempates da esquerda para a direita.
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=True, unique=True, index=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=True)
    posts = db.relationship('Post', backref='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


db.create_all()  ## Cria todas as tabelas. Se já existir, não cria.

""" Iremos comentar este MOCK para troca-lo pelo banco de dados do SQLAlchemy
posts = [
   {
        "title": "O meu Primeiro Post",
        "body": "Aqui é o texto do Post",
        "author": "Feulo",
        "created": datetime(2022,7,25)
    },
    {
        "title": "O meu Segundo Post",
        "body": "Aqui é o texto do Post",
        "author": "Danilo",
        "created": datetime(2022,7,26)
    },
]
"""

@app.route("/") ## Rotas são chamadas de VIEWS
def index():
    # Busca os posts do BD
    posts = Post.query.all()
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Username registered sussecfull!")
        except IntegrityError:
            flash("Username or e-mail already exist!")
        else:
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Incorret Username or Password")
            return redirect(url_for("login"))
            
        login_user(user)
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
@login_required   ## Não permite entrar na view CREATE sem autenticação
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        try:
            post = Post(title=title, body=body, author=current_user)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        except IntegrityError:
            flash("Erro on creating post.")

    return render_template("create.html")


""" Trocamos o populate por código py
@app.route("/populate")
def populate():
    user = User(username='Pena', email='g@g.com', password_hash='a')
    post1 = Post(title="Post1", body="Texto do post 1", author=user)
    post2 = Post(title="Post2", body="Texto do post 2", author=user)
    db.session.add(user)
    db.session.add(post1)
    db.session.add(post2)
    db.session.commit()
    return redirect(url_for("index"))
    
"""