# #from langgraph.graph import StateGraph
# from utils.doc_utils import process_all_repositories


# def generate_docs_node(state: dict) -> dict:
#     print('='*50)
#     print("📝 Generating docs from repos...")
#     print('='*50)

#     try:
#         # Run doc generation pipeline
#         process_all_repositories(base_path="data/github_repos")

#         state["docs"] = "✅ Documentation generated and saved in repos_docs2/"
#         state["status"] = "docs_generated"

#     except Exception as e:
#         state["docs"] = f"❌ Failed to generate docs: {e}"
#         state["status"] = "error"

#     return state



# nodes/generate_docs.py
import os
from pathlib import Path
from utils.doc_utils import process_repository


def generate_docs_node(state: dict) -> dict:
    """
    Generate documentation for all repositories
    """
    print(f"\n{'='*60}")
    print("📝 Documentation Generation Node")
    print(f"{'='*60}\n")
    
    base_path = "data/github_repos"
    base = Path(base_path)
    
    # Check if repos directory exists
    if not base.exists():
        print(f"❌ Repos directory not found: {base_path}")
        state["docs"] = "❌ No repos directory"
        state["status"] = "error"
        return state
    
    # Get all repo directories
    repos = [d for d in base.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not repos:
        print(f"⚠️  No repositories found in {base_path}")
        state["docs"] = "⚠️ No repositories to document"
        state["status"] = "warning"
        return state
    
    print(f"✅ Found {len(repos)} repositories to process:")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo.name}")
    print()
    
    # Process each repository
    results = []
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    for i, repo in enumerate(repos, 1):
        print(f"\n{'='*50}")
        print(f"[{i}/{len(repos)}] Processing: {repo.name}")
        print(f"{'='*50}")
        
        try:
            result = process_repository(str(repo), repo.name)
            results.append((repo.name, result))
            
            if "Success" in result:
                success_count += 1
                print(f"✅ {result}")
            elif "Skipped" in result:
                skipped_count += 1
                print(f"⏩ {result}")
            else:
                failed_count += 1
                print(f"❌ {result}")
                
        except Exception as e:
            failed_count += 1
            error_msg = f"Failed: {str(e)}"
            results.append((repo.name, error_msg))
            print(f"❌ {error_msg}")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Documentation Generation Summary")
    print(f"{'='*60}")
    print(f"✅ Success:  {success_count}")
    print(f"⏩ Skipped:  {skipped_count}")
    print(f"❌ Failed:   {failed_count}")
    print(f"📂 Total:    {len(repos)}")
    print(f"{'='*60}\n")
    
    # Check if any docs were created
    docs_dir = Path("repos_docs2")
    if docs_dir.exists():
        doc_files = list(docs_dir.glob("*.md"))
        print(f"📄 Documentation files in {docs_dir}: {len(doc_files)}\n")
        state["doc_file_count"] = len(doc_files)
    else:
        print(f"⚠️  Docs directory not created\n")
        state["doc_file_count"] = 0
    
    # Update state
    state["docs"] = f"✅ Processed {len(repos)} repos: {success_count} success, {skipped_count} skipped, {failed_count} failed"
    state["status"] = "docs_generated" if success_count > 0 else "error"
    state["doc_results"] = results
    
    return state
