from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.db import get_db
from app.models import User, Order, OrderItem, UserCart, Game
from app.schemas import OrderCreate, OrderOut, OrderItemOut
from app.api.auth.authorization import get_current_user

router = APIRouter(prefix="/me/orders", tags=["orders"])

TAX_RATE = Decimal("0.05")

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

    #2 calculate totals
    subtotal = Decimal("0.00")
    for item in cart_items:
        if item.product:
            subtotal += Decimal(str(item.product.price))

    tax = subtotal * TAX_RATE
    total = subtotal + tax

    try:
        #3 create order
        order = Order(
            user_id=current_user.id,
            status="paid",
            payment_method=order_in.payment_method,
            subtotal=subtotal.quantize(Decimal("0.01")),
            tax=tax.quantize(Decimal("0.01")),
            total=total.quantize(Decimal("0.01"))
        )
        db.add(order)
        db.flush()

        #4 create OrderItems from cart
        for item in cart_items:
            if item.product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    price_at_purchase=Decimal(str(item.product.price))
                )
                db.add(order_item)

        #5 clear cart
        db.query(UserCart).filter(UserCart.user_id == current_user.id).delete()

        db.commit()
        db.refresh(order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

    # construct response
    items_out = [
        OrderItemOut(product_id=oi.product_id, price_at_purchase=oi.price_at_purchase)
        for oi in order.items
    ]

    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
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
            OrderItemOut(product_id=oi.product_id, price_at_purchase=oi.price_at_purchase)
            for oi in o.items
        ]
        result.append(OrderOut(
            id=o.id,
            status=o.status,
            subtotal=o.subtotal,
            tax=o.tax,
            total=o.total,
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
        OrderItemOut(product_id=oi.product_id, price_at_purchase=oi.price_at_purchase)
        for oi in order.items
    ]

    return OrderOut(
        id=order.id,
        status=order.status,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        created_at=order.created_at,
        items=items_out
    )