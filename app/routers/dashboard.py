from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.db.models import Document,Chat,User
from sqlalchemy import func,case,asc
from datetime import datetime
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from app.utils.auth import get_current_user

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard-card")
def dash_card_details(db: Session = Depends(get_db),current_user: int = Depends(get_current_user)):

    result = (
        db.query(
            func.count(Document.id).label("total_docs"),

            func.count(
                case((Document.status == "Classified", 1))
            ).label("total_classified"),

            func.count(
                case((Document.status == "Error", 1))
            ).label("total_error"),

            func.coalesce(func.sum(Document.token), 0).label("total_tokens"),
            func.coalesce(func.sum(Document.cost), 0).label("total_cost"),
        )
        .one() 
    )

    return {
        "total_docs": result.total_docs,
        "total_classified": result.total_classified,
        "total_error": result.total_error,
        "total_tokens": result.total_tokens,
        "total_cost": result.total_cost,
    }

@router.get("/token-details")
def token_details(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    last_7_days = datetime.utcnow().date() - timedelta(days=6)

    results = (
        db.query(
            func.date(Document.uploaded_time).label("day"),
            func.coalesce(func.sum(Document.token), 0).label("total_tokens")
        )
        .filter(func.date(Document.uploaded_time) >= last_7_days)
        .group_by(func.date(Document.uploaded_time))
        .all()
    )
    db_data = {
        day: total_tokens
        for day, total_tokens in results
    }
    response = {}

    for i in range(7):
        day = last_7_days + timedelta(days=i)
        response[day.strftime("%B %d")] = db_data.get(day, 0)

    return response



@router.get("/document-type-graph")
def document_type_graph(db: Session = Depends(get_db),current_user: int = Depends(get_current_user)):

    results = (
        db.query(
            Document.classified_class,
            func.count(Document.id).label("total_docs")
        )
        .filter(Document.classified_status == True)
        .group_by(Document.classified_class)
        .order_by(func.count(Document.id).desc())
        .all()
    )

    response = {
        doc_class: count
        for doc_class, count in results
        if doc_class is not None
    }

    return response

@router.post("/list-sessions")
def list_sessions(user_id: int = Depends(get_current_user), db: Session = Depends(get_db),current_user: int = Depends(get_current_user)):
    user = db.query(User).filter(User.email == current_user).first()
    results = (
        db.query(
            Chat.session_id,
            Chat.content
        )
        .filter(Chat.user_id == user.id)
        .distinct(Chat.session_id)
        .order_by(Chat.session_id, asc(Chat.id))
        .all()
    )
    # print(results)
    response = []

    response=[]
    for i in results:
        response.append({"content":i[-1][0].get('content'),"session id":i[0]})


    return response


#document_list_api
class DocumentListRequest(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None   # Classified / Error
    class_type: Optional[str] = None

@router.post("/document-list")
def document_list(payload:DocumentListRequest,db:Session=Depends(get_db),current_user: int = Depends(get_current_user)):

    query=(db.query(
        Document.filename,
            Document.classified_class.label("class_type"),
            Document.status,
            Document.confidence.label("confidence_score"),
            User.username,
            Document.uploaded_time
    ).join(User, User.id == Document.user_id))
    # print('the query is >>>>>>>',query)

    if payload and payload.search:
        query=query.filter(Document.filename.ilike(f"%{payload.search}"))

    if payload and payload.status:
        query=query.filter(Document.status==payload.status)

    if payload and payload.class_type:
        query=query.filter(
            Document.classified_class==payload.class_type
        )

    results=query.order_by(Document.uploaded_time.desc()).all()
    # print(results)
    response=[]
    for r in results:
        response.append({
                       "filename": r.filename,
            "class_type": r.class_type,
            "classified_status": r.status,
            "confidence_score": r.confidence_score,
            "username": r.username,
            "uploaded_time": r.uploaded_time
        })

    return response

