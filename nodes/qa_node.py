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




# ################# test 3 ########################################### nodes/qa_node.py
# import os
# import json
# from datetime import datetime
# from langchain_groq import ChatGroq
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from config import GROQ_API_KEY, OUTPUT_LOG_DIR


# def save_qa_log(repo_name, query, chunks, answer):
#     """
#     Save Q&A interaction to log file
#     """
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     log_file = os.path.join(OUTPUT_LOG_DIR, f"qa_log_{timestamp}.json")
    
#     log_data = {
#         "timestamp": datetime.now().isoformat(),
#         "repository": repo_name,
#         "query": query,
#         "retrieved_chunks": [
#             {
#                 "chunk_id": i + 1,
#                 "content": chunk.page_content,
#                 "metadata": chunk.metadata
#             }
#             for i, chunk in enumerate(chunks)
#         ],
#         "answer": answer
#     }
    
#     with open(log_file, 'w', encoding='utf-8') as f:
#         json.dump(log_data, f, indent=2, ensure_ascii=False)
    
#     print(f"💾 Q&A log saved to: {log_file}")
#     return log_file


# def qa_node(state: dict) -> dict:
#     """
#     QA node with repository filtering and logging
#     """
#     print(f"\n{'='*60}")
#     print("💬 QA Node - Answering Query")
#     print(f"{'='*60}")
    
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
#         # Create filter for specific repo
#         search_kwargs = {
#             "k": 5,
#             "filter": Filter(
#                 must=[
#                     FieldCondition(
#                         key="metadata.repo_name",
#                         match=MatchValue(value=selected_repo)
#                     )
#                 ]
#             )
#         }
        
#         print(f"🔍 Searching in repository: {selected_repo}")
        
#         # Create retriever
#         retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
#         # Get relevant documents
#         print(f"📚 Retrieving relevant chunks...")
#         docs = retriever.get_relevant_documents(query)
#         print(f"✅ Retrieved {len(docs)} chunks")
        
#         if len(docs) == 0:
#             state["qa"] = [
#                 f"⚠️  No relevant information found in '{selected_repo}'",
#                 "Try rephrasing your question."
#             ]
#             return state
        
#         # Display retrieved chunks
#         print(f"\n{'='*50}")
#         print(f"📄 Retrieved Chunks:")
#         print(f"{'='*50}")
#         for i, doc in enumerate(docs, 1):
#             print(f"\nChunk {i}:")
#             print(f"Source: {doc.metadata.get('source_file', 'Unknown')}")
#             print(f"Content preview: {doc.page_content[:200]}...")
#         print(f"{'='*50}\n")
        
#         # Initialize LLM
#         print(f"🤖 Generating answer with LLM...")
#         llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_KEY,
#             temperature=0.3
#         )
        
#         # Create prompt
#         prompt_template = """You are a helpful AI assistant for GitHub repositories.

# Repository: {context}

# Question: {question}

# Instructions:
# - Answer based ONLY on the provided documentation
# - Be specific and cite file names when relevant
# - If information is not in the docs, say so clearly
# - Keep answer concise but complete

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
        
#         # Get answer
#         result = qa_chain.invoke({"query": query})
#         answer = result["result"]
#         source_docs = result["source_documents"]
        
#         print(f"✅ Answer generated")
        
#         # Save to log file
#         log_file = save_qa_log(selected_repo, query, source_docs, answer)
        
#         # Format response
#         response_lines = [
#             f"📂 Repository: {selected_repo}",
#             f"",
#             f"💡 Answer:",
#             answer,
#             f"",
#             f"📚 Sources ({len(source_docs)} chunks):"
#         ]
        
#         for i, doc in enumerate(source_docs, 1):
#             source_file = doc.metadata.get("source_file", "Unknown")
#             response_lines.append(f"  {i}. {source_file}")
        
#         response_lines.append(f"")
#         response_lines.append(f"💾 Log saved: {log_file}")
        
#         state["qa"] = response_lines
        
#     except Exception as e:
#         print(f"❌ Error during QA: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["qa"] = [f"❌ Error: {str(e)}"]
    
#     print(f"{'='*60}\n")
#     return state


# def interactive_qa_loop(state: dict):
#     """
#     Interactive QA loop
#     """
#     from nodes.qa_utils import list_available_repos
    
#     print(f"\n{'='*60}")
#     print("💬 Interactive QA Mode")
#     print(f"{'='*60}\n")
    
#     # Get available repos
#     available_repos = list_available_repos()
    
#     if not available_repos:
#         print("⚠️  No repositories available")
#         return state
    
