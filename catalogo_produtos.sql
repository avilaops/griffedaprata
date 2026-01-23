-- ================================================
-- Script SQL: Catálogo Griffe da Prata
-- Gerado em: 23/01/2026 19:12:57
-- ATENÇÃO: PDFs são imagens - Preencher manualmente
-- ================================================

-- Criar tabela de produtos do catálogo
CREATE TABLE IF NOT EXISTS produtos_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL,
    categoria TEXT,
    preco_atacado REAL NOT NULL,
    preco_varejo REAL NOT NULL,
    peso TEXT,
    material TEXT DEFAULT 'Prata 925',
    descricao TEXT,
    imagem TEXT,
    estoque INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    fonte TEXT,
    data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_codigo ON produtos_catalogo(codigo);
CREATE INDEX IF NOT EXISTS idx_categoria ON produtos_catalogo(categoria);
CREATE INDEX IF NOT EXISTS idx_ativo ON produtos_catalogo(ativo);


-- ================================================
-- PRODUTOS PARA INSERIR MANUALMENTE
-- ================================================
-- Arquivos encontrados no catálogo:
-- • Escapularios Terços
-- • FECHO
-- • FEMININA
-- • IBERIA LCB5J
-- • LINHA ESPECIAL
-- • Linha Especial (two)
-- • MASCULINA

-- Template de INSERT (copie e preencha para cada produto):
BEGIN TRANSACTION;

-- EXEMPLOS (substitua com seus dados reais):


-- Categoria: FEMININA
INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('F001', 'Anel Solitário Prata 925', 'FEMININA', 25.0, 62.5, '3g', 'FEMININA.pdf');

INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('F002', 'Brinco Argola Média', 'FEMININA', 30.0, 75.0, '4g', 'FEMININA.pdf');

INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('F003', 'Colar Corrente Veneziana', 'FEMININA', 45.0, 112.5, '5g', 'FEMININA.pdf');


-- Categoria: MASCULINA
INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('M001', 'Pulseira Groumet 8mm', 'MASCULINA', 120.0, 300.0, '25g', 'MASCULINA.pdf');

INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('M002', 'Corrente Cartier 60cm', 'MASCULINA', 180.0, 450.0, '30g', 'MASCULINA.pdf');

INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('M003', 'Anel Quadrado Liso', 'MASCULINA', 55.0, 137.5, '8g', 'MASCULINA.pdf');


-- Categoria: FECHO
INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('FC01', 'Fecho Lagosta 10mm', 'FECHO', 5.0, 12.5, '0.5g', 'FECHO.pdf');

INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('FC02', 'Fecho Boia 8mm', 'FECHO', 4.0, 10.0, '0.3g', 'FECHO.pdf');


-- Categoria: LINHA ESPECIAL
INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('LE01', 'Pingente Cruz Cravejada', 'LINHA ESPECIAL', 85.0, 212.5, '6g', 'LINHA ESPECIAL.pdf');

INSERT INTO produtos_catalogo (codigo, titulo, categoria, preco_atacado, preco_varejo, peso, fonte)
VALUES ('LE02', 'Conjunto Coração Zircônia', 'LINHA ESPECIAL', 150.0, 375.0, '10g', 'LINHA ESPECIAL.pdf');


COMMIT;


-- ================================================
-- QUERIES ÚTEIS
-- ================================================

-- Ver todos os produtos por categoria
-- SELECT categoria, COUNT(*) as total FROM produtos_catalogo GROUP BY categoria;

-- Ver produtos mais caros
-- SELECT codigo, titulo, preco_varejo FROM produtos_catalogo ORDER BY preco_varejo DESC LIMIT 10;

-- Calcular preço médio por categoria
-- SELECT categoria, AVG(preco_atacado) as media_atacado, AVG(preco_varejo) as media_varejo FROM produtos_catalogo GROUP BY categoria;

-- Total de produtos ativos
-- SELECT COUNT(*) as total_ativos FROM produtos_catalogo WHERE ativo = 1;

-- Produtos sem estoque
-- SELECT codigo, titulo, categoria FROM produtos_catalogo WHERE estoque = 0;
