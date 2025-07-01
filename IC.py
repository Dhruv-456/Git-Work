import gradio as gr
import sqlite3
import google.generativeai as genai

# --- Configuration ---
# IMPORTANT: For production applications, it's highly recommended to use environment variables
# for API keys instead of hardcoding them directly in the script for security reasons.
genai.configure(api_key="AIzaSyDEBzZEOKUpmGYPnCr7SILzR7eZxhFjF6w")
# Corrected model name from "gemimi-2.0-flash" to "gemini-2.0-flash"
model = genai.GenerativeModel("gemini-2.0-flash")

DB_NAME = "chat_history_db"

# --- Database Functions ---
def init_db():
    """Initializes the SQLite database and creates the messages table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(thread_id, role, content):
    """Saves a single message (user or assistant) to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Corrected SQL syntax: removed extra comma after VALUES clause
    c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)",
              (thread_id, role, content))
    conn.commit()
    conn.close()

def load_threads():
    """Loads all distinct conversation threads and their messages from the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Corrected SQL syntax: "SELCT" changed to "SELECT"
    c.execute("SELECT DISTINCT thread_id FROM messages ORDER BY thread_id")
    thread_ids = [row[0] for row in c.fetchall()]
    threads = []
    for tid in thread_ids:
        c.execute("SELECT role, content FROM messages WHERE thread_id = ? ORDER BY id", (tid,))
        messages = [{"role": role, "content": content} for role, content in c.fetchall()]
        threads.append({"thread_id": tid, "messages": messages})
    conn.close()
    return threads

def get_next_thread_id():
    """Determines the next available thread ID for a new conversation by finding the maximum existing ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT MAX(thread_id) FROM messages")
    result = c.fetchone()
    max_id = result[0] if result[0] else 0
    # Corrected function call: "conn_close()" changed to "conn.close()"
    conn.close()
    return max_id + 1

# --- Chatbot Logic ---
def chatbot(user_input, history, thread_id):
    """
    Generates a response from the Gemini API using the provided conversation history.
    This function modifies the 'history' list in-place to update the Gradio state.
    """
    # Prepare the conversation history in the format expected by the Gemini model.
    # The 'history' list comes from Gradio's state, which is a list of
    # {'role': 'user'/'assistant', 'content': '...'}.
    gemini_conversation = []
    for msg in history:
        # Each message needs 'role' and 'parts', where 'parts' is a list of content parts.
        gemini_conversation.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})
    
    # Add the current user's input to the conversation history for the model call.
    # This is crucial for the model to understand the current turn's context.
    gemini_conversation.append({"role": "user", "parts": [{"text": user_input}]})

    bot_response = ""
    try:
        # Call the Gemini model with the prepared conversation history.
        # For multi-turn conversations, pass the entire list of Content objects.
        response = model.generate_content(gemini_conversation)
        bot_response = response.text.strip()
        if not bot_response:
            # Fallback message if the model returns an empty response.
            bot_response = "Hmm, I couldn't come up with a response. Could you please rephrase your question?"
    except Exception as e:
        # Error handling for API calls.
        bot_response = f"Sorry, something went wrong with the AI model: {e}"
        print(f"Error generating content: {e}") # Log the error for debugging

    # Save the user's message and the bot's response to the SQLite database.
    save_message(thread_id, "user", user_input)
    save_message(thread_id, "assistant", bot_response)
    
    # Append the new assistant message to the 'history' list (Gradio state).
    # This list will be returned by the 'respond' function and update the
    # 'history_state' in Gradio, maintaining the current conversation.
    history.append({"role": "assistant", "content": bot_response})
    
    # Return the bot's response text and the updated history list.
    return bot_response, history

# --- UI Formatting Functions ---
def format_chat_history(threads):
    """
    Formats the chat history into collapsible sections for each thread,
    suitable for Gradio Markdown display. Each thread includes its ID.
    """
    if not threads:
        return "No conversation yet."

    formatted = ""
    for idx, thread in enumerate(threads, 1):
        thread_content = ""
        for msg in thread["messages"]:
            role = msg["role"].capitalize()
            # Use Markdown for bold roles and double newlines for separation.
            thread_content += f"**{role}**: {msg['content']}\n\n"
        # Use HTML <details> and <summary> for collapsible sections.
        formatted += f"<details><summary><strong>Thread {idx} (ID: {thread['thread_id']})</strong></summary>\n\n{thread_content}</details>\n\n"
    return formatted

def reset_chat():
    """
    Resets the chat interface to start a new conversation thread.
    Returns an empty chat display, a placeholder for the sidebar, a new thread ID,
    and clears the internal history state.
    """
    new_thread_id = get_next_thread_id()
    # Return values for: chat, history_box, thread_id_state, history_state (cleared)
    return [], "No conversation yet.", new_thread_id, []

# --- Gradio Interface Setup ---
# Initialize the database when the script starts.
init_db()

