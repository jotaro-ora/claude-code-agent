#!/usr/bin/env python3
"""
Tool Selector - AI-powered tool filtering for efficient tool discovery.

Uses Claude AI to intelligently filter and recommend tools based on natural language queries.
Designed to be fast, cost-effective, and scalable for hundreds of tools.
"""

import os
import json
import re
import argparse
from typing import List, Dict, Any, Optional
from pathlib import Path

# Optional dependencies
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ToolSelector:
    """AI-powered tool selector for efficient tool discovery."""
    
    def __init__(self, tools_dir: str = None):
        """Initialize the tool selector."""
        # Load environment variables from project root
        project_root = Path(__file__).parent.parent
        if DOTENV_AVAILABLE:
            load_dotenv(project_root / '.env')
        
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.ai_available = ANTHROPIC_AVAILABLE and self.api_key
        
        if self.ai_available:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            
        self.tools_dir = Path(tools_dir) if tools_dir else Path(__file__).parent
        self.tools_list_file = self.tools_dir / 'tools_list.md'
        
        # Load tools data
        self.tools_data = self._load_tools_data()
    
    def _load_tools_data(self) -> Dict[str, Dict[str, Any]]:
        """Load and parse tools data from tools_list.md."""
        if not self.tools_list_file.exists():
            return {}
        
        with open(self.tools_list_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tools = {}
        current_tool = None
        
        # Parse the markdown content
        lines = content.split('\n')
        for line in lines:
            # Match tool headers like "### 1. coingecko.py"
            tool_match = re.match(r'^### \d+\. (.+\.py)$', line)
            if tool_match:
                current_tool = tool_match.group(1)
                tools[current_tool] = {'name': current_tool, 'content': []}
                continue
            
            # Collect content for current tool
            if current_tool and line.strip():
                tools[current_tool]['content'].append(line)
        
        # Process tool data
        for tool_name, tool_data in tools.items():
            content_text = '\n'.join(tool_data['content'])
            
            # Extract key information
            purpose_match = re.search(r'\*\*Purpose\*\*: (.+)', content_text)
            main_func_match = re.search(r'\*\*Main Function\*\*: `(.+)`', content_text)
            description_match = re.search(r'\*\*Description\*\*: (.+)', content_text)
            
            tool_data.update({
                'purpose': purpose_match.group(1) if purpose_match else '',
                'main_function': main_func_match.group(1) if main_func_match else '',
                'description': description_match.group(1) if description_match else '',
                'full_content': content_text
            })
        
        return tools
    
    def search_tools(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search tools using AI-powered filtering or fallback to text matching."""
        if not self.tools_data:
            return []
        
        # Use AI if available, otherwise fallback to text matching
        if self.ai_available and self.client:
            return self._ai_search(query, max_results)
        else:
            print("AI search not available, using fallback text matching...")
            return self._fallback_search(query, max_results)
    
    def _ai_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """AI-powered search using Claude."""
        # Create a compact representation of tools for AI processing
        tools_summary = []
        for tool_name, tool_data in self.tools_data.items():
            summary = {
                'name': tool_name,
                'purpose': tool_data.get('purpose', ''),
                'main_function': tool_data.get('main_function', ''),
                'description': tool_data.get('description', '')
            }
            tools_summary.append(summary)
        
        # Prepare prompt for Claude
        prompt = f"""You are a tool recommendation system. Given a user query, select the most relevant tools from the available options.

User Query: "{query}"

Available Tools:
{json.dumps(tools_summary, indent=2)}

Please analyze the query and return a JSON array of the top {max_results} most relevant tools, ordered by relevance (most relevant first).

For each tool, include:
- name: the tool filename
- relevance_score: a number from 0-100 indicating how relevant it is
- reason: a brief explanation of why this tool is relevant

Return only the JSON array, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use fast, cost-effective model
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group(0))
                
                # Enrich with full tool data
                enriched_results = []
                for rec in recommendations:
                    tool_name = rec.get('name', '')
                    if tool_name in self.tools_data:
                        enriched_rec = {
                            **rec,
                            'full_content': self.tools_data[tool_name]['full_content']
                        }
                        enriched_results.append(enriched_rec)
                
                return enriched_results[:max_results]
            
        except Exception as e:
            print(f"Error querying AI: {e}")
            # Fallback to simple text matching
            return self._fallback_search(query, max_results)
        
        return []
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback search using simple text matching."""
        query_lower = query.lower()
        results = []
        
        for tool_name, tool_data in self.tools_data.items():
            score = 0
            search_text = f"{tool_data.get('purpose', '')} {tool_data.get('description', '')} {tool_name}".lower()
            
            # Simple scoring based on keyword matches
            query_words = query_lower.split()
            for word in query_words:
                if word in search_text:
                    score += search_text.count(word) * 10
            
            if score > 0:
                results.append({
                    'name': tool_name,
                    'relevance_score': min(score, 100),
                    'reason': f"Matches keywords from query",
                    'full_content': tool_data['full_content']
                })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:max_results]
    
    def get_tool_details(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific tool."""
        return self.tools_data.get(tool_name)
    
    def list_all_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools_data.keys())


def main():
    """CLI interface for tool selection."""
    parser = argparse.ArgumentParser(description='AI-powered tool selector')
    parser.add_argument('query', help='Search query for tools')
    parser.add_argument('--max-results', '-n', type=int, default=5, 
                       help='Maximum number of results to return')
    parser.add_argument('--format', choices=['json', 'text'], default='text',
                       help='Output format')
    parser.add_argument('--details', action='store_true',
                       help='Include full tool details in output')
    
    args = parser.parse_args()
    
    try:
        selector = ToolSelector()
        results = selector.search_tools(args.query, args.max_results)
        
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"Found {len(results)} relevant tools for: '{args.query}'\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['name']} (Score: {result['relevance_score']})")
                print(f"   Reason: {result['reason']}")
                
                if args.details:
                    print(f"   Details:\n{result['full_content']}")
                print()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())