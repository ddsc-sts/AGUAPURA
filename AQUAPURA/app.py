from flask import Flask, render_template

app = Flask(__name__)

# ===== Rota da página inicial =====
@app.route('/')
def index():
    return render_template('index.html')

# ===== Execução local =====
if __name__ == '__main__':
    app.run(debug=True)
