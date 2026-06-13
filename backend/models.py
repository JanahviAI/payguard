from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    amount_inr = db.Column(db.Float, nullable=False)
    amount_mon = db.Column(db.Float, nullable=True)
    client_addr = db.Column(db.String(64), nullable=False)
    freelancer_addr = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="open")
    submission = db.Column(db.Text, nullable=True)
    ai_verdict = db.Column(db.String(32), nullable=True)
    ai_reasoning = db.Column(db.Text, nullable=True)
    ai_confidence = db.Column(db.Float, nullable=True)
    tx_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "requirements": self.requirements,
            "amount_inr": self.amount_inr,
            "amount_mon": self.amount_mon,
            "client_addr": self.client_addr,
            "freelancer_addr": self.freelancer_addr,
            "status": self.status,
            "submission": self.submission,
            "ai_verdict": self.ai_verdict,
            "ai_reasoning": self.ai_reasoning,
            "ai_confidence": self.ai_confidence,
            "tx_hash": self.tx_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
