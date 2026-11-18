# 1 - Import required libraries

import asyncio
import json
from router import select_route
from structured_retriever import retrieve_structured_data
import re  # Used to identify count questions

from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Context
)

from llama_index.core.schema import NodeWithScore
from llama_index.core.llms import ChatMessage

# 2 - Import existing RAG components

from retrieve import retriever, response_synthesizer,llm

# Import input validation function
from validators import (
                        validate_query, 
                        validate_retrieved_nodes,
                        validate_retrieval_confidence,
                        can_retry
                        )
#Define retry configuration- Maximum number of additional search attempts
MAX_RETRIES = 2
# Identify questions that require counting
def is_count_question(query: str) -> bool:

    count_patterns = [
        r"\bhow many\b",
        r"\bcount\b",
        r"\bnumber of\b",
        r"\btotal\b"
    ]

    return any(
        re.search(pattern, query, re.IGNORECASE)
        for pattern in count_patterns
    )

class ValidInputEvent(Event):
    query: str


# 3 - Define an event for retrieved nodes

class RetrievedEvent(Event):
    query: str
    nodes: list[NodeWithScore]

# Define an event for retrying the retrieval
class RetryEvent(Event):
    query: str

# Event for passing validated nodes to synthesis
class ValidatedRetrievalEvent(Event):
    query: str
    nodes: list[NodeWithScore]

class SemanticRouteEvent(Event):
    query: str
    reason: str

class StructuredRetrievedEvent(Event):
    query: str
    structured_query: dict
    records: list[dict]

class StructuredRouteEvent(Event):
    query: str
    reason: str
# 4 - Define the RAG workflow

