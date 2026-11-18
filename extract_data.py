
# # 1 - Import required libraries
# import os 
# import json  
# import cohere  
# from dotenv import load_dotenv  

# from llama_index.core import SimpleDirectoryReader

# from netfree_unstrict_ssl import unstrict_ssl  

# # 2 - Load environment variables
# load_dotenv()   
# unstrict_ssl()  

# # 3 - Initialize the Cohere API client
# cohere_client = cohere.ClientV2(  
#     api_key=os.environ["COHERE_API_KEY"]  
# )  

# MODEL_NAME = "command-a-03-2025"  

# # 4 - Import the Pydantic extraction schema
# from extraction_models import ExtractedData

# # 5 - Load the source documents
# documents = SimpleDirectoryReader(
#     input_dir="kiro-steering"
# ).load_data()

# # 6 - Select one document for the initial test
# document = documents[0]
# document_text = document.get_content()

# # 7 - Define the JSON Schema for structured extraction
# extraction_schema = { 
#     "type": "object",
#     "properties": {
#         "technologies": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string"},
#                     "category": {"type": "string"},
#                     "description": {"type": "string"},
#                     "source_location": {"type": "string"}
#                 },
#                 "required": [
#                     "name",
#                     "category",
#                     "description",
#                     "source_location"
#                 ]
#             }
#         },
#         "architecture": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string"},
#                     "category": {"type": "string"},
#                     "description": {"type": "string"},
#                     "source_location": {"type": "string"}
#                 },
#                 "required": [
#                     "name",
#                     "category",
#                     "description",
#                     "source_location"
#                 ]
#             }
#         },
#         "rules": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string"},
#                     "category": {"type": "string"},
#                     "description": {"type": "string"},
#                     "source_location": {"type": "string"}
#                 },
#                 "required": [
#                     "name",
#                     "category",
#                     "description",
#                     "source_location"
#                 ]
#             }
#         }
#     },
#     "required": [
#         "technologies",
#         "architecture",
#         "rules"
#     ]
# }

# # 7 - Prepare extraction instructions
# # prompt = f"""
# # Extract structured information from the following project document.

# # You must organize the extracted information into exactly three categories:
# # technologies, architecture, and rules.

# # IMPORTANT: Each item in every category MUST be a structured object,
# # NOT a string.

# # Every item MUST contain these four fields:
# # - name: The name of the technology, component, or rule.
# # - category: The specific type of item.
# # - description: A short factual explanation based only on the document.
# # - source_location: The section heading where the information appears,
# #   or null if it cannot be identified.

# # Category definitions:

# # 1. technologies:
# # Programming languages, frameworks, libraries, platforms,
# # databases, cloud services, and other technologies used in the project.

# # 2. architecture:
# # Architectural components, communication patterns,
# # system organization, and infrastructure patterns.

# # 3. rules:
# # Explicit development rules, naming conventions,
# # and coding standards.

# # Example of the required item structure:

# # {{
# #     "name": "AWS Bedrock",
# #     "category": "Cloud Service",
# #     "description": "Used for AI model integration.",
# #     "source_location": "AI Integration"
# # }}

# # Important instructions:
# # - Never return an item as a plain string.
# # - Every item must contain all four fields.
# # - Extract only information explicitly stated in the document.
# # - Do not invent information or add external knowledge.
# # - Do not duplicate the same item.
# # - Keep descriptions short and factual.
# # - Return empty arrays when a category has no relevant information.

# # Document:
# # {document_text}
# # """
# # 8 - Prepare extraction instructions
# prompt = f"""
# Extract structured information from the following project document.

# Generate a JSON object that follows the provided JSON Schema.

# Extract information into exactly three categories:

# 1. technologies:
# Programming languages, frameworks, libraries, platforms,
# databases, cloud services, and other technologies.

# 2. architecture:
# Architectural components, communication patterns,
# system organization, and infrastructure patterns.

# 3. rules:
# Explicit development rules, naming conventions,
# and coding standards.

# Each item MUST be an object containing:
# - name
# - category
# - description
# - source_location

# Important instructions:
# - Never return plain strings as items.
# - Extract only information explicitly stated in the document.
# - Do not invent information or add external knowledge.
# - Do not duplicate the same item.
# - Keep descriptions short and factual.
# - Use the relevant section heading as source_location.
# - If the section heading is unavailable, use an empty string.
# - Return empty arrays when a category has no relevant information.

