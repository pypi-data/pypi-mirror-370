import argparse
import os
import sys
import logging
import dotenv
from .mcp_email import mcp

def main():
    """Main entry point for the package."""
    # Load environment variables from .env file first.
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Start MCP Email Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3002, help="Port to listen on (default: 3002)")
    parser.add_argument("--transport", type=str, default="stdio", help="Transport type (default: stdio)")
    
    # Set default values from environment variables. CLI arguments will override them.
    parser.add_argument("--username", type=str, default=os.getenv("EMAIL_USERNAME"), 
                        help="Username for Email. Overrides EMAIL_USERNAME in .env file.")
    parser.add_argument("--password", type=str, default=os.getenv("EMAIL_PASSWORD"), 
                        help="Password for Email. Overrides EMAIL_PASSWORD in .env file.")
    parser.add_argument("--dir", type=str, default=os.getenv("ATTACHMENT_FOLDER"),
                        help="Directory for attachments. Overrides ATTACHMENT_FOLDER in .env file.")
    
    args = parser.parse_args()

    # Validate that credentials and directory are set.
    if not args.username or not args.password:
        print("Error: EMAIL_USERNAME and EMAIL_PASSWORD must be provided.", file=sys.stderr)
        print("You can set them in a .env file or provide them as command-line arguments (--username, --password).", file=sys.stderr)
        sys.exit(1)

    # Set the final resolved values back into the environment for the tools to use
    os.environ['EMAIL_USERNAME'] = args.username
    os.environ['EMAIL_PASSWORD'] = args.password
    os.environ['ATTACHMENT_FOLDER'] = os.path.abspath(args.dir)

    logger = logging.getLogger('mcp_email_server')
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting MCP Email Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport != 'stdio':
        logger.info(f"Host: {args.host}")
        logger.info(f"Port: {args.port}")
    logger.info(f"Attachment Directory: {os.environ['ATTACHMENT_FOLDER']}")
    logger.info(f"Email Username: {os.environ['EMAIL_USERNAME']}")

    # Run the server
    if args.transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
