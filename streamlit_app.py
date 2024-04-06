import os
import streamlit as st
import json

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
    print(api)
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

def list_templates():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as file:
            data = json.load(file)
            return list(data.keys())
    return []

# Assuming the rest of the provided code is available and functions are defined as before

def streamlit_app(llm):

    template_name = st.text_input("Template Name")
    if st.button("Save Current Session"):
        save_session(template_name, st.session_state.agents, st.session_state.tasks)
        st.success(f"Session '{template_name}' saved.")

    template_to_load = st.selectbox("Load Template", options=list_templates())
    if st.button("Load Selected Template"):
        session_data = load_session(template_to_load)
        st.session_state.agents = session_data["agents"]
        st.session_state.tasks = session_data["tasks"]
        st.success(f"Loaded template: {template_to_load}")


    # Initialize session state for agents and tasks
    if 'agents' not in st.session_state:
        st.session_state.agents = []
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []

    def add_agent():
        st.session_state.agents.append({'role': '', 'goal': '', 'backstory': ''})

    def add_task():
        st.session_state.tasks.append({'description': '', 'expected_output': ''})

    st.title("Dynamic LLM Crew App")

    # Buttons to add agents and tasks
    st.button("Add Agent", on_click=add_agent)
    st.button("Add Task", on_click=add_task)

    # Dynamically create input fields for each agent
    for i, _ in enumerate(st.session_state.agents):
        with st.container():
            st.write(f"Agent {i+1}")
            st.session_state.agents[i]['role'] = st.text_input(
                f"Role {i+1}", 
                value=st.session_state.agents[i].get('role', ''), 
                key=f"role_{i}"
            )
            st.session_state.agents[i]['goal'] = st.text_input(
                f"Goal {i+1}", 
                value=st.session_state.agents[i].get('goal', ''), 
                key=f"goal_{i}"
            )
            st.session_state.agents[i]['backstory'] = st.text_area(
                f"Backstory {i+1}", 
                value=st.session_state.agents[i].get('backstory', ''), 
                key=f"backstory_{i}"
            )

    # Dynamically create input fields for tasks, including an agent dropdown
    for i, task in enumerate(st.session_state.tasks):
        with st.container():
            st.write(f"Task {i+1}")
            
            # Create a list of agent roles for the dropdown and find the index of the current task's agent
            agent_options = [agent['role'] for agent in st.session_state.agents]
            current_agent_index = agent_options.index(task['agent']) if task['agent'] in agent_options else 0
            
            # Dropdown for selecting an agent for the task
            selected_agent = st.selectbox(
                f"Select Agent for Task {i+1}", 
                agent_options, 
                index=current_agent_index, 
                key=f"agent_select_{i}"
            )
            
            # Set the selected agent and update task details with the current values or empty strings if not present
            task['agent'] = selected_agent
            task['description'] = st.text_input(
                f"Description {i+1}", 
                value=task.get('description', ''), 
                key=f"description_{i}"
            )
            task['expected_output'] = st.text_input(
                f"Expected Output {i+1}", 
                value=task.get('expected_output', ''), 
                key=f"expected_output_{i}"
            )
    # Submit button to process the inputs
    if st.button('Run Crew'):
        st.write("Running Crew with provided details...")
        # Assuming run_crew returns a markdown string as a result
        result = run_crew(llm, st.session_state.agents, st.session_state.tasks)
        st.markdown(result, unsafe_allow_html=True)
        # If you want to let the user copy the result, you could use a text_area like this:
        st.text_area("Result", result, height=300)

api = get_api_key("api_key.gitignore")
llm = generate_llm(api)
streamlit_app(llm)
