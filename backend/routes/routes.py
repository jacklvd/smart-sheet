from flask import Blueprint, request, jsonify, current_app
from app import db
from datetime import datetime, timedelta
from models.summary import Summary, MarkdownConversion
from services.summarizer import TextSummarizer
from services.markdown_converter import MarkdownConverter
from utils.text_processor import count_words
import traceback

api_bp = Blueprint("api", __name__)
summarizer = TextSummarizer()
markdown_converter = MarkdownConverter()


@api_bp.route("/summarize", methods=["POST", "OPTIONS"])
def summarize_text():
    """API endpoint to summarize text with improved error handling and data expiration"""
    # Handle preflight OPTIONS request for CORS
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data provided"}), 400

        if "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data.get("text", "")
        max_length = data.get("max_length")
        summary_type = data.get("type", "concise")

        if not text or not text.strip():
            return jsonify({"error": "Empty text provided"}), 400

        # Validate max_length if provided
        if max_length is not None:
            try:
                max_length = int(max_length)
                if max_length <= 0:
                    return (
                        jsonify({"error": "max_length must be a positive integer"}),
                        400,
                    )
            except (ValueError, TypeError):
                return jsonify({"error": "max_length must be a valid integer"}), 400

        # Validate summary_type
        if summary_type not in ["concise", "detailed"]:
            return (
                jsonify({"error": "summary_type must be 'concise' or 'detailed'"}),
                400,
            )

        # Generate summary with better error handling
        try:
            result = summarizer.summarize(text, max_length, summary_type)

            if not result or "summary" not in result:
                current_app.logger.error("Summarizer returned invalid result")
                return jsonify({"error": "Failed to generate summary"}), 500

        except Exception as e:
            current_app.logger.error(f"Summarization error: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({"error": f"Error generating summary: {str(e)}"}), 500

        # Store in database with error handling
        try:
            # Set expiration time based on config
            ttl = current_app.config.get("DATA_TTL", timedelta(hours=1))
            expires_at = datetime.utcnow() + ttl

            # Create summary object
            summary = Summary(
                original_text=text[:5000],  # Limit size to prevent DB issues
                summary_text=result["summary"][
                    :5000
                ],  # Limit size to prevent DB issues
                original_length=result.get("original_length", count_words(text)),
                summary_length=result.get(
                    "summary_length", count_words(result["summary"])
                ),
                summary_type=summary_type,
            )

            # Set expiration
            summary.expires_at = expires_at

            # Add and commit with error handling
            db.session.add(summary)
            db.session.commit()

            # Return response
            return (
                jsonify(
                    {
                        "summary": result["summary"],
                        "original_length": result["original_length"],
                        "summary_length": result["summary_length"],
                        "id": summary.id,
                    }
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            current_app.logger.error(traceback.format_exc())

            # Still return the summary even if DB storage failed
            return (
                jsonify(
                    {
                        "summary": result["summary"],
                        "original_length": result["original_length"],
                        "summary_length": result["summary_length"],
                        "warning": "Summary generated but not saved to database",
                    }
                ),
                200,
            )

    except Exception as e:
        current_app.logger.error(f"Unexpected error in summarize_text: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@api_bp.route("/markdown", methods=["POST", "OPTIONS"])
def convert_markdown():
    """API endpoint to convert text to/from markdown with data expiration"""
    # Handle preflight OPTIONS request for CORS
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON data provided"}), 400

        if "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data.get("text", "")
        mode = data.get("mode", "to_markdown")

        if not text.strip():
            return jsonify({"error": "Empty text provided"}), 400

        if mode not in ["to_markdown", "to_text"]:
            return jsonify({"error": "Invalid conversion mode"}), 400

        # Convert text with error handling
        try:
            result = markdown_converter.convert(text, mode)
        except Exception as e:
            current_app.logger.error(f"Markdown conversion error: {str(e)}")
            return jsonify({"error": f"Error converting text: {str(e)}"}), 500

        # Store in database with error handling
        try:
            # Set expiration time based on config
            ttl = current_app.config.get("DATA_TTL", timedelta(hours=1))
            expires_at = datetime.utcnow() + ttl

            conversion = MarkdownConversion(
                original_text=text[:5000],  # Limit size to prevent DB issues
                converted_text=result[:5000],  # Limit size to prevent DB issues
                conversion_type=mode,
            )

            # Set expiration
            conversion.expires_at = expires_at

            db.session.add(conversion)
            db.session.commit()

            return jsonify({"result": result}), 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")

            # Still return the conversion result even if DB storage failed
            return (
                jsonify(
                    {
                        "result": result,
                        "warning": "Conversion completed but not saved to database",
                    }
                ),
                200,
            )

    except Exception as e:
        current_app.logger.error(f"Unexpected error in convert_markdown: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint with DB stats"""
    try:
        # Check database connection
        db.session.execute("SELECT 1")
        db_status = "connected"

        # Get record counts
        summary_count = db.session.query(Summary).count()
        conversion_count = db.session.query(MarkdownConversion).count()

        # Get cleanup settings
        cleanup_interval = current_app.config.get("DATA_CLEANUP_INTERVAL", 3600)
        max_records = current_app.config.get("MAX_RECORDS_PER_TABLE", 1000)
        ttl_hours = (
            current_app.config.get("DATA_TTL", timedelta(hours=1)).total_seconds()
            / 3600
        )

        return (
            jsonify(
                {
                    "status": "healthy",
                    "database": db_status,
                    "api_version": "1.0.0",
                    "stats": {
                        "summary_records": summary_count,
                        "conversion_records": conversion_count,
                        "cleanup_interval_seconds": cleanup_interval,
                        "max_records_per_table": max_records,
                        "data_ttl_hours": ttl_hours,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        db_status = f"error: {str(e)}"
        return jsonify({"status": "degraded", "database": db_status}), 500
