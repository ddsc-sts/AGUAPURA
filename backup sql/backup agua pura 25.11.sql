-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: aguapura
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `carrinho`
--

DROP TABLE IF EXISTS `carrinho`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `carrinho` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` varchar(255) NOT NULL,
  `produto_id` int NOT NULL,
  `quantidade` int DEFAULT '1',
  `cor` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_carrinho_produto` (`produto_id`),
  CONSTRAINT `fk_carrinho_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carrinho`
--

LOCK TABLES `carrinho` WRITE;
/*!40000 ALTER TABLE `carrinho` DISABLE KEYS */;
INSERT INTO `carrinho` VALUES (3,'d2ea2769-981b-4f7d-808f-0c39c9772f16',1,1,'Preto'),(7,'832a56c4-b3e1-4563-b1df-61a875edf26a',1,1,'Preto');
/*!40000 ALTER TABLE `carrinho` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES (1,'Garrafa'),(2,'Copo'),(3,'Acessório');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `produto` varchar(150) DEFAULT NULL,
  `quantidade` int DEFAULT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_compra_usuario` (`usuario_id`),
  CONSTRAINT `fk_compra_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enderecos_usuarios`
--

DROP TABLE IF EXISTS `enderecos_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enderecos_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `nome_destinatario` varchar(150) NOT NULL,
  `cpf` varchar(20) NOT NULL,
  `rua` varchar(150) NOT NULL,
  `numero` varchar(20) NOT NULL,
  `bairro` varchar(100) DEFAULT NULL,
  `cidade` varchar(100) NOT NULL,
  `estado` varchar(2) NOT NULL,
  `cep` varchar(20) NOT NULL,
  `criado_em` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_end_usuario` (`usuario_id`),
  CONSTRAINT `fk_end_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enderecos_usuarios`
--

LOCK TABLES `enderecos_usuarios` WRITE;
/*!40000 ALTER TABLE `enderecos_usuarios` DISABLE KEYS */;
INSERT INTO `enderecos_usuarios` VALUES (1,1,'DANIEL DOS SANTOS COSTA','16000763948','Rua Janaúba','704','Jardim Iririu','Joinville','SC','89224280','2025-11-24 22:10:41'),(2,1,'Administrador','16000763948','Rua areia Branca','704','Jardim Iririu','Joinville','SC','89224280','2025-11-24 22:42:16');
/*!40000 ALTER TABLE `enderecos_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favoritos`
--

DROP TABLE IF EXISTS `favoritos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favoritos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `produto_id` int DEFAULT NULL,
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_fav_usuario` (`usuario_id`),
  KEY `fk_fav_produto` (`produto_id`),
  CONSTRAINT `fk_fav_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`),
  CONSTRAINT `fk_fav_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favoritos`
--

LOCK TABLES `favoritos` WRITE;
/*!40000 ALTER TABLE `favoritos` DISABLE KEYS */;
/*!40000 ALTER TABLE `favoritos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `imagens_produto`
--

DROP TABLE IF EXISTS `imagens_produto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imagens_produto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produto_id` int NOT NULL,
  `imagem` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_img_produto` (`produto_id`),
  CONSTRAINT `fk_img_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `imagens_produto`
--

LOCK TABLES `imagens_produto` WRITE;
/*!40000 ALTER TABLE `imagens_produto` DISABLE KEYS */;
/*!40000 ALTER TABLE `imagens_produto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagamentos_usuarios`
--

DROP TABLE IF EXISTS `pagamentos_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagamentos_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `tipo` enum('PIX','CARTAO') NOT NULL,
  `nome_impresso` varchar(150) DEFAULT NULL,
  `numero_mascarado` varchar(30) DEFAULT NULL,
  `validade` varchar(7) DEFAULT NULL,
  `chave_pix` varchar(150) DEFAULT NULL,
  `criado_em` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_pag_usuario` (`usuario_id`),
  CONSTRAINT `fk_pag_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagamentos_usuarios`
--

LOCK TABLES `pagamentos_usuarios` WRITE;
/*!40000 ALTER TABLE `pagamentos_usuarios` DISABLE KEYS */;
INSERT INTO `pagamentos_usuarios` VALUES (1,1,'CARTAO','DANIEL DOS SANTOS COSTA','**** **** **** 2523','10/23',NULL,'2025-11-24 22:12:02'),(2,1,'CARTAO','DANIEL DOS SANTOS COSTA','**** **** **** 5235','22/22',NULL,'2025-11-24 22:35:40');
/*!40000 ALTER TABLE `pagamentos_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_itens`
--

DROP TABLE IF EXISTS `pedido_itens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_itens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pedido_id` int NOT NULL,
  `produto_id` int NOT NULL,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_item_pedido` (`pedido_id`),
  KEY `fk_item_produto` (`produto_id`),
  CONSTRAINT `fk_item_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_item_produto` FOREIGN KEY (`produto_id`) REFERENCES `produtos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_itens`
--

LOCK TABLES `pedido_itens` WRITE;
/*!40000 ALTER TABLE `pedido_itens` DISABLE KEYS */;
INSERT INTO `pedido_itens` VALUES (1,2,1,1,119.90),(2,2,3,1,29.90),(3,3,1,1,119.90),(4,3,3,1,29.90),(5,4,1,1,119.90);
/*!40000 ALTER TABLE `pedido_itens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `valor_total` decimal(10,2) DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pendente',
  `criado_em` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `pagamento_metodo` varchar(30) DEFAULT NULL,
  `cliente_nome` varchar(150) DEFAULT NULL,
  `cliente_cpf` varchar(30) DEFAULT NULL,
  `cliente_endereco` text,
  PRIMARY KEY (`id`),
  KEY `fk_pedido_usuario` (`usuario_id`),
  CONSTRAINT `fk_pedido_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (2,1,161.80,'entregue','2025-11-24 22:25:45','CARTAO','DANIEL DOS SANTOS COSTA','16000763948','Rua Janaúba, 704 - Jardim Iririu - Joinville/SC - CEP 89224280'),(3,1,161.80,'aguardando_pagamento','2025-11-24 22:35:40','CARTAO','Administrador','16000763948','Rua areia Branca, 704 - Jardim Iririu - Joinville/SC - CEP 89224280'),(4,1,131.90,'aguardando_pagamento','2025-11-24 22:42:16','CARTAO','Administrador','16000763948','Rua areia Branca, 704 - Jardim Iririu - Joinville/SC - CEP 89224280');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produtos`
--

DROP TABLE IF EXISTS `produtos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produtos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `descricao` text,
  `preco` decimal(10,2) NOT NULL,
  `categoria` varchar(50) NOT NULL,
  `imagem_principal` varchar(255) NOT NULL,
  `estoque` int DEFAULT '0',
  `criado_em` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produtos`
--

LOCK TABLES `produtos` WRITE;
/*!40000 ALTER TABLE `produtos` DISABLE KEYS */;
INSERT INTO `produtos` VALUES (1,'Copo Térmico Classic 600ml','Copo térmico com parede dupla e vedação superior. Mantém bebidas quentes ou frias por longos períodos.',94.90,'Copo','/static/img/copo_classic.png',15,'2025-11-25 19:10:00'),(2,'Copo Térmico Hexagonal 450ml','Copo térmico estiloso com design hexagonal e isolamento de alto desempenho. Ideal para uso diário.',79.90,'Copo','/static/img/copo_hexagonal.png',20,'2025-11-25 19:10:00'),(3,'Copo Térmico Grip 500ml','Copo térmico com anel de silicone antiderrapante. Excelente para bebidas quentes e geladas.',89.90,'Copo','/static/img/copo_grip.png',18,'2025-11-25 19:10:00'),(4,'Garrafa com Canudo 900ml Travel','Garrafa térmico grande com alça lateral e canudo. Ideal para hidratação diária e atividades ao ar livre.',119.90,'Garrafa','/static/img/garrafa_canudo.png',14,'2025-11-25 19:10:00'),(5,'Taça Térmica Wine 350ml','Taça térmica premium, ideal para vinho, drinks ou bebidas geladas. Parede dupla e acabamento fosco.',74.90,'Copo','/static/img/copo_wine.png',22,'2025-11-25 19:10:00'),(6,'Caneca Térmica Café 350ml','Caneca térmica com alça ergonômica. Mantém a temperatura ideal para café, chá e outras bebidas.',69.90,'Copo','/static/img/copo_caneca.png',25,'2025-11-25 19:10:00'),(7,'Garrafa Térmica Slim 500ml','Garrafa térmica compacta com tampa translúcida. Perfeita para levar na bolsa ou mochila.',109.90,'Garrafa','/static/img/garrafa_slim.png',16,'2025-11-25 19:10:00'),(8,'Garrafa Térmica Tritan 600ml','Garrafa com corpo resistente e tampa flip com trava. Ideal para esportes e uso diário.',79.90,'Garrafa','/static/img/garrafa_tritan.png',19,'2025-11-25 19:10:00'),(9,'Garrafa Esportiva Outdoor 950ml','Garrafa térmica de grande capacidade com alça integrada. Perfeita para trilhas, academia e longas rotinas.',139.90,'Garrafa','/static/img/garrafa_esportiva.png',12,'2025-11-25 19:10:00'),(10,'Tampa Extra para Copos e Garrafas','Tampa extra universal compatível com diversos modelos AquaPura. Material resistente, livre de BPA.',24.90,'Acessório','/static/img/copo_tampa.png',30,'2025-11-25 19:10:00');
/*!40000 ALTER TABLE `produtos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `tipo` enum('admin','cliente') DEFAULT 'cliente',
  `criado_em` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Administrador','admin@aguapura.com','scrypt:32768:8:1$so3Bg6a8P0OXkBQg$d336d5fe08059bf79b0d3ae47e11260030706a2c9b010b1d1dd66ae79cac169e4040b74cd8a888bbac3a6f2eff263749a018e4084310bb8cc69fd3785b3f5bc6','uploads/avatars/user_admin.png','admin','2025-11-24 21:42:17'),(2,'daniel','teste@teste.com','scrypt:32768:8:1$8wRrR5kCYscW53Rv$df2a6f41c305f1854908af5f3d0eba7bdd7f1910ec387001baff74255c4556f61cf0c7582c9cb7273616aad87d0cc5db075ca4ab4862b837d8fed82442e1c9d7','uploads/avatars/user.png','cliente','2025-11-24 22:12:44');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-25 16:24:03
