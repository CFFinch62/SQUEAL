-- Aggregate functions and GROUP BY

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    amount INTEGER
);

INSERT INTO orders (id, customer, amount) VALUES (1, 'Alice', 100);
INSERT INTO orders (id, customer, amount) VALUES (2, 'Alice', 50);
INSERT INTO orders (id, customer, amount) VALUES (3, 'Bob', 75);

SELECT COUNT(*) AS order_count, SUM(amount) AS total, AVG(amount) AS average
FROM orders;

SELECT customer, SUM(amount) AS total_spent
FROM orders
GROUP BY customer
ORDER BY total_spent DESC;
