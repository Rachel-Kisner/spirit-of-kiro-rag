
# 1 - Import required components

from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import ToolMetadata

# Reuse the existing Cohere LLM
from retrieve import llm


# 2 - Define the available routing options

routing_choices = [
    ToolMetadata(
        name="semantic",
        description=(
            "Use semantic search when the user asks for explanations, "
            "descriptions, how something works, or questions requiring "
            "understanding the context of project documentation. "
            "This route searches relevant text chunks in Pinecone."
        )
    ),
    ToolMetadata(
        name="structured",
        description=(
            "Use structured lookup when the user asks for complete lists, "
            "all items of a category, specific fields, counts, filtering, "
            "or information that can be retrieved from extracted_data.json. "
            "This route retrieves structured records such as technologies, "
            "architecture components, and development rules."
        )
    )
]


# 3 - Initialize the LlamaIndex selector

selector = LLMSingleSelector.from_defaults(
    llm=llm
)


# 4 - Select the appropriate route

def select_route(query: str) -> tuple[str, str]:

    selection_result = selector.select(
        routing_choices,
        query=query
    )

    selected_option = selection_result.selections[0]

    selected_route = routing_choices[selected_option.index].name

    return selected_route, selected_option.reason


# 5 - Test the router directly

if __name__ == "__main__":

    query = input("Enter your question: ")

    route, reason = select_route(query)

    print("\nRouting Result:")
    print("Selected Route:", route)
    print("Reason:", reason)
