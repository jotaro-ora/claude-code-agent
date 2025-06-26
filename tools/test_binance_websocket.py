#!/usr/bin/env python3
"""
Simple test script for Binance WebSocket tool

This script tests the basic functionality of the Binance WebSocket API tool
by connecting to Binance, subscribing to a few popular cryptocurrencies,
and monitoring their real-time price updates for a short period.

Usage:
    python tools/test_binance_websocket.py

Requirements:
    - websockets package: pip install websockets
    - aiohttp package: pip install aiohttp
    - No API key required (uses public data streams)

Test Duration: 30 seconds (configurable)
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from archived.binance_websocket import BinanceWebSocket, monitor_symbols
    print("✅ Successfully imported BinanceWebSocket")
except ImportError as e:
    print(f"❌ Failed to import BinanceWebSocket: {e}")
    print("Please install required dependencies:")
    print("pip install websockets aiohttp")
    sys.exit(1)


class TestMonitor:
    """Test class for Binance WebSocket functionality."""
    
    def __init__(self):
        self.price_updates = {}
        self.start_time = None
        self.test_duration = 30  # seconds
        self.monitor = None
    
    async def price_callback(self, symbol: str, price_data: dict):
        """Handle price updates from WebSocket."""
        current_time = time.time()
        
        # Store latest price for each symbol
        self.price_updates[symbol] = {
            'price': price_data['price'],
            'volume': price_data['volume'],
            'change': price_data['change'],
            'timestamp': current_time,
            'formatted_time': time.strftime('%H:%M:%S', time.localtime(current_time))
        }
        
        # Print formatted price update
        print(f"[{self.price_updates[symbol]['formatted_time']}] "
              f"{symbol.upper()}: ${price_data['price']:.4f} "
              f"({price_data['change']:+.2f}%) "
              f"Vol: {price_data['volume']:.2f}")
    
    async def run_basic_test(self):
        """Run basic connectivity and subscription test."""
        print("\n🚀 Testing Binance WebSocket Basic Functionality")
        print("=" * 60)
        
        # Test symbols (popular cryptocurrencies)
        test_symbols = ['btcusdt', 'ethusdt', 'adausdt', 'solusdt']
        
        try:
            # Create monitor instance
            self.monitor = BinanceWebSocket(
                price_callback=self.price_callback,
                auto_reconnect=True,
                log_level="INFO"
            )
            
            print(f"📡 Connecting to Binance WebSocket...")
            
            # Connect to WebSocket
            await self.monitor.connect()
            print("✅ Connected successfully")
            
            print(f"📊 Subscribing to {len(test_symbols)} symbols...")
            
            # Subscribe to symbols
            success = await self.monitor.subscribe(test_symbols)
            if success:
                print("✅ Subscriptions successful")
            else:
                print("❌ Some subscriptions failed")
            
            # Get subscribed symbols
            subscribed = await self.monitor.get_subscribed_symbols()
            print(f"📋 Currently subscribed: {', '.join(subscribed)}")
            
            print(f"\n🔄 Starting price monitoring for {self.test_duration} seconds...")
            print("Press Ctrl+C to stop early")
            print("-" * 60)
            
            # Start monitoring
            self.start_time = time.time()
            await self.monitor.start_monitoring()
            
        except KeyboardInterrupt:
            print("\n⏹️  Test stopped by user")
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
        finally:
            await self.cleanup()
    
    async def run_convenience_test(self):
        """Test the convenience function."""
        print("\n🚀 Testing Convenience Function")
        print("=" * 60)
        
        test_symbols = ['btcusdt', 'ethusdt']
        
        try:
            print(f"📡 Using convenience function to monitor {len(test_symbols)} symbols...")
            
            # Use convenience function
            monitor = await monitor_symbols(
                symbols=test_symbols,
                callback=self.price_callback,
                auto_reconnect=True
            )
            
            print("✅ Convenience function successful")
            print(f"📋 Subscribed symbols: {await monitor.get_subscribed_symbols()}")
            
            # Monitor for 10 seconds
            print("🔄 Monitoring for 10 seconds...")
            await asyncio.sleep(10)
            
            await monitor.disconnect()
            print("✅ Convenience test completed")
            
        except Exception as e:
            print(f"❌ Convenience test failed: {e}")
    
    async def run_error_handling_test(self):
        """Test error handling with invalid inputs."""
        print("\n🚀 Testing Error Handling")
        print("=" * 60)
        
        try:
            # Test with invalid callback
            try:
                monitor = BinanceWebSocket("not_a_function")
                print("❌ Should have raised ValueError for invalid callback")
            except ValueError as e:
                print(f"✅ Correctly caught invalid callback: {e}")
            
            # Test with empty symbols list
            monitor = BinanceWebSocket(self.price_callback)
            await monitor.connect()
            
            try:
                await monitor.subscribe([])
                print("❌ Should have raised ValueError for empty symbols")
            except ValueError as e:
                print(f"✅ Correctly caught empty symbols: {e}")
            
            await monitor.disconnect()
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
    
    async def cleanup(self):
        """Clean up resources."""
        if self.monitor:
            try:
                await self.monitor.disconnect()
                print("✅ Cleanup completed")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")
    
    def print_summary(self):
        """Print test summary."""
        if not self.price_updates:
            print("\n❌ No price updates received during test")
            return
        
        print("\n📊 Test Summary")
        print("=" * 60)
        print(f"📈 Received updates for {len(self.price_updates)} symbols:")
        
        for symbol, data in self.price_updates.items():
            print(f"   {symbol.upper()}: ${data['price']:.4f} "
                  f"({data['change']:+.2f}%) at {data['formatted_time']}")
        
        if self.start_time:
            duration = time.time() - self.start_time
            print(f"\n⏱️  Test duration: {duration:.1f} seconds")
            print(f"📊 Average updates per second: {len(self.price_updates) / duration:.2f}")


async def main():
    """Main test function."""
    print("🧪 Binance WebSocket Test Suite")
    print("=" * 60)
    
    # Check dependencies
    try:
        import websockets
        import aiohttp
        print("✅ Required dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install: pip install websockets aiohttp")
        return
    
    test_monitor = TestMonitor()
    
    try:
        # Run basic functionality test
        await test_monitor.run_basic_test()
        
        # Run convenience function test
        await test_monitor.run_convenience_test()
        
        # Run error handling test
        await test_monitor.run_error_handling_test()
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
    
    finally:
        # Print summary
        test_monitor.print_summary()
        print("\n🏁 Test suite completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}") 