#     print(f"📚 {len(available_repos)} repositories available")
#     print(f"\nCommands:")
#     print(f"  'list' - Show all repositories")
#     print(f"  'exit' or 'quit' - Exit Q&A mode")
#     print(f"{'='*60}\n")
    
#     while True:
#         try:
#             # Get repository
#             repo_name = input("📂 Enter repository name: ").strip()
            
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
#                 print(f"Use 'list' to see available repos\n")
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
#             print("📋 Answer:")
#             print(f"{'='*60}")
#             for line in state.get("qa", ["No answer found"]):
#                 print(line)
#             print(f"{'='*60}\n")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 Interrupted. Goodbye!")
#             break
#         except Exception as e:
#             print(f"\n❌ Error: {e}\n")
#             continue
    
#     return state



################# Improved QA Node ##########################################
# nodes/qa_node.py
# import os
# import json
# from datetime import datetime
# from langchain_groq import ChatGroq
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from config import GROQ_API_KEY, OUTPUT_LOG_DIR


# def save_qa_log(repo_name, query, chunks, answer):
#     """
#     Save Q&A interaction to log file
#     """
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     log_file = os.path.join(OUTPUT_LOG_DIR, f"qa_log_{timestamp}.json")
    
#     log_data = {
#         "timestamp": datetime.now().isoformat(),
#         "repository": repo_name,
#         "query": query,
#         "retrieved_chunks": [
#             {
#                 "chunk_id": i + 1,
#                 "content": chunk.page_content,
#                 "metadata": chunk.metadata
#             }
#             for i, chunk in enumerate(chunks)
#         ],
#         "answer": answer
#     }
    
#     with open(log_file, 'w', encoding='utf-8') as f:
#         json.dump(log_data, f, indent=2, ensure_ascii=False)
    
#     print(f"💾 Q&A log saved to: {log_file}")
#     return log_file


# def qa_node(state: dict) -> dict:
#     """
#     QA node with repository filtering and logging
#     """
#     print(f"\n{'='*60}")
#     print("💬 QA Node - Answering Query")
#     print(f"{'='*60}")
    
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
#         # Create filter for specific repo
#         search_kwargs = {
#             "k": 5,
#             "filter": Filter(
#                 must=[
#                     FieldCondition(
#                         key="metadata.repo_name",
#                         match=MatchValue(value=selected_repo)
#                     )
#                 ]
#             )
#         }
        
#         print(f"🔍 Searching in repository: {selected_repo}")
        
#         # Create retriever
#         retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
#         # Get relevant documents
#         print(f"📚 Retrieving relevant chunks...")
#         docs = retriever.get_relevant_documents(query)
#         print(f"✅ Retrieved {len(docs)} chunks")
        
#         if len(docs) == 0:
#             state["qa"] = [
#                 f"⚠️  No relevant information found in '{selected_repo}'",
#                 "Try rephrasing your question."
#             ]
#             return state
        
#         # Display retrieved chunks
#         print(f"\n{'='*50}")
#         print(f"📄 Retrieved Chunks:")
#         print(f"{'='*50}")
#         for i, doc in enumerate(docs, 1):
#             print(f"\nChunk {i}:")
#             print(f"Source: {doc.metadata.get('source_file', 'Unknown')}")
#             print(f"Content preview: {doc.page_content[:200]}...")
#         print(f"{'='*50}\n")
        
#         # Initialize LLM
#         print(f"🤖 Generating answer with LLM...")
#         llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_KEY,
#             temperature=0.3
#         )
        
#         # Create prompt
#         prompt_template = """You are a helpful AI assistant for GitHub repositories.

# Repository: {context}

# Question: {question}

# Instructions:
# - Answer based ONLY on the provided documentation
# - Be specific and cite file names when relevant
# - If information is not in the docs, say so clearly
# - Keep answer concise but complete

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
        
#         # Get answer
#         result = qa_chain.invoke({"query": query})
#         answer = result["result"]
#         source_docs = result["source_documents"]
        
#         print(f"✅ Answer generated")
        
#         # Save to log file
#         log_file = save_qa_log(selected_repo, query, source_docs, answer)
        
#         # Format response
#         response_lines = [
#             f"📂 Repository: {selected_repo}",
#             f"",
#             f"💡 Answer:",
#             answer,
#             f"",
#             f"📚 Sources ({len(source_docs)} chunks):"
#         ]
        
#         for i, doc in enumerate(source_docs, 1):
#             source_file = doc.metadata.get("source_file", "Unknown")
#             response_lines.append(f"  {i}. {source_file}")
        
