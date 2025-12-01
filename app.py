from flask import Flask, render_template, request, redirect, url_for, flash, session , jsonify
import mysql.connector, uuid, re
from decimal import Decimal
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "chave-muito-segura"
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "minha_chave"

# Config SMTP diretamente no app (sem env vars)
app.config['SMTP_HOST'] = "smtp.gmail.com"
app.config['SMTP_PORT'] = 465   # SSL
app.config['SMTP_USER'] = "aquapura.suporte@gmail.com"
app.config['SMTP_PASS'] = "yhdj jaud tjug tofx"
app.config['CODIGO_EXPIRACAO_MIN'] = 15

# Variáveis locais (importantes!)
SMTP_HOST = app.config['SMTP_HOST']
SMTP_PORT = app.config['SMTP_PORT']
SMTP_USER = app.config['SMTP_USER']
SMTP_PASS = app.config['SMTP_PASS']
CODIGO_EXPIRACAO_MIN = app.config['CODIGO_EXPIRACAO_MIN']



print("DEBUG:", SMTP_USER, SMTP_PASS)


# --------------- ADIÇÕES PARA O SISTEMA DE RECUPERAÇÃO DE SENHA ---------------
import smtplib
import ssl
import random
from datetime import datetime, timedelta
from email.message import EmailMessage
# ------------------------------------------------------------------------------

# ============================
# Conexão com MySQL
# ============================
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",

        port=3407,
        password="root",   # altere se tiver senha
        database="aguapura"
    )


# ============================
# DECORADORES DE PROTEÇÃO
# ============================



from functools import wraps

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logado"):
            flash("Você precisa estar logado!", "erro")
            return redirect("/admin/login")
        
        if session.get("tipo") != "admin":
            flash("Acesso negado! Apenas administradores.", "erro")
            return redirect("/")
        
        return func(*args, **kwargs)
    return wrapper


def funcionario_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logado"):
            flash("Você precisa estar logado!", "erro")
            return redirect("/admin/login")
        
        tipo = session.get("tipo")
        if tipo not in ["funcionario", "admin"]:
            flash("Acesso negado! Apenas funcionários e administradores.", "erro")
            return redirect("/")
        
        return func(*args, **kwargs)
    return wrapper


# ============================
# LOGIN ADMIN/FUNCIONÁRIO
# ============================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        db = conectar()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("E-mail não encontrado!", "erro")
            return redirect("/admin/login")

        # Verifica se é admin ou funcionário
        if user["tipo"] not in ["admin", "funcionario"]:
            flash("Acesso negado! Apenas funcionários e administradores.", "erro")
            return redirect("/admin/login")

        # Verifica senha
        if not check_password_hash(user["senha"], senha):
            flash("Senha incorreta!", "erro")
            return redirect("/admin/login")

        # Login bem-sucedido
        session["usuario_id"] = user["id"]
        session["usuario_nome"] = user["nome"]
        session["usuario_avatar"] = user["avatar"]
        session["tipo"] = user["tipo"]
        session["logado"] = True

        # Redireciona conforme o tipo
        if user["tipo"] == "admin":
            flash(f"Bem-vindo, Admin {user['nome']}!", "sucesso")
            return redirect("/admin/painel")
        else:
            flash(f"Bem-vindo, {user['nome']}!", "sucesso")
            return redirect("/funcionario/painel")

    return render_template("admin/login.html")


# ============================
# PAINEL DO FUNCIONÁRIO
# ============================

@app.route("/funcionario/painel")
@funcionario_required
def funcionario_painel():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Estatísticas rápidas
    cursor.execute("SELECT COUNT(*) as total FROM pedidos WHERE DATE(criado_em) = CURDATE()")
    pedidos_hoje = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM pedidos WHERE status = 'aguardando_pagamento'")
    pedidos_pendentes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM produtos WHERE estoque < 10")
    estoque_baixo = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE tipo = 'cliente'")
    total_clientes = cursor.fetchone()["total"]

    return render_template("funcionario/painel.html",
                         pedidos_hoje=pedidos_hoje,
                         pedidos_pendentes=pedidos_pendentes,
                         estoque_baixo=estoque_baixo,
                         total_clientes=total_clientes)


@app.route("/funcionario/pedidos")
@funcionario_required
def funcionario_pedidos():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Filtros
    status_filtro = request.args.get("status", "todos")
    
    if status_filtro == "todos":
        cursor.execute("""
            SELECT p.*, u.nome as cliente_nome, u.email as cliente_email
            FROM pedidos p
            LEFT JOIN usuarios u ON u.id = p.usuario_id
            ORDER BY p.criado_em DESC
        """)
    else:
        cursor.execute("""
            SELECT p.*, u.nome as cliente_nome, u.email as cliente_email
            FROM pedidos p
            LEFT JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.status = %s
            ORDER BY p.criado_em DESC
        """, (status_filtro,))
    
    pedidos = cursor.fetchall()

    return render_template("funcionario/pedidos.html", pedidos=pedidos, status_filtro=status_filtro)


