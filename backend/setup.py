import os
import ssl
import stat
import secrets
import subprocess
from pathlib import Path


def setup_nltk():
    """Download required NLTK resources with proper SSL handling if not already installed"""
    print("\n--- Setting up NLTK Resources ---")

    try:
        import nltk
        from nltk.data import find

        # Check if resources are already installed
        resources_needed = []

        try:
            find("tokenizers/punkt")
            print("punkt resource is already installed.")
        except LookupError:
            resources_needed.append("punkt")

        try:
            find("corpora/stopwords")
            print("stopwords resource is already installed.")
        except LookupError:
            resources_needed.append("stopwords")
        try:
            find("corpora/wordnet")
            print("wordnet resource is already installed.")
        except LookupError:
            resources_needed.append("wordnet")

        try:
            find("punkt_tab")
            print("punkt_tab resource is already installed.")
        except LookupError:
            resources_needed.append("punkt_tab")

        # If any resources need to be downloaded
        if resources_needed:
            print(f"Downloading missing NLTK resources: {', '.join(resources_needed)}")

            # Create a custom SSL context that doesn't verify certificates
            # This is a workaround for SSL certificate verification issues on macOS
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            # Download only the missing resources
            for resource in resources_needed:
                nltk.download(resource)
                print(f"Downloaded {resource} successfully")

            print("All required NLTK resources are now installed!")
        else:
            print("All required NLTK resources are already installed!")

        return True
    except Exception as e:
        print(f"Error setting up NLTK resources: {e}")
        return False


def setup_env_file():
    """Generate a secret key and set up the .env file with absolute database path"""
    print("\n--- Setting up Environment File ---")

    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    instance_dir = os.path.join(script_dir, "instance")
    db_path = os.path.join(instance_dir, "app.db")
    database_url = f"sqlite:///{db_path}"

    # Generate a secure token
    secret_key = secrets.token_hex(16)
    print(f"Generated Secret Key: {secret_key}")

    # Check if .env file exists
    env_file = os.path.join(script_dir, ".env")

    env_content = ""
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_content = f.read()

        # Update existing .env file
        lines = env_content.split("\n")
        updated_lines = []

        # Keep track of what we've updated
        updated_secret_key = False
        updated_database_url = False
        updated_cleanup_interval = False
        updated_max_records = False

        for line in lines:
            if line.startswith("SECRET_KEY="):
                updated_lines.append(f"SECRET_KEY={secret_key}")
                updated_secret_key = True
            elif line.startswith("DATABASE_URL="):
                updated_lines.append(f"DATABASE_URL={database_url}")
                updated_database_url = True
            elif line.startswith("DATA_CLEANUP_INTERVAL="):
                updated_cleanup_interval = True
                updated_lines.append(line)
            elif line.startswith("MAX_RECORDS_PER_TABLE="):
                updated_max_records = True
                updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add missing configurations
        if not updated_secret_key:
            updated_lines.append(f"SECRET_KEY={secret_key}")
        if not updated_database_url:
            updated_lines.append(f"DATABASE_URL={database_url}")
        if not updated_cleanup_interval:
            updated_lines.append("DATA_CLEANUP_INTERVAL=3600")  # 1 hour in seconds
        if not updated_max_records:
            updated_lines.append("MAX_RECORDS_PER_TABLE=1000")  # Max records per table

        new_content = "\n".join(updated_lines)
    else:
        # Create new .env file with basic configuration and absolute database path
        new_content = f"""FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY={secret_key}
DATABASE_URL={database_url}
DATA_CLEANUP_INTERVAL=3600
MAX_RECORDS_PER_TABLE=1000
"""

    # Write updated content
    with open(env_file, "w") as f:
        f.write(new_content)

    print(
        f"Environment file updated with secret key, database path, and data cleanup settings!"
    )

    # Return the database_url for later use
    return True, database_url


def db_exists():
    """Check if the database file already exists"""
    script_dir = Path(__file__).parent.absolute()
    instance_dir = os.path.join(script_dir, "instance")
    db_path = os.path.join(instance_dir, "app.db")

    return os.path.exists(db_path)


