import logging
from unittest.mock import ANY, MagicMock, patch

import pytest

from fastapi_myauth import email
from fastapi_myauth.config import settings
from fastapi_myauth.models import EmailValidation

# Define minimal required settings for tests
TEST_SETTINGS = {
    "EMAILS_ENABLED": True,
    "SMTP_HOST": "smtp.example.com",
    "SMTP_PORT": 587,
    "SMTP_TLS": True,
    "SMTP_USER": "test_user",
    "SMTP_PASSWORD": "test_password",
    "EMAILS_FROM_NAME": "Test Sender",
    "EMAILS_FROM_EMAIL": "sender@example.com",
    "FRONTEND_URL": "http://test.frontend.com",
    "FRONTEND_HOST": "test.frontend.com",  # Assuming this is distinct from URL
    "SERVER_BOT": "Test Bot",  # Assuming this is needed
    "PROJECT_NAME": "Test Project",
    "EMAIL_TEMPLATES_DIR": "dummy_template_dir",  # Will be replaced by tmp_path
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,  # 60 minutes
}

# --- Fixtures ---


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Modify settings for the duration of a test."""
    # Use a copy to avoid modifying the original TEST_SETTINGS dict
    current_settings = TEST_SETTINGS.copy()
    for key, value in current_settings.items():
        monkeypatch.setattr(settings, key, value, raising=False)
    # Allow individual tests to override specific settings
    return current_settings


@pytest.fixture
def mock_message():
    """Fixture to mock emails.Message and its send method."""
    # Mock the JinjaTemplate class to just return the input string
    # This simplifies testing the content without actual Jinja rendering
    # You could also make it more sophisticated if needed
    with (
        patch("fastapi_myauth.email.JinjaTemplate", side_effect=lambda t: t),
        patch("fastapi_myauth.email.emails.Message") as MockMessageCls,
    ):
        mock_msg_instance = MockMessageCls.return_value
        mock_msg_instance.send = MagicMock(return_value="mock_send_response_ok")
        yield MockMessageCls  # Yield the mocked class


@pytest.fixture
def _tmp_templates(tmp_path, monkeypatch):
    """Create temporary template files and set settings.EMAIL_TEMPLATES_DIR."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    monkeypatch.setattr(settings, "EMAIL_TEMPLATES_DIR", str(template_dir))

    # Create dummy template files used by the functions
    (template_dir / "confirm_email.html").write_text("Confirm {{ link }}")
    (template_dir / "test_email.html").write_text("Test for {{ email }}")
    (template_dir / "magic_login.html").write_text(
        "Magic {{ link }} for {{ valid_minutes }} min"
    )
    (template_dir / "reset_password.html").write_text(
        "Reset {{ link }} for {{ username }} ({{ valid_hours }} hrs)"
    )
    (template_dir / "new_account.html").write_text(
        "New account {{ username }} at {{ link }}"
    )

    return template_dir


# --- Test Cases ---


def test_send_email_disabled(monkeypatch):
    """Test that send_email raises AssertionError if EMAILS_ENABLED is False."""
    monkeypatch.setattr(settings, "EMAILS_ENABLED", False)
    with pytest.raises(
        AssertionError, match="no provided configuration for email variables"
    ):
        email.send_email(
            email_to="test@example.com",
            subject_template="Test Subject",
            html_template="Test HTML",
            environment={},
        )


