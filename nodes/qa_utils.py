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



# # nodes/qa_utils.py
# from qdrant_client import QdrantClient
# from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME
# import time


# def get_collection_stats():
#     """
#     Get detailed statistics about the Qdrant collection
#     Returns dict with exists, vectors_count, and other info
#     """
#     print(f"\n{'='*60}")
#     print(f"🔍 Checking Collection: {COLLECTION_NAME}")
#     print(f"{'='*60}")
    
#     try:
#         client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
#         # Get all collections
#         collections = client.get_collections().collections
#         collection_names = [col.name for col in collections]
        
#         print(f"📦 Available collections: {len(collection_names)}")
#         for name in collection_names:
#             print(f"   - {name}")
        
#         if COLLECTION_NAME not in collection_names:
#             print(f"❌ Collection '{COLLECTION_NAME}' NOT FOUND")
#             print(f"{'='*60}\n")
#             return {
#                 "exists": False,
#                 "vectors_count": 0,
#                 "message": f"Collection '{COLLECTION_NAME}' not found"
#             }
        
#         # Get collection info
#         print(f"✅ Collection '{COLLECTION_NAME}' EXISTS")
#         collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        
#         # Wait a bit and retry to ensure indexing is complete
#         vectors_count = collection_info.points_count if hasattr(collection_info, 'points_count') else 0
        
#         if vectors_count == 0:
#             print(f"⏳ Waiting for vectors to be indexed...")
#             time.sleep(2)
#             collection_info = client.get_collection(collection_name=COLLECTION_NAME)
#             vectors_count = collection_info.points_count if hasattr(collection_info, 'points_count') else 0
        
#         print(f"📊 Vectors count: {vectors_count}")
#         print(f"{'='*60}\n")
        
#         return {
#             "exists": True,
#             "vectors_count": vectors_count,
#             "collection_name": COLLECTION_NAME,
#             "status": "active" if vectors_count > 0 else "empty"
#         }
        
#     except Exception as e:
#         print(f"❌ Error checking collection: {e}")
#         print(f"{'='*60}\n")
#         return {
#             "exists": False,
#             "vectors_count": 0,
#             "error": str(e)
#         }


# def list_available_repos():
#     """
#     List all unique repository names from the collection
#     """
#     print(f"\n{'='*60}")
#     print(f"📚 Fetching Available Repositories")
#     print(f"{'='*60}")
    
#     try:
#         client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
#         # Check collection exists
#         stats = get_collection_stats()
#         if not stats["exists"] or stats["vectors_count"] == 0:
#             print("⚠️  No data in collection")
#             print(f"{'='*60}\n")
#             return []
        
#         # Scroll through collection
#         print(f"🔄 Scanning collection for repositories...")
#         records, _ = client.scroll(
#             collection_name=COLLECTION_NAME,
#             limit=1000,
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
        
#         repo_list = sorted(list(repo_names))
        
#         print(f"✅ Found {len(repo_list)} repositories:")
#         for i, repo in enumerate(repo_list, 1):
#             print(f"   {i}. {repo}")
#         print(f"{'='*60}\n")
        
#         return repo_list
        
#     except Exception as e:
#         print(f"❌ Error listing repositories: {e}")
#         import traceback
#         traceback.print_exc()
#         print(f"{'='*60}\n")
#         return []


# def collection_needs_creation():
#     """
#     Check if collection needs to be created (doesn't exist or is empty)
#     """
#     stats = get_collection_stats()
#     needs_creation = not stats["exists"] or stats["vectors_count"] == 0
    
#     if needs_creation:
#         print(f"🔧 Collection needs to be created/populated")
#     else:
#         print(f"✅ Collection is ready with {stats['vectors_count']} vectors")
    
#     return needs_creation






"""
QA Utilities Module
~~~~~~~~~~~~~~~~~~~
Utility functions for Q&A operations and vector store management.

This module provides:
- Collection statistics and health checks
- Repository listing and discovery
- Document counting and analytics
- Collection status validation
"""

import time
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from config import QDRANT_URL, QDRANT_API_KEY, COLLECTION_NAME


# ============================================================================
# Constants
# ============================================================================

SEPARATOR = "=" * 60
RETRY_DELAY = 2  # seconds


# ============================================================================
# Collection Management
# ============================================================================

