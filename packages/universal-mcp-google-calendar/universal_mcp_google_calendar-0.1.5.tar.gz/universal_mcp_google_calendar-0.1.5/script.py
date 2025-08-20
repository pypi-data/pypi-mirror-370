from re import A
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp_google_calendar import app
from universal_mcp_google_calendar.app import GoogleCalendarApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="google-calendar", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = GoogleCalendarApp(integration=integration)
tool_manager = ToolManager()

tool_manager.add_tool(app_instance.add_an_event)
tool_manager.add_tool(app_instance.get_user_timezone)


async def main():
    # Get a specific tool by name
   
    tool=tool_manager.get_tool("get_user_timezone")

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
    
    # Execute the tool
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="get_message", arguments={"message_id": "1985f5a3d2a6c3c8"})
    # result = await tool_manager.call_tool(
    #     name="send_email",
    #     arguments={
    #         "to": "rishabh@agentr.dev",
    #         "subject": " Email",
    #         "body": "<html><body><h1>Hello!</h1><p>This is a <b>test email</b> sent from the script.</p></body></html>",
    #         "body_type": "html"
    #     }
    # )
    # result = await tool_manager.call_tool(name="create_draft", arguments={"to": "rishabh@agentr.dev", "subject": " Draft Email", "body": " test email"})
    # result = await tool_manager.call_tool(name="send_draft", arguments={"draft_id": "r354126479467734631"})
    # result = await tool_manager.call_tool(name="get_draft", arguments={"draft_id": "r5764319286899776116"})
    # result = await tool_manager.call_tool(name="get_profile",arguments={})
    # result = await tool_manager.call_tool(name="list_drafts", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="list_labels",arguments={})
    # result = await tool_manager.call_tool(name="create_label",arguments={"name": "test_label"})
    # Example: Send new email
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": "Meeting Tomorrow", "body": "Let's meet at 2pm"})
    
    # Example: Reply to thread (using thread_id)
    # result = await tool_manager.call_tool(name="add_an_event", arguments={
    #     "summary": "Test Event", 
    #     "description": "This is a test event", 
    #     "start": {"dateTime": "2025-08-20T10:00:00Z", "timeZone": "UTC"}, 
    #     "end": {"dateTime": "2025-08-20T11:00:00Z", "timeZone": "UTC"}, 
    #     "attendees": [{"email": "rishabh@agentr.dev"}], 
    #     "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=TU,FR;COUNT=5"]
    # })
    result = await tool_manager.call_tool(name="get_user_timezone", arguments={})
    print(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)