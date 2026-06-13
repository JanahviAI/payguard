import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from agent import evaluate
from blockchain import BlockchainError, refund_payment, release_payment
from models import Job, db

load_dotenv()
logging.basicConfig(level=logging.INFO)


VALID_STATUSES = {
    "open",
    "submitted",
    "approved",
    "rejected",
    "revision",
    "human_review",
}


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///payguard.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    CORS(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/jobs")
    def create_job():
        payload = request.get_json(silent=True) or {}
        required = ["title", "requirements", "amount_inr", "client_addr", "freelancer_addr"]
        missing = [k for k in required if k not in payload or payload[k] in (None, "")]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        custom_id = payload.get("id")
        job = Job(
            id=int(custom_id) if custom_id else None,
            title=payload["title"],
            requirements=payload["requirements"],
            amount_inr=float(payload["amount_inr"]),
            amount_mon=float(payload.get("amount_mon") or 0),
            client_addr=payload["client_addr"],
            freelancer_addr=payload["freelancer_addr"],
            status="open",
            tx_hash=payload.get("tx_hash"),
        )
        db.session.add(job)
        db.session.commit()
        return jsonify(job.to_dict()), 201

    @app.get("/api/jobs")
    def list_jobs():
        status = request.args.get("status")
        query = Job.query
        if status:
            query = query.filter_by(status=status)
        jobs = query.order_by(Job.created_at.desc()).all()
        return jsonify([job.to_dict() for job in jobs])

    @app.post("/api/jobs/<int:job_id>/submit")
    def submit_work(job_id):
        job = Job.query.get_or_404(job_id)
        payload = request.get_json(silent=True) or {}
        submission = (payload.get("submission") or "").strip()
        if not submission:
            return jsonify({"error": "Submission is required"}), 400

        job.submission = submission
        job.status = "submitted"

        try:
            verdict = evaluate(job.requirements, submission)
            job.ai_verdict = verdict["verdict"]
            job.ai_reasoning = verdict["reasoning"]
            job.ai_confidence = float(verdict["confidence"])

            if job.ai_verdict == "approved" and job.ai_confidence >= 0.7:
                job.status = "approved"
                job.tx_hash = release_payment(job.id)
            elif job.ai_verdict == "rejected" and job.ai_confidence >= 0.7:
                job.status = "rejected"
                job.tx_hash = refund_payment(job.id)
            else:
                job.status = "human_review"

            db.session.commit()
            return jsonify(job.to_dict())
        except (ValueError, KeyError):
            db.session.rollback()
            app.logger.exception("AI evaluation failed")
            return jsonify({"error": "AI evaluation failed"}), 502
        except BlockchainError:
            db.session.rollback()
            app.logger.exception("Blockchain transaction failed")
            return jsonify({"error": "Blockchain transaction failed"}), 502

    @app.post("/api/jobs/<int:job_id>/decide")
    def decide(job_id):
        job = Job.query.get_or_404(job_id)
        payload = request.get_json(silent=True) or {}
        decision = str(payload.get("decision", "")).strip().lower()
        if decision not in {"approve", "reject"}:
            return jsonify({"error": "Decision must be approve or reject"}), 400

        try:
            if decision == "approve":
                job.status = "approved"
                job.tx_hash = release_payment(job.id)
            else:
                job.status = "rejected"
                job.tx_hash = refund_payment(job.id)

            db.session.commit()
            return jsonify(job.to_dict())
        except BlockchainError:
            db.session.rollback()
            app.logger.exception("Blockchain transaction failed")
            return jsonify({"error": "Blockchain transaction failed"}), 502

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
