# AGUAPURA
É um projeto de venda de garrafas termicas e Serviço de personalização do produto

USE aguapura;

-- Ver a estrutura atual
SHOW COLUMNS FROM usuarios WHERE Field = 'tipo';

-- Corrigir para aceitar funcionario
ALTER TABLE usuarios 
MODIFY COLUMN tipo ENUM('admin','cliente','funcionario') 
NOT NULL DEFAULT 'cliente';

-- Verificar se funcionou
SHOW COLUMNS FROM usuarios WHERE Field = 'tipo';

ALTER TABLE usuarios 
MODIFY COLUMN tipo ENUM('cliente','funcionario','admin') 
DEFAULT 'cliente';