def get_collection_stats() -> Dict:
    """
    Get comprehensive statistics about the Qdrant collection.
    
    This function checks:
    - Collection existence
    - Number of vectors stored
    - Collection status and health
    
    Returns:
        Dictionary containing:
        - exists (bool): Whether collection exists
        - vectors_count (int): Number of vectors in collection
        - collection_name (str): Name of the collection
        - status (str): 'active', 'empty', or 'error'
        - message (str): Optional status message
        - error (str): Optional error message
    """
    print(f"\n{SEPARATOR}")
    print(f"🔍 CHECKING COLLECTION: {COLLECTION_NAME}")
    print(SEPARATOR)
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Get all available collections
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        print(f"📦 Available collections: {len(collection_names)}")
        for name in collection_names:
            status_icon = "✓" if name == COLLECTION_NAME else " "
            print(f"   [{status_icon}] {name}")
        
        # Check if target collection exists
        if COLLECTION_NAME not in collection_names:
            print(f"\n❌ Collection '{COLLECTION_NAME}' NOT FOUND")
            print(SEPARATOR)
            return {
                "exists": False,
                "vectors_count": 0,
                "collection_name": COLLECTION_NAME,
                "status": "not_found",
                "message": f"Collection '{COLLECTION_NAME}' does not exist"
            }
        
        # Get collection information
        print(f"\n✅ Collection '{COLLECTION_NAME}' EXISTS")
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        
        # Get vector count with retry logic
        vectors_count = _get_vectors_count_with_retry(client)
        
        # Determine status
        if vectors_count > 0:
            status = "active"
            print(f"📊 Status: Active with {vectors_count:,} vectors")
        else:
            status = "empty"
            print(f"⚠️  Status: Empty (no vectors found)")
        
        print(SEPARATOR)
        
        return {
            "exists": True,
            "vectors_count": vectors_count,
            "collection_name": COLLECTION_NAME,
            "status": status
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(SEPARATOR)
        return {
            "exists": False,
            "vectors_count": 0,
            "collection_name": COLLECTION_NAME,
            "status": "error",
            "error": str(e)
        }


def _get_vectors_count_with_retry(client: QdrantClient) -> int:
    """
    Get vector count with retry logic for indexing delays.
    
    Args:
        client: Initialized Qdrant client
        
    Returns:
        Number of vectors in collection
    """
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    vectors_count = getattr(collection_info, 'points_count', 0)
    
    # Retry if count is zero (might be indexing)
    if vectors_count == 0:
        print(f"⏳ Waiting {RETRY_DELAY}s for indexing to complete...")
        time.sleep(RETRY_DELAY)
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        vectors_count = getattr(collection_info, 'points_count', 0)
    
    return vectors_count


def collection_needs_creation() -> bool:
    """
    Check if collection needs to be created or populated.
    
    Returns:
        True if collection doesn't exist or is empty, False otherwise
    """
    stats = get_collection_stats()
    needs_creation = not stats["exists"] or stats["vectors_count"] == 0
    
    if needs_creation:
        print(f"🔧 Action Required: Collection needs to be created/populated")
    else:
        print(f"✅ Collection Ready: {stats['vectors_count']:,} vectors available")
    
    return needs_creation


# ============================================================================
# Repository Discovery
# ============================================================================

def list_available_repos() -> List[str]:
    """
    List all unique repository names from the collection.
    
    This function scans the vector store and extracts unique repository
    names from document metadata.
    
    Returns:
        Sorted list of repository names. Empty list if:
        - Collection doesn't exist
        - Collection is empty
        - Error occurs during scanning
    """
    print(f"\n{SEPARATOR}")
    print(f"📚 SCANNING FOR REPOSITORIES")
    print(SEPARATOR)
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Verify collection exists and has data
        stats = get_collection_stats()
        
        if not stats["exists"]:
            print("❌ Collection does not exist")
            print(f"💡 Create and populate the collection first")
            print(SEPARATOR)
            return []
        
        if stats["vectors_count"] == 0:
            print("⚠️  Collection is empty")
            print(f"💡 Index some repositories before using Q&A")
            print(SEPARATOR)
            return []
        
        # Scan collection for repository names
        print(f"🔄 Scanning {stats['vectors_count']:,} vectors...")
        
        records, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,  # Adjust if you have more than 1000 repos
            with_payload=True,
            with_vectors=False
        )
        
        # Extract unique repository names
        repo_names = set()
        processed_count = 0
        
        for record in records:
            processed_count += 1
            if record.payload and "metadata" in record.payload:
                repo_name = record.payload["metadata"].get("repo_name")
                if repo_name:
                    repo_names.add(repo_name)
        
        repo_list = sorted(list(repo_names))
        
        # Display results
        print(f"✅ Scanned {processed_count:,} records")
        print(f"✅ Found {len(repo_list)} unique repositories")
        
        if repo_list:
            print(f"\n📋 Repositories:")
            for i, repo in enumerate(repo_list, 1):
                print(f"   {i:2d}. {repo}")
        
        print(SEPARATOR)
        
        return repo_list
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print(SEPARATOR)
        return []


# ============================================================================
# Repository Analytics
# ============================================================================

