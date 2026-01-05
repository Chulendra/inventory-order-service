from app import models


def test_create_order_success(client, session):
    # 1. Create a product first
    product = models.Product(name="Test Item", price=100.0, stock_quantity=10)
    session.add(product)
    session.commit()

    # 2. Place order
    response = client.post("/orders", json={
        "items": [{"product_id": 1, "quantity": 2}]
    })

    # 3. Assertions
    assert response.status_code == 201
    assert response.json()["status"] == "Pending"

    # Verify stock was reduced
    session.refresh(product)
    assert product.stock_quantity == 8


def test_create_order_insufficient_stock(client, session):
    # 1. Create a product with low stock
    product = models.Product(name="Limited Item", price=50.0, stock_quantity=1)
    session.add(product)
    session.commit()

    # 2. Try to buy 5 (only 1 available)
    response = client.post("/orders", json={
        "items": [{"product_id": 1, "quantity": 5}]
    })

    # 3. Assertions
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    # Verify stock was NOT reduced (Atomicity)
    session.refresh(product)
    assert product.stock_quantity == 1


def test_order_cancellation_restocks(client, session):
    # 1. Setup Product and Order
    product = models.Product(id=1, name="Laptop", price=1000, stock_quantity=5)
    order = models.Order(id=1, status="Pending")
    item = models.OrderItem(order_id=1, product_id=1, quantity=2, order_price=1000)
    session.add_all([product, order, item])
    session.commit()

    # 2. Cancel the order
    response = client.patch("/orders/1/status", json={"status": "Canceled"})

    # 3. Assertions
    assert response.status_code == 200
    session.refresh(product)
    assert product.stock_quantity == 7  # 5 + 2