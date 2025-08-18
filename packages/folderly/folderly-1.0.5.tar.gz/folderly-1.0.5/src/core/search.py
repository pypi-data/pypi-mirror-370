from pathlib import Path
from typing import List, Dict, Any

def filter_by_name(items: List[Path], name_substring: str) -> Dict[str, Any]:
    """
    Returns items whose name contains the given substring (case-insensitive).
    Args:
        items (List[Path]): List of Path objects to filter.
        name_substring (str): Substring to search for in the item names.
    Returns:
        Dict[str, Any]: Dictionary with success status, results, and metadata.
    """
    try:
        norm_sub = name_substring.lower().strip()
        results = [item for item in items if norm_sub in item.name.lower()]
        
        return {
            "success": True,
            "results": results,
            "total_found": len(results),
            "search_term": name_substring
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    from .core import list_directory_items
    all_items = list_directory_items()
    search_term = input("Enter a file or folder name (or part of it) to search for: ").strip()
    if search_term:
        result = filter_by_name(all_items, search_term)
        if result["success"]:
            matches = result["results"]
            if matches:
                print(f"\nFound {result['total_found']} matches:")
                for match in matches:
                    print(match)
            else:
                print("No files or folders found matching your search.")
        else:
            print(f"Error: {result['error']}")
    else:
        print("No search term entered.") 