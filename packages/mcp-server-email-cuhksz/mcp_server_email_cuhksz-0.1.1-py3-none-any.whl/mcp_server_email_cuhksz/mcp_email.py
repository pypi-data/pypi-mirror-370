import argparse
import asyncio
import os
import json
import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union

from fastmcp import FastMCP
from mcp import McpError
from mcp.types import (ErrorData, TextContent, INVALID_PARAMS, INTERNAL_ERROR)

from pydantic import BaseModel, Field
from dotenv import load_dotenv

logger = logging.getLogger('mcp_email_server')
logging.basicConfig(level=logging.INFO)
logger.info("Starting MCP Email Server")

load_dotenv()

# Get the directory where the service is started
server_dir = os.path.dirname(os.path.abspath(__file__))

def initialization_email_config():
    with open(os.path.join(server_dir, "email.json"), "r", encoding="UTF-8") as file:
        return json.load(file)

email_config = initialization_email_config()

class EmailMessage(BaseModel):
    receiver: list[str] = Field(description="The list of recipient email addresses, supports multiple recipients")
    body: str = Field(description="The main content of the email")
    subject: str = Field(description="The subject line of the email")
    attachments: Union[list[str], str] = Field(default=[], description="Email attachments, just need to get the file name of the attachment")

def get_smtp_info() -> tuple[str, int] | tuple[None, None]:
    """Get the SMTP server address and port from the configuration based on the sender's email domain name.

    Returns:
        tuple[str, int] | tuple[None, None]: Returns the matching SMTP server address and port; if not found, returns (None, None).
    """
    sender = os.getenv("EMAIL_USERNAME")
    if not sender:
        raise ValueError("EMAIL_USERNAME environment variable not set.")
    # Extract the domain name part of the sender's email
    try:
        domain = f"@{sender.split('@')[1]}"
    except IndexError:
        raise ValueError("Invalid email format for SENDER.")

    # Traverse the configuration and find the matching domain name
    for config in email_config:
        if config.get("domain") == domain:
            return config.get("server"), config.get("port")

    # No matching configuration found
    return None, None

def attach_file(file_path):
    # Define allowed file types
    ALLOWED_EXTENSIONS = {
        'document': ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf'],
        'archive': ['zip', 'rar', '7z', 'tar', 'gz'],
        'text': ['txt', 'log', 'csv', 'json', 'xml'],
        'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
        'other': ['md']  # Other special formats allowed
    }

    # Flatten the list of allowed extensions
    allowed_extensions = [ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts]

    with open(file_path, 'rb') as f:
        file_data = f.read()
        filename = os.path.basename(file_path)
        ext = filename.lower().split('.')[-1]

        # Check if the file type is allowed
        if ext not in allowed_extensions:
            raise ValueError(f"Unsupported file types: {ext}")

        # Process according to file type
        if ext in ALLOWED_EXTENSIONS['image']:
            attachment = MIMEImage(file_data)
        else:
            # For documents, archives, text, and others, use MIMEApplication
            attachment = MIMEApplication(file_data)
            if ext in ALLOWED_EXTENSIONS['document']:
                attachment.add_header('Content-Type', 'application/octet-stream', name=filename)
            elif ext in ALLOWED_EXTENSIONS['archive']:
                attachment.add_header('Content-Type', 'application/octet-stream', name=filename)
            elif ext in ALLOWED_EXTENSIONS['text']:
                 try:
                    # Try to decode as text, if fails, treat as binary
                    text_content = file_data.decode('utf-8')
                    attachment = MIMEText(text_content, 'plain')
                 except UnicodeDecodeError:
                    pass # Keep as MIMEApplication

        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        return attachment

