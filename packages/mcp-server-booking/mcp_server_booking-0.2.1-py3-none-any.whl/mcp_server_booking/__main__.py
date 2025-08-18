import argparse
import os
import sys
import dotenv
from .booking import mcp

def main():
    # Load environment variables from .env file first.
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(description="Start MCP Booking server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=3001, help="Port to listen on (default: 3001)")
    parser.add_argument("--transport", type=str, default="stdio", help="Transport type (default: stdio)")
    
    # Set default values from environment variables. CLI arguments will override them.
    parser.add_argument("--username", type=str, default=os.getenv("BOOKING_USERNAME"), 
                        help="Username for Booking system. Overrides BOOKING_USERNAME in .env file.")
    parser.add_argument("--password", type=str, default=os.getenv("BOOKING_PASSWORD"), 
                        help="Password for Booking system. Overrides BOOKING_PASSWORD in .env file.")
    
    args = parser.parse_args()

    # Validate that credentials are set.
    if not args.username or not args.password:
        print("Error: BOOKING_USERNAME and BOOKING_PASSWORD must be provided.", file=sys.stderr)
        print("You can set them in a .env file or provide them as command-line arguments (--username, --password).", file=sys.stderr)
        sys.exit(1)

    # Set the final credentials back into the environment.
    os.environ['BOOKING_USERNAME'] = args.username
    os.environ['BOOKING_PASSWORD'] = args.password

    print("Starting Booking-MCP server...")
    if args.transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)

if __name__ == "__main__":
    main()