with gr.Blocks() as demo:
    # Custom CSS for the "New Chat" button and chat history box.
    gr.Markdown(
        """
        <style>
            #new-chat-btn {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background-color: #0d6efd;
                color: white;
                padding: 8px 12px; /* Corrected padding syntax: space instead of comma */
                border-radius: 6px;
                cursor: pointer;
                font-weight: bold;
                border: none; /* Removed default button border */
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Added subtle shadow */
            }
            #new-chat-btn:hover {
                background-color: #0b5ed7;
                box-shadow: 0 6px 8px rgba(0,0,0,0.15); /* Slightly larger shadow on hover */
            }
            /* Style for the history box to make it scrollable */
            #history-box {
                max-height: 500px; /* Limits the height of the history box */
                overflow-y: auto; /* Enables vertical scrolling if content exceeds max-height */
                border: 1px solid #e0e0e0; /* Subtle border for visual separation */
                padding: 10px; /* Inner padding */
                border-radius: 8px; /* Rounded corners */
                background-color: #f9f9f9; /* Light background */
            }
            /* Basic styling for the entire Gradio app layout */
            .gradio-container {
                font-family: 'Inter', sans-serif;
            }
        </style>
        """    
    )

    gr.Markdown("# Gemini 2.0 Chatbot")

    # The "New Chat" button, placed absolutely via CSS.
    new_chat_button = gr.Button("New Chat", elem_id="new-chat-btn")

    with gr.Row():
        with gr.Column(scale=3):
            # Gradio Chatbot component for displaying the conversation.
            # Initialized with an empty list for a clean start.
            chat = gr.Chatbot(value=[], label="Conversation")
            user_input = gr.Textbox(label="Your Message", placeholder="Type here and press send", lines=2)
            submit_button = gr.Button("Send")
        with gr.Column(scale=1):
            gr.Markdown("### Chat History")
            # This markdown element will display the formatted conversation threads from the database.
            history_box = gr.Markdown("No conversation yet.", elem_id="history-box")

    # Gradio State components to manage conversation data across interactions.
    # `history_state`: Stores the current conversation messages as a list of dictionaries.
    history_state = gr.State([]) 
    # `thread_id_state`: Stores the ID of the current conversation thread.
    thread_id_state = gr.State(get_next_thread_id())

    # --- Event Handlers ---
    def respond(user_input, history_list_from_state, current_thread_id):
        """
        Handles user input, generates the bot's response, updates the Gradio state,
        and refreshes the UI components (chat display, sidebar, input box).
        """
        # Append the user's message to the history list that came from Gradio's state.
        # This modification is in-place and Gradio will recognize it as an update to the state.
        history_list_from_state.append({"role": "user", "content": user_input})

        # Call the 'chatbot' function which handles:
        # 1. Formatting history for the LLM.
        # 2. Calling the Gemini model.
        # 3. Saving both user and bot messages to the database.
        # 4. Appending the bot's response to `history_list_from_state` (modifying it in-place).
        bot_response, updated_history_for_state = chatbot(user_input, history_list_from_state, current_thread_id)
        
        # Format the `updated_history_for_state` for display in the Gradio Chatbot component.
        # The Gradio Chatbot expects a list of lists: [[user_msg, bot_msg], [user_msg, bot_msg], ...].
        gradio_chat_display = []
        for i in range(0, len(updated_history_for_state), 2):
            user_msg_content = updated_history_for_state[i]["content"] if i < len(updated_history_for_state) and updated_history_for_state[i]["role"] == "user" else None
            bot_msg_content = updated_history_for_state[i+1]["content"] if (i+1 < len(updated_history_for_state) and updated_history_for_state[i+1]["role"] == "assistant") else None
            gradio_chat_display.append([user_msg_content, bot_msg_content])

        # Reload and format all conversation threads for the sidebar display,
        # ensuring the newly added messages are reflected.
        threads = load_threads()
        sidebar_md = format_chat_history(threads)
        
        # Return values corresponding to the Gradio outputs:
        # chat component content, updated history_state, updated history_box markdown, empty user_input (to clear textbox).
        return gradio_chat_display, updated_history_for_state, sidebar_md, ""

    # Attach event listeners to the buttons.
    # The 'submit_button' triggers the 'respond' function when clicked.
    submit_button.click(
        fn=respond,
        inputs=[user_input, history_state, thread_id_state],
        outputs=[chat, history_state, history_box, user_input]
    )

    # The 'new_chat_button' triggers the 'reset_chat' function.
    new_chat_button.click(
        fn=reset_chat,
        # Outputs include clearing the chat display, resetting history_box,
        # updating thread_id_state, and clearing the internal history_state.
        outputs=[history_state, history_box, thread_id_state, chat]
    )

    # Function to load and display the chat history in the sidebar when the app initially loads.
    def load_sidebar_history():
        threads = load_threads()
        sidebar_md = format_chat_history(threads)
        return sidebar_md

    # Attach the 'load_sidebar_history' function to the demo's load event.
    demo.load(
        fn=load_sidebar_history,
        outputs=[history_box]
    )

# Run the Gradio demo if the script is executed directly.
if __name__ == "__main__":
    demo.launch(share=True) # share=True generates a public link for easy sharing.