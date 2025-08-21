"""
gcp_notifier: Notification microservice for Email and Google Chat.
"""
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
__version__ = "0.1.3"

def get_secret(project_id: str, secret_id: str, version_id: str = "latest") -> str:
    """
    Retrieve a secret from Google Secret Manager.

    Args:
        project_id: GCP project ID
        secret_id: Secret ID in Secret Manager
        version_id: Version of the secret to retrieve

    Returns:
        The secret value as a string
    """
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    secret_value = response.payload.data.decode("UTF-8")
    return secret_value

# Detect GCP project and fetch secrets
try:
    import google.auth
    credentials, project_id = google.auth.default()

    def _fetch_secret_or_none(secret_id: str) -> str:
        if not project_id:
            return None
        try:
            return get_secret(project_id, secret_id)
        except Exception as e:
            print(f"Failed to fetch secret '{secret_id}': {e}")
            return None

    GCHAT_WEBHOOK_URL = _fetch_secret_or_none("GCHAT_WEBHOOK_URL")
    EMAIL_SENDER = _fetch_secret_or_none("EMAIL_SENDER")
    EMAIL_PASSWORD = _fetch_secret_or_none("EMAIL_PASSWORD")
    EMAIL_RECIPIENTS = _fetch_secret_or_none("EMAIL_RECIPIENTS")
except Exception:
    credentials, project_id = None, None
    GCHAT_WEBHOOK_URL = EMAIL_SENDER = EMAIL_PASSWORD = EMAIL_RECIPIENTS = None

def _send_email(subject: str, message: str) -> None:
    """Send notification email using configured SMTP credentials."""
    try:
        import smtplib
        from email.message import EmailMessage

        if not EMAIL_RECIPIENTS:
            print("ERROR: EMAIL_RECIPIENTS is not set. Please add the 'EMAIL_RECIPIENTS' secret (comma-separated list of recipient email addresses) to Google Secret Manager in your GCP project.")
            return
        recipients = [email.strip() for email in EMAIL_RECIPIENTS.split(",") if email.strip()]
        if not recipients:
            print("ERROR: EMAIL_RECIPIENTS is empty. Please check the 'EMAIL_RECIPIENTS' secret in Google Secret Manager.")
            return
        if not EMAIL_SENDER:
            print("ERROR: EMAIL_SENDER is not set. Please add the 'EMAIL_SENDER' secret (sender email address for Email) to Google Secret Manager in your GCP project.")
            return
        if not EMAIL_PASSWORD:
            print("ERROR: EMAIL_PASSWORD is not set. Please add the 'EMAIL_PASSWORD' secret (password or app password for sender) to Google Secret Manager in your GCP project.")
            return

        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.set_content(message)

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def _send_gchat_alert(message: str) -> None:
    """Send a notification to Google Chat via Webhook."""
    try:
        import requests
        if not GCHAT_WEBHOOK_URL:
            print("ERROR: GCHAT_WEBHOOK_URL is not set. Please add the 'GCHAT_WEBHOOK_URL' secret (Google Chat webhook URL) to Google Secret Manager in your GCP project.")
            return
        payload = {"text": message}
        headers = {"Content-Type": "application/json"}
        response = requests.post(GCHAT_WEBHOOK_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print("GChat alert sent successfully!")
        else:
            print(f"Failed to send GChat alert: {response.text}")
    except Exception as e:
        print(f"Failed to send GChat alert: {e}")

def notify(subject: str, body: str, channels: list[str] = ["email", "gchat"]) -> None:
    """
    Send a notification via email, Google Chat, or both.

    Args:
        subject: The subject for email (ignored for gchat)
        body: The message body
        channels: List of channels to send to ("email", "gchat")
    """
    if not channels:
        print("No channels specified. Nothing to send.")
        return
    if "email" in channels:
        _send_email(subject, body)
    if "gchat" in channels:
        _send_gchat_alert(body)

# Expose functions for import
def notify_on_failure(retry_state) -> None:
    """
    Tenacity retry_error_callback to send notification on final failure.
    Usage: @retry(..., retry_error_callback=notify_on_failure)
    """
    fn_name = getattr(retry_state.fn, "__name__", str(retry_state.fn))
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    msg = f"Function '{fn_name}' failed after retries. Exception: {exception}"
    notify(subject=f"Failure in {fn_name}", body=msg, channels=["email", "gchat"])

__all__ = ["notify", "project_id", "notify_on_failure"]
