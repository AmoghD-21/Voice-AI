import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load local environment variables from a .env file
load_dotenv()

def get_llm_agent():
    # Validate GitHub token
    gh_token = os.getenv("GITHUB_TOKEN")

    if not gh_token:
        raise ValueError(
            "GITHUB_TOKEN not found in .env file."
        )
    
    # Configure LangChain to use GitHub's free Model registry
    llm = ChatOpenAI(
        model="gpt-4o",  # You can also use "gpt-4o-mini" for faster processing
        api_key=gh_token,
        base_url="https://models.inference.ai.azure.com"
    )
    
    return llm

if __name__ == "__main__":
    # Test our free LLM endpoint quickly
    try:
        agent = get_llm_agent()
        response = agent.invoke("Hello! Confirming you are working through GitHub Models free tier.")
        print("Success! Response from model:")
        print(response.content)
    except Exception as e:
        print(f"Initialization failed: {e}")