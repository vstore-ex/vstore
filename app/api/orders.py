from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import User, Order, OrderItem, UserCart, Game
from app.schemas import OrderCreate, OrderOut, OrderItemOut
from app.api.auth.authorization import get_current_user

router = APIRouter(prefix="/me/orders", tags=["orders"])

TAX_RATE = 0.05

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #1 get current cart items
    cart_items = db.query(UserCart).filter(UserCart.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="cart is empty")

    #2 calculate totals with explicit float conversion
    subtotal = 0.0
    for item in cart_items:
        if item.product:
            subtotal += float(item.product.price)

    tax = subtotal * TAX_RATE
    total = subtotal + tax

    try:
        #3 create order
        order = Order(
            user_id=current_user.id,
            status="paid",
            payment_method=order_in.payment_method,
            subtotal=round(subtotal, 2),
            tax=round(tax, 2),
            total=round(total, 2)
        )
        db.add(order)
        db.flush()

        #4 create OrderItems from cart
        for item in cart_items:
            if item.product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    price_at_purchase=float(item.product.price)
                )
                db.add(order_item)

        db.query(UserCart).filter(UserCart.user_id == current_user.id).delete()

        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

    # construct response
    items_out = [
        OrderItemOut(product_id=oi.product_id, price_at_purchase=float(oi.price_at_purchase))
        for oi in order.items
    ]

    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=float(order.subtotal),
        tax=float(order.tax),
        total=float(order.total),
        created_at=order.created_at,
        items=items_out
    )

@router.get("/", response_model=List[OrderOut])
async def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()

    result = []
    for o in orders:
        items_out = [
            OrderItemOut(product_id=oi.product_id, price_at_purchase=float(oi.price_at_purchase))
            for oi in o.items
        ]
        result.append(OrderOut(
            id=o.id,
            status=o.status,
            subtotal=float(o.subtotal),
            tax=float(o.tax),
            total=float(o.total),
            created_at=o.created_at,
            items=items_out
        ))
    return result

@router.get("/{order_id}", response_model=OrderOut)
async def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")

    items_out = [
        OrderItemOut(product_id=oi.product_id, price_at_purchase=float(oi.price_at_purchase))
        for oi in order.items
    ]

    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=float(order.subtotal),
        tax=float(order.tax),
        total=float(order.total),
        created_at=order.created_at,
        items=items_out
    )