import asyncio
import sys

from dbt_mcp.config.config import load_config
from dbt_mcp.mcp.server import create_dbt_mcp


def main() -> None:
    if "--help" in sys.argv or "-h" in sys.argv:
        print("dbt-mcp - Enhanced dbt Model Context Protocol Server with Lightdash Integration")
        print("\nUsage: dbt-mcp")
        print("\nThis is an MCP server that runs via stdio and should be used with an MCP client like LibreChat.")
        print("\nEnvironment Variables:")
        print("  LIGHTDASH_API_URL        - Lightdash API endpoint")
        print("  LIGHTDASH_API_KEY        - Your Lightdash API key")
        print("  LIGHTDASH_PROJECT_ID     - Lightdash project UUID")
        print("  LIGHTDASH_DEFAULT_SPACE_ID - Default space for charts")
        print("  DISABLE_LIGHTDASH        - Set to 'true' to disable Lightdash features")
        sys.exit(0)
    
    config = load_config()
    asyncio.run(create_dbt_mcp(config)).run()


if __name__ == "__main__":
    main()
