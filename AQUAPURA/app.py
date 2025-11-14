from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector, uuid
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "chave-muito-segura"

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get("logado"):
            flash("Você precisa estar logado para acessar o carrinho.", "erro")
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


# ============================
# Conexão com MySQL
# ============================
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        port=3406,
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

#Carrinho

@app.route("/carrinho")
@login_required
def carrinho():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    cursor.execute("""
        SELECT c.id AS carrinho_id, c.quantidade, 
               p.nome, p.preco, p.imagem_principal
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.session_id = %s
    """, (session_id,))
    
    itens = cursor.fetchall()

    # Garantir que valores sejam Decimal
    subtotal = Decimal("0.00")

    for item in itens:
        preco = Decimal(item["preco"])
        quantidade = Decimal(item["quantidade"])
        subtotal += preco * quantidade

    # Frete também como Decimal
    frete = Decimal("12.00") if subtotal > 0 else Decimal("0.00")

    total = subtotal + frete

    return render_template("carrinho.html",itens=itens,subtotal=subtotal,frete=frete,total=total)



@app.route("/add_carrinho/<int:produto_id>")
def add_carrinho(produto_id):
    db = conectar()
    cursor = db.cursor()

    session_id = get_session_id()

    # Verifica se já existe o item no carrinho
    cursor.execute("""
        SELECT quantidade FROM carrinho 
        WHERE session_id = %s AND produto_id = %s
    """, (session_id, produto_id))

    item = cursor.fetchone()

    if item:
        cursor.execute("""
            UPDATE carrinho 
            SET quantidade = quantidade + 1
            WHERE session_id = %s AND produto_id = %s
        """, (session_id, produto_id))
    else:
        cursor.execute("""
            INSERT INTO carrinho (session_id, produto_id, quantidade)
            VALUES (%s, %s, 1)
        """, (session_id, produto_id))

    db.commit()
    return redirect(url_for("carrinho"))

@app.route("/carrinho/add/<int:id>")
@login_required
def aumentar_item(id):
    db = conectar()
    cursor = db.cursor()

    cursor.execute("UPDATE carrinho SET quantidade = quantidade + 1 WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for("carrinho"))


@app.route("/carrinho/sub/<int:id>")
def diminuir_item(id):
    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT quantidade FROM carrinho WHERE id = %s", (id,))
    q = cursor.fetchone()[0]

    if q > 1:
        cursor.execute("UPDATE carrinho SET quantidade = quantidade - 1 WHERE id = %s", (id,))
    else:
        cursor.execute("DELETE FROM carrinho WHERE id = %s", (id,))

    db.commit()
    return redirect(url_for("carrinho"))

@app.route("/carrinho/remover/<int:id>")
def remover_item(id):
    db = conectar()
    cursor = db.cursor()

    cursor.execute("DELETE FROM carrinho WHERE id = %s", (id,))
    db.commit()

    return redirect(url_for("carrinho"))


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

@app.context_processor
def contador_carrinho():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()
    cursor.execute("SELECT SUM(quantidade) AS total FROM carrinho WHERE session_id = %s", (session_id,))
    
    total = cursor.fetchone()["total"]
    return {"total_carrinho": total if total else 0}

# --------------------------- CADASTRO ---------------------------

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        db = conectar()
        cursor = db.cursor(dictionary=True)

        # Verifica se email já existe
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existente = cursor.fetchone()

        if existente:
            flash("Este e-mail já está cadastrado!", "erro")
            return redirect("/cadastro")

        # Criptografa a senha
        senha_hash = generate_password_hash(senha)

        # Salvar no banco
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        db.commit()

        flash("Conta criada com sucesso! Faça login.", "sucesso")
        return redirect("/login")

    return render_template("cadastro.html")


# --------------------------- LOGIN ---------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        db = conectar()
        cursor = db.cursor(dictionary=True)

        # Busca usuário
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("E-mail não encontrado!", "erro")
            return redirect("/login")

        # Verifica senha
        if not check_password_hash(user["senha"], senha):
            flash("Senha incorreta!", "erro")
            return redirect("/login")

        # Tudo certo → salva sessão
        session["usuario_id"] = user["id"]
        session["usuario_nome"] = user["nome"]
        session["logado"] = True

        flash("Bem-vindo(a), " + user["nome"] + "!", "sucesso")
        return redirect("/")

    return render_template("login.html")


# --------------------------- LOGOUT ---------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect("/")



if __name__ == '__main__':
    app.run(debug=True)