#         response_lines.append(f"")
#         response_lines.append(f"💾 Log saved: {log_file}")
        
#         state["qa"] = response_lines
        
#     except Exception as e:
#         print(f"❌ Error during QA: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["qa"] = [f"❌ Error: {str(e)}"]
    
#     print(f"{'='*60}\n")
#     return state


# def display_repo_list(available_repos):
#     """
#     Display formatted list of available repositories
#     """
#     print(f"\n{'='*60}")
#     print(f"📚 AVAILABLE REPOSITORIES ({len(available_repos)})")
#     print(f"{'='*60}")
#     for i, repo in enumerate(available_repos, 1):
#         print(f"  {i}. {repo}")
#     print(f"{'='*60}")


# def select_repository(available_repos):
#     """
#     Let user select a repository by number or name
#     Returns: (repo_name, should_exit)
#     """
#     while True:
#         print(f"\n💡 Options:")
#         print(f"   • Enter repo number (1-{len(available_repos)})")
#         print(f"   • Enter repo name directly")
#         print(f"   • Type 'list' to show repos again")
#         print(f"   • Type 'exit' or 'quit' to exit")
        
#         user_input = input(f"\n📂 Select repository: ").strip()
        
#         # Check for exit
#         if user_input.lower() in ['exit', 'quit', 'q']:
#             return None, True
        
#         # Show list again
#         if user_input.lower() == 'list':
#             display_repo_list(available_repos)
#             continue
        
#         # Empty input
#         if not user_input:
#             print("⚠️  Please enter a repository number or name")
#             continue
        
#         # Try as number
#         if user_input.isdigit():
#             repo_index = int(user_input) - 1
#             if 0 <= repo_index < len(available_repos):
#                 selected_repo = available_repos[repo_index]
#                 print(f"✅ Selected: {selected_repo}")
#                 return selected_repo, False
#             else:
#                 print(f"⚠️  Invalid number. Please enter 1-{len(available_repos)}")
#                 continue
        
#         # Try as name
#         if user_input in available_repos:
#             print(f"✅ Selected: {user_input}")
#             return user_input, False
#         else:
#             print(f"⚠️  Repository '{user_input}' not found")
#             print(f"💡 Type 'list' to see available repositories")
#             continue


# def qa_session_for_repo(state: dict, repo_name: str):
#     """
#     Run continuous Q&A session for a specific repository
#     """
#     print(f"\n{'='*60}")
#     print(f"💬 Q&A SESSION: {repo_name}")
#     print(f"{'='*60}")
#     print(f"🎯 Ask questions about '{repo_name}'")
#     print(f"💡 Type 'exit', 'quit', 'back', or 'change' to return to repo selection")
#     print(f"{'='*60}\n")
    
#     question_count = 0
    
#     while True:
#         try:
#             # Get question
#             query = input(f"\n❓ Your question (or 'exit'/'back' to change repo): ").strip()
            
#             # Check for exit commands
#             if query.lower() in ['exit', 'quit', 'q', 'back', 'change']:
#                 print(f"\n📊 Session summary: {question_count} questions answered")
#                 return False  # Return to repo selection
            
#             # Empty query
#             if not query:
#                 print("⚠️  Please enter a question")
#                 continue
            
#             # Update state and get answer
#             state["selected_repo"] = repo_name
#             state["query"] = query
            
#             # Get answer
#             state = qa_node(state)
            
#             # Display answer
#             print(f"\n{'='*60}")
#             print("📋 ANSWER:")
#             print(f"{'='*60}")
#             for line in state.get("qa", ["No answer found"]):
#                 print(line)
#             print(f"{'='*60}")
            
#             question_count += 1
            
#         except KeyboardInterrupt:
#             print(f"\n\n⚠️  Interrupted")
#             print(f"📊 Session summary: {question_count} questions answered")
#             return False
#         except Exception as e:
#             print(f"\n❌ Error: {e}")
#             import traceback
#             traceback.print_exc()
#             continue


# def interactive_qa_loop(state: dict):
#     """
#     Interactive QA loop with improved UX
#     """
#     from nodes.qa_utils import list_available_repos
    
#     print(f"\n{'='*70}")
#     print(f"{'='*70}")
#     print(f"  💬 INTERACTIVE Q&A MODE")
#     print(f"{'='*70}")
#     print(f"{'='*70}")
    
#     # Get available repos
#     available_repos = list_available_repos()
    
#     if not available_repos:
#         print("\n⚠️  No repositories available in the collection")
#         print("💡 Please index some repositories first")
#         return state
    
