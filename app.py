import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('artesa.db')
    cursor = conn.cursor()
    
    # Tabela de Produtos (Catálogo - Tela 1)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            cor TEXT NOT NULL,
            imagem TEXT NOT NULL
        )
    ''')
    
    # Tabela de Encomendas (Telas 2 e 3)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS encomendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            telefone TEXT,
            produto_id INTEGER,
            data_pedido TEXT NOT NULL,
            prazo_entrega TEXT NOT NULL,
            status TEXT DEFAULT 'Pendente',
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Inserir produtos iniciais se a tabela estiver vazia (para popular a Tela 1)
    cursor.execute('SELECT COUNT(*) FROM produtos')
    if cursor.fetchone()[0] == 0:
        produtos_iniciais = [
            ('Bolsa Marrom com Tassel', 150.00, 'Marrom', 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=300'),
            ('Bolsa Branca Texturizada', 200.00, 'Branco', 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=300'),
            ('Bolsa Preta Executiva', 250.00, 'Preto', 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=300'),
            ('Bolsa Bege Clássica', 180.00, 'Bege', 'https://images.unsplash.com/photo-1591561954557-26941169b49e?w=300')
        ]
        cursor.executemany('INSERT INTO produtos (nome, preco, cor, imagem) VALUES (?, ?, ?, ?)', produtos_iniciais)
        conn.commit()
        
    conn.close()

# Templates HTML integrados com o design system do Ateliê A. Lorena
LAYOUT_BASE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A. Lorena Handmade</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #dcd6cd;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .smartphone-container {
            width: 100%;
            max-width: 400px;
            background-color: #f4f1ea;
            border-radius: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
            border: 10px solid #2b2b2b;
            display: flex;
            flex-direction: column;
            min-height: 750px;
        }
        header {
            background-color: #e3ded5;
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid #d0c8be;
        }
        header h1 {
            font-family: serif;
            margin: 0;
            color: #4a3b32;
            font-size: 22px;
        }
        header span {
            font-size: 11px;
            letter-spacing: 2px;
            color: #7a6b62;
            text-transform: uppercase;
        }
        .content {
            padding: 15px;
            overflow-y: auto;
            flex: 1;
        }
        .btn-primary {
            background-color: #2b70e4;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
            text-align: center;
            display: block;
            text-decoration: none;
            font-size: 15px;
            margin-top: 15px;
        }
        .alert-success {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 15px;
            border: 1px solid #c3e6cb;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="smartphone-container">
        <header>
            <h1>A. Lorena</h1>
            <span>Handmade</span>
        </header>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
'''

# Rota 1: Menu Inicial e Catálogo de Produtos (Tela 1)[cite: 14]
@app.route('/')
def index():
    busca = request.args.get('q', '')
    conn = sqlite3.connect('artesa.db')
    cursor = conn.cursor()
    if busca:
        cursor.execute("SELECT * FROM produtos WHERE nome LIKE ? OR cor LIKE ?", (f'%{busca}%', f'%{busca}%'))
    else:
        cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    
    html = LAYOUT_BASE.replace('{% block content %}{% endblock %}', '''
    <div style="margin-bottom: 15px;">
        <form method="GET" action="/">
            <input type="text" name="q" placeholder="Buscar Bolsas..." value="'''+busca+'''" style="width: 100%; padding: 10px; border-radius: 20px; border: 1px solid #ccc; box-sizing: border-box;">
        </form>
    </div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        {% for p in produtos %}
        <div style="background: white; padding: 10px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <img src="{{ p[4] }}" alt="{{ p[1] }}" style="width: 100%; height: 100px; object-fit: cover; border-radius: 6px;">
            <div style="font-size: 12px; font-weight: bold; margin-top: 5px; color: #333;">{{ p[1] }}</div>
            <div style="font-size: 11px; color: #666; margin-top: 2px;">preço: R$ {{ "%.2f"|format(p[2]) }}</div>
            <div style="font-size: 11px; color: #666;">cor: {{ p[3] }}</div>
        </div>
        {% endfor %}
    </div>
    
    <a href="/nova-encomenda" class="btn-primary" style="margin-top: 25px; background-color: #1a73e8;">+ NOVA ENCOMENDA</a>
    ''')
    return render_template_string(html, produtos=produtos)

