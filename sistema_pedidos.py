"""
Sistema de Pedidos - Backend
Gerencia pedidos da Griffe da Prata e integração com Atacado de Prata
"""

import json
from datetime import datetime
from pathlib import Path
import hashlib


class SistemaPedidos:
    def __init__(self):
        self.pedidos_dir = Path("sistema_pedidos")
        self.pedidos_dir.mkdir(exist_ok=True)
        self.pedidos_file = self.pedidos_dir / "pedidos.json"
        self.produtos_file = "silvercrown_scraper/atacadodeprata_completo/dados/produtos_atacado_completo.json"
        
        # Carregar pedidos existentes
        self.pedidos = self._carregar_pedidos()
        self.produtos = self._carregar_produtos()
    
    def _carregar_pedidos(self):
        """Carrega pedidos salvos"""
        if self.pedidos_file.exists():
            with open(self.pedidos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _carregar_produtos(self):
        """Carrega catálogo de produtos"""
        try:
            with open(self.produtos_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {p['codigo']: p for p in data['produtos']}
        except:
            return {}
    
    def _salvar_pedidos(self):
        """Salva pedidos em JSON"""
        with open(self.pedidos_file, 'w', encoding='utf-8') as f:
            json.dump(self.pedidos, f, ensure_ascii=False, indent=2)
    
    def criar_pedido(self, cliente_nome, cliente_whatsapp, items):
        """
        Cria novo pedido
        
        items = [
            {'codigo': 'K2-80', 'quantidade': 3},
            {'codigo': 'P3-10', 'quantidade': 1}
        ]
        """
        pedido_id = hashlib.md5(f"{datetime.now().isoformat()}{cliente_nome}".encode()).hexdigest()[:8]
        
        # Calcular valores
        total_atacado = 0
        total_varejo = 0
        items_detalhados = []
        
        for item in items:
            codigo = item['codigo']
            quantidade = item['quantidade']
            
            if codigo in self.produtos:
                produto = self.produtos[codigo]
                
                # Extrair valores numéricos
                preco_atacado_str = produto.get('preco_atacado', 'R$0,00')
                preco_varejo_str = produto.get('preco_varejo', 'R$0,00')
                
                try:
                    preco_atacado = float(preco_atacado_str.replace('R$', '').replace(',', '.').strip())
                    preco_varejo = float(preco_varejo_str.replace('R$', '').replace(',', '.').strip())
                except:
                    preco_atacado = 0
                    preco_varejo = 0
                
                subtotal_atacado = preco_atacado * quantidade
                subtotal_varejo = preco_varejo * quantidade
                
                total_atacado += subtotal_atacado
                total_varejo += subtotal_varejo
                
                items_detalhados.append({
                    'codigo': codigo,
                    'titulo': produto.get('titulo', ''),
                    'quantidade': quantidade,
                    'preco_atacado': f"R$ {preco_atacado:.2f}".replace('.', ','),
                    'preco_varejo': f"R$ {preco_varejo:.2f}".replace('.', ','),
                    'subtotal_atacado': f"R$ {subtotal_atacado:.2f}".replace('.', ','),
                    'subtotal_varejo': f"R$ {subtotal_varejo:.2f}".replace('.', ',')
                })
        
        pedido = {
            'id': pedido_id,
            'data': datetime.now().isoformat(),
            'cliente': {
                'nome': cliente_nome,
                'whatsapp': cliente_whatsapp
            },
            'items': items_detalhados,
            'total_atacado': f"R$ {total_atacado:.2f}".replace('.', ','),
            'total_varejo': f"R$ {total_varejo:.2f}".replace('.', ','),
            'lucro': f"R$ {(total_varejo - total_atacado):.2f}".replace('.', ','),
            'margem': '250%',
            'status': 'pendente',  # pendente, enviado, concluido
            'enviado_fornecedor': False
        }
        
        self.pedidos.append(pedido)
        self._salvar_pedidos()
        
        return pedido
    
    def listar_pedidos(self, status=None):
        """Lista pedidos, opcionalmente filtrados por status"""
        if status:
            return [p for p in self.pedidos if p['status'] == status]
        return self.pedidos
    
    def atualizar_status(self, pedido_id, novo_status):
        """Atualiza status do pedido"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                pedido['status'] = novo_status
                if novo_status == 'enviado':
                    pedido['enviado_fornecedor'] = True
                    pedido['data_envio'] = datetime.now().isoformat()
                self._salvar_pedidos()
                return True
        return False
    
    def gerar_mensagem_whatsapp(self, pedido_id):
        """Gera mensagem formatada para WhatsApp do fornecedor"""
        pedido = next((p for p in self.pedidos if p['id'] == pedido_id), None)
        if not pedido:
            return None
        
        msg = f"🛒 *NOVO PEDIDO - GRIFFE DA PRATA*\n\n"
        msg += f"📋 Pedido: #{pedido['id']}\n"
        msg += f"📅 Data: {datetime.fromisoformat(pedido['data']).strftime('%d/%m/%Y %H:%M')}\n\n"
        msg += f"*PRODUTOS:*\n"
        
        for item in pedido['items']:
            msg += f"• {item['codigo']} - {item['quantidade']}x - {item['preco_atacado']}\n"
        
        msg += f"\n💰 *Total: {pedido['total_atacado']}*\n\n"
        msg += f"Cliente: {pedido['cliente']['nome']}\n"
        msg += f"Confirma disponibilidade? 🙏"
        
        return msg
    
    def gerar_relatorio(self):
        """Gera relatório geral de pedidos"""
        total_pedidos = len(self.pedidos)
        pendentes = len([p for p in self.pedidos if p['status'] == 'pendente'])
        enviados = len([p for p in self.pedidos if p['status'] == 'enviado'])
        concluidos = len([p for p in self.pedidos if p['status'] == 'concluido'])
        
        return {
            'total': total_pedidos,
            'pendentes': pendentes,
            'enviados': enviados,
            'concluidos': concluidos,
            'pedidos': self.pedidos
        }


# Exemplo de uso
if __name__ == "__main__":
    sistema = SistemaPedidos()
    
    # Criar pedido exemplo
    pedido = sistema.criar_pedido(
        cliente_nome="Maria Oliveira",
        cliente_whatsapp="5511987654321",
        items=[
            {'codigo': 'J2-54', 'quantidade': 2},
            {'codigo': 'J1-61', 'quantidade': 3},
            {'codigo': 'O9-2', 'quantidade': 1}
        ]
    )
    
    print("✅ Pedido criado!")
    print(f"ID: {pedido['id']}")
    print(f"Total Atacado: {pedido['total_atacado']}")
    print(f"Total Varejo: {pedido['total_varejo']}")
    print(f"Lucro: {pedido['lucro']}")
    
    # Gerar mensagem WhatsApp
    msg = sistema.gerar_mensagem_whatsapp(pedido['id'])
    print(f"\n📱 Mensagem WhatsApp:\n{msg}")
