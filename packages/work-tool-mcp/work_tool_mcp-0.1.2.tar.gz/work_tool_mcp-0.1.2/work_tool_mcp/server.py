import logging
import os
from typing import Any
from mcp.server.fastmcp import FastMCP

from work_tool_mcp.tools.save_pdf_info import save_pdf_info

# Import exceptions
from work_tool_mcp.exceptions import (
    ValidationError,
    WorkbookError,
    SheetError,
    DataError,
    FormattingError,
    CalculationError,
    PivotError,
    ChartError
)

logger = logging.getLogger(__name__)


# Get project root directory path for log file path.
# When using the stdio transmission method,
# relative paths may cause log files to fail to create
# due to the client's running location and permission issues,
# resulting in the program not being able to run.
# Thus using os.path.join(ROOT_DIR, "work-tool-mcp.log") instead.

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "work-tool-mcp.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # Referring to https://github.com/modelcontextprotocol/python-sdk/issues/409#issuecomment-2816831318
        # The stdio mode server MUST NOT write anything to its stdout that is not a valid MCP message.
        logging.FileHandler(LOG_FILE)
    ],
)
logger = logging.getLogger("work-tool-mcp")
# Initialize FastMCP server
mcp = FastMCP(
    "work-tool-mcp",
    host=os.environ.get("FASTMCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("FASTMCP_PORT", "8017")),
    instructions="Work Tool MCP Server for manipulating work files"
)

def get_file_path(filename: str) -> str:
    """
    Get full path of a file.
    Args:
        filename: The name of the file to get the path of.
    Returns:
        The full path of the file.
    """
    # If filename is already an absolute path, return it
    if os.path.isabs(filename):
        return filename
    
    # Must use absolute path
    raise ValueError(f"Invalid filename: {filename}, must be an absolute path when not in SSE mode")


@mcp.tool()
def get_pdf_info(pdf_filepath: str, output_folder: str) -> str:
    """
    Get information about a PDF file.
    """
    try:
        full_path = get_file_path(pdf_filepath)
        save_pdf_info(full_path, output_folder)
        return "Success"
    except (ValidationError, CalculationError) as e:
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error validating formula: {e}")
        raise

def run_stdio():
    """Run Work Tool MCP server in stdio mode."""
    
    try:
        logger.info("Starting Work Tool MCP server with stdio transport")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    save_pdf_info("/Users/Vint/Desktop/03 点读脚本生成/inputs/01 欲速则不达.pdf", "/Users/Vint/Desktop/Test/")