@app.route("/funcionario/pedido/<int:pedido_id>")
@funcionario_required
def funcionario_pedido_detalhe(pedido_id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Buscar pedido
    cursor.execute("""
        SELECT p.*, u.nome as cliente_nome, u.email as cliente_email
        FROM pedidos p
        LEFT JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.id = %s
    """, (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        flash("Pedido não encontrado!", "erro")
        return redirect("/funcionario/pedidos")

    # Buscar itens do pedido
    cursor.execute("""
        SELECT pi.*, p.nome, p.imagem_principal
        FROM pedido_itens pi
        JOIN produtos p ON p.id = pi.produto_id
        WHERE pi.pedido_id = %s
    """, (pedido_id,))
    itens = cursor.fetchall()

    return render_template("funcionario/pedido_detalhe.html", pedido=pedido, itens=itens)


@app.route("/funcionario/pedido/<int:pedido_id>/atualizar-status", methods=["POST"])
@funcionario_required
def funcionario_atualizar_status(pedido_id):
    novo_status = request.form["status"]
    
    db = conectar()
    cursor = db.cursor()
    
    cursor.execute("UPDATE pedidos SET status = %s WHERE id = %s", (novo_status, pedido_id))
    db.commit()
    
    flash("Status atualizado com sucesso!", "sucesso")
    return redirect(f"/funcionario/pedido/{pedido_id}")


@app.route("/funcionario/clientes")
@funcionario_required
def funcionario_clientes():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.*, COUNT(p.id) as total_pedidos
        FROM usuarios u
        LEFT JOIN pedidos p ON p.usuario_id = u.id
        WHERE u.tipo = 'cliente'
        GROUP BY u.id
        ORDER BY total_pedidos DESC
    """)
    clientes = cursor.fetchall()

    return render_template("funcionario/clientes.html", clientes=clientes)


# ============================
# GERENCIAR ESTOQUE
# ============================

@app.route("/funcionario/estoque")
@funcionario_required
def funcionario_estoque():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Buscar TODOS os produtos
    cursor.execute("SELECT * FROM produtos ORDER BY estoque ASC, nome ASC")
    produtos = cursor.fetchall()
    
    # Converter estoque para int
    for produto in produtos:
        produto['estoque'] = int(produto['estoque'])
    
    # Calcular estatísticas
    total_produtos = len(produtos)
    estoque_ok = sum(1 for p in produtos if p['estoque'] > 10)
    estoque_baixo = sum(1 for p in produtos if 1 <= p['estoque'] <= 10)
    esgotados = sum(1 for p in produtos if p['estoque'] == 0)
    
    # DEBUG no console
    print(f"\n📊 ESTOQUE - DEBUG:")
    print(f"   Total: {total_produtos}")
    print(f"   OK (>10): {estoque_ok}")
    print(f"   Baixo (1-10): {estoque_baixo}")
    print(f"   Esgotados (0): {esgotados}")
    
    produtos_zerados = [p for p in produtos if p['estoque'] == 0]
    if produtos_zerados:
        print(f"   🔴 Produtos esgotados:")
        for p in produtos_zerados:
            print(f"      - {p['nome']} (ID: {p['id']})")
    print()

    cursor.close()
    db.close()

    return render_template("funcionario/estoque.html", 
                         produtos=produtos,
                         stats={
                             'total': total_produtos,
                             'ok': estoque_ok,
                             'baixo': estoque_baixo,
                             'esgotados': esgotados
                         })


# ROTA DE AJUSTE DE ESTOQUE

# ROTA DE AJUSTE DE ESTOQUE

  
# ============================
# PAINEL DO ADMIN
# ============================

@app.route("/admin/painel")
@admin_required
def admin_painel():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Estatísticas completas
    cursor.execute("SELECT COUNT(*) as total FROM pedidos")
    total_pedidos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM produtos")
    total_produtos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE tipo = 'cliente'")
    total_clientes = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(valor_total) as total FROM pedidos WHERE status = 'concluido'")
    faturamento = cursor.fetchone()["total"] or 0

    # Pedidos recentes
    cursor.execute("""
        SELECT p.*, u.nome as cliente_nome
        FROM pedidos p
        LEFT JOIN usuarios u ON u.id = p.usuario_id
        ORDER BY p.criado_em DESC
        LIMIT 5
    """)
    pedidos_recentes = cursor.fetchall()

    # Produtos mais vendidos
    cursor.execute("""
        SELECT pr.nome, pr.imagem_principal, SUM(pi.quantidade) as vendas
        FROM pedido_itens pi
        JOIN produtos pr ON pr.id = pi.produto_id
        GROUP BY pi.produto_id
        ORDER BY vendas DESC
        LIMIT 5
    """)
    produtos_top = cursor.fetchall()

    return render_template("admin/painel.html",
                         total_pedidos=total_pedidos,
                         total_produtos=total_produtos,
                         total_clientes=total_clientes,
                         faturamento=faturamento,
                         pedidos_recentes=pedidos_recentes,
                         produtos_top=produtos_top)


@app.route("/admin/usuarios")
@admin_required
def admin_usuarios():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios ORDER BY criado_em DESC")
    usuarios = cursor.fetchall()

    return render_template("admin/usuarios.html", usuarios=usuarios)


@app.route("/admin/usuario/<int:user_id>/promover/<tipo>")
@admin_required
def admin_promover_usuario(user_id, tipo):
    if tipo not in ["cliente", "funcionario", "admin"]:
        flash("Tipo inválido!", "erro")
        return redirect("/admin/usuarios")

    db = conectar()
    cursor = db.cursor()
    
    cursor.execute("UPDATE usuarios SET tipo = %s WHERE id = %s", (tipo, user_id))
    db.commit()
    
    flash(f"Usuário promovido para {tipo} com sucesso!", "sucesso")
    return redirect("/admin/usuarios")


# ============================================
# ROTA DE RELATÓRIOS - VERSÃO COMPLETA
# ============================================

@app.route("/admin/relatorios")
@admin_required
def admin_relatorios():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # ============================================
    # VENDAS MENSAIS - CORRIGIDO
    # ============================================
    cursor.execute("""
        SELECT 
            MONTH(criado_em) as mes,
            YEAR(criado_em) as ano,
            COUNT(id) as total_pedidos,
            SUM(valor_total) as faturamento
        FROM pedidos
        WHERE status IN ('pago', 'enviado', 'entregue', 'concluido')
        GROUP BY ano, mes
        ORDER BY ano DESC, mes DESC
        LIMIT 12
    """)
    vendas_mensais = cursor.fetchall()

    # ============================================
    # PRODUTOS MAIS VENDIDOS - CORRIGIDO
    # ============================================
    cursor.execute("""
        SELECT 
            p.nome,
            p.categoria,
            SUM(pi.quantidade) as total_vendido,
            SUM(pi.quantidade * pi.valor) as receita
        FROM pedido_itens pi
        JOIN produtos p ON p.id = pi.produto_id
        JOIN pedidos ped ON ped.id = pi.pedido_id
        WHERE ped.status IN ('pago', 'enviado', 'entregue', 'concluido')
        GROUP BY p.id, p.nome, p.categoria
        ORDER BY total_vendido DESC
        LIMIT 10
    """)
    produtos_top = cursor.fetchall()

    # ============================================
    # PEDIDOS CANCELADOS (Últimos 20)
    # ============================================
    cursor.execute("""
        SELECT 
            p.id,
            p.criado_em,
            p.valor_total,
            p.pagamento_metodo,
            p.cliente_nome,
            u.nome as usuario_nome,
            (SELECT COUNT(*) FROM pedido_itens WHERE pedido_id = p.id) as total_itens
        FROM pedidos p
        LEFT JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.status = 'cancelado'
        ORDER BY p.criado_em DESC
        LIMIT 20
    """)
    pedidos_cancelados = cursor.fetchall()

    # ============================================
    # TOTAL DE PEDIDOS CANCELADOS
    # ============================================
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM pedidos
        WHERE status = 'cancelado'
    """)
    total_cancelados_result = cursor.fetchone()
    total_cancelados = total_cancelados_result['total'] if total_cancelados_result else 0

    # ============================================
    # ESTATÍSTICAS GERAIS
    # ============================================
    cursor.execute("SELECT COUNT(*) as total FROM pedidos")
    total_pedidos_geral = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT SUM(valor_total) as total 
        FROM pedidos 
        WHERE status IN ('pago', 'enviado', 'entregue', 'concluido')
    """)
    faturamento_total = cursor.fetchone()['total'] or 0

    cursor.close()
    db.close()

    return render_template("admin/relatorios.html",
                         vendas_mensais=vendas_mensais,
                         produtos_top=produtos_top,
                         pedidos_cancelados=pedidos_cancelados,
                         total_cancelados=total_cancelados,
                         total_pedidos_geral=total_pedidos_geral,
                         faturamento_total=faturamento_total)
# ============================================
# ROTA AUXILIAR: FORÇAR ATUALIZAÇÃO DE COMPRAS
# (útil para corrigir dados inconsistentes)
# ============================================

@app.route("/admin/sincronizar-compras")
@admin_required
def sincronizar_compras():
    """
    Popula a tabela compras com todos os pedidos entregues
    que ainda não foram registrados
    """
    db = conectar()
    cursor = db.cursor()
    
    try:
        # Inserir todas as compras de pedidos entregues que não estão em compras
        cursor.execute("""
            INSERT INTO compras (pedido_id, usuario_id, produto_id, quantidade, valor_unitario, valor_total, criado_em)
            SELECT 
                p.id as pedido_id,
                p.usuario_id,
                pi.produto_id,
                pi.quantidade,
                pi.valor as valor_unitario,
                pi.valor * pi.quantidade as valor_total,
                p.criado_em
            FROM pedidos p
            JOIN pedido_itens pi ON pi.pedido_id = p.id
            WHERE p.status = 'entregue'
            AND NOT EXISTS (
                SELECT 1 FROM compras c 
                WHERE c.pedido_id = p.id 
                AND c.produto_id = pi.produto_id
            )
        """)
        
        linhas_inseridas = cursor.rowcount
        db.commit()
        
        flash(f"✅ {linhas_inseridas} compras sincronizadas com sucesso!", "sucesso")
        
    except Exception as e:
        db.rollback()
        flash(f"❌ Erro ao sincronizar: {str(e)}", "erro")
        print(f"Erro na sincronização: {e}")
    
    cursor.close()
    db.close()
    
    return redirect("/admin/relatorios")
@app.route("/admin/produtos/editar/<int:produto_id>", methods=["GET", "POST"])
@admin_required
def admin_editar_produto(produto_id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        preco = request.form["preco"]
        estoque = request.form["estoque"]
        categoria = request.form["categoria"]

        cursor.execute("""
            UPDATE produtos 
            SET nome = %s, descricao = %s, preco = %s, estoque = %s, categoria = %s
            WHERE id = %s
        """, (nome, descricao, preco, estoque, categoria, produto_id))
        db.commit()

        flash("Produto atualizado com sucesso!", "sucesso")
        return redirect("/admin/produtos")

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()

    return render_template("admin/editar_produto.html", produto=produto, categorias=categorias)


@app.route("/admin/produtos/excluir/<int:produto_id>")
@admin_required
def admin_excluir_produto(produto_id):
    db = conectar()
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
    db.commit()
    
    flash("Produto excluído com sucesso!", "sucesso")
    return redirect("/admin/produtos")

# Caminho ABSOLUTO para garantir que salve no lugar certo
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Criar pasta se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/config/atualizar-perfil", methods=["POST"])
def atualizar_perfil():
    if "usuario_id" not in session:
        flash("Você precisa estar logado!", "erro")
        return redirect("/login")
    
    nome = request.form["nome"]
    email = request.form["email"]
    user_id = session["usuario_id"]
    
    db = conectar()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT avatar FROM usuarios WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    avatar_path = user['avatar'] if user and user['avatar'] else None
    
    # Upload de avatar
    if 'avatar' in request.files:
        avatar = request.files['avatar']
        if avatar and avatar.filename and allowed_file(avatar.filename):
            import uuid
            ext = avatar.filename.rsplit('.', 1)[1].lower()
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
            
            # CAMINHO COMPLETO DO ARQUIVO
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Salvar arquivo
            avatar.save(filepath)
            
            # Caminho RELATIVO para salvar no banco (sem /static/)
            avatar_path = f"uploads/avatars/{filename}"
            
            print(f"✅ Avatar salvo em: {filepath}")
            print(f"✅ Caminho no banco: {avatar_path}")
    
    # Atualizar banco
    cursor.execute("""
        UPDATE usuarios 
        SET nome = %s, email = %s, avatar = %s 
        WHERE id = %s
    """, (nome, email, avatar_path, user_id))
    db.commit()
    
    # Atualizar sessão
    session["usuario_nome"] = nome
    session["usuario_email"] = email
    session["usuario_avatar"] = avatar_path
    
    flash("Perfil atualizado com sucesso!", "sucesso")
    return redirect("/config")

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

# ============================================
# ROTAS DO CARRINHO - VERSÃO MELHORADA
# ============================================

@app.route("/carrinho")
@login_required
def carrinho():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    # Buscar itens com personalização
    cursor.execute("""
        SELECT c.id AS carrinho_id, c.quantidade, c.cor, c.personalizacao,
               p.id AS produto_id, p.nome, p.preco, p.imagem_principal, p.estoque
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.session_id = %s
    """, (session_id,))
    itens = cursor.fetchall()

    # Calcular subtotal
    subtotal = Decimal("0.00")
    for item in itens:
        preco = Decimal(item["preco"])
        quantidade = Decimal(item["quantidade"])
        subtotal += preco * quantidade

    frete = Decimal("12.00") if subtotal > 0 else Decimal("0.00")
    
    # Verificar se há cupom aplicado na sessão
    desconto = Decimal("0.00")
    cupom_info = None
    if 'cupom_codigo' in session:
        cursor.execute("""
            SELECT * FROM cupons 
            WHERE codigo = %s AND ativo = TRUE
            AND (data_expiracao IS NULL OR data_expiracao >= CURDATE())
            AND (uso_maximo IS NULL OR uso_atual < uso_maximo)
        """, (session['cupom_codigo'],))
        cupom = cursor.fetchone()
        
        if cupom:
            if cupom['tipo'] == 'percentual':
                desconto = subtotal * (Decimal(cupom['valor']) / Decimal("100"))
            else:  # fixo
                desconto = Decimal(cupom['valor'])
            
            cupom_info = {
                'codigo': cupom['codigo'],
                'tipo': cupom['tipo'],
                'valor': cupom['valor']
            }
        else:
            # Cupom inválido, remover da sessão
            session.pop('cupom_codigo', None)
    
    total = subtotal + frete - desconto
    if total < 0:
        total = Decimal("0.00")

    cursor.close()
    db.close()

    return render_template("carrinho.html", 
                          itens=itens, 
                          subtotal=subtotal, 
                          frete=frete, 
                          desconto=desconto,
                          cupom_info=cupom_info,
                          total=total)


# ---------------------------
# APLICAR CUPOM
# ---------------------------
@app.route("/carrinho/aplicar_cupom", methods=["POST"])
@login_required
def aplicar_cupom():
    codigo = request.form.get("codigo_cupom", "").strip().upper()
    
    if not codigo:
        flash("Digite um código de cupom.", "erro")
        return redirect(url_for("carrinho"))
    
    db = conectar()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM cupons 
        WHERE codigo = %s AND ativo = TRUE
        AND (data_expiracao IS NULL OR data_expiracao >= CURDATE())
        AND (uso_maximo IS NULL OR uso_atual < uso_maximo)
    """, (codigo,))
    cupom = cursor.fetchone()
    
    cursor.close()
    db.close()
    
    if cupom:
        session['cupom_codigo'] = codigo
        flash(f"Cupom '{codigo}' aplicado com sucesso!", "sucesso")
    else:
        flash("Cupom inválido ou expirado.", "erro")
    
    return redirect(url_for("carrinho"))


# ---------------------------
# REMOVER CUPOM
# ---------------------------
@app.route("/carrinho/remover_cupom")
@login_required
def remover_cupom():
    session.pop('cupom_codigo', None)
    flash("Cupom removido.", "info")
    return redirect(url_for("carrinho"))


# ---------------------------
# ATUALIZAR PERSONALIZAÇÃO
# ---------------------------
@app.route("/carrinho/personalizar/<int:id>", methods=["POST"])
@login_required
def atualizar_personalizacao(id):
    personalizacao = request.form.get("personalizacao", "").strip()
    
    db = conectar()
    cursor = db.cursor()
    
    cursor.execute("""
        UPDATE carrinho 
        SET personalizacao = %s 
        WHERE id = %s
    """, (personalizacao if personalizacao else None, id))
    
    db.commit()
    cursor.close()
    db.close()
    
    flash("Personalização salva!", "sucesso")
    return redirect(url_for("carrinho"))


# ---------------------------
# Atualizar add_carrinho para incluir personalização
# ---------------------------
@app.route("/add_carrinho/<int:produto_id>", methods=["POST"])
def add_carrinho(produto_id):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    qtd_form = int(request.form.get("quantidade", 1))
    cor = request.form.get("cor", "") or ""
    personalizacao = request.form.get("personalizacao", "").strip() or None

    kit_produtos = request.form.getlist("kit_produtos")
    kit_qtds = request.form.getlist("kit_qtds")

    def upsert_carrinho(prod_id, qtd, cor_value="", person_value=None):
        cursor.execute("SELECT estoque FROM produtos WHERE id = %s", (prod_id,))
        r = cursor.fetchone()
        if not r:
            return False, f"Produto {prod_id} não encontrado."

        estoque = int(r["estoque"])

        # Procurar item com mesma session, produto, cor E personalização
        cursor.execute("""
            SELECT id, quantidade FROM carrinho
            WHERE session_id = %s AND produto_id = %s 
            AND IFNULL(cor, '') = %s
            AND IFNULL(personalizacao, '') = %s
        """, (session_id, prod_id, cor_value, person_value or ''))
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
                INSERT INTO carrinho (session_id, produto_id, quantidade, cor, personalizacao)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, prod_id, nova_qtd, cor_value, person_value))

        return True, None

    ok, err = upsert_carrinho(produto_id, qtd_form, cor, personalizacao)
    if not ok:
        flash(err, "erro")
        return redirect(url_for("produto", id=produto_id))

    if kit_produtos and kit_qtds:
        for idx, pid_str in enumerate(kit_produtos):
            try:
                pid = int(pid_str)
                qtd_kit = int(kit_qtds[idx]) if idx < len(kit_qtds) else 1
            except:
                continue
            ok, err = upsert_carrinho(pid, qtd_kit, "", None)
            if not ok:
                flash(f"Erro ao adicionar item do kit: {err}", "erro")

    db.commit()
    cursor.close()
    db.close()
    
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