#     # Show initial repo list
#     display_repo_list(available_repos)
    
#     # Main loop
#     while True:
#         # Select repository
#         selected_repo, should_exit = select_repository(available_repos)
        
#         if should_exit:
#             print("\n👋 Exiting Q&A mode. Goodbye!")
#             break
        
#         # Run Q&A session for selected repo
#         should_continue = qa_session_for_repo(state, selected_repo)
        
#         # If user wants to exit completely
#         if not should_continue:
#             continue  # Go back to repo selection
    
#     return state



################# Improved QA Node ##########################################
# nodes/qa_node.py
# import os
# import json
# from datetime import datetime
# from langchain_groq import ChatGroq
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from config import GROQ_API_KEY, OUTPUT_LOG_DIR


# def save_qa_log(repo_name, query, chunks, answer):
#     """
#     Save Q&A interaction to log file
#     """
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     log_file = os.path.join(OUTPUT_LOG_DIR, f"qa_log_{timestamp}.json")
    
#     log_data = {
#         "timestamp": datetime.now().isoformat(),
#         "repository": repo_name,
#         "query": query,
#         "retrieved_chunks": [
#             {
#                 "chunk_id": i + 1,
#                 "content": chunk.page_content,
#                 "metadata": chunk.metadata
#             }
#             for i, chunk in enumerate(chunks)
#         ],
#         "answer": answer
#     }
    
#     with open(log_file, 'w', encoding='utf-8') as f:
#         json.dump(log_data, f, indent=2, ensure_ascii=False)
    
#     print(f"💾 Q&A log saved to: {log_file}")
#     return log_file


# def qa_node(state: dict) -> dict:
#     """
#     QA node with repository filtering and logging
#     """
#     print(f"\n{'='*60}")
#     print("💬 QA Node - Answering Query")
#     print(f"{'='*60}")
    
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
#         # Create filter for specific repo
#         search_kwargs = {
#             "k": 5,
#             "filter": Filter(
#                 must=[
#                     FieldCondition(
#                         key="metadata.repo_name",
#                         match=MatchValue(value=selected_repo)
#                     )
#                 ]
#             )
#         }
        
#         print(f"🔍 Searching in repository: {selected_repo}")
        
#         # Create retriever
#         retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
#         # Get relevant documents
#         print(f"📚 Retrieving relevant chunks...")
#         docs = retriever.get_relevant_documents(query)
#         print(f"✅ Retrieved {len(docs)} chunks")
        
#         if len(docs) == 0:
#             state["qa"] = [
#                 f"⚠️  No relevant information found in '{selected_repo}'",
#                 "Try rephrasing your question."
#             ]
#             return state
        
#         # Display retrieved chunks
#         print(f"\n{'='*50}")
#         print(f"📄 Retrieved Chunks:")
#         print(f"{'='*50}")
#         for i, doc in enumerate(docs, 1):
#             print(f"\nChunk {i}:")
#             print(f"Source: {doc.metadata.get('source_file', 'Unknown')}")
#             print(f"Content preview: {doc.page_content[:200]}...")
#         print(f"{'='*50}\n")
        
#         # Initialize LLM
#         print(f"🤖 Generating answer with LLM...")
#         llm = ChatGroq(
#             model="llama-3.3-70b-versatile",
#             api_key=GROQ_API_KEY,
#             temperature=0.3
#         )
        
#         # Create prompt
#         prompt_template = """You are a helpful AI assistant for GitHub repositories.

# Repository: {context}

# Question: {question}

# Instructions:
# - Answer based ONLY on the provided documentation
# - Be specific and cite file names when relevant
# - If information is not in the docs, say so clearly
# - Keep answer concise but complete

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
        
#         # Get answer
#         result = qa_chain.invoke({"query": query})
#         answer = result["result"]
#         source_docs = result["source_documents"]
        
#         print(f"✅ Answer generated")
        
#         # Save to log file
#         log_file = save_qa_log(selected_repo, query, source_docs, answer)
        
#         # Format response
#         response_lines = [
#             f"📂 Repository: {selected_repo}",
#             f"",
#             f"💡 Answer:",
#             answer,
#             f"",
#             f"📚 Sources ({len(source_docs)} chunks):"
#         ]
        
#         for i, doc in enumerate(source_docs, 1):
#             source_file = doc.metadata.get("source_file", "Unknown")
#             response_lines.append(f"  {i}. {source_file}")
        
#         response_lines.append(f"")
#         response_lines.append(f"💾 Log saved: {log_file}")
        
#         state["qa"] = response_lines
        
