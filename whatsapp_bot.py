# -*- coding: utf-8 -*-
"""
Integração WhatsApp - Sistema Inteligente
Sistema de atendimento SEM APIs externas
"""

import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_hibrido import gerar_resposta

app = Flask(__name__)
CORS(app)

# Banco de dados para conversas WhatsApp
DB_WHATSAPP = "whatsapp_conversas.db"

def init_whatsapp_db():
    """Inicializa banco de dados WhatsApp"""
    conn = sqlite3.connect(DB_WHATSAPP)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversas_whatsapp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_telefone TEXT NOT NULL,
            mensagem_cliente TEXT NOT NULL,
            mensagem_bot TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'enviada',
            metadata TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes_whatsapp (
            numero_telefone TEXT PRIMARY KEY,
            nome TEXT,
            email TEXT,
            primeira_interacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultima_interacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_mensagens INTEGER DEFAULT 0,
            status_cliente TEXT DEFAULT 'ativo'
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Banco WhatsApp inicializado!")

def get_historico_whatsapp(numero, limite=10):
    """Busca histórico de conversa WhatsApp"""
    conn = sqlite3.connect(DB_WHATSAPP)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mensagem_cliente, mensagem_bot 
        FROM conversas_whatsapp 
        WHERE numero_telefone = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (numero, limite))
    
    historico = cursor.fetchall()
    conn.close()
    
    mensagens = []
    for cliente_msg, bot_msg in reversed(historico):
        mensagens.append({"role": "user", "content": cliente_msg})
        mensagens.append({"role": "assistant", "content": bot_msg})
    
    return mensagens

def salvar_conversa_whatsapp(numero, mensagem_cliente, mensagem_bot, metadata=None):
    """Salva conversa WhatsApp no banco"""
    conn = sqlite3.connect(DB_WHATSAPP)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO conversas_whatsapp (numero_telefone, mensagem_cliente, mensagem_bot, metadata)
        VALUES (?, ?, ?, ?)
    """, (numero, mensagem_cliente, mensagem_bot, json.dumps(metadata or {})))
    
    # Atualizar cliente
    cursor.execute("""
        INSERT INTO clientes_whatsapp (numero_telefone, ultima_interacao, total_mensagens)
        VALUES (?, CURRENT_TIMESTAMP, 1)
        ON CONFLICT(numero_telefone) DO UPDATE SET
            ultima_interacao = CURRENT_TIMESTAMP,
            total_mensagens = total_mensagens + 1
    """, (numero,))
    
    conn.commit()
    conn.close()

def detectar_intencao(mensagem):
    """Detecta a intenção do cliente usando IA"""
    prompt = f"""
Analise esta mensagem de WhatsApp e identifique a intenção principal:

Mensagem: "{mensagem}"

Classifique como:
- consulta_produto: Cliente perguntando sobre produtos
- pedido: Cliente quer fazer um pedido
- rastreamento: Cliente quer rastrear pedido
- reclamacao: Cliente insatisfeito
- duvida: Dúvida geral
- preco: Pergunta sobre preço
- pagamento: Dúvida sobre forma de pagamento
- troca: Solicitação de troca/devolução

Responda apenas com a categoria.
"""
    
    try:
        intencao = gerar_resposta(f"Classifique a intenção: {mensagem}", 'whatsapp')
        return intencao.strip().lower()[:20]  # Primeiras palavras
    except:
        return "duvida"

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook para receber mensagens do WhatsApp Business API
    Integre com Twilio, MessageBird ou outra plataforma
    """
    try:
        dados = request.json
        
        # Extrair informações (formato varia por provedor)
        numero = dados.get('from', '').replace('whatsapp:', '')
        mensagem = dados.get('body', '').strip()
        
        if not numero or not mensagem:
            return jsonify({'erro': 'Dados incompletos'}), 400
        
        print(f"📱 WhatsApp de {numero}: {mensagem}")
        
        # Detectar intenção
        intencao = detectar_intencao(mensagem)
        print(f"🎯 Intenção detectada: {intencao}")
        
        # Buscar histórico
        historico = get_historico_whatsapp(numero, limite=5)
        
        # Preparar contexto
        historico_simples = [(msg_cliente, msg_bot) for msg_cliente, msg_bot in historico]

        # Gerar resposta
        resposta = gerar_resposta(mensagem, 'whatsapp', historico_simples)
        
        if not resposta:
            resposta = "Desculpe, estou com dificuldades. Um atendente humano entrará em contato em breve!"
        
        # Salvar conversa
        metadata = {
            'intencao': intencao,
            'timestamp': datetime.now().isoformat()
        }
        salvar_conversa_whatsapp(numero, mensagem, resposta, metadata)
        
        # Retornar resposta (formato varia por provedor)
        return jsonify({
            'to': numero,
            'body': resposta,
            'intencao': intencao
        })
        
    except Exception as e:
        print(f"❌ Erro no webhook WhatsApp: {e}")
        return jsonify({'erro': str(e)}), 500

