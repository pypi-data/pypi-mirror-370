import os
import re
from pathlib import Path
from typing import List, Dict, Any
import shutil
import asyncio
from datetime import datetime, timedelta
from send2trash import send2trash

try:
    from config import TARGET_FOLDER
except ImportError:
    TARGET_FOLDER = "Desktop"

# File type mappings - centralized to avoid duplication
FILE_TYPE_MAPPINGS = {
    "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".ppt", ".pptx", ".xls", ".xlsx"],
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
    "videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm", ".m4v"],
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "executables": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
    "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".php", ".rb", ".go"]
}

# Folder name mappings for cross-platform compatibility
FOLDER_MAPPINGS = {
    "documents": ["Documents", "My Documents", "Documenti"],
    "downloads": ["Downloads", "Download"],
    "desktop": ["Desktop"],
    "pictures": ["Pictures", "My Pictures", "Immagini"],
    "music": ["Music", "My Music", "Musica"],
    "videos": ["Videos", "My Videos", "Video"]
}

async def execute_operations(operations, execution_mode="parallel"):
    """Execute multiple operations in parallel or sequential mode"""
    if execution_mode == "parallel":
        # Handle both async and sync functions
        tasks = []
        for func, args, kwargs in operations:
            if asyncio.iscoroutinefunction(func):
                tasks.append(func(*args, **kwargs))
            else:
                tasks.append(asyncio.to_thread(func, *args, **kwargs))
        return await asyncio.gather(*tasks)
    else:
        results = []
        for func, args, kwargs in operations:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.to_thread(func, *args, **kwargs)
            results.append(result)
        return results

def get_directory(folder_name: str = None, root_dir: Path = Path.home(), custom_path: str = None) -> Path:
    """Get directory path for any root folder (Desktop, Downloads, Documents, etc.) or custom path"""
    
    if custom_path:
        custom_path_obj = Path(custom_path)
        if custom_path_obj.exists() and custom_path_obj.is_dir():
            return custom_path_obj
    
    if folder_name is None:
        folder_name = TARGET_FOLDER
    
    folder_lower = folder_name.lower() if folder_name else TARGET_FOLDER.lower()
    
    exact_path = root_dir / folder_name
    if exact_path.exists():
        return exact_path
    
    if folder_lower in FOLDER_MAPPINGS:
        for variation in FOLDER_MAPPINGS[folder_lower]:
            variation_path = root_dir / variation
            if variation_path.exists():
                return variation_path
    
    if folder_lower in ["documents", "pictures", "music", "videos"]:
        onedrive_variations = ["OneDrive", "OneDrive - Personal"]
        
        for onedrive_folder in onedrive_variations:
            onedrive_paths = [
                root_dir / onedrive_folder / folder_name,
                root_dir / onedrive_folder / FOLDER_MAPPINGS[folder_lower][0] if folder_lower in FOLDER_MAPPINGS else folder_name
            ]
            
            for onedrive_path in onedrive_paths:
                if onedrive_path.exists():
                    return onedrive_path
    
    return root_dir / folder_name

