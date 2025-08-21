# run_app.py (at root level)
from src.mcp_kyvos_server import main
import os

if __name__ == "__main__":
    transport = os.environ.get("TRANSPORT")
    port = os.environ.get("PORT")  
    main(args=["--transport", "sse", "--port", "8000"])