def get_repo_document_count(repo_name: str) -> int:
    """
    Get count of documents/chunks for a specific repository.
    
    Args:
        repo_name: Name of the repository
        
    Returns:
        Number of document chunks for the repository
    """
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Count points with repository filter
        result = client.count(
            collection_name=COLLECTION_NAME,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.repo_name",
                        match=MatchValue(value=repo_name)
                    )
                ]
            )
        )
        
        return result.count
        
    except Exception as e:
        print(f"⚠️  Error counting documents for '{repo_name}': {e}")
        return 0


def get_repo_file_list(repo_name: str) -> List[str]:
    """
    Get list of unique source files for a repository.
    
    Args:
        repo_name: Name of the repository
        
    Returns:
        Sorted list of source file paths
    """
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Scroll through records with repo filter
        records, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.repo_name",
                        match=MatchValue(value=repo_name)
                    )
                ]
            ),
            limit=1000,
            with_payload=True,
            with_vectors=False
        )
        
        # Extract unique source files
        source_files = set()
        for record in records:
            if record.payload and "metadata" in record.payload:
                source_file = record.payload["metadata"].get("source_file")
                if source_file:
                    source_files.add(source_file)
        
        return sorted(list(source_files))
        
    except Exception as e:
        print(f"⚠️  Error getting file list for '{repo_name}': {e}")
        return []


def display_repo_stats(repos: Optional[List[str]] = None) -> None:
    """
    Display detailed statistics for repositories.
    
    Args:
        repos: Optional list of specific repositories to show.
               If None, shows stats for all repositories.
    """
    if repos is None:
        repos = list_available_repos()
    
    if not repos:
        print("\n⚠️  No repositories to display")
        return
    
    print(f"\n{SEPARATOR}")
    print(f"📊 REPOSITORY STATISTICS")
    print(SEPARATOR)
    
    total_docs = 0
    
    for i, repo in enumerate(repos, 1):
        doc_count = get_repo_document_count(repo)
        total_docs += doc_count
        
        # Format with thousand separators
        count_str = f"{doc_count:,}".rjust(8)
        print(f"{i:2d}. {repo:40s} {count_str} chunks")
    
    print(SEPARATOR)
    print(f"{'Total':43s} {total_docs:,} chunks")
    print(SEPARATOR)


def display_repo_details(repo_name: str) -> None:
    """
    Display detailed information about a specific repository.
    
    Args:
        repo_name: Name of the repository
    """
    print(f"\n{SEPARATOR}")
    print(f"📂 REPOSITORY DETAILS: {repo_name}")
    print(SEPARATOR)
    
    # Get document count
    doc_count = get_repo_document_count(repo_name)
    print(f"📊 Total chunks: {doc_count:,}")
    
    # Get file list
    print(f"\n📄 Retrieving source files...")
    files = get_repo_file_list(repo_name)
    
    if files:
        print(f"📄 Source files ({len(files)}):")
        for i, file in enumerate(files, 1):
            print(f"   {i:2d}. {file}")
    else:
        print(f"⚠️  No source files found")
    
    print(SEPARATOR)


# ============================================================================
# Health Check
# ============================================================================

def health_check() -> Dict:
    """
    Perform comprehensive health check of the Q&A system.
    
    Returns:
        Dictionary with health check results:
        - collection_healthy (bool)
        - repos_available (int)
        - total_vectors (int)
        - status (str): 'healthy', 'warning', or 'error'
        - messages (List[str]): Status messages
    """
    print(f"\n{SEPARATOR}")
    print(f"🏥 SYSTEM HEALTH CHECK")
    print(SEPARATOR)
    
    messages = []
    status = "healthy"
    
    # Check collection
    stats = get_collection_stats()
    collection_healthy = stats["exists"] and stats["vectors_count"] > 0
    
    if not stats["exists"]:
        messages.append("❌ Collection does not exist")
        status = "error"
    elif stats["vectors_count"] == 0:
        messages.append("⚠️  Collection is empty")
        status = "warning"
    else:
        messages.append(f"✅ Collection active with {stats['vectors_count']:,} vectors")
    
    # Check repositories
    repos = list_available_repos() if collection_healthy else []
    
    if collection_healthy:
        if len(repos) == 0:
            messages.append("⚠️  No repositories found")
            status = "warning"
        else:
            messages.append(f"✅ {len(repos)} repositories available")
    
    # Display results
    print(f"\n📋 Health Check Results:")
    for msg in messages:
        print(f"   {msg}")
    
    print(f"\n🏥 Overall Status: {status.upper()}")
    print(SEPARATOR)
    
    return {
        "collection_healthy": collection_healthy,
        "repos_available": len(repos),
        "total_vectors": stats.get("vectors_count", 0),
        "status": status,
        "messages": messages
    }


# ============================================================================
# Module Entry Point
# ============================================================================

if __name__ == "__main__":
    print("QA Utilities Module")
    print("=" * 60)
    print("\nRunning health check...")
    health_check()
    print("\nRunning repository stats...")
    display_repo_stats()