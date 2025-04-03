import os
import sys
import subprocess
from app import create_app, db
from services.cleanup import cleanup_service
import sqlalchemy as sa

app = create_app()


# Function to check if a column exists in a table
def check_column_exists(table_name, column_name):
    """Check if a column exists in the database table"""
    with app.app_context():
        inspector = sa.inspect(db.engine)
        if inspector.has_table(table_name):
            columns = [col["name"] for col in inspector.get_columns(table_name)]
            return column_name in columns
        return False


# Create database tables if they don't exist
with app.app_context():
    try:
        # Check if tables exist before creating them
        if not db.engine.dialect.has_table(db.engine.connect(), "summaries"):
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully")
        else:
            print("Database tables already exist")

            # Check if expires_at column exists in the tables
            summaries_has_expires = check_column_exists("summaries", "expires_at")
            markdown_has_expires = check_column_exists(
                "markdown_conversions", "expires_at"
            )

            if not summaries_has_expires or not markdown_has_expires:
                print("Database tables need migration to add expires_at column")

                # Run the migration script
                try:
                    migration_script = os.path.join(
                        os.path.dirname(__file__), "migrate_db.py"
                    )

                    # Check if migration script exists, if not create it
                    if not os.path.exists(migration_script):
                        print("Creating migration script...")
                        with open(migration_script, "w") as f:
                            f.write(
                                '''"""
Migration script to add expires_at column to existing tables
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import Flask app and database
from app import create_app, db
from models.summary import Summary, MarkdownConversion

def add_expires_at_column():
    """Add expires_at column to existing tables if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        # Check if the columns exist in the tables
        inspector = db.inspect(db.engine)
        
        # Check summaries table
        summaries_columns = [col['name'] for col in inspector.get_columns('summaries')]
        needs_summaries_migration = 'expires_at' not in summaries_columns
        
        # Check markdown_conversions table
        markdown_columns = [col['name'] for col in inspector.get_columns('markdown_conversions')]
        needs_markdown_migration = 'expires_at' not in markdown_columns
        
        if needs_summaries_migration or needs_markdown_migration:
            print("Database tables need migration to add expires_at column")
            
            # Get data cleanup settings from config
            ttl = app.config.get('DATA_TTL', timedelta(hours=1))
            
            # Create the columns using SQLAlchemy Core
            with db.engine.begin() as conn:
                if needs_summaries_migration:
                    print("Adding expires_at column to summaries table...")
                    conn.execute(db.text("ALTER TABLE summaries ADD COLUMN expires_at DATETIME"))
                    
                if needs_markdown_migration:
                    print("Adding expires_at column to markdown_conversions table...")
                    conn.execute(db.text("ALTER TABLE markdown_conversions ADD COLUMN expires_at DATETIME"))
            
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
                        synchronize_session=False
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
                        synchronize_session=False
                    )
                    
                    print("Updated expiration dates for existing markdown conversions")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error updating markdown conversions: {e}")
            
            db.session.commit()
            print("Database migration completed successfully!")
        else:
            print("Database tables already have expires_at column. No migration needed.")

if __name__ == "__main__":
    add_expires_at_column()
'''
                            )
                        print("Migration script created")

                    print("Running database migration...")
                    subprocess.run([sys.executable, migration_script], check=True)
                    print("Database migration completed")
                except Exception as e:
                    print(f"Error during migration: {e}")
                    print("You may need to run the migration script manually")
            else:
                print("Database schema is up to date")

    except Exception as e:
        print(f"Error checking/creating database tables: {e}")

# Start the data cleanup service
with app.app_context():
    cleanup_service.init_app(app)
    cleanup_service.start()
    print(
        f"Data cleanup service started - interval: {app.config['DATA_CLEANUP_INTERVAL']} seconds"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
