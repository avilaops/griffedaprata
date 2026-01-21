# -*- coding: utf-8 -*-
"""
Chatbot de Atendimento ao Cliente - Backend
Sistema inteligente SEM APIs externas - 100% Gratuito
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from chatbot_hibrido import gerar_resposta

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
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Banco de dados para conversas
DB_CONVERSAS = "chatbot_conversas.db"

def init_db():
    """Inicializa banco de dados de conversas"""
    conn = sqlite3.connect(DB_CONVERSAS)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sessao_id TEXT NOT NULL,
            mensagem_usuario TEXT NOT NULL,
            mensagem_bot TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessoes (
            sessao_id TEXT PRIMARY KEY,
            email TEXT,
            nome TEXT,
            telefone TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultima_atividade DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_mensagens INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados do chatbot inicializado!")

def get_historico_conversa(sessao_id, limite=10):
    """Busca histórico de conversa de uma sessão"""
    conn = sqlite3.connect(DB_CONVERSAS)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mensagem_usuario, mensagem_bot 
        FROM conversas 
        WHERE sessao_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (sessao_id, limite))
    
    historico = cursor.fetchall()
    conn.close()
    
    # Converter para formato de mensagens
    mensagens = []
    for user_msg, bot_msg in reversed(historico):
        mensagens.append({"role": "user", "content": user_msg})
        mensagens.append({"role": "assistant", "content": bot_msg})
    
    return mensagens

def salvar_conversa(sessao_id, mensagem_usuario, mensagem_bot, metadata=None):
    """Salva conversa no banco"""
    conn = sqlite3.connect(DB_CONVERSAS)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO conversas (sessao_id, mensagem_usuario, mensagem_bot, metadata)
        VALUES (?, ?, ?, ?)
    """, (sessao_id, mensagem_usuario, mensagem_bot, json.dumps(metadata or {})))
    
    # Atualizar sessão
    cursor.execute("""
        INSERT INTO sessoes (sessao_id, ultima_atividade, total_mensagens)
        VALUES (?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(sessao_id) DO UPDATE SET
            ultima_atividade = CURRENT_TIMESTAMP,
            total_mensagens = total_mensagens + 1
    """, (sessao_id,))
    
    conn.commit()
    conn.close()

def buscar_produtos_relevantes(query):
    """Busca produtos relevantes baseado na query"""
    from backend_api import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca simples por título e código
    cursor.execute("""
        SELECT codigo, titulo, preco_varejo, peso
        FROM produtos
        WHERE titulo LIKE ? OR codigo LIKE ?
        LIMIT 5
    """, (f"%{query}%", f"%{query}%"))
    
    produtos = []
    for row in cursor.fetchall():
        produtos.append({
            'codigo': row[0],
            'titulo': row[1],
            'preco': row[2],
            'peso': row[3]
        })
    
    conn.close()
    return produtos

