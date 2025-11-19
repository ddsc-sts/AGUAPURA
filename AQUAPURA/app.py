from flask import Flask, render_template, request, redirect, url_for, flash, session , jsonify
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

    # Produto atual
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
    produto = cursor.fetchone()

    # Imagens adicionais
    cursor.execute("SELECT imagem FROM imagens_produto WHERE produto_id = %s", (id,))
    imagens = cursor.fetchall()

    # Se for Copo ou Garrafa → sugerir acessórios
    if produto["categoria"] in ("Copo", "Garrafa"):
        cursor.execute("SELECT * FROM produtos WHERE categoria = 'Acessório' LIMIT 4")
        sugestoes = cursor.fetchall()

    # Se for Acessório → sugerir Copos e Garrafas
    else:
        cursor.execute("SELECT * FROM produtos WHERE categoria IN ('Copo', 'Garrafa') LIMIT 4")
        sugestoes = cursor.fetchall()

    return render_template(
        'produto.html',
        produto=produto,
        imagens=imagens,
        sugestoes=sugestoes
    )




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

# ---------------------------
# CARRINHO
# ---------------------------

@app.route("/carrinho")
@login_required
def carrinho():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    cursor.execute("""
        SELECT c.id AS carrinho_id, c.quantidade, c.cor,
               p.id AS produto_id, p.nome, p.preco, p.imagem_principal, p.estoque
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.session_id = %s
    """, (session_id,))
    itens = cursor.fetchall()

    # Calcular subtotal com Decimal
    subtotal = Decimal("0.00")
    for item in itens:
        preco = Decimal(item["preco"])
        quantidade = Decimal(item["quantidade"])
        subtotal += preco * quantidade

    frete = Decimal("12.00") if subtotal > 0 else Decimal("0.00")
    total = subtotal + frete

    return render_template("carrinho.html", itens=itens, subtotal=subtotal, frete=frete, total=total)



