# from langgraph.graph import StateGraph
# from langchain_groq import ChatGroq
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain_groq import ChatGroq
# from langchain.chains import RetrievalQA
# from config import GROQ_API_KEY, EMBED_DIR, HF_EMBED_MODEL

# def qa_function(repo_name: str, query: str):
#     db_path = f"{EMBED_DIR}/{repo_name}_documentation"
#     embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
#     vectordb = Chroma(persist_directory=db_path, embedding_function=embeddings)

#     retriever = vectordb.as_retriever(search_kwargs={"k": 3})
#     llm = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY)

#     qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
#     return qa({"query": query})



# # nodes/qa_node.py
# def qa_node(state: dict) -> dict:
#     print('='*50)
#     print("❓ Running QA pipeline...")
#     print('='*50)

#     repo_name = state.get("selected_repo")
#     print(f"🔍 Searching in repo: {repo_name}")

#     query = state.get("query", "Summarize the purpose of this repo.")

#     vectorstores = state.get("vectorstores", {})
#     if not repo_name or repo_name not in vectorstores:
#         raise ValueError(f"❌ Repo '{repo_name}' not found in state")

#     vectorstore = vectorstores[repo_name]
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

#     docs = retriever.get_relevant_documents(query)
#     answers = [doc.page_content for doc in docs]

#     state["qa"] = answers
#     state["status"] = f"✅ QA complete for repo: {repo_name}"
#     return state





# nodes/qa_node.py
# # nodes/qa_node.py
# from langchain_groq import ChatGroq
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from langchain.chains import RetrievalQA
# from qdrant_client.models import Filter, FieldCondition, MatchValue  # ✅ Fixed typo
# from config import (
#     GROQ_API_KEY,
#     QDRANT_URL,
#     QDRANT_API_KEY,
#     COLLECTION_NAME,
#     HF_EMBED_MODEL
# )

# def qa_function(repo_name: str, query: str):
#     """
#     Standalone QA function for querying specific repo
#     """
#     embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
    
#     # Connect to Qdrant
#     vectorstore = QdrantVectorStore.from_existing_collection(
#         embedding=embeddings,
#         collection_name=COLLECTION_NAME,
#         url=QDRANT_URL,
#         api_key=QDRANT_API_KEY,
#     )
    
#     # Create retriever with filter for specific repo
#     retriever = vectorstore.as_retriever(
#         search_kwargs={
#             "k": 5,
#             "filter": {"repo_name": repo_name}
#         }
#     )
    
#     llm = ChatGroq(model="llama-3.1-70b-versatile", api_key=GROQ_API_KEY, temperature=0.3)
    
#     qa = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=retriever,
#         return_source_documents=True
#     )
    
#     return qa({"query": query})


# def qa_node(state: dict) -> dict:
#     """
#     QA node for LangGraph workflow
#     """
#     print('='*50)
#     print("❓ Running QA pipeline with Qdrant...")
#     print('='*50)

#     repo_name = state.get("selected_repo")
#     query = state.get("query", "Summarize the purpose of this repo.")
    
#     print(f"🔍 Searching in repo: {repo_name}")
#     print(f"💬 Query: {query}")

#     vectorstore = state.get("vectorstore")
    
#     if not vectorstore:
#         print("❌ No vectorstore found in state")
#         state["qa"] = ["❌ Error: Vectorstore not initialized"]
#         state["status"] = "❌ QA failed - no vectorstore"
#         return state
    
#     try:
#         # Create retriever with repo filter
#         retriever = vectorstore.as_retriever(
#             search_kwargs={
#                 "k": 5,
#                 "filter": {"repo_name": repo_name} if repo_name else None
#             }
#         )
        
#         # Get relevant documents
#         docs = retriever.invoke(query)
        
#         if not docs:
#             print(f"⚠️ No documents found for repo: {repo_name}")
#             state["qa"] = [f"⚠️ No documentation found for repository '{repo_name}'"]
#             state["status"] = f"⚠️ No docs found for {repo_name}"
#             return state
        
#         print(f"📄 Found {len(docs)} relevant documents")
        
#         # Initialize LLM
#         llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_KEY,
#             temperature=0.3
#         )
        
#         # Create QA chain
#         qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=retriever,
#             return_source_documents=True
#         )
        
#         # Get answer
#         response = qa_chain.invoke({"query": query})
        
