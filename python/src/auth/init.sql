-- Create a new user for MySQL database which can only connect to the MySQL database when it is running on localhost
CREATE USER 'auth_user'@'localhost' IDENTIFIED BY 'Aauth123';

-- Create a new database named 'auth'
CREATE DATABASE auth;

-- Grant all privileges on the 'auth' database to 'auth_user'
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'localhost';

-- Switch to the 'auth' database
USE auth;

-- Create a 'user' table with columns for id, email, and password
CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Insert a user record into the 'user' table which can access gateway API
INSERT INTO user (email, password) VALUES ('swapnil@gmail.com', 'Admin123');