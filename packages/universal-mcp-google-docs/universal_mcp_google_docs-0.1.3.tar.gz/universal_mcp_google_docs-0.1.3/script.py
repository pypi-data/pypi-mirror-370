from universal_mcp.integrations import AgentRIntegration
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp_google_docs.app import GoogleDocsApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="google-calendar", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = GoogleDocsApp(integration=integration)
tool_manager = ToolManager()

tool_manager.add_tool(app_instance.style_text)
tool_manager.add_tool(app_instance.add_content)
tool_manager.add_tool(app_instance.delete_content)

async def main():
    # Get a specific tool by name
   
    tool=tool_manager.get_tool("style_text")
    tool2=tool_manager.get_tool("add_content")
    tool=tool_manager.get_tool("delete_content")
    print(tool)
    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    # Get all tools
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    # List tools in different formats
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    
    
    # result = await tool_manager.call_tool(name="get_today_events", arguments={"days": 5})
    # result = await tool_manager.call_tool(name="style_text", arguments={"document_id": "1Sf6aNiAVhxiOGk6s1712Bp2ApR_7FHJnqZazHbhspLI", "start_index": 1, "end_index": 10, "bold": True, "italic": True, "underline": True, "strikethrough": True, "small_caps": True, "font_size": 12, "font_family": "Arial", "font_weight": 700, "foreground_color": {"red": 0.0, "green": 0.0, "blue": 0.0}, "background_color": {"red": 1.0, "green": 1.0, "blue": 1.0}, "link_url": "https://www.google.com"})
    result=await tool_manager.call_tool(name="add_content", arguments={"document_id": "1Btnr0thri_lN2dLFKGNue0jjipEeqvRU4qB2G6tMFEA", "content": "Hello, world!"})
    # result=await tool_manager.call_tool(name="delete_content", arguments={"document_id": "1kxmcrZKElUP_aDEl1gF1j0vUdQTqFhWTrS5ymacBXxI", "start_index": 1, "end_index": 10})
    print(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)