from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.db.models import User, Document

def get_user_details(db: Session):
    return (
        db.query(
            User.username.label("username"),
            User.email.label("email"),
            User.role.label("role"),
            User.last_login.label("last_login"),
            func.count(Document.id).label("docs_processed"),
            case(
                (func.count(Document.id) > 0, "Active"),
                else_="Inactive"
            ).label("status"),
        )
        .outerjoin(Document, Document.user_id == User.id)
        .group_by(User.id)
        .order_by(User.username)
        .all()
    )
