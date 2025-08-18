import threading
import logging
from datetime import datetime
from typing import Dict, Any, List

# Set up logging - only show warnings and errors
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def auto_expiry_cleanup(expires_at, operation_items, delete_metadata_func, delete_backup_func) -> Dict[str, Any]:
    """
    Waits until expiry, then deletes backups and metadata.
    - expires_at: datetime object for expiry
    - operation_items: list of items with 'backup_path'
    - delete_metadata_func: function to delete operation metadata
    - delete_backup_func: function to delete a backup file/folder
    
    Returns:
        Dict with cleanup status and details
    """
    try:
        now = datetime.now()
        wait_seconds = (expires_at - now).total_seconds()
        
        if wait_seconds > 0:
            threading.Event().wait(wait_seconds)
        
        cleaned_items = []
        failed_items = []
        
        for item in operation_items:
            try:
                delete_backup_func(item['backup_path'])
                cleaned_items.append({
                    "backup_path": item['backup_path'],
                    "original_path": item['original_path'],
                    "status": "cleaned"
                })
            except Exception as e:
                failed_items.append({
                    "backup_path": item['backup_path'],
                    "original_path": item['original_path'],
                    "error": str(e),
                    "status": "failed"
                })
        
        # Delete metadata
        try:
            delete_metadata_func()
            metadata_status = "deleted"
        except Exception as e:
            metadata_status = f"failed: {str(e)}"
        
        cleanup_result = {
            "success": len(failed_items) == 0,
            "timestamp": datetime.now().isoformat(),
            "operation_type": "undo_expiry_cleanup",
            "items_cleaned": len(cleaned_items),
            "items_failed": len(failed_items),
            "metadata_status": metadata_status,
            "cleaned_items": cleaned_items,
            "failed_items": failed_items
        }
        
        # Log the result instead of printing
        if cleanup_result["success"]:
            logger.info(f"Undo window expired. Cleaned {len(cleaned_items)} backup(s). Metadata: {metadata_status}")
        else:
            logger.warning(f"Undo cleanup completed with {len(failed_items)} failure(s). Cleaned: {len(cleaned_items)}, Failed: {len(failed_items)}")
        
        return cleanup_result
        
    except Exception as e:
        error_result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "operation_type": "undo_expiry_cleanup",
            "error": str(e),
            "items_cleaned": 0,
            "items_failed": len(operation_items),
            "metadata_status": "unknown"
        }
        logger.error(f"Undo expiry cleanup failed: {str(e)}")
        return error_result 