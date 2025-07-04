#!/usr/bin/env python3
"""
CLI Commands Test Script

This script tests all CLI commands in the tools directory to ensure they are working properly.
It runs each tool with basic parameters and verifies that they execute without errors.

Usage:
    python test_cli_commands.py
    python test_cli_commands.py --verbose
    python test_cli_commands.py --test-specific-tool top_coins
"""

import subprocess
import sys
import os
import argparse
import time
from typing import List, Dict, Tuple

# Add the tools directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class CLITester:
    """Test CLI commands for all tools."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.tools_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = []
        
    def run_command(self, command: List[str], tool_name: str) -> Tuple[bool, str]:
        """Run a CLI command and return success status and output."""
        try:
            if self.verbose:
                print(f"Running: {' '.join(command)}")
            
            # Run the command with a timeout
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=self.tools_dir
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            if self.verbose:
                print(f"Return code: {result.returncode}")
                if output:
                    print(f"Output: {output[:200]}...")
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, f"Error running command: {str(e)}"
    
    def test_tool(self, tool_name: str, command: List[str]) -> Dict:
        """Test a specific tool with given command."""
        print(f"Testing {tool_name}...")
        
        start_time = time.time()
        success, output = self.run_command(command, tool_name)
        end_time = time.time()
        
        result = {
            'tool': tool_name,
            'command': ' '.join(command),
            'success': success,
            'output': output,
            'duration': end_time - start_time
        }
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} ({result['duration']:.2f}s)")
        
        if not success and self.verbose:
            print(f"  Error: {output}")
        
        self.results.append(result)
        return result
    
    def test_all_tools(self) -> None:
        """Test all CLI tools."""
        print("Testing all CLI tools...")
        print("=" * 50)
        
        # Define test commands for each tool
        test_commands = [
            # Core CoinGecko API Tools
            ('coingecko.py', [
                'python', 'coingecko.py', 
                '--symbol', 'BTC_USD', 
                '--interval', '1d', 
                '--start_time', '2024-01-01', 
                '--end_time', '2024-01-02'
            ]),
            
            # Top Coins
            ('top_coins.py', [
                'python', 'top_coins.py', 
                '--n', '5'
            ]),
            
            # Coin Data
            ('coin_data_by_id.py', [
                'python', 'coin_data_by_id.py', 
                '--coin_id', 'bitcoin'
            ]),
            
            # Coin Tickers
            ('coin_tickers_by_id.py', [
                'python', 'coin_tickers_by_id.py', 
                '--coin_id', 'bitcoin'
            ]),
            
            # Historical Data
            ('coin_historical_data_by_id.py', [
                'python', 'coin_historical_data_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--date', '01-01-2024'
            ]),
            
            # Historical Chart
            ('coin_historical_chart_by_id.py', [
                'python', 'coin_historical_chart_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--days', '7'
            ]),
            
            # Historical Chart Range
            ('coin_historical_chart_range_by_id.py', [
                'python', 'coin_historical_chart_range_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--from_timestamp', '1704067200',  # 2024-01-01
                '--to_timestamp', '1704153600'     # 2024-01-02
            ]),
            
            # OHLC Data
            ('coin_ohlc_by_id.py', [
                'python', 'coin_ohlc_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--days', '7'
            ]),
            
            # OHLC Range
            ('coin_ohlc_range_by_id.py', [
                'python', 'coin_ohlc_range_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--from_timestamp', '1704067200',  # 2024-01-01
                '--to_timestamp', '1704153600'     # 2024-01-02
            ]),
            
            # Coins List
            ('coins_list.py', [
                'python', 'coins_list.py', 
                '--limit', '5'
            ]),
            
            # Coins List Market Data
            ('coins_list_market_data.py', [
                'python', 'coins_list_market_data.py', 
                '--per_page', '5'
            ]),
            
            # Coins Gainers Losers
            ('coins_gainers_losers.py', [
                'python', 'coins_gainers_losers.py'
            ]),
            
            # DEX Volume Ranking
            ('dex_volume_ranking.py', [
                'python', 'dex_volume_ranking.py', 
                '5'
            ]),
            
            # CoinGlass API Tools (23 endpoints) - NOTE: These need CLI implementation first
            ('coinglass/coin_taker_buy_sell_volume_history.py', [
                'python', 'coinglass/coin_taker_buy_sell_volume_history.py', 
                '--symbol', 'BTC'
            ]),
            ('coinglass/funding_rate_arbitrage.py', [
                'python', 'coinglass/funding_rate_arbitrage.py', 
                '--symbol', 'BTC'
            ]),
            ('coinglass/funding_rate_exchange_list.py', [
                'python', 'coinglass/funding_rate_exchange_list.py'
            ]),
            ('coinglass/futures_supported_coins.py', [
                'python', 'coinglass/futures_supported_coins.py'
            ]),
            ('coinglass/index_fear_greed_history.py', [
                'python', 'coinglass/index_fear_greed_history.py'
            ]),
            ('coinglass/liquidation_coin_list.py', [
                'python', 'coinglass/liquidation_coin_list.py'
            ]),
            ('coinglass/liquidation_exchange_list.py', [
                'python', 'coinglass/liquidation_exchange_list.py'
            ]),
            ('coinglass/open_interest_exchange_list.py', [
                'python', 'coinglass/open_interest_exchange_list.py'
            ]),
            ('coinglass/spot_supported_coins.py', [
                'python', 'coinglass/spot_supported_coins.py'
            ]),
            
            # LunaCrush API Tools (10 endpoints) - NOTE: These need CLI implementation first
            ('lunacrush/coins_list.py', [
                'python', 'lunacrush/coins_list.py', 
                '--limit', '10'
            ]),
            ('lunacrush/coin_meta.py', [
                'python', 'lunacrush/coin_meta.py', 
                '--symbol', 'BTC'
            ]),
            ('lunacrush/coin_time_series.py', [
                'python', 'lunacrush/coin_time_series.py', 
                '--symbol', 'BTC', '--interval', '1d'
            ]),
            ('lunacrush/topic_details.py', [
                'python', 'lunacrush/topic_details.py', 
                '--topic', 'bitcoin'
            ]),
            ('lunacrush/category_details.py', [
                'python', 'lunacrush/category_details.py', 
                '--category', 'defi'
            ]),
        ]
        
        # Test each tool
        for tool_name, command in test_commands:
            self.test_tool(tool_name, command)
            time.sleep(1)  # Small delay between tests
        
        # Print summary
        self.print_summary()
    
    def test_specific_tool(self, tool_name: str) -> None:
        """Test a specific tool."""
        print(f"Testing specific tool: {tool_name}")
        print("=" * 50)
        
        # Find the tool in test commands
        test_commands = [
            ('coingecko.py', [
                'python', 'coingecko.py', 
                '--symbol', 'BTC_USD', 
                '--interval', '1d', 
                '--start_time', '2024-01-01', 
                '--end_time', '2024-01-02'
            ]),
            ('top_coins.py', [
                'python', 'top_coins.py', 
                '--n', '5'
            ]),
            ('coin_data_by_id.py', [
                'python', 'coin_data_by_id.py', 
                '--coin_id', 'bitcoin'
            ]),
            ('coin_tickers_by_id.py', [
                'python', 'coin_tickers_by_id.py', 
                '--coin_id', 'bitcoin'
            ]),
            ('coin_historical_data_by_id.py', [
                'python', 'coin_historical_data_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--date', '01-01-2024'
            ]),
            ('coin_historical_chart_by_id.py', [
                'python', 'coin_historical_chart_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--days', '7'
            ]),
            ('coin_historical_chart_range_by_id.py', [
                'python', 'coin_historical_chart_range_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--from_timestamp', '1704067200',
                '--to_timestamp', '1704153600'
            ]),
            ('coin_ohlc_by_id.py', [
                'python', 'coin_ohlc_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--days', '7'
            ]),
            ('coin_ohlc_range_by_id.py', [
                'python', 'coin_ohlc_range_by_id.py', 
                '--coin_id', 'bitcoin', 
                '--from_timestamp', '1704067200',
                '--to_timestamp', '1704153600'
            ]),
            ('coins_list.py', [
                'python', 'coins_list.py', 
                '--limit', '5'
            ]),
            ('coins_list_market_data.py', [
                'python', 'coins_list_market_data.py', 
                '--per_page', '5'
            ]),
            ('coins_gainers_losers.py', [
                'python', 'coins_gainers_losers.py'
            ]),
            ('dex_volume_ranking.py', [
                'python', 'dex_volume_ranking.py', 
                '5'
            ]),
            
            # CoinGlass API Tools (23 endpoints) - NOTE: These need CLI implementation first
            ('coinglass/coin_taker_buy_sell_volume_history.py', [
                'python', 'coinglass/coin_taker_buy_sell_volume_history.py', 
                '--symbol', 'BTC'
            ]),
            ('coinglass/funding_rate_arbitrage.py', [
                'python', 'coinglass/funding_rate_arbitrage.py', 
                '--symbol', 'BTC'
            ]),
            ('coinglass/funding_rate_exchange_list.py', [
                'python', 'coinglass/funding_rate_exchange_list.py'
            ]),
            ('coinglass/futures_supported_coins.py', [
                'python', 'coinglass/futures_supported_coins.py'
            ]),
            ('coinglass/index_fear_greed_history.py', [
                'python', 'coinglass/index_fear_greed_history.py'
            ]),
            ('coinglass/liquidation_coin_list.py', [
                'python', 'coinglass/liquidation_coin_list.py'
            ]),
            ('coinglass/liquidation_exchange_list.py', [
                'python', 'coinglass/liquidation_exchange_list.py'
            ]),
            ('coinglass/open_interest_exchange_list.py', [
                'python', 'coinglass/open_interest_exchange_list.py'
            ]),
            ('coinglass/spot_supported_coins.py', [
                'python', 'coinglass/spot_supported_coins.py'
            ]),
            
            # LunaCrush API Tools (10 endpoints) - NOTE: These need CLI implementation first
            ('lunacrush/coins_list.py', [
                'python', 'lunacrush/coins_list.py', 
                '--limit', '10'
            ]),
            ('lunacrush/coin_meta.py', [
                'python', 'lunacrush/coin_meta.py', 
                '--symbol', 'BTC'
            ]),
            ('lunacrush/coin_time_series.py', [
                'python', 'lunacrush/coin_time_series.py', 
                '--symbol', 'BTC', '--interval', '1d'
            ]),
            ('lunacrush/topic_details.py', [
                'python', 'lunacrush/topic_details.py', 
                '--topic', 'bitcoin'
            ]),
            ('lunacrush/category_details.py', [
                'python', 'lunacrush/category_details.py', 
                '--category', 'defi'
            ]),
        ]
        
        for name, command in test_commands:
            if name == tool_name:
                self.test_tool(name, command)
                break
        else:
            print(f"❌ Tool '{tool_name}' not found in test commands")
            return
        
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print test summary."""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['tool']}: {result['output'][:100]}...")
        
        if passed_tests == total_tests:
            print("\n🎉 All CLI tests passed!")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Check the output above for details.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test CLI commands for all tools")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--test-specific-tool', '-t', type=str, help='Test a specific tool')
    
    args = parser.parse_args()
    
    tester = CLITester(verbose=args.verbose)
    
    if args.test_specific_tool:
        tester.test_specific_tool(args.test_specific_tool)
    else:
        tester.test_all_tools()


if __name__ == "__main__":
    main() 