#     except Exception as e:
#         print(f"❌ Error during QA: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["qa"] = [f"❌ Error: {str(e)}"]
    
#     print(f"{'='*60}\n")
#     return state


# def display_repo_list(available_repos):
#     """
#     Display formatted list of available repositories
#     """
#     print(f"\n{'='*60}")
#     print(f"📚 AVAILABLE REPOSITORIES ({len(available_repos)})")
#     print(f"{'='*60}")
#     for i, repo in enumerate(available_repos, 1):
#         print(f"  {i}. {repo}")
#     print(f"{'='*60}")


# def select_repository(available_repos):
#     """
#     Let user select a repository by number or name
#     Returns: (repo_name, should_exit)
#     """
#     while True:
#         print(f"\n💡 Options:")
#         print(f"   • Enter repo number (1-{len(available_repos)})")
#         print(f"   • Enter repo name directly")
#         print(f"   • Type 'list' to show repos again")
#         print(f"   • Type 'exit' or 'quit' to exit")
        
#         user_input = input(f"\n📂 Select repository: ").strip()
        
#         # Check for exit
#         if user_input.lower() in ['exit', 'quit', 'q']:
#             return None, True
        
#         # Show list again
#         if user_input.lower() == 'list':
#             display_repo_list(available_repos)
#             continue
        
#         # Empty input
#         if not user_input:
#             print("⚠️  Please enter a repository number or name")
#             continue
        
#         # Try as number
#         if user_input.isdigit():
#             repo_index = int(user_input) - 1
#             if 0 <= repo_index < len(available_repos):
#                 selected_repo = available_repos[repo_index]
#                 print(f"✅ Selected: {selected_repo}")
#                 return selected_repo, False
#             else:
#                 print(f"⚠️  Invalid number. Please enter 1-{len(available_repos)}")
#                 continue
        
#         # Try as name
#         if user_input in available_repos:
#             print(f"✅ Selected: {user_input}")
#             return user_input, False
#         else:
#             print(f"⚠️  Repository '{user_input}' not found")
#             print(f"💡 Type 'list' to see available repositories")
#             continue


# def qa_session_for_repo(state: dict, repo_name: str):
#     """
#     Run continuous Q&A session for a specific repository
#     """
#     print(f"\n{'='*60}")
#     print(f"💬 Q&A SESSION: {repo_name}")
#     print(f"{'='*60}")
#     print(f"🎯 Ask questions about '{repo_name}'")
#     print(f"💡 Type 'exit', 'quit', 'back', or 'change' to return to repo selection")
#     print(f"{'='*60}\n")
    
#     question_count = 0
    
#     while True:
#         try:
#             # Get question
#             query = input(f"\n❓ Your question (or 'exit'/'back' to change repo): ").strip()
            
#             # Check for exit commands
#             if query.lower() in ['exit', 'quit', 'q', 'back', 'change']:
#                 print(f"\n📊 Session summary: {question_count} questions answered")
#                 return False  # Return to repo selection
            
#             # Empty query
#             if not query:
#                 print("⚠️  Please enter a question")
#                 continue
            
#             # Update state and get answer
#             state["selected_repo"] = repo_name
#             state["query"] = query
            
#             # Get answer
#             state = qa_node(state)
            
#             # Display answer
#             print(f"\n{'='*60}")
#             print("📋 ANSWER:")
#             print(f"{'='*60}")
#             for line in state.get("qa", ["No answer found"]):
#                 print(line)
#             print(f"{'='*60}")
            
#             question_count += 1
            
#         except KeyboardInterrupt:
#             print(f"\n\n⚠️  Interrupted")
#             print(f"📊 Session summary: {question_count} questions answered")
#             return False
#         except Exception as e:
#             print(f"\n❌ Error: {e}")
#             import traceback
#             traceback.print_exc()
#             continue


# def interactive_qa_loop(state: dict):
#     """
#     Interactive QA loop with improved UX
#     """
#     from nodes.qa_utils import list_available_repos
    
#     print(f"\n{'='*70}")
#     print(f"{'='*70}")
#     print(f"  💬 INTERACTIVE Q&A MODE")
#     print(f"{'='*70}")
#     print(f"{'='*70}")
    
#     # Get available repos
#     available_repos = list_available_repos()
    
#     if not available_repos:
#         print("\n⚠️  No repositories available in the collection")
#         print("💡 Please index some repositories first")
#         return state
    
#     # Show initial repo list
#     display_repo_list(available_repos)
    
#     # Main loop
#     while True:
#         # Select repository
#         selected_repo, should_exit = select_repository(available_repos)
        
