# from graph import build_graph

# if __name__ == "__main__":
#     graph = build_graph()
#     state = {}
#     result = graph.invoke(state)
#     print("\n✅ Pipeline Finished:")
#     print(result)


############# 2nd test 

# from graph import build_graph

# if __name__ == "__main__":
#     print("="*50)
#     print("👋 Starting GitHub LangGraph Chatbot...")
#     print("="*50)

#     graph = build_graph()

#     # Run pipeline once to prepare repos + embeddings
#     state = {}
#     state = graph.invoke(state)

#     print("\n✅ Embedding pipeline complete. Repos ready for QnA.")
#     print("Type 'exit' anytime to quit.\n")

#     while True:
#         repo_name = input("🔹 Enter repo name for QnA (or 'exit' to quit): ")
#         if repo_name.lower().strip() == "exit":
#             print("👋 Stopping chatbot...")
#             break

#         query = input(f"💬 Your question about {repo_name}: ")
#         if query.lower().strip() == "exit":
#             print("👋 Stopping chatbot...")
#             break

#         # Pass user selection + query into graph
#         state["selected_repo"] = repo_name
#         state["query"] = query

#         try:
#             state = graph.invoke(state)
#             print("🤖 Answer:", state.get("qa", "No answer found"))
#             print("=" * 50)
#         except Exception as e:
#             print(f"❌ Error: {e}")



# ################## 3rd test

# from graph import build_graph

# if __name__ == "__main__":
#     graph = build_graph()

#     # Step 1: run pipeline until embeddings
#     state = {}
#     state = graph.invoke(state)   # this should NOT call qa_node yet
#     print("✅ Embeddings ready.")

#     # Step 2: chat loop
#     while True:
#         repo_name = input("\n📂 Enter repo name (or 'exit' to quit): ").strip()
#         if repo_name.lower() == "exit":
#             break
#         query = input("💬 Your question: ").strip()

#         state["selected_repo"] = repo_name
#         state["query"] = query

#         # run only qa node instead of entire graph
#         from nodes.qa_node import qa_node
#         state = qa_node(state)

#         print("\n🤖 Answer:")
#         for i, ans in enumerate(state.get("qa", []), 1):
#             print(f"{i}. {ans[:300]}...")





# # main.py
# from graph import build_graph
# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams, PointStruct
# from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
# import os

# def list_available_repos():
#     """
#     List all available repositories from Qdrant collection
#     """
#     try:
#         client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
#         # Check if collection exists
#         collections = client.get_collections().collections
#         collection_names = [col.name for col in collections]
        
#         if COLLECTION_NAME not in collection_names:
#             print(f"⚠️ Collection '{COLLECTION_NAME}' not found")
#             return []
        
#         # Get collection info
#         collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        
#         if collection_info.vectors_count == 0:
#             print("⚠️ Collection is empty. Run pipeline first.")
#             return []
        
#         # Scroll through collection to get unique repo names
#         records, _ = client.scroll(
#             collection_name=COLLECTION_NAME,
#             limit=100,
#             with_payload=True,
#             with_vectors=False
#         )
        
#         # Extract unique repo names
#         repo_names = set()
#         for record in records:
#             if record.payload and "metadata" in record.payload:
#                 repo_name = record.payload["metadata"].get("repo_name")
#                 if repo_name:
#                     repo_names.add(repo_name)
        
#         return sorted(list(repo_names))
        
#     except Exception as e:
#         print(f"❌ Error listing repos: {e}")
#         return []


# def display_banner():
#     """Display welcome banner"""
#     print("\n" + "="*60)
#     print("🤖 GitHub Repository Documentation QA System")
#     print("="*60)
#     print("📦 Vector Store: Qdrant Cloud")
#     print(f"🗄️ Collection: {COLLECTION_NAME}")
#     print("="*60 + "\n")


# if __name__ == "__main__":
#     display_banner()
    
#     try:
#         graph = build_graph()
        
#         # Step 1: Run pipeline until embeddings are ready
#         print("🚀 Starting pipeline...")
#         print("This will:")
#         print("  1. Download GitHub repositories")
#         print("  2. Generate documentation")
#         print("  3. Create embeddings in Qdrant Cloud")
#         print("\nThis may take a few minutes...\n")
        
#         state = {}
#         state = graph.invoke(state)
        
#         print("\n" + "="*60)
#         print("✅ Pipeline completed!")
#         print("="*60)
#         print(f"Status: {state.get('status', 'Unknown')}")
#         if state.get('total_chunks'):
#             print(f"Total chunks embedded: {state['total_chunks']}")
#         print("="*60 + "\n")
        
#         # Check if embeddings were created successfully
#         if not state.get("vectorstore"):
#             print("❌ No vectorstore created. Please check the logs above.")
#             exit(1)
        
#         # List available repositories
#         print("📚 Fetching available repositories from Qdrant...")
#         available_repos = list_available_repos()
        
