from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import User, SupportArticle, SupportTicket
from app.schemas import (
    SupportArticleOut,
    SupportArticlePaginatedResponse,
    SupportTicketCreate,
    SupportTicketOut,
    SupportTicketUpdate
)
from app.api.auth.authorization import get_current_user, require_admin

router = APIRouter(tags=["support"])

# public

@router.get("/articles", response_model=SupportArticlePaginatedResponse)
async def list_support_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * page_size

    total = db.query(SupportArticle).count()
    articles = db.query(SupportArticle).offset(offset).limit(page_size).all()

    total_pages = (total + page_size - 1) // page_size

    return SupportArticlePaginatedResponse(
        items=articles,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/articles/{article_id}", response_model=SupportArticleOut)
async def get_support_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    article = db.query(SupportArticle).filter(SupportArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="article not found")
    return article

# user tickets

@router.post("/tickets", response_model=SupportTicketOut, status_code=status.HTTP_201_CREATED)
async def create_support_ticket(
    ticket_in: SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = SupportTicket(
        user_id=current_user.id,
        subject=ticket_in.subject,
        message=ticket_in.message,
        priority=ticket_in.priority or "medium"
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/me/tickets", response_model=List[SupportTicketOut])
async def get_my_support_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id).all()

# admin tickets

@router.get("/admin/tickets", response_model=List[SupportTicketOut])
async def list_all_support_tickets(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    return db.query(SupportTicket).all()

@router.patch("/admin/tickets/{ticket_id}", response_model=SupportTicketOut)
async def update_support_ticket(
    ticket_id: int,
    ticket_in: SupportTicketUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="ticket not found")

    if ticket_in.status is not None:
        ticket.status = ticket_in.status
    if ticket_in.priority is not None:
        ticket.priority = ticket_in.priority

    db.commit()
    db.refresh(ticket)
    return ticket