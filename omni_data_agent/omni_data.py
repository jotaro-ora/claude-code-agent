#!/usr/bin/env python3
"""
Omni Data Agent CLI Tool

A CLI tool that uses Claude Code SDK to handle data requests intelligently.
This tool can process queries about cryptocurrency data using available tools.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add the project root to Python path for importing tools
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions

# Load environment variables from project root
load_dotenv(project_root / '.env')

class OmniDataAgent:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.project_root = project_root
        
    def load_system_prompt(self):
        """Load system prompt from README.md file."""
        readme_path = self.project_root / 'omni_data_agent' / 'README.md'
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            system_prompt = f"""
You are an expert data analyst with access to cryptocurrency data tools. Your task is to handle data requests efficiently following the instructions below.

Current working directory: {self.project_root}
Available tools directory: {self.project_root}/tools/

{readme_content}

Important Notes:
- Environment variables are already loaded from .env file in the project root
- You have access to all tools listed in tools/tools_list.md
- Follow the efficiency principles strictly - return only what the user requested
"""
            return system_prompt
            
        except Exception as e:
            # Fallback to basic prompt if README can't be read
            return f"""
You are an expert data analyst with access to cryptocurrency data tools. 
Current working directory: {self.project_root}
Available tools directory: {self.project_root}/tools/
Always read tools/tools_list.md first to understand available tools.
Error loading README instructions: {str(e)}
"""

    async def process_query(self, user_query):
        """Process a data query using Claude Code SDK with streaming output."""
        
        system_prompt = self.load_system_prompt()

        try:
            # Use Claude Code SDK to process the query
            options = ClaudeCodeOptions(
                system_prompt=system_prompt,
                cwd=str(self.project_root),
                permission_mode='bypassPermissions'  # Allow all tools for automation
            )
            
            print("🤖 Processing your query...\n", flush=True)
            
            response_parts = []
            message_count = 0
            
            async for message in query(prompt=user_query, options=options):
                message_count += 1
                
                # Print streaming status
                if message_count % 3 == 1:
                    print("⚡ Analyzing...", flush=True)
                elif message_count % 3 == 2:
                    print("🔍 Searching tools...", flush=True)
                else:
                    print("📊 Processing data...", flush=True)
                
                if hasattr(message, 'content') and message.content:
                    # Handle both string and list content
                    if isinstance(message.content, list):
                        for item in message.content:
                            if isinstance(item, str):
                                response_parts.append(item)
                                # Print partial results for user feedback
                                if len(item) > 50:  # Only print substantial content
                                    print(f"📝 {item[:100]}{'...' if len(item) > 100 else ''}", flush=True)
                            elif hasattr(item, 'text'):
                                response_parts.append(item.text)
                                if len(item.text) > 50:
                                    print(f"📝 {item.text[:100]}{'...' if len(item.text) > 100 else ''}", flush=True)
                            else:
                                content_str = str(item)
                                response_parts.append(content_str)
                                if len(content_str) > 50:
                                    print(f"📝 {content_str[:100]}{'...' if len(content_str) > 100 else ''}", flush=True)
                    else:
                        content_str = str(message.content)
                        response_parts.append(content_str)
                        if len(content_str) > 50:
                            print(f"📝 {content_str[:100]}{'...' if len(content_str) > 100 else ''}", flush=True)
            
            print("\n✅ Query completed!\n" + "="*50 + "\n", flush=True)
            return '\n'.join(response_parts) if response_parts else "No response generated"
            
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"

async def main():
    parser = argparse.ArgumentParser(
        description="Omni Data Agent - Intelligent cryptocurrency data query tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python omni_data_agent/omni_data.py "What's BTC price today"
  python omni_data_agent/omni_data.py "Compare BTC and ETH 24h volumes"
  python omni_data_agent/omni_data.py "Show top 10 cryptocurrencies by market cap"
        """
    )
    
    parser.add_argument('query', help='Data query to process')
    
    args = parser.parse_args()
    
    try:
        agent = OmniDataAgent()
        result = await agent.process_query(args.query)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())