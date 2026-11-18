# # 1 - Import required libraries

# import json
# from pathlib import Path
# from typing import Literal

# from pydantic import BaseModel, Field

# # Import Cohere Client and environment variables

# import os
# from cohere import ClientV2
# from dotenv import load_dotenv

# load_dotenv()

# cohere_client = ClientV2(
#     api_key=os.environ["COHERE_API_KEY"]
# )


# # 2 - Define the structured query schema

# class StructuredQuery(BaseModel):

#     categories: list[
#         Literal["technologies", "architecture", "rules"]
#     ] = Field(
#         default_factory=list,
#         description="Categories to search. Empty means all categories."
#     )

#     keywords: list[str] = Field(
#         default_factory=list,
#         description="Keywords to search in item fields."
#     )

#     source_file: str | None = Field(
#         default=None,
#         description="Optional source file filter."
#     )

#     # Explicitly indicate whether the user requests all records
#     search_all: bool = Field(
#         default=False,
#         description="True only when the user explicitly requests all records or all records in a category."
#     )

#     limit: int = Field(
#         default=100,
#         ge=1,
#         le=1000,
#         description="Maximum number of results."
#     )


# # 3 - Load the structured data

# DATA_FILE = Path(__file__).parent / "extracted_data.json"


# def load_structured_data() -> dict:

#     with open(DATA_FILE, "r", encoding="utf-8") as file:
#         return json.load(file)



# # 4 - Generate a structured query using Cohere JSON Schema

# def generate_structured_query(user_query: str) -> StructuredQuery:

#     prompt = f"""
#     Convert the user's question into a structured query.

#     Available categories:
#     - technologies
#     - architecture
#     - rules

#     Available fields:
#     - name
#     - category
#     - description
#     - source_location
#     - source_file

#     Rules:
#     - Select only relevant categories.
#     - Use keywords only when filtering is necessary.
#     - Use an empty categories list when searching all categories.
#     - Use null for source_file unless a specific file is requested.
#     - Do not invent filters.
    
#     User question:
#     {user_query}
#     """

# #Create a Cohere-compatible JSON Schema

#     schema = StructuredQuery.model_json_schema()

#     # Remove unsupported numeric constraints
#     schema["properties"]["limit"].pop("minimum", None)
#     schema["properties"]["limit"].pop("maximum", None)

#     # Require all fields in the generated response
#     schema["required"] = [
#         "categories",
#         "keywords",
#         "source_file",
#         "limit"
#     ]


#     # Send the structured query request to Cohere

#     response = cohere_client.chat(
#         model="command-a-03-2025",
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         response_format={
#             "type": "json_object",
#             "schema": schema
#         }
#     )

#     response_text = response.message.content[0].text

#     return StructuredQuery.model_validate_json(response_text)


# # 5 - Execute the structured query

# def execute_structured_query(
#     structured_query: StructuredQuery
# ) -> list[dict]:

#     data = load_structured_data()

#     selected_categories = (
#         structured_query.categories
#         if structured_query.categories
#         else ["technologies", "architecture", "rules"]
#     )

#     results = []

#     for category in selected_categories:

#         items = data.get("items", {}).get(category, [])

#         for item in items:

#             # Apply the source file filter
#             if structured_query.source_file:

#                 source_file = item.get("source_file", "")

#                 if structured_query.source_file.casefold() not in source_file.casefold():
#                     continue

#             # Apply keyword filtering
#             searchable_text = " ".join([
#                 str(item.get("name", "")),
#                 str(item.get("category", "")),
#                 str(item.get("description", "")),
#                 str(item.get("source_location", "")),
#                 str(item.get("source_file", ""))
#             ]).casefold()

#             if structured_query.keywords:

#                 if not any(
#                     keyword.casefold() in searchable_text
#                     for keyword in structured_query.keywords
#                 ):
#                     continue

#             results.append(item)

#             if len(results) >= structured_query.limit:
#                 return results

#     return results


# # 6 - Combine query generation and structured retrieval

# def retrieve_structured_data(user_query: str):

#     structured_query = generate_structured_query(user_query)

#     results = execute_structured_query(structured_query)

#     return structured_query, results


# # 7 - Test structured retrieval directly

# if __name__ == "__main__":

#     query = input("Enter your question: ")

#     structured_query, results = retrieve_structured_data(query)

#     print("\nGenerated Structured Query:")
#     print(structured_query.model_dump_json(indent=2))

#     print("\nRetrieved Items:")
#     print(json.dumps(results, indent=2, ensure_ascii=False))

#     print("\nNumber of Retrieved Items:", len(results))

# 1 - Import required libraries

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# Import Cohere Client and environment variables

import os
from cohere import ClientV2
from dotenv import load_dotenv

load_dotenv()

cohere_client = ClientV2(
    api_key=os.environ["COHERE_API_KEY"]
)


# 2 - Define the structured query schema

class StructuredQuery(BaseModel):

    categories: list[
        Literal["technologies", "architecture", "rules"]
    ] = Field(
        default_factory=list,
        description="Categories to search."
    )

    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords to search in item fields."
    )

    source_file: str | None = Field(
        default=None,
        description="Optional source file filter."
    )

    # NEW: Explicitly indicate whether the user requests all records
    search_all: bool = Field(
        default=False,
        description="True only when the user explicitly requests all records or all records in a category."
    )

    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of results."
    )


# 3 - Load the structured data

DATA_FILE = Path(__file__).parent / "extracted_data.json"


