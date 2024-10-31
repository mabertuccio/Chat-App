-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS chat_db;

-- Seleccionar la base de datos
USE chat_db;

-- Crear la tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,  -- ID único para cada usuario
    nickname VARCHAR(50) NOT NULL UNIQUE,  -- Nombre de usuario único
    created_at DATETIME NOT NULL,  -- Fecha de creación de la cuenta
    connected_at DATETIME  -- Última fecha de conexión
);
