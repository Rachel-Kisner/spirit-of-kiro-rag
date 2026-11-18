
import gradio as gr
# Import the Event-Driven Workflow
from workflow import RAGWorkflow

# Initialize the RAG workflow
rag_workflow = RAGWorkflow(timeout=120)

# Handle user questions and return RAG answers
async def answer_question(message, history):

    # Run the Event-Driven Workflow
    result = await rag_workflow.run(query=message)

    # Extract the generated answer
    answer = result

    # Initialize conversation history if empty
    history = history or []

    # Add the user's message to the conversation
    history.append({
        "role": "user",
        "content": message
    })

    # Add the RAG answer to the conversation
    history.append({
        "role": "assistant",
        "content": answer
    })

    # Clear the textbox and update the chat
    return "", history

# Define custom CSS for the chat interface
custom_css = """
.gradio-container {
    max-width: 1000px !important;
    margin: auto !important;
}

#main-title {
    text-align: center;
    margin-bottom: 5px;
}

#subtitle {
    text-align: center;
    color: #64748b;
    margin-bottom: 25px;
}

#chatbot {
    border-radius: 15px;
}

footer {
    display: none !important;
}
"""
# Create the Gradio interface
def main():

    with gr.Blocks(
        title="Kiro RAG Assistant"
    ) as demo:

        gr.Markdown(
            "# 💬 Kiro RAG Assistant",
            elem_id="main-title"
        )

        gr.Markdown(
            "Ask questions about your project documents",
            elem_id="subtitle"
        )

        chatbot = gr.Chatbot(
            label="Conversation",
            height=500,
            elem_id="chatbot"
        )

        with gr.Row():

            message = gr.Textbox(
                placeholder="Type your question here...",
                show_label=False,
                scale=8,
                lines=2
            )

            send_button = gr.Button(
                "Send",
                variant="primary",
                scale=1
            )

        gr.Examples(
            examples=[
                "What is Kiro?",
                "Explain the project architecture",
                "What are the main steering files?"
            ],
            inputs=message
        )

        clear_button = gr.Button(
            "Clear conversation",
            variant="secondary"
        )

        # Submit a question by pressing Enter
        message.submit(
            answer_question,
            inputs=[message, chatbot],
            outputs=[message, chatbot]
        )

        # Submit a question by clicking Send
        send_button.click(
            answer_question,
            inputs=[message, chatbot],
            outputs=[message, chatbot]
        )

        # Clear the conversation history
        clear_button.click(
            lambda: [],
            inputs=None,
            outputs=chatbot
        )

    # Launch the Gradio interface
    demo.launch(
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="blue"
        ),
        css=custom_css
    )


# Run the application
if __name__ == "__main__":
    main()

