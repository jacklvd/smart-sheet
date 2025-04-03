from datetime import datetime
from app import db


class Summary(db.Model):
    """Summary model for storing text summaries with automatic cleanup"""

    __tablename__ = "summaries"

    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    original_length = db.Column(db.Integer, nullable=False)
    summary_length = db.Column(db.Integer, nullable=False)
    summary_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # TTL field to track when record should be removed
    expires_at = db.Column(db.DateTime, nullable=True)

    def __init__(
        self, original_text, summary_text, original_length, summary_length, summary_type
    ):
        self.original_text = original_text
        self.summary_text = summary_text
        self.original_length = original_length
        self.summary_length = summary_length
        self.summary_type = summary_type

    def to_dict(self):
        return {
            "id": self.id,
            "summary": self.summary_text,
            "original_length": self.original_length,
            "summary_length": self.summary_length,
            "reduction_percentage": (
                round((1 - (self.summary_length / self.original_length)) * 100, 1)
                if self.original_length > 0
                else 0
            ),
            "created_at": self.created_at.isoformat(),
        }


class MarkdownConversion(db.Model):
    """Model for storing markdown conversions with automatic cleanup"""

    __tablename__ = "markdown_conversions"

    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    converted_text = db.Column(db.Text, nullable=False)
    conversion_type = db.Column(
        db.String(20), nullable=False
    )  # 'to_markdown' or 'to_text'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # TTL field to track when record should be removed
    expires_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, original_text, converted_text, conversion_type):
        self.original_text = original_text
        self.converted_text = converted_text
        self.conversion_type = conversion_type

    def to_dict(self):
        return {
            "id": self.id,
            "result": self.converted_text,
            "conversion_type": self.conversion_type,
            "created_at": self.created_at.isoformat(),
        }