#         if not available_repos:
#             print("⚠️ No repositories found in the collection.")
#             print("Please make sure the pipeline ran successfully.")
#             exit(1)
        
#         print(f"\n✅ Found {len(available_repos)} repositories:")
#         for i, repo in enumerate(available_repos, 1):
#             print(f"  {i}. {repo}")
#         print()
        
#         # Step 2: Interactive chat loop
#         print("="*60)
#         print("💬 Interactive QA Mode")
#         print("="*60)
#         print("Commands:")
#         print("  - Type 'list' to see available repositories")
#         print("  - Type 'exit' or 'quit' to stop")
#         print("="*60 + "\n")
        
#         while True:
#             try:
#                 # Get repository name
#                 repo_name = input("📂 Enter repo name (or command): ").strip()
                
#                 if repo_name.lower() in ['exit', 'quit']:
#                     print("\n👋 Goodbye!")
#                     break
                
#                 if repo_name.lower() == 'list':
#                     print("\n📚 Available repositories:")
#                     for i, repo in enumerate(available_repos, 1):
#                         print(f"  {i}. {repo}")
#                     print()
#                     continue
                
#                 if not repo_name:
#                     print("⚠️ Please enter a repository name\n")
#                     continue
                
#                 # Validate repo exists
#                 if repo_name not in available_repos:
#                     print(f"⚠️ Repository '{repo_name}' not found.")
#                     print(f"Available repos: {', '.join(available_repos)}\n")
#                     continue
                
#                 # Get query
#                 query = input(f"💬 Your question about '{repo_name}': ").strip()
                
#                 if query.lower() in ['exit', 'quit']:
#                     print("\n👋 Goodbye!")
#                     break
                
#                 if not query:
#                     print("⚠️ Please enter a question\n")
#                     continue
                
#                 # Update state with user input
#                 state["selected_repo"] = repo_name
#                 state["query"] = query
                
#                 # Run QA node
#                 print("\n🔍 Searching documentation...")
#                 from nodes.qa_node import qa_node
#                 state = qa_node(state)
                
#                 # Display answer
#                 print("\n" + "="*60)
#                 qa_response = state.get("qa", ["No answer found"])
#                 for line in qa_response:
#                     print(line)
#                 print("="*60 + "\n")
                
#             except KeyboardInterrupt:
#                 print("\n\n👋 Interrupted by user. Goodbye!")
#                 break
#             except Exception as e:
#                 print(f"\n❌ Error: {e}\n")
#                 continue
    
#     except KeyboardInterrupt:
#         print("\n\n👋 Interrupted by user. Goodbye!")
#     except Exception as e:
#         print(f"\n❌ Fatal error: {e}")
#         import traceback
#         traceback.print_exc()













# # main.py
# from graph import build_graph
# from nodes.qa_utils import list_available_repos, get_collection_stats
# from nodes.qa_node import interactive_qa_loop
# from config import COLLECTION_NAME
# import sys


# def display_banner():
#     """Display welcome banner"""
#     print("\n" + "="*60)
#     print("🤖 GitHub Repository Documentation QA System")
#     print("="*60)
#     print("☁️  Vector Store: Qdrant Cloud")
#     print(f"📦 Collection: {COLLECTION_NAME}")
#     print("="*60 + "\n")


# def check_collection_status():
#     """Check if Qdrant collection exists and has data"""
#     stats = get_collection_stats()
    
#     if not stats.get("exists"):
#         print("⚠️  Qdrant collection not found or empty")
#         print("Running the full pipeline...\n")
#         return False
    
#     print(f"✅ Qdrant collection exists")
#     print(f"📊 Vectors count: {stats['vectors_count']}")
    
#     if stats['vectors_count'] == 0:
#         print("⚠️  Collection is empty")
#         return False
    
#     return True


# def run_pipeline():
#     """Run the full pipeline"""
#     print("\n" + "="*60)
#     print("🚀 Starting Full Pipeline")
#     print("="*60)
#     print("This will:")
#     print("  1. ⬇️  Download GitHub repositories")
#     print("  2. 📝 Generate documentation")
#     print("  3. ☁️  Create embeddings in Qdrant Cloud")
#     print("  4. 💾 Save chunks locally")
#     print("\nThis may take several minutes...")
#     print("="*60 + "\n")
    
#     try:
#         graph = build_graph()
#         state = {}
#         state = graph.invoke(state)
        
#         print("\n" + "="*60)
#         print("✅ Pipeline Completed Successfully")
#         print("="*60)
#         print(f"Status: {state.get('status', 'Unknown')}")
#         if state.get('total_chunks'):
#             print(f"Total chunks: {state['total_chunks']}")
#         if state.get('vectors_in_cloud'):
#             print(f"Vectors in Qdrant: {state['vectors_in_cloud']}")
#         print("="*60 + "\n")
        
#         return state
        
#     except Exception as e:
#         print(f"\n❌ Pipeline failed: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# def main():
#     """Main entry point"""
#     display_banner()
    
