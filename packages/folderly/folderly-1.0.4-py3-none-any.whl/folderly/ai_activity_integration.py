#!/usr/bin/env python3
"""
AI Integration with Activity Tracker
Analyzes user file activity patterns and provides insights
"""

from folderly.activity_tracker import FolderlyActivityTracker, show_activity_summary
from datetime import datetime

def analyze_activity_with_ai(tracker: FolderlyActivityTracker):
    """Use AI to analyze user activity patterns"""
    
    # Get recent activities
    activities = tracker.get_recent_activities(24)  # Last 24 hours
    
    if not activities:
        return "No recent activity to analyze."
    
    # Prepare activity summary for AI
    activity_summary = []
    for activity in activities:
        timestamp = datetime.fromisoformat(activity["timestamp"]).strftime("%H:%M")
        action = activity["action"]
        details = activity["details"]
        
        if action == "file_created":
            activity_summary.append(f"{timestamp}: Created {details['filename']}")
        elif action == "file_moved":
            activity_summary.append(f"{timestamp}: Moved {details['old_name']} → {details['new_name']}")
        elif action == "file_deleted":
            activity_summary.append(f"{timestamp}: Deleted {details['filename']}")
        elif action == "file_modified":
            activity_summary.append(f"{timestamp}: Modified {details['filename']}")
    
    # Create AI prompt
    prompt = f"""
    Analyze this user's file activity from the last 24 hours:
    
    {chr(10).join(activity_summary)}
    
    Provide insights about:
    1. Organization patterns
    2. File management habits
    3. Potential improvements
    4. Productivity observations
    
    Keep it friendly and helpful.
    """
    
    # For now, return a simple analysis without API call
    return f"Based on your activity: {chr(10).join(activity_summary[:3])} - You've been working with files. Consider organizing them into folders for better structure."

def get_ai_activity_insights(tracker: FolderlyActivityTracker):
    """Get AI-powered insights about user activity - returns data instead of printing"""
    
    insights = analyze_activity_with_ai(tracker)
    return {
        "success": True,
        "insights": insights,
        "message": "AI analysis completed"
    }

def suggest_ai_actions(tracker: FolderlyActivityTracker):
    """Use AI to suggest actions based on activity - returns data instead of printing"""
    
    activities = tracker.get_recent_activities(24)
    
    if not activities:
        return {
            "success": True,
            "suggestions": [],
            "message": "No recent activity to suggest actions for."
        }
    
    # Count activity types
    created_files = [a for a in activities if a["action"] == "file_created"]
    moved_files = [a for a in activities if a["action"] == "file_moved"]
    
    suggestions = []
    
    if len(created_files) > 5:
        suggestions.append("📁 You created many files today. Consider organizing them into folders.")
    
    if len(moved_files) > 3:
        suggestions.append("📦 You moved several files. Great organization work!")
    
    if len(created_files) == 0 and len(moved_files) == 0:
        suggestions.append("📭 No file activity today. Everything organized?")
    
    return {
        "success": True,
        "suggestions": suggestions,
        "message": f"Found {len(suggestions)} suggestions"
    }

def show_ai_enhanced_activity(tracker: FolderlyActivityTracker):
    """Show activity summary with AI insights - returns data instead of printing"""
    
    # Get activity summary
    activity_data = show_activity_summary(tracker)
    
    # Get AI insights
    ai_insights = get_ai_activity_insights(tracker)
    
    # Get AI suggestions
    ai_suggestions = suggest_ai_actions(tracker)
    
    return {
        "success": True,
        "activity_data": activity_data,
        "ai_insights": ai_insights,
        "ai_suggestions": ai_suggestions,
        "message": "Complete activity analysis with AI insights"
    } 