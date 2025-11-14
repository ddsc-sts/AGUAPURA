from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# ============================
# Conexão com MySQL
# ============================
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # altere se tiver senha
        database="aguapura"
    )

# ============================
# ROTAS PRINCIPAIS
# ============================

@app.route('/')
def home():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos ORDER BY criado_em DESC LIMIT 6")
    produtos = cursor.fetchall()

    return render_template('index.html', produtos=produtos)


@app.route('/produto/<int:id>')
def produto(id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
    produto = cursor.fetchone()

    cursor.execute("SELECT imagem FROM imagens_produto WHERE produto_id = %s", (id,))
    imagens = cursor.fetchall()

    return render_template('produto.html', produto=produto, imagens=imagens)


# ============================
# CATEGORIAS – agora dinâmicas
# ============================

@app.route('/copos')
def copos():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE categoria = 'Copo'")
    produtos = cursor.fetchall()

    return render_template('copos.html', produtos=produtos)


@app.route('/garrafas')
def garrafas():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE categoria = 'Garrafa'")
    produtos = cursor.fetchall()

    return render_template('garrafas.html', produtos=produtos)


@app.route('/acessorios')
def acessorios():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE categoria = 'Acessório'")
    produtos = cursor.fetchall()

    return render_template('acessorios.html', produtos=produtos)


# ============================
# OUTRAS PÁGINAS
# ============================

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


# ============================
# ROTAS DO PAINEL ADMIN
# ============================

@app.route("/admin")
def admin_home():
    return render_template("admin/dashboard.html")


@app.route("/admin/produtos")
def admin_produtos():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # removido categoria_id porque NÃO existe no banco
    cursor.execute("SELECT * FROM produtos ORDER BY id DESC")
    produtos = cursor.fetchall()

    return render_template("admin/produtos.html", produtos=produtos)


@app.route("/admin/produtos/novo", methods=["GET", "POST"])
def admin_novo_produto():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # categorias ainda existem, então isso pode continuar
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        estoque = request.form["estoque"]
        categoria = request.form["categoria"]  # agora salva diretamente como texto

        cursor.execute("""
            INSERT INTO produtos (nome, descricao, preco, estoque, categoria, imagem_principal)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, descricao, preco, estoque, categoria, "/static/img/default.png"))

        db.commit()
        return redirect("/admin/produtos")

    return render_template("admin/novo_produto.html", categorias=categorias)


if __name__ == '__main__':
    app.run(debug=True)