#         if should_exit:
#             print("\n👋 Exiting Q&A mode. Goodbye!")
#             break
        
#         # Run Q&A session for selected repo
#         should_continue = qa_session_for_repo(state, selected_repo)
        
#         # If user wants to exit completely
#         if not should_continue:
#             continue  # Go back to repo selection
    
#     return state





















"""
QA Node Module
~~~~~~~~~~~~~~
Handles question-answering operations with repository filtering and logging.

This module provides:
- Interactive Q&A sessions for GitHub repositories
- Repository selection and management
- Answer generation using LLM with RAG
- Logging and audit trail of Q&A interactions
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config import GROQ_API_KEY, OUTPUT_LOG_DIR


# ============================================================================
# Constants
# ============================================================================

QA_PROMPT_TEMPLATE = """You are a helpful AI assistant for GitHub repositories.

Repository: {context}

Question: {question}

Instructions:
- Answer based ONLY on the provided documentation
- Be specific and cite file names when relevant
- If information is not in the docs, say so clearly
- Keep answer concise but complete

Answer:"""

EXIT_COMMANDS = ['exit', 'quit', 'q', 'back', 'change']
LIST_COMMAND = 'list'

# Visual separators
SEPARATOR_THICK = "=" * 70
SEPARATOR_THIN = "-" * 70


# ============================================================================
# Logging Functions
# ============================================================================

def save_qa_log(repo_name: str, query: str, chunks: List, answer: str) -> str:
    """
    Save Q&A interaction to a timestamped JSON log file.
    
    Args:
        repo_name: Name of the repository
        query: User's question
        chunks: Retrieved document chunks
        answer: Generated answer
        
    Returns:
        Path to the saved log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(OUTPUT_LOG_DIR, f"qa_log_{timestamp}.json")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_LOG_DIR, exist_ok=True)
    
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
    
    print(f"💾 Log saved: {log_file}")
    return log_file


# ============================================================================
# Core QA Functions
# ============================================================================

def qa_node(state: Dict) -> Dict:
    """
    Execute Q&A operation with repository filtering.
    
    This function:
    1. Validates input state
    2. Retrieves relevant documents from vector store
    3. Generates answer using LLM
    4. Logs the interaction
    5. Updates state with results
    
    Args:
        state: Dictionary containing:
            - query: User's question
            - selected_repo: Repository name
            - vectorstore: Initialized vector store
            
    Returns:
        Updated state dictionary with 'qa' field containing formatted response
    """
    print(f"\n{SEPARATOR_THICK}")
    print("💬 QA NODE - ANSWERING QUERY")
    print(SEPARATOR_THICK)
    
    # Extract and validate inputs
    query = state.get("query", "").strip()
    selected_repo = state.get("selected_repo", "").strip()
    vectorstore = state.get("vectorstore")
    
    # Input validation
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
    print(f"❓ Query: {query[:100]}{'...' if len(query) > 100 else ''}")
    
    try:
        # Retrieve and generate answer
        source_docs = _retrieve_documents(vectorstore, selected_repo, query)
        
        if not source_docs:
            state["qa"] = [
                f"⚠️  No relevant information found in '{selected_repo}'",
                "💡 Try rephrasing your question or check if the repository is properly indexed."
            ]
            return state
        
        # Generate answer using LLM
        answer = _generate_answer(vectorstore, selected_repo, query, source_docs)
        
        # Save interaction log
        log_file = save_qa_log(selected_repo, query, source_docs, answer)
        
        # Format response
        state["qa"] = _format_response(selected_repo, answer, source_docs, log_file)
        
    except Exception as e:
        print(f"❌ Error during QA: {e}")
        import traceback
        traceback.print_exc()
        state["qa"] = [
            f"❌ Error occurred: {str(e)}",
            "💡 Please try again or contact support if the issue persists."
        ]
    
    print(f"{SEPARATOR_THICK}\n")
    return state


