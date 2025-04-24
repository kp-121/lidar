import struct
import serial
import numpy as np
import threading
import time


class DataExtractor:
    def __init__(self, port: str, baudrate: int, timeout: float = 0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.buffer = bytearray()
        self._lock = threading.Lock()
        self._latest_cloud = []
        self._stop_flag = threading.Event()
        self._current_sweep = []
        self._prev_start_angle = None

        # Start background reader thread
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

    def _reader_loop(self):
        # Lazy-open serial once
        if self.ser is None:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"[init] opened serial port {self.port}")
        while not self._stop_flag.is_set():
            if self.ser.in_waiting:
                self.buffer += self.ser.read(self.ser.in_waiting)
            while len(self.buffer) >= 47:
                if self.buffer[0] != 0x54:
                    self.buffer.pop(0)
                    continue
                pkt = bytes(self.buffer[:47])
                del self.buffer[:47]
                start_angle, points = self._parse_packet_with_angle(pkt)
                if self._prev_start_angle is not None and start_angle < self._prev_start_angle:
                    with self._lock:
                        self._latest_cloud = [(x, y, conf) for x, y, z, conf in self._current_sweep]
                    self._current_sweep = []
                self._current_sweep.extend(points)
                self._prev_start_angle = start_angle
            time.sleep(0.005)

    def get_latest_cloud(self):
        with self._lock:
            return list(self._latest_cloud)

    def shutdown(self):
        self._stop_flag.set()
        self._reader_thread.join()
        if self.ser:
            self.ser.close()
            print(f"[shutdown] closed serial port {self.port}")

    @staticmethod
    def _parse_packet_with_angle(pkt: bytes):
        start = struct.unpack('<H', pkt[4:6])[0] / 100.0
        end   = struct.unpack('<H', pkt[42:44])[0] / 100.0
        diff  = (end - start) % 360
        pts = []
        for i in range(12):
            off  = 6 + 3 * i
            dist = struct.unpack('<H', pkt[off:off+2])[0] / 1000.0
            conf = pkt[off+2]
            angle = (start + diff * (i / 11.0)) % 360
            theta = np.radians((360 - angle) % 360)
            x = dist * np.cos(theta)
            y = dist * np.sin(theta)
            z = 0.0
            pts.append((x, y, z, conf))
        return start, pts