class RAGWorkflow(Workflow):
    #Validate the user's input
    @step
    async def validate_input_step(
        self, ctx: Context, ev: StartEvent
    ) -> ValidInputEvent | StopEvent:

        query = ev.query

        # Check if the input is valid
        if not validate_query(query):
            return StopEvent(
                result="Please enter a valid question."
            )
        await ctx.store.set("original_query", query)
        await ctx.store.set("current_query", query)
        await ctx.store.set("retry_count", 0)
        await ctx.store.set("attempted_queries", [query])
        await ctx.store.set("search_history", [])

        # Continue the workflow with valid input
        return ValidInputEvent(query=query)
    
    #  Select the retrieval route
    @step
    async def route_step(
        self, ctx: Context, ev: ValidInputEvent
    ) -> SemanticRouteEvent | StructuredRouteEvent | StopEvent:

        route, reason = select_route(ev.query)

        # Save the routing decision in the workflow state
        await ctx.store.set("selected_route", route)
        await ctx.store.set("routing_reason", reason)

        print("\nRouting Result:")
        print("Selected Route:", route)
        print("Reason:", reason)

        # Send the question to the selected route
        if route == "structured":
            return StructuredRouteEvent(
                query=ev.query,
                reason=reason
            )

        if route == "semantic":
            return SemanticRouteEvent(
                query=ev.query,
                reason=reason
            )

        return StopEvent(
            result=f"Unsupported retrieval route: {route}"
        )

    # Retrieve relevant nodes from Pinecone
    @step
    async def retrieve_step(
       self,
       ctx: Context,
       ev: SemanticRouteEvent | RetryEvent
       ) -> RetrievedEvent:

        query = ev.query

        await ctx.store.set("current_query", query)

        retrieved_nodes = retriever.retrieve(query)
        
        # Get the existing search history from the state
        search_history = await ctx.store.get("search_history")
        #  Record the current search attempt
        search_history.append({
           "query": query,
           "scores": [
            node.score for node in retrieved_nodes
        ]
    })
         # NEW: Save the updated search history in the state
        await ctx.store.set("search_history", search_history)


        # Display the retrieved chunks for debugging
        print("\nRelevant Chunks:\n")

        if retrieved_nodes:
         for i, node in enumerate(retrieved_nodes, start=1):
          print(f"Chunk {i}")
          print(f"Similarity Score: {node.score}")
          print(node.node.get_content())
          print("Source Tool:", node.node.metadata.get("tool"))
          print("Source File:", node.node.metadata.get("file_name"))
          print("-" * 60)

        else:
         print("No chunks were retrieved.")
          # : Display the search history for debugging
        print("\nSearch History:")
        print(search_history)
        # Display the current workflow state
        print("\nWorkflow State:")
        print("Original Query:", await ctx.store.get("original_query"))
        print("Current Query:", await ctx.store.get("current_query"))
        print("Retry Count:", await ctx.store.get("retry_count"))

        # Send retrieved nodes to the next step
        return RetrievedEvent(
            query=query,
            nodes=retrieved_nodes
        )
    # NEW: Retrieve structured records from JSON
    @step
    async def structured_retrieve_step(
        self,
        ctx: Context,
        ev: StructuredRouteEvent
    ) -> StructuredRetrievedEvent | StopEvent:

        structured_query, items = retrieve_structured_data(ev.query)

        # Save structured retrieval information in the workflow state
        await ctx.store.set(
            "structured_query",
            structured_query.model_dump()
        )
        await ctx.store.set("structured_results_count", len(items))

        print("\nGenerated Structured Query:")
        print(structured_query.model_dump_json(indent=2))

        print("\nNumber of Retrieved Items:", len(items))

        # Stop if no structured records were found
        if not items:
            return StopEvent(
                result=(
                    "I couldn't find matching structured information "
                    "in the project data. Please try rephrasing your question."
                )
            )

        return StructuredRetrievedEvent(
            query=ev.query,
            structured_query=structured_query.model_dump(),
            records=items
        )
        # Validate the retrieved nodes
    @step
    async def validate_retrieval_step(
        self,
        ctx: Context,
        ev: RetrievedEvent
    ) -> ValidatedRetrievalEvent | RetryEvent | StopEvent:
        has_nodes = validate_retrieved_nodes(ev.nodes)
        has_confidence = validate_retrieval_confidence(ev.nodes)

        if has_nodes and has_confidence:
         return ValidatedRetrievalEvent(
            query=ev.query,
            nodes=ev.nodes
        )
        retry_count = await ctx.store.get("retry_count")
        if not can_retry(retry_count, MAX_RETRIES):
         if not has_nodes:
            return StopEvent(
                result=(
                    "I couldn't find relevant information "
                    "in the project documentation after multiple attempts. "
                    "Please try rephrasing your question or asking "
                    "about another project topic."
                )
            )
         return StopEvent(
            result=(
                "I found some information, but it wasn't relevant enough "
                "to answer your question reliably. "
                "Please try asking in a different way."
            )
        )
        
        original_query = await ctx.store.get("original_query")
        prompt = f"""
        Rewrite the following question into a more specific search query
        that may retrieve relevant information from project documentation.

        Keep the original meaning.
        Return only the rewritten query, without explanations.

        Original question: {original_query}
        Previous search query: {ev.query}
        """
        chat_response = llm.chat([
        ChatMessage(
            role="user",
            content=prompt
    )
])

        rewritten_query = (chat_response.message.content or "").strip()
        if not rewritten_query or rewritten_query.casefold() == ev.query.casefold():
          return StopEvent(
            result=(
                "I couldn't generate a different search query. "
                "Please try rephrasing your question."
            )
        )
        retry_count += 1
        await ctx.store.set("retry_count", retry_count)
        # Record the rewritten query
        attempted_queries = await ctx.store.get("attempted_queries")
        attempted_queries.append(rewritten_query)
        await ctx.store.set("attempted_queries", attempted_queries)
        print("\nRetrying retrieval...")
        print("Retry Count:", retry_count)
        print("Rewritten Query:", rewritten_query)

    # Send a retry event to trigger another retrieval
        return RetryEvent(query=rewritten_query)

    # Generate an answer using the LLM = Generate an answer from semantic nodes
    @step
    async def synthesize_step(self, ev: ValidatedRetrievalEvent) -> StopEvent:

        response = response_synthesizer.synthesize(
            query=ev.query,
            nodes=ev.nodes
        )

        # Finish the workflow and return the answer
        return StopEvent(result=str(response))
    
    # Generate an answer from structured records
    @step
    async def synthesize_structured_step(
        self, ev: StructuredRetrievedEvent
    ) -> StopEvent:
        # NEW: Handle count questions using Python
        if is_count_question(ev.query):

            count = len(ev.records)

            categories = ev.structured_query.get("categories", [])

            category_label = (
            ", ".join(categories)
            if categories
            else "structured"
        )

            answer = (
                f"The number of matching {category_label} records "
                f"is {count}.\n\n"
                "Note: This count represents extracted records, "
                "not necessarily unique technologies or components. "
                "Repeated entries are counted separately."
           )

            return StopEvent(result=answer)
        # Convert the retrieved records into readable JSON text

        structured_context = json.dumps(
            ev.records,
            indent=2,
            ensure_ascii=False
        )

        prompt = f"""
        Answer the user's question using only the structured data below.

        User question:
        {ev.query}

        Retrieved structured data:
        {structured_context}

        Instructions:
        - Use only information present in the retrieved data.
        - Include all relevant records when the user asks for a complete list.
        - Preserve names and source file information.
        - Do not invent missing details.
        - If the data does not fully answer the question, explain what is missing.
        - Write a clear and organized answer.
        """

        chat_response = llm.chat([
            ChatMessage(
                role="user",
                content=prompt
            )
        ])

        answer = (
            chat_response.message.content or ""
        ).strip()

        return StopEvent(result=answer)


# 5 - Test the workflow directly
async def main():

    query = input("Enter your question: ")

    workflow = RAGWorkflow(timeout=120)

    result = await workflow.run(query=query)

    print("\nAnswer:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