# Rota 2: Formulário de Registro de Encomenda (Tela 2)[cite: 15]
@app.route('/nova-encomenda', methods=['GET', 'POST'])
def nova_encomenda():
    conn = sqlite3.connect('artesa.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        cliente = request.form['cliente']
        telefone = request.form['telefone']
        produto_id = request.form['produto_id']
        data_pedido = request.form['data_pedido']
        prazo_entrega = request.form['prazo_entrega']
        
        cursor.execute('''
            INSERT INTO encomendas (cliente, telefone, produto_id, data_pedido, prazo_entrega, status)
            VALUES (?, ?, ?, ?, ?, 'Pendente')
        ''', (cliente, telefone, produto_id, data_pedido, prazo_entrega))
        conn.commit()
        conn.close()
        return redirect(url_for('painel_status', sucesso=1))
        
    cursor.execute("SELECT id, nome, cor FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    html = LAYOUT_BASE.replace('{% block content %}{% endblock %}', '''
    <h3 style="color: #4a3b32; margin-top: 0; text-align: center;">Cadastrar Nova Encomenda</h3>
    <form method="POST">
        <label style="font-size: 13px; font-weight: bold; color: #555;">Nome do Cliente (Obrigatório)</label>
        <input type="text" name="cliente" required placeholder="Nome do Cliente" style="width: 100%; padding: 8px; margin: 5px 0 12px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
        
        <label style="font-size: 13px; font-weight: bold; color: #555;">Telefone (Opcional)</label>
        <input type="text" name="telefone" placeholder="(00) 00000-0000" style="width: 100%; padding: 8px; margin: 5px 0 12px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
        
        <label style="font-size: 13px; font-weight: bold; color: #555;">Modelo da Bolsa (Produto)</label>
        <select name="produto_id" style="width: 100%; padding: 8px; margin: 5px 0 12px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; background: white;">
            {% for p in produtos %}
            <option value="{{ p[0] }}">{{ p[1] }} (Cor: {{ p[2] }})</option>
            {% endfor %}
        </select>
        
        <label style="font-size: 13px; font-weight: bold; color: #555;">Data do Pedido</label>
        <input type="date" name="data_pedido" value="'''+hoje+'''" required style="width: 100%; padding: 8px; margin: 5px 0 12px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
        
        <label style="font-size: 13px; font-weight: bold; color: #555;">Prazo da Entrega</label>
        <input type="date" name="prazo_entrega" required style="width: 100%; padding: 8px; margin: 5px 0 15px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box;">
        
        <div style="display: flex; gap: 10px;">
            <a href="/" style="flex: 1; background: #ccc; color: #333; padding: 10px; text-align: center; border-radius: 6px; text-decoration: none; font-weight: bold;">Cancelar</a>
            <button type="submit" style="flex: 1; background: #2b70e4; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer;">Salvar Encomenda</button>
        </div>
    </form>
    ''')
    return render_template_string(html, produtos=produtos)

# Rota 3: Painel de Status e Alertas (Tela 3)[cite: 16]
@app.route('/painel')
def painel_status():
    sucesso = request.args.get('sucesso')
    conn = sqlite3.connect('artesa.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.cliente, p.nome, e.status 
        FROM encomendas e 
        JOIN produtos p ON e.produto_id = p.id 
        ORDER BY e.id DESC
    ''')
    encomendas = cursor.fetchall()
    conn.close()
    
    alerta_html = '<div class="alert-success">Encomenda cadastrada com sucesso</div>' if sucesso else ''
    
    html = LAYOUT_BASE.replace('{% block content %}{% endblock %}', '''
    '''+alerta_html+'''
    <h3 style="color: #4a3b32; margin-top: 0; text-align: center;">Painel de Status e Alertas</h3>
    
    <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
        {% for e in encomendas %}
        <div style="background: white; padding: 12px; border-radius: 8px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 13px; font-weight: bold; color: #333;">Encomenda 00{{ e[0] }} - {{ e[1] }}</div>
                <div style="font-size: 12px; color: #666; margin: 2px 0;">{{ e[2] }}</div>
                <div style="font-size: 12px;">Status: 
                    <span style="font-weight: bold; padding: 2px 6px; border-radius: 4px; background: {% if e[3] == 'Pendente' %}#fff3cd{% elif e[3] == 'Em Produção' %}#cce5ff{% else %}#d4edda{% endif %}; color: {% if e[3] == 'Pendente' %}#856404{% elif e[3] == 'Em Produção' %}#004085{% else %}#155724{% endif %};">
                        {{ e[3] }}
                    </span>
                </div>
            </div>
            <a href="/atualizar/{{ e[0] }}" style="background: #e9ecef; border: 1px solid #ced4da; padding: 6px 10px; border-radius: 6px; font-size: 11px; text-decoration: none; color: #007bff; font-weight: bold; text-align: center;">Atualizar<br>Status</a>
        </div>
        {% endfor %}
    </div>
    
    <a href="/" class="btn-primary" style="background-color: #2b70e4; text-align: center;">Voltar ao catalogo</a>
    ''')
    return render_template_string(html, encomendas=encomendas)

# Rota para alternar o status do pedido (ciclo: Pendente -> Em Produção -> Pronto)
@app.route('/atualizar/<int:id>')
def atualizar_status(id):
    conn = sqlite3.connect('artesa.db')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM encomendas WHERE id = ?", (id,))
    atual = cursor.fetchone()[0]
    
    novo_status = 'Pendente'
    if atual == 'Pendente':
        novo_status = 'Em Produção'
    elif atual == 'Em Produção':
        novo_status = 'Pronto'
    else:
        novo_status = 'Pendente'
        
    cursor.execute("UPDATE encomendas SET status = ? WHERE id = ?", (novo_status, id))
    conn.commit()
    conn.close()
    return redirect('/painel')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)