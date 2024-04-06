from crewai import Agent
from crewai_tools import SerperDevTool, FileReadTool, WebsiteSearchTool

# Define a mapping of tool names to tool constructors
tool_mapping = {
    'SerperDevTool': SerperDevTool,
    'FileReadTool': FileReadTool,
    'WebsiteSearchTool' : WebsiteSearchTool
    # Add more tools as necessary
}

# Function to convert input string to tool objects
def map_tools(input_string):
    # Split the input string by commas to get the tool names
    tool_names = input_string.split(',')
    tools = []
    for name in tool_names:
        tool_class = tool_mapping.get(name.strip())  # Use strip() to remove any leading/trailing spaces
        if tool_class:
            tools.append(tool_class())
        else:
            print(f"Warning: No tool found for name '{name}'. Skipping.")
    return tools

# Example usage
# Assuming you received the following input from a web form as a single string
# input_tools = "SerperDevTool,FileReadTool"  # This could come from a web form input field

# Map the input string to tool objects
# assigned_tools = map_tools(input_tools)

# Assign the tools to an agent
# agent_with_tools = Agent(
#     role='Example Agent',
#     goal='Demonstrate tool assignment from web form input',
#     tools=assigned_tools,
#     verbose=True
# )

# Now, agent_with_tools has the SerperDevTool and FileReadTool assigned based on the web form input
