# -*- coding: utf-8 -*-
"""
Assistente de Desenvolvimento com IA
Analisa código, sugere melhorias e gera código automaticamente
"""

import os
import sys
from config_grok import gerar_resposta_grok
from pathlib import Path

def analisar_arquivo(caminho_arquivo):
    """Analisa um arquivo de código e sugere melhorias"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        prompt = f"""
Analise o seguinte código e forneça:

1. **Resumo**: O que o código faz
2. **Qualidade**: Nota de 0-10 e justificativa
3. **Bugs Potenciais**: Problemas encontrados
4. **Vulnerabilidades**: Questões de segurança
5. **Melhorias**: Sugestões de otimização
6. **Refatoração**: Código refatorado (se necessário)

**Arquivo**: {os.path.basename(caminho_arquivo)}

```python
{codigo}
```
"""
        
        print(f"\n🔍 Analisando {caminho_arquivo}...")
        resposta = chat_completion(
            [{"role": "user", "content": prompt}],
            tipo='dev_assistant'
        )
        
        return resposta
        
    except Exception as e:
        return f"Erro ao analisar arquivo: {e}"

def gerar_documentacao(caminho_arquivo):
    """Gera documentação automática para o código"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        prompt = f"""
Gere documentação completa para este código em formato Markdown:

**Inclua:**
1. Título e descrição geral
2. Dependências necessárias
3. Como usar / Exemplos
4. Documentação de cada função/classe
5. Parâmetros e retornos
6. Possíveis erros/exceções

**Código:**
```python
{codigo}
```
"""
        
        print(f"\n📝 Gerando documentação para {caminho_arquivo}...")
        resposta = gerar_resposta_grok(prompt, tipo='dev_assistant')
        
        # Salvar documentação
        nome_doc = os.path.splitext(caminho_arquivo)[0] + '_DOC.md'
        with open(nome_doc, 'w', encoding='utf-8') as f:
            f.write(resposta)
        
        print(f"✅ Documentação salva em: {nome_doc}")
        return resposta
        
    except Exception as e:
        return f"Erro ao gerar documentação: {e}"

def sugerir_testes(caminho_arquivo):
    """Sugere e gera testes unitários"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        prompt = f"""
Gere testes unitários completos usando pytest para este código:

**Requisitos:**
1. Testes para todas as funções públicas
2. Casos de sucesso e falha
3. Edge cases
4. Mocks quando necessário
5. Docstrings nos testes

**Código:**
```python
{codigo}
```

Retorne apenas o código dos testes, pronto para usar.
"""
        
        print(f"\n🧪 Gerando testes para {caminho_arquivo}...")
        resposta = gerar_resposta_grok(prompt, tipo='dev_assistant')
        
        # Salvar testes
        nome_teste = 'test_' + os.path.basename(caminho_arquivo)
        with open(nome_teste, 'w', encoding='utf-8') as f:
            f.write(resposta)
        
        print(f"✅ Testes salvos em: {nome_teste}")
        return resposta
        
    except Exception as e:
        return f"Erro ao gerar testes: {e}"

def otimizar_performance(caminho_arquivo):
    """Analisa performance e sugere otimizações"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        prompt = f"""
Analise a performance deste código e sugira otimizações:

**Foco em:**
1. Complexidade algorítmica (Big O)
2. Uso de memória
3. I/O e queries ao banco
4. Loops e iterações
5. Cache e memoização
6. Processamento assíncrono

**Forneça:**
- Análise de performance atual
- Gargalos identificados
- Código otimizado
- Ganho estimado de performance

**Código:**
```python
{codigo}
```
"""
        
        print(f"\n⚡ Analisando performance de {caminho_arquivo}...")
        resposta = gerar_resposta_grok(prompt, tipo='dev_assistant')
        
        return resposta
        
    except Exception as e:
        return f"Erro ao analisar performance: {e}"

def revisar_seguranca(caminho_arquivo):
    """Revisa código em busca de vulnerabilidades de segurança"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        prompt = f"""
Faça uma auditoria de segurança completa deste código:

**Verifique:**
1. SQL Injection
2. XSS (Cross-Site Scripting)
3. CSRF
4. Autenticação e autorização
5. Validação de entrada
6. Exposição de dados sensíveis
7. Dependências vulneráveis
8. OWASP Top 10