@pytest.mark.parametrize(
    "smtp_tls, smtp_user, smtp_password, expected_ssl, expected_user, expected_password",
    [
        (True, "user", "pass", True, "user", "pass"),
        (
            False,
            "user",
            "pass",
            None,
            "user",
            "pass",
        ),  # ssl key absent if SMTP_TLS is False
        (True, None, None, True, None, None),  # user/pass absent if None
        (False, None, None, None, None, None),
    ],
)
def test_send_email_smtp_options(
    mock_message,
    monkeypatch,
    caplog,
    smtp_tls,
    smtp_user,
    smtp_password,
    expected_ssl,
    expected_user,
    expected_password,
):
    """Test send_email builds SMTP options correctly based on settings."""
    monkeypatch.setattr(settings, "SMTP_TLS", smtp_tls)
    monkeypatch.setattr(settings, "SMTP_USER", smtp_user)
    monkeypatch.setattr(settings, "SMTP_PASSWORD", smtp_password)

    test_email = "recipient@example.com"
    test_subject = "Subject Template {{ var }}"
    test_html = "Html Template {{ var }}"
    test_env = {"var": "value"}

    expected_smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
    }
    if expected_ssl is not None:
        expected_smtp_options["ssl"] = expected_ssl
    if expected_user is not None:
        expected_smtp_options["user"] = expected_user
    if expected_password is not None:
        expected_smtp_options["password"] = expected_password

    expected_render_env = {
        "var": "value",
        "server_host": settings.FRONTEND_URL,
        "server_name": settings.FRONTEND_HOST,
        "server_bot": settings.SERVER_BOT,
    }

    with caplog.at_level(logging.INFO):
        email.send_email(
            email_to=test_email,
            subject_template=test_subject,
            html_template=test_html,
            environment=test_env,
        )

    # Assert Message was initialized correctly
    # Note: JinjaTemplate mock returns the raw string here
    mock_message.assert_called_once_with(
        subject=test_subject,
        html=test_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    # A Assert send was called correctly
    mock_msg_instance = mock_message.return_value
    mock_msg_instance.send.assert_called_once_with(
        to=test_email,
        render=expected_render_env,
        smtp=expected_smtp_options,
    )

    # Check logs (optional but good)
    assert "send email result: mock_send_response_ok" in caplog.text


def test_send_email_validation_email(mock_message, _tmp_templates):
    """Test sending the email validation email."""
    validation_data = EmailValidation(
        email="validate@example.com",
        subject="Please Confirm Your Email",
        token="abc123xyz",
    )
    expected_link = f"{settings.FRONTEND_URL}?token={validation_data.token}"

    email.send_email_validation_email(data=validation_data)

    expected_subject = f"{settings.PROJECT_NAME} - {validation_data.subject}"
    expected_html = "Confirm {{ link }}"  # Content from dummy file

    # Assert Message was initialized correctly
    mock_message.assert_called_once_with(
        subject=expected_subject,
        html=expected_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    # Assert send was called correctly
    mock_msg_instance = mock_message.return_value
    expected_render_env = {
        "link": expected_link,
        "server_host": settings.FRONTEND_URL,
        "server_name": settings.FRONTEND_HOST,
        "server_bot": settings.SERVER_BOT,
    }
    mock_msg_instance.send.assert_called_once_with(
        to=validation_data.email,
        render=expected_render_env,
        smtp=ANY,  # Check smtp options in the dedicated test
    )


def test_send_test_email(mock_message, _tmp_templates):
    """Test sending the test email."""
    test_email = "test@example.com"
    email.send_test_email(email_to=test_email)

    expected_subject = f"{settings.PROJECT_NAME} - Test email"
    expected_html = "Test for {{ email }}"  # Content from dummy file

    mock_message.assert_called_once_with(
        subject=expected_subject,
        html=expected_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    mock_msg_instance = mock_message.return_value
    expected_render_env = {
        "project_name": settings.PROJECT_NAME,
        "email": test_email,
        "server_host": settings.FRONTEND_URL,
        "server_name": settings.FRONTEND_HOST,
        "server_bot": settings.SERVER_BOT,
    }
    mock_msg_instance.send.assert_called_once_with(
        to=test_email,
        render=expected_render_env,
        smtp=ANY,
    )


def test_send_magic_login_email(mock_message, _tmp_templates):
    """Test sending the magic login email."""
    test_email = "magic@example.com"
    test_token = "magictoken123"
    expected_link = f"{settings.FRONTEND_URL}?magic={test_token}"
    expected_valid_minutes = int(settings.ACCESS_TOKEN_EXPIRE_SECONDS / 60)

    email.send_magic_login_email(email_to=test_email, token=test_token)

    expected_subject = f"Your {settings.PROJECT_NAME} magic login"
    expected_html = "Magic {{ link }} for {{ valid_minutes }} min"  # Dummy content

    mock_message.assert_called_once_with(
        subject=expected_subject,
        html=expected_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    mock_msg_instance = mock_message.return_value
    expected_render_env = {
        "project_name": settings.PROJECT_NAME,
        "valid_minutes": expected_valid_minutes,
        "link": expected_link,
        "server_host": settings.FRONTEND_URL,
        "server_name": settings.FRONTEND_HOST,
        "server_bot": settings.SERVER_BOT,
    }
    mock_msg_instance.send.assert_called_once_with(
        to=test_email,
        render=expected_render_env,
        smtp=ANY,
    )


def test_send_reset_password_email(mock_message, _tmp_templates):
    """Test sending the reset password email."""
    test_email = "reset@example.com"  # The actual recipient
    username_for_msg = "reset_user"  # The username mentioned in the email
    test_token = "resettoken456"
    expected_link = f"{settings.FRONTEND_URL}/reset-password?token={test_token}"
    expected_valid_hours = int(
        settings.ACCESS_TOKEN_EXPIRE_SECONDS / 60
    )  # Note: original code uses /60 for 'hours'

    email.send_reset_password_email(
        email_to=test_email, email=username_for_msg, token=test_token
    )

    expected_subject = (
        f"{settings.PROJECT_NAME} - Password recovery for user {username_for_msg}"
    )
    expected_html = (
        "Reset {{ link }} for {{ username }} ({{ valid_hours }} hrs)"  # Dummy content
    )

    mock_message.assert_called_once_with(
        subject=expected_subject,
        html=expected_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    mock_msg_instance = mock_message.return_value
    expected_render_env = {
        "project_name": settings.PROJECT_NAME,
        "username": username_for_msg,
        "email": test_email,
        "valid_hours": expected_valid_hours,
        "link": expected_link,
        "server_host": settings.FRONTEND_URL,
        "server_name": settings.FRONTEND_HOST,
        "server_bot": settings.SERVER_BOT,
    }
    mock_msg_instance.send.assert_called_once_with(
        to=test_email,
        render=expected_render_env,
        smtp=ANY,
    )


def test_send_new_account_email(mock_message, _tmp_templates):
    """Test sending the new account notification email."""
    test_email = "newuser@example.com"
    test_username = "new_user_xyz"
    expected_link = settings.FRONTEND_URL

    email.send_new_account_email(email_to=test_email, username=test_username)

    expected_subject = f"{settings.PROJECT_NAME} - New account for user {test_username}"
    expected_html = "New account {{ username }} at {{ link }}"  # Dummy content

    mock_message.assert_called_once_with(
        subject=expected_subject,
        html=expected_html,
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    mock_msg_instance = mock_message.return_value
    expected_render_env = {
        "project_name": settings.PROJECT_NAME,
        "username": test_username,
        "email": test_email,
        "link": expected_link,
        "server_host": settings.FRONTEND_URL,
        "server_name": settings.FRONTEND_HOST,
        "server_bot": settings.SERVER_BOT,
    }
    mock_msg_instance.send.assert_called_once_with(
        to=test_email,
        render=expected_render_env,
        smtp=ANY,
    )
