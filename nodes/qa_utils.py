# # nodes/qa_utils.py
# from qdrant_client import QdrantClient
# import os
# from config import QDRANT_URL, QDRANT_API_KEY
# COLLECTION_NAME = os.getenv("COLLECTION_NAME", "github_repos")


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
#             print(f"⚠️  Collection '{COLLECTION_NAME}' not found in Qdrant")
#             return []
        
#         # Get collection info
#         collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        
#         if collection_info.vectors_count == 0:
#             print("⚠️  Collection is empty. Run the pipeline first.")
#             return []
        
#         # Scroll through collection to get unique repo names
#         records, _ = client.scroll(
#             collection_name=COLLECTION_NAME,
#             limit=1000,  # Increased limit to get all repos
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
#         print(f"❌ Error listing repositories: {e}")
#         import traceback
#         traceback.print_exc()
#         return []


# def get_collection_stats():
#     """
#     Get statistics about the Qdrant collection
#     """
#     try:
#         client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
#         collections = client.get_collections().collections
#         collection_names = [col.name for col in collections]
#         print("="*60 + "\n")
#         print(f"COLLECTION_NAME: {COLLECTION_NAME} \ncollections: {collections} \ncollection_names: {collection_names}")
#         print("="*60 + "\n")
#         if COLLECTION_NAME not in collection_names:
#             return {
#                 "exists": False,
#                 "message": f"Collection '{COLLECTION_NAME}' not found"
#             }
        
#         collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        
#         return {
#             "exists": True,
#             # "vectors_count": collection_info.vectors_count,
#             "vectors_count": collection_info.vectors_count or 0,
#             "collection_name": COLLECTION_NAME,
#             "status": "active"
#         }
        
#     except Exception as e:
#         return {
#             "exists": False,
#             "error": str(e)
#         }



# nodes/qa_utils.py
from qdrant_client import QdrantClient
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
import time


def get_collection_stats():
    """
    Get detailed statistics about the Qdrant collection
    Returns dict with exists, vectors_count, and other info
    """
    print(f"\n{'='*60}")
    print(f"🔍 Checking Collection: {COLLECTION_NAME}")
    print(f"{'='*60}")
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Get all collections
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        print(f"📦 Available collections: {len(collection_names)}")
        for name in collection_names:
            print(f"   - {name}")
        
        if COLLECTION_NAME not in collection_names:
            print(f"❌ Collection '{COLLECTION_NAME}' NOT FOUND")
            print(f"{'='*60}\n")
            return {
                "exists": False,
                "vectors_count": 0,
                "message": f"Collection '{COLLECTION_NAME}' not found"
            }
        
        # Get collection info
        print(f"✅ Collection '{COLLECTION_NAME}' EXISTS")
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        
        # Wait a bit and retry to ensure indexing is complete
        vectors_count = collection_info.points_count if hasattr(collection_info, 'points_count') else 0
        
        if vectors_count == 0:
            print(f"⏳ Waiting for vectors to be indexed...")
            time.sleep(2)
            collection_info = client.get_collection(collection_name=COLLECTION_NAME)
            vectors_count = collection_info.points_count if hasattr(collection_info, 'points_count') else 0
        
        print(f"📊 Vectors count: {vectors_count}")
        print(f"{'='*60}\n")
        
        return {
            "exists": True,
            "vectors_count": vectors_count,
            "collection_name": COLLECTION_NAME,
            "status": "active" if vectors_count > 0 else "empty"
        }
        
    except Exception as e:
        print(f"❌ Error checking collection: {e}")
        print(f"{'='*60}\n")
        return {
            "exists": False,
            "vectors_count": 0,
            "error": str(e)
        }


def list_available_repos():
    """
    List all unique repository names from the collection
    """
    print(f"\n{'='*60}")
    print(f"📚 Fetching Available Repositories")
    print(f"{'='*60}")
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Check collection exists
        stats = get_collection_stats()
        if not stats["exists"] or stats["vectors_count"] == 0:
            print("⚠️  No data in collection")
            print(f"{'='*60}\n")
            return []
        
        # Scroll through collection
        print(f"🔄 Scanning collection for repositories...")
        records, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        
        # Extract unique repo names
        repo_names = set()
        for record in records:
            if record.payload and "metadata" in record.payload:
                repo_name = record.payload["metadata"].get("repo_name")
                if repo_name:
                    repo_names.add(repo_name)
        
        repo_list = sorted(list(repo_names))
        
        print(f"✅ Found {len(repo_list)} repositories:")
        for i, repo in enumerate(repo_list, 1):
            print(f"   {i}. {repo}")
        print(f"{'='*60}\n")
        
        return repo_list
        
    except Exception as e:
        print(f"❌ Error listing repositories: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return []


def collection_needs_creation():
    """
    Check if collection needs to be created (doesn't exist or is empty)
    """
    stats = get_collection_stats()
    needs_creation = not stats["exists"] or stats["vectors_count"] == 0
    
    if needs_creation:
        print(f"🔧 Collection needs to be created/populated")
    else:
        print(f"✅ Collection is ready with {stats['vectors_count']} vectors")
    
    return needs_creation