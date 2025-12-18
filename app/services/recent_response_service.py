from sqlalchemy.orm import Session
from app.db.models import Chat, User, Document

def get_recent_responses(db: Session, limit: int = 5):
    results = (
        db.query(
            User.username.label("username"),
            Document.filename.label("filename"),
            Chat.response_time.label("response_time"),
            Chat.qtoken.label("qtokens"),
            Chat.atoken.label("atokens"),
            (Chat.qtoken + Chat.atoken).label("total_tokens"),
            Chat.cost.label("cost"),
        )
        .join(User, Chat.user_id == User.id)
        .outerjoin(Document, Document.user_id == User.id)
        .order_by(Chat.id.desc())
        .limit(limit)
        .all()
    )

    return results
