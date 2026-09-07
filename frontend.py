import streamlit as st
import requests

st.set_page_config(page_title="Deep Work Coach", page_icon="📚")
st.title("📚 Deep Work Coach")
st.write("Ask me anything about Cal Newport's book!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is deep work?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call your FastAPI backend
    with st.spinner("Thinking..."):
        response = requests.post("http://127.0.0.1:8000/chat", json={"user_text": prompt})
        if response.status_code == 200:
            data = response.json()
            answer = data["coach_response"]
            sources = data["sources_used"]
            
            # Format the answer with sources
            full_response = f"**Answer:**\n\n{answer}\n\n"
            full_response += "---\n**📖 Sources Used from the Book:**\n"
            for i, src in enumerate(sources):
                full_response += f"*Excerpt {i+1}:* {src[:200]}...\n\n"
        else:
            full_response = "Error: Could not connect to the backend."

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(full_response)
    
    # Add to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})