@app.context_processor
def dados_usuario():
    if "usuario_id" in session:
        db = conectar()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT avatar FROM usuarios WHERE id = %s", (session["usuario_id"],))
        user = cursor.fetchone()
        
        if user and user["avatar"]:
            avatar_path = user["avatar"]
        else:
            avatar_path = "img/user.png"
        
        return {"usuario_avatar": url_for('static', filename=avatar_path)}
    
    return {"usuario_avatar": url_for('static', filename='img/user.png')}
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

        # ✅ AVATAR PADRÃO
        avatar_padrao = "uploads/avatars/user.png"

        # Salvar no banco COM AVATAR PADRÃO
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, avatar) VALUES (%s, %s, %s, %s)",
            (nome, email, senha_hash, avatar_padrao)
        )
        db.commit()

        flash("Conta criada com sucesso! Faça login.", "sucesso")
        return redirect("/login")

    return render_template("cadastro.html")

### 2. **Criar a imagem padrão**



# --------------------------- LOGIN ---------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        db = conectar()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("E-mail não encontrado!", "erro")
            return redirect("/login")

        if not check_password_hash(user["senha"], senha):
            flash("Senha incorreta!", "erro")
            return redirect("/login")

        # ✅ CORRIGIDO: garantir que avatar sempre tenha valor
        session["usuario_id"] = user["id"]
        session["usuario_nome"] = user["nome"]
        session["usuario_avatar"] = user["avatar"] if user["avatar"] else "uploads/avatars/default-avatar.png"
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



