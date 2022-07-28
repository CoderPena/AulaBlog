from flask import Flask, render_template, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask("hello")

## Dicionário de configuração desta aplicação py flask. Opções de banco:
## "sqlite:///app.db"
## "mongodb:///app.db"
## "mysql:///app.db"
## Etc
## A 1a. '/' indica que o BD está LOCAL
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)    ## Pluging para instanciar um banco de dados e relacionar à aplicação py flask

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(70), nullable=False)
    body = db.Column(db.String(500))
    author = db.Column(db.String(20))
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

""" meu código com erro
class Post(db.Model):   ## Post herdará a classe Model instanciado no objeto db
    __tablename__ = 'posts' ## Se não houver esta redefinição, é assumido o nome da classe como nome da tabela
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = dbColumn(db.String(70), nullable=False)
    body = dbColumn(db.String(500))
    author = dbColumn(db.String(20))
    created = dbColumn(db.DateTime, nullable=False, default=datetime.now)
"""

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=True, unique=True, index=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=True)
    posts = db.relationship('Post', backref='author')

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

@app.route("/")
def index():
    # Busca os posts do BD
    posts = Post.query.all()
    return render_template("index.html", posts=posts)

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
    
