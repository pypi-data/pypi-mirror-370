#!/usr/bin/env python3
"""
Folderly CLI - AI-Powered Desktop Organization Tool
"""

import os
import json
import openai
import asyncio
import sys
from pathlib import Path
from src.ai.prompts import (
    load_system_prompt, load_welcome_message, 
    load_goodbye_message, load_empty_input_message, load_error_message
)


async def start_ai_chat():
    """Start AI chat mode - the only function users need"""
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Error: No API key available.")
        print("Please set OPENAI_API_KEY environment variable:")
        print("   Windows: $env:OPENAI_API_KEY='your_key_here'")
        print("   macOS/Linux: export OPENAI_API_KEY='your_key_here'")
        return
    
    print("✅ API Key loaded successfully!")
    
    # NOW import and use the working AI integration
    from src.ai.ai_integration import chat_with_ai
    await chat_with_ai()


async def main():
    """Main entry point - starts AI chat immediately"""
    await start_ai_chat()


def main_sync():
    """Synchronous wrapper for async main function"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