# --- Main Business Logic ---
def send_email_logic(email_message: EmailMessage):
    """Core logic to send an email. This is a blocking function."""
    sender = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    if not sender or not password:
        raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD environment variables must be set.")

    smtp_server, smtp_port = get_smtp_info()
    if not (smtp_server and smtp_port):
        raise ValueError("Please check that your email address is entered correctly, or it is not a supported email service")

    logger.info(f"Sending email: {email_message.model_dump_json(indent=2)}")
    
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ", ".join(email_message.receiver)
    message["Subject"] = email_message.subject
    message.attach(MIMEText(email_message.body, "plain"))

    attachments = email_message.attachments
    if isinstance(attachments, str):
        try:
            attachments = json.loads(attachments)
        except json.JSONDecodeError:
            raise ValueError("Attachments string is not valid JSON.")

    if attachments:
        attachment_folder = os.getenv("ATTACHMENT_FOLDER")
        for file in attachments:
            absolute_path = os.path.join(attachment_folder, file)
            if os.path.isfile(absolute_path):
                message.attach(attach_file(absolute_path))
            else:
                raise ValueError(f"Attachment not found: {absolute_path}")

    server = None
    try:
        # Manually manage the SMTP connection to handle cleanup errors gracefully.
        smtp_class = smtplib.SMTP_SSL if smtp_port == 465 else smtplib.SMTP
        server = smtp_class(smtp_server, smtp_port, timeout=20)

        if smtp_port != 465:
            server.starttls()

        server.login(sender, password)
        server.send_message(message)

        # If we reach here, the email has been sent successfully.
        return f"Email to {', '.join(email_message.receiver)} sent successfully from {sender}"

    except smtplib.SMTPAuthenticationError:
        raise ValueError("Authentication failed - check username and password in your .env file.")
    except smtplib.SMTPServerDisconnected:
        raise ConnectionError("Server disconnected unexpectedly during operation. Please check credentials.")
    except smtplib.SMTPException as e:
        raise ConnectionError(f"SMTP error occurred: {str(e)}")
    except TimeoutError:
        raise ConnectionError("Connection to the mail server timed out.")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")
    finally:
        # This `finally` block ensures we attempt to close the connection,
        # regardless of what happened in the `try` block.
        if server:
            try:
                # We try to be polite and send a QUIT command.
                server.quit()
            except (smtplib.SMTPException, smtplib.SMTPServerDisconnected):
                # We deliberately ignore exceptions here.
                # The email has already been sent. Some servers (like QQ's)
                # are known to close the connection abruptly after sending,
                # causing `quit()` to fail. This is not a real error in our case.
                logger.info("Ignoring cleanup error during server.quit(), as email was already sent.")
                pass

async def search_attachments_logic(pattern: str, ignore_case: bool = True) -> str:
    """Core logic to search for attachments."""
    attachment_folder = os.getenv("ATTACHMENT_FOLDER")
    if not attachment_folder or not os.path.isdir(attachment_folder):
        raise ValueError(f"Attachment directory not found or not set: {attachment_folder}")

    matches = set()
    search_pattern = pattern.lower() if ignore_case else pattern

    for root, _, files in os.walk(attachment_folder):
        for file in files:
            file_to_check = file.lower() if ignore_case else file
            if search_pattern in file_to_check:
                matches.add(os.path.join(root, file))
    
    if not matches:
        return "No matching files found."
        
    return "\n".join(matches)

# --- MCP Server Setup ---
mcp = FastMCP("mcp-email-server")

@mcp.tool(
    description="Send an email to one or more recipients with a specified subject, body, and optional attachments."
)
async def send_email(
    receiver: list[str] = Field(..., description="A list of recipient email addresses."),
    subject: str = Field(..., description="The subject line of the email."),
    body: str = Field(..., description="The main content/body of the email."),
    attachments: list[str] = Field(default_factory=list, description="A list of file names to attach. The files must be in the pre-configured attachments directory.")
) -> str:
    """
    Sends an email to one or more recipients.

    This tool composes and sends an email with a specified subject, body, and optional attachments. Before sending, it is good practice to confirm the details with the user.
    """
    try:
        email_details = EmailMessage(receiver=receiver, subject=subject, body=body, attachments=attachments)
        # Run the blocking smtplib code in a separate thread to avoid freezing the asyncio event loop.
        result = await asyncio.to_thread(send_email_logic, email_details)
        return result
    except (ValueError, ConnectionError, RuntimeError) as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=str(e)))


@mcp.tool(
    description="Search for files in the pre-configured attachments directory that match a given pattern."
)
async def search_attachments(
    pattern: str = Field(..., description="The text pattern to search for in file names. The search is case-insensitive.")
) -> str:
    """
    Searches for files in the pre-configured attachments directory that match a given pattern.

    This tool is useful for finding specific files or attachments to be included in an email. It returns a list of full paths for all matching files.
    """
    try:
        # We can add a timeout to prevent long-running searches
        search_result = await asyncio.wait_for(search_attachments_logic(pattern=pattern), timeout=10.0)
        return f"Search results for '{pattern}':\n{search_result}"
    except asyncio.TimeoutError:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message="Search operation timed out after 10 seconds."))
    except ValueError as e:
        raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"An unexpected error occurred during search: {e}"))