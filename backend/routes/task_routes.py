from flask import Blueprint, request, jsonify, current_app, session
from models import db, Task
from auth_middleware import login_required, role_required
import datetime
from types import SimpleNamespace
from threading import Thread
from utils.datetime_utils import now_ist_iso
from utils.email_utils import send_task_assignment_email

task_bp = Blueprint('task', __name__)


def _send_assignment_email_async(task_payload, mail_config):
    task_snapshot = SimpleNamespace(
        title=task_payload.get("title"),
        description=task_payload.get("description"),
        priority=task_payload.get("priority"),
        deadline=task_payload.get("deadline"),
        assignedTo=task_payload.get("assignedTo"),
        assignedBy=task_payload.get("assignedBy"),
        email=task_payload.get("email"),
    )
    try:
        print(f"Sending task assignment email to {task_snapshot.email or 'missing recipient'}")
        email_sent, email_message = send_task_assignment_email(task_snapshot, mail_config)
        print(f"Task assignment email: {email_message} sent={email_sent}")
    except Exception as email_error:
        print(f"Error sending task assignment email: {email_error}")

@task_bp.route("/tasks", methods=["GET", "POST"])
@login_required
def handle_tasks():
    if request.method == "GET":
        try:
            tasks = Task.query.order_by(Task.id.desc()).all()
            return jsonify([t.to_dict() for t in tasks])
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return jsonify({"error": str(e)}), 500

    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"error": "Request body required"}), 400
            
        new_task = Task(
            title=data.get("title"),
            domain=data.get("domain"),
            assignedTo=data.get("assignedTo"),
            email=data.get("internEmail") or data.get("email"),
            userId=data.get("userId"),
            deadline=data.get("deadline"),
            priority=data.get("priority"),
            description=data.get("description"),
            status=data.get("status", "Pending"),
            createdAt=data.get("createdAt", now_ist_iso()),
            assignedBy=data.get("assignedBy")
        )
        try:
            db.session.add(new_task)
            db.session.commit()
            task_payload = new_task.to_dict()
            mail_config = {
                key: current_app.config.get(key)
                for key in (
                    "MAIL_SERVER",
                    "MAIL_PORT",
                    "MAIL_USERNAME",
                    "MAIL_PASSWORD",
                    "MAIL_USE_TLS",
                    "MAIL_USE_SSL",
                    "MAIL_DEFAULT_SENDER",
                )
            }
            Thread(
                target=_send_assignment_email_async,
                args=(task_payload.copy(), mail_config),
                daemon=True,
            ).start()

            task_payload["emailNotification"] = {
                "sent": None,
                "message": "Task saved. Assignment email is being sent in the background.",
            try:
                email_sent, email_message = send_task_assignment_email(new_task, current_app.config)
            except Exception as email_error:
                email_sent = False
                email_message = "Task saved, but assignment email could not be sent."
                print(f"Error sending task assignment email: {email_error}")

            task_payload["emailNotification"] = {
                "sent": email_sent,
                "message": email_message,
            }
            return jsonify(task_payload), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error creating task: {e}")
            return jsonify({"error": str(e)}), 500

@task_bp.route("/tasks/<int:task_id>", methods=["PUT", "DELETE"])
@login_required
def handle_task_item(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if request.method == "PUT":
        data = request.json
        try:
            if "title" in data: task.title = data["title"]
            if "status" in data: task.status = data["status"]
            if "isChecked" in data: task.isChecked = data["isChecked"]
            if "priority" in data: task.priority = data["priority"]
            if "deadline" in data: task.deadline = data["deadline"]
            if "internEmail" in data:
                task.email = data["internEmail"]
            elif "email" in data:
                task.email = data["email"]
            db.session.commit()
            return jsonify(task.to_dict())
        except Exception:
            db.session.rollback()
            return jsonify({"error": "Failed to update task."}), 500

    if request.method == "DELETE":
        # Restrict deletion to admins
        @role_required("superadmin", "admin", "mentor")
        def delete_task():
            try:
                db.session.delete(task)
                db.session.commit()
                return jsonify({"success": True, "message": "Task deleted"})
            except Exception:
                db.session.rollback()
                return jsonify({"error": "Failed to delete task."}), 500
        return delete_task()