# Document:
# {document_text}
# """

# # 9 - Request structured extraction from Cohere
# response = cohere_client.chat( 
#     model=MODEL_NAME,  
#     messages=[  
#         {  
#             "role": "user",  
#             "content": prompt  
#         }  
#     ],  
#     response_format={  
#         "type": "json_object",  
#         "schema": extraction_schema 
#     },  
#     temperature=0.1  
# )
# # 10 - Parse the JSON response
# response_text = response.message.content[0].text  
# extracted_json = json.loads(response_text)
# # 11 - Validate the extracted data with Pydantic
# extracted_data = ExtractedData.model_validate(extracted_json)

# # 10 - Display the extracted information
# print("\nExtracted Data:\n")
# print(extracted_data.model_dump_json(indent=2))

# 1 - Import required libraries
import os
import json
from pathlib import Path
from datetime import datetime, timezone

import cohere
from dotenv import load_dotenv

from netfree_unstrict_ssl import unstrict_ssl

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import TextNode
from llama_index.core.types import BasePydanticProgram
from llama_index.core.extractors import PydanticProgramExtractor

from extraction_models import ExtractedData
print("ExtractedData:", ExtractedData)
print("Is class:", isinstance(ExtractedData, type))
print("Has model_validate:", hasattr(ExtractedData, "model_validate"))

# 2 - Load environment variables
load_dotenv()
unstrict_ssl()


# 3 - Initialize the Cohere API client
cohere_client = cohere.ClientV2(
    api_key=os.environ["COHERE_API_KEY"]
)

MODEL_NAME = "command-a-03-2025"


# 4 - Define the JSON Schema for extraction
item_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "category": {"type": "string"},
        "description": {"type": "string"},
        "source_location": {"type": "string"}
    },
    "required": [
        "name",
        "category",
        "description",
        "source_location"
    ]
}

extraction_schema = {
    "type": "object",
    "properties": {
        "technologies": {
            "type": "array",
            "items": item_schema
        },
        "architecture": {
            "type": "array",
            "items": item_schema
        },
        "rules": {
            "type": "array",
            "items": item_schema
        }
    },
    "required": [
        "technologies",
        "architecture",
        "rules"
    ]
}


# 5 - Define the Cohere structured output program
class CohereJSONSchemaProgram(BasePydanticProgram[ExtractedData]):

    def __init__(self, client, model_name, output_cls):
        self.client = client
        self.model_name = model_name
        self._output_cls = output_cls

    @property
    def output_cls(self):
        return self._output_cls

    def __call__(self, *args, **kwargs):

        # Get the extraction prompt
        prompt = kwargs["input"]

        # Request structured output from Cohere
        response = self.client.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object",
                "schema": extraction_schema
            },
            temperature=0.1
        )

        # Extract the JSON response
        response_text = response.message.content[0].text

        # Validate the response using Pydantic
        return self.output_cls.model_validate_json(response_text)


# # 6 - Define the extraction prompt
# EXTRACT_TEMPLATE_STR = """
# Extract structured information from the following project document.

# Organize the information into exactly three categories:

# 1. technologies:
# Programming languages, frameworks, libraries, platforms,
# databases, cloud services, and other technologies used.

# 2. architecture:
# Architectural components, communication patterns,
# system organization, and infrastructure patterns.

# 3. rules:
# Explicit development rules, naming conventions,
# and coding standards.

# Every extracted item must contain:
# - name
# - category
# - description
# - source_location

# Important instructions:
# - Return every item as an object, never as a plain string.
# - Extract only information explicitly stated in the document.
# - Do not invent information or add external knowledge.
# - Do not duplicate the same item.
# - Keep descriptions short and factual.
# - Use the relevant section heading as source_location.
# - If the heading is unavailable, use an empty string.
# - Return empty arrays when a category has no relevant information.

# Document:
# {context_str}
# """



