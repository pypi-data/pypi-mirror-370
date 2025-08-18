import os
import shutil
from .utils import write_operation_metadata, read_operation_metadata, delete_operation_metadata
from .backup import backup_file_or_folder, delete_backup_file_or_folder, restore_file_or_folder
from datetime import datetime, timedelta
import threading
from .undo_expiry import auto_expiry_cleanup
from .undo_manager import undo_last_operation

def perform_move_with_undo(items_to_move, destination_dir, session_id="folderly_session"): 
    """
    Moves files/folders to destination_dir with undo support.
    items_to_move: list of file/folder paths to move
    destination_dir: where to move them
    session_id: unique session identifier
    """
    # 1. Check for existing undoable operation
    metadata = read_operation_metadata()
    if metadata:
        for item in metadata['current_operation'].get('items', []):
            delete_backup_file_or_folder(item['backup_path'])
        delete_operation_metadata()

    # 2. Prepare operation details
    operation_items = []
    for src in items_to_move:
        backup_path = backup_file_or_folder(src)
        name = os.path.basename(src)
        dst = os.path.join(destination_dir, name)
        operation_items.append({
            'original_path': src,
            'destination_path': dst,
            'backup_path': backup_path
        })

    # 3. Write operation metadata with 30s expiry
    expires_at = datetime.now() + timedelta(seconds=30)
    operation_data = {
        'session_id': session_id,
        'current_operation': {
            'id': f'op_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'type': 'move',
            'timestamp': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'status': 'active',
            'items': operation_items
        }
    }
    write_operation_metadata(operation_data)

    # 4. Perform the move
    for item in operation_items:
        shutil.move(item['original_path'], item['destination_path'])
    
    # Return message instead of printing
    return f"Moved {len(operation_items)} item(s) to {destination_dir}. Undo is available for 30 seconds."

    # 5. Start expiry timer in background using the new expiry manager
    threading.Thread(
        target=auto_expiry_cleanup,
        args=(expires_at, operation_items, delete_operation_metadata, delete_backup_file_or_folder),
        daemon=True
    ).start()
