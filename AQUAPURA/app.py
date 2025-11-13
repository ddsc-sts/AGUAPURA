from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/copos')
def copos():
    return render_template('copos.html')

@app.route('/garrafas')
def garrafas():
    return render_template('garrafas.html')

@app.route('/acessorios')
def acessorios():
    return render_template('acessorios.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/politica_troca')
def politica_troca():
    return render_template('politica_troca.html')

@app.route("/politica-privacidade")
def politica_privacidade():
    return render_template("politica_privacidade.html")

@app.route("/carrinho")
def carrinho():
    return render_template("carrinho.html")


if __name__ == '__main__':
    app.run(debug=True)
