#!/usr/bin/env python3
"""
Test suite for tool_selector.py
"""

import unittest
import json
import os
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tool_selector import ToolSelector


class TestToolSelectorBasic(unittest.TestCase):
    """Basic test cases for ToolSelector that don't require API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a ToolSelector instance that won't make API calls
        try:
            self.selector = ToolSelector()
        except Exception as e:
            # If initialization fails, skip these tests
            self.skipTest(f"Cannot initialize ToolSelector: {e}")
    
    def test_load_tools_data(self):
        """Test loading tools data from tools_list.md."""
        tools_data = self.selector._load_tools_data()
        self.assertIsInstance(tools_data, dict)
        self.assertGreater(len(tools_data), 0)
        
        # Check that some expected tools are present
        expected_tools = ['coingecko.py', 'top_coins.py', 'coin_data_by_id.py']
        for tool in expected_tools:
            self.assertIn(tool, tools_data)
    
    def test_fallback_search(self):
        """Test fallback search functionality."""
        # Test fallback search directly (doesn't use API)
        results = self.selector._fallback_search("bitcoin", max_results=3)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)
        
        # Check result structure
        for result in results:
            self.assertIn('name', result)
            self.assertIn('relevance_score', result)
            self.assertIn('reason', result)
            self.assertIn('full_content', result)
    
    def test_get_tool_details(self):
        """Test getting tool details."""
        # Test with existing tool
        details = self.selector.get_tool_details('coingecko.py')
        self.assertIsNotNone(details)
        self.assertIn('name', details)
        self.assertIn('purpose', details)
        
        # Test with non-existing tool
        details = self.selector.get_tool_details('nonexistent.py')
        self.assertIsNone(details)
    
    def test_list_all_tools(self):
        """Test listing all available tools."""
        tools = self.selector.list_all_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check that all items are strings
        for tool in tools:
            self.assertIsInstance(tool, str)
            self.assertTrue(tool.endswith('.py'))
    
    def test_tools_data_structure(self):
        """Test the structure of loaded tools data."""
        for tool_name, tool_data in self.selector.tools_data.items():
            self.assertIsInstance(tool_name, str)
            self.assertIsInstance(tool_data, dict)
            
            # Check required fields
            required_fields = ['name', 'content', 'purpose', 'main_function', 'description', 'full_content']
            for field in required_fields:
                self.assertIn(field, tool_data)
    
    def test_fallback_search_specific_queries(self):
        """Test fallback search with specific queries."""
        test_cases = [
            ("OHLC", ["coin_ohlc_by_id.py"]),
            ("top coins", ["top_coins.py"]),
            ("historical", ["coin_historical_data_by_id.py", "coin_historical_chart_by_id.py"]),
            ("market", ["coins_list_market_data.py"]),
            ("DEX", ["dex_volume_ranking.py"])
        ]
        
        for query, expected_tools in test_cases:
            results = self.selector._fallback_search(query, max_results=5)
            self.assertGreater(len(results), 0, f"No results for query: {query}")
            
            # Check if at least one expected tool is in results
            result_names = [r['name'] for r in results]
            found_expected = any(tool in result_names for tool in expected_tools)
            self.assertTrue(found_expected, 
                          f"Expected tools {expected_tools} not found in results {result_names} for query: {query}")
    
    def test_fallback_search_edge_cases(self):
        """Test fallback search with edge cases."""
        # Test with empty query
        results = self.selector._fallback_search("", max_results=3)
        self.assertIsInstance(results, list)
        
        # Test with zero max_results
        results = self.selector._fallback_search("bitcoin", max_results=0)
        self.assertEqual(len(results), 0)
        
        # Test with special characters
        results = self.selector._fallback_search("bitcoin & ethereum @# $%", max_results=3)
        self.assertIsInstance(results, list)
    
    def test_fallback_search_scoring(self):
        """Test fallback search scoring mechanism."""
        results = self.selector._fallback_search("bitcoin", max_results=5)
        
        # Check that results are sorted by score (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                self.assertGreaterEqual(results[i]['relevance_score'], 
                                      results[i + 1]['relevance_score'])
        
        # Check score range
        for result in results:
            self.assertGreaterEqual(result['relevance_score'], 0)
            self.assertLessEqual(result['relevance_score'], 100)


class TestToolSelectorWithoutAPI(unittest.TestCase):
    """Test ToolSelector behavior when API is not available."""
    
    def setUp(self):
        """Set up test fixtures with invalid API key."""
        # Temporarily remove API key to test fallback
        self.original_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if 'ANTHROPIC_API_KEY' in os.environ:
            del os.environ['ANTHROPIC_API_KEY']
    
    def tearDown(self):
        """Restore original API key."""
        if self.original_api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.original_api_key
    
    def test_initialization_without_api_key(self):
        """Test that ToolSelector raises error when API key is missing."""
        # Also remove from dotenv by temporarily renaming .env file
        env_file = Path(__file__).parent.parent.parent / '.env'
        env_backup = env_file.with_suffix('.env.backup')
        
        try:
            if env_file.exists():
                env_file.rename(env_backup)
            
            with self.assertRaises(ValueError):
                ToolSelector()
        finally:
            # Restore .env file
            if env_backup.exists():
                env_backup.rename(env_file)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)