#     try:
#         # Check if we need to run the pipeline
#         collection_exists = check_collection_status()
        
#         if not collection_exists:
#             # Run full pipeline
#             state = run_pipeline()
            
#             if not state or not state.get("vectorstore"):
#                 print("❌ Pipeline failed. Cannot proceed to QA.")
#                 return
#         else:
#             # Collection exists, just connect to it
#             print("✅ Using existing Qdrant collection")
#             print("⏩ Skipping pipeline, going directly to QA\n")
            
#             from nodes.create_embeddings import create_embeddings_node
#             state = {}
#             # This will just connect to existing collection without recreating
#             state = create_embeddings_node(state)
        
#         # Check collection one more time
#         stats = get_collection_stats()
#         print("="*60 + "\n")
#         print(f"vectors_count: {stats.get("vectors_count")}")
#         print("="*60 + "\n")
#         if not stats.get("exists") or stats.get("vectors_count", 0) == 0:
#             print("❌ No data in Qdrant collection. Cannot proceed.")
#             return
        
#         # List available repositories
#         print("="*60)
#         print("📚 Fetching Available Repositories")
#         print("="*60)
        
#         available_repos = list_available_repos()
        
#         if not available_repos:
#             print("⚠️  No repositories found in the collection")
#             print("Please run the pipeline first.")
#             return
        
#         print(f"\n✅ Found {len(available_repos)} repositories:\n")
#         for i, repo in enumerate(available_repos, 1):
#             print(f"  {i}. {repo}")
#         print()
        
#         # Start interactive QA
#         state = interactive_qa_loop(state)
        
#     except KeyboardInterrupt:
#         print("\n\n👋 Interrupted by user. Goodbye!")
#     except Exception as e:
#         print(f"\n❌ Fatal error: {e}")
#         import traceback
#         traceback.print_exc()


# if __name__ == "__main__":
#     main()







 #############  test 3 ############################
# main.py
from graph import build_graph
from nodes.qa_utils import get_collection_stats, list_available_repos
from nodes.qa_node import interactive_qa_loop
from nodes.create_embeddings import create_embeddings_node
from config import COLLECTION_NAME


def display_banner():
    """Display welcome banner"""
    print("\n" + "="*60)
    print("🤖 GitHub Repository Documentation QA System")
    print("="*60)
    print(f"📦 Collection: {COLLECTION_NAME}")
    print("="*60 + "\n")


def run_full_pipeline():
    """Run the complete pipeline"""
    print(f"\n{'='*60}")
    print("🚀 Running Full Pipeline")
    print(f"{'='*60}")
    print("Steps:")
    print("  1. ⬇️  Download/sync GitHub repositories")
    print("  2. 📝 Generate documentation")
    print("  3. ✂️  Create text chunks")
    print("  4. ☁️  Upload embeddings to Qdrant")
    print(f"{'='*60}\n")
    
    try:
        graph = build_graph()
        state = {}
        
        print("🔄 Starting pipeline execution...\n")
        state = graph.invoke(state)
        
        print(f"\n{'='*60}")
        print("✅ Pipeline Complete")
        print(f"{'='*60}")
        print(f"Status: {state.get('status', 'Unknown')}")
        print(f"{'='*60}\n")
        
        return state
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    display_banner()
    
    try:
        # Check collection status
        print("🔍 Checking Qdrant collection status...")
        stats = get_collection_stats()
        
        # Decide if we need to run pipeline
        if not stats["exists"] or stats["vectors_count"] == 0:
            print("🔧 Collection needs setup")
            
            # Ask user
            response = input("\n🤔 Run full pipeline? (y/n): ").strip().lower()
            
            if response != 'y':
                print("👋 Exiting. Run with 'y' to create collection.")
                return
            
            # Run pipeline
            state = run_full_pipeline()
            
            if not state or not state.get("vectorstore"):
                print("❌ Pipeline failed. Cannot proceed.")
                return
        else:
            print(f"✅ Collection ready with {stats['vectors_count']} vectors")
            print("⏩ Skipping pipeline, connecting to existing data...")
            
            # Connect to existing collection
            state = {}
            state = create_embeddings_node(state)
            
            if not state.get("vectorstore"):
                print("❌ Failed to connect. Cannot proceed.")
                return
        
        # Verify data exists
        final_stats = get_collection_stats()
        
        if not final_stats["exists"] or final_stats["vectors_count"] == 0:
            print("❌ No data available. Cannot proceed.")
            return
        
        # List repositories
        print(f"\n{'='*60}")
        print("📚 Available Repositories")
        print(f"{'='*60}")
        
        repos = list_available_repos()
        
        if not repos:
            print("⚠️  No repositories found")
            return
        
        # Start Q&A
        print(f"\n{'='*60}")
        print("🎯 Starting Interactive Q&A")
        print(f"{'='*60}\n")
        
        state = interactive_qa_loop(state)
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()