from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal

from app.core.db import get_db
from app.models import User, Game, UserCart
from app.schemas import CartResponse, CartItemOut
from app.api.auth.authorization import get_current_user

router = APIRouter(tags=["cart"])

TAX_RATE = Decimal("0.05")  # 5% tax

@router.get("/me/cart", response_model=CartResponse)
async def get_my_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items = db.query(UserCart).options(
        joinedload(UserCart.product)
    ).filter(UserCart.user_id == current_user.id).all()

    subtotal = Decimal("0.00")
    cart_items = []
    for item in items:
        price = Decimal(str(item.product.price)) if item.product else Decimal("0.00")
        subtotal += price
        cart_items.append({
            "product_id": item.product.id if item.product else None,
            "title": item.product.title if item.product else "Unknown",
            "price": price,
            "added_at": item.added_at
        })

    tax = subtotal * TAX_RATE
    total = subtotal + tax

    return CartResponse(
        items=cart_items,
        subtotal=subtotal.quantize(Decimal("0.01")),
        tax=tax.quantize(Decimal("0.01")),
        total=total.quantize(Decimal("0.01")),
        currency="UAH"
    )

@router.post("/me/cart/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Game).filter(Game.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="product not found")

    existing = db.query(UserCart).filter(
        UserCart.user_id == current_user.id,
        UserCart.product_id == product_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="product already in cart")

    cart_item = UserCart(user_id=current_user.id, product_id=product_id)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return {"message": "product added to cart"}

@router.delete("/me/cart/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(UserCart).filter(
        UserCart.user_id == current_user.id,
        UserCart.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="product not found in cart")

    db.delete(item)
    db.commit()

    return None

@router.delete("/me/cart", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(UserCart).filter(UserCart.user_id == current_user.id).delete()
    db.commit()

    return None