# ---------------------------
# Atualizar carrinho (agora aceita POST, salva cor e itens do kit como itens normais)
# ---------------------------
@app.route("/add_carrinho/<int:produto_id>", methods=["POST"])
def add_carrinho(produto_id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    # quantidade do produto principal
    qtd_form = int(request.form.get("quantidade", 1))
    cor = request.form.get("cor", "") or ""  # salva string vazia se não tiver cor

    # kit (se vier): listas paralelas de ids e quantidades
    kit_produtos = request.form.getlist("kit_produtos")
    kit_qtds = request.form.getlist("kit_qtds")

    # --- Função util: inserir/atualizar um item no carrinho levando em conta 'cor' ---
    def upsert_carrinho(prod_id, qtd, cor_value=""):
        # pegar estoque atual do produto
        cursor.execute("SELECT estoque FROM produtos WHERE id = %s", (prod_id,))
        r = cursor.fetchone()
        if not r:
            return False, f"Produto {prod_id} não encontrado."

        estoque = int(r["estoque"])

        # procurar item com mesma session, produto e cor
        cursor.execute("""
            SELECT id, quantidade FROM carrinho
            WHERE session_id = %s AND produto_id = %s AND IFNULL(cor, '') = %s
        """, (session_id, prod_id, cor_value))
        existing = cursor.fetchone()

        nova_qtd = qtd + (existing["quantidade"] if existing else 0)

        if nova_qtd > estoque:
            return False, f"Quantidade solicitada maior que estoque (disponível {estoque})."

        if existing:
            cursor.execute("""
                UPDATE carrinho SET quantidade = %s WHERE id = %s
            """, (nova_qtd, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO carrinho (session_id, produto_id, quantidade, cor)
                VALUES (%s, %s, %s, %s)
            """, (session_id, prod_id, nova_qtd, cor_value))

        return True, None

    # Primeiro, adiciona/atualiza produto principal
    ok, err = upsert_carrinho(produto_id, qtd_form, cor)
    if not ok:
        flash(err, "erro")
        return redirect(url_for("produto", id=produto_id))

    # Em seguida, adiciona itens do kit (se houver)
    if kit_produtos and kit_qtds:
        # kit_produtos and kit_qtds são lists de strings; iterar de forma segura
        for idx, pid_str in enumerate(kit_produtos):
            try:
                pid = int(pid_str)
                qtd_kit = int(kit_qtds[idx]) if idx < len(kit_qtds) else 1
            except:
                continue
            ok, err = upsert_carrinho(pid, qtd_kit, "")  # acessórios sem cor por padrão
            if not ok:
                flash(f"Erro ao adicionar item do kit: {err}", "erro")
                # continuar tentando os outros, mas informar o usuário
    db.commit()
    flash("Produto(s) adicionados ao carrinho!", "sucesso")
    return redirect(url_for("carrinho"))







# ---------------------------
# AUMENTAR QUANTIDADE (CHECK DE ESTOQUE)
# ---------------------------
@app.route("/carrinho/add/<int:id>")
@login_required
def aumentar_item(id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Buscar item + estoque do produto
    cursor.execute("""
        SELECT c.quantidade, p.estoque, c.produto_id
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.id = %s
    """, (id,))
    item = cursor.fetchone()

    if not item:
        return redirect(url_for("carrinho"))

    if item["quantidade"] >= item["estoque"]:
        flash(f"Máximo disponível: {item['estoque']} unidades.", "erro")
        return redirect(url_for("carrinho"))

    cursor.execute("UPDATE carrinho SET quantidade = quantidade + 1 WHERE id = %s", (id,))
    db.commit()

    return redirect(url_for("carrinho"))



# ---------------------------
# DIMINUIR QUANTIDADE (NÃO NEGATIVO)
# ---------------------------
@app.route("/carrinho/sub/<int:id>")
@login_required
def diminuir_item(id):
    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT quantidade FROM carrinho WHERE id = %s", (id,))
    q = cursor.fetchone()

    if not q:
        return redirect(url_for("carrinho"))

    qtd = q[0]

    if qtd <= 1:
        cursor.execute("DELETE FROM carrinho WHERE id = %s", (id,))
    else:
        cursor.execute("UPDATE carrinho SET quantidade = quantidade - 1 WHERE id = %s", (id,))

    db.commit()
    return redirect(url_for("carrinho"))



# ---------------------------
# REMOVER ITEM
# ---------------------------
@app.route("/carrinho/remover/<int:id>")
@login_required
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

@app.route('/buscar')
def buscar():
    termo = request.args.get("q", "").strip()

    if termo == "":
        return redirect(url_for("index"))

    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Busca por nome OU parte do nome
    cursor.execute("""
        SELECT * FROM produtos 
        WHERE nome LIKE %s
    """, (f"%{termo}%", ))

    resultados = cursor.fetchall()

    return render_template("buscar.html", termo=termo, resultados=resultados)

# ---------------------------
# Checkout (dados do cliente + escolha método) - GET mostra o form, POST processa
# ---------------------------
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    # obter itens do carrinho
    cursor.execute("""
        SELECT c.id AS carrinho_id, c.quantidade, c.cor, p.id AS produto_id, p.nome, p.preco, p.imagem_principal, p.estoque
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.session_id = %s
    """, (session_id,))
    itens = cursor.fetchall()

    if request.method == "GET":
        # se não houver itens, redireciona
        if not itens:
            flash("Seu carrinho está vazio.", "erro")
            return redirect(url_for("home"))

        # calcula subtotal / frete / total aqui e passa pro template (corrige problema do zero)
        from decimal import Decimal
        subtotal = Decimal("0.00")
        for item in itens:
            preco = Decimal(item["preco"])
            qtd = int(item["quantidade"])
            subtotal += preco * qtd

        frete = Decimal("12.00") if subtotal > 0 else Decimal("0.00")
        total = subtotal + frete

        return render_template("checkout.html", itens=itens, subtotal=subtotal, frete=frete, total=total)

    # POST: processar checkout
    # ler dados do formulário (endereços separados)
    nome = request.form.get("nome", "").strip()
    cpf = request.form.get("cpf", "").strip()
    email = request.form.get("email", "").strip()
    telefone = request.form.get("telefone", "").strip()

    rua = request.form.get("rua", "").strip()
    numero = request.form.get("numero", "").strip()
    bairro = request.form.get("bairro", "").strip()
    estado = request.form.get("estado", "").strip()
    cidade = request.form.get("cidade", "").strip()
    cep = request.form.get("cep", "").strip()

    metodo = request.form.get("metodo_pagamento")  # "PIX" ou "CARTAO"

    # val server-side mínimo
    if not nome or not cpf or not rua or not numero or not estado or not cidade or not cep or not metodo:
        flash("Preencha todos os campos obrigatórios.", "erro")
        return redirect(url_for("checkout"))

    # normaliza cpf/cep (apenas dígitos)
    import re
    cpf_digits = re.sub(r"\D", "", cpf)
    cep_digits = re.sub(r"\D", "", cep)

    if len(cpf_digits) != 11:
        flash("CPF inválido. Verifique o formato.", "erro")
        return redirect(url_for("checkout"))
    if len(cep_digits) != 8:
        flash("CEP inválido. Verifique o formato.", "erro")
        return redirect(url_for("checkout"))

    # recalcular total e validar estoque antes de criar pedido
    from decimal import Decimal
    subtotal = Decimal("0.00")
    for item in itens:
        preco = Decimal(item["preco"])
        qtd = int(item["quantidade"])
        # verificar estoque atual
        cursor.execute("SELECT estoque FROM produtos WHERE id = %s", (item["produto_id"],))
        estoque_row = cursor.fetchone()
        if not estoque_row:
            flash("Produto não encontrado durante checkout.", "erro")
            return redirect(url_for("carrinho"))
        estoque = int(estoque_row["estoque"])
        if qtd > estoque:
            flash(f"Quantidade do produto {item['nome']} maior que o estoque ({estoque}).", "erro")
            return redirect(url_for("carrinho"))
        subtotal += preco * Decimal(qtd)

    frete = Decimal("12.00") if subtotal > 0 else Decimal("0.00")
    total = subtotal + frete

    # monta endereço final (pode ter colunas separadas no DB, aqui concatenamos)
    endereco = f"{rua}, {numero}" + (f" - {bairro}" if bairro else "") + f" - {cidade}/{estado} - CEP {cep_digits}"

    # criar pedido (ajuste as colunas conforme seu schema)
    try:
        cursor.execute("""
            INSERT INTO pedidos (usuario_id, valor_total, status, pagamento_metodo, cliente_nome, cliente_cpf, cliente_endereco)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (None, str(total), "aguardando_pagamento", metodo, nome, cpf_digits, endereco))
        db.commit()
    except Exception as e:
        db.rollback()
        flash("Erro ao criar pedido. Tente novamente.", "erro")
        print("Erro INSERT pedidos:", e)
        return redirect(url_for("checkout"))

    pedido_id = cursor.lastrowid

    # inserir itens do pedido e reduzir estoque
    try:
        for item in itens:
            produto_id = item["produto_id"]
            qtd = int(item["quantidade"])
            preco = Decimal(item["preco"])

            cursor.execute("""
                INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, valor)
                VALUES (%s, %s, %s, %s)
            """, (pedido_id, produto_id, qtd, str(preco)))

            # reduzir estoque no produto
            cursor.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (qtd, produto_id))

        # limpar carrinho do usuário (sessão)
        cursor.execute("DELETE FROM carrinho WHERE session_id = %s", (session_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        flash("Erro ao processar itens do pedido. Contate o suporte.", "erro")
        print("Erro pedido_itens/estoque:", e)
        return redirect(url_for("carrinho"))

    # redirecionar para página "pedido feito"
    flash("Pedido criado com sucesso!", "sucesso")
    return redirect(url_for("pedido_finalizado", pedido_id=pedido_id))


# ---------------------------
# Página "Pedido Feito"
# ---------------------------
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    if "usuario_id" not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect("/login")

    usuario_id = session["usuario_id"]
    carrinho = session.get("carrinho", [])

    if not carrinho:
        flash("Carrinho vazio!", "erro")
        return redirect("/carrinho")

    valor_total = sum(item["preco"] * item["quantidade"] for item in carrinho)

    db = conectar()
    cursor = db.cursor(dictionary=True)

    # 🔥 AGORA O usuario_id ESTÁ SENDO SALVO
    cursor.execute("""
        INSERT INTO pedidos (usuario_id, valor_total, status, pagamento_metodo)
        VALUES (%s, %s, 'Aguradando Pagamento', %s)
    """, (usuario_id, valor_total, "PIX"))

    pedido_id = cursor.lastrowid

    # Salva cada item do pedido
    for item in carrinho:
        cursor.execute("""
            INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (%s, %s, %s, %s)
        """, (pedido_id, item["id"], item["quantidade"], item["preco"]))

    db.commit()
    cursor.close()
    db.close()

    session["carrinho"] = []  # limpa carrinho

    return redirect(url_for("pedido_finalizado", pedido_id=pedido_id))

@app.route("/pedido_finalizado/<int:pedido_id>")
def pedido_finalizado(pedido_id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        flash("Pedido não encontrado.", "erro")
        return redirect("/")

    cursor.execute("""
        SELECT pi.*, p.nome, p.imagem_principal
        FROM pedido_itens pi
        JOIN produtos p ON p.id = pi.produto_id
        WHERE pi.pedido_id = %s
    """, (pedido_id,))
    itens = cursor.fetchall()

    return render_template("pedido_finalizado.html", pedido=pedido, itens=itens)

@app.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect("/login")

    user_id = session["usuario_id"]

    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id, nome, avatar, criado_em FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()

    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY criado_em DESC", (user_id,))
    pedidos = cursor.fetchall()

    cursor.execute("""
        SELECT produtos.nome, produtos.imagem_principal
        FROM favoritos
        JOIN produtos ON produtos.id = favoritos.produto_id
        WHERE favoritos.usuario_id = %s
    """, (user_id,))
    favoritos = cursor.fetchall()

    return render_template("perfil.html", usuario=usuario, pedidos=pedidos, favoritos=favoritos)

# --------------------------
# API PARA GRÁFICO EM JS
# --------------------------

@app.route("/api/estatisticas")
def api_estatisticas():
    if "usuario_id" not in session:
        return jsonify({"erro": "não logado"}), 401

    user_id = session["usuario_id"]

    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            MONTH(criado_em) AS mes,
            COUNT(*) AS total
        FROM pedidos
        WHERE usuario_id = %s
        GROUP BY MONTH(criado_em)
    """, (user_id,))

    dados = cursor.fetchall()

    return jsonify(dados)


if __name__ == '__main__':
    app.run(debug=True)

