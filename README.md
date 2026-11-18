# Spirit of Kiro – RAG System

## 1. Project Purpose

This project implements a Retrieval-Augmented Generation (RAG) system that enables users to ask natural-language questions about the **Spirit of Kiro** game project and receive answers based on its documentation.

The knowledge base combines Markdown documentation generated using two Agentic Coding tools:

- **Kiro**
- **GitHub Copilot**

The system uses LlamaIndex, Cohere embeddings, Pinecone, and an LLM to retrieve relevant information and generate context-based answers.

The project consists of three main stages:

- **Stage A – Semantic RAG:** Load Markdown documents, split them into chunks, generate embeddings, store them in Pinecone, and retrieve relevant information through semantic search.
- **Stage B – Event-Driven Workflow:** Implement an event-driven workflow that validates user questions, routes them to the appropriate retrieval method, and manages the answer-generation process.
- **Stage C – Structured Data Extraction:** Extract structured information from Markdown documents into JSON and support structured queries alongside semantic search.

The main goal is to demonstrate how multiple Agentic Coding documentation sources can be combined into a single RAG system that supports both semantic and structured information retrieval.

## 2. Installation and Configuration

### Prerequisites

Make sure the following tools and accounts are available:

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- A Cohere API key
- A Pinecone API key
- A configured Pinecone index

### Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Rag-LLamaIndex-Project
```

### Install Dependencies

Install the project dependencies using uv:

```bash
uv sync
```

### Configure Environment Variables

Create a `.env` file in the project root directory:

```env
COHERE_API_KEY=your_cohere_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

Make sure the Pinecone index `kiro-steering-classic` exists and is configured with the required dimensions and similarity metric.

**Important:** Never commit your `.env` file or expose API keys in the repository.

## 3. Running the Project

### Stage A – Prepare the Vector Database

```bash
uv run prepare.py
```

This script:

- Loads the Kiro and GitHub Copilot Markdown documents.
- Splits the documents into text chunks.
- Preserves source metadata.
- Generates embeddings using Cohere.
- Stores the vectors in Pinecone.

### Stage B – Run the Event-Driven Workflow

```bash
uv run workflow.py
```

This script runs the event-driven workflow, including input validation, question routing, retrieval, and answer generation.

Enter a question when prompted.

### Stage C – Extract Structured Data

```bash
uv run extract_data.py
```

This script extracts structured information from the Markdown documents and saves it to:

```text
extracted_data.json
```

The extracted information includes:

- Technologies
- Architecture
- Rules

### Launch the Gradio Interface

```bash
uv run app.py
```

After launching, open the following address in your browser:

```text
http://127.0.0.1:7860
```

The Gradio interface provides a chat-based way to ask questions and receive answers using the RAG system.

## 4. Example Questions

The RAG Agent supports two types of queries:

### Semantic Questions

These questions require understanding, explanation, or comparison of information across the project documentation.

Examples:

1. What are the main gameplay features of Spirit of Kiro, and how does AI contribute to the crafting experience?
2. What is the role of AWS Bedrock in the application?
3. Compare what Kiro and GitHub Copilot document about the project architecture and AWS services.
4. What limitations does GitHub Copilot mention about the available repository files?

### Structured Questions

These questions retrieve specific records from the extracted JSON data using categories, keywords, and source information.

Examples:

1. Find all components related to WebSocket.
2. List all technologies used in the project.
3. Find all architecture components.
4. What rules are documented in the source files?

## Workflow Diagram

The diagram below illustrates the RAG workflow, including input validation, semantic and structured retrieval, retrieval validation, retry handling, and answer generation.

See [Spirit of Kiro – RAG Workflow](spirit-of-kiro-rag-workflow.html).