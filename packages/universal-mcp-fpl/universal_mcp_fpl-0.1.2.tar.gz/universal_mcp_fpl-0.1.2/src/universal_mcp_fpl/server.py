
from universal_mcp.servers import SingleMCPServer
from universal_mcp.stores import EnvironmentStore

from universal_mcp_fpl.app import FplApp

env_store = EnvironmentStore()

app_instance = FplApp()

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()