def _retrieve_documents(vectorstore, repo_name: str, query: str) -> List:
    """
    Retrieve relevant documents from vector store with repository filtering.
    
    Args:
        vectorstore: Initialized vector store
        repo_name: Repository to search in
        query: Search query
        
    Returns:
        List of retrieved documents
    """
    search_kwargs = {
        "k": 5,
        "filter": Filter(
            must=[
                FieldCondition(
                    key="metadata.repo_name",
                    match=MatchValue(value=repo_name)
                )
            ]
        )
    }
    
    print(f"🔍 Searching in repository: {repo_name}")
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    print(f"📚 Retrieving relevant chunks...")
    docs = retriever.get_relevant_documents(query)
    print(f"✅ Retrieved {len(docs)} chunks")
    
    # Display retrieved chunks preview
    if docs:
        print(f"\n{SEPARATOR_THIN}")
        print(f"📄 RETRIEVED CHUNKS PREVIEW")
        print(SEPARATOR_THIN)
        for i, doc in enumerate(docs[:3], 1):  # Show first 3
            source = doc.metadata.get('source_file', 'Unknown')
            preview = doc.page_content[:150].replace('\n', ' ')
            print(f"{i}. {source}")
            print(f"   {preview}...")
        if len(docs) > 3:
            print(f"   ... and {len(docs) - 3} more chunks")
        print(SEPARATOR_THIN)
    
    return docs