async def list_directory_items(
    folder_name: str = None,
    custom_path: str = None,
    extension: str = None,
    file_type: str = None,
    pattern: str = None,
    date_range: tuple = None,
    size_range: tuple = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    include_folders: bool = True,
    include_files: bool = True,
    max_results: int = None
) -> Dict[str, Any]:
    """Lists files and folders in the specified root folder with advanced filtering"""
    try:
        target_dir = get_directory(folder_name, custom_path=custom_path)
        
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Folder '{folder_name or TARGET_FOLDER}' does not exist at {target_dir}",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        if not target_dir.is_dir():
            return {
                "success": False,
                "error": f"'{target_dir}' is not a directory",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        all_items = list(target_dir.iterdir())
        results = []
        
        for item in all_items:
            item_info = {
                "name": item.name,
                "path": str(item),
                "is_file": item.is_file(),
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            }
            
            if not include_folders and item.is_dir():
                continue
            if not include_files and item.is_file():
                continue
            
            if extension and item.is_file():
                if not item.name.lower().endswith(f".{extension.lower()}"):
                    continue
            
            if file_type and item.is_file():
                if not is_file_type_match(item.name, file_type):
                    continue
            
            if pattern and not re.search(pattern, item.name, re.IGNORECASE):
                continue
            
            if date_range and not is_in_date_range(item_info["modified"], date_range):
                continue
            
            if size_range and item.is_file():
                if not is_in_size_range(item_info["size"], size_range):
                    continue
            
            results.append(item_info)
        
        if sort_by == "name":
            results.sort(key=lambda x: x["name"].lower(), reverse=(sort_order == "desc"))
        elif sort_by == "modified":
            results.sort(key=lambda x: x["modified"], reverse=(sort_order == "desc"))
        elif sort_by == "size":
            results.sort(key=lambda x: x["size"] or 0, reverse=(sort_order == "desc"))
        
        if max_results:
            results = results[:max_results]
        
        return {
            "success": True,
            "results": [item["name"] for item in results],
            "full_results": results,
            "total_count": len(results),
            "folder_name": folder_name or TARGET_FOLDER,
            "filters_applied": {
                "extension": extension,
                "file_type": file_type,
                "pattern": pattern,
                "date_range": date_range,
                "size_range": size_range,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name or TARGET_FOLDER
        }

def filter_and_sort_by_modified(items: List[Path], days: int) -> Dict[str, Any]:
    """Filter and sort items by modification date"""
    try:
        cutoff = datetime.now() - timedelta(days=days)
        filtered = [p for p in items if datetime.fromtimestamp(p.stat().st_mtime) >= cutoff]
        sorted_items = sorted(filtered, key=lambda p: p.stat().st_mtime, reverse=True)
        
        return {
            "success": True,
            "results": [str(path) for path in sorted_items],
            "total_found": len(sorted_items),
            "days_threshold": days
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def create_directory(target_dir: Path, base_path: str = "Desktop") -> Dict[str, Any]:
    """Creates a new directory in the specified base path"""
    try:
        base_directory = get_directory(base_path)
        full_path = base_directory / target_dir
        
        full_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "results": str(full_path),
            "directory_created": str(full_path),
            "base_path": str(base_directory),
            "already_existed": full_path.exists()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def create_multiple_directories(directories: List[str], base_path: str = "Desktop", execution_mode: str = "parallel") -> Dict[str, Any]:
    """Creates multiple directories in the specified base path"""
    try:
        base_directory = get_directory(base_path)
        
        def create_single_directory(dir_path):
            try:
                target_dir = Path(dir_path)
                full_path = base_directory / target_dir
                full_path.mkdir(parents=True, exist_ok=True)
                return {"success": True, "path": str(full_path)}
            except Exception as e:
                return {"success": False, "path": dir_path, "error": str(e)}
        
        operations = [(create_single_directory, (dir_path,), {}) for dir_path in directories]
        results = await execute_operations(operations, execution_mode)
        
        created_dirs = []
        failed_dirs = []
        
        for result in results:
            if result["success"]:
                created_dirs.append(result["path"])
            else:
                failed_dirs.append({"path": result["path"], "error": result["error"]})
        
        return {
            "success": True,
            "created_directories": created_dirs,
            "failed_directories": failed_dirs,
            "total_created": len(created_dirs),
            "total_failed": len(failed_dirs),
            "base_path": str(base_directory)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "base_path": base_path
        }

async def move_items_to_directory(items: list[Path], destination_dir: Path, execution_mode: str = "parallel") -> Dict[str, Any]:
    """Moves multiple items to a destination directory"""
    try:
        def move_single_item(item):
            try:
                if item.name.startswith('.'):
                    return {"success": False, "item": str(item), "reason": "hidden file"}
                
                dest = destination_dir / item.name
                shutil.move(str(item), str(dest))
                return {"success": True, "item": str(item), "destination": str(dest)}
            except PermissionError:
                return {"success": False, "item": str(item), "reason": "file in use"}
            except Exception as e:
                return {"success": False, "item": str(item), "reason": str(e)}
        
        operations = [(move_single_item, (item,), {}) for item in items]
        results = await execute_operations(operations, execution_mode)
        
        moved_items = []
        skipped_items = []
        
        for result in results:
            if result["success"]:
                moved_items.append(result["destination"])
            else:
                skipped_items.append({"item": result["item"], "reason": result["reason"]})
        
        return {
            "success": True,
            "results": moved_items,
            "total_moved": len(moved_items),
            "skipped_items": skipped_items,
            "destination": str(destination_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def create_numbered_files(base_name: str, count: int, extension: str, start_number: int = 1, target_dir: Path = None, custom_path: str = None, execution_mode: str = "parallel") -> Dict[str, Any]:
    """Creates multiple numbered files with specified extension"""
    try:
        if target_dir is None:
            target_dir = get_directory(custom_path=custom_path)
        
        def create_single_file(file_number):
            try:
                filename = f"{base_name}_{file_number}.{extension}"
                file_path = target_dir / filename
                
                content = f"This is {base_name} number {file_number}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "filename": filename,
                    "path": str(file_path),
                    "content_length": len(content)
                }
            except Exception as e:
                return {
                    "success": False,
                    "filename": f"{base_name}_{file_number}.{extension}",
                    "error": str(e)
                }
        
        operations = [(create_single_file, (i,), {}) for i in range(start_number, start_number + count)]
        results = await execute_operations(operations, execution_mode)
        
        created_files = []
        failed_files = []
        
        for result in results:
            if result["success"]:
                created_files.append({
                    "filename": result["filename"],
                    "path": result["path"],
                    "content_length": result["content_length"]
                })
            else:
                failed_files.append({
                    "filename": result["filename"],
                    "error": result["error"]
                })
        
        return {
            "success": True,
            "created_files": created_files,
            "failed_files": failed_files,
            "total_created": len(created_files),
            "total_failed": len(failed_files),
            "target_directory": str(target_dir)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def delete_single_item(item_path: str) -> Dict[str, Any]:
    """Deletes a single file or directory"""
    return await _delete_item_internal(item_path)

async def delete_multiple_items(item_paths: List[str], execution_mode: str = "parallel") -> Dict[str, Any]:
    """Deletes multiple files and directories"""
    try:
        operations = [(_delete_item_internal, (item_path,), {}) for item_path in item_paths]
        results = await execute_operations(operations, execution_mode)
        
        deleted_items = []
        failed_items = []
        
        for i, result in enumerate(results):
            item_path = item_paths[i]
            if result["success"]:
                deleted_items.append({
                    "path": item_path,
                    "type": result.get("item_type", "unknown"),
                    "deletion_method": "sent_to_trash"
                })
            else:
                failed_items.append({
                    "path": item_path,
                    "error": result.get("error", "Unknown error"),
                    "reason": result.get("reason", "unknown")
                })
        
        return {
            "success": True,
            "deleted_items": deleted_items,
            "failed_items": failed_items,
            "total_deleted": len(deleted_items),
            "total_failed": len(failed_items),
            "deletion_method": "sent_to_trash"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_items": len(item_paths)
        }

async def _delete_item_internal(item_path: str) -> Dict[str, Any]:
    """Internal helper function for deleting items"""
    try:
        path = Path(item_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"Item does not exist: {item_path}",
                "item_path": item_path
            }
        
        if not path.is_file() and not path.is_dir():
            return {
                "success": False,
                "error": f"Item is not a file or directory: {item_path}",
                "item_path": item_path
            }
        
        send2trash(str(path))
        
        return {
            "success": True,
            "deleted_item": item_path,
            "item_type": "file" if path.is_file() else "directory",
            "deletion_method": "sent_to_trash"
        }
        
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot delete {item_path}",
            "item_path": item_path,
            "reason": "file_in_use_or_protected"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "item_path": item_path
        }

async def delete_items_by_pattern(pattern: str, target_dir: str = None, custom_path: str = None, execution_mode: str = "parallel") -> Dict[str, Any]:
    """Deletes files and directories matching a pattern"""
    try:
        if target_dir is None:
            target_dir = str(get_directory(custom_path=custom_path))
        
        search_dir = Path(target_dir)
        
        if not search_dir.exists():
            return {
                "success": False,
                "error": f"Target directory does not exist: {target_dir}",
                "target_dir": target_dir
            }
        
        matching_items = list(search_dir.glob(pattern))
        
        if not matching_items:
            return {
                "success": True,
                "message": f"No items found matching pattern: {pattern}",
                "pattern": pattern,
                "target_dir": target_dir,
                "total_found": 0
            }
        
        item_paths = [str(item) for item in matching_items]
        result = await delete_multiple_items(item_paths, execution_mode)
        result["pattern"] = pattern
        result["target_dir"] = target_dir
        result["total_found"] = len(matching_items)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "pattern": pattern,
            "target_dir": target_dir
        }

def list_nested_folders_tree(target_dir: str = None, max_depth: int = 3, custom_path: str = None) -> Dict[str, Any]:
    """Lists all nested folders in a tree structure format"""
    try:
        if target_dir is None:
            target_dir = str(get_directory(custom_path=custom_path))
        
        search_dir = Path(target_dir)
        
        if not search_dir.exists():
            return {
                "success": False,
                "error": f"Target directory does not exist: {target_dir}",
                "target_dir": target_dir
            }
        
        def build_tree(path: Path, depth: int = 0, is_last: bool = False, prefix: str = "") -> str:
            if depth > max_depth:
                return ""
            
            try:
                items = sorted([item for item in path.iterdir() if item.is_dir()], key=lambda x: x.name.lower())
            except PermissionError:
                return f"{prefix}└── [Access Denied]\n"
            
            if not items:
                return ""
            
            tree_lines = []
            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                connector = "└──" if is_last_item else "├──"
                line_prefix = "    " if is_last else "│   "
                
                tree_lines.append(f"{prefix}{connector} {item.name}/")
                
                child_prefix = prefix + line_prefix
                child_tree = build_tree(item, depth + 1, is_last_item, child_prefix)
                if child_tree:
                    tree_lines.append(child_tree)
            
            return "\n".join(tree_lines)
        
        tree_structure = build_tree(search_dir)
        
        if not tree_structure:
            return {
                "success": True,
                "message": f"No folders found in {target_dir}",
                "target_dir": target_dir,
                "tree_structure": f"{search_dir.name}/\n",
                "total_folders": 0
            }
        
        full_tree = f"{search_dir.name}/\n{tree_structure}"
        folder_count = len([line for line in full_tree.split('\n') if line.strip().endswith('/')])
        
        return {
            "success": True,
            "target_dir": target_dir,
            "tree_structure": full_tree,
            "total_folders": folder_count,
            "max_depth": max_depth
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "target_dir": target_dir
        }

async def count_files_by_extension(folder_name: str = None, custom_path: str = None) -> Dict[str, Any]:
    """Counts files by extension in the specified folder"""
    try:
        target_dir = get_directory(folder_name, custom_path=custom_path)
        
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Folder '{folder_name or TARGET_FOLDER}' does not exist",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        all_files = [f for f in target_dir.iterdir() if f.is_file()]
        
        extension_counts = {}
        total_files = len(all_files)
        
        for file_path in all_files:
            ext = file_path.suffix.lower()
            if ext:
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
            else:
                extension_counts["no_extension"] = extension_counts.get("no_extension", 0) + 1
        
        sorted_extensions = sorted(extension_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "total_files": total_files,
            "extension_counts": dict(sorted_extensions),
            "top_extensions": sorted_extensions[:10],
            "directory": str(target_dir),
            "folder_name": folder_name or TARGET_FOLDER
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name or TARGET_FOLDER
        }

async def get_file_type_statistics(folder_name: str = None, custom_path: str = None) -> Dict[str, Any]:
    """Gets file type statistics (documents, images, videos, etc.) for the specified folder"""
    try:
        target_dir = get_directory(folder_name, custom_path=custom_path)
        
        if not target_dir.exists():
            return {
                "success": False,
                "error": f"Folder '{folder_name or TARGET_FOLDER}' does not exist",
                "folder_name": folder_name or TARGET_FOLDER
            }
        
        all_files = [f for f in target_dir.iterdir() if f.is_file()]
        
        type_counts = {file_type: 0 for file_type in FILE_TYPE_MAPPINGS.keys()}
        type_counts["other"] = 0
        total_files = len(all_files)
        
        for file_path in all_files:
            ext = file_path.suffix.lower()
            categorized = False
            
            for file_type, extensions in FILE_TYPE_MAPPINGS.items():
                if ext in extensions:
                    type_counts[file_type] += 1
                    categorized = True
                    break
            
            if not categorized:
                type_counts["other"] += 1
        
        non_zero_counts = {k: v for k, v in type_counts.items() if v > 0}
        sorted_types = sorted(non_zero_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "success": True,
            "total_files": total_files,
            "file_type_counts": dict(sorted_types),
            "top_file_types": sorted_types[:5],
            "directory": str(target_dir),
            "folder_name": folder_name or TARGET_FOLDER
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name or TARGET_FOLDER
        }

async def copy_multiple_items(items: list[Path], destination_dir: Path, execution_mode: str = "parallel") -> Dict[str, Any]:
    """Copies multiple items to a destination directory"""
    try:
        def copy_single_item(item):
            try:
                if item.name.startswith('.'):
                    return {"success": False, "item": str(item), "reason": "hidden file"}
                
                dest = destination_dir / item.name
                if item.is_file():
                    shutil.copy2(str(item), str(dest))
                else:
                    shutil.copytree(str(item), str(dest), dirs_exist_ok=True)
                
                return {"success": True, "item": str(item), "destination": str(dest)}
            except PermissionError:
                return {"success": False, "item": str(item), "reason": "permission denied"}
            except Exception as e:
                return {"success": False, "item": str(item), "reason": str(e)}
        
        operations = [(copy_single_item, (item,), {}) for item in items]
        results = await execute_operations(operations, execution_mode)
        
        copied_items = []
        failed_items = []
        
        for result in results:
            if result["success"]:
                copied_items.append(result["destination"])
            else:
                failed_items.append({"item": result["item"], "reason": result["reason"]})
        
        return {
            "success": True,
            "results": copied_items,
            "total_copied": len(copied_items),
            "failed_items": failed_items,
            "destination": str(destination_dir)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def rename_multiple_items(items: list[tuple[Path, str]], execution_mode: str = "parallel") -> Dict[str, Any]:
    """Renames multiple items with new names"""
    try:
        def rename_single_item(item_tuple):
            try:
                old_path, new_name = item_tuple
                
                if old_path.name.startswith('.'):
                    return {"success": False, "item": str(old_path), "reason": "hidden file"}
                
                new_path = old_path.parent / new_name
                
                if new_path.exists():
                    return {"success": False, "item": str(old_path), "reason": "new name already exists"}
                
                old_path.rename(new_path)
                
                return {"success": True, "old_path": str(old_path), "new_path": str(new_path)}
            except PermissionError:
                return {"success": False, "item": str(old_path), "reason": "permission denied"}
            except Exception as e:
                return {"success": False, "item": str(old_path), "reason": str(e)}
        
        operations = [(rename_single_item, (item_tuple,), {}) for item_tuple in items]
        results = await execute_operations(operations, execution_mode)
        
        renamed_items = []
        failed_items = []
        
        for result in results:
            if result["success"]:
                renamed_items.append({
                    "old_path": result["old_path"],
                    "new_path": result["new_path"]
                })
            else:
                failed_items.append({"item": result["item"], "reason": result["reason"]})
        
        return {
            "success": True,
            "renamed_items": renamed_items,
            "total_renamed": len(renamed_items),
            "failed_items": failed_items
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Helper functions
def is_file_type_match(filename: str, file_type: str) -> bool:
    """Check if filename matches the specified file type"""
    if file_type not in FILE_TYPE_MAPPINGS:
        return False
    
    return any(filename.lower().endswith(ext) for ext in FILE_TYPE_MAPPINGS[file_type])

def is_in_date_range(modified_date: str, date_range: tuple) -> bool:
    """Check if modified date is within the specified range"""
    try:
        if isinstance(date_range, int):
            days_ago = date_range
            cutoff = datetime.now() - timedelta(days=days_ago)
            file_date = datetime.fromisoformat(modified_date)
            return file_date >= cutoff
        elif isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            file_date = datetime.fromisoformat(modified_date)
            return start_date <= file_date <= end_date
        return True
    except:
        return True

def is_in_size_range(size: int, size_range: tuple) -> bool:
    """Check if file size is within the specified range"""
    if not size_range or len(size_range) != 2:
        return True
    
    min_size, max_size = size_range
    if min_size is not None and size < min_size:
        return False
    if max_size is not None and size > max_size:
        return False
    return True



# Path discovery functions
def find_candidate_paths():
    """Find all possible OneDrive and user profile paths"""
    user_profile = os.environ.get("USERPROFILE")
    if not user_profile:
        raise RuntimeError("USERPROFILE not found")

    candidates = []

    # Gather OneDrive-like folders under user profile
    for entry in os.listdir(user_profile):
        full_path = os.path.join(user_profile, entry)
        if os.path.isdir(full_path) and entry.startswith("OneDrive"):
            candidates.append(full_path)

    # Always include the plain user profile root as well
    candidates.append(user_profile)

    return candidates

def find_special_folders(base_paths):
    """Find Desktop, Documents, Downloads in the candidate paths"""
    target_names = ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]
    results = []

    for base in base_paths:
        # Directly under base
        for name in target_names:
            path = os.path.join(base, name)
            if os.path.exists(path):
                results.append(path)

        # One level deeper (to catch OneDrive/something/Desktop)
        try:
            for sub in os.listdir(base):
                sub_path = os.path.join(base, sub)
                if os.path.isdir(sub_path):
                    for name in target_names:
                        path = os.path.join(sub_path, name)
                        if os.path.exists(path):
                            results.append(path)
        except PermissionError:
            # skip folders we can't access
            continue

    return results

def summarize_paths(paths):
    """Count files in each path and return structured data"""
    results = []
    
    for path in paths:
        try:
            path_obj = Path(path)
            files = os.listdir(path)
            # Count non-hidden files and folders
            count = len([f for f in files if not f.startswith('.')])
            
            # Determine if this is OneDrive-managed
            is_onedrive = "onedrive" in str(path).lower()
            
            # Get the folder type (Desktop, Documents, etc.)
            folder_type = path_obj.name
            
            # Get the base path for context
            base_path = str(path_obj.parent)
            
            results.append({
                "path": str(path),
                "folder_type": folder_type,
                "file_count": count,
                "is_onedrive": is_onedrive,
                "base_path": base_path,
                "access": "success"
            })
            
        except PermissionError:
            results.append({
                "path": str(path),
                "folder_type": "unknown",
                "file_count": 0,
                "is_onedrive": "onedrive" in str(path).lower(),
                "base_path": "unknown",
                "access": "no access"
            })
        except Exception as e:
            results.append({
                "path": str(path),
                "folder_type": "unknown", 
                "file_count": 0,
                "is_onedrive": "onedrive" in str(path).lower(),
                "base_path": "unknown",
                "access": f"error: {str(e)}"
            })
    
    return results

async def discover_user_paths() -> Dict[str, Any]:
    """Main function to discover all user folder paths with analysis"""
    try:
        # Find candidate base paths
        base_paths = find_candidate_paths()
        
        # Find special folders in those paths
        special_folders = find_special_folders(base_paths)
        
        # Analyze each path
        path_analysis = summarize_paths(special_folders)
        
        # Group by folder type for better organization
        organized_paths = {}
        for path_info in path_analysis:
            folder_type = path_info["folder_type"]
            if folder_type not in organized_paths:
                organized_paths[folder_type] = []
            organized_paths[folder_type].append(path_info)
        
        return {
            "success": True,
            "total_paths_discovered": len(special_folders),
            "base_paths": base_paths,
            "organized_paths": organized_paths,
            "path_analysis": path_analysis,
            "message": f"Discovered {len(special_folders)} folder locations across {len(base_paths)} base paths"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to discover user paths"
        }