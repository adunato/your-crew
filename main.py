from core_logic import get_api_key, generate_llm
from streamlit_app import streamlit_app

def main():
    api = get_api_key("api_key.gitignore")
    llm = generate_llm(api)
    streamlit_app(llm)

if __name__ == "__main__":
    main()
