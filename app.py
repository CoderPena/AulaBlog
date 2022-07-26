from flask import Flask, render_template

app = Flask("hello")

@app.route("/")             # Define como raiz o recurso da página, nosso primeiro endpoint.
@app.route("/hello")        # Define hello como sinônimo do mesmo endpoint.
def hello(): 
    return "Hello World"    

@app.route("/meucontato")    # Define nosso segundo endpoint, que vem abaixo do raiz.
def meuContato():
    return render_template('index.html')