@app.route('/whatsapp/enviar', methods=['POST'])
def enviar_whatsapp():
    """Envia mensagem via WhatsApp (para testes)"""
    try:
        dados = request.json
        numero = dados.get('numero')
        mensagem = dados.get('mensagem')
        
        # Aqui você integraria com Twilio/MessageBird/etc
        # Por enquanto, apenas simula
        
        print(f"📤 Enviando para {numero}: {mensagem}")
        
        return jsonify({
            'status': 'enviado',
            'numero': numero,
            'mensagem': mensagem
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/whatsapp/historico/<numero>', methods=['GET'])
def historico_whatsapp(numero):
    """Retorna histórico de conversa de um número"""
    try:
        conn = sqlite3.connect(DB_WHATSAPP)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mensagem_cliente, mensagem_bot, timestamp, metadata
            FROM conversas_whatsapp
            WHERE numero_telefone = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (numero,))
        
        conversas = []
        for row in cursor.fetchall():
            conversas.append({
                'cliente': row[0],
                'bot': row[1],
                'timestamp': row[2],
                'metadata': json.loads(row[3]) if row[3] else {}
            })
        
        conn.close()
        
        return jsonify({
            'numero': numero,
            'total': len(conversas),
            'conversas': conversas
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/whatsapp/clientes', methods=['GET'])
def listar_clientes_whatsapp():
    """Lista todos os clientes que interagiram via WhatsApp"""
    try:
        conn = sqlite3.connect(DB_WHATSAPP)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT numero_telefone, nome, email, primeira_interacao, 
                   ultima_interacao, total_mensagens, status_cliente
            FROM clientes_whatsapp
            ORDER BY ultima_interacao DESC
        """)
        
        clientes = []
        for row in cursor.fetchall():
            clientes.append({
                'numero': row[0],
                'nome': row[1],
                'email': row[2],
                'primeira_interacao': row[3],
                'ultima_interacao': row[4],
                'total_mensagens': row[5],
                'status': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'total': len(clientes),
            'clientes': clientes
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/whatsapp/estatisticas', methods=['GET'])
def estatisticas_whatsapp():
    """Retorna estatísticas do atendimento WhatsApp"""
    try:
        conn = sqlite3.connect(DB_WHATSAPP)
        cursor = conn.cursor()
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes_whatsapp")
        total_clientes = cursor.fetchone()[0]
        
        # Total de mensagens
        cursor.execute("SELECT COUNT(*) FROM conversas_whatsapp")
        total_mensagens = cursor.fetchone()[0]
        
        # Clientes hoje
        cursor.execute("""
            SELECT COUNT(*) FROM clientes_whatsapp 
            WHERE DATE(ultima_interacao) = DATE('now')
        """)
        clientes_hoje = cursor.fetchone()[0]
        
        # Média de mensagens
        media = total_mensagens / total_clientes if total_clientes > 0 else 0
        
        conn.close()
        
        return jsonify({
            'total_clientes': total_clientes,
            'total_mensagens': total_mensagens,
            'clientes_hoje': clientes_hoje,
            'media_mensagens': round(media, 2)
        })
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    print("📱 Iniciando WhatsApp Bot API...")
    init_whatsapp_db()
    print("✅ WhatsApp Bot rodando em http://localhost:5002")
    print("\n💡 Para integrar com WhatsApp Business:")
    print("   - Configure webhook: http://seu-servidor:5002/whatsapp/webhook")
    print("   - Use Twilio, MessageBird ou WhatsApp Business API")
    
    app.run(host='0.0.0.0', port=5002, debug=True)