**Forneça:**
- Vulnerabilidades encontradas (com severity)
- Código corrigido
- Boas práticas recomendadas

**Código:**
```python
{codigo}
```
"""
        
        print(f"\n🔒 Revisando segurança de {caminho_arquivo}...")
        resposta = gerar_resposta_grok(prompt, tipo='dev_assistant')
        
        return resposta
        
    except Exception as e:
        return f"Erro ao revisar segurança: {e}"

def gerar_feature(descricao):
    """Gera código para uma nova feature baseado em descrição"""
    prompt = f"""
Gere código Python completo e funcional para esta feature:

**Descrição:**
{descricao}

**Requisitos:**
1. Código limpo e bem estruturado
2. Docstrings completas
3. Type hints
4. Tratamento de erros
5. Logging apropriado
6. Compatível com Flask/SQLite

Retorne o código pronto para uso.
"""
    
    print(f"\n✨ Gerando feature: {descricao[:50]}...")
    resposta = gerar_resposta_grok(prompt, tipo='dev_assistant')
    
    return resposta

def analisar_projeto_completo(diretorio='.'):
    """Analisa todo o projeto e gera relatório"""
    arquivos_python = list(Path(diretorio).glob('*.py'))
    
    relatorio = "# Análise Completa do Projeto\n\n"
    relatorio += f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    relatorio += f"**Arquivos analisados:** {len(arquivos_python)}\n\n"
    
    for arquivo in arquivos_python:
        print(f"\n📊 Analisando {arquivo}...")
        analise = analisar_arquivo(str(arquivo))
        relatorio += f"\n## {arquivo.name}\n\n{analise}\n\n---\n"
    
    # Salvar relatório
    with open('ANALISE_PROJETO.md', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("\n✅ Relatório completo salvo em: ANALISE_PROJETO.md")
    return relatorio

def chat_interativo():
    """Modo chat interativo com o assistente"""
    print("\n🤖 Assistente de Desenvolvimento Ativo")
    print("Digite 'sair' para encerrar\n")
    
    historico = []
    
    while True:
        pergunta = input("Você: ").strip()
        
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            print("👋 Até logo!")
            break
        
        if not pergunta:
            continue
        
        historico.append({"role": "user", "content": pergunta})
        
        resposta = chat_completion(historico, tipo='dev_assistant')
        print(f"\n🤖 Assistente: {resposta}\n")
        
        historico.append({"role": "assistant", "content": resposta})

if __name__ == "__main__":
    from datetime import datetime
    
    print("="*60)
    print("🤖 ASSISTENTE DE DESENVOLVIMENTO COM IA")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python assistente_dev.py analisar <arquivo.py>")
        print("  python assistente_dev.py documentar <arquivo.py>")
        print("  python assistente_dev.py testar <arquivo.py>")
        print("  python assistente_dev.py otimizar <arquivo.py>")
        print("  python assistente_dev.py seguranca <arquivo.py>")
        print("  python assistente_dev.py feature 'descrição da feature'")
        print("  python assistente_dev.py projeto")
        print("  python assistente_dev.py chat")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando == 'analisar' and len(sys.argv) > 2:
        resultado = analisar_arquivo(sys.argv[2])
        print(f"\n{resultado}")
        
    elif comando == 'documentar' and len(sys.argv) > 2:
        resultado = gerar_documentacao(sys.argv[2])
        print(f"\n{resultado}")
        
    elif comando == 'testar' and len(sys.argv) > 2:
        resultado = sugerir_testes(sys.argv[2])
        print(f"\n{resultado}")
        
    elif comando == 'otimizar' and len(sys.argv) > 2:
        resultado = otimizar_performance(sys.argv[2])
        print(f"\n{resultado}")
        
    elif comando == 'seguranca' and len(sys.argv) > 2:
        resultado = revisar_seguranca(sys.argv[2])
        print(f"\n{resultado}")
        
    elif comando == 'feature' and len(sys.argv) > 2:
        descricao = ' '.join(sys.argv[2:])
        resultado = gerar_feature(descricao)
        print(f"\n{resultado}")
        
    elif comando == 'projeto':
        resultado = analisar_projeto_completo()
        
    elif comando == 'chat':
        chat_interativo()
        
    else:
        print("❌ Comando inválido!")
