#!/usr/bin/env python3
"""
Activity Tracker for Folderly
Monitors user file activities in the background
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FolderlyActivityTracker(FileSystemEventHandler):
    """Tracks user file activities for Folderly"""
    
    def __init__(self, desktop_path: str = None):
        self.desktop_path = desktop_path or str(Path.home() / "Desktop")
        self.activities = []
        self.log_file = "folderly_activities.json"
        
        # Files/folders to ignore (case-insensitive)
        self.ignore_patterns = [
            "thumbs.db",
            ".ds_store",
            "desktop.ini",
            "~$",  # Temporary files
            ".tmp",
            ".temp",
            ".log",
            ".cache",
            "node_modules",
            ".git",
            ".vscode",
            "__pycache__",
            ".pytest_cache",
            ".coverage",
            ".env",
            ".venv",
            "venv",
            "env"
        ]
        
        self.load_activities()
    
    def should_ignore(self, filename: str) -> bool:
        """Check if file/folder should be ignored"""
        filename_lower = filename.lower()
        
        for pattern in self.ignore_patterns:
            if pattern in filename_lower:
                return True
        
        return False
    
    def load_activities(self):
        """Load existing activities from file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    self.activities = json.load(f)
        except Exception as e:
            print(f"Could not load activities: {e}")
            self.activities = []
    
    def save_activities(self):
        """Save activities to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.activities, f, indent=2)
        except Exception as e:
            print(f"Could not save activities: {e}")
    
    def add_activity(self, action: str, details: Dict[str, Any]):
        """Add a new activity"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        self.activities.append(activity)
        self.save_activities()
    
    def on_created(self, event):
        """Track file and folder creation"""
        filename = os.path.basename(event.src_path)
        
        # Skip if file/folder should be ignored
        if self.should_ignore(filename):
            return
            
        item_type = "folder" if event.is_directory else "file"
        self.add_activity(f"{item_type}_created", {
            "filename": filename,
            "path": event.src_path,
            "type": item_type
        })
    
    def on_deleted(self, event):
        """Track file and folder deletion"""
        filename = os.path.basename(event.src_path)
        
        # Skip if file/folder should be ignored
        if self.should_ignore(filename):
            return
            
        item_type = "folder" if event.is_directory else "file"
        self.add_activity(f"{item_type}_deleted", {
            "filename": filename,
            "path": event.src_path,
            "type": item_type
        })
    
    def on_modified(self, event):
        """Track file and folder modification"""
        filename = os.path.basename(event.src_path)
        
        # Skip if file/folder should be ignored
        if self.should_ignore(filename):
            return
            
        item_type = "folder" if event.is_directory else "file"
        self.add_activity(f"{item_type}_modified", {
            "filename": filename,
            "path": event.src_path,
            "type": item_type
        })
    
    def on_moved(self, event):
        """Track file and folder movement"""
        old_name = os.path.basename(event.src_path)
        new_name = os.path.basename(event.dest_path)
        
        # Skip if either old or new name should be ignored
        if self.should_ignore(old_name) or self.should_ignore(new_name):
            return
            
        item_type = "folder" if event.is_directory else "file"
        self.add_activity(f"{item_type}_moved", {
            "old_name": old_name,
            "new_name": new_name,
            "from_path": event.src_path,
            "to_path": event.dest_path,
            "type": item_type
        })
    
    def get_recent_activities(self, hours: int = 24) -> List[Dict]:
        """Get activities from the last N hours"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        recent = []
        
        for activity in self.activities:
            activity_time = datetime.fromisoformat(activity["timestamp"]).timestamp()
            if activity_time >= cutoff:
                recent.append(activity)
        
        return recent
    
    def get_activity_summary(self, hours: int = 24) -> Dict[str, int]:
        """Get summary of activities"""
        recent = self.get_recent_activities(hours)
        summary = {
            "files_created": 0,
            "files_deleted": 0,
            "files_modified": 0,
            "files_moved": 0,
            "folders_created": 0,
            "folders_deleted": 0,
            "folders_modified": 0,
            "folders_moved": 0
        }
        
        for activity in recent:
            action = activity["action"]
            if action in summary:
                summary[action] += 1
        
        return summary
    
    def clear_old_activities(self, days: int = 7):
        """Clear activities older than N days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        self.activities = [
            activity for activity in self.activities
            if datetime.fromisoformat(activity["timestamp"]).timestamp() >= cutoff
        ]
        self.save_activities()

def start_activity_monitoring(desktop_path: str = None) -> FolderlyActivityTracker:
    """Start monitoring desktop activities"""
    tracker = FolderlyActivityTracker(desktop_path)
    observer = Observer()
    observer.schedule(tracker, tracker.desktop_path, recursive=False)
    observer.start()
    
    return tracker, observer

def show_activity_summary(tracker: FolderlyActivityTracker):
    """Show user's recent activity summary - returns data instead of printing"""
    summary = tracker.get_activity_summary()
    recent_activities = tracker.get_recent_activities()
    
    if not recent_activities:
        return {
            "success": True,
            "message": "No recent activity found",
            "summary": summary,
            "activities": []
        }
    
    # Format activities for return
    formatted_activities = []
    for activity in recent_activities[-10:]:  # Last 10 activities
        timestamp = datetime.fromisoformat(activity["timestamp"]).strftime("%H:%M")
        action = activity["action"]
        details = activity["details"]
        
        if action == "file_created":
            formatted_activities.append(f"{timestamp} 📄 Created file: {details['filename']}")
        elif action == "folder_created":
            formatted_activities.append(f"{timestamp} 📁 Created folder: {details['filename']}")
        elif action == "file_deleted":
            formatted_activities.append(f"{timestamp} 🗑️ Deleted file: {details['filename']}")
        elif action == "folder_deleted":
            formatted_activities.append(f"{timestamp} 🗑️ Deleted folder: {details['filename']}")
        elif action == "file_modified":
            formatted_activities.append(f"{timestamp} ✏️ Modified file: {details['filename']}")
        elif action == "folder_modified":
            formatted_activities.append(f"{timestamp} ✏️ Modified folder: {details['filename']}")
        elif action == "file_moved":
            formatted_activities.append(f"{timestamp} 📦 Moved file: {details['old_name']} → {details['new_name']}")
        elif action == "folder_moved":
            formatted_activities.append(f"{timestamp} 📦 Moved folder: {details['old_name']} → {details['new_name']}")
    
    return {
        "success": True,
        "message": "Activity summary retrieved successfully",
        "summary": summary,
        "activities": formatted_activities,
        "total_activities": len(recent_activities)
    } 