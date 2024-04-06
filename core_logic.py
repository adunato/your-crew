import json
import os

from crewai import Agent, Task, Process, Crew
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate


def get_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()  # .strip() removes any leading/trailing whitespace
    except FileNotFoundError:
        print("API key file not found.")
        return None
    
def test_llm_connection(chat):
    try:        
      prompt = ChatPromptTemplate.from_messages(
          [("human", "Give me a list of famous tourist attractions in Japan")]
      )
      chain = prompt | chat
      for chunk in chain.stream({}):
          print(chunk.content, end="", flush=True)
      return True
    except Exception as e:
        print("LLM Connection Failed. Error:", str(e))
        return False
    
def generate_llm(api):
    # print(api)
    llm = ChatAnthropic(model="claude-3-haiku-20240307", anthropic_api_key=api)
    return llm

def run_crew(llm, agent_details, task_details):
    # Create Agent objects dynamically from agent_details
    agents = [Agent(role=agent['role'],
                    goal=agent['goal'],
                    backstory=agent['backstory'],
                    verbose=True,
                    allow_delegation=True,
                    llm=llm) for agent in agent_details]
    
    # Match agents to tasks based on role
    tasks = []
    for task_detail in task_details:
        # Find the agent assigned to this task
        agent_for_task = next((agent for agent in agents if agent.role == task_detail['agent']), None)
        if agent_for_task:
            # Create Task object and append to tasks list
            tasks.append(Task(description=task_detail['description'],
                              agent=agent_for_task,
                              expected_output=task_detail['expected_output']))
    
    # Run the crew with the dynamically created agents and tasks
    crew = Crew(agents=agents, tasks=tasks, verbose=2, process=Process.sequential)
    result = crew.kickoff()
    
    return result

SESSIONS_FILE = "sessions.json"

def save_session(template_name, agents, tasks):
    data = {
        template_name: {
            "agents": agents,
            "tasks": tasks
        }
    }
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r+") as file:
            existing_data = json.load(file)
            existing_data.update(data)
            file.seek(0)
            json.dump(existing_data, file, indent=4)
    else:
        with open(SESSIONS_FILE, "w") as file:
            json.dump(data, file, indent=4)

def load_session(template_name):
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as file:
            data = json.load(file)
            return data.get(template_name, {"agents": [], "tasks": []})
    return {"agents": [], "tasks": []}

def delete_session(template_name):
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r') as file:
            data = json.load(file)
        
        # Check if the template exists and delete it
        if template_name in data:
            del data[template_name]
            
            # Write the updated data back to the file
            with open(SESSIONS_FILE, 'w') as file:
                json.dump(data, file, indent=4)

def list_templates():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as file:
            data = json.load(file)
            return list(data.keys())
    return []

