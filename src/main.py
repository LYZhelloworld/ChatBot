import streamlit as st

from langchain_core.messages import HumanMessage, AIMessage

from chatbot.agent import Agent
from chatbot.types import StreamedResponse

st.set_page_config(page_title="ChatBot")

# Initialize session states
# Initialize an empty list to store messages
st.session_state.messages = []
# Check if the agent key exists in the session state, if not, initialize it as None
if "agent" not in st.session_state:
    st.session_state.agent = None

# Styles
st.markdown("""
<style>            
    details {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    summary {
        font-weight: bold;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Display the title and caption in the sidebar to introduce the ChatBot
    st.title("ChatBot")
    st.caption("An interactive chatting tool powered by Streamlit")

    # List all available agents for user to choose from
    agents = Agent.list_agents()
    selected_agent = st.selectbox("Select an agent:", agents)

    # Handle the selection of an agent or the reset to default state
    if not selected_agent:
        st.session_state.agent = None
    elif st.session_state.agent is None or st.session_state.agent.name != selected_agent:
        st.session_state.agent = Agent(selected_agent)


def print_assistant_message(response: StreamedResponse):
    """
    Process and print the assistant's message.

    This function iterates over the response chunks, separating the assistant's thoughts and actual responses based on <think> tags.
    It then dynamically updates the message interface to show the assistant's thought process and final response.

    :param StreamedResponse response: the streamed response object containing the assistant's response and thoughts.
    """

    # Initialize variables for storing thoughts and responses
    reasoning_resposne = ""
    assistant_response = ""

    # Create an empty placeholder for displaying messages
    message_placeholder = st.empty()
    is_inside_think_tag = False

    # Iterate over each chunk in the response
    for chunk in response:
        # Check if the current chunk is a start or end tag for thoughts
        if chunk == "<think>":
            is_inside_think_tag = True
            continue
        elif chunk == "</think>":
            is_inside_think_tag = False
            continue

        # Based on whether inside <think> tags, decide to accumulate thoughts or responses
        if is_inside_think_tag:
            reasoning_resposne += chunk
            # Update the placeholder to show the assistant's current thought process
            message_placeholder.markdown(f'<details><summary>Thinking</summary>{reasoning_resposne}</details>', unsafe_allow_html=True)
        else:
            assistant_response += chunk
            # Update the placeholder to show the assistant's current thought process and response
            message_placeholder.markdown(
                f'<details><summary>Thinking</summary>{reasoning_resposne}</details>{assistant_response}', unsafe_allow_html=True)

    # Add the assistant's response to the session state messages list
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})


def main_loop():
    """
    The main function for the chat interface loop.
    This function is responsible for displaying the chat history, rendering messages, and processing user input.
    """
    # Set the title of the chat interface to the name of the agent.
    if not st.session_state.agent:
        st.title("Please select an agent.")
        return

    st.title(st.session_state.agent.name)

    # Load history when loading the page.
    if not st.session_state.messages:
        history = st.session_state.agent.history()
        for item in history:
            if isinstance(item, HumanMessage):
                st.session_state.messages.append({"role": "user", "content": item.content})
            elif isinstance(item, AIMessage):
                st.session_state.messages.append({"role": "assistant", "content": item.content})

    # Render all messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process user inputs
    if prompt := st.chat_input("Type something..."):
        prompt = prompt.strip()
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.session_state.agent.chat(prompt)
            print_assistant_message(response)


main_loop()
