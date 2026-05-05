import html
import smtplib
from email.message import EmailMessage


def _clean(value, fallback="Not provided"):
    text = str(value or "").strip()
    return text if text else fallback


def _smtp_password(password, mail_server):
    password = _clean(password, "")
    if mail_server.lower() == "smtp.gmail.com":
        return password.replace(" ", "")
    return password


def _task_email_text(task):
    return "\n".join(
        [
            f"Hello {_clean(task.assignedTo, 'there')},",
            "",
            "A new task has been assigned to you.",
            "",
            f"Title: {_clean(task.title)}",
            f"Description: {_clean(task.description)}",
            f"Priority: {_clean(task.priority)}",
            f"Deadline: {_clean(task.deadline)}",
            f"Assigned by: {_clean(task.assignedBy)}",
            "",
            "Please check your ISMS dashboard for updates.",
        ]
    )


def _task_email_html(task):
    rows = [
        ("Title", task.title),
        ("Description", task.description),
        ("Priority", task.priority),
        ("Deadline", task.deadline),
        ("Assigned by", task.assignedBy),
    ]
    row_markup = "".join(
        "<tr>"
        f"<td style='padding:8px 12px;font-weight:700;border-bottom:1px solid #e5e7eb;'>{html.escape(label)}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e5e7eb;'>{html.escape(_clean(value))}</td>"
        "</tr>"
        for label, value in rows
    )
    assigned_to = html.escape(_clean(task.assignedTo, "there"))
    return f"""
    <div style="font-family:Arial,sans-serif;color:#0f172a;line-height:1.5;">
      <p>Hello {assigned_to},</p>
      <p>A new task has been assigned to you.</p>
      <table style="border-collapse:collapse;width:100%;max-width:640px;border:1px solid #e5e7eb;">
        {row_markup}
      </table>
      <p>Please check your ISMS dashboard for updates.</p>
    </div>
    """


def send_task_assignment_email(task, app_config):
    recipient = _clean(task.email, "")
    mail_server = _clean(app_config.get("MAIL_SERVER"), "")
    sender = _clean(app_config.get("MAIL_DEFAULT_SENDER"), "")

    if not recipient:
        return False, "No recipient email provided."
    if not mail_server or not sender:
        return False, "SMTP mail settings are not configured."

    message = EmailMessage()
    message["Subject"] = f"New Task Assigned: {_clean(task.title)}"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(_task_email_text(task))
    message.add_alternative(_task_email_html(task), subtype="html")

    port = int(app_config.get("MAIL_PORT", 587))
    username = _clean(app_config.get("MAIL_USERNAME"), "")
    password = _smtp_password(app_config.get("MAIL_PASSWORD"), mail_server)
    use_ssl = bool(app_config.get("MAIL_USE_SSL", False))
    use_tls = bool(app_config.get("MAIL_USE_TLS", True))

    smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with smtp_class(mail_server, port, timeout=15) as smtp:
        if use_tls and not use_ssl:
            smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)

    return True, "Task assignment email sent."