@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    session_id = get_session_id()

    # Obter itens do carrinho COM PERSONALIZAÇÃO
    cursor.execute("""
        SELECT c.id AS carrinho_id, c.quantidade, c.cor, c.personalizacao,
               p.id AS produto_id, p.nome, p.preco, p.imagem_principal, p.estoque
        FROM carrinho c
        JOIN produtos p ON p.id = c.produto_id
        WHERE c.session_id = %s
    """, (session_id,))
    itens = cursor.fetchall()

    if request.method == "GET":
        # Se não houver itens, redireciona
        if not itens:
            flash("Seu carrinho está vazio.", "erro")
            cursor.close()
            db.close()
            return redirect(url_for("home"))

        # Calcula subtotal
        subtotal = Decimal("0.00")
        for item in itens:
            preco = Decimal(item["preco"])
            qtd = int(item["quantidade"])
            subtotal += preco * qtd

        # Frete padrão
        frete = Decimal("12.00") if subtotal > 0 else Decimal("0.00")
        
        # ========== VERIFICAR CUPOM APLICADO ==========
        desconto = Decimal("0.00")
        cupom_info = None
        
        if 'cupom_codigo' in session:
            cursor.execute("""
                SELECT * FROM cupons 
                WHERE codigo = %s AND ativo = TRUE
                AND (data_expiracao IS NULL OR data_expiracao >= CURDATE())
                AND (uso_maximo IS NULL OR uso_atual < uso_maximo)
            """, (session['cupom_codigo'],))
            cupom = cursor.fetchone()
            
            if cupom:
                if cupom['tipo'] == 'percentual':
                    desconto = subtotal * (Decimal(cupom['valor']) / Decimal("100"))
                else:  # fixo
                    desconto = Decimal(cupom['valor'])
                
                cupom_info = {
                    'codigo': cupom['codigo'],
                    'tipo': cupom['tipo'],
                    'valor': cupom['valor']
                }
            else:
                # Cupom inválido, remover da sessão
                session.pop('cupom_codigo', None)
        
        total = subtotal + frete - desconto
        if total < 0:
            total = Decimal("0.00")

        # Se usuário logado, buscar endereços e pagamentos salvos
        enderecos = []
        pagamentos = []
        if "usuario_id" in session:
            user_id = session["usuario_id"]
            
            # Endereços
            cursor.execute("""
                SELECT id, nome_destinatario, cpf, rua, numero, bairro, cidade, estado, cep
                FROM enderecos_usuarios
                WHERE usuario_id = %s
                ORDER BY criado_em DESC
            """, (user_id,))
            enderecos = cursor.fetchall()

            # Pagamentos
            cursor.execute("""
                SELECT id, tipo, nome_impresso, numero_mascarado, validade, chave_pix
                FROM pagamentos_usuarios
                WHERE usuario_id = %s
                ORDER BY criado_em DESC
            """, (user_id,))
            pagamentos = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template("checkout.html",
                               itens=itens,
                               subtotal=subtotal,
                               frete=frete,
                               desconto=desconto,
                               cupom_info=cupom_info,
                               total=total,
                               enderecos=enderecos,
                               pagamentos=pagamentos)

    # ============================================================
    # ---------------- POST - PROCESSAR PEDIDO -------------------
    # ============================================================
    
    # Dados básicos do cliente
    nome = request.form.get("nome", "").strip()
    cpf = request.form.get("cpf", "").strip()
    email = request.form.get("email", "").strip()
    telefone = request.form.get("telefone", "").strip()

    # ========== ENDEREÇO ==========
    endereco_selecionado = request.form.get("endereco_selecionado", "novo")

    if endereco_selecionado != "novo":
        # Usa endereço salvo
        cursor.execute("SELECT * FROM enderecos_usuarios WHERE id = %s", (endereco_selecionado,))
        endereco_row = cursor.fetchone()
        if endereco_row:
            rua = endereco_row["rua"]
            numero = endereco_row["numero"]
            bairro = endereco_row["bairro"]
            estado = endereco_row["estado"]
            cidade = endereco_row["cidade"]
            cep = endereco_row["cep"]
            nome_destinatario = endereco_row["nome_destinatario"]
            cpf = endereco_row["cpf"]
        else:
            flash("Endereço selecionado não encontrado.", "erro")
            cursor.close()
            db.close()
            return redirect(url_for("checkout"))
    else:
        # Usa endereço novo do formulário
        rua = request.form.get("rua", "").strip()
        numero = request.form.get("numero", "").strip()
        bairro = request.form.get("bairro", "").strip()
        estado = request.form.get("estado", "").strip()
        cidade = request.form.get("cidade", "").strip()
        cep = request.form.get("cep", "").strip()
        nome_destinatario = nome

    # ========== PAGAMENTO ==========
    pagamento_selecionado = request.form.get("pagamento_selecionado", "pix_padrao")
    
    # Determinar método de pagamento
    metodo_pagamento = None
    pix_chave = None
    cartao_info = {}

    if pagamento_selecionado == "pix_padrao":
        # PIX padrão (sem chave salva)
        metodo_pagamento = "PIX"
        
    elif pagamento_selecionado == "novo":
        # Novo cartão
        metodo_pagamento = "CARTAO"
        
        cartao_num = request.form.get("cartao_num", "").strip()
        cartao_nome = request.form.get("cartao_nome", "").strip()
        cartao_validade = request.form.get("cartao_validade", "").strip()
        cartao_cvv = request.form.get("cartao_cvv", "").strip()
        
        # Validação básica
        cartao_num_digits = re.sub(r"\D", "", cartao_num)
        if len(cartao_num_digits) < 12:
            flash("Número do cartão inválido.", "erro")
            cursor.close()
            db.close()
            return redirect(url_for("checkout"))
        
        cartao_info = {
            "nome_impresso": cartao_nome,
            "numero": cartao_num_digits,
            "numero_mascarado": '**** **** **** ' + cartao_num_digits[-4:],
            "validade": cartao_validade,
            "cvv": cartao_cvv
        }
            
    else:
        # Método salvo - buscar no banco
        cursor.execute("SELECT * FROM pagamentos_usuarios WHERE id = %s", (pagamento_selecionado,))
        p_row = cursor.fetchone()
        
        if p_row:
            metodo_pagamento = p_row.get("tipo")
            if metodo_pagamento == "PIX":
                pix_chave = p_row.get("chave_pix")
            else:
                cartao_info = {
                    "nome_impresso": p_row.get("nome_impresso"),
                    "numero_mascarado": p_row.get("numero_mascarado"),
                    "validade": p_row.get("validade")
                }
        else:
            flash("Método de pagamento não encontrado.", "erro")
            cursor.close()
            db.close()
            return redirect(url_for("checkout"))

    # Validações básicas
    if not nome or not cpf or not rua or not numero or not estado or not cidade or not cep or not metodo_pagamento:
        flash("Preencha todos os campos obrigatórios.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("checkout"))

    # Normaliza cpf/cep
    cpf_digits = re.sub(r"\D", "", cpf)
    cep_digits = re.sub(r"\D", "", cep)

    if len(cpf_digits) != 11:
        flash("CPF inválido. Verifique o formato.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("checkout"))
    if len(cep_digits) != 8:
        flash("CEP inválido. Verifique o formato.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("checkout"))

    # Recalcular total e validar estoque
    subtotal = Decimal("0.00")
    for item in itens:
        preco = Decimal(item["preco"])
        qtd = int(item["quantidade"])
        cursor.execute("SELECT estoque FROM produtos WHERE id = %s", (item["produto_id"],))
        estoque_row = cursor.fetchone()
        if not estoque_row:
            flash("Produto não encontrado durante checkout.", "erro")
            cursor.close()
            db.close()
            return redirect(url_for("carrinho"))
        estoque = int(estoque_row["estoque"])
        if qtd > estoque:
            flash(f"Quantidade do produto {item['nome']} maior que o estoque ({estoque}).", "erro")
            cursor.close()
            db.close()
            return redirect(url_for("carrinho"))
        subtotal += preco * Decimal(qtd)

    # ========== CALCULAR FRETE (GRÁTIS SE SC E > R$129,90) ==========
    frete = Decimal("12.00")
    estado_limpo = estado.strip().upper()
    
    if estado_limpo == "SC" and subtotal > Decimal("129.90"):
        frete = Decimal("0.00")
    
    # ========== APLICAR CUPOM DE DESCONTO ==========
    desconto = Decimal("0.00")
    cupom_usado = None
    cupom_id = None
    
    if 'cupom_codigo' in session:
        cursor.execute("""
            SELECT * FROM cupons 
            WHERE codigo = %s AND ativo = TRUE
            AND (data_expiracao IS NULL OR data_expiracao >= CURDATE())
            AND (uso_maximo IS NULL OR uso_atual < uso_maximo)
        """, (session['cupom_codigo'],))
        cupom = cursor.fetchone()
        
        if cupom:
            if cupom['tipo'] == 'percentual':
                desconto = subtotal * (Decimal(cupom['valor']) / Decimal("100"))
            else:  # fixo
                desconto = Decimal(cupom['valor'])
            
            cupom_usado = cupom['codigo']
            cupom_id = cupom['id']
    
    # Calcular total final
    total = subtotal + frete - desconto
    if total < 0:
        total = Decimal("0.00")

    # Monta endereço completo
    endereco_texto = f"{rua}, {numero}" + (f" - {bairro}" if bairro else "") + f" - {cidade}/{estado} - CEP {cep_digits}"

    # ========== SALVAR ENDEREÇO SE MARCADO ==========
    lembrar_endereco = request.form.get("lembrar_endereco")
    user_id = session.get("usuario_id")

    if lembrar_endereco and user_id and endereco_selecionado == "novo":
        try:
            cursor.execute("""
                INSERT INTO enderecos_usuarios 
                (usuario_id, nome_destinatario, cpf, rua, numero, bairro, cidade, estado, cep)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, nome_destinatario, cpf_digits, rua, numero, bairro, cidade, estado, cep_digits))
            db.commit()
        except Exception as e:
            print("Erro salvando endereço:", e)
            db.rollback()

    # ========== CRIAR PEDIDO COM CUPOM ==========
    try:
        usuario_for_insert = user_id if user_id else None

        cursor.execute("""
            INSERT INTO pedidos (usuario_id, valor_total, status, pagamento_metodo, 
                                 cliente_nome, cliente_cpf, cliente_endereco, 
                                 cupom_usado, desconto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (usuario_for_insert, str(total), "aguardando_pagamento", metodo_pagamento, 
              nome_destinatario or nome, cpf_digits, endereco_texto, 
              cupom_usado, str(desconto)))
        db.commit()
    except Exception as e:
        db.rollback()
        flash("Erro ao criar pedido. Tente novamente.", "erro")
        print("Erro INSERT pedidos:", e)
        cursor.close()
        db.close()
        return redirect(url_for("checkout"))

    pedido_id = cursor.lastrowid

    # ========== INSERIR ITENS COM PERSONALIZAÇÃO E REDUZIR ESTOQUE ==========
    try:
        for item in itens:
            produto_id = item["produto_id"]
            qtd = int(item["quantidade"])
            preco = Decimal(item["preco"])
            personalizacao = item.get("personalizacao")

            cursor.execute("""
                INSERT INTO pedido_itens (pedido_id, produto_id, quantidade, valor, personalizacao)
                VALUES (%s, %s, %s, %s, %s)
            """, (pedido_id, produto_id, qtd, str(preco), personalizacao))

            cursor.execute("UPDATE produtos SET estoque = estoque - %s WHERE id = %s", (qtd, produto_id))

        # ========== INCREMENTAR USO DO CUPOM ==========
        if cupom_id:
            cursor.execute("""
                UPDATE cupons SET uso_atual = uso_atual + 1 
                WHERE id = %s
            """, (cupom_id,))

        # ========== SALVAR MÉTODO DE PAGAMENTO SE MARCADO ==========
        lembrar_pagamento = request.form.get("lembrar_pagamento")

        if lembrar_pagamento and user_id and pagamento_selecionado == "novo":
            if metodo_pagamento == "CARTAO" and cartao_info:
                cursor.execute("""
                    INSERT INTO pagamentos_usuarios (usuario_id, tipo, nome_impresso, numero_mascarado, validade)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, 'CARTAO', cartao_info["nome_impresso"], cartao_info["numero_mascarado"], cartao_info["validade"]))

        # Limpar carrinho
        cursor.execute("DELETE FROM carrinho WHERE session_id = %s", (session_id,))
        
        # Remover cupom da sessão após usar
        session.pop('cupom_codigo', None)
        
        db.commit()

    except Exception as e:
        db.rollback()
        flash("Erro ao processar itens do pedido. Contate o suporte.", "erro")
        print("Erro pedido_itens/estoque:", e)
        cursor.close()
        db.close()
        return redirect(url_for("carrinho"))

    cursor.close()
    db.close()

    flash("Pedido criado com sucesso!", "sucesso")
    
    # Se for PIX, redireciona para página de pagamento PIX
    if metodo_pagamento == "PIX":
        return redirect(url_for("pagamento_pix", pedido_id=pedido_id))
    else:
        # Se for CARTÃO, vai direto para pedido finalizado com flag de pagamento
        return redirect(url_for("pedido_finalizado", pedido_id=pedido_id) + "?pago=true")


# ============================================================
# ROTA: PÁGINA DE PAGAMENTO PIX
# ============================================================
@app.route("/pagamento_pix/<int:pedido_id>")
def pagamento_pix(pedido_id):
    """
    Exibe a tela de pagamento PIX com QR Code e timer
    """
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Buscar dados do pedido
    cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        flash("Pedido não encontrado.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("home"))

    # Verificar se é pagamento PIX
    if pedido["pagamento_metodo"] != "PIX":
        flash("Este pedido não é pagamento via PIX.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("pedido_finalizado", pedido_id=pedido_id))

    cursor.close()
    db.close()

    return render_template("pagamento_pix.html", pedido=pedido)


# ============================================================
# ROTA: PÁGINA DE PEDIDO FINALIZADO (NOTA FISCAL)
# ============================================================
@app.route("/pedido_finalizado/<int:pedido_id>")
def pedido_finalizado(pedido_id):
    """
    Exibe a nota fiscal / cupom fiscal do pedido
    Mostra mensagem de confirmação se vier com ?pago=true
    """
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Buscar dados do pedido
    cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        flash("Pedido não encontrado.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("home"))

    # Buscar itens do pedido com informações do produto
    cursor.execute("""
        SELECT pi.*, p.nome, p.imagem_principal
        FROM pedido_itens pi
        JOIN produtos p ON p.id = pi.produto_id
        WHERE pi.pedido_id = %s
    """, (pedido_id,))
    itens = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("pedido_finalizado.html", pedido=pedido, itens=itens)


# ============================================================
# ROTA OPCIONAL: VERIFICAR PAGAMENTO PIX (SIMULAÇÃO)
# ============================================================
@app.route("/verificar_pagamento_pix/<int:pedido_id>")
def verificar_pagamento_pix(pedido_id):
    """
    ROTA OPCIONAL: Simula verificação de pagamento PIX
    Em produção, você integraria com API do banco (Mercado Pago, PagSeguro, etc)
    """
    db = conectar()
    cursor = db.cursor(dictionary=True)

    # Buscar pedido
    cursor.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
    pedido = cursor.fetchone()

    if not pedido:
        flash("Pedido não encontrado.", "erro")
        cursor.close()
        db.close()
        return redirect(url_for("home"))

    # SIMULAÇÃO: Em produção, aqui você consultaria a API do banco
    # Por enquanto, apenas atualiza o status para "em_analise"
    
    try:
        cursor.execute("""
            UPDATE pedidos 
            SET status = 'em_analise'
            WHERE id = %s
        """, (pedido_id,))
        db.commit()
        
        flash("Pagamento recebido! Aguarde aprovação do administrador.", "sucesso")
    except Exception as e:
        db.rollback()
        flash("Erro ao verificar pagamento.", "erro")
        print("Erro ao atualizar status:", e)

    cursor.close()
    db.close()

    return redirect(url_for("pedido_finalizado", pedido_id=pedido_id) + "?pago=true")


# ============================================================
# ROTA: MEUS PEDIDOS (Se ainda não existir)
# ============================================================
@app.route("/meus_pedidos")
def meus_pedidos():
    """
    Lista todos os pedidos do usuário logado
    """
    if "usuario_id" not in session:
        flash("Faça login para ver seus pedidos.", "erro")
        return redirect(url_for("login"))

    db = conectar()
    cursor = db.cursor(dictionary=True)

    user_id = session["usuario_id"]

    # Buscar pedidos do usuário
    cursor.execute("""
        SELECT * FROM pedidos 
        WHERE usuario_id = %s 
        ORDER BY criado_em DESC
    """, (user_id,))
    pedidos = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("meus_pedidos.html", pedidos=pedidos)

@app.route("/perfil")
@login_required
def perfil():
    user_id = session["usuario_id"]

    db = conectar()
    cursor = db.cursor(dictionary=True)

    # usuário
    cursor.execute("SELECT id, nome, avatar, criado_em FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()

    # 🔥 Ajuste DEFINITIVO do avatar
    if usuario and usuario["avatar"]:
        avatar = usuario["avatar"].strip()  # remove espaços, \n etc

        # Se não começar com /static, vamos normalizar
        if not avatar.startswith("/static"):
            # remove "/uploads" duplicado se existir
            avatar = avatar.replace("static/", "").replace("/static", "").replace("uploads", "").strip("/")
            # monta caminho correto
            avatar = "/static/uploads/avatars/" + usuario["avatar"].split("/")[-1]

        usuario["avatar"] = avatar



    # pedidos
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY criado_em DESC", (user_id,))
    pedidos = cursor.fetchall()

    # favoritos (mantive como antes)
    cursor.execute("""
        SELECT produtos.nome, produtos.imagem_principal
        FROM favoritos
        JOIN produtos ON produtos.id = favoritos.produto_id
        WHERE favoritos.usuario_id = %s
    """, (user_id,))
    favoritos = cursor.fetchall()

    # endereços salvos
    cursor.execute("""
        SELECT id, nome_destinatario, cpf, rua, numero, bairro, cidade, estado, cep, criado_em
        FROM enderecos_usuarios
        WHERE usuario_id = %s
        ORDER BY criado_em DESC
    """, (user_id,))
    enderecos = cursor.fetchall()

    # métodos de pagamento salvos
    cursor.execute("""
        SELECT id, tipo, nome_impresso, numero_mascarado, validade, chave_pix, criado_em
        FROM pagamentos_usuarios
        WHERE usuario_id = %s
        ORDER BY criado_em DESC
    """, (user_id,))
    pagamentos = cursor.fetchall()

    cursor.close()
    db.close()

    # passar pro template
    return render_template("perfil.html",
                           usuario=usuario,
                           pedidos=pedidos,
                           favoritos=favoritos,
                           enderecos=enderecos,
                           pagamentos=pagamentos,
                           avatar = avatar)

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


# Alterar senha
# Alterar senha
# Alterar senha
@app.route('/config/alterar-senha', methods=['POST'])
def alterar_senha():
    if 'usuario_id' not in session:
        return redirect('/login')
    
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    print(f"🔍 DEBUG 1 - Senha atual digitada: [{senha_atual}]")
    print(f"🔍 DEBUG 2 - Nova senha: [{nova_senha}]")
    
    # Validar se as novas senhas coincidem
    if nova_senha != confirmar_senha:
        flash('As senhas não coincidem!', 'erro')
        return redirect('/config')
    
    # Validar comprimento mínimo
    if len(nova_senha) < 6:
        flash('A senha deve ter no mínimo 6 caracteres!', 'erro')
        return redirect('/config')
    
    # Conectar ao banco
    db = conectar()
    cursor = db.cursor(dictionary=True)
    
    # Buscar a senha atual do usuário
    cursor.execute('SELECT senha FROM usuarios WHERE id = %s', (session['usuario_id'],))
    usuario = cursor.fetchone()
    
    print(f"🔍 DEBUG 3 - Usuário encontrado: {usuario is not None}")
    if usuario:
        print(f"🔍 DEBUG 4 - Hash no banco (primeiros 50 caracteres): {usuario['senha'][:50] if usuario['senha'] else 'VAZIO'}...")
        print(f"🔍 DEBUG 5 - Tamanho do hash: {len(usuario['senha']) if usuario['senha'] else 0}")
    
    if not usuario:
        flash('Usuário não encontrado!', 'erro')
        cursor.close()
        db.close()
        return redirect('/config')
    
    # VERIFICAR SE A SENHA ATUAL ESTÁ CORRETA
    resultado_check = check_password_hash(usuario['senha'], senha_atual)
    print(f"🔍 DEBUG 6 - Resultado do check_password_hash: {resultado_check}")
    
    if not resultado_check:
        print("🔍 DEBUG 7 - SENHA INCORRETA! Deveria parar aqui...")
        flash('Senha atual incorreta!', 'erro')
        cursor.close()
        db.close()
        return redirect('/config')
    
    print("🔍 DEBUG 8 - Senha correta! Prosseguindo com alteração...")
    
    # Se chegou aqui, tudo está OK - pode alterar a senha
    nova_senha_hash = generate_password_hash(nova_senha)
    cursor.execute('UPDATE usuarios SET senha = %s WHERE id = %s', 
                   (nova_senha_hash, session['usuario_id']))
    db.commit()
    cursor.close()
    db.close()
    
    print("🔍 DEBUG 9 - Senha alterada com sucesso!")
    flash('Senha alterada com sucesso!', 'sucesso')
    return redirect('/config')
# Atualizar endereço
@app.route("/config/atualizar-endereco", methods=["POST"])
def atualizar_endereco():
    # Salvar endereço no banco
    flash("Endereço atualizado!", "sucesso")
    return redirect("/config")

# Excluir conta
@app.route("/config/excluir-conta")
def excluir_conta():
    if "usuario_id" not in session:
        return redirect("/login")
    
    user_id = session["usuario_id"]
    db = conectar()
    cursor = db.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
    db.commit()
    
    session.clear()
    flash("Conta excluída com sucesso.", "sucesso")
    return redirect("/")

# Rota GET da página
@app.route("/config")
def config():
    if "usuario_id" not in session:
        flash("Você precisa estar logado!", "erro")
        return redirect("/login")
    
    user_id = session["usuario_id"]
    
    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT nome, email, avatar FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    
    # Atualizar sessão com dados atuais
    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]
    session["usuario_avatar"] = usuario["avatar"]
    
    return render_template("config.html", usuario=usuario)

@app.route("/perfil/excluir-pedido/<int:pedido_id>", methods=["POST"])
def excluir_pedido(pedido_id):
    if "usuario_id" not in session:
        return jsonify({"sucesso": False, "erro": "Não logado"}), 401
    
    user_id = session["usuario_id"]
    
    db = conectar()
    cursor = db.cursor(dictionary=True)
    
    # Verificar se o pedido pertence ao usuário
    cursor.execute("SELECT usuario_id FROM pedidos WHERE id = %s", (pedido_id,))
    pedido = cursor.fetchone()
    
    if not pedido:
        return jsonify({"sucesso": False, "erro": "Pedido não encontrado"})
    
    if pedido["usuario_id"] != user_id:
        return jsonify({"sucesso": False, "erro": "Pedido não pertence ao usuário"})
    
    # Excluir pedido (CASCADE vai deletar os itens automaticamente)
    cursor.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
    db.commit()
    
    return jsonify({"sucesso": True})
# ============================
# ROTAS DE FAVORITOS
# ============================

@app.route("/favorito/adicionar/<int:produto_id>", methods=["POST"])
@login_required
def adicionar_favorito(produto_id):
    """Adiciona produto aos favoritos"""
    user_id = session["usuario_id"]
    
    db = conectar()
    cursor = db.cursor(dictionary=True)
    
    # Verificar se produto existe
    cursor.execute("SELECT id FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()
    
    if not produto:
        flash("Produto não encontrado!", "erro")
        return redirect(url_for("home"))
    
    # Verificar se já está nos favoritos
    cursor.execute("""
        SELECT id FROM favoritos 
        WHERE usuario_id = %s AND produto_id = %s
    """, (user_id, produto_id))
    
    ja_existe = cursor.fetchone()
    
    if ja_existe:
        flash("Este produto já está nos seus favoritos!", "info")
    else:
        # Adicionar aos favoritos
        cursor.execute("""
            INSERT INTO favoritos (usuario_id, produto_id)
            VALUES (%s, %s)
        """, (user_id, produto_id))
        db.commit()
        flash("Produto adicionado aos favoritos! ❤️", "sucesso")
    
    cursor.close()
    db.close()
    
    return redirect(url_for("produto", id=produto_id))


@app.route("/favorito/remover/<int:produto_id>", methods=["POST"])
@login_required
def remover_favorito(produto_id):
    """Remove produto dos favoritos"""
    user_id = session["usuario_id"]
    
    db = conectar()
    cursor = db.cursor()
    
    cursor.execute("""
        DELETE FROM favoritos 
        WHERE usuario_id = %s AND produto_id = %s
    """, (user_id, produto_id))
    
    db.commit()
    cursor.close()
    db.close()
    
    flash("Produto removido dos favoritos.", "info")
    return redirect(url_for("produto", id=produto_id))


# ============================
# API DE FAVORITOS (para o perfil.html)
# ============================

@app.route("/api/favoritos")
@login_required
def api_favoritos():
    """API JSON que retorna os favoritos do usuário"""
    user_id = session["usuario_id"]
    
    db = conectar()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.id, p.nome, p.preco, p.imagem_principal, f.criado_em
        FROM favoritos f
        JOIN produtos p ON p.id = f.produto_id
        WHERE f.usuario_id = %s
        ORDER BY f.criado_em DESC
    """, (user_id,))
    
    favoritos = cursor.fetchall()
    
    # Converter Decimal para float para JSON
    for fav in favoritos:
        fav['preco'] = float(fav['preco'])
        fav['criado_em'] = fav['criado_em'].strftime('%Y-%m-%d %H:%M:%S')
        # ✅ CORREÇÃO: Usar o caminho direto do banco
        # O banco já tem o caminho completo: /static/img/...
    
    cursor.close()
    db.close()
    
    return jsonify(favoritos)

# ============================
# CONTEXT PROCESSOR - Verificar se produto está nos favoritos
# ============================

@app.context_processor
def verificar_favorito():
    """Adiciona função para verificar se produto está nos favoritos"""
    def is_favorito(produto_id):
        if "usuario_id" not in session:
            return False
        
        user_id = session["usuario_id"]
        
        db = conectar()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id FROM favoritos 
            WHERE usuario_id = %s AND produto_id = %s
        """, (user_id, produto_id))
        
        resultado = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        return resultado is not None
    
    return {"is_favorito": is_favorito}

@app.route('/salvar_endereco', methods=['POST'])
@login_required
def salvar_endereco():
    usuario_id = session['usuario_id']

    nome_destinatario = request.form.get('nome_destinatario', '').strip()
    cpf = request.form.get('cpf', '').strip()
    rua = request.form.get('rua', '').strip()
    numero = request.form.get('numero', '').strip()
    bairro = request.form.get('bairro', '').strip()
    cidade = request.form.get('cidade', '').strip()
    estado = request.form.get('estado', '').strip()
    cep = request.form.get('cep', '').strip()

    # validações mínimas server-side
    cpf_digits = re.sub(r"\D", "", cpf)
    cep_digits = re.sub(r"\D", "", cep)
    if len(cpf_digits) != 11 or len(cep_digits) != 8 or not rua or not numero or not cidade or not estado:
        flash("Preencha corretamente os campos obrigatórios (CPF/CEP/Endereço).", "erro")
        return redirect(url_for("perfil"))

    db = conectar()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO enderecos_usuarios 
        (usuario_id, nome_destinatario, cpf, rua, numero, bairro, cidade, estado, cep)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (usuario_id, nome_destinatario, cpf_digits, rua, numero, bairro, cidade, estado.upper(), cep_digits))
    db.commit()
    cursor.close()
    db.close()

    flash("Endereço salvo com sucesso!", "sucesso")
    return redirect(url_for("perfil"))

@app.route('/excluir_endereco/<int:endereco_id>', methods=['POST'])
@login_required
def excluir_endereco(endereco_id):
    usuario_id = session['usuario_id']

    db = conectar()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM enderecos_usuarios 
        WHERE id = %s AND usuario_id = %s
    """, (endereco_id, usuario_id))
    db.commit()
    cursor.close()
    db.close()

    flash("Endereço removido.", "info")
    return redirect(url_for("perfil"))

@app.route('/salvar_pagamento', methods=['POST'])
@login_required
def salvar_pagamento():
    usuario_id = session['usuario_id']
    tipo = request.form.get('tipo')

    db = conectar()
    cursor = db.cursor()

    if tipo == 'PIX':
        chave_pix = request.form.get('chave_pix', '').strip()
        if not chave_pix:
            flash("Informe a chave PIX.", "erro")
            return redirect(url_for("perfil"))
        cursor.execute("""
            INSERT INTO pagamentos_usuarios (usuario_id, tipo, chave_pix)
            VALUES (%s, %s, %s)
        """, (usuario_id, 'PIX', chave_pix))

    elif tipo == 'CARTAO':
        nome_impresso = request.form.get('nome_impresso', '').strip()
        numero = request.form.get('numero', '').strip()
        validade = request.form.get('validade', '').strip()

        # validação simples
        numero_digits = re.sub(r"\D", "", numero)
        if len(numero_digits) < 12:
            flash("Número do cartão inválido.", "erro")
            return redirect(url_for("perfil"))

        numero_mascarado = '**** **** **** ' + numero_digits[-4:]
        cursor.execute("""
            INSERT INTO pagamentos_usuarios 
            (usuario_id, tipo, nome_impresso, numero_mascarado, validade)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, 'CARTAO', nome_impresso, numero_mascarado, validade))
    else:
        flash("Método inválido.", "erro")
        return redirect(url_for("perfil"))

    db.commit()
    cursor.close()
    db.close()

    flash("Método de pagamento salvo!", "sucesso")
    return redirect(url_for("perfil"))

@app.route('/excluir_pagamento/<int:pid>', methods=['POST'])
@login_required
def excluir_pagamento(pid):
    usuario_id = session['usuario_id']

    db = conectar()
    cursor = db.cursor()
    cursor.execute("""
        DELETE FROM pagamentos_usuarios 
        WHERE id = %s AND usuario_id = %s
    """, (pid, usuario_id))
    db.commit()
    cursor.close()
    db.close()

    flash("Método de pagamento removido.", "info")
    return redirect(url_for("perfil"))

# ===== ROTA 404 - PÁGINA NÃO ENCONTRADA =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Helper: enviar email (Gmail via SSL)
def enviar_email_codigo(destino_email, nome_destinatario, codigo):
    if not SMTP_USER or not SMTP_PASS:
        print("ERRO: SMTP_USER ou SMTP_PASS não definidos!")
        return False

    assunto = "AguaPura — Código de recuperação de senha"
    corpo_html = f"""
    <html>
      <body style="font-family:Arial,Helvetica,sans-serif;color:#222">
        <div style="max-width:600px;margin:0 auto;padding:20px;border-radius:8px;background:#f8f9fb">
          <h2 style="color:#0d6efd">Recuperação de senha — AguaPura</h2>
          <p>Olá {nome_destinatario},</p>
          <p>Use o código abaixo para alterar sua senha. Este código expira em {CODIGO_EXPIRACAO_MIN} minutos.</p>
          <div style="font-size:1.6rem;font-weight:700;background:#fff;padding:12px 18px;border-radius:6px;display:inline-block;border:1px solid #e6eefc">
            {codigo}
          </div>
          <p style="margin-top:18px">Se não foi você, ignore este e-mail.</p>
          <p>Equipe AguaPura</p>
        </div>
      </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"] = SMTP_USER
    msg["To"] = destino_email
    msg.set_content(f"Código de recuperação: {codigo}")
    msg.add_alternative(corpo_html, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as smtp:
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)



# ROTA: Formulário "Esqueci minha senha" (GET) e envio do código (POST)
@app.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            flash("Informe seu e-mail", "warning")
            return redirect(url_for("esqueci_senha"))

        db = conectar()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, email FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if not usuario:
            # Não expor se o e-mail existe — retornar mensagem genérica
            flash("Se o e-mail existir no sistema, um código foi enviado.", "info")
            cursor.close()
            db.close()
            return redirect(url_for("login"))  # ou ficar na mesma página

        # gera código de 6 dígitos
        codigo = f"{random.randint(100000, 999999)}"
        from datetime import datetime, timedelta, timezone
        expiracao = datetime.now(timezone.utc) + timedelta(minutes=CODIGO_EXPIRACAO_MIN)



        # salva no banco
        cursor.execute("""
            INSERT INTO recuperacao_senha (usuario_id, codigo, expiracao, ip_solicitante)
            VALUES (%s, %s, %s, %s)
        """, (usuario["id"], codigo, expiracao, request.remote_addr))
        db.commit()

        # envia email (pode levantar exception se smtp falhar)
        try:
            enviar_email_codigo(usuario["email"], usuario["nome"], codigo)
        except Exception as e:
            # opcional: apagar o registro de recuperacao se o envio falhar
            cursor.execute("DELETE FROM recuperacao_senha WHERE usuario_id = %s AND codigo = %s", (usuario["id"], codigo))
            db.commit()
            cursor.close()
            db.close()
            flash("Erro ao enviar email. Verifique as configurações de SMTP.", "danger")
            # log do erro no servidor
            print("Erro SMTP:", e)
            return redirect(url_for("esqueci_senha"))

        cursor.close()
        db.close()
        flash("Se o e-mail existir no sistema, um código foi enviado. Verifique sua caixa de entrada.", "success")
        # redireciona para página de verificação de código (opcional: passar user_id via session)
        session["recuperacao_usuario_id"] = usuario["id"]
        return redirect(url_for("verificar_codigo"))

    return render_template("esqueci_senha.html")


# ROTA: Verificar código (GET mostra o form, POST valida)
@app.route("/verificar-codigo", methods=["GET", "POST"])
def verificar_codigo():
    usuario_id = session.get("recuperacao_usuario_id")
    if not usuario_id:
        flash("Inicie o processo informando seu e-mail.", "warning")
        return redirect(url_for("esqueci_senha"))

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        if not codigo:
            flash("Informe o código enviado por e-mail.", "warning")
            return redirect(url_for("verificar_codigo"))

        db = conectar()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, codigo, expiracao, usado FROM recuperacao_senha
            WHERE usuario_id = %s AND codigo = %s
            ORDER BY criado_em DESC LIMIT 1
        """, (usuario_id, codigo))
        rec = cursor.fetchone()

        if not rec:
            flash("Código inválido.", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("verificar_codigo"))

        # verifica expiracao e se ja foi usado
        agora = datetime.utcnow()
        expiracao_dt = rec["expiracao"]
        if isinstance(expiracao_dt, str):
            expiracao_dt = datetime.fromisoformat(expiracao_dt)

        if rec["usado"]:
            flash("Este código já foi utilizado.", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("esqueci_senha"))

        if agora > expiracao_dt:
            flash("Código expirado. Solicite um novo código.", "warning")
            cursor.close()
            db.close()
            return redirect(url_for("esqueci_senha"))

        # Código válido → setar flag na session e redirecionar para trocar senha
        session["recuperacao_validada"] = True
        session["recuperacao_codigo_id"] = rec["id"]
        cursor.close()
        db.close()
        return redirect(url_for("trocar_senha"))

    return render_template("verificar_codigo.html")


# ROTA: Trocar senha (GET mostra form, POST aplica a troca)
@app.route("/trocar-senha", methods=["GET", "POST"])
def trocar_senha():
    # validações
    usuario_id = session.get("recuperacao_usuario_id")
    validado = session.get("recuperacao_validada")
    codigo_id = session.get("recuperacao_codigo_id")

    if not usuario_id or not validado or not codigo_id:
        flash("Sessão inválida. Inicie o processo novamente.", "warning")
        return redirect(url_for("esqueci_senha"))

    if request.method == "POST":
        nova = request.form.get("senha", "")
        confirmar = request.form.get("confirmar", "")
        if not nova or not confirmar:
            flash("Preencha ambos campos.", "warning")
            return redirect(url_for("trocar_senha"))
        if nova != confirmar:
            flash("As senhas não conferem.", "danger")
            return redirect(url_for("trocar_senha"))
        if len(nova) < 6:
            flash("Senha muito curta (mínimo 6 caracteres).", "warning")
            return redirect(url_for("trocar_senha"))

        # opcional: checar força da senha aqui

        # Hash da nova senha (usar mesma abordagem do seu sistema).
        # Aqui usamos werkzeug.generate_password_hash (PBKDF2) — você pode trocar para scrypt se quiser.
        nova_hash = generate_password_hash(nova)  # padrão: pbkdf2:sha256

        db = conectar()
        cursor = db.cursor()
        # Atualiza a senha do usuário
        cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (nova_hash, usuario_id))
        # Marca o código como usado
        cursor.execute("UPDATE recuperacao_senha SET usado = 1 WHERE id = %s", (codigo_id,))
        db.commit()
        cursor.close()
        db.close()

        # limpa dados de sessão do fluxo de recuperação
        session.pop("recuperacao_usuario_id", None)
        session.pop("recuperacao_validada", None)
        session.pop("recuperacao_codigo_id", None)

        flash("Senha alterada com sucesso. Faça login com a nova senha.", "success")
        return redirect(url_for("login"))

    return render_template("trocar_senha.html")

# ============================
# AJUSTAR ESTOQUE - ROTA PARA O MODAL
# ============================



# ROTA DE AJUSTE DE ESTOQUE
@app.route("/admin/estoque/ajustar", methods=["POST"])
@admin_required
def admin_ajustar_estoque():
    """Ajusta o estoque de um produto (adicionar, remover ou definir)"""
    try:
        produto_id = int(request.form.get("produto_id"))
        quantidade = int(request.form.get("quantidade"))
        tipo = request.form.get("tipo")
        
        if quantidade < 0:
            flash("Quantidade inválida!", "erro")
            return redirect("/funcionario/estoque")
        
        db = conectar()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT estoque, nome FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()
        
        if not produto:
            flash("Produto não encontrado!", "erro")
            cursor.close()
            db.close()
            return redirect("/funcionario/estoque")
        
        estoque_atual = int(produto["estoque"])
        nome_produto = produto["nome"]
        
        # Calcular novo estoque
        if tipo == "adicionar":
            novo_estoque = estoque_atual + quantidade
            msg = f"✅ {quantidade} unidades adicionadas ao estoque de '{nome_produto}'"
            
        elif tipo == "remover":
            novo_estoque = estoque_atual - quantidade
            if novo_estoque < 0:
                flash(f"❌ Estoque insuficiente! Disponível: {estoque_atual}", "erro")
                cursor.close()
                db.close()
                return redirect("/funcionario/estoque")
            msg = f"✅ {quantidade} unidades removidas do estoque de '{nome_produto}'"
            
        elif tipo == "definir":
            novo_estoque = quantidade
            msg = f"✅ Estoque de '{nome_produto}' definido para {quantidade} unidades"
            
        else:
            flash("Tipo de ajuste inválido!", "erro")
            cursor.close()
            db.close()
            return redirect("/funcionario/estoque")
        
        # Atualizar no banco
        cursor.execute("UPDATE produtos SET estoque = %s WHERE id = %s", (novo_estoque, produto_id))
        db.commit()
        
        print(f"✅ Estoque atualizado: {nome_produto} → {estoque_atual} para {novo_estoque}")
        
        cursor.close()
        db.close()
        
        flash(msg, "sucesso")
        return redirect("/funcionario/estoque")
        
    except ValueError:
        flash("Erro nos valores informados!", "erro")
        return redirect("/funcionario/estoque")
    except Exception as e:
        flash(f"Erro ao ajustar estoque: {str(e)}", "erro")
        print(f"❌ ERRO: {e}")
        return redirect("/funcionario/estoque")

    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
