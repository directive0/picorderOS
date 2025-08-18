# Micropython script designed to be run on Raspberry Pi Pico 2W
# Collects sensor data and sends it to a Raspberry Pi over bluetooth.

import bluetooth
import time
import struct
from micropython import const

# BLE constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

# UART Service UUID (Nordic UART Service)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), bluetooth.FLAG_WRITE)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX))

class BTTransfer:
    def __init__(self, device_name="TempSensor01"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.device_name = device_name
        self.connected = False
        self.conn_handle = None
        
        # Register GATT service
        ((self.tx_handle, self.rx_handle),) = self.ble.gatts_register_services((_UART_SERVICE,))
        
        # Setup BLE
        self.ble.irq(self._ble_irq)
        self._advertise()
        print(f"BLE UART service started as '{device_name}'")
    
    def _ble_irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self.conn_handle, _, _ = data
            self.connected = True
            print("Device connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self.connected = False
            self.conn_handle = None
            print("Device disconnected")
            self._advertise()  # Restart advertising
        elif event == _IRQ_GATTS_WRITE:
            # Handle incoming data (if needed)
            pass
    
    def _advertise(self):
        """Start BLE advertising"""
        name = self.device_name.encode('utf-8')
        
        # Create advertising payload
        payload = bytearray()
        
        # Flags
        payload.extend(b'\x02\x01\x06')
        
        # Complete local name
        payload.extend(bytes([len(name) + 1, 0x09]))
        payload.extend(name)
        
        # Service UUID (128-bit UUID in little-endian format)
        payload.extend(b'\x11\x07')  # 16 bytes + 1 byte type = 17 bytes total, type 0x07 for 128-bit
        # Nordic UART Service UUID: 6E400001-B5A3-F393-E0A9-E50E24DCCA9E
        payload.extend(b'\x9e\xca\xdc\x24\x0e\xe5\xa9\xe0\x93\xf3\xa3\xb5\x01\x00\x40\x6e')
        
        self.ble.gap_advertise(100000, payload)  # Advertise every 100ms
        print("Advertising started")
    
    def send_data(self, value, min_val, max_val, description, symbol, timestamp=None, position=None):
        """Send sensor data via BLE UART"""
        if not self.connected:
            print("Not connected - cannot send data")
            return False
        
        if timestamp is None:
            timestamp = time.time()
        
        if position is None:
            position = "unknown"
        
        # Format data as CSV string
        data_str = f"{value},{min_val},{max_val},{description},{symbol},{self.device_name},{timestamp},{position}\n"
        
        try:
            # Send data via BLE notification
            data_bytes = data_str.encode('utf-8')
            
            # Split into chunks if too large (BLE has ~20 byte limit per packet)
            chunk_size = 20
            for i in range(0, len(data_bytes), chunk_size):
                chunk = data_bytes[i:i+chunk_size]
                self.ble.gatts_notify(self.conn_handle, self.tx_handle, chunk)
                time.sleep_ms(10)  # Small delay between chunks
            
            print(f"Sent: {data_str.strip()}")
            return True
            
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def is_connected(self):
        return self.connected

# Global instance for easy access
_bt_instance = None

def init_bluetooth(device_name="TempSensor01"):
    """Initialize Bluetooth - call this once at startup"""
    global _bt_instance
    _bt_instance = BTTransfer(device_name)
    return _bt_instance

def send_sensor_data(value, min_val, max_val, description, symbol, timestamp=None, position=None):
    """Send sensor data - call this from your sensor code"""
    global _bt_instance
    
    if _bt_instance is None:
        print("Bluetooth not initialized! Call init_bluetooth() first")
        return False
    
    return _bt_instance.send_data(value, min_val, max_val, description, symbol, timestamp, position)

def wait_for_connection(timeout=30):
    """Wait for a device to connect"""
    global _bt_instance
    
    if _bt_instance is None:
        print("Bluetooth not initialized!")
        return False
    
    print("Waiting for connection...")
    start_time = time.time()
    
    while not _bt_instance.is_connected():
        if timeout and (time.time() - start_time) > timeout:
            print("Connection timeout")
            return False
        time.sleep_ms(100)
    
    print("Connected!")
    return True

# Example usage
if __name__ == "__main__":
    # Initialize Bluetooth
    bt = init_bluetooth("TempSensor01")
    
    # Wait for connection
    if wait_for_connection():
        # Send sample data every 5 seconds
        counter = 0
        while True:
            try:
                if bt.is_connected():
                    temp = 20 + (counter % 10)  # Simulate temperature readings
                    send_sensor_data(
                        value=temp,
                        min_val=-40,
                        max_val=125,
                        description="Temperature",
                        symbol="°C",
                        position="TestRoom"
                    )
                    counter += 1
                else:
                    print("Connection lost, waiting for reconnection...")
                    wait_for_connection()
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("Stopping...")
                break
