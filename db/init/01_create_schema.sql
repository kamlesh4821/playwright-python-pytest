-- Initial schema for saucedemo test database
-- Mirrors the saucedemo.com domain: users, products, orders, order_items

CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(100) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    user_type   VARCHAR(50)  NOT NULL DEFAULT 'standard',
    created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) UNIQUE NOT NULL,
    price       NUMERIC(10, 2) NOT NULL,
    description TEXT,
    image_url   VARCHAR(500),
    in_stock    BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    status      VARCHAR(50) NOT NULL DEFAULT 'placed',
    total       NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL DEFAULT 1,
    unit_price  NUMERIC(10, 2) NOT NULL
);

-- Seed saucedemo products
INSERT INTO products (name, price, description, in_stock) VALUES
('Sauce Labs Backpack',     29.99, 'carry.allTheThings() with the sleek, streamlined Sly Pack', TRUE),
('Sauce Labs Bike Light',   9.99,  'A red light isn''t the desired state in testing but it''s a great indicator', TRUE),
('Sauce Labs Bolt T-Shirt', 15.99, 'Get your testing superhero on with the Sauce Labs bolt T-shirt', TRUE),
('Sauce Labs Fleece Jacket',49.99, 'It''s not every day that you come across a midweight quarter-zip fleece jacket', TRUE),
('Sauce Labs Onesie',       7.99,  'Rib snap infant onesie for the junior automation engineer in development', TRUE),
('Test.allTheThings() T-Shirt (Red)', 15.99, 'This is a t-shirt', TRUE)
ON CONFLICT (name) DO NOTHING;
