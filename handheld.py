#!/usr/bin/env python3

# Script designed to run on Raspberry Pi Zero to receive sensor data from a handheld Pi Pico based sensor platform using over bluetooth.
# Vibe coded by gemini with modifications by directive0

import asyncio
import csv
import os
import logging
from datetime import datetime
import threading

# Shared storage for integration with picorderOS
# Format: { "description": [value, min, max, symbol, device, timestamp, position] }
latest_data = {}
data_lock = threading.Lock()
_receiver_thread = None


# Nordic UART Service UUIDs
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write to this
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notifications from this

class BLEReceiver:
    def __init__(self, data_file="sensor_data.csv", log_file="ble_receiver.log"):
        self.data_file = data_file
        self.log_file = log_file
        self.running = False
        self.data_buffer = ""
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create CSV file with headers if it doesn't exist
        self._init_csv_file()
        
    def _init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['value', 'min_value', 'max_value', 'description', 
                               'symbol', 'device_name', 'timestamp', 'position', 'received_at'])
    
    def _save_data(self, data_row):
        """Save received data to CSV file"""
        try:
            # Add received timestamp
            data_row.append(datetime.now().isoformat())
            
            with open(self.data_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data_row)
            
            # Update shared storage for sensors.py integration
            with data_lock:
                latest_data[data_row[3]] = data_row
            
            self.logger.info(f"Saved: {data_row[3]} = {data_row[0]} {data_row[4]} from {data_row[5]}")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
    
    def _parse_sensor_data(self, data_string):
        """Parse incoming sensor data string"""
        try:
            # Remove whitespace and split by comma
            parts = [part.strip() for part in data_string.strip().split(',')]
            
            if len(parts) >= 8:
                return [
                    float(parts[0]),    # value
                    float(parts[1]),    # min_value
                    float(parts[2]),    # max_value
                    parts[3],           # description
                    parts[4],           # symbol
                    parts[5],           # device_name
                    parts[6],           # timestamp
                    parts[7]            # position
                ]
            else:
                self.logger.warning(f"Invalid data format (expected 8 parts, got {len(parts)}): {data_string}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parsing data '{data_string}': {e}")
            return None
    
    def notification_handler(self, sender, data):
        """Handle BLE notifications (incoming data chunks)"""
        try:
            # Convert bytes to string and add to buffer
            chunk = data.decode('utf-8')
            self.data_buffer += chunk
            
            # Process complete lines (ending with \n)
            while '\n' in self.data_buffer:
                line, self.data_buffer = self.data_buffer.split('\n', 1)
                line = line.strip()
                
                if line:
                    self.logger.info(f"Received complete data: {line}")
                    parsed_data = self._parse_sensor_data(line)
                    if parsed_data:
                        self._save_data(parsed_data)
                        
        except Exception as e:
            self.logger.error(f"Error in notification handler: {e}")
    
    async def scan_for_devices(self, duration=10, target_name=None):
        """Scan for BLE devices"""
        self.logger.info(f"Scanning for BLE devices{' named ' + target_name if target_name else ''}...")
        from bleak import BleakScanner
        
        devices = await BleakScanner.discover(timeout=duration)
        found_devices = []
        
        for device in devices:
            # Log all devices for debugging
            self.logger.debug(f"Found device: {device.name or 'Unknown'} ({device.address})")
            
            if target_name:
                if device.name == target_name:
                    found_devices.append(device)
                    self.logger.info(f"Found target device: {device.name} ({device.address})")
            else:
                # Look for sensor-like devices
                if device.name and any(keyword in device.name.lower() 
                                     for keyword in ['sensor', 'temp', 'pico']):
                    found_devices.append(device)
                    self.logger.info(f"Found sensor device: {device.name} ({device.address})")
        
        return found_devices
    
    async def connect_to_device(self, device):
        """Connect to a BLE device and handle data"""
        from bleak import BleakClient
        client = None
        try:
            self.logger.info(f"Connecting to {device.name} ({device.address})...")
            
            client = BleakClient(device.address)
            await client.connect()
            self.logger.info(f"Connected to {device.name}")
            
            # Get all services and log them for debugging
            services = client.services
            self.logger.info("Available services:")
            for service in services:
                self.logger.info(f"  Service: {service.uuid}")
                for char in service.characteristics:
                    self.logger.info(f"    Char: {char.uuid} - Properties: {char.properties}")
            
            # Look for UART service
            uart_service = None
            for service in services:
                if service.uuid.lower() == UART_SERVICE_UUID.lower():
                    uart_service = service
                    break
            
            if not uart_service:
                self.logger.error(f"UART service {UART_SERVICE_UUID} not found on {device.name}")
                # Try to find any notifiable characteristic as fallback
                for service in services:
                    for char in service.characteristics:
                        if "notify" in char.properties:
                            self.logger.info(f"Found notifiable characteristic: {char.uuid}")
                            await client.start_notify(char, self.notification_handler)
                            self.logger.info(f"Started notifications from fallback characteristic")
                            # Keep connection alive
                            while self.running and client.is_connected:
                                await asyncio.sleep(1)
                            return
                return
            
            # Get TX characteristic (for receiving notifications)
            tx_char = None
            for char in uart_service.characteristics:
                if char.uuid.lower() == UART_TX_CHAR_UUID.lower():
                    tx_char = char
                    break
            
            if not tx_char:
                self.logger.error(f"TX characteristic {UART_TX_CHAR_UUID} not found")
                return
            
            # Start notifications
            await client.start_notify(tx_char, self.notification_handler)
            self.logger.info(f"Started notifications from UART TX characteristic")
            
            # Keep connection alive
            while self.running and client.is_connected:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Error with device {device.name}: {e}")
        finally:
            if client and client.is_connected:
                try:
                    await client.disconnect()
                    self.logger.info(f"Disconnected from {device.name}")
                except:
                    pass
    
    async def start_receiver(self, target_device_name="TempSensor01"):
        """Start the BLE receiver"""
        self.running = True
        self.logger.info(f"Starting BLE receiver for device: {target_device_name}")
        
        while self.running:
            try:
                # Scan for the target device
                devices = await self.scan_for_devices(duration=5, target_name=target_device_name)
                
                if devices:
                    # Connect to the first matching device
                    await self.connect_to_device(devices[0])
                else:
                    self.logger.info(f"Device '{target_device_name}' not found. Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                    
            except Exception as e:
                self.logger.error(f"Error in receiver loop: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        """Stop the receiver"""
        self.running = False
        self.logger.info("Stopping receiver...")

async def main():
    from bleak import BleakScanner, BleakClient
    receiver = BLEReceiver()
    
    try:
        print("BLE Sensor Data Receiver")
        device_name = input("Enter device name to connect to (default: TempSensor01): ").strip()
        if not device_name:
            device_name = "TempSensor01"
        
        print(f"Looking for device: {device_name}")
        print("Press Ctrl+C to stop")
        
        await receiver.start_receiver(device_name)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        receiver.stop()

def start_background_receiver(device_name="TempSensor01"):
    """Helper to run the async receiver in a background thread for picorderOS integration"""
    global _receiver_thread
    
    # Prevent starting multiple threads in the same process
    if _receiver_thread and _receiver_thread.is_alive():
        return _receiver_thread

    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        receiver = BLEReceiver()
        loop.run_until_complete(receiver.start_receiver(device_name))
        
    thread = threading.Thread(target=run_async, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    asyncio.run(main())