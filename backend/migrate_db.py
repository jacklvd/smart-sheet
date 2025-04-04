"""
Migration script to add expires_at column to existing tables
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from app import create_app, db
from models.summary import Summary, MarkdownConversion


def add_expires_at_column():
    """Add expires_at column to existing tables if it doesn't exist"""
    app = create_app()

    with app.app_context():
        # Check if the columns exist in the tables
        inspector = db.inspect(db.engine)

        # Check summaries table
        summaries_columns = [col["name"] for col in inspector.get_columns("summaries")]
        needs_summaries_migration = "expires_at" not in summaries_columns

        # Check markdown_conversions table
        markdown_columns = [
            col["name"] for col in inspector.get_columns("markdown_conversions")
        ]
        needs_markdown_migration = "expires_at" not in markdown_columns

        if needs_summaries_migration or needs_markdown_migration:
            print("Database tables need migration to add expires_at column")

            # Get data cleanup settings from config
            ttl = app.config.get("DATA_TTL", timedelta(hours=1))

            # Create the columns using SQLAlchemy Core
            with db.engine.begin() as conn:
                if needs_summaries_migration:
                    print("Adding expires_at column to summaries table...")
                    conn.execute(
                        db.text("ALTER TABLE summaries ADD COLUMN expires_at DATETIME")
                    )

                if needs_markdown_migration:
                    print("Adding expires_at column to markdown_conversions table...")
                    conn.execute(
                        db.text(
                            "ALTER TABLE markdown_conversions ADD COLUMN expires_at DATETIME"
                        )
                    )

            # Update existing records with expiration dates
            now = datetime.utcnow()
            expires_at = now + ttl
            cutoff_time = now - ttl

            # Update existing summaries
            if needs_summaries_migration:
                try:
                    # Handle old records (older than TTL)
                    db.session.query(Summary).filter(
                        Summary.created_at <= cutoff_time
                    ).update({"expires_at": now}, synchronize_session=False)

                    # Handle newer records
                    db.session.query(Summary).filter(
                        Summary.created_at > cutoff_time
                    ).update(
                        {"expires_at": datetime.utcnow() + ttl},
                        synchronize_session=False,
                    )

                    print("Updated expiration dates for existing summaries")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error updating summaries: {e}")

            # Update existing markdown conversions
            if needs_markdown_migration:
                try:
                    # Handle old records (older than TTL)
                    db.session.query(MarkdownConversion).filter(
                        MarkdownConversion.created_at <= cutoff_time
                    ).update({"expires_at": now}, synchronize_session=False)

                    # Handle newer records
                    db.session.query(MarkdownConversion).filter(
                        MarkdownConversion.created_at > cutoff_time
                    ).update(
                        {"expires_at": datetime.utcnow() + ttl},
                        synchronize_session=False,
                    )

                    print("Updated expiration dates for existing markdown conversions")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error updating markdown conversions: {e}")

            db.session.commit()
            print("Database migration completed successfully!")
        else:
            print(
                "Database tables already have expires_at column. No migration needed."
            )


if __name__ == "__main__":
    add_expires_at_column()
