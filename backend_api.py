"""
Backend API com Flask + SQLite
Sistema de Pedidos - Griffe da Prata
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import hashlib
from PIL import Image
import pillow_avif  # Plugin para suporte AVIF
import io
import base64
import re

app = Flask(__name__)

# CORS configurado para GitHub Pages + desenvolvimento local
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://griffedaprata.com.br",
            "https://www.griffedaprata.com.br",
            "https://avilaops.github.io",
            "http://localhost:*",
            "http://127.0.0.1:*"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

DB_PATH = "pedidos.db"
PRODUTOS_JSON = "silvercrown_scraper/atacadodeprata_completo/dados/produtos_atacado_completo.json"


# ==================== DATABASE ====================

def init_db():
    """Inicializa o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            cliente_nome TEXT NOT NULL,
            cliente_whatsapp TEXT NOT NULL,
            total_atacado REAL NOT NULL,
            total_varejo REAL NOT NULL,
            lucro REAL NOT NULL,
            margem TEXT DEFAULT '250%',
            status TEXT DEFAULT 'pendente',
            enviado_fornecedor INTEGER DEFAULT 0,
            data_envio TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de itens do pedido
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedido_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id TEXT NOT NULL,
            codigo TEXT NOT NULL,
            titulo TEXT,
            quantidade INTEGER NOT NULL,
            preco_atacado REAL NOT NULL,
            preco_varejo REAL NOT NULL,
            subtotal_atacado REAL NOT NULL,
            subtotal_varejo REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
        )
    ''')
    
    # Tabela de produtos (cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            codigo TEXT PRIMARY KEY,
            categoria TEXT DEFAULT 'OUTROS',
            titulo TEXT,
            preco_atacado REAL,
            preco_varejo REAL,
            peso TEXT,
            lote TEXT,
            descricao TEXT,
            imagem_url TEXT,
            imagem_local TEXT,
            imagem TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Adicionar coluna categoria se não existir (migração)
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN categoria TEXT DEFAULT 'OUTROS'")
    except:
        pass  # Coluna já existe
    
    # Adicionar coluna imagem se não existir (migração)
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN imagem TEXT")
    except:
        pass  # Coluna já existe
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado!")


def carregar_produtos_json():
    """Carrega produtos do JSON e salva no banco"""
    try:
        with open(PRODUTOS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for produto in data['produtos']:
            # Converter preços para float
            preco_atacado = float(produto['preco_atacado'].replace('R$', '').replace(',', '.').strip())
            preco_varejo = float(produto['preco_varejo'].replace('R$', '').replace(',', '.').strip())
            
            cursor.execute('''
                INSERT OR REPLACE INTO produtos 
                (codigo, titulo, preco_atacado, preco_varejo, peso, lote, descricao, imagem_url, imagem_local)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                produto['codigo'],
                produto.get('titulo', ''),
                preco_atacado,
                preco_varejo,
                produto.get('peso', ''),
                produto.get('lote', ''),
                produto.get('descricao', ''),
                produto.get('imagem_url', ''),
                produto.get('imagem_local', '')
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ {len(data['produtos'])} produtos carregados no banco!")
        
    except Exception as e:
        print(f"❌ Erro ao carregar produtos: {e}")


def get_db():
    """Retorna conexão com o banco"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==================== ENDPOINTS ====================

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    """Lista todos os produtos disponíveis"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM produtos ORDER BY codigo')
    produtos = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(produtos)


