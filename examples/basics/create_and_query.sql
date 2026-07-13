-- Create a table, insert some rows, and query them back

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER
);

INSERT INTO users (id, name, age) VALUES (1, 'Alice', 30);
INSERT INTO users (id, name, age) VALUES (2, 'Bob', 25);
INSERT INTO users (id, name, age) VALUES (3, 'Carol', 35);

SELECT * FROM users ORDER BY age;

SELECT name FROM users WHERE age > 28;