def _generate_answer(vectorstore, repo_name: str, query: str, docs: List) -> str:
    """
    Generate answer using LLM with retrieved documents.
    
    Args:
        vectorstore: Initialized vector store
        repo_name: Repository name
        query: User's question
        docs: Retrieved documents
        
    Returns:
        Generated answer string
    """
    print(f"🤖 Generating answer with LLM...")
    
    # Initialize LLM
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.3
    )
    
    # Create prompt
    PROMPT = PromptTemplate(
        template=QA_PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    # Create retriever with repo filter
    search_kwargs = {
        "k": 5,
        "filter": Filter(
            must=[
                FieldCondition(
                    key="metadata.repo_name",
                    match=MatchValue(value=repo_name)
                )
            ]
        )
    }
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    # Create QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    
    # Generate answer
    result = qa_chain.invoke({"query": query})
    print(f"✅ Answer generated successfully")
    
    return result["result"]


def _format_response(repo_name: str, answer: str, docs: List, log_file: str) -> List[str]:
    """
    Format Q&A response for display.
    
    Args:
        repo_name: Repository name
        answer: Generated answer
        docs: Source documents
        log_file: Path to log file
        
    Returns:
        List of formatted response lines
    """
    response_lines = [
        f"📂 Repository: {repo_name}",
        "",
        "💡 ANSWER:",
        SEPARATOR_THIN,
        answer,
        SEPARATOR_THIN,
        "",
        f"📚 SOURCES ({len(docs)} chunks retrieved):"
    ]
    
    for i, doc in enumerate(docs, 1):
        source_file = doc.metadata.get("source_file", "Unknown")
        response_lines.append(f"  {i}. {source_file}")
    
    response_lines.extend([
        "",
        f"💾 Interaction logged to: {os.path.basename(log_file)}"
    ])
    
    return response_lines


# ============================================================================
# UI Display Functions
# ============================================================================

def display_repo_list(available_repos: List[str]) -> None:
    """
    Display formatted list of available repositories.
    
    Args:
        available_repos: List of repository names
    """
    print(f"\n{SEPARATOR_THICK}")
    print(f"📚 AVAILABLE REPOSITORIES ({len(available_repos)})")
    print(SEPARATOR_THICK)
    
    for i, repo in enumerate(available_repos, 1):
        print(f"  {i:2d}. {repo}")
    
    print(SEPARATOR_THICK)


def display_welcome_banner() -> None:
    """Display welcome banner for interactive Q&A mode."""
    print(f"\n{SEPARATOR_THICK}")
    print(f"{SEPARATOR_THICK}")
    print(f"  💬 INTERACTIVE Q&A MODE")
    print(f"  Ask questions about your GitHub repositories")
    print(f"{SEPARATOR_THICK}")
    print(f"{SEPARATOR_THICK}")


def display_commands_help() -> None:
    """Display available commands help."""
    print(f"\n💡 AVAILABLE COMMANDS:")
    print(f"   • Enter number (1-N) to select repository")
    print(f"   • Type repository name directly")
    print(f"   • 'list' - Show repositories again")
    print(f"   • 'exit', 'quit', 'q' - Exit the program")


# ============================================================================
# Repository Selection
# ============================================================================

def select_repository(available_repos: List[str]) -> Tuple[Optional[str], bool]:
    """
    Let user select a repository by number or name.
    
    Args:
        available_repos: List of available repository names
        
    Returns:
        Tuple of (selected_repo_name, should_exit)
        - selected_repo_name: Name of selected repository or None
        - should_exit: True if user wants to exit
    """
    while True:
        display_commands_help()
        
        user_input = input(f"\n📂 Select repository: ").strip()
        
        # Handle exit commands
        if user_input.lower() in ['exit', 'quit', 'q']:
            return None, True
        
        # Handle list command
        if user_input.lower() == LIST_COMMAND:
            display_repo_list(available_repos)
            continue
        
        # Validate empty input
        if not user_input:
            print("⚠️  Please enter a repository number or name")
            continue
        
        # Try selection by number
        if user_input.isdigit():
            repo_index = int(user_input) - 1
            if 0 <= repo_index < len(available_repos):
                selected_repo = available_repos[repo_index]
                print(f"✅ Selected: {selected_repo}\n")
                return selected_repo, False
            else:
                print(f"⚠️  Invalid number. Please enter 1-{len(available_repos)}")
                continue
        
        # Try selection by name
        if user_input in available_repos:
            print(f"✅ Selected: {user_input}\n")
            return user_input, False
        
        # Repository not found
        print(f"⚠️  Repository '{user_input}' not found")
        print(f"💡 Type 'list' to see available repositories")


# ============================================================================
# Q&A Session Management
# ============================================================================

def qa_session_for_repo(state: Dict, repo_name: str) -> bool:
    """
    Run continuous Q&A session for a specific repository.
    
    Args:
        state: Application state dictionary
        repo_name: Name of the repository for Q&A
        
    Returns:
        False to return to repo selection, True to exit completely
    """
    print(f"\n{SEPARATOR_THICK}")
    print(f"💬 Q&A SESSION: {repo_name}")
    print(SEPARATOR_THICK)
    print(f"🎯 Ask questions about '{repo_name}'")
    print(f"💡 Commands: 'exit', 'quit', 'back', 'change' - Return to repo selection")
    print(SEPARATOR_THICK)
    
    question_count = 0
    
    while True:
        try:
            # Get question from user
            query = input(f"\n❓ Your question: ").strip()
            
            # Handle exit commands
            if query.lower() in EXIT_COMMANDS:
                print(f"\n📊 Session Summary: {question_count} questions answered")
                print(f"🔙 Returning to repository selection...")
                return False
            
            # Validate query
            if not query:
                print("⚠️  Please enter a question")
                continue
            
            # Update state and get answer
            state["selected_repo"] = repo_name
            state["query"] = query
            
            # Execute Q&A
            state = qa_node(state)
            
            # Display answer
            print(f"\n{SEPARATOR_THICK}")
            print("📋 ANSWER:")
            print(SEPARATOR_THICK)
            for line in state.get("qa", ["⚠️ No answer generated"]):
                print(line)
            print(SEPARATOR_THICK)
            
            question_count += 1
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Session interrupted (Ctrl+C)")
            print(f"📊 Session Summary: {question_count} questions answered")
            return False
            
        except Exception as e:
            print(f"\n❌ Error during Q&A: {e}")
            print(f"💡 Please try again with a different question")
            continue


# ============================================================================
# Main Interactive Loop
# ============================================================================

def interactive_qa_loop(state: Dict) -> Dict:
    """
    Main interactive Q&A loop with repository selection.
    
    This function orchestrates the entire Q&A experience:
    1. Displays available repositories
    2. Lets user select a repository
    3. Runs Q&A session for selected repository
    4. Returns to selection or exits based on user choice
    
    Args:
        state: Application state dictionary
        
    Returns:
        Updated state dictionary
    """
    from nodes.qa_utils import list_available_repos
    
    # Display welcome banner
    display_welcome_banner()
    
    # Get available repositories
    print("🔄 Loading repositories from vector store...")
    available_repos = list_available_repos()
    
    # Validate repositories exist
    if not available_repos:
        print(f"\n{SEPARATOR_THICK}")
        print("⚠️  NO REPOSITORIES AVAILABLE")
        print(SEPARATOR_THICK)
        print("No repositories found in the collection.")
        print("💡 Please index some repositories first before using Q&A.")
        print(SEPARATOR_THICK)
        return state
    
    print(f"✅ Loaded {len(available_repos)} repositories\n")
    
    # Display initial repository list
    display_repo_list(available_repos)
    
    # Main interaction loop
    while True:
        # Step 1: Select repository
        selected_repo, should_exit = select_repository(available_repos)
        
        if should_exit:
            print(f"\n{SEPARATOR_THICK}")
            print("👋 Thank you for using Interactive Q&A!")
            print(SEPARATOR_THICK)
            break
        
        # Step 2: Run Q&A session for selected repository
        qa_session_for_repo(state, selected_repo)
        
        # Loop continues to repository selection
    
    return state


# ============================================================================
# Module Entry Point
# ============================================================================

if __name__ == "__main__":
    print("This module should be imported, not run directly.")
    print("Use: from nodes.qa_node import interactive_qa_loop")