from datetime import datetime, timedelta
import threading
import time
from app import db
from models.summary import Summary, MarkdownConversion
from flask import current_app
import logging
import sqlalchemy as sa

logger = logging.getLogger(__name__)


class DataCleanupService:
    """Service to periodically clean up old database records"""

    def __init__(self, app=None):
        self.app = app
        self.cleanup_thread = None
        self.running = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app

    def start(self):
        """Start the cleanup service in a background thread"""
        if self.cleanup_thread is not None and self.cleanup_thread.is_alive():
            logger.info("Cleanup service is already running")
            return

        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        logger.info("Data cleanup service started")

    def stop(self):
        """Stop the cleanup service"""
        self.running = False
        if self.cleanup_thread is not None:
            self.cleanup_thread.join(timeout=5.0)
            logger.info("Data cleanup service stopped")

    def _cleanup_worker(self):
        """Background worker that runs the cleanup tasks"""
        with self.app.app_context():
            cleanup_interval = self.app.config["DATA_CLEANUP_INTERVAL"]
            logger.info(f"Data cleanup worker running every {cleanup_interval} seconds")

            while self.running:
                try:
                    self._perform_cleanup()
                except Exception as e:
                    logger.error(f"Error during data cleanup: {str(e)}")

                # Sleep until next cleanup
                time.sleep(cleanup_interval)

    def _check_column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        inspector = sa.inspect(db.engine)
        columns = [col["name"] for col in inspector.get_columns(table_name)]
        return column_name in columns

    def _perform_cleanup(self):
        """Perform the actual data cleanup"""
        logger.info("Running scheduled data cleanup")

        # Check if expires_at column exists in the tables
        summaries_has_expires = self._check_column_exists("summaries", "expires_at")
        markdown_has_expires = self._check_column_exists(
            "markdown_conversions", "expires_at"
        )

        if not summaries_has_expires or not markdown_has_expires:
            logger.warning(
                "Database tables missing expires_at column. Skipping cleanup operation."
            )
            return

        # Get config values
        ttl = self.app.config["DATA_TTL"]
        max_records = self.app.config["MAX_RECORDS_PER_TABLE"]

        # Set current time for consistent comparisons
        now = datetime.utcnow()
        cutoff_time = now - ttl

        with db.session.begin():
            try:
                # Update expired_at for records that don't have it set
                self._update_expiration_dates(Summary, cutoff_time, now)
                self._update_expiration_dates(MarkdownConversion, cutoff_time, now)

                # Delete expired records
                summary_deleted = (
                    db.session.query(Summary).filter(Summary.expires_at <= now).delete()
                )

                markdown_deleted = (
                    db.session.query(MarkdownConversion)
                    .filter(MarkdownConversion.expires_at <= now)
                    .delete()
                )

                # Enforce maximum records limit by removing oldest records if needed
                summary_count = db.session.query(Summary).count()
                if summary_count > max_records:
                    excess = summary_count - max_records
                    oldest_summaries = (
                        db.session.query(Summary)
                        .order_by(Summary.created_at)
                        .limit(excess)
                        .all()
                    )

                    for record in oldest_summaries:
                        db.session.delete(record)

                    logger.info(
                        f"Removed {excess} oldest summary records to maintain limit"
                    )

                markdown_count = db.session.query(MarkdownConversion).count()
                if markdown_count > max_records:
                    excess = markdown_count - max_records
                    oldest_conversions = (
                        db.session.query(MarkdownConversion)
                        .order_by(MarkdownConversion.created_at)
                        .limit(excess)
                        .all()
                    )

                    for record in oldest_conversions:
                        db.session.delete(record)

                    logger.info(
                        f"Removed {excess} oldest markdown conversion records to maintain limit"
                    )

                logger.info(
                    f"Cleanup completed. Deleted {summary_deleted} summary records and "
                    f"{markdown_deleted} markdown conversion records based on TTL."
                )

            except Exception as e:
                logger.error(f"Error during database cleanup: {str(e)}")
                db.session.rollback()
                raise

    def _update_expiration_dates(self, model, cutoff_time, now):
        """Update expiration dates for records that don't have them set"""
        # Update old records that should already be expired
        db.session.query(model).filter(
            model.created_at <= cutoff_time, model.expires_at.is_(None)
        ).update({"expires_at": now}, synchronize_session=False)

        # Set expiration dates for newer records without them
        ttl = self.app.config["DATA_TTL"]
        db.session.query(model).filter(
            model.created_at > cutoff_time, model.expires_at.is_(None)
        ).update({"expires_at": model.created_at + ttl}, synchronize_session=False)


# Singleton instance
cleanup_service = DataCleanupService()
