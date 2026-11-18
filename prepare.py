import os
from dotenv import load_dotenv
load_dotenv()
from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()

#Loading

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

# Loading

reader_kiro = SimpleDirectoryReader(input_dir="kiro-steering")
kiro_documents = reader_kiro.load_data()

reader_copilot = SimpleDirectoryReader(input_dir="copilot-docs")
copilot_documents = reader_copilot.load_data()

documents = kiro_documents + copilot_documents

print(f"Kiro documents loaded: {len(kiro_documents)}")
print(f"Copilot documents loaded: {len(copilot_documents)}")
print(f"Total documents loaded: {len(documents)}")

print(f"Number of documents loaded: {len(documents)}")

for doc in kiro_documents:
    doc.metadata["tool"] = "Kiro"

for doc in copilot_documents:
    doc.metadata["tool"] = "GitHub Copilot"

#Chunking

from llama_index.core.node_parser import TokenTextSplitter

node_parser = TokenTextSplitter(
    chunk_size=300,
    chunk_overlap=20
)

nodes = node_parser.get_nodes_from_documents(
    documents=documents, show_progress=True
)

print("\nNodes with missing tool metadata:")

for i, node in enumerate(nodes):
    if not node.metadata.get("tool"):
        print(f"Node {i}")
        print("File:", node.metadata.get("file_name"))
        print("Metadata:", node.metadata)
print(f"Number of nodes created: {len(nodes)}")

# Verify metadata
print("\nMetadata verification:")

for node in nodes:
    print({
        "tool": node.metadata.get("tool"),
        "file_name": node.metadata.get("file_name"),
        "file_path": node.metadata.get("file_path")
    })

#Embedding

COHERE_API_KEY=os.getenv("COHERE_API_KEY")
from llama_index.embeddings.cohere import CohereEmbedding

# with input_typ='search_query'
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
    input_type="search_document",
)
# texts=[(node.get_content())for node in nodes]
# embeddings = embed_model.get_text_embedding_batch(texts)

# print(len(embeddings))
# print(embeddings[:5])
#Indexing And Saving

from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext

PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]

pc = Pinecone(api_key=PINECONE_API_KEY)
description = pc.describe_index("kiro-steering-vectors")

print("Index description:")
print(description)
print("Available Pinecone Indexes:")

for idx in pc.list_indexes():
    print(idx)
pinecone_index = pc.Index("kiro-steering-classic")
pinecone_vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="kiro-steering")
storage_context = StorageContext.from_defaults(vector_store=pinecone_vector_store)
index = VectorStoreIndex(
    nodes=nodes,
    storage_context=storage_context,
    embed_model=embed_model
)
print("Documents successfully indexed in Pinecone!")

# Check Pinecone vector count

stats = pinecone_index.describe_index_stats()

print("\nPinecone statistics:")
print(stats)

print(
    "Vectors in kiro-steering namespace:",
    stats.namespaces.get("kiro-steering", {}).get("vector_count", 0)
)
#Pinecone Instance - Connection

#Storage Context

#index = VectoreStoreIndex