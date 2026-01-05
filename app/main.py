from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app import models, schemas
from app.database import get_db
from typing import List

app = FastAPI()


@app.post("/orders", response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(status=models.OrderStatus.PENDING)
    db.add(new_order)

    try:
        db.flush()

        for item in order_data.items:
            # CRITICAL: .with_for_update() prevents race conditions
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id
            ).with_for_update().first()

            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {product.name}"
                )

            # Reduce stock
            product.stock_quantity -= item.quantity

            # Create OrderItem
            order_item = models.OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                order_price=product.price
            )
            db.add(order_item)

        # Commit makes the changes permanent and releases the locks
        db.commit()
        db.refresh(new_order)
        return new_order

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")  # Log the actual error for debugging
        raise HTTPException(status_code=500, detail="Transaction failed")


# --- PRODUCT ENDPOINTS ---

@app.post("/products", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=List[schemas.Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


# --- ORDER RETRIEVAL ---

@app.get("/orders", response_model=List[schemas.Order])
def list_orders(db: Session = Depends(get_db)):
    # .options(joinedload(...)) makes the API much faster
    return db.query(models.Order).options(joinedload(models.Order.items)).all()


@app.get("/orders/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).options(
        joinedload(models.Order.items)
    ).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(
        order_id: int,
        status_update: schemas.OrderBase,
        db: Session = Depends(get_db)
):
    # 1. Fetch order with items (using with_for_update for the order itself)
    order = db.query(models.Order).filter(models.Order.id == order_id).with_for_update().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    current_status = order.status
    new_status = status_update.status

    if current_status == new_status:
        return order

    # 2. Transition Validation
    if current_status == models.OrderStatus.CANCELED:
        raise HTTPException(status_code=400, detail="Canceled orders are final.")

    # 3. Handle RESTOCK Logic (Pending -> Canceled)
    if new_status == models.OrderStatus.CANCELED:
        for item in order.items:
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id
            ).with_for_update().first()

            if product:
                # Add the quantity back to inventory
                product.stock_quantity += item.quantity

    # 4. Handle "Already Shipped" restriction
    if current_status == models.OrderStatus.SHIPPED and new_status == models.OrderStatus.CANCELED:
        raise HTTPException(status_code=400, detail="Cannot cancel a shipped order.")

    # 5. Apply changes transactionally
    order.status = new_status
    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update order status")