@app.route('/api/produtos/<codigo>', methods=['GET'])
def buscar_produto(codigo):
    """Busca produto específico por código"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM produtos WHERE codigo = ?', (codigo,))
    produto = cursor.fetchone()
    
    conn.close()
    
    if produto:
        return jsonify(dict(produto))
    return jsonify({'error': 'Produto não encontrado'}), 404


@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    """Cria novo pedido"""
    data = request.json
    
    cliente_nome = data.get('cliente_nome')
    cliente_whatsapp = data.get('cliente_whatsapp')
    items = data.get('items', [])
    
    if not cliente_nome or not cliente_whatsapp or not items:
        return jsonify({'error': 'Dados incompletos'}), 400
    
    # Gerar ID único
    pedido_id = hashlib.md5(f"{datetime.now().isoformat()}{cliente_nome}".encode()).hexdigest()[:8]
    data_pedido = datetime.now().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Calcular totais
    total_atacado = 0
    total_varejo = 0
    items_processados = []
    
    for item in items:
        codigo = item['codigo']
        quantidade = item['quantidade']
        
        # Buscar produto
        cursor.execute('SELECT * FROM produtos WHERE codigo = ?', (codigo,))
        produto = cursor.fetchone()
        
        if not produto:
            conn.close()
            return jsonify({'error': f'Produto {codigo} não encontrado'}), 404
        
        preco_atacado = produto['preco_atacado']
        preco_varejo = produto['preco_varejo']
        
        subtotal_atacado = preco_atacado * quantidade
        subtotal_varejo = preco_varejo * quantidade
        
        total_atacado += subtotal_atacado
        total_varejo += subtotal_varejo
        
        items_processados.append({
            'codigo': codigo,
            'titulo': produto['titulo'],
            'quantidade': quantidade,
            'preco_atacado': preco_atacado,
            'preco_varejo': preco_varejo,
            'subtotal_atacado': subtotal_atacado,
            'subtotal_varejo': subtotal_varejo
        })
    
    lucro = total_varejo - total_atacado
    
    # Inserir pedido
    cursor.execute('''
        INSERT INTO pedidos 
        (id, data, cliente_nome, cliente_whatsapp, total_atacado, total_varejo, lucro, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pendente')
    ''', (pedido_id, data_pedido, cliente_nome, cliente_whatsapp, total_atacado, total_varejo, lucro))
    
    # Inserir items
    for item in items_processados:
        cursor.execute('''
            INSERT INTO pedido_items 
            (pedido_id, codigo, titulo, quantidade, preco_atacado, preco_varejo, subtotal_atacado, subtotal_varejo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pedido_id, item['codigo'], item['titulo'], item['quantidade'],
            item['preco_atacado'], item['preco_varejo'],
            item['subtotal_atacado'], item['subtotal_varejo']
        ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': pedido_id,
        'data': data_pedido,
        'cliente': {'nome': cliente_nome, 'whatsapp': cliente_whatsapp},
        'items': items_processados,
        'total_atacado': total_atacado,
        'total_varejo': total_varejo,
        'lucro': lucro,
        'status': 'pendente'
    }), 201


@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    """Lista todos os pedidos"""
    status_filter = request.args.get('status')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if status_filter:
        cursor.execute('SELECT * FROM pedidos WHERE status = ? ORDER BY data DESC', (status_filter,))
    else:
        cursor.execute('SELECT * FROM pedidos ORDER BY data DESC')
    
    pedidos = []
    for row in cursor.fetchall():
        pedido = dict(row)
        pedido_id = pedido['id']
        
        # Buscar items do pedido
        cursor.execute('SELECT * FROM pedido_items WHERE pedido_id = ?', (pedido_id,))
        items = [dict(item) for item in cursor.fetchall()]
        pedido['items'] = items
        
        pedidos.append(pedido)
    
    conn.close()
    return jsonify(pedidos)


@app.route('/api/pedidos/<pedido_id>', methods=['GET'])
def buscar_pedido(pedido_id):
    """Busca pedido específico"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,))
    pedido = cursor.fetchone()
    
    if not pedido:
        conn.close()
        return jsonify({'error': 'Pedido não encontrado'}), 404
    
    pedido_dict = dict(pedido)
    
    # Buscar items
    cursor.execute('SELECT * FROM pedido_items WHERE pedido_id = ?', (pedido_id,))
    items = [dict(item) for item in cursor.fetchall()]
    pedido_dict['items'] = items
    
    conn.close()
    return jsonify(pedido_dict)


