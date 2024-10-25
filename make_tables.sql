CREATE TABLE IF NOT EXISTS suppliers
(
    _id INT NOT NULL,
    name VARCHAR(50),
    email VARCHAR(100),
    PRIMARY KEY (_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS tel
(
    supp_id INT NOT NULL,
    number VARCHAR(20) NOT NULL,
    PRIMARY KEY (number),
    FOREIGN KEY(supp_id) REFERENCES suppliers(_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS orders
(
    order_id INT NOT NULL,
    when_date DATE,
    supp_id INT NOT NULL,
    PRIMARY KEY(order_id),
    FOREIGN KEY(supp_id) REFERENCES suppliers(_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS items
(
    order_id INT NOT NULL,
    part_id INT NOT NULL,
    qty int,
    PRIMARY KEY(order_id, part_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (part_id) REFERENCES parts(_id)
) ENGINE = InnoDB;

