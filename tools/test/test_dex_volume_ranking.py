"""
Tests for DEX Volume Ranking Tool functionality.

This test suite validates real external API connections and tool functionality.
All tests use real DeFiLlama API calls to ensure the tool works correctly.
"""

import unittest
import pandas as pd
from tools.dex_volume_ranking import get_dex_volume_ranking


class TestDexVolumeRanking(unittest.TestCase):
    """Test suite for dex_volume_ranking with real external connections."""
    
    def test_real_api_connection(self):
        """Test actual API connection - no mocking allowed."""
        # Test with small number to avoid timeout
        result = get_dex_volume_ranking(5)
        
        # Verify we got a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Verify we have the expected columns
        expected_columns = ['rank', 'name', 'total1d', 'total30d', 'change1d', 'change30d']
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Verify we have data
        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 5)
        
        # Verify data types
        self.assertTrue(all(isinstance(x, int) for x in result['rank']))
        self.assertTrue(all(isinstance(x, str) for x in result['name']))
        self.assertTrue(all(isinstance(x, (int, float)) for x in result['total1d']))
        self.assertTrue(all(isinstance(x, (int, float)) for x in result['total30d']))
    
    def test_top_10_dexes(self):
        """Test getting top 10 DEXes with real API."""
        result = get_dex_volume_ranking(10)
        
        # Verify we got up to 10 results
        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 10)
        
        # Verify ranking is correct (rank column should be 1, 2, 3, ...)
        expected_ranks = list(range(1, len(result) + 1))
        self.assertListEqual(list(result['rank']), expected_ranks)
        
        # Verify data is sorted by 24h volume (descending)
        volumes = list(result['total1d'])
        self.assertEqual(volumes, sorted(volumes, reverse=True))
    
    def test_single_dex(self):
        """Test getting single DEX (n=1)."""
        result = get_dex_volume_ranking(1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['rank'], 1)
        self.assertIsInstance(result.iloc[0]['name'], str)
        self.assertGreater(result.iloc[0]['total1d'], 0)
    
    def test_large_number_request(self):
        """Test requesting large number of DEXes."""
        # Test with 20 DEXes
        result = get_dex_volume_ranking(20)
        
        # Should return data (API typically has many DEXes)
        self.assertGreater(len(result), 0)
        self.assertLessEqual(len(result), 20)
        
        # Verify all required columns exist
        required_cols = ['rank', 'name', 'total1d', 'total30d', 'change1d', 'change30d']
        for col in required_cols:
            self.assertIn(col, result.columns)
    
    def test_input_validation(self):
        """Test input validation logic."""
        # Test invalid types
        with self.assertRaises(ValueError):
            get_dex_volume_ranking("5")
        
        with self.assertRaises(ValueError):
            get_dex_volume_ranking(5.5)
        
        with self.assertRaises(ValueError):
            get_dex_volume_ranking(None)
        
        # Test invalid values
        with self.assertRaises(ValueError):
            get_dex_volume_ranking(0)
        
        with self.assertRaises(ValueError):
            get_dex_volume_ranking(-1)
        
        with self.assertRaises(ValueError):
            get_dex_volume_ranking(101)  # Exceeds maximum
    
    def test_data_quality(self):
        """Test quality of returned data."""
        result = get_dex_volume_ranking(5)
        
        # Verify all names are non-empty strings
        for name in result['name']:
            self.assertIsInstance(name, str)
            self.assertGreater(len(name.strip()), 0)
        
        # Verify all volume values are positive
        for vol_1d in result['total1d']:
            self.assertGreater(vol_1d, 0)
        
        # Verify 30d volume is typically higher than 1d volume
        for _, row in result.iterrows():
            # 30d volume should be at least as high as 1d volume
            self.assertGreaterEqual(row['total30d'], row['total1d'])
    
    def test_zero_and_empty_values(self):
        """Test handling of zero and empty values from API."""
        # This test ensures our tool handles edge cases properly
        result = get_dex_volume_ranking(10)
        
        # Verify no empty names
        for name in result['name']:
            self.assertNotEqual(name.strip(), "")
        
        # Verify no zero or negative 24h volumes (filtered out)
        for vol in result['total1d']:
            self.assertGreater(vol, 0)
        
        # Verify no NaN values
        self.assertFalse(result.isnull().any().any())
    
    def test_api_response_format(self):
        """Test that API response format matches expectations."""
        # Test with minimal request to check response structure
        result = get_dex_volume_ranking(3)
        
        # Check that we have numeric data in expected ranges
        for _, row in result.iterrows():
            # 24h volume should be reasonable (> $1000)
            self.assertGreater(row['total1d'], 1000)
            
            # Change percentages should be reasonable (-100% to +10000%)
            self.assertGreaterEqual(row['change1d'], -100)
            self.assertLessEqual(row['change1d'], 10000)
            
            # 30d volume should be reasonable
            self.assertGreater(row['total30d'], 1000)
    
    def test_error_handling_scenarios(self):
        """Test error handling for various scenarios."""
        # Test maximum boundary
        try:
            result = get_dex_volume_ranking(50)
            # Should work or give meaningful error
            self.assertIsInstance(result, pd.DataFrame)
        except ValueError as e:
            # Should provide meaningful error message
            self.assertIn("exceed", str(e).lower())
    
    def test_ranking_consistency(self):
        """Test that ranking is consistent and logical."""
        result = get_dex_volume_ranking(5)
        
        # Check that ranks are sequential starting from 1
        ranks = list(result['rank'])
        expected_ranks = list(range(1, len(result) + 1))
        self.assertEqual(ranks, expected_ranks)
        
        # Check that volumes are in descending order
        volumes = list(result['total1d'])
        for i in range(len(volumes) - 1):
            self.assertGreaterEqual(volumes[i], volumes[i + 1])
    
    def test_data_types_consistency(self):
        """Test that data types are consistent across results."""
        result = get_dex_volume_ranking(5)
        
        # Check data types for each column
        for rank in result['rank']:
            self.assertIsInstance(rank, int)
        
        for name in result['name']:
            self.assertIsInstance(name, str)
        
        for vol in result['total1d']:
            self.assertIsInstance(vol, (int, float))
        
        for vol in result['total30d']:
            self.assertIsInstance(vol, (int, float))
        
        for change in result['change1d']:
            self.assertIsInstance(change, (int, float))
        
        for change in result['change30d']:
            self.assertIsInstance(change, (int, float))


if __name__ == "__main__":
    unittest.main()