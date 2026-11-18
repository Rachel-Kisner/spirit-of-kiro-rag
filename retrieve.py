# 1- # Loading environment variables

import os
from dotenv import load_dotenv

load_dotenv()

from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()
#2-# Initializing Cohere embedding model
from llama_index.embeddings.cohere import CohereEmbedding

embed_model = CohereEmbedding(
    api_key=os.environ["COHERE_API_KEY"],
    model_name="embed-english-v3.0",
    input_type="search_query",
)
#-3# Connecting to Pinecone vector database
from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore

pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)

pinecone_index = pc.Index("kiro-steering-classic")

vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    namespace="kiro-steering"
)
#-4 # Loading existing vector store
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)
# 5- Creating a retriever
retriever = index.as_retriever(
    similarity_top_k=6
)
# 6 - Initializing Cohere LLM
from llama_index.llms.cohere import Cohere

llm = Cohere(
    api_key=os.environ["COHERE_API_KEY"],
    model="command-a-03-2025",
    temperature=0.1
)
# 7 - Creating a response synthesizer
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode

response_synthesizer = get_response_synthesizer(
    llm=llm,
    response_mode=ResponseMode.COMPACT
)
# 8 - Defining the RAG function
def get_rag_answer(query):

    # Retrieve the most relevant chunks from Pinecone
    retrieved_nodes = retriever.retrieve(query)

    # Display the retrieved chunks for debugging
    print("\nRelevant Chunks:\n")

    for i, node in enumerate(retrieved_nodes, start=1):
        print(f"Chunk {i}")
        print(f"Similarity Score: {node.score}")
        print(node.node.get_content())
        print("-" * 60)

    # Generate an answer using the retrieved chunks
    response = response_synthesizer.synthesize(
        query=query,
        nodes=retrieved_nodes
    )

    # Return the generated answer as text
    return str(response)
# 9 - Testing the RAG function directly
if __name__ == "__main__":

    query = input("Enter your question: ")

    answer = get_rag_answer(query)

    print("\nAnswer:\n")
    print(answer)

