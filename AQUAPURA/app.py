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

if __name__ == '__main__':
    app.run(debug=True)
