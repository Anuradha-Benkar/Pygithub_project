# #  nodes/create_embeddings.py
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_chroma import Chroma
# # from utils.embed_utils import run_embedding_pipeline

# # def create_embeddings_node(state: dict) -> dict:
# #     print("🔎 Creating embeddings...")

# #     try:
# #         run_embedding_pipeline()
# #         embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# #         vectorstore = Chroma(
# #             embedding_function=embeddings,
# #             persist_directory="repo_embedding"
# #         )

# #         # ✅ Save vectorstore in state for later nodes
# #         state["vectorstore"] = vectorstore
# #         state["status"] = "✅ Embeddings created"

# #     except Exception as e:
# #         state["vectorstore"] = None
# #         state["status"] = f"❌ Failed to create embeddings: {e}"

# #     return state


# ####################   2nd test   ##########################


# # # nodes/create_embeddings.py
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_chroma import Chroma
# # from utils.embed_utils import run_embedding_pipeline
# # from config import EMBED_DIR, HF_EMBED_MODEL
# # import os

# # def create_embeddings_node(state: dict) -> dict:
# #     print('='*50)
# #     print("🔎 Creating embeddings...")
# #     print('='*50)

# #     try:
# #         # Run pipeline → saves per-repo embeddings under EMBED_DIR
# #         print(f"{('='*50)} \n📦 Running embedding pipeline... \n{('='*50)}")

# #         result = run_embedding_pipeline()

# #         # Build a single Chroma over EMBED_DIR
# #         embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
# #         vectorstore = Chroma(
# #             embedding_function=embeddings,
# #             persist_directory=EMBED_DIR  # main directory containing all sub-dbs
# #         )

# #         # Save in state for QA node
# #         state["vectorstore"] = vectorstore
# #         state["status"] = result["status"]

# #     except Exception as e:
# #         print(f"❌ Error during embedding creation: {e}")
# #         state["vectorstore"] = None
# #         state["status"] = f"❌ Failed to create embeddings: {e}"

# #     return state


# ################################  3rd test   ##########################

# # # nodes/create_embeddings.py
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_chroma import Chroma
# # from utils.embed_utils import run_embedding_pipeline
# # from config import EMBED_DIR, HF_EMBED_MODEL
# # import os

# # def create_embeddings_node(state: dict) -> dict:
# #     print('='*50)
# #     print("🔎 Creating embeddings...")
# #     print('='*50)

# #     try:
# #         result = run_embedding_pipeline()  # returns embed_dirs
# #         print(f"✅ Embedding pipeline result: {result}")
        
# #         embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)

# #         repo_stores = {}
# #         for db_path in result["embed_dirs"]:
# #             repo_name = os.path.basename(db_path)   # use folder name as repo key
# #             repo_stores[repo_name] = Chroma(
# #                 embedding_function=embeddings,
# #                 persist_directory=db_path
# #             )

# #         state["vectorstores"] = repo_stores
# #         state["status"] = result["status"]

# #     except Exception as e:
# #         print(f"❌ Error during embedding creation: {e}")
# #         state["vectorstores"] = {}
# #         state["status"] = f"❌ Failed to create embeddings: {e}"

# #     return state




# # nodes/create_embeddings.py
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from utils.embed_utils import run_embedding_pipeline
# from config import (
#     QDRANT_URL,
#     QDRANT_API_KEY,
#     COLLECTION_NAME,
#     HF_EMBED_MODEL
# )

# def create_embeddings_node(state: dict) -> dict:
#     """
#     Create embeddings and store in Qdrant Cloud
#     """
#     print('='*50)
#     print("🔎 Creating embeddings in Qdrant Cloud...")
#     print('='*50)

#     try:
#         # Run embedding pipeline
#         result = run_embedding_pipeline()
#         print(f"✅ Embedding pipeline result: {result}")
        
#         # Initialize embeddings model
#         embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
        
#         # Create Qdrant vectorstore connection
#         vectorstore = QdrantVectorStore.from_existing_collection(
#             embedding=embeddings,
#             collection_name=COLLECTION_NAME,
#             url=QDRANT_URL,
#             api_key=QDRANT_API_KEY,
#         )
        
#         # Store vectorstore in state for QA node
#         state["vectorstore"] = vectorstore
#         state["collection_name"] = COLLECTION_NAME
#         state["status"] = result["status"]
#         state["total_chunks"] = result.get("total_chunks", 0)

#     except Exception as e:
#         print(f"❌ Error during embedding creation: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["vectorstore"] = None
#         state["collection_name"] = None
#         state["status"] = f"❌ Failed to create embeddings: {e}"

#     return state

######################## test 2 #########################
# # nodes/create_embeddings.py
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from utils.embed_utils import run_embedding_pipeline
# from nodes.qa_utils import get_collection_stats
# from config import (
#     QDRANT_URL,
#     QDRANT_API_KEY,
#     COLLECTION_NAME,
#     HF_EMBED_MODEL
# )