def load_structured_data() -> dict:

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# 4 - Generate a structured query using Cohere JSON Schema

def generate_structured_query(user_query: str) -> StructuredQuery:

    # prompt = f"""
    # Convert the user's question into a structured query.

    # Available categories:
    # - technologies
    # - architecture
    # - rules

    # Available fields:
    # - name
    # - category
    # - description
    # - source_location
    # - source_file

    # Rules:

    # - Select only relevant categories.
    # - Use keywords when the question refers to specific entities,
    #   concepts, or subjects.
    # - Use source_file only when the user requests information
    #   from a specific file.
    # - Set search_all to true ONLY when the user explicitly asks
    #   for all records or all records in a specific category.
    # - Examples of explicit requests:
    #   "List all technologies"
    #   "List all architecture components"
    #   "How many technologies are documented?"
    #   "Show all development rules"
    # - For a question about an entity or subject that is not
    #   represented in the available categories, do not select
    #   an unrelated category.
    # - Do not use search_all as a fallback when you cannot
    #   identify relevant information.
    # - If the question cannot be matched to the available data,
    #   return empty categories, empty keywords, null source_file,
    #   and search_all=false.
    # - Do not invent filters.

    # User question:
    # {user_query}
    # """

    prompt = f"""
    Convert the user's question into a structured query.

    Available categories:
    - technologies
    - architecture
    - rules

    Available fields:
    - name
    - category
    - description
    - source_location
    - source_file

    Rules:

    - Select ALL relevant categories, not just the most obvious one.
    - A subject may appear in multiple categories.
    - When the user asks for all records related to a subject,
    include every category that may contain matching records.
    - For example:
    "Find all components related to WebSocket"
    must select both "technologies" and "architecture",
    because WebSocket-related records may exist in both categories.
    - Do not select unrelated categories.
    - Use keywords when the question refers to specific entities,
    concepts, subjects, features, or conditions.
    - Use source_file only when the user requests information
    from a specific file.
    - Set search_all to true ONLY when the user explicitly asks
    for all records in general or all records in a specific category,
    without an additional filtering condition.

    - Examples of search_all=true:
    "List all technologies"
    "List all architecture components"
    "How many technologies are documented?"
    "Show all development rules"

    - Examples of search_all=false:
    "Find all components related to WebSocket"
    "List technologies used by the authentication feature"
    "Find all architecture components related to networking"

    - Important:
    The word "all" does not automatically mean search_all=true.
    If the question contains a specific entity, subject, feature,
    or condition, treat it as a filtered query and extract relevant
    keywords.

    - For a question about an entity or subject that is not
    represented in the available categories, do not select
    an unrelated category.
    - Do not use search_all as a fallback when you cannot
    identify relevant information.
    - If the question cannot be matched to the available data,
    return empty categories, empty keywords, null source_file,
    and search_all=false.
    - Do not invent filters.

    User question:
    {user_query}
    """


    # Create a Cohere-compatible JSON Schema

    schema = StructuredQuery.model_json_schema()

    # Remove unsupported numeric constraints
    schema["properties"]["limit"].pop("minimum", None)
    schema["properties"]["limit"].pop("maximum", None)

    # Require all fields in the generated response
    schema["required"] = [
        "categories",
        "keywords",
        "source_file",
        "search_all",
        "limit"
    ]

    # Send the structured query request to Cohere

    response = cohere_client.chat(
        model="command-a-03-2025",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object",
            "schema": schema
        }
    )

    response_text = response.message.content[0].text

    return StructuredQuery.model_validate_json(response_text)


# 5 - Execute the structured query

def execute_structured_query(
    structured_query: StructuredQuery
) -> list[dict]:

    # NEW: Prevent unrestricted retrieval when no valid filter exists
    has_filters = (
        bool(structured_query.categories)
        or bool(structured_query.keywords)
        or bool(structured_query.source_file)
    )

    if not structured_query.search_all and not has_filters:
        return []

    data = load_structured_data()

    # CHANGED: Search all categories only when explicitly requested
    selected_categories = (
        structured_query.categories
        if structured_query.categories
        else (
            ["technologies", "architecture", "rules"]
            if structured_query.search_all
            else []
        )
    )

    results = []

    for category in selected_categories:

        items = data.get("items", {}).get(category, [])

        for item in items:

            # Apply the source file filter
            if structured_query.source_file:

                source_file = item.get("source_file", "")

                if structured_query.source_file.casefold() not in source_file.casefold():
                    continue

            # Apply keyword filtering
            searchable_text = " ".join([
                str(item.get("name", "")),
                str(item.get("category", "")),
                str(item.get("description", "")),
                str(item.get("source_location", "")),
                str(item.get("source_file", ""))
            ]).casefold()

            if structured_query.keywords:

                if not any(
                    keyword.casefold() in searchable_text
                    for keyword in structured_query.keywords
                ):
                    continue

            results.append(item)

            if len(results) >= structured_query.limit:
                return results

    return results


# 6 - Combine query generation and structured retrieval

def retrieve_structured_data(user_query: str):

    structured_query = generate_structured_query(user_query)

    results = execute_structured_query(structured_query)

    return structured_query, results


# 7 - Test structured retrieval directly

if __name__ == "__main__":

    query = input("Enter your question: ")

    structured_query, results = retrieve_structured_data(query)

    print("\nGenerated Structured Query:")
    print(structured_query.model_dump_json(indent=2))

    print("\nRetrieved Items:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

    print("\nNumber of Retrieved Items:", len(results))