EXTRACT_TEMPLATE_STR = """
Extract structured information from the following project document.

Organize the information into exactly three categories:

1. technologies:
Programming languages, frameworks, libraries, platforms,
databases, cloud services, AI models, and other technologies used.

2. architecture:
Architectural components, communication patterns,
system organization, and infrastructure patterns.

3. rules:
Explicit development rules, naming conventions,
and coding standards.

Every extracted item must contain:
- name
- category
- description
- source_location

Important extraction rules:

- Extract only information explicitly stated in the document.
- Never invent, assume, infer, or add external knowledge.
- Do not add technical details that are not explicitly documented.
- Keep every description strictly faithful to the source.
- Do not describe a component's functionality based only on its name.
- Do not assign responsibilities to a technology or component
  unless the document explicitly states them.
- Do not duplicate the same item within the same document.
- Use the relevant section heading as source_location.
- If the heading is unavailable, use an empty string.
- Return empty arrays when a category has no relevant information.

Category-specific instructions:

Technologies:
- Extract only technologies explicitly mentioned in the document.
- Do not assume how a technology is used unless the document explains it.
- Do not assign a technical role or responsibility based only
  on general knowledge about that technology.

- **NEW: Model-specific attribution**
  When a document mentions multiple AI models and describes
  several capabilities together, do not assign individual
  capabilities to specific models unless the document explicitly
  establishes that relationship.
  If the document does not specify which model performs which task,
  describe each model only as one of the listed models used
  by the documented AI integration.
  Do not infer model responsibilities from general knowledge.

- **NEW: Technology descriptions**
  Preserve the exact level of detail provided by the source.
  If the document only mentions an integration or a client,
  do not describe it as a database, cache, state manager,
  or another specific role unless that role is explicitly documented.

Architecture:
- Extract only architectural components and patterns explicitly
  described in the document.
- A component name alone is not evidence of its functionality.
- Do not infer responsibilities, behavior, or implementation details
  from component names.
- If a component is listed without an explanation, use a neutral
  description.
- Do not add examples of functionality unless they appear explicitly
  in the source document.
- Preserve the distinction between a component, an architectural
  pattern, and an architectural structure.

Rules:
- Extract only explicit development rules and conventions.
- Do not turn general descriptions or recommendations into rules.
- Preserve the exact scope of each rule as documented.

Document:
{context_str}
"""

# 7 - Initialize the LlamaIndex Pydantic program
extraction_program = CohereJSONSchemaProgram(
    client=cohere_client,
    model_name=MODEL_NAME,
    output_cls=ExtractedData
)


# 8 - Create the LlamaIndex Pydantic extractor
program_extractor = PydanticProgramExtractor(
    program=extraction_program,
    input_key="input",
    extract_template_str=EXTRACT_TEMPLATE_STR,
    show_progress=True
)


# 9 - Load all source documents from both Agentic Coding tools

kiro_documents = SimpleDirectoryReader(
    input_dir="kiro-steering"
).load_data()

copilot_documents = SimpleDirectoryReader(
    input_dir="copilot-docs"
).load_data()

documents = kiro_documents + copilot_documents

print("\nLoaded Documents:")
for document in documents:
    print(document.metadata.get("file_name"))


# 10 - Convert documents into LlamaIndex nodes
nodes = [
    TextNode(text=document.get_content())
    for document in documents
]


# 11 - Extract structured information from all documents
extraction_results = program_extractor.extract(nodes)


# 12 - Initialize the combined extraction result
all_data = ExtractedData()


# 13 - Combine results and attach source file names
for index, (document, result) in enumerate(
    zip(documents, extraction_results)
):

    # Get the source file name
    source_file = (
        document.metadata.get("file_name")
        or Path(
            document.metadata.get(
                "file_path",
                f"document_{index + 1}"
            )
        ).name
    )

    # Convert the extracted dictionary into a Pydantic object
    document_data = ExtractedData.model_validate(result)

    # Add the source file to every extracted item
    for category in [
        "technologies",
        "architecture",
        "rules"
    ]:

        for item in getattr(document_data, category):

            updated_item = item.model_copy(
                update={"source_file": source_file}
            )

            getattr(all_data, category).append(updated_item)


# 14 - Prepare the final JSON structure
output_data = {
    "schema_version": "1.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "items": all_data.model_dump()
}


# 15 - Save the extracted data to JSON
with open(
    "extracted_data.json",
    "w",
    encoding="utf-8"
) as json_file:

    json.dump(
        output_data,
        json_file,
        ensure_ascii=False,
        indent=2
    )


# 16 - Display the extraction summary
print("\nExtraction completed successfully!")

print("\nExtraction Summary:")

print(
    "Technologies:",
    len(all_data.technologies)
)

print(
    "Architecture:",
    len(all_data.architecture)
)

print(
    "Rules:",
    len(all_data.rules)
)

print("\nSaved to: extracted_data.json")
