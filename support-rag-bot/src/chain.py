"""
Step 2: RAG chain.

Builds a LangChain Retrieval-Augmented Generation (RAG) chain that:
  1. Takes the user's question
  2. Retrieves the top-k most relevant chunks from the vector store
  3. Injects those chunks into a prompt as context
  4. Sends the enriched prompt to the LLM
  5. Returns the answer and the source chunks used

Key concepts demonstrated:
- Retriever        : Wraps the vector store. On each query it converts the
                     question to a vector and returns the k nearest chunks.
- Prompt template  : Instructs the LLM to answer only from the provided
                     context, reducing hallucination.
- LangChain LCEL   : The pipe (|) operator chains retriever → prompt → LLM
                     → output parser into a single callable.
- Source citations : The chain returns which document chunks were used,
                     giving transparency into why the answer was produced.
"""

from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma

MODEL = "claude-opus-4-6"
TOP_K = 4  # number of chunks to retrieve per query

PROMPT_TEMPLATE = """You are a helpful customer support agent for FlowDesk.

Use only the context below to answer the question. If the answer is not in
the context, say: "I don't have that information in the documentation —
please contact support@flowdesk.io."

Context:
{context}

Question: {question}

Answer:"""


def build_chain(vectorstore: Chroma) -> tuple:
    """
    Build and return (chain, retriever).

    The chain is a LangChain LCEL pipeline:
        retriever | prompt | llm | output_parser

    Returns the retriever separately so callers can inspect source chunks.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=PROMPT_TEMPLATE,
    )

    llm = ChatAnthropic(model=MODEL)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # LCEL chain: retrieve → format → prompt → LLM → parse
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain, retriever