def init_db():
    """Initialize the database using flask commands with improved path handling"""
    print("\n--- Initializing Database ---")

    # Make sure we're in the correct directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)

    # Check if database already exists
    if db_exists():
        print("Database already exists. Skipping initialization.")
        return True

    # Set Flask environment variables
    os.environ["FLASK_APP"] = "run.py"

    # Create instance directory with proper permissions
    instance_dir = os.path.join(script_dir, "instance")
    if not os.path.exists(instance_dir):
        print(f"Creating instance directory: {instance_dir}")
        os.makedirs(instance_dir, exist_ok=True)

    # Set proper permissions (rwxr-xr-x - 755)
    os.chmod(
        instance_dir,
        stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH,
    )
    print(f"Set permissions 755 on instance directory: {instance_dir}")

    # Check if we can write to the instance directory
    test_file_path = os.path.join(instance_dir, "test_write.txt")
    use_alt_location = False
    alt_db_path = None

    try:
        with open(test_file_path, "w") as f:
            f.write("Testing write access")
        os.remove(test_file_path)
        print(f"Confirmed write access to instance directory: {instance_dir}")

        # Use the instance directory for the database
        db_path = os.path.join(instance_dir, "app.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    except Exception as e:
        print(f"Warning: Cannot write to instance directory: {e}")
        use_alt_location = True

    # If we can't write to the instance directory, use a directory in the user's home folder
    if use_alt_location:
        home_dir = os.path.expanduser("~")
        alt_db_dir = os.path.join(home_dir, ".flask_summarizer")
        print(f"Attempting to use alternative directory: {alt_db_dir}")

        os.makedirs(alt_db_dir, exist_ok=True)
        # Set permissions on alternative directory
        os.chmod(
            alt_db_dir,
            stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH,
        )

        alt_db_path = os.path.join(alt_db_dir, "app.db")
        database_url = f"sqlite:///{alt_db_path}"

        # Update the DATABASE_URL in the environment
        os.environ["DATABASE_URL"] = database_url

        # Verify we can write to this directory
        test_file_path = os.path.join(alt_db_dir, "test_write.txt")
        try:
            with open(test_file_path, "w") as f:
                f.write("Testing write access")
            os.remove(test_file_path)
            print(f"Confirmed write access to alternative directory: {alt_db_dir}")
        except Exception as e:
            print(f"Error: Cannot write to alternative directory either: {e}")
            return False

        # Update .env file with the alternative database location
        env_path = os.path.join(script_dir, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                env_content = f.readlines()

            with open(env_path, "w") as f:
                for line in env_content:
                    if line.startswith("DATABASE_URL="):
                        f.write(f"DATABASE_URL={database_url}\n")
                    else:
                        f.write(line)

            print(f"Updated .env file with new database location: {database_url}")

    print(f"Using database URL: {os.environ.get('DATABASE_URL')}")

    try:
        # Initialize migrations directory
        print("Initializing migrations directory...")
        result = subprocess.run(
            ["python", "-m", "flask", "db", "init"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)

        # Create initial migration
        print("Creating initial migration...")
        result = subprocess.run(
            ["python", "-m", "flask", "db", "migrate", "-m", "Initial migration"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)

        # Apply migration
        print("Applying migration...")
        result = subprocess.run(
            ["python", "-m", "flask", "db", "upgrade"],
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)

        print("Database initialized successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during database initialization: {e}")
        print(f"Error output: {e.stderr}")
        return False


def setup_app():
    """Run the complete setup process"""
    print("=== Starting Application Setup ===")

    # Step 1: Set up NLTK resources
    nltk_success = setup_nltk()

    # Step 2: Set up environment file with absolute database path
    env_success, _ = setup_env_file()

    # Step 3: Initialize database with improved path handling and permissions
    db_success = init_db()

    # Summary
    print("\n=== Setup Summary ===")
    print(f"NLTK Resources: {'✅ Success' if nltk_success else '❌ Failed'}")
    print(f"Environment File: {'✅ Success' if env_success else '❌ Failed'}")
    print(f"Database Initialization: {'✅ Success' if db_success else '❌ Failed'}")

    if nltk_success and env_success and db_success:
        print("\n🎉 Setup completed successfully! Your application is ready to run.")
        print("To start the application, run: python run.py")
    else:
        print("\n⚠️ Setup completed with some issues. Please check the output above.")

        if not db_success:
            print("\nTroubleshooting database issues:")
            print(
                "1. Check that your user has write permissions for the project directory"
            )
            print("2. Try running the application with sudo or as an administrator")
            print("3. Manually create the instance directory and ensure it's writable")
            print("4. Check if any other process is locking the database file")

    return nltk_success and env_success and db_success


if __name__ == "__main__":
    setup_app()
