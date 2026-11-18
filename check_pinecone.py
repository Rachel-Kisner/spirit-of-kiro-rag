import os
from dotenv import load_dotenv

load_dotenv()

from pinecone import Pinecone

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

index_name = "kiro-steering-vectors"

print("INDEX INFORMATION:")
print(pc.describe_index(index_name))

print("\nINDEX SCHEMA:")
print(pc.indexes.describe(name=index_name).schema)