# def create_embeddings_node(state: dict) -> dict:
#     """
#     Create embeddings and store in Qdrant Cloud
#     """
#     print("\n" + "="*60)
#     print("🔎 Embeddings Node - Qdrant Cloud Integration")
#     print("="*60 + "\n")

#     try:
#         # Check if collection already exists with data
#         stats = get_collection_stats()
        
#         # if stats.get("exists") and stats.get("vectors_count", 0) > 0:
#         if stats.get("exists") and (stats.get("vectors_count") or 0) > 0:
#             print(f"✅ Collection '{COLLECTION_NAME}' exists with {stats['vectors_count']} vectors")
#             print("⏩ Skipping embedding creation\n")
            
#             # Just connect to existing collection
#             embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
            
#             vectorstore = QdrantVectorStore.from_existing_collection(
#                 embedding=embeddings,
#                 collection_name=COLLECTION_NAME,
#                 url=QDRANT_URL,
#                 api_key=QDRANT_API_KEY,
#             )
            
#             state["vectorstore"] = vectorstore
#             state["collection_name"] = COLLECTION_NAME
#             state["status"] = "✅ Connected to existing collection"
#             state["total_chunks"] = stats['vectors_count']
#             state["vectors_in_cloud"] = stats['vectors_count']
            
#             print("✅ Connected to Qdrant collection successfully\n")
#             return state
        
#         # Collection doesn't exist or is empty, run full pipeline
#         print("📝 Running embedding creation pipeline...")
#         result = run_embedding_pipeline()
        
#         print(f"\n{'='*50}")
#         print(f"📊 Pipeline Result:")
#         print(f"{'='*50}")
#         for key, value in result.items():
#             print(f"  {key}: {value}")
#         print(f"{'='*50}\n")
        
#         # Initialize embeddings model
#         embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
        
#         # Connect to the newly created collection
#         vectorstore = QdrantVectorStore.from_existing_collection(
#             embedding=embeddings,
#             collection_name=COLLECTION_NAME,
#             url=QDRANT_URL,
#             api_key=QDRANT_API_KEY,
#         )
        
#         # Store in state
#         state["vectorstore"] = vectorstore
#         state["collection_name"] = COLLECTION_NAME
#         state["status"] = result["status"]
#         state["total_chunks"] = result.get("total_chunks", 0)
#         state["vectors_in_cloud"] = result.get("vectors_in_cloud", 0)
        
#         print("✅ Embeddings created and vectorstore initialized\n")

#     except Exception as e:
#         print(f"❌ Error during embedding creation: {e}")
#         import traceback
#         traceback.print_exc()
        
#         state["vectorstore"] = None
#         state["collection_name"] = None
#         state["status"] = f"❌ Failed to create embeddings: {e}"

#     return state



################# test 3 ##########################
# nodes/create_embeddings.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from utils.embed_utils import run_embedding_pipeline
from nodes.qa_utils import collection_needs_creation
from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    COLLECTION_NAME,
    HF_EMBED_MODEL
)


def create_embeddings_node(state: dict) -> dict:
    """
    Create embeddings node - only creates if needed
    """
    print(f"\n{'='*60}")
    print("🔎 Embeddings Node - Starting")
    print(f"{'='*60}\n")

    try:
        # Check if we need to create embeddings
        needs_creation = collection_needs_creation()
        
        if not needs_creation:
            print(f"✅ Collection already exists with data")
            print(f"⏩ Connecting to existing collection...")
            
            # Just connect to existing collection
            embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
            
            vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=embeddings,
                collection_name=COLLECTION_NAME,
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY,
            )
            
            print(f"✅ Connected successfully")
            
            state["vectorstore"] = vectorstore
            state["collection_name"] = COLLECTION_NAME
            state["status"] = "✅ Using existing collection"
            
            return state
        
        # Need to create embeddings
        print(f"🔧 Creating new embeddings...")
        result = run_embedding_pipeline(force_recreate=False)
        
        print(f"\n{'='*50}")
        print(f"📊 Embedding Result:")
        print(f"{'='*50}")
        for key, value in result.items():
            if key != "processed_files":  # Don't print long file list
                print(f"  {key}: {value}")
        print(f"{'='*50}\n")
        
        # Connect to the collection
        print(f"🔗 Connecting to vectorstore...")
        embeddings = HuggingFaceEmbeddings(model_name=HF_EMBED_MODEL)
        
        vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        
        print(f"✅ Vectorstore ready")
        
        # Update state
        state["vectorstore"] = vectorstore
        state["collection_name"] = COLLECTION_NAME
        state["status"] = result["status"]
        state["total_chunks"] = result.get("total_chunks", 0)
        state["vectors_in_cloud"] = result.get("vectors_in_cloud", 0)

    except Exception as e:
        print(f"❌ Error in embeddings node: {e}")
        import traceback
        traceback.print_exc()
        
        state["vectorstore"] = None
        state["status"] = f"❌ Failed: {e}"

    print(f"\n{'='*60}")
    print("✅ Embeddings Node - Complete")
    print(f"{'='*60}\n")
    
    return state