@app.route('/api/chatbot/mensagem', methods=['POST'])
def chatbot_mensagem():
    """Endpoint principal do chatbot"""
    try:
        dados = request.json
        mensagem_usuario = dados.get('mensagem', '').strip()
        sessao_id = dados.get('sessao_id', 'anonimo')
        
        if not mensagem_usuario:
            return jsonify({'erro': 'Mensagem vazia'}), 400
        
        # Buscar histórico
        historico = get_historico_conversa(sessao_id, limite=5)
        
        # Buscar produtos se houver menção a categorias
        produtos_relevantes = None
        categorias = ['anel', 'brinco', 'colar', 'pulseira', 'berloque', 'conjunto']
        for cat in categorias:
            if cat in mensagem_usuario.lower():
                produtos_relevantes = buscar_produtos_relevantes(cat)
                break
        
        # Adicionar contexto de produtos se encontrou
        contexto_adicional = ""
        if produtos_relevantes:
            contexto_adicional = f"\n\n**Produtos Relevantes:**\n"
            for p in produtos_relevantes:
                contexto_adicional += f"- {p['titulo']} ({p['codigo']}) - R$ {p['preco']:.2f}\n"
        
        # Preparar mensagens para API
        mensagens = historico + [
            {"role": "user", "content": mensagem_usuario + contexto_adicional}
        ]

        # Converter histórico para formato simples
        historico_simples = [(msg['content'], '') for msg in historico if msg['role'] == 'user']
        
        # Chamar chatbot híbrido
        resposta_bot = gerar_resposta(mensagem_usuario + contexto_adicional, 'chatbot_site', historico_simples)
        
        if not resposta_bot:
            resposta_bot = "Desculpe, estou com dificuldades técnicas. Por favor, entre em contato pelo WhatsApp: (82) 98160-2651"
        
        # Salvar no banco
        metadata = {
            'produtos_mostrados': [p['codigo'] for p in produtos_relevantes] if produtos_relevantes else [],
            'timestamp': datetime.now().isoformat()
        }
        salvar_conversa(sessao_id, mensagem_usuario, resposta_bot, metadata)
        
        return jsonify({
            'resposta': resposta_bot,
            'sessao_id': sessao_id,
            'produtos': produtos_relevantes,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Erro no chatbot: {e}")
        return jsonify({
            'erro': 'Erro interno',
            'detalhes': str(e)
        }), 500

@app.route('/api/chatbot/iniciar', methods=['POST'])
def chatbot_iniciar():
    """Inicia uma nova sessão de chat"""
    try:
        dados = request.json
        sessao_id = dados.get('sessao_id')
        nome = dados.get('nome')
        email = dados.get('email')
        
        if not sessao_id:
            from uuid import uuid4
            sessao_id = str(uuid4())
        
        conn = sqlite3.connect(DB_CONVERSAS)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessoes (sessao_id, nome, email, criado_em, ultima_atividade)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (sessao_id, nome, email))
        
        conn.commit()
        conn.close()
        
        # Mensagem de boas-vindas
        mensagem_inicial = f"""Olá{f' {nome}' if nome else ''}! 👋

Sou a assistente virtual da **Griffe da Prata**! ✨

Como posso ajudar você hoje?

💎 Ver produtos
❓ Tirar dúvidas
📦 Rastrear pedido
🔄 Trocas e devoluções

Digite sua dúvida ou escolha uma opção!"""
        
        return jsonify({
            'sessao_id': sessao_id,
            'mensagem_inicial': mensagem_inicial
        })
        
    except Exception as e:
        print(f"Erro ao iniciar sessão: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/api/chatbot/historico/<sessao_id>', methods=['GET'])
def chatbot_historico(sessao_id):
    """Retorna histórico de uma sessão"""
    try:
        conn = sqlite3.connect(DB_CONVERSAS)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mensagem_usuario, mensagem_bot, timestamp
            FROM conversas
            WHERE sessao_id = ?
            ORDER BY timestamp ASC
        """, (sessao_id,))
        
        historico = []
        for row in cursor.fetchall():
            historico.append({
                'usuario': row[0],
                'bot': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'sessao_id': sessao_id,
            'historico': historico,
            'total': len(historico)
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/chatbot/estatisticas', methods=['GET'])
def chatbot_estatisticas():
    """Retorna estatísticas do chatbot"""
    try:
        conn = sqlite3.connect(DB_CONVERSAS)
        cursor = conn.cursor()
        
        # Total de sessões
        cursor.execute("SELECT COUNT(*) FROM sessoes")
        total_sessoes = cursor.fetchone()[0]
        
        # Total de mensagens
        cursor.execute("SELECT COUNT(*) FROM conversas")
        total_mensagens = cursor.fetchone()[0]
        
        # Sessões hoje
        cursor.execute("""
            SELECT COUNT(*) FROM sessoes 
            WHERE DATE(criado_em) = DATE('now')
        """)
        sessoes_hoje = cursor.fetchone()[0]
        
        # Média de mensagens por sessão
        media_mensagens = total_mensagens / total_sessoes if total_sessoes > 0 else 0
        
        conn.close()
        
        return jsonify({
            'total_sessoes': total_sessoes,
            'total_mensagens': total_mensagens,
            'sessoes_hoje': sessoes_hoje,
            'media_mensagens_por_sessao': round(media_mensagens, 2)
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Iniciando Chatbot API...")
    init_db()
    print("✅ Chatbot rodando em http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
