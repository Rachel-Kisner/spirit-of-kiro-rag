# 1 - Validate user input

def validate_query(query):

    # Check if the query is empty or contains only spaces
    if not query or not query.strip():
        return False

    return True
# 2 - Validate retrieved nodes

def validate_retrieved_nodes(nodes):

    # Check if at least one relevant node was retrieved
    if not nodes:
        return False

    return True

# 3 - Validate retrieval confidence

def validate_retrieval_confidence(nodes, threshold=0.3):

    # Check if at least one retrieved node meets the confidence threshold
    if not nodes:
        return False

    return any(
        node.score is not None and node.score >= threshold
        for node in nodes
    )

# 4 - Check whether another retry is allowed
def can_retry(retry_count, max_retries):
    return retry_count < max_retries


# Test query validation
if __name__ == "__main__":

    # Test empty and valid queries
    # print(validate_query(""))
    # print(validate_query("   "))
    # print(validate_query("What is Kiro?"))

    # Test empty and non-empty node lists
    # print("Empty nodes:", validate_retrieved_nodes([]))
    # print("Retrieved nodes:", validate_retrieved_nodes([1, 2, 3]))
    

    class MockNode:
        def __init__(self, score):
            self.score = score

    # Test high confidence
    high_scores = [
        MockNode(0.8),
        MockNode(0.6)
    ]

    # Test low confidence
    low_scores = [
        MockNode(0.2),
        MockNode(0.3)
    ]

    print("High confidence:", validate_retrieval_confidence(high_scores))
    print("Low confidence:", validate_retrieval_confidence(low_scores))
    print("No results:", validate_retrieval_confidence([]))