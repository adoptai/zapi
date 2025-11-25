from langchain.agents import create_agent
from zapi import ZAPI, interactive_chat


def demo_zapi_langchain():
    """ZAPI LangChain integration demo."""
    print("\n🚀 ZAPI LangChain - Demo Example")
    print("=" * 40)

    # Initialize ZAPI and create agent
    z = ZAPI()

    agent = create_agent(
        z.get_llm_model_name(), z.get_zapi_tools(), system_prompt="You are a helpful assistant with access to APIs."
    )

    # Start interactive chat
    interactive_chat(agent, debug_mode=False)


# Run the demo
demo_zapi_langchain()
