from core_logic import get_api_key, generate_llm
from streamlit_app import streamlit_app
import os

def main():
    claudeapi = os.environ.get("CLAUDE3_API_KEY")
    # api = get_api_key("api_key.gitignore")
    llm = generate_llm(claudeapi)
    streamlit_app(llm)

if __name__ == "__main__":
    main()