@app.route('/api/pedidos/<pedido_id>/status', methods=['PUT'])
def atualizar_status(pedido_id):
    """Atualiza status do pedido"""
    data = request.json
    novo_status = data.get('status')
    
    if novo_status not in ['pendente', 'enviado', 'concluido']:
        return jsonify({'error': 'Status inválido'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    if novo_status == 'enviado':
        cursor.execute('''
            UPDATE pedidos 
            SET status = ?, enviado_fornecedor = 1, data_envio = ?
            WHERE id = ?
        ''', (novo_status, datetime.now().isoformat(), pedido_id))
    else:
        cursor.execute('UPDATE pedidos SET status = ? WHERE id = ?', (novo_status, pedido_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'pedido_id': pedido_id, 'status': novo_status})


@app.route('/api/pedidos/<pedido_id>/whatsapp', methods=['GET'])
def gerar_whatsapp(pedido_id):
    """Gera mensagem formatada para WhatsApp"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,))
    pedido = cursor.fetchone()
    
    if not pedido:
        conn.close()
        return jsonify({'error': 'Pedido não encontrado'}), 404
    
    pedido_dict = dict(pedido)
    
    cursor.execute('SELECT * FROM pedido_items WHERE pedido_id = ?', (pedido_id,))
    items = [dict(item) for item in cursor.fetchall()]
    
    conn.close()
    
    # Formatar mensagem
    msg = f"🛒 *NOVO PEDIDO - GRIFFE DA PRATA*\n\n"
    msg += f"📋 Pedido: #{pedido_id}\n"
    msg += f"📅 Data: {datetime.fromisoformat(pedido_dict['data']).strftime('%d/%m/%Y %H:%M')}\n\n"
    msg += f"*PRODUTOS:*\n"
    
    for item in items:
        msg += f"• {item['codigo']} - {item['quantidade']}x - R$ {item['preco_atacado']:.2f}\n"
    
    msg += f"\n💰 *Total: R$ {pedido_dict['total_atacado']:.2f}*\n\n"
    msg += f"Cliente: {pedido_dict['cliente_nome']}\n"
    msg += f"Confirma disponibilidade? 🙏"
    
    whatsapp_fornecedor = "5517997088111"
    
    return jsonify({
        'mensagem': msg,
        'whatsapp': whatsapp_fornecedor,
        'url': f"https://wa.me/{whatsapp_fornecedor}?text={msg}"
    })


@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    """Retorna estatísticas gerais"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM pedidos')
    total = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM pedidos WHERE status = "pendente"')
    pendentes = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM pedidos WHERE status = "enviado"')
    enviados = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM pedidos WHERE status = "concluido"')
    concluidos = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(lucro) as total_lucro FROM pedidos WHERE status = "concluido"')
    total_lucro = cursor.fetchone()['total_lucro'] or 0
    
    conn.close()
    
    return jsonify({
        'total': total,
        'pendentes': pendentes,
        'enviados': enviados,
        'concluidos': concluidos,
        'total_lucro': total_lucro
    })


# ==================== CONVERSÃO DE IMAGENS ====================

def converter_para_avif(imagem_base64):
    """
    Converte qualquer imagem para formato AVIF (silenciosamente)
    Retorna a imagem em base64 no formato AVIF
    """
    try:
        # Se não houver imagem, retornar None
        if not imagem_base64:
            return None
        
        # Extrair o tipo de imagem e os dados base64
        match = re.match(r'data:image/(\w+);base64,(.+)', imagem_base64)
        if not match:
            # Se não tiver prefixo, assume que é base64 puro
            img_data = imagem_base64
        else:
            formato_original = match.group(1)
            img_data = match.group(2)
            
            # Se já for AVIF, retornar como está
            if formato_original.lower() == 'avif':
                return imagem_base64
        
        # Decodificar base64
        img_bytes = base64.b64decode(img_data)
        
        # Abrir imagem com Pillow
        img = Image.open(io.BytesIO(img_bytes))
        
        # Converter para RGB se necessário (AVIF não suporta RGBA diretamente)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Criar fundo branco
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar se muito grande (otimização)
        max_size = 1920
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Salvar como AVIF
        output = io.BytesIO()
        img.save(output, format='AVIF', quality=85, speed=6)
        output.seek(0)
        
        # Converter para base64
        avif_base64 = base64.b64encode(output.read()).decode('utf-8')
        
        # Retornar com prefixo data URI
        return f"data:image/avif;base64,{avif_base64}"
        
    except Exception as e:
        print(f"⚠️  Erro na conversão para AVIF: {str(e)}")
        # Em caso de erro, retornar a imagem original
        return imagem_base64


# ==================== GERENCIAMENTO DE PRODUTOS ====================

@app.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    """Adiciona ou atualiza um produto"""
    try:
        dados = request.json
        
        # 🔄 Converter imagem para AVIF silenciosamente
        if dados.get('imagem'):
            print("🔄 Convertendo imagem para AVIF...")
            dados['imagem'] = converter_para_avif(dados['imagem'])
            print("✅ Imagem convertida para AVIF com sucesso!")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se produto já existe
        cursor.execute("SELECT codigo FROM produtos WHERE codigo = ?", (dados['codigo'],))
        existe = cursor.fetchone()
        
        if existe:
            # Atualizar produto existente
            cursor.execute("""
                UPDATE produtos 
                SET categoria = ?, titulo = ?, descricao = ?, 
                    preco_varejo = ?, preco_atacado = ?, peso = ?, imagem = ?
                WHERE codigo = ?
            """, (
                dados.get('categoria'),
                dados.get('titulo'),
                dados.get('descricao'),
                dados.get('preco_varejo'),
                dados.get('preco_atacado'),
                dados.get('peso'),
                dados.get('imagem'),
                dados['codigo']
            ))
        else:
            # Inserir novo produto
            cursor.execute("""
                INSERT INTO produtos 
                (codigo, categoria, titulo, descricao, preco_varejo, preco_atacado, peso, imagem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados['codigo'],
                dados.get('categoria'),
                dados.get('titulo'),
                dados.get('descricao'),
                dados.get('preco_varejo'),
                dados.get('preco_atacado'),
                dados.get('peso'),
                dados.get('imagem')
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'sucesso': True, 'mensagem': 'Produto salvo com sucesso!'})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/produtos/<codigo>', methods=['DELETE'])
def deletar_produto(codigo):
    """Deleta um produto"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM produtos WHERE codigo = ?", (codigo,))
        conn.commit()
        conn.close()
        
        if cursor.rowcount > 0:
            return jsonify({'sucesso': True, 'mensagem': 'Produto excluído!'})
        else:
            return jsonify({'erro': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Página inicial da API"""
    return jsonify({
        'api': 'Sistema de Pedidos - Griffe da Prata',
        'versao': '1.0',
        'endpoints': {
            'produtos': '/api/produtos',
            'pedidos': '/api/pedidos',
            'estatisticas': '/api/estatisticas'
        }
    })


# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    print("🚀 Iniciando Backend API...")
    init_db()
    carregar_produtos_json()
    print("\n✅ Backend rodando em http://localhost:5000")
    print("📚 Documentação: http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
