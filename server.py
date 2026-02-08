from fastmcp import FastMCP
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from bs4 import BeautifulSoup
import os

# Initialize FastMCP
mcp = FastMCP("plesk-docs-rag", log_level="ERROR")

# Configuration
STORAGE_DIR = Path(__file__).parent / "storage"
DB_PATH = STORAGE_DIR / "vector_db"
DOCS_DIR = Path(__file__).parent  # The current folder containing .htm files

# Ensure storage exists
STORAGE_DIR.mkdir(exist_ok=True)

# --- Lazy Loading Helpers ---

def get_db_client():
    return chromadb.PersistentClient(path=str(DB_PATH))

def get_embedding_fn():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment")
    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1",
        model_name="text-embedding-3-small"
    )

# --- Helper: HTML Cleaner ---

def parse_sphinx_html(file_path):
    """
    Extracts title and clean content from Sphinx-generated HTML.
    Targeting <div itemprop="articleBody"> to ignore navigation sidebars.
    """
    try:
        html_content = file_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Get Title
        title = "Untitled"
        if soup.title:
            title = soup.title.string.replace(" — Developing Extensions for Plesk", "").strip()

        # 2. Extract Main Content Only
        # Sphinx docs usually put the real meat inside itemprop="articleBody"
        main_content = soup.find("div", attrs={"itemprop": "articleBody"})
        
        # Fallback if specific tag isn't found
        if not main_content:
            main_content = soup.body
        
        if main_content:
            # 3. Clean up noise (scripts, styles, nav links)
            for tag in main_content(["script", "style", "nav", "footer", "iframe"]):
                tag.decompose()

            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = None
            
        return title, text
    except Exception as e:
        print(f"Error parsing {file_path.name}: {e}")
        return "Untitled", None

# --- Tool 1: Indexing ---

def index_extensions_guide():
    """
    Scans the local folder (and subfolders) for .htm files.
    """
    client = get_db_client()
    ef = get_embedding_fn()
    
    collection = client.get_or_create_collection(name="plesk_docs", embedding_function=ef)
    
    count = 0
    
    # CHANGED: Use rglob("*") to search recursively in all subfolders
    # We still ignore files starting with "_"
    files = [f for f in DOCS_DIR.rglob("*.htm") if not f.name.startswith("_")]

    for file_path in files:
        # ... rest of the loop remains exactly the same ...
        title, content = parse_sphinx_html(file_path)
        
        if content and len(content) > 50:
            try:
                context_text = f"Title: {title}\nFile: {file_path.name}\n---\n{content}"
                
                collection.upsert(
                    ids=[file_path.name],
                    documents=[context_text],
                    metadatas=[{"title": title, "filename": file_path.name}]
                )
                count += 1
            except Exception as e:
                print(f"Failed to index {file_path.name}: {e}")

    return f"Indexing Complete. Processed {count} documentation files."

# --- Tool 2: Search ---

def search_extensions_guide(query: str):
    """
    Searches the Plesk Extensions Guide (Concepts, How-Tos, Tutorials).
    Use this for general questions about extension structure, lifecycle, UI patterns, and best practices.
    """
    client = get_db_client()
    ef = get_embedding_fn()
    collection = client.get_collection(name="plesk_docs", embedding_function=ef)

    results = collection.query(query_texts=[query], n_results=3)
    
    output = []
    if results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            title = meta.get("title", "Unknown")
            filename = meta.get("filename", "unknown.htm")
            
            output.append(f"=== DOC: {title} ({filename}) ===\n{doc}\n")
    
    return "\n".join(output) if output else "No relevant documentation found."

# Register tools with MCP
mcp.tool(index_extensions_guide)
mcp.tool(search_extensions_guide)

if __name__ == "__main__":
    mcp.run()
