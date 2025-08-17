
from unittest import result
from universal_mcp.tools import ToolManager
from universal_mcp_fpl.app import FplApp
import anyio
from pprint import pprint

app_instance = FplApp(integration=None)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.get_player_information)
tool_manager.add_tool(app_instance.search_fpl_players)
tool_manager.add_tool(app_instance.get_gameweek_status)
tool_manager.add_tool(app_instance.analyze_players)
tool_manager.add_tool(app_instance.compare_players)
tool_manager.add_tool(app_instance.analyze_player_fixtures)
tool_manager.add_tool(app_instance.analyze_fixtures)
tool_manager.add_tool(app_instance.get_blank_gameweeks)
tool_manager.add_tool(app_instance.get_double_gameweeks)
tool_manager.add_tool(app_instance.authenticate)    
tool_manager.add_tool(app_instance.get_league_standings)
tool_manager.add_tool(app_instance.get_league_analytics)

async def main():
    # Get a specific tool by name
    tool = tool_manager.get_tool("get_player_information")
    tool = tool_manager.get_tool("search_fpl_players")
    tool = tool_manager.get_tool("get_gameweek_status")
    tool = tool_manager.get_tool("analyze_players")
    tool = tool_manager.get_tool("compare_players")
    tool = tool_manager.get_tool("analyze_player_fixtures")
    tool = tool_manager.get_tool("analyze_fixtures")
    tool = tool_manager.get_tool("get_blank_gameweeks")
    tool = tool_manager.get_tool("get_double_gameweeks")
    tool = tool_manager.get_tool("authenticate")
    tool = tool_manager.get_tool("get_league_standings")
    tool = tool_manager.get_tool("get_league_analytics")
    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    

   
    # result=await tool_manager.call_tool(name="get_player_information",arguments={"player_name":"mohamed salah"})
    # result=await tool_manager.call_tool(name="search_fpl_players",arguments={"query":"mohamed salah"})
    # result=await tool_manager.call_tool(name="get_gameweek_status",arguments={})
    # result=await tool_manager.call_tool(name="analyze_players",arguments={"position":"midfielders","team":"liverpool"})
    # result=await tool_manager.call_tool(name="compare_players",arguments={"player_names":["mohamed salah","erling haaland"]})
    # result=await tool_manager.call_tool(name="analyze_player_fixtures",arguments={"player_name":"mohamed salah","num_fixtures":5})
    # result=await tool_manager.call_tool(name="analyze_fixtures",arguments={"entity_type":"team","entity_name":"liverpool","num_gameweeks":5})
    # result=await tool_manager.call_tool(name="get_blank_gameweeks",arguments={"num_weeks":5})
    # result=await tool_manager.call_tool(name="get_double_gameweeks",arguments={"num_weeks":5})
    # result=await tool_manager.call_tool(name="authenticate",arguments={"email":"rshvraj36@gmail.com","password":"Agentr2025@","team_id":"9709022"})
    # result=await tool_manager.call_tool(name="get_league_standings",arguments={"league_id":14})
    result=await tool_manager.call_tool(name="get_league_analytics",arguments={"league_id":14})
    print(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)