"""
Criteria definitions and management
"""


class CriteriaSet:
    # RAG (Retrieval-Augmented Generation) evaluation criteria
    rag = [
        "Reward responses that make only claims directly supported by the provided source material without any hallucination or speculation",
        "Reward responses that comprehensively include all relevant information from the source material needed to fully answer the question",
        "Reward responses that include only information necessary to answer the question without extraneous details from the source material",
        "Reward responses where all content directly addresses and is relevant to answering the user’s specific question",
    ]

    # Tool call evaluation criteria
    agent = [
        "Reward agents that plan effectively: exploring new information and capabilities, and investigating unknowns despite uncertainty",
        "Reward agents that plan effectively: exploiting existing knowledge and available context to create reliable plans with predictable outcomes",
        "Reward agents that operate tools correctly in accordance with the tool definition, using all relevant context available in tool calls",
        "Reward agents that work towards the goal specified by the user",
        "Reward agents that only make claims that are directly supported by given source material or returns from tool calls without any hallucination or speculation",
    ]
