#!/usr/bin/env python3
"""
Binance WebSocket Demo Script

This script demonstrates how to use the Binance WebSocket tool for real-time
cryptocurrency price monitoring. It showcases various features including
multiple symbol subscription, automatic reconnection, and price alerts.

Usage:
    python demo_binance_websocket.py

Features Demonstrated:
- Real-time price monitoring for multiple cryptocurrencies
- Automatic reconnection on connection loss
- Price change alerts and notifications
- Volume tracking and analysis
- Clean shutdown handling
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add tools directory to path
sys.path.append(str(Path(__file__).parent))

from binance_websocket import BinanceWebSocket, monitor_symbols


class PriceAlert:
    """Simple price alert system for demonstration."""
    
    def __init__(self, alert_threshold_percent=5.0):
        """
        Initialize price alert system.
        
        Args:
            alert_threshold_percent: Price change percentage to trigger alerts
        """
        self.alert_threshold = alert_threshold_percent
        self.last_prices = {}
        self.price_history = {}
    
    async def price_callback(self, symbol: str, price_data: dict):
        """
        Handle price updates and trigger alerts.
        
        Args:
            symbol: Trading pair symbol (e.g., 'btcusdt')
            price_data: Price and volume data from Binance
        """
        current_price = price_data['price']
        volume = price_data['volume']
        change_percent = price_data['change']
        
        # Store price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': current_price,
            'timestamp': datetime.now(),
            'volume': volume
        })
        
        # Keep only last 100 price points
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        # Display current price
        symbol_display = symbol.upper()
        print(f"📊 {symbol_display}: ${current_price:,.2f} "
              f"({change_percent:+.2f}%) Vol: {volume:,.0f}")
        
        # Check for significant price changes
        if abs(change_percent) > self.alert_threshold:
            direction = "🚀" if change_percent > 0 else "📉"
            print(f"🚨 ALERT: {symbol_display} {direction} "
                  f"{change_percent:+.2f}% change!")
        
        # Update last known price
        self.last_prices[symbol] = current_price


async def basic_monitoring_demo():
    """Demonstrate basic real-time monitoring."""
    print("🎯 Basic Monitoring Demo")
    print("=" * 50)
    
    alert_system = PriceAlert(alert_threshold_percent=3.0)
    
    # Create monitor with callback
    monitor = BinanceWebSocket(
        price_callback=alert_system.price_callback,
        auto_reconnect=True,
        log_level="INFO"
    )
    
    try:
        # Connect to Binance WebSocket
        print("🔌 Connecting to Binance WebSocket...")
        await monitor.connect()
        print("✅ Connected successfully!")
        
        # Subscribe to popular trading pairs
        symbols = ['btcusdt', 'ethusdt', 'adausdt', 'solusdt', 'dotusdt']
        print(f"📡 Subscribing to {len(symbols)} symbols...")
        
        success = await monitor.subscribe(symbols)
        if success:
            print(f"✅ Subscribed to: {', '.join(s.upper() for s in symbols)}")
        else:
            print("❌ Some subscriptions failed")
            return
        
        print("\n🚀 Starting real-time monitoring...")
        print("Press Ctrl+C to stop\n")
        
        # Start monitoring (this will run until interrupted)
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await monitor.disconnect()
        print("✅ Disconnected successfully")


async def convenience_function_demo():
    """Demonstrate using the convenience function."""
    print("🎯 Convenience Function Demo")
    print("=" * 50)
    
    price_count = 0
    
    async def simple_callback(symbol: str, price_data: dict):
        """Simple callback to count price updates."""
        nonlocal price_count
        price_count += 1
        
        if price_count % 10 == 0:  # Print every 10th update
            print(f"📊 {symbol.upper()}: ${price_data['price']:,.2f} "
                  f"(Update #{price_count})")
    
    try:
        print("🔌 Using monitor_symbols convenience function...")
        
        # Use convenience function for quick setup
        monitor = await monitor_symbols(
            symbols=['btcusdt', 'ethusdt'],
            callback=simple_callback,
            auto_reconnect=True
        )
        
        print("✅ Monitor created and connected!")
        print("🚀 Monitoring BTC/USDT and ETH/USDT...")
        print("Press Ctrl+C to stop\n")
        
        # Monitor for a limited time for demo purposes
        await asyncio.wait_for(monitor.start_monitoring(), timeout=30.0)
        
    except asyncio.TimeoutError:
        print(f"\n⏰ Demo completed after 30 seconds ({price_count} updates received)")
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            await monitor.disconnect()
        except:
            pass


async def symbol_management_demo():
    """Demonstrate dynamic symbol subscription/unsubscription."""
    print("🎯 Symbol Management Demo")
    print("=" * 50)
    
    update_count = {}
    
    async def counting_callback(symbol: str, price_data: dict):
        """Count updates per symbol."""
        if symbol not in update_count:
            update_count[symbol] = 0
        update_count[symbol] += 1
        
        if update_count[symbol] % 5 == 0:
            print(f"📊 {symbol.upper()}: ${price_data['price']:,.2f} "
                  f"(#{update_count[symbol]} updates)")
    
    monitor = BinanceWebSocket(counting_callback, auto_reconnect=True)
    
    try:
        await monitor.connect()
        print("✅ Connected to Binance WebSocket")
        
        # Subscribe to initial symbols
        initial_symbols = ['btcusdt', 'ethusdt']
        await monitor.subscribe(initial_symbols)
        print(f"📡 Subscribed to: {', '.join(s.upper() for s in initial_symbols)}")
        
        # Monitor for 10 seconds
        print("🚀 Monitoring for 10 seconds...")
        monitoring_task = asyncio.create_task(monitor.start_monitoring())
        
        await asyncio.sleep(10)
        
        # Add more symbols
        additional_symbols = ['adausdt', 'solusdt']
        await monitor.subscribe(additional_symbols)
        print(f"➕ Added symbols: {', '.join(s.upper() for s in additional_symbols)}")
        
        await asyncio.sleep(10)
        
        # Remove some symbols
        await monitor.unsubscribe(['ethusdt', 'solusdt'])
        print("➖ Removed ETH/USDT and SOL/USDT")
        
        # Check current subscriptions
        current_symbols = await monitor.get_subscribed_symbols()
        print(f"📋 Currently monitoring: {', '.join(s.upper() for s in current_symbols)}")
        
        await asyncio.sleep(5)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await monitor.disconnect()
        print(f"✅ Demo completed. Total updates: {sum(update_count.values())}")


async def error_handling_demo():
    """Demonstrate error handling and reconnection."""
    print("🎯 Error Handling Demo")
    print("=" * 50)
    
    connection_events = []
    
    async def robust_callback(symbol: str, price_data: dict):
        """Callback that logs connection health."""
        # This callback intentionally includes some that might fail
        try:
            price = price_data['price']
            # Simulate occasional processing error
            if len(connection_events) % 50 == 0:
                raise Exception("Simulated processing error")
            
            print(f"📊 {symbol.upper()}: ${price:,.2f}")
            
        except Exception as e:
            print(f"⚠️ Callback error for {symbol}: {e}")
    
    monitor = BinanceWebSocket(
        robust_callback,
        auto_reconnect=True,
        reconnect_delay=2,  # Fast reconnection for demo
        log_level="INFO"
    )
    
    try:
        await monitor.connect()
        await monitor.subscribe(['btcusdt'])
        
        print("✅ Connected and subscribed to BTC/USDT")
        print("🔄 Demonstrating automatic error recovery...")
        print("Press Ctrl+C to stop\n")
        
        # Start monitoring with automatic error handling
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Demo stopped")
    except Exception as e:
        print(f"❌ Unhandled error: {e}")
    finally:
        await monitor.disconnect()


async def main():
    """Main demo function with menu selection."""
    print("🚀 Binance WebSocket Tool Demo")
    print("=" * 50)
    print("Available demos:")
    print("1. Basic Monitoring (with price alerts)")
    print("2. Convenience Function Usage")
    print("3. Dynamic Symbol Management")
    print("4. Error Handling & Reconnection")
    print("5. Run all demos sequentially")
    print()
    
    try:
        choice = input("Select demo (1-5) or press Enter for demo 1: ").strip()
        if not choice:
            choice = "1"
        
        if choice == "1":
            await basic_monitoring_demo()
        elif choice == "2":
            await convenience_function_demo()
        elif choice == "3":
            await symbol_management_demo()
        elif choice == "4":
            await error_handling_demo()
        elif choice == "5":
            print("🎬 Running all demos...\n")
            await convenience_function_demo()
            print("\n" + "="*50 + "\n")
            await symbol_management_demo()
            print("\n" + "="*50 + "\n")
            await error_handling_demo()
        else:
            print(f"❌ Invalid choice: {choice}")
            return
    
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)