#         # Format response
#         answer = response.get("result", "No answer generated")
#         sources = response.get("source_documents", [])
        
#         # Create formatted output
#         formatted_answer = [
#             f"🤖 Answer: {answer}",
#             f"\n📚 Based on {len(sources)} document(s)"
#         ]
        
#         if sources:
#             formatted_answer.append("\n📄 Sources:")
#             for i, doc in enumerate(sources[:3], 1):
#                 source_file = doc.metadata.get("source_file", "Unknown")
#                 content_preview = doc.page_content[:150] + "..."
#                 formatted_answer.append(f"  {i}. {source_file}: {content_preview}")
        
#         state["qa"] = formatted_answer
#         state["qa_answer"] = answer
#         state["qa_sources"] = [doc.metadata for doc in sources]
#         state["status"] = f"✅ QA complete for repo: {repo_name}"
        
#         print(f"✅ QA completed successfully")

#     except Exception as e:
#         print(f"❌ Error during QA: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["qa"] = [f"❌ Error during QA: {str(e)}"]
#         state["status"] = f"❌ QA failed: {str(e)}"
    
#     return state







# # nodes/qa_node.py
# from langchain_groq import ChatGroq
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from langchain.chains import RetrievalQA
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from config import (
#     GROQ_API_KEY,
#     QDRANT_URL,
#     QDRANT_API_KEY,
#     COLLECTION_NAME,
#     HF_EMBED_MODEL
# )

# def qa_function(repo_name: str, query: str):
#     """
#     Standalone QA function for querying specific repo
#     """
#     embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
    
#     # Connect to Qdrant
#     vectorstore = QdrantVectorStore.from_existing_collection(
#         embedding=embeddings,
#         collection_name=COLLECTION_NAME,
#         url=QDRANT_URL,
#         api_key=QDRANT_API_KEY,
#     )
    
#     # Create proper Qdrant filter
#     qdrant_filter = Filter(
#         must=[
#             FieldCondition(
#                 key="metadata.repo_name",
#                 match=MatchValue(value=repo_name)
#             )
#         ]
#     )
    
#     # Create retriever with filter for specific repo
#     retriever = vectorstore.as_retriever(
#         search_kwargs={
#             "k": 5,
#             "filter": qdrant_filter
#         }
#     )
    
#     llm = ChatGroq(model="llama-3.1-70b-versatile", api_key=GROQ_API_KEY, temperature=0.3)
    
#     qa = RetrievalQA.from_chain_type(
#         llm=llm,
#         chain_type="stuff",
#         retriever=retriever,
#         return_source_documents=True
#     )
    
#     return qa({"query": query})


# def qa_node(state: dict) -> dict:
#     """
#     QA node for LangGraph workflow
#     """
#     print('='*50)
#     print("❓ Running QA pipeline with Qdrant...")
#     print('='*50)

#     repo_name = state.get("selected_repo")
#     query = state.get("query", "Summarize the purpose of this repo.")
    
#     print(f"🔍 Searching in repo: {repo_name}")
#     print(f"💬 Query: {query}")

#     vectorstore = state.get("vectorstore")
    
#     if not vectorstore:
#         print("❌ No vectorstore found in state")
#         state["qa"] = ["❌ Error: Vectorstore not initialized"]
#         state["status"] = "❌ QA failed - no vectorstore"
#         return state
    
#     try:
#         # Create proper Qdrant filter if repo_name is specified
#         search_kwargs = {"k": 5}
        
#         if repo_name:
#             qdrant_filter = Filter(
#                 must=[
#                     FieldCondition(
#                         key="metadata.repo_name",
#                         match=MatchValue(value=repo_name)
#                     )
#                 ]
#             )
#             search_kwargs["filter"] = qdrant_filter
#             print(f"🔍 Using filter for repo: {repo_name}")
        
#         # Create retriever with proper filter
#         retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
#         # Get relevant documents
#         docs = retriever.invoke(query)
        
#         if not docs:
#             print(f"⚠️ No documents found for repo: {repo_name}")
#             state["qa"] = [f"⚠️ No documentation found for repository '{repo_name}'"]
#             state["status"] = f"⚠️ No docs found for {repo_name}"
#             return state
        
#         print(f"📄 Found {len(docs)} relevant documents")
        
#         # Initialize LLM
#         llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_KEY,
#             temperature=0.3
#         )
        
#         # Create QA chain
#         qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=retriever,
#             return_source_documents=True
#         )
        
#         # Get answer
#         response = qa_chain.invoke({"query": query})
        
#         # Format response
#         answer = response.get("result", "No answer generated")
#         sources = response.get("source_documents", [])
        
#         # Create formatted output
#         formatted_answer = [
#             f"🤖 Answer: {answer}",
#             f"\n📚 Based on {len(sources)} document(s)"
#         ]
        
#         if sources:
#             formatted_answer.append("\n📄 Sources:")
#             for i, doc in enumerate(sources[:3], 1):
#                 source_file = doc.metadata.get("source_file", "Unknown")
#                 content_preview = doc.page_content[:150] + "..."
#                 formatted_answer.append(f"  {i}. {source_file}: {content_preview}")
        
#         state["qa"] = formatted_answer
#         state["qa_answer"] = answer
#         state["qa_sources"] = [doc.metadata for doc in sources]
#         state["status"] = f"✅ QA complete for repo: {repo_name}"
        
#         print(f"✅ QA completed successfully")

#     except Exception as e:
#         print(f"❌ Error during QA: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["qa"] = [f"❌ Error during QA: {str(e)}"]
#         state["status"] = f"❌ QA failed: {str(e)}"
    
#     return state





# # nodes/qa_node.py
# from langchain_groq import ChatGroq
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from config import GROQ_API_KEY


# def qa_node(state: dict) -> dict:
#     """
#     QA node with Qdrant filtering by repository name
#     """
#     print(f"\n{'='*60}")
#     print("💬 QA Node - Answering Query")
#     print(f"{'='*60}")
    
#     # Get query and repository
#     query = state.get("query", "")
#     selected_repo = state.get("selected_repo", "")
#     vectorstore = state.get("vectorstore")
    
#     if not query:
#         state["qa"] = ["⚠️  No query provided"]
#         return state
    
#     if not selected_repo:
#         state["qa"] = ["⚠️  No repository selected"]
#         return state
    
#     if not vectorstore:
#         state["qa"] = ["❌ Vectorstore not initialized"]
#         return state
    
#     print(f"📂 Repository: {selected_repo}")
#     print(f"❓ Query: {query}")
    
#     try:
#         # Create Qdrant filter for specific repository
#         search_kwargs = {
#             "k": 5,  # Top 5 most relevant chunks
#             "filter": Filter(
#                 must=[
#                     FieldCondition(
#                         key="metadata.repo_name",
#                         match=MatchValue(value=selected_repo)
#                     )
#                 ]
#             )
#         }
        
#         print(f"🔍 Searching with filter: repo_name='{selected_repo}'")
        
#         # Create retriever with filtering
#         retriever = vectorstore.as_retriever(
#             search_kwargs=search_kwargs
#         )
        
#         # Test retrieval
#         docs = retriever.get_relevant_documents(query)
#         print(f"📚 Found {len(docs)} relevant chunks")
        
#         if len(docs) == 0:
#             state["qa"] = [
#                 f"⚠️  No relevant information found in repository '{selected_repo}'",
#                 "Try rephrasing your question or check if the repository documentation was generated correctly."
#             ]
#             return state
        
#         # Initialize LLM
#         llm = ChatGroq(
#             model="llama-3.1-70b-versatile",
#             api_key=GROQ_API_KEY,
#             temperature=0.3
#         )
        
#         # Create custom prompt
#         prompt_template = """You are a helpful AI assistant that answers questions about GitHub repositories based on their documentation.

# Repository: {context}

# Question: {question}

# Instructions:
# - Answer the question based ONLY on the provided repository documentation
# - Be specific and cite relevant code/file names when applicable
# - If the documentation doesn't contain the answer, say so clearly
# - Keep your answer concise but complete

# Answer:"""

#         PROMPT = PromptTemplate(
#             template=prompt_template,
#             input_variables=["context", "question"]
#         )
        
#         # Create QA chain
#         qa_chain = RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type="stuff",
#             retriever=retriever,
#             chain_type_kwargs={"prompt": PROMPT},
#             return_source_documents=True
#         )
        
#         print(f"🤖 Generating answer...")
        
#         # Get answer
#         result = qa_chain.invoke({"query": query})
#         answer = result["result"]
#         source_docs = result["source_documents"]
        
#         # Format response
#         response_lines = [
#             f"📂 Repository: {selected_repo}",
#             f"",
#             f"💡 Answer:",
#             answer,
#             f"",
#             f"📚 Sources ({len(source_docs)} chunks used):"
#         ]
        
#         # Add source information
#         for i, doc in enumerate(source_docs, 1):
#             source_file = doc.metadata.get("source_file", "Unknown")
#             response_lines.append(f"  {i}. {source_file}")
        
#         state["qa"] = response_lines
#         print(f"✅ Answer generated successfully")
        
#     except Exception as e:
#         print(f"❌ Error during QA: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["qa"] = [
#             f"❌ Error processing query: {str(e)}",
#             "Please check the logs for details."
#         ]
    
#     print(f"{'='*60}\n")
#     return state


# def interactive_qa_loop(state: dict):
#     """
#     Interactive QA loop for user queries
#     """
#     from nodes.qa_utils import list_available_repos
    
#     available_repos = list_available_repos()
    
#     if not available_repos:
#         print("⚠️  No repositories available for QA")
#         return state
    
#     print(f"\n{'='*60}")
#     print("💬 Interactive QA Mode")
#     print(f"{'='*60}")
#     print(f"📚 Available repositories ({len(available_repos)}):")
#     for i, repo in enumerate(available_repos, 1):
#         print(f"  {i}. {repo}")
#     print(f"\nCommands:")
#     print(f"  - Type 'list' to see repositories")
#     print(f"  - Type 'exit' or 'quit' to stop")
#     print(f"{'='*60}\n")
    
#     while True:
#         try:
#             # Get repository
#             repo_name = input("📂 Enter repo name (or command): ").strip()
            
#             if repo_name.lower() in ['exit', 'quit']:
#                 print("\n👋 Goodbye!")
#                 break
            
#             if repo_name.lower() == 'list':
#                 print(f"\n📚 Available repositories:")
#                 for i, repo in enumerate(available_repos, 1):
#                     print(f"  {i}. {repo}")
#                 print()
#                 continue
            
#             if not repo_name:
#                 print("⚠️  Please enter a repository name\n")
#                 continue
            
#             if repo_name not in available_repos:
#                 print(f"⚠️  Repository '{repo_name}' not found")
#                 print(f"Available: {', '.join(available_repos)}\n")
#                 continue
            
#             # Get query
#             query = input(f"❓ Your question about '{repo_name}': ").strip()
            
#             if query.lower() in ['exit', 'quit']:
#                 print("\n👋 Goodbye!")
#                 break
            
#             if not query:
#                 print("⚠️  Please enter a question\n")
#                 continue
            
#             # Update state
#             state["selected_repo"] = repo_name
#             state["query"] = query
            
#             # Get answer
#             state = qa_node(state)
            
#             # Display answer
#             print(f"\n{'='*60}")
#             for line in state.get("qa", ["No answer found"]):
#                 print(line)
#             print(f"{'='*60}\n")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 Interrupted by user. Goodbye!")
#             break
#         except Exception as e:
#             print(f"\n❌ Error: {e}\n")
#             continue
    
#     return state




################# test 3 ########################################### nodes/qa_node.py
import os
import json
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config import GROQ_API_KEY, OUTPUT_LOG_DIR


def save_qa_log(repo_name, query, chunks, answer):
    """
    Save Q&A interaction to log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(OUTPUT_LOG_DIR, f"qa_log_{timestamp}.json")
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "repository": repo_name,
        "query": query,
        "retrieved_chunks": [
            {
                "chunk_id": i + 1,
                "content": chunk.page_content,
                "metadata": chunk.metadata
            }
            for i, chunk in enumerate(chunks)
        ],
        "answer": answer
    }
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Q&A log saved to: {log_file}")
    return log_file


def qa_node(state: dict) -> dict:
    """
    QA node with repository filtering and logging
    """
    print(f"\n{'='*60}")
    print("💬 QA Node - Answering Query")
    print(f"{'='*60}")
    
    query = state.get("query", "")
    selected_repo = state.get("selected_repo", "")
    vectorstore = state.get("vectorstore")
    
    if not query:
        state["qa"] = ["⚠️  No query provided"]
        return state
    
    if not selected_repo:
        state["qa"] = ["⚠️  No repository selected"]
        return state
    
    if not vectorstore:
        state["qa"] = ["❌ Vectorstore not initialized"]
        return state
    
    print(f"📂 Repository: {selected_repo}")
    print(f"❓ Query: {query}")
    
    try:
        # Create filter for specific repo
        search_kwargs = {
            "k": 5,
            "filter": Filter(
                must=[
                    FieldCondition(
                        key="metadata.repo_name",
                        match=MatchValue(value=selected_repo)
                    )
                ]
            )
        }
        
        print(f"🔍 Searching in repository: {selected_repo}")
        
        # Create retriever
        retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
        # Get relevant documents
        print(f"📚 Retrieving relevant chunks...")
        docs = retriever.get_relevant_documents(query)
        print(f"✅ Retrieved {len(docs)} chunks")
        
        if len(docs) == 0:
            state["qa"] = [
                f"⚠️  No relevant information found in '{selected_repo}'",
                "Try rephrasing your question."
            ]
            return state
        
        # Display retrieved chunks
        print(f"\n{'='*50}")
        print(f"📄 Retrieved Chunks:")
        print(f"{'='*50}")
        for i, doc in enumerate(docs, 1):
            print(f"\nChunk {i}:")
            print(f"Source: {doc.metadata.get('source_file', 'Unknown')}")
            print(f"Content preview: {doc.page_content[:200]}...")
        print(f"{'='*50}\n")
        
        # Initialize LLM
        print(f"🤖 Generating answer with LLM...")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0.3
        )
        
        # Create prompt
        prompt_template = """You are a helpful AI assistant for GitHub repositories.

Repository: {context}

Question: {question}

Instructions:
- Answer based ONLY on the provided documentation
- Be specific and cite file names when relevant
- If information is not in the docs, say so clearly
- Keep answer concise but complete

Answer:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        # Get answer
        result = qa_chain.invoke({"query": query})
        answer = result["result"]
        source_docs = result["source_documents"]
        
        print(f"✅ Answer generated")
        
        # Save to log file
        log_file = save_qa_log(selected_repo, query, source_docs, answer)
        
        # Format response
        response_lines = [
            f"📂 Repository: {selected_repo}",
            f"",
            f"💡 Answer:",
            answer,
            f"",
            f"📚 Sources ({len(source_docs)} chunks):"
        ]
        
        for i, doc in enumerate(source_docs, 1):
            source_file = doc.metadata.get("source_file", "Unknown")
            response_lines.append(f"  {i}. {source_file}")
        
        response_lines.append(f"")
        response_lines.append(f"💾 Log saved: {log_file}")
        
        state["qa"] = response_lines
        
    except Exception as e:
        print(f"❌ Error during QA: {e}")
        import traceback
        traceback.print_exc()
        
        state["qa"] = [f"❌ Error: {str(e)}"]
    
    print(f"{'='*60}\n")
    return state


def interactive_qa_loop(state: dict):
    """
    Interactive QA loop
    """
    from nodes.qa_utils import list_available_repos
    
    print(f"\n{'='*60}")
    print("💬 Interactive QA Mode")
    print(f"{'='*60}\n")
    
    # Get available repos
    available_repos = list_available_repos()
    
    if not available_repos:
        print("⚠️  No repositories available")
        return state
    
    print(f"📚 {len(available_repos)} repositories available")
    print(f"\nCommands:")
    print(f"  'list' - Show all repositories")
    print(f"  'exit' or 'quit' - Exit Q&A mode")
    print(f"{'='*60}\n")
    
    while True:
        try:
            # Get repository
            repo_name = input("📂 Enter repository name: ").strip()
            
            if repo_name.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!")
                break
            
            if repo_name.lower() == 'list':
                print(f"\n📚 Available repositories:")
                for i, repo in enumerate(available_repos, 1):
                    print(f"  {i}. {repo}")
                print()
                continue
            
            if not repo_name:
                print("⚠️  Please enter a repository name\n")
                continue
            
            if repo_name not in available_repos:
                print(f"⚠️  Repository '{repo_name}' not found")
                print(f"Use 'list' to see available repos\n")
                continue
            
            # Get query
            query = input(f"❓ Your question about '{repo_name}': ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                print("⚠️  Please enter a question\n")
                continue
            
            # Update state
            state["selected_repo"] = repo_name
            state["query"] = query
            
            # Get answer
            state = qa_node(state)
            
            # Display answer
            print(f"\n{'='*60}")
            print("📋 Answer:")
            print(f"{'='*60}")
            for line in state.get("qa", ["No answer found"]):
                print(line)
            print(f"{'='*60}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue
    
    return state