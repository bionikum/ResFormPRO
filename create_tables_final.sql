-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    stripe_customer_id VARCHAR(100),
    subscription_status VARCHAR(20) DEFAULT 'inactive'
);

-- Создание индекса для email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Создадим администратора
INSERT INTO users (email, name, role, is_active, password_hash)
VALUES ('admin@resformpro.ru', 'Administrator', 'admin', TRUE, '')
ON CONFLICT (email) DO NOTHING;
