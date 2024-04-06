import os
import streamlit as st
from core_logic import get_api_key, test_llm_connection, generate_llm, run_crew, save_session, load_session, list_templates

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
