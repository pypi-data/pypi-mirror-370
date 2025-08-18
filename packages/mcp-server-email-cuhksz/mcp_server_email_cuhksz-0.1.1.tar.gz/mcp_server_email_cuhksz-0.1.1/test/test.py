import asyncio
import logging
from fastmcp import Client

# Server address, pointing to the MCP service running in Docker.
# The URL includes /sse to hint the client to use SSETransport.
MCP_SERVER_URL = "http://localhost:3002/sse"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    """
    Connects to the MCP email server and sends a test email with an attachment.
    """
    logging.info(f"🚀 Starting test, connecting to: {MCP_SERVER_URL}")

    try:
        # Initialize the FastMCP client
        client = Client(MCP_SERVER_URL)
        
        async with client:
            tools = await client.list_tools()
            if not tools:
                logging.error("❌ No tools found, aborting test.")
                return

            tool_names = [tool.name for tool in tools]
            logging.info(f"\n✅ Connected successfully! Found {len(tools)} available tools: {tool_names}")
            
            # Details for the email to be sent
            email_details = {
                "receiver": ["123090296@link.cuhk.edu.cn"],
                "subject": "MCP Test Email via FastMCP Client",
                "body": "This is a test email sent using the FastMCP client to a service running in a Docker container.",
                "attachments": ["test_attachment.txt"]
            }

            tool_name = "send_email"
            if tool_name not in tool_names:
                logging.error(f"Tool '{tool_name}' not found on the server.")
                return

            logging.info(f"\n--- Calling tool: {tool_name} ---")
            logging.info(f"   Parameters: {email_details}")
            
            try:
                # Call the 'send_email' tool with the prepared parameters
                result = await client.call_tool(tool_name, email_details, timeout=60.0)
                
                # The result from fastmcp is a list of content blocks
                result_text = ""
                if isinstance(result, list):
                    for content_block in result:
                        if hasattr(content_block, 'text'):
                            result_text += content_block.text
                else:
                    # Fallback for older versions or different return types
                    result_text = str(result)
                
                logging.info(f"\n✅ Tool '{tool_name}' called successfully! Server response:\n---\n{result_text}\n---")

            except Exception as e:
                logging.error(f"⚠️ An error occurred while calling tool '{tool_name}': {e}\n")

            # --- Test search_attachments tool ---
            tool_name = "search_attachments"
            search_pattern = "test_attachment.txt"
            
            if tool_name not in tool_names:
                logging.error(f"Tool '{tool_name}' not found on the server.")
                return

            logging.info(f"\n--- Calling tool: {tool_name} ---")
            logging.info(f"   Parameters: {{'pattern': '{search_pattern}'}}")

            try:
                result = await client.call_tool(tool_name, {"pattern": search_pattern}, timeout=10.0)
                
                result_text = ""
                if isinstance(result, list):
                    for content_block in result:
                        if hasattr(content_block, 'text'):
                            result_text += content_block.text
                else:
                    result_text = str(result)
                
                logging.info(f"\n✅ Tool '{tool_name}' called successfully! Server response:\n---\n{result_text}\n---")
                
                # Verify that the attachment was found
                if search_pattern in result_text and "/app/attachments/" in result_text:
                    logging.info(f"✅ Verification successful: Found '{search_pattern}' in search results.")
                else:
                    logging.error(f"❌ Verification failed: Did not find '{search_pattern}' in search results.")

            except Exception as e:
                logging.error(f"⚠️ An error occurred while calling tool '{tool_name}': {e}\n")

    except Exception as e:
        logging.error(f"❌ Test failed. Could not connect to the service: {e}")
        logging.error("\nPlease ensure:")
        logging.error("1. The Docker container is running ('docker-compose up --build').")
        logging.error(f"2. Port 3002 is correctly mapped and the server is listening.")
        logging.error("3. The .env file is correctly configured with email credentials.")
        logging.error("4. Check container logs for errors ('docker-compose logs -f mcp-email-server').")

if __name__ == "__main__":
    asyncio.run(main())
