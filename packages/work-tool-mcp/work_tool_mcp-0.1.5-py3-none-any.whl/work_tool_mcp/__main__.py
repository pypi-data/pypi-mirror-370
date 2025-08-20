import typer

from .server import run_stdio


app = typer.Typer(name="work-tool-mcp", help="Work tool MCP server")

@app.command()
def stdio():
    """Start Work Tool MCP Server in stdio mode"""
    try:
        run_stdio()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Service stopped.")


if __name__ == "__main__":
    app()
