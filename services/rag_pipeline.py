import re

from models.llm import llm

def ask_question(vector_db, user_query, chat_history):

    kb_match = re.search(r"\bKB\d+\b", user_query, re.IGNORECASE)
    if kb_match:
        requested_kb = kb_match.group(0).upper()
        all_docs = list(vector_db.docstore._dict.values())
        results = [
            doc for doc in all_docs
            if doc.metadata.get("kb_id", "").upper() == requested_kb
        ]
    else:
        results = vector_db.similarity_search(user_query, k=3)

    if not results:
        return "I could not find relevant information in the PDFs under the data folder."

    context_parts = []
    sources = []
    for doc in results:
        kb_id = doc.metadata.get("kb_id", "NOT AVAILABLE")
        ticket_id = doc.metadata.get("ticket_id", "NOT AVAILABLE")
        source = doc.metadata.get("source", "NOT AVAILABLE")
        author = doc.metadata.get("author", "NOT AVAILABLE")
        last_modified = doc.metadata.get("last_modified", "NOT AVAILABLE")
        sources.append(f"{kb_id} / {ticket_id} / {source} / Author: {author}")
        context_parts.append(
            f"[KB: {kb_id} | Ticket: {ticket_id} | Source: {source} | "
            f"Author: {author} | Last modified: {last_modified}]\n"
            f"{doc.page_content[:2500]}"
        )

    lowered_query = user_query.lower()
    if "author" in lowered_query or "authored" in lowered_query or "who wrote" in lowered_query:
        for doc in results:
            author = doc.metadata.get("author", "NOT AVAILABLE")
            if author != "NOT AVAILABLE":
                kb_id = doc.metadata.get("kb_id", "NOT AVAILABLE")
                ticket_id = doc.metadata.get("ticket_id", "NOT AVAILABLE")
                source = doc.metadata.get("source", "NOT AVAILABLE")
                return f"{kb_id} was authored by {author}. Source: {source}. Ticket: {ticket_id}."

    context = "\n\n---\n\n".join(context_parts)
    source_list = "\n".join(f"- {source}" for source in sources)

    prompt = f"""
You are an IT support assistant.

Answer the user using only the PDF context below. Do not use outside knowledge.
If the answer is not present in the PDF context, say:
"I could not find this in the available KB PDFs."

PDF context:
{context}

User Issue:
{user_query}

Answer in 5 short bullets or fewer.
Always include the source KB/Ticket when available.

Available retrieved sources:
{source_list}
"""

    return llm.invoke(prompt)
