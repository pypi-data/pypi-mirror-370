#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
from typing import List
import requests
import struct # For packing/unpacking binary data
import subprocess
import time
import os
import re
from enum import Enum

__all__ = ['PM', 'SDK']

class ParameterType(Enum):
    STRING = 0
    INT = 1
    FLOAT = 2
    BOOL = 3
# we need to use this to get around the rc issues
class PM_Response:
    def __init__(self, rc: int, status_code: int, content: bytes):
        self.rc = rc
        self.status_code = status_code
        self.content = content

class PM:
    _lock = threading.Lock()
    _command_queue = None
    _sta_thread = None
    _pma = None
    _initialized = False

    _url = "http://localhost:8080"

    @staticmethod
    def GetHighestPhotometricaVersionInstalled():
        base_dir = r"C:\\Program Files\\Westboro Photonics"
        try:
            dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
            photometrica_dirs = []
            for d in dirs:
                match = re.match(r"Photometrica(\\d+)$", d)
                if match:
                    version = int(match.group(1))
                    photometrica_dirs.append((version, d))
            if not photometrica_dirs:
                raise FileNotFoundError("No Photometrica installation found in 'C:\\Program Files\\Westboro Photonics'.")
            highest_version_dir = max(photometrica_dirs, key=lambda x: x[0])[1]
            return os.path.join(base_dir, highest_version_dir)
        except Exception as e:
            raise FileNotFoundError(f"Failed to find Photometrica installation: {e}")

    @classmethod
    def Init(cls, photometrica_path: str = None, port: int = 8080, useGui: bool = False, autoRespond: bool = True):
        """
        Initializes the Photometrica server process

        Args: 
            photometrica_path (str): The file path to the Photometrica installation.
            port (int): The port number for the server.
            useGui (bool): Whether to use the GUI.
            autoRespond (bool): Whether to enable auto-responding.
        
        Returns:
            None
        """
        with cls._lock:
            if cls._initialized:
                print("PM already initialized.")
                return

            if photometrica_path is None:
                photometrica_path = cls.GetHighestPhotometricaVersionInstalled()

            executable_path = photometrica_path + r"\Photometrica.exe"
            try:
                print(f"Launching executable: {executable_path}")
                # Build the argument list dynamically
                args = [executable_path, f"-port={port}"]
                if not useGui:
                    args.append("-nogui")
                args.append("-autorespond=" + str(autoRespond).lower())

                # Pass the argument list to Popen
                cls._process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if port != 8080:
                    cls.SetPort(port)

                # cls._initialized = True
                timeout = 45  # Maximum time to wait (in seconds)
                interval = 1  # Time between checks (in seconds)
                start_time = time.time()

                while time.time() - start_time < timeout:
                    try:
                        # Send a simple GET request to check if the server is running
                        response = requests.get(cls._url)
                        if response.status_code == 200:
                            print("Server is ready.")
                            cls._initialized = True
                            return
                    except requests.ConnectionError:
                        # Server is not ready yet, wait and retry
                        pass
                    time.sleep(interval)

                # If the timeout is reached, raise an exception
                raise TimeoutError("Server did not start within the expected time.")        
            except Exception as e:
                print(f"Failed to launch executable: {e}")
                raise e

    @classmethod
    def Shutdown(cls):
        """
        Shuts down the Photometrica server process

        Args:
            None

        Returns:
            None
        """
        print("Entering Shutdown method...")
        with cls._lock:
            if cls._initialized:
                # Safely terminate the process created during Init()
                if hasattr(cls, "_process") and cls._process is not None:
                    print("Terminating the process...")
                    cls._process.terminate()  # Gracefully terminate the process
                    cls._process.wait()  # Wait for the process to terminate
                    cls._process = None  # Clear the process reference
                    print("Process terminated.")

                # Clean up other resources
                if cls._command_queue is not None:
                    cls._command_queue.CompleteAdding()
                    cls._sta_thread.Join()
                    cls._command_queue.Dispose()
                    cls._command_queue = None
                    cls._sta_thread = None
                    cls._pma = None

                cls._initialized = False
                print("Shutdown method completed.")
            else:
                print("PM is not initialized. Nothing to shut down.")

    @classmethod
    def SetPort(cls, port: int):
        """
        Sets the port for the Photometrica server

        Args:
            port (int): The port number to set

        Returns:
            str: The updated URL for the server
        """
        PM._url = f"http://localhost:{port}" # we need to update the url to the new port
        return PM._url
    
    @classmethod
    def SetHostname(cls, host: str):
        """
        Sets the hostname for the Photometrica server

        Args:
            host (str): The hostname to set

        Returns:
            str: The updated URL for the server
        """
        port = cls._url.split(":")[-1]
        cls._url = f"{host}:{port}"
        return cls._url
    
    @classmethod
    def SetUrl(cls, url: str):
        """
        Sets the URL for the Photometrica server

        Args:
            url (str): The URL to set

        Returns:
            str: The updated URL for the server
        """
        cls._url = url
        return cls._url

    @classmethod
    def SendApiRequest(cls, payload: bytes, methodName: str):
        """
        Sends an API request to the Photometrica server

        Args:
            payload (bytes): The request payload
            methodName (str): The name of the API method to call

        Returns:
            PM_Response: The response from the server
        """
        # Send an HTTP request to the URL defined by PM
        request_url = f"{PM._url}/api"
        request_url += f"?method={methodName}"

        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(request_url, data=payload, headers=headers)

        # we are prepending the return_code before any of the data

        # we need a custom response which has the status code and the content, but the content is shifted by 4 bytes

        # it should also have our rc
        rc = SDK_Helper.DecodeInt(response.content[:4])
        content = response.content[4:]
        status_code = response.status_code

        return PM_Response(rc, status_code, content)

class PM_List:
    def __init__(self, handle: int, values: list):
        self.handle = handle
        self._values = values

    def __getitem__(self, index):
        return self._values[index]

    def __setitem__(self, index, value):
        self._values[index] = value

    def __delitem__(self, index):
        del self._values[index]

    def __len__(self):
        return len(self._values)

    def append(self, value):
        self._values.append(value)

    def extend(self, iterable):
        self._values.extend(iterable)

    def insert(self, index, value):
        self._values.insert(index, value)

    def remove(self, value):
        self._values.remove(value)

    def pop(self, index=-1):
        return self._values.pop(index)

    def clear(self):
        self._values.clear()

    def index(self, value, start=0, stop=None):
        return self._values.index(value, start, stop)

    def count(self, value):
        return self._values.count(value)

    def sort(self, *, key=None, reverse=False):
        self._values.sort(key=key, reverse=reverse)

    def reverse(self):
        self._values.reverse()

    def __iter__(self):
        return iter(self._values)

    def __contains__(self, item):
        return item in self._values
    
class SDK_Helper:
    @staticmethod
    def DecodePMList(binary) -> PM_List:
        """Decodes a PMList from binary data."""
            # This is a bit more dynamic. We have encoded the length of the list first, followed by each element prefixed with its type (1 for float, 2 for string)
        handle = SDK_Helper.DecodeInt(binary[:4])
        offset = 4 
        length = SDK_Helper.DecodeInt(binary[offset:offset + 4])
        offset += 4
        result = []
        for _ in range(length):
            type_id = SDK_Helper.DecodeInt(binary[offset:offset + 4])
            offset += 4
            if type_id == 1:  # String
            # Decode the 7-bit encoded length of the string
                value7Bit, length = SDK_Helper.decode_7bit_int_with_length(binary[offset:])

                value = SDK_Helper.DecodeString(binary[offset:])
                # Decode the string using the decoded length
                offset += len(value) + length
            elif type_id == 2:  # Double
                value = SDK_Helper.DecodeDouble(binary[offset:offset + 8])
                offset += 8
            else:
                raise ValueError(f"Unknown type ID: {type_id}")
            result.append(value)
        
        return PM_List(handle, result)

        
    @staticmethod
    def encode_7bit_int(value: int) -> bytes:
        """Encodes an integer using 7-bit encoding."""
        result = bytearray()
        while value >= 0x80:
            result.append((value & 0x7F) | 0x80)  # Add the lower 7 bits and set the MSB
            value >>= 7
        result.append(value & 0x7F)  # Add the last 7 bits
        return bytes(result)

    @staticmethod
    def EncodeString(string: str) -> bytes:
        """Encodes a string with a 7-bit encoded length prefix."""
        encoded_string = string.encode('utf-8')  # Encode the string as UTF-8
        length_prefix = SDK_Helper.encode_7bit_int(len(encoded_string))  # Encode the length using 7-bit encoding
        return length_prefix + encoded_string
    
    @staticmethod
    def decode_7bit_int(binary: bytes) -> int:
        """Decodes an integer using 7-bit encoding."""
        result = 0
        shift = 0
        for byte in binary:
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:  # If MSB is not set, this is the last byte
                break
            shift += 7
        return result
        
    @staticmethod
    def decode_7bit_int_with_length(data: bytes) -> tuple[int, int]:
        """
        Decodes a 7-bit encoded integer and returns the integer value along with the number of bytes used.
        
        Args:
            data (bytes): The byte array containing the 7-bit encoded integer.
        
        Returns:
            tuple: (decoded integer, number of bytes used)
        """
        result = 0
        shift = 0
        length = 0
        for byte in data:
            length += 1
            result |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7
        return result, length
    
    @staticmethod
    def DecodeString(binary) -> str:
        """Decodes a string with a 7-bit encoded length prefix."""
        # Decode the length prefix
        length = SDK_Helper.decode_7bit_int(binary)
        
        # Find the number of bytes used for the length prefix
        length_prefix_size = 0
        for byte in binary:
            length_prefix_size += 1
            if (byte & 0x80) == 0:  # Stop when MSB is not set
                break
        
        # Extract and decode the string
        string_data = binary[length_prefix_size:length_prefix_size + length]
        return string_data.decode('utf-8')
        
    @staticmethod
    def EncodeFloat(float_value: float) -> bytes:
        return struct.pack('f', float_value)
    
    @staticmethod
    def DecodeFloat(binary: bytes) -> float:
        if (len(binary) < 4):
            return
        return struct.unpack('f', binary)[0]
    
    @staticmethod
    def EncodeInt(int_value: int) -> bytes:
        return struct.pack('i', int_value)
    
    @staticmethod
    def DecodeInt(binary: bytes) -> int | None:
        if (len(binary) < 4):
            return None
        return struct.unpack('i', binary)[0]
    
    @staticmethod
    def EncodeBool(bool_value: bool) -> bytes:
        return struct.pack('?', bool_value)
    
    @staticmethod
    def DecodeBool(binary: bytes) -> bool | None:
        if (len(binary) < 1):
            return None
        return struct.unpack('?', binary)[0]
    
    @staticmethod
    def EncodeDouble(double_value: float) -> bytes:
        return struct.pack('d', double_value)
    
    @staticmethod
    def DecodeDouble(binary: bytes) -> float | None:
        if (len(binary) < 8):
            return None
        return struct.unpack('d', binary)[0]
    
    @staticmethod
    def EncodeByte(byte_value: int) -> bytes:
        return struct.pack('B', byte_value)
    
    @staticmethod
    def DecodeByte(binary: bytes) -> int | None:
        if (len(binary) < 1):
            return None
        return struct.unpack('b', binary)[0]

    @staticmethod
    def DecodeFloatArray(binary: bytes) -> list[float]:
        if (len(binary) < 4): # there should at least be 4 bytes for the length
            return []
        length = struct.unpack('i', binary[:4])[0]
        if (len(binary) < 4 + length * 4): # content length should be 4 + length * 4
            return []
        return struct.unpack('f'*length, binary[4:])
    
    @staticmethod
    def EncodeFloatArray(float_array: list[float]) -> bytes:
        binary = struct.pack('i', len(float_array))
        for f in float_array:
            binary += struct.pack('f', f)
        return binary
    
    
    @staticmethod
    def EncodeIntArray(int_array: list[int]) -> bytes:
        binary = struct.pack('i', len(int_array))  # Pack the length of the array
        for i in int_array:
            binary += struct.pack('i', i)  # Pack each integer
        return binary
    
    @staticmethod
    def DecodeIntArray(binary: bytes) -> list[int]:
        if (len(binary) < 4): # there should at least be 4 bytes for the length
            return []
        length = struct.unpack('i', binary[:4])[0]
        if (len(binary) < 4 + length * 4): # content length should be 4 + length * 4
            return []
        return struct.unpack('i'*length, binary[4:])
    

    @staticmethod
    def EncodeBoolArray(bool_array: list[bool]) -> bytes:
        binary = struct.pack('i', len(bool_array))  # Pack the length of the array
        for b in bool_array:
            binary += struct.pack('?', b)  # Pack each boolean
        return binary
    
    @staticmethod
    def DecodeBoolArray(binary: bytes) -> list[bool]:
        if (len(binary) < 4):
            return []
        length = struct.unpack('i', binary[:4])[0]
        if (len(binary) < 4 + length): # content length should be 4 + length
            return []
        return struct.unpack('?'*length, binary[4:])

    @staticmethod
    def EncodeDoubleArray(double_array: list[float]) -> bytes:
        binary = struct.pack('i', len(double_array))  # Pack the length of the array
        for d in double_array:
            binary += struct.pack('d', d)  # Pack each double
        return binary
    
    @staticmethod
    def DecodeDoubleArray(binary: bytes) -> list[float]:
        if (len(binary) < 4):
            return []
        length = struct.unpack('i', binary[:4])[0]
        if (len(binary) < 4 + length * 8): # content length should be 4 + length * 8
            return []
        return struct.unpack('d'*length, binary[4:])

    @staticmethod
    def EncodeByteArray(byte_array: list[int]) -> bytes:
        binary = struct.pack('i', len(byte_array))  # Pack the length of the array
        for b in byte_array:
            binary += struct.pack('b', b)  # Pack each byte
        return binary
    
    @staticmethod
    def DecodeByteArray(binary: bytes) -> list[int]:
        if (len(binary) < 4):
            return []
        length = struct.unpack('i', binary[:4])[0]
        if (len(binary) < 4 + length): # content length should be 4 + length
            return []
        return struct.unpack('b'*length, binary[4:])

    @staticmethod
    def EncodeStringArray(string_array: list[str]) -> bytes:
        binary = struct.pack('i', len(string_array))  # Pack the length of the array
        for s in string_array:
            binary += SDK_Helper.EncodeString(s)  # Use EncodeString for each string
        return binary
    
    @staticmethod
    def DecodeStringArray(binary: bytes) -> list[str]:
        if (len(binary) < 4):
            return []
        length = struct.unpack('i', binary[:4])[0]
        strings = []
        start = 4
        for i in range(length):
            string_length = struct.unpack('i', binary[start:start+4])[0]
            start += 4
            strings.append(binary[start:start+string_length].decode('utf-8'))
            start += string_length
        return strings
    

class SDK:
    @staticmethod
    def ActivateEllipseApertureSelectTool(aperture_size: float) -> None:
        """
        Activates the Ellipse Aperture Select tool.

        Args:
            aperture_size (float): The size of the aperture to set.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(aperture_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateEllipseApertureSelectTool')
        
        if response.status_code == 200:
            print(f"ActivateEllipseApertureSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateEllipseSelectTool() -> None:
        """
        Activates the Ellipse Select tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateEllipseSelectTool')
        
        if response.status_code == 200:
            print(f"ActivateEllipseSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateEraserTool() -> None:
        """
        Activates the Eraser tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateEraserTool')
        
        if response.status_code == 200:
            print(f"ActivateEraserTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateLassoSelectTool() -> None:
        """
        Activates the Lasso Select tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateLassoSelectTool')
        
        if response.status_code == 200:
            print(f"ActivateLassoSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateLineSelectTool() -> None:
        """
        Activates the Line Select tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateLineSelectTool')
        
        if response.status_code == 200:
            print(f"ActivateLineSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateMagicWandTool(threshold_min: float, threshold_max: float) -> None:
        """
        Activates the Magic Wand tool.

        Args:
            threshold_min (float): The minimum threshold for the Magic Wand tool.
            threshold_max (float): The maximum threshold for the Magic Wand tool.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(threshold_min)
        binary_payload += SDK_Helper.EncodeFloat(threshold_max)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateMagicWandTool')
        
        if response.status_code == 200:
            print(f"ActivateMagicWandTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateMoveAoiTool() -> None:
        """
        Activates the Move AOI tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateMoveAoiTool')
        
        if response.status_code == 200:
            print(f"ActivateMoveAoiTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateMoveTool() -> None:
        """
        Activates the Move tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateMoveTool')
        
        if response.status_code == 200:
            print(f"ActivateMoveTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivatePanTool() -> None:
        """
        Activates the Pan tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivatePanTool')
        
        if response.status_code == 200:
            print(f"ActivatePanTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivatePencilTool() -> None:
        """
        Activates the Pencil tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivatePencilTool')
        
        if response.status_code == 200:
            print(f"ActivatePencilTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivatePolygonSelectTool() -> None:
        """
        Activates the Polygon Select tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivatePolygonSelectTool')
        
        if response.status_code == 200:
            print(f"ActivatePolygonSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateRectangleApertureSelectTool(apSize: float) -> None:
        """
        Activates the Rectangle Aperture Select tool.

        Args:
            apSize (float): The size of the aperture to set.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(apSize)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateRectangleApertureSelectTool')
        
        if response.status_code == 200:
            print(f"ActivateRectangleApertureSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateRectangleSelectTool() -> None:
        """
        Activates the Rectangle Select tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateRectangleSelectTool')
        
        if response.status_code == 200:
            print(f"ActivateRectangleSelectTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateRectangleTool() -> None:
        """
        Activates the Rectangle tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateRectangleTool')
        
        if response.status_code == 200:
            print(f"ActivateRectangleTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateTextTool() -> None:
        """
        Activates the Annotation Text tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateTextTool')
        
        if response.status_code == 200:
            print(f"ActivateTextTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateTool(tool_name: str) -> None:
        """
        Activates a tool by name.

        Args:
            tool_name (str): The name of the tool to activate.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(tool_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateTool')
        
        if response.status_code == 200:
            print(f"ActivateTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ActivateZoomTool() -> None:
        """
        Activates the Zoom tool.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ActivateZoomTool')
        
        if response.status_code == 200:
            print(f"ActivateZoomTool: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromAoi(new_name: str, action: str, source_AOI_name: str, action_parameter: str) -> None:
        """
        Adds an Area of Interest (AOI) from another AOI.

        Args:
            new_name (str): The name of the new AOI.
            action (str): The action to perform ["edge", "combine", "intersect", "erode", "grow", "smooth"].
            source_AOI_name (str): The name of the source AOI.
            action_parameter (str): Additional parameters for the action.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(action)
        binary_payload += SDK_Helper.EncodeString(source_AOI_name)
        binary_payload += SDK_Helper.EncodeString(action_parameter)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromAoi')
        
        if response.status_code == 200:
            print(f"AddAoiFromAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromDataTable(data_table_name: str) -> None:
        """
        Adds an Area of Interest (AOI) from a data table.
        (see user manual for details on the table format)

        Args:
            data_table_name (str): The name of the data table to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromDataTable')
        
        if response.status_code == 200:
            print(f"AddAoiFromDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromFile(file_path: str) -> None:
        """
        Adds an AOI from a saved file to the current document. Relative file paths are resolved with respect to the current working folder.

        Args:
            file_path (str): The path to the file to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromFile')
        
        if response.status_code == 200:
            print(f"AddAoiFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromMagicWand(new_name: str, x: int, y: int, measurement_name: str, threshold_min: float, threshold_max: float) -> None:
        """
        Adds an AOI to the document using magic wand parameters.
        Args:
            new_name (str): The name of the new AOI.
            x (int): The x-coordinate of the AOI region.
            y (int): The y-coordinate of the AOI region.
            measurement_name (str): The name of the measurement to use for the source values.
            threshold_min (float): The minimum threshold for the magic wand.
            threshold_max (float): The maximum threshold for the magic wand.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeFloat(threshold_min)
        binary_payload += SDK_Helper.EncodeFloat(threshold_max)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromMagicWand')
        
        if response.status_code == 200:
            print(f"AddAoiFromMagicWand: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromMask(new_name: str) -> None:
        """
        Adds an AOI from the mask.
        Args:
            new_name (str): The name of the new AOI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromMask')
        
        if response.status_code == 200:
            print(f"AddAoiFromMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromPolygon(new_name: str, point_list: list[float]) -> None:
        """
        Adds an AOI from a polygon.

        Args:
            new_name (str): The name of the new AOI.
            point_list (list[float]): The list of points defining the polygon.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeFloatArray(point_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromPolygon')
        
        if response.status_code == 200:
            print(f"AddAoiFromPolygon: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromSelection(new_name: str) -> None:
        """
        Adds an AOI from the active selection.
        Args:
            new_name (str): The name of the new AOI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromSelection')
        
        if response.status_code == 200:
            print(f"AddAoiFromSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiFromShape(new_name: str, shape: str, x: int, y: int, width: int, height: int) -> None:
        """
        Adds an AOI from a shape.
        Args:
            new_name (str): The name of the new AOI.
            shape (str): The shape of the AOI (e.g., "rectangle", "ellipse").
            x (int): The x-coordinate of the AOI. For an ellipse, this is the center x-coordinate. Otherwise, this is the top-left coordinate.
            y (int): The y-coordinate of the AOI. For an ellipse, this is the center y-coordinate.  Otherwise, this is the top-left coordinate.
            width (int): The width of the AOI. 
            height (int): The height of the AOI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(shape)
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiFromShape')
        
        if response.status_code == 200:
            print(f"AddAoiFromShape: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiInPolar(name: str, shape: str, theta: float, phi: float, size: float) -> None:
        """
        Adds an AOI in polar coordinates.
        Args:
            name (str): The name of the new AOI.
            shape (str): The shape of the AOI (e.g., "circle", "ellipse").
            theta (float): The polar angle (in degrees) of the AOI.
            phi (float): The azimuthal angle (in degrees) of the AOI.
            size (float): The size of the AOI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        binary_payload += SDK_Helper.EncodeString(shape)
        binary_payload += SDK_Helper.EncodeFloat(theta)
        binary_payload += SDK_Helper.EncodeFloat(phi)
        binary_payload += SDK_Helper.EncodeFloat(size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiInPolar')
        
        if response.status_code == 200:
            print(f"AddAoiInPolar: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiMetaField(name: str, type: str) -> None:
        """
        Adds a new AOI meta field to the document. Group meta fields will have a checkbox for a control and have a value of one (in group) or zero (not in group).
        Args:
            name (str): The name of the metadata field.
            type (str): The type of the metadata field (e.g., "string", "number").

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        binary_payload += SDK_Helper.EncodeString(type)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiMetaField')
        
        if response.status_code == 200:
            print(f"AddAoiMetaField: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoisInGrid(
        shape: str,
        size: str,
        size_units: str,
        rows: int,
        columns: int,
        top: int,
        bottom: int,
        left: int,
        right: int,
        slope: float,
        prefix: str
    ) -> None:
        """
        Adds a set of AOI to the document. The margins are the number of pixels from the edge of document workspace.

        Args:
            shape (str): The shape of the AOI (e.g., "rectangle", "ellipse").
            size (str): The size of the AOI. Specify width and height pass in "<width>x<height>", "<width>,<height>", "<width>;<height>", "<width> <height>".
            size_units (str): The units for the size (e.g., "pixels", "inches").
            rows (int): The number of rows in the grid.
            columns (int): The number of columns in the grid.
            top (int): The top margin in pixels.
            bottom (int): The bottom margin in pixels.
            left (int): The left margin in pixels.
            right (int): The right margin in pixels.
            slope (float): The slope of the AOI.
            prefix (str): The prefix for the AOI names.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(shape)
        binary_payload += SDK_Helper.EncodeString(size)
        binary_payload += SDK_Helper.EncodeString(size_units)
        binary_payload += SDK_Helper.EncodeInt(rows)
        binary_payload += SDK_Helper.EncodeInt(columns)
        binary_payload += SDK_Helper.EncodeInt(top)
        binary_payload += SDK_Helper.EncodeInt(bottom)
        binary_payload += SDK_Helper.EncodeInt(left)
        binary_payload += SDK_Helper.EncodeInt(right)
        binary_payload += SDK_Helper.EncodeFloat(slope)
        binary_payload += SDK_Helper.EncodeString(prefix)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoisInGrid')
        
        if response.status_code == 200:
            print(f"AddAoisInGrid: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoisInPolar(
        theta_start: float,
        theta_step: float,
        theta_end: float,
        phi_start: float,
        phi_step: float,
        phi_end: float,
        size: float
    ) -> None:
        """
        Adds a set of AOIs to the document. For more about polar coordinates see Geometry & Coordinates in the User Manual. 

        The set of AOIs will include all combinations of theta and phi according to the start, step (increment) and end (maximum) parameters for each.


        Args:
            theta_start (float): The starting polar angle (in degrees).
            theta_step (float): The step size for the polar angle (in degrees).
            theta_end (float): The ending polar angle (in degrees).
            phi_start (float): The starting azimuthal angle (in degrees).
            phi_step (float): The step size for the azimuthal angle (in degrees).
            phi_end (float): The ending azimuthal angle (in degrees).
            size (float): The size of the AOIs.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(theta_start)
        binary_payload += SDK_Helper.EncodeFloat(theta_step)
        binary_payload += SDK_Helper.EncodeFloat(theta_end)
        binary_payload += SDK_Helper.EncodeFloat(phi_start)
        binary_payload += SDK_Helper.EncodeFloat(phi_step)
        binary_payload += SDK_Helper.EncodeFloat(phi_end)
        binary_payload += SDK_Helper.EncodeFloat(size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoisInPolar')
        
        if response.status_code == 200:
            print(f"AddAoisInPolar: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiTableColumn(new_name: str, formula: str, type: str, heading: str, width: int, visible: bool) -> None:
        """
        Adds a new column to the AOI table.

        Args:
            new_name (str): The name of the new column.
            formula (str): The formula for the new column.
            type (str): The type of the new column.
            heading (str): The heading for the new column.
            width (int): The width of the new column.
            visible (bool): Whether the new column is visible.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(formula)
        binary_payload += SDK_Helper.EncodeString(type)
        binary_payload += SDK_Helper.EncodeString(heading)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(visible)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiTableColumn')
        
        if response.status_code == 200:
            print(f"AddAoiTableColumn: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiTableScheme(new_name: str, active_scheme: bool, visible_column_names: str) -> None:
        """
        Adds a new AOI table scheme.

        Args:
            new_name (str): The name of the new scheme.
            active_scheme (bool): Whether the new scheme is active.
            visible_column_names (str): A comma-separated list of visible column names.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeBool(active_scheme)
        binary_payload += SDK_Helper.EncodeString(visible_column_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiTableScheme')
        
        if response.status_code == 200:
            print(f"AddAoiTableScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddAoiToMask(AOI_name: str) -> None:
        """
        Adds an AOI's region to the mask.

        Args:
            AOI_name (str): The name of the AOI to add to the mask.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddAoiToMask')
        
        if response.status_code == 200:
            print(f"AddAoiToMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCapture(
        new_name: str,
        lens_ID: int,
        fov_ID: int,
        iris_ID: int,
        overlap: int,
        nd: int,
        min: float,
        max: float,
        use_min: bool,
        use_max: bool,
        averaging_count: int,
        scalar: float,
        measurement_name: str,
        data_type_name: str,
        replace: bool,
        presentation_name: str
    ) -> None:
        """
        Adds a photometric capture scheme to the document. 
        When using this calling convention additional settings must be set by calls to SetCaptureProperty.

        Args:
            new_name (str): The name of the new capture scheme.
            lens_ID (int): The ID of the lens to use.
            fov_ID (int): The ID of the field of view to use.
            iris_ID (int): The ID of the iris to use.
            overlap (int): The overlap percentage to use.
            nd (int): The neutral density filter to use.
            min (float): The minimum exposure time to use.
            max (float): The maximum exposure time to use.
            use_min (bool): Whether to use the minimum exposure time.
            use_max (bool): Whether to use the maximum exposure time.
            averaging_count (int): The number of averages to use.
            scalar (float): The scalar value to use.
            measurement_name (str): The name of the measurement to use.
            data_type_name (str): The name of the data type to use.
            replace (bool): Whether to replace an existing capture scheme.
            presentation_name (str): The name of the presentation to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeInt(lens_ID)
        binary_payload += SDK_Helper.EncodeInt(fov_ID)
        binary_payload += SDK_Helper.EncodeInt(iris_ID)
        binary_payload += SDK_Helper.EncodeInt(overlap)
        binary_payload += SDK_Helper.EncodeInt(nd)
        binary_payload += SDK_Helper.EncodeFloat(min)
        binary_payload += SDK_Helper.EncodeFloat(max)
        binary_payload += SDK_Helper.EncodeBool(use_min)
        binary_payload += SDK_Helper.EncodeBool(use_max)
        binary_payload += SDK_Helper.EncodeInt(averaging_count)
        binary_payload += SDK_Helper.EncodeFloat(scalar)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(data_type_name)
        binary_payload += SDK_Helper.EncodeBool(replace)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCapture')
        
        if response.status_code == 200:
            print(f"AddCapture: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCaptureFromFile(file_path: str) -> None:
        """
        Adds a capture scheme to the document from a file. Relative file paths are resolved with respect to the current working folder.

        Args:
            file_path (str): The path to the file containing the capture scheme.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCaptureFromFile')
        
        if response.status_code == 200:
            print(f"AddCaptureFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCaptureFromMeasurement(measurement_name: str, capture_scheme: str, exposure_step: int, show_editor: bool) -> None:
        """
        Adds a capture scheme to the document based on the exposures used in the specified measurement. The capture scheme created is either a custom exposure set or a single fixed exposure depending on the custom exposure set step parameter.

        Args:
            measurement_name (str): The name of the measurement to use.
            capture_scheme (str): The name of the capture scheme to create.
            exposure_step (int): The exposure step to use.
            show_editor (bool): Whether to show the editor.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(capture_scheme)
        binary_payload += SDK_Helper.EncodeInt(exposure_step)
        binary_payload += SDK_Helper.EncodeBool(show_editor)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCaptureFromMeasurement')
        
        if response.status_code == 200:
            print(f"AddCaptureFromMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCaptureScheme(new_name: str, tab_delimited_parameters: str) -> None:
        """
        The same as AddCapture
        Newer versions of Photometrica support this api call having only 2 parameters, where the second parameter is a tab delimited string of many settings.

        Args:
            new_name (str): The name of the new capture scheme.
            tab_delimited_parameters (str): The tab-delimited string of parameters.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_parameters)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCaptureScheme')
        
        if response.status_code == 200:
            print(f"AddCaptureScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorCaptureScheme(
        new_name: str,
        iris_ID: int,
        mode: str,
        bracketing: str,
        longest: float,
        measurement_name: str,
        TSV_components: str,
        presentation_name: str
    ) -> None:
        """
        Adds a color capture scheme to the document. Use SetCaptureProperty to set additional parameters.
        Args:
            new_name (str): The name of the new color capture scheme.
            iris_ID (int): The ID of the iris to use.
            mode (str): The mode to use.
            bracketing (str): The bracketing to use.
            longest (float): The longest exposure time to use.
            measurement_name (str): The name of the measurement to use.
            TSV_components (str): The TSV components to use.
            presentation_name (str): The presentation name to use.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeInt(iris_ID)
        binary_payload += SDK_Helper.EncodeString(mode)
        binary_payload += SDK_Helper.EncodeString(bracketing)
        binary_payload += SDK_Helper.EncodeDouble(longest)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(TSV_components)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorCaptureScheme')
        
        if response.status_code == 200:
            print(f"AddColorCaptureScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorCorrection(tab_delimited_names: str) -> None:
        """
        Adds a color correction to the document

        Args:
            tab_delimited_names (str): The tab-delimited names of the color corrections to add.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(tab_delimited_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorCorrection')
        
        if response.status_code == 200:
            print(f"AddColorCorrection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorGroupFiles(file_path: str) -> None:
        """
        Adds a color group file to the document.

        Args:
            file_path (str): The path to the color group file.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorGroupFiles')
        
        if response.status_code == 200:
            print(f"AddColorGroupFiles: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorRegionFromEllipse(
        color_space: str,
        new_name: str,
        line_style_name: str,
        r: int,
        g: int,
        b: int,
        center_x: float,
        center_y: float,
        major_axis: float,
        minor_axis: float,
        rotation_degrees: float
    ) -> None:
        """
        Creates an elliptical color region.

        Args:
            color_space (str): The color space to use.
            new_name (str): The name of the new color region.
            line_style_name (str): The name of the line style to use.
            r (int): The red component of the color.
            g (int): The green component of the color.
            b (int): The blue component of the color.
            center_x (float): The x-coordinate of the center of the ellipse.
            center_y (float): The y-coordinate of the center of the ellipse.
            major_axis (float): The length of the major axis of the ellipse.
            minor_axis (float): The length of the minor axis of the ellipse.
            rotation_degrees (float): The rotation angle of the ellipse in degrees.

        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_space)
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(line_style_name)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        binary_payload += SDK_Helper.EncodeFloat(center_x)
        binary_payload += SDK_Helper.EncodeFloat(center_y)
        binary_payload += SDK_Helper.EncodeFloat(major_axis)
        binary_payload += SDK_Helper.EncodeFloat(minor_axis)
        binary_payload += SDK_Helper.EncodeFloat(rotation_degrees)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorRegionFromEllipse')
        
        if response.status_code == 200:
            print(f"AddColorRegionFromEllipse: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorRegionFromPolygon(
        color_space: str,
        new_name: str,
        line_style_name: str,
        r: int,
        g: int,
        b: int,
        point_list: list[float]
    ) -> None:
        """
        Creates a polygonal color region. A minimum of three coordinate pairs are required.

        Args:
            color_space (str): The color space to use.
            new_name (str): The name of the new color region.
            line_style_name (str): The name of the line style to use.
            r (int): The red component of the color.
            g (int): The green component of the color.
            b (int): The blue component of the color.
            point_list (list[float]): A list of points defining the polygon.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_space)
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(line_style_name)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        binary_payload += SDK_Helper.EncodeFloatArray(point_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorRegionFromPolygon')
        
        if response.status_code == 200:
            print(f"AddColorRegionFromPolygon: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorRegionMacAdam(
        color_space: str,
        new_name: str,
        line_style_name: str,
        r: int,
        g: int,
        b: int,
        center_x: float,
        center_y: float,
        step: float
    ) -> None:
        """
        Creates a MacAdam color region.

        Args:
            color_space (str): The color space to use.
            new_name (str): The name of the new color region.
            line_style_name (str): The name of the line style to use.
            r (int): The red component of the color.
            g (int): The green component of the color.
            b (int): The blue component of the color.
            center_x (float): The x-coordinate of the center of the MacAdam region.
            center_y (float): The y-coordinate of the center of the MacAdam region.
            step (float): The step size for the MacAdam region.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_space)
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(line_style_name)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        binary_payload += SDK_Helper.EncodeFloat(center_x)
        binary_payload += SDK_Helper.EncodeFloat(center_y)
        binary_payload += SDK_Helper.EncodeFloat(step)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorRegionMacAdam')
        
        if response.status_code == 200:
            print(f"AddColorRegionMacAdam: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddColorRegionsToGroup(group_name: str, file_path: str) -> None:
        """
        Adds a color region to a color group

        Args:
            group_name (str): The name of the color group.
            file_path (str): The file path of the color region to add.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(group_name)
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddColorRegionsToGroup')
        
        if response.status_code == 200:
            print(f"AddColorRegionsToGroup: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCompoundFilter(new_name: str, filter_name_list: str) -> None:
        """
        Creates a new compound filter which runs a series of filters.

        Args:
            new_name (str): The name of the new compound filter.
            filter_name_list (str): A comma-separated list of filter names to include in the compound filter.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(filter_name_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCompoundFilter')
        
        if response.status_code == 200:
            print(f"AddCompoundFilter: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCompoundPresentation(new_name: str, presentation_name_list: str) -> None:
        """
        Creates a new compound presentation scheme.

        Args:
            new_name (str): The name of the new compound presentation.
            presentation_name_list (str): A comma-separated list of presentation names to include in the compound presentation.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(presentation_name_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCompoundPresentation')
        
        if response.status_code == 200:
            print(f"AddCompoundPresentation: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddComputation(new_name: str, formula: str, measurement_name: str, presentation_name: str, data_type_name: str) -> None:
        """
        Adds a new computation scheme to the document from the provided parameters.

        Args:
            new_name (str): The name of the new computation.
            formula (str): The formula for the computation.
            measurement_name (str): The name of the measurement to use.
            presentation_name (str): The name of the presentation to use.
            data_type_name (str): The name of the data type to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(formula)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        binary_payload += SDK_Helper.EncodeString(data_type_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddComputation')
        
        if response.status_code == 200:
            print(f"AddComputation: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddComputationFromFile(file_path: str) -> None:
        """
        Adds a new computation scheme to the document from the provided file.

        Args:
            file_path (str): The file path of the file containing the computation scheme.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddComputationFromFile')
        
        if response.status_code == 200:
            print(f"AddComputationFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCustomFilterRegistrationDataTable(data_table_name: str, option: str) -> None:
        """
        Creates a data table with either the custom or factory filter registration settings.

        Args:
            data_table_name (str): The name of the data table to create.
            option (str): The filter registration option to use (*custom or *factory).
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(option)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCustomFilterRegistrationDataTable')
        
        if response.status_code == 200:
            print(f"AddCustomFilterRegistrationDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddCustomPresentation(new_name: str, color_list: list[int], value_list: list[float]) -> None:
        """
        Creates a presentation where the colors and values for each bin are specified in lists.

        Args:
            new_name (str): The name of the new presentation.
            color_list (list[int]): The list of colors for each bin.
            value_list (list[float]): The list of values for each bin.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeIntArray(color_list)
        binary_payload += SDK_Helper.EncodeFloatArray(value_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddCustomPresentation')
        
        if response.status_code == 200:
            print(f"AddCustomPresentation: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTable(new_name: str, columns: int, rows: int, descriptive_text: str) -> None:
        """
        Creates a new data table
        
        Args:
            new_name (str): The name of the new data table.
            columns (int): The number of columns in the data table.
            rows (int): The number of rows in the data table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeInt(columns)
        binary_payload += SDK_Helper.EncodeInt(rows)
        binary_payload += SDK_Helper.EncodeString(descriptive_text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTable')
        
        if response.status_code == 200:
            print(f"AddDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTableFromDictionary(new_name: str, dictionary_name: str, options: str) -> None:
        """
        Creates a data table from a dictionary

        Args:
            new_name (str): The name of the new data table.
            dictionary_name (str): The name of the dictionary to use.
            options (str): Additional options for the data table.
        Returns:
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        binary_payload += SDK_Helper.EncodeString(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTableFromDictionary')
        
        if response.status_code == 200:
            print(f"AddDataTableFromDictionary: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTableFromGraph(new_name: str, graph_window: str) -> None:
        """
        Creates a data table from a graph

        Args:
            new_name (str): The name of the new data table.
            graph_window (str): The name of the graph window to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(graph_window)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTableFromGraph')
        
        if response.status_code == 200:
            print(f"AddDataTableFromGraph: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTableFromHistogram(new_name: str, measurement_name: str, AOI_name: str, bin_count: int, options: str) -> None:
        """
        Creates a new data table with histogram data for a specific measurement.

        Args:
            new_name (str): The name of the new data table.
            measurement_name (str): The name of the measurement to use.
            AOI_name (str): The name of the area of interest.
            bin_count (int): The number of bins for the histogram.
            options (str): Additional options for the histogram.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeInt(bin_count)
        binary_payload += SDK_Helper.EncodeString(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTableFromHistogram')
        
        if response.status_code == 200:
            print(f"AddDataTableFromHistogram: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTableFromObjectTable(new_name: str, object_type: str, options: str) -> None:
        """
        Adds a data table from the table of objects
        
        Args:
            new_name (str): The name of the new data table.
            object_type (str): The type of objects to include in the table.
            options (str): Additional options for the data table. (tab delimited)

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(object_type)
        binary_payload += SDK_Helper.EncodeString(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTableFromObjectTable')
        
        if response.status_code == 200:
            print(f"AddDataTableFromObjectTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTableFromSpectrum(new_name: str, measurement_name: str, increment: float) -> None:
        """
        Creates a new data table with spectrum data for a specific measurement. The first column is the wavelength for the center of the bin. The second column is the mean spectrum value for the bin.
        Once the spectrum data is in a data table other methods can be used to perform analysis. Use GetDataTableRange to extract the values to then use list specific methods such as GetFunctionPeaks to find the peaks of the spectrum.

        Args:
            new_name (str): The name of the new data table.
            measurement_name (str): The name of the measurement to use.
            increment (float): The increment value for the spectrum data.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeFloat(increment)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTableFromSpectrum')
        
        if response.status_code == 200:
            print(f"AddDataTableFromSpectrum: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDataTableFromSurface(
        new_name: str,
        UDW_name: str,
        UDW_control_name: str,
        shape: str,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        options: str
    ) -> None:
        """
        Creates a new data table with data from a surface control.

        Args:
            new_name (str): The name of the new data table.
            UDW_name (str): The name of the UDW.
            UDW_control_name (str): The name of the UDW control.
            shape (str): The shape of the data.
            x0 (int): The starting x-coordinate.
            y0 (int): The starting y-coordinate.
            x1 (int): The ending x-coordinate.
            y1 (int): The ending y-coordinate.
            options (str): Additional options for the data table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(shape)
        binary_payload += SDK_Helper.EncodeInt(x0)
        binary_payload += SDK_Helper.EncodeInt(y0)
        binary_payload += SDK_Helper.EncodeInt(x1)
        binary_payload += SDK_Helper.EncodeInt(y1)
        binary_payload += SDK_Helper.EncodeString(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDataTableFromSurface')
        
        if response.status_code == 200:
            print(f"AddDataTableFromSurface: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDictionary(new_name: str) -> None:
        """
        Adds a new dictionary.
        Args:
            new_name (str): The name of the new dictionary.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDictionary')
        
        if response.status_code == 200:
            print(f"AddDictionary: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddDictionaryFromDataTable(new_name: str, data_table_name: str) -> None:
        """
        Adds a new dictionary from a data table.

        Args:
            new_name (str): The name of the new dictionary.
            data_table_name (str): The name of the data table to use.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddDictionaryFromDataTable')
        
        if response.status_code == 200:
            print(f"AddDictionaryFromDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddEvaluationEntry(new_name: str, formula: str, data_type_name: str) -> None:
        """
        Adds an entry to the Evaluation table.
        In <6.0, this method was called "AddAoiSummaryEntry".

        Args:
            new_name (str): The name of the new evaluation entry.
            formula (str): The formula for the evaluation entry.
            data_type_name (str): The data type name for the evaluation entry.
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(formula)
        binary_payload += SDK_Helper.EncodeString(data_type_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddEvaluationEntry')
        
        if response.status_code == 200:
            print(f"AddEvaluationEntry: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddEvaluationFromDataTable(data_table_name: str) -> None:
        """
        Adds a number of Evaluations, reading a data table for specifications.
        The data table must have at least five columns but may have more. 
        If the data table has the first row as headings, it will be skipped. Otherwise the first row will be parsed for evaluation data.

        Args:
            data_table_name (str): The name of the data table to use.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddEvaluationFromDataTable')
        
        if response.status_code == 200:
            print(f"AddEvaluationFromDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddFilter(new_name: str, shape: str, width: int, height: int, stat_name: str) -> None:
        """
        Creates a new filter.
        A shape of custom or Gaussian must have "weighted" as its statistic. A shape of rectangle or ellipse must not use "weighted" as its statistic.

        Args:
            new_name (str): The name of the new filter.
            shape (str): The shape of the new filter. ("rect", "ellipse", "gaussian", "custom")
            width (int): The width of the new filter.
            height (int): The height of the new filter.
            stat_name (str): The statistic name of the new filter.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(shape)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(stat_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddFilter')
        
        if response.status_code == 200:
            print(f"AddFilter: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddFilterFromFile(file_path: str) -> None:
        """
        Adds a new filter from a file.

        Args:
            file_path (str): The path to the file containing the filter specifications.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddFilterFromFile')
        
        if response.status_code == 200:
            print(f"AddFilterFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddImageFromDataTable(new_name: str, data_table_name: str) -> None:
        """
        Creates an image using drawing instructions in a data table
        The data table must have at least 7 columns. The first row of the data table must be the 'canvas' row that defines the size and background color of the image.

        Args:
            new_name (str): The name of the new image.
            data_table_name (str): The name of the data table containing the drawing instructions.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddImageFromDataTable')
        
        if response.status_code == 200:
            print(f"AddImageFromDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddImageFromWindow(new_name: str, window_name: str) -> None:
        """
        Creates an image using the current visible state of the specified window

        Args:
            new_name (str): The name of the new image.
            window_name (str): The name of the window to capture.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(window_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddImageFromWindow')
        
        if response.status_code == 200:
            print(f"AddImageFromWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddInstrumentDataTable(content_type: str, new_name: str, parameters: str) -> None:
        """
        Creates a new data table with instrument data.

        Args:
            content_type (str): The content type of the data table.
            new_name (str): The name of the new data table.
            parameters (str): The parameters for the data table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(content_type)
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(parameters)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddInstrumentDataTable')
        
        if response.status_code == 200:
            print(f"AddInstrumentDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddInstrumentLogDataTable(data_table_name: str) -> None:
        """
        Creates a new data table with instrument log data.

        Args:
            data_table_name (str): The name of the new data table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddInstrumentLogDataTable')
        
        if response.status_code == 200:
            print(f"AddInstrumentLogDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddIsoline(value: float, r: int, g: int, b: int, measurement_name: str) -> None:
        """
        Adds an isoline to a measurement.

        Args:
            value (float): The value of the isoline.
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).
            measurement_name (str): The name of the measurement to which the isoline belongs.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(value)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddIsoline')
        
        if response.status_code == 200:
            print(f"AddIsoline: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddMeasurement(new_name: str, presentation_name: str, types: str, value: float) -> None:
        """
        Adds a new measurement with the specified components. The pixels will be initialized to the value provided.

        Args:
            new_name (str): The name of the new measurement.
            presentation_name (str): The presentation name of the new measurement.
            types (str): The types of the new measurement.
            value (float): The initial value of the new measurement.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        binary_payload += SDK_Helper.EncodeString(types)
        binary_payload += SDK_Helper.EncodeFloat(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddMeasurement')
        
        if response.status_code == 200:
            print(f"AddMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddMeasurementFromDataTable(new_name: str, presentation_name: str, data_table_name: str) -> None:
        """
        Adds a new measurement filled with Invalid except for the pixels specified in the data table.
        The data table must be formatted with at least three (3) columns of which the first two are for coordinates. The first row of the table is used to indicate the coordinate space and the data type(s) of the measurements components.
        The coordinate columns may be any of the following matched pairs:
        - theta, phi
        - cx, cy
        - nx, ny
        - thetah, thetav
        After the coordinate columns is at least one data column. The headings are formal measurement component data types: see the list of measurement components on the Measurements page.
        For example, to add a measurement such that (5, 4) pixels relative to the center, the luminance is three (3) and the X Tristimulus is two (2), so use the following table. The headings must be included in the table, and positions other than (5, 4) will have Invalid pixels
        cx | cy | luminance | trix
        5  | 4  | 3         | 2
        Args:
            new_name (str): The name of the new measurement.
            presentation_name (str): The presentation name of the new measurement.
            data_table_name (str): The name of the existing data table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddMeasurementFromDataTable')
        
        if response.status_code == 200:
            print(f"AddMeasurementFromDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddMeasurementFromPattern(pattern_name: str, measurement_name: str) -> None:
        """
        Adds a new measurement based on an existing pattern.

        Args:
            pattern_name (str): The name of the existing pattern.
            measurement_name (str): The name of the new measurement.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(pattern_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddMeasurementFromPattern')
        
        if response.status_code == 200:
            print(f"AddMeasurementFromPattern: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddMeasurementMetaField(new_name: str, type: str) -> None:
        """
        Adds a new metadata field for a measurement.

        Args:
            new_name (str): The name of the new metadata field.
            type (str): The type of the new metadata field.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(type)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddMeasurementMetaField')
        
        if response.status_code == 200:
            print(f"AddMeasurementMetaField: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddMetaPlot(
        new_name: str,
        MMF_name: str,
        measurement_name: str,
        x_log: bool,
        y_heading: str,
        y_formula: str,
        y_axis_log: bool,
        y_axis_normalized: bool,
        smoothing_factor: int
    ) -> None:
        """
        Adds a new meta plot scheme to the document

        Args:
            new_name (str): The name of the new meta plot scheme.
            MMF_name (str): The name of the MMF to associate with the plot.
            measurement_name (str): The name of the measurement to associate with the plot.
            x_log (bool): Whether to use a logarithmic scale for the x-axis.
            y_heading (str): The heading for the y-axis.
            y_formula (str): The formula for the y-axis.
            y_axis_log (bool): Whether to use a logarithmic scale for the y-axis.
            y_axis_normalized (bool): Whether to normalize the y-axis.
            smoothing_factor (int): The smoothing factor for the plot.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(MMF_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(x_log)
        binary_payload += SDK_Helper.EncodeString(y_heading)
        binary_payload += SDK_Helper.EncodeString(y_formula)
        binary_payload += SDK_Helper.EncodeBool(y_axis_log)
        binary_payload += SDK_Helper.EncodeBool(y_axis_normalized)
        binary_payload += SDK_Helper.EncodeInt(smoothing_factor)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddMetaPlot')
        
        if response.status_code == 200:
            print(f"AddMetaPlot: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddObjectFromFile(object_type: str, file_path: str) -> None:
        """
        Adds an object from a saved file to the current document.
        In some cases, this method is an alias for a method specific to the object type.
        Currently, isolines and measurements (including components) cannot be imported with this method.

        Args:
            object_type (str): The type of the object to add.
            file_path (str): The path to the file containing the object data.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type)
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddObjectFromFile')
        
        if response.status_code == 200:
            print(f"AddObjectFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddPattern(new_name: str, content: str, comments: str) -> None:
        """
        Creates a new pattern with the specified content.

        Args:
            new_name (str): The name of the new pattern.
            content (str): The content of the new pattern.
            comments (str): Any comments associated with the new pattern.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(content)
        binary_payload += SDK_Helper.EncodeString(comments)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddPattern')
        
        if response.status_code == 200:
            print(f"AddPattern: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddPresentation(
        new_name: str,
        bin_count: int,
        palette_type: str,
        color_list: int,
        range_source: str,
        min: float,
        max: float,
        mapping_type: str
    ) -> None:
        """
        Creates a new presentation scheme. If you need to specify individual bin values use AddCustomPresentation instead.

        Args:
            new_name (str): The name of the new presentation scheme.
            bin_count (int): The number of bins for the presentation.
            palette_type (str): The type of color palette to use.
            color_list (int): The index of the color list to use.
            range_source (str): The source of the data range.
            min (float): The minimum value for the data range.
            max (float): The maximum value for the data range.
            mapping_type (str): The type of mapping to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeInt(bin_count)
        binary_payload += SDK_Helper.EncodeString(palette_type)
        binary_payload += SDK_Helper.EncodeInt(color_list)
        binary_payload += SDK_Helper.EncodeString(range_source)
        binary_payload += SDK_Helper.EncodeFloat(min)
        binary_payload += SDK_Helper.EncodeFloat(max)
        binary_payload += SDK_Helper.EncodeString(mapping_type)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddPresentation')
        
        if response.status_code == 200:
            print(f"AddPresentation: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddPresentationFromFile(file_path: str) -> None:
        """
        Adds a presentation to the document from a file. Relative file paths are resolved with respect to the current working folder.

        Args:
            file_path (str): The path to the file containing the presentation data.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddPresentationFromFile')
        
        if response.status_code == 200:
            print(f"AddPresentationFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddProfile(new_name: str, x0: int, y0: int, x1: int, y1: int) -> None:
        """
        Adds a profile to the document from the provided parameters. The first calling method can only create profiles with a single line segment. To create a profile with more than one line segment, use the calling method that takes a list (handle) as a parameter.
        All coordinates are in top-left pixel coordinate space. Use CxToX, CyToY, PolarToXY or RwuToXY to convert centered pixel, polar or linear coordinates to top-left pixel coordinate space. 

        Args:
            new_name (str): The name of the new profile.
            x0 (int): The x-coordinate of the starting point.
            y0 (int): The y-coordinate of the starting point.
            x1 (int): The x-coordinate of the ending point.
            y1 (int): The y-coordinate of the ending point.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeInt(x0)
        binary_payload += SDK_Helper.EncodeInt(y0)
        binary_payload += SDK_Helper.EncodeInt(x1)
        binary_payload += SDK_Helper.EncodeInt(y1)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddProfile')
        
        if response.status_code == 200:
            print(f"AddProfile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddProfileFromSelection(new_name: str) -> None:
        """
        Adds a profile to the document from the current selection.

        Args:
            new_name (str): The name of the new profile.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddProfileFromSelection')
        
        if response.status_code == 200:
            print(f"AddProfileFromSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddProfileInPolar(new_name: str, theta0: float, phi0: float, theta1: float, phi1: float) -> None:
        """
        Adds a profile to the document based on the polar coordinate parameters.
        The angles are measured in degrees.

        Args:
            new_name (str): The name of the new profile.
            theta0 (float): The starting polar angle (theta) in degrees.
            phi0 (float): The starting polar angle (phi) in degrees.
            theta1 (float): The ending polar angle (theta) in degrees.
            phi1 (float): The ending polar angle (phi) in degrees.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeFloat(theta0)
        binary_payload += SDK_Helper.EncodeFloat(phi0)
        binary_payload += SDK_Helper.EncodeFloat(theta1)
        binary_payload += SDK_Helper.EncodeFloat(phi1)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddProfileInPolar')
        
        if response.status_code == 200:
            print(f"AddProfileInPolar: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddProfilePlotScheme(
        new_name: str,
        active_scheme: bool,
        smoothing: bool,
        y_axis_logarithmic: bool,
        full_width_percent_max: bool,
        polar_plot_mode: bool
    ) -> None:
        """
        Creates a new profile plot scheme with customizable options for smoothing, axis scaling, and plot modes.

        Args:
            new_name (str): The name of the new profile.
            active_scheme (bool): Whether the scheme is active.
            smoothing (bool): Whether to apply smoothing.
            y_axis_logarithmic (bool): Whether to use a logarithmic scale on the y-axis.
            full_width_percent_max (bool): Whether to use full width percent max.
            polar_plot_mode (bool): Whether to use polar plot mode.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeBool(active_scheme)
        binary_payload += SDK_Helper.EncodeBool(smoothing)
        binary_payload += SDK_Helper.EncodeBool(y_axis_logarithmic)
        binary_payload += SDK_Helper.EncodeBool(full_width_percent_max)
        binary_payload += SDK_Helper.EncodeBool(polar_plot_mode)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddProfilePlotScheme')
        
        if response.status_code == 200:
            print(f"AddProfilePlotScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddRefinementScheme(
        name: str,
        doMinThreshold: bool,
        doMaxThreshold: bool,
        minThreshold: float,
        maxThreshold: float,
        erosion: int,
        minArea: int,
        combine: bool
    ) -> None:
        """
        Creates a new refinement scheme.
        When refinement is applied to an AOI, the samples between the threshold minimum and maximum are used to create one or more child AOI.
        Note - To set other properties, or to refine based on a formula call SetRefinementProperty once the scheme has been created.

        Args:
            name (str): The name of the refinement scheme.
            doMinThreshold (bool): Whether to apply the minimum threshold.
            doMaxThreshold (bool): Whether to apply the maximum threshold.
            minThreshold (float): The minimum threshold value.
            maxThreshold (float): The maximum threshold value.
            erosion (int): The erosion value.
            minArea (int): The minimum area value.
            combine (bool): Whether to combine the results.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        binary_payload += SDK_Helper.EncodeBool(doMinThreshold)
        binary_payload += SDK_Helper.EncodeBool(doMaxThreshold)
        binary_payload += SDK_Helper.EncodeFloat(minThreshold)
        binary_payload += SDK_Helper.EncodeFloat(maxThreshold)
        binary_payload += SDK_Helper.EncodeInt(erosion)
        binary_payload += SDK_Helper.EncodeInt(minArea)
        binary_payload += SDK_Helper.EncodeBool(combine)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddRefinementScheme')
        
        if response.status_code == 200:
            print(f"AddRefinementScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReport(new_name: str, header_text: str, font_size: int, image: str, img_size: int) -> None:
        """
        Adds a new report to the document.
        When adding report elements, if you don't specify a width (that is, using a width of zero), it is generally automatically calculated.

        Args:
            new_name (str): The name of the new report.
            header_text (str): The header text for the report.
            font_size (int): The font size for the report text.
            image (str): The image file path for the report.
            img_size (int): The size of the image in the report.

        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(header_text)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        binary_payload += SDK_Helper.EncodeString(image)
        binary_payload += SDK_Helper.EncodeInt(img_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReport')
        
        if response.status_code == 200:
            print(f"AddReport: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportAoiTable(report_name: str, width: int, horizontal_stacking: bool, font_size: int, swap_rows_columns: bool) -> None:
        """
        Adds an AOI table element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the AOI table.
            horizontal_stacking (bool): Whether to stack the AOI table horizontally.
            font_size (int): The font size for the AOI table.
            swap_rows_columns (bool): Whether to swap rows and columns in the AOI table.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        binary_payload += SDK_Helper.EncodeBool(swap_rows_columns)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportAoiTable')
        
        if response.status_code == 200:
            print(f"AddReportAoiTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportCiePlot(report_name: str, width: int, horizontal_stacking: bool, height: int, scheme_name: str) -> None:
        """
        Adds a CIE plot element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the CIE plot.
            horizontal_stacking (bool): Whether to stack the CIE plot horizontally.
            height (int): The height of the CIE plot.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportCiePlot')
        
        if response.status_code == 200:
            print(f"AddReportCiePlot: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportDataTable(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        font_size: int,
        data_table_name: str,
        columns: str,
        rows: str,
        parameters: str
    ) -> None:
        """
        Adds a data table element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the data table.
            horizontal_stacking (bool): Whether to stack the data table horizontally.
            font_size (int): The font size for the data table.
            data_table_name (str): The name of the data table.
            columns (str): The columns of the data table.
            rows (str): The rows of the data table.
            parameters (str): The parameters for the data table.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(columns)
        binary_payload += SDK_Helper.EncodeString(rows)
        binary_payload += SDK_Helper.EncodeString(parameters)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportDataTable')
        
        if response.status_code == 200:
            print(f"AddReportDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportDataTableGraph(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        data_table_name: str,
        xtext: str,
        ytext: str,
        parameters: str
    ) -> None:
        """
        Adds a data table graph element to a report. For additional options (such as x markers) use AddReportElement.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the data table graph.
            horizontal_stacking (bool): Whether to stack the data table graph horizontally.
            height (int): The height of the data table graph.
            data_table_name (str): The name of the data table.
            xtext (str): The text for the x-axis.
            ytext (str): The text for the y-axis.
            parameters (str): The parameters for the data table graph.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(xtext)
        binary_payload += SDK_Helper.EncodeString(ytext)
        binary_payload += SDK_Helper.EncodeString(parameters)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportDataTableGraph')
        
        if response.status_code == 200:
            print(f"AddReportDataTableGraph: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportDivider(report_name: str, width: int, horizontal_stacking: bool, height: int) -> None:
        """
        Adds a divider element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the divider.
            horizontal_stacking (bool): Whether to stack the divider horizontally.
            height (int): The height of the divider.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportDivider')
        
        if response.status_code == 200:
            print(f"AddReportDivider: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportDocumentText(report_name: str, width: int, horizontal_stacking: bool, font_size: int) -> None:
        """
        Adds the document user notes text to a report

        Args:
            report_name (str): The name of the report.
            width (int): The width of the document text.
            horizontal_stacking (bool): Whether to stack the document text horizontally.
            font_size (int): The font size for the document text.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportDocumentText')
        
        if response.status_code == 200:
            print(f"AddReportDocumentText: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportEvaluationsTable(report_name: str, width: int, horizontal_stacking: bool, font_size: int) -> None:
        """
        Adds an evaluation table element to a report

        Args:
            report_name (str): The name of the report.
            width (int): The width of the evaluation table.
            horizontal_stacking (bool): Whether to stack the evaluation table horizontally.
            font_size (int): The font size for the evaluation table.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportEvaluationsTable')
        
        if response.status_code == 200:
            print(f"AddReportEvaluationsTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportFileName(report_name: str, width: int, horizontal_stacking: bool, font_size: int) -> None:
        """
        Adds a document file name element to a report

        Args:
            report_name (str): The name of the report.
            width (int): The width of the file name element.
            horizontal_stacking (bool): Whether to stack the file name element horizontally.
            font_size (int): The font size for the file name element.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportFileName')
        
        if response.status_code == 200:
            print(f"AddReportFileName: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportIsolinesLegend(report_name: str, width: int, horizontal_stacking: bool, height: int, meas: str) -> None:
        """
        Adds an Isolines legend for a specific measurement to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the isolines legend.
            horizontal_stacking (bool): Whether to stack the isolines legend horizontally.
            height (int): The height of the isolines legend.
            meas (str): The measurement for the isolines legend.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(meas)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportIsolinesLegend')
        
        if response.status_code == 200:
            print(f"AddReportIsolinesLegend: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMeasurement(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        measurement_name: str,
        show_isolines: bool,
        show_AOIs: bool,
        show_AOI_highlighting: bool,
        show_AOI_labels: bool,
        show_annotation: bool
    ) -> None:
        """
        Adds a measurement image element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the measurement image element.
            horizontal_stacking (bool): Whether to stack the measurement image element horizontally.
            height (int): The height of the measurement image element.
            measurement_name (str): The name of the measurement.
            show_isolines (bool): Whether to show isolines.
            show_AOIs (bool): Whether to show AOIs.
            show_AOI_highlighting (bool): Whether to show AOI highlighting.
            show_AOI_labels (bool): Whether to show AOI labels.
            show_annotation (bool): Whether to show annotations.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(show_isolines)
        binary_payload += SDK_Helper.EncodeBool(show_AOIs)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_highlighting)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_labels)
        binary_payload += SDK_Helper.EncodeBool(show_annotation)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMeasurement')
        
        if response.status_code == 200:
            print(f"AddReportMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMeasurementHistogram(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        measurement_name: str,
        xlog: bool,
        ylog: bool,
        hzoom: bool
    ) -> None:
        """
        Adds a measurement histogram element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the measurement histogram element.
            horizontal_stacking (bool): Whether to stack the measurement histogram element horizontally.
            height (int): The height of the measurement histogram element.
            measurement_name (str): The name of the measurement.
            xlog (bool): Whether to use logarithmic scaling on the x-axis.
            ylog (bool): Whether to use logarithmic scaling on the y-axis.
            hzoom (bool): Whether to enable horizontal zooming.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(xlog)
        binary_payload += SDK_Helper.EncodeBool(ylog)
        binary_payload += SDK_Helper.EncodeBool(hzoom)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMeasurementHistogram')
        
        if response.status_code == 200:
            print(f"AddReportMeasurementHistogram: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMeasurementInThetaHV(report_name: str, width: int, stack: bool, height: int, measurement_name: str) -> None:
        """
        Adds a measurement in theta HV format to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the measurement element.
            stack (bool): Whether to stack the measurement element.
            height (int): The height of the measurement element.
            measurement_name (str): The name of the measurement.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(stack)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMeasurementInThetaHV')
        
        if response.status_code == 200:
            print(f"AddReportMeasurementInThetaHV: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMeasurementSurfacePlot(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        measurement_name: str,
        AOI_name: str
    ) -> None:
        """
        Adds a measurement surface plot image to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the measurement surface plot image.
            horizontal_stacking (bool): Whether to stack the measurement surface plot image horizontally.
            height (int): The height of the measurement surface plot image.
            measurement_name (str): The name of the measurement.
            AOI_name (str): The name of the area of interest.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMeasurementSurfacePlot')
        
        if response.status_code == 200:
            print(f"AddReportMeasurementSurfacePlot: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMeasurementThermometer(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        measurement_name: str
    ) -> None:
        """
        Adds a measurement thermometer graphic element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the measurement thermometer element.
            horizontal_stacking (bool): Whether to stack the measurement thermometer element horizontally.
            height (int): The height of the measurement thermometer element.
            measurement_name (str): The name of the measurement.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMeasurementThermometer')
        
        if response.status_code == 200:
            print(f"AddReportMeasurementThermometer: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMetaInfoTable(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        font_size: int
    ) -> None:
        """
        Adds the document's meta information table to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the meta information table.
            horizontal_stacking (bool): Whether to stack the meta information table horizontally.
            font_size (int): The font size of the meta information table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMetaInfoTable')
        
        if response.status_code == 200:
            print(f"AddReportMetaInfoTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMetaPlot(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        meta_plot_scheme_name: str
    ) -> None:
        """
        Adds a plot element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the plot element.
            horizontal_stacking (bool): Whether to stack the plot element horizontally.
            height (int): The height of the plot element.
            meta_plot_scheme_name (str): The name of the meta plot scheme.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(meta_plot_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMetaPlot')
        
        if response.status_code == 200:
            print(f"AddReportMetaPlot: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportMetaPlotLegend(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int
    ) -> None:
        """
        Adds a legend for a meta plot to a report.
        Args:
            report_name (str): The name of the report.
            width (int): The width of the plot legend.
            horizontal_stacking (bool): Whether to stack the plot legend horizontally.
            height (int): The height of the plot legend.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportMetaPlotLegend')
        
        if response.status_code == 200:
            print(f"AddReportMetaPlotLegend: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportPageBreak(report_name: str) -> None:
        """
        Adds a page break to a report.

        Args:
            report_name (str): The name of the report.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportPageBreak')
        
        if response.status_code == 200:
            print(f"AddReportPageBreak: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportProfileLegend(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int
    ) -> None:
        """
        Adds a profile plot legend to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the profile plot legend.
            horizontal_stacking (bool): Whether to stack the profile plot legend horizontally.
            height (int): The height of the profile plot legend.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportProfileLegend')
        
        if response.status_code == 200:
            print(f"AddReportProfileLegend: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportProfilePlot(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        profile: str,
        y_axis_is_log: bool,
        filtering: int
    ) -> None:
        """
        Adds a profile plot element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the profile plot element.
            horizontal_stacking (bool): Whether to stack the profile plot element horizontally.
            height (int): The height of the profile plot element.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(profile)
        binary_payload += SDK_Helper.EncodeBool(y_axis_is_log)
        binary_payload += SDK_Helper.EncodeInt(filtering)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportProfilePlot')
        
        if response.status_code == 200:
            print(f"AddReportProfilePlot: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportProfilePolarPlot(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        profile_name: str,
        y_axis_log: bool,
        smoothing_factor: int
    ) -> None:
        """
        Adds a profile polar plot element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the profile polar plot element.
            horizontal_stacking (bool): Whether to stack the profile polar plot element horizontally.
            height (int): The height of the profile polar plot element.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(profile_name)
        binary_payload += SDK_Helper.EncodeBool(y_axis_log)
        binary_payload += SDK_Helper.EncodeInt(smoothing_factor)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportProfilePolarPlot')
        
        if response.status_code == 200:
            print(f"AddReportProfilePolarPlot: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportStaticImage(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        height: int,
        image_name: str
    ) -> None:
        """
        Adds a static image element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the static image element.
            horizontal_stacking (bool): Whether to stack the static image element horizontally.
            height (int): The height of the static image element.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(image_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportStaticImage')
        
        if response.status_code == 200:
            print(f"AddReportStaticImage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportStaticText(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        font_size: int,
        text: str
    ) -> None:
        """
        Adds a static text element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the static text element.
            horizontal_stacking (bool): Whether to stack the static text element horizontally.
            font_size (int): The font size of the static text element.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportStaticText')
        
        if response.status_code == 200:
            print(f"AddReportStaticText: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddReportWorkingFolder(
        report_name: str,
        width: int,
        horizontal_stacking: bool,
        font_size: int
    ) -> None:
        """
        Adds a working folder element to a report.

        Args:
            report_name (str): The name of the report.
            width (int): The width of the working folder element.
            horizontal_stacking (bool): Whether to stack the working folder element horizontally.
            font_size (int): The font size of the working folder element.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeBool(horizontal_stacking)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddReportWorkingFolder')
        
        if response.status_code == 200:
            print(f"AddReportWorkingFolder: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddScript(new_name: str, script_text: str) -> None:
        """
        Adds a script to PM.

        Args:
            new_name (str): The new name of the script.
            script_text (str): The text of the script.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(script_text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddScript')
        
        if response.status_code == 200:
            print(f"AddScript: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddScriptFromFile(file_path: str) -> None:
        """
        Adds a script from a file to PM.

        Args:
            file_path (str): The path to the script file.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddScriptFromFile')
        
        if response.status_code == 200:
            print(f"AddScriptFromFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddSelectionToMask() -> None:
        """
        Adds a selection to the mask.
        
        Args:
            None
        
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddSelectionToMask')
        
        if response.status_code == 200:
            print(f"AddSelectionToMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddToSelection(
        shape_name: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        """
        In the workspace, selects the specified region in addition to the existing workspace selection.

        Args:
            shape_name (str): The name of the shape to select.
            x (int): The x-coordinate of the selection.
            y (int): The y-coordinate of the selection.
            width (int): The width of the selection.
            height (int): The height of the selection.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(shape_name)
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddToSelection')
        
        if response.status_code == 200:
            print(f"AddToSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddUdwControl(
        UDW_name: str,
        UDW_control_name: str,
        new_name: str,
        text: str,
        image: str,
        script: str,
        width: int,
        height: int,
        position_keyword: str,
        parent_UDW_control_name: str
    ) -> None:
        """
        Adds a control to a User-Defined Window (UDW) definition. To update the UDW window call ApplyUdwChanges.

        Args:
            UDW_name (str): The name of the User-Defined Window.
            UDW_control_name (str): The name of the control to add. (see user manual for complete list of all types)
            new_name (str): The new name for the control.
            text (str): The text to display on the control.
            image (str): The image to display on the control.
            script (str): The script to execute when the control is used.
            width (int): The width of the control.
            height (int): The height of the control.
            position_keyword (str): The position keyword for the control.
            parent_UDW_control_name (str): The name of the parent control.

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeString(text)
        binary_payload += SDK_Helper.EncodeString(image)
        binary_payload += SDK_Helper.EncodeString(script)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(position_keyword)
        binary_payload += SDK_Helper.EncodeString(parent_UDW_control_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddUdwControl')
        
        if response.status_code == 200:
            print(f"AddUdwControl: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddUserDefinedDataType(
        formula_text: str,
        unit_suffix: str,
        description: str,
        options: str
    ) -> None:
        """
        This method adds a new data type which can be assigned to measurement components and formula results.

        Args:
            formula_text (str): The formula text for the data type.
            unit_suffix (str): The unit suffix for the data type.
            description (str): The description of the data type.
            options (str): The options for the data type.
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(formula_text)
        binary_payload += SDK_Helper.EncodeString(unit_suffix)
        binary_payload += SDK_Helper.EncodeString(description)
        binary_payload += SDK_Helper.EncodeString(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddUserDefinedDataType')
        
        if response.status_code == 200:
            print(f"AddUserDefinedDataType: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AddVectorAoiPolygon(new_name: str, point_list: list[float]) -> None:
        """
        Adds a "Vector AOI" to the document. Vector AOIs can be manipulated using the vector AOI tool in the Workspace window. They do not appear in the AOI table, nor are usable as a regular AOI.

        Args:
            new_name (str): The name of the new vector AOI.
            point_list (list[float]): A list of points defining the polygon.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(new_name)
        binary_payload += SDK_Helper.EncodeFloatArray(point_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AddVectorAoiPolygon')
        
        if response.status_code == 200:
            print(f"AddVectorAoiPolygon: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoClear(
        top_left_x: int,
        top_left_y: int,
        width: int,
        height: int
    ) -> None:
        """
        Clears the annotations in the specified area.

        Args:
            top_left_x (int): The x-coordinate of the top-left corner.
            top_left_y (int): The y-coordinate of the top-left corner.
            width (int): The width of the area to clear.
            height (int): The height of the area to clear.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(top_left_x)
        binary_payload += SDK_Helper.EncodeInt(top_left_y)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoClear')
        
        if response.status_code == 200:
            print(f"AnnoClear: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoDrawEllipse(
        center_x: int,
        center_y: int,
        x_axis: int,
        y_axis: int,
        thickness: int,
        r: int,
        g: int,
        b: int
    ) -> None:
        """
        Draws an ellipse on the annotation graphic layer.
        All coordinates are in top-left pixel coordinates. Use CxToX, CyToY, PolarToXY or RwuToXY to convert centered pixel, polar or linear coordinates to this coordinate space.

        Args:
            center_x (int): The x-coordinate of the center.
            center_y (int): The y-coordinate of the center.
            x_axis (int): The length of the x-axis.
            y_axis (int): The length of the y-axis.
            thickness (int): The thickness of the ellipse outline.
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(center_x)
        binary_payload += SDK_Helper.EncodeInt(center_y)
        binary_payload += SDK_Helper.EncodeInt(x_axis)
        binary_payload += SDK_Helper.EncodeInt(y_axis)
        binary_payload += SDK_Helper.EncodeInt(thickness)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoDrawEllipse')
        
        if response.status_code == 200:
            print(f"AnnoDrawEllipse: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoDrawImage(
        image_name: str,
        top_left_x: int,
        top_left_y: int,
        draw_under: bool
    ) -> None:
        """
        Draws an image on the annotation graphic layer.

        Args:
            image_name (str): The name of the image to draw.
            top_left_x (int): The x-coordinate of the top-left corner.
            top_left_y (int): The y-coordinate of the top-left corner.
            draw_under (bool): Whether to draw the image under other annotations.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(image_name)
        binary_payload += SDK_Helper.EncodeInt(top_left_x)
        binary_payload += SDK_Helper.EncodeInt(top_left_y)
        binary_payload += SDK_Helper.EncodeBool(draw_under)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoDrawImage')
        
        if response.status_code == 200:
            print(f"AnnoDrawImage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoDrawLine(
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        thickness: int,
        r: int,
        g: int,
        b: int
    ) -> None:
        """
        Draws a line on the annotation graphic layer.

        Args:
            start_x (int): The x-coordinate of the start point.
            start_y (int): The y-coordinate of the start point.
            end_x (int): The x-coordinate of the end point.
            end_y (int): The y-coordinate of the end point.
            thickness (int): The thickness of the line.
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(start_x)
        binary_payload += SDK_Helper.EncodeInt(start_y)
        binary_payload += SDK_Helper.EncodeInt(end_x)
        binary_payload += SDK_Helper.EncodeInt(end_y)
        binary_payload += SDK_Helper.EncodeInt(thickness)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoDrawLine')
        
        if response.status_code == 200:
            print(f"AnnoDrawLine: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoDrawRectangle(
        top_left_x: int,
        top_left_y: int,
        width: int,
        height: int,
        thickness: int,
        r: int,
        g: int,
        b: int
    ) -> None:
        """
        Draws a rectangle on the annotation graphic layer.

        Args:
            top_left_x (int): The x-coordinate of the top-left corner.
            top_left_y (int): The y-coordinate of the top-left corner.
            width (int): The width of the rectangle.
            height (int): The height of the rectangle.
            thickness (int): The thickness of the rectangle outline.
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(top_left_x)
        binary_payload += SDK_Helper.EncodeInt(top_left_y)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeInt(thickness)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoDrawRectangle')
        
        if response.status_code == 200:
            print(f"AnnoDrawRectangle: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoDrawText(
        text: str,
        top_left_x: int,
        top_left_y: int,
        font_size: float,
        r: int,
        g: int,
        b: int,
        options: bool
    ) -> None:
        """
        Draws text on the annotation graphic layer.

        Args:
            text (str): The text to draw.
            top_left_x (int): The x-coordinate of the top-left corner.
            top_left_y (int): The y-coordinate of the top-left corner.
            font_size (float): The font size of the text.
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).
            options (bool): Additional drawing options.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        binary_payload += SDK_Helper.EncodeInt(top_left_x)
        binary_payload += SDK_Helper.EncodeInt(top_left_y)
        binary_payload += SDK_Helper.EncodeFloat(font_size)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        binary_payload += SDK_Helper.EncodeBool(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoDrawText')
        
        if response.status_code == 200:
            print(f"AnnoDrawText: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoSaveImage(file_path: str) -> None:
        """
        Saves the current annotation graphic to a file. Relative file paths are resolved with respect to the current working folder.

        Args:
            file_path (str): The path to the file where the annotation graphic will be saved.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoSaveImage')
        
        if response.status_code == 200:
            print(f"AnnoSaveImage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoSaveImageAs(dialog_title: str) -> None:
        """
        Allows the user to use a "Save as" dialog, to specify a folder and file name, and then saves the current annotation graphic to that file.

        Args:
            dialog_title (str): The title of the "Save as" dialog.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dialog_title)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoSaveImageAs')
        
        if response.status_code == 200:
            print(f"AnnoSaveImageAs: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AnnoSetVisible(visible: bool) -> None:
        """
        Sets the visibility of the annotation graphic layer.

        Args:
            visible (bool): Whether the annotation graphic layer should be visible.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(visible)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AnnoSetVisible')
        
        if response.status_code == 200:
            print(f"AnnoSetVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AoiExists(AOI_name: str) -> None:
        """
        Checks if an Area of Interest (AOI) exists.

        Args:
            AOI_name (str): The name of the AOI to check.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AoiExists')
        
        if response.status_code == 200:
            print(f"AoiExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AppendSelectionToInstrumentMask() -> None:
        """
        Appends the current selection to the instrument mask.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AppendSelectionToInstrumentMask')
        
        if response.status_code == 200:
            print(f"AppendSelectionToInstrumentMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AppendToList(list_handle: int, values: list) -> None:
        """
        Appends values to a list.

        Args:
            list_handle (int): The handle of the list to append to.
            values (list): The values to append.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        # Ensure all values are converted to strings before encoding
        string_values = [str(value) for value in values]
        binary_payload += SDK_Helper.EncodeStringArray(string_values)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AppendToList')
        if response.status_code == 200:
            print(f"AppendToList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def AppendToListIfMissing(list_handle: int, value: str | int | float | bool) -> None:
        """
        Appends a value to a list if it is not already present.

        Args:
            list_handle (int): The handle of the list to append to.
            value (str | int | float | bool): The value to append.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(str(value))

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AppendToListIfMissing')
        if response.status_code == 200:
            print(f"AppendToListIfMissing: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyHighlightToAoi(highlight_scheme_name: str, AOI_name: str) -> None:
        """
        Applies a highlight scheme to an Area of Interest (AOI).

        Args:
            highlight_scheme_name (str): The name of the highlight scheme to apply.
            AOI_name (str): The name of the AOI to apply the highlight scheme to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyHighlightToAoi')
        
        if response.status_code == 200:
            print(f"ApplyHighlightToAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def ApplyListMath(list_handle_a: int, operator: str, list_handle_b: int) -> PM_List:
        """
        Returns a new list where its elements are the values calculated by applying an operator to the same index elements from list A and list B.

        Args:
            list_handle_a (int): The handle of the first list.
            operator (str): The mathematical operator to apply. ("+", "-", "*", "/")
            list_handle_b (int): The handle of the second list.

        Returns:
            PM_List: The result of the mathematical operation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle_a)
        binary_payload += SDK_Helper.EncodeString(operator)
        binary_payload += SDK_Helper.EncodeInt(list_handle_b)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyListMath')

        if response.status_code == 200:
            print(f"ApplyListMath: Success")
            # Decode the response
            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyMetaValueToAoi(amf: str, value: str | int | float | bool, aoi: str) -> None:
        """
        Sets the meta field value to a specific value for all the specified AOI(s).
        
        Args:
            amf (str): The name of the meta field to modify.
            value (str | int | float | bool): The new value to set for the meta field.
            aoi (str): The name of the AOI to modify.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(amf)
        binary_payload += SDK_Helper.EncodeString(value)
        binary_payload += SDK_Helper.EncodeString(aoi)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyMetaValueToAoi')
        
        if response.status_code == 200:
            print(f"ApplyMetaValueToAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyRefinementToAoi(measurement_name: str, refinement_name: str, AOI_name: str) -> None:
        """
        Applies a refinement to an AOI. When refinement is applies to an AOI, the samples between the threshold minimum and maximum are used to create one or more child AOIs.

        Args:
            measurement_name (str): The name of the measurement to refine.
            refinement_name (str): The name of the refinement to apply.
            AOI_name (str): The name of the AOI to apply the refinement to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(refinement_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyRefinementToAoi')
        
        if response.status_code == 200:
            print(f"ApplyRefinementToAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyToDataTableRange(
        data_table_name: str,
        start_column: int,
        end_column: int,
        start_row: int,
        end_row: int,
        action: str,
        value: str | int | float | bool
    ) -> None:
        """
        Performs an action on every cell in the specified range of the data table.

        Args:
            data_table_name (str): The name of the data table to modify.
            start_column (int): The starting column index (0-based).
            end_column (int): The ending column index (0-based).
            start_row (int): The starting row index (0-based).
            end_row (int): The ending row index (0-based).
            action (str): The action to perform on each cell (see the table in the user manual).
            value (str | int | float | bool): The value to use for the action.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(start_column)
        binary_payload += SDK_Helper.EncodeInt(end_column)
        binary_payload += SDK_Helper.EncodeInt(start_row)
        binary_payload += SDK_Helper.EncodeInt(end_row)
        binary_payload += SDK_Helper.EncodeString(action)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyToDataTableRange')
        
        if response.status_code == 200:
            print(f"ApplyToDataTableRange: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyToList(list_handle: int, action: str, value: str = "") -> PM_List:
        """
        Performs an action on all (applicable) elements in a list

        Args:
            list_handle (int): The handle of the list to modify.
            action (str): The action to perform on each element (see the table in the user manual).
            value (str): The value to use for the action.

        Return:
            PM_List: The modified list.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(action)
        binary_payload += SDK_Helper.EncodeString(value)

        response = PM.SendApiRequest(binary_payload, 'ApplyToList')

        if (response.status_code == 200):
            print(f"ApplyToList: Success")
            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyToUdwTable(udw: str, table: str, action: str, params: str) -> None:
        """
        Applies an action to a User-Defined Window (UDW) table.

        Args:
            udw (str): The name of the User-Defined Window (UDW) to modify.
            table (str): The name of the table within the UDW.
            action (str): The action to perform on the table (see the table in the user manual).
            params (str): The parameters for the action.

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(udw)
        binary_payload += SDK_Helper.EncodeString(table)
        binary_payload += SDK_Helper.EncodeString(action)
        binary_payload += SDK_Helper.EncodeString(params)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyToUdwTable')
        
        if response.status_code == 200:
            print(f"ApplyToUdwTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ApplyUdwChanges(UDW_name: str) -> None:
        """
        Recreates a UDW from its definition.

        Args:
            UDW_name (str): The name of the User-Defined Window (UDW) to modify.

        Returns: 
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ApplyUdwChanges')
        
        if response.status_code == 200:
            print(f"ApplyUdwChanges: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AppropriatePackageContents(package: str, objecttype: str) -> None:
        """
        Missing Implementation - TODO
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(package)
        binary_payload += SDK_Helper.EncodeString(objecttype)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AppropriatePackageContents')
        
        if response.status_code == 200:
            print(f"AppropriatePackageContents: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def Ask(text: str) -> bool:
        """
        Displays a message window with the specified text. The script is paused until the 'Yes' or 'No' button on the message window is clicked. The pop-up ID used for auto reply is 5000. Use AskCustomQuestion to specify another ID.

        Args:
            text (str): The text to display in the message window.

        Returns:
            bool: The user's response (True for 'Yes', False for 'No').
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'Ask')
        
        if response.status_code == 200:
            print(f"Ask: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AskCustomQuestion(text: str, popup_ID: str) -> bool:
        """
        Displays a message window with the specified text and pop-up ID. The script is paused until the 'Yes' or 'No' button on the message window is clicked. The pop-up ID is used to record auto reply settings. See SetAutoResponse.

        Args:
            text (str): The text to display in the message window.
            popup_ID (str): The pop-up ID to use for the message window.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        binary_payload += SDK_Helper.EncodeInt(popup_ID)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AskCustomQuestion')
        
        if response.status_code == 200:
            print(f"AskCustomQuestion: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AskForFile(
        dialog_title: str,
        initial_folder_path: str,
        initial_file_name: str,
        filespec_pattern: str,
        must_exist: bool,
        multiple: bool
    ) -> str:
        """
        Displays a file dialog for the user to select a file.

        Args:
            dialog_title (str): The title of the dialog window.
            initial_folder_path (str): The initial folder path to display in the dialog.
            initial_file_name (str): The initial file name to display in the dialog.
            filespec_pattern (str): The file specification pattern to filter files.
            must_exist (bool): Whether the file must exist.
            multiple (bool): Whether to allow multiple file selection.

        Returns:
            str: The selected file path or an empty string if no file was selected.

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dialog_title)
        binary_payload += SDK_Helper.EncodeString(initial_folder_path)
        binary_payload += SDK_Helper.EncodeString(initial_file_name)
        binary_payload += SDK_Helper.EncodeString(filespec_pattern)
        binary_payload += SDK_Helper.EncodeBool(must_exist)
        binary_payload += SDK_Helper.EncodeBool(multiple)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AskForFile')
        
        if response.status_code == 200:
            print(f"AskForFile: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AskForFolder(caption: str, initial_folder_path: str) -> str:
        """
        Displays a folder dialog for the user to select a folder.

        Args:
            caption (str): The title of the dialog window.
            initial_folder_path (str): The initial folder path to display in the dialog.

        Returns:
            str: The selected folder path or an empty string if no folder was selected.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(caption)
        binary_payload += SDK_Helper.EncodeString(initial_folder_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AskForFolder')
        
        if response.status_code == 200:
            print(f"AskForFolder: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def AssignNVISWeightingTable(tableName: str) -> None:
        """
        Assigns the specified NVIS weighting table for the NVIS Package.

        Args:
            tableName (str): The name of the NVIS weighting table to assign.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(tableName)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'AssignNVISWeightingTable')
        
        if response.status_code == 200:
            print(f"AssignNVISWeightingTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def BatchCapture(capture_scheme_name_list: list[str]) -> None:
        """
        Performs a measurement capture operation.
        Performs a series of captures using capture schemes passed using a list handle.

        Args:
            capture_scheme_name_list (list[str]): The list of capture scheme names to use for the measurement capture.
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'BatchCapture')
        
        if response.status_code == 200:
            print(f"BatchCapture: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def Calculate(formula: str, AOI_name: str = "") -> float:
        """
        Returns the result of a calculation using a formula that could be used within the AOI or Evaluation table

        Args:
            formula (str): The formula to calculate.
            AOI_name (str, optional): The name of the AOI to use in the calculation.
        Returns:
            float: The result of the calculation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(formula)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'Calculate')
        
        if response.status_code == 200:
            print(f"Calculate: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CalculateCustomAoiStat(AOI_name: str, formula: str, stat_name: str) -> float:
        """
        Returns the statistic (sum, mean, min or max) of the set of values which are the result of applying the formula specified to each pixel within the AOI.

        Args:
            AOI_name (str): The name of the AOI to use in the calculation.
            formula (str): The formula to apply to each pixel within the AOI.
            stat_name (str): The name of the statistic to calculate (sum, mean, min, max).
        Returns:
            float: The result of the calculation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(formula)
        binary_payload += SDK_Helper.EncodeString(stat_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CalculateCustomAoiStat')
        
        if response.status_code == 200:
            print(f"CalculateCustomAoiStat: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CalculateLineLength(start_x: float, start_y: float, end_x: float, end_y: float) -> float:
        """
        Calculates the length of a line segment defined by two points.

        Args:
            start_x (float): The x-coordinate of the start point.
            start_y (float): The y-coordinate of the start point.
            end_x (float): The x-coordinate of the end point.
            end_y (float): The y-coordinate of the end point.

        Returns:
            float: The length of the line segment.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(start_x)
        binary_payload += SDK_Helper.EncodeDouble(start_y)
        binary_payload += SDK_Helper.EncodeDouble(end_x)
        binary_payload += SDK_Helper.EncodeDouble(end_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CalculateLineLength')
        
        if response.status_code == 200:
            print(f"CalculateLineLength: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CalculateSpectrumProperty(datatable_name: str, property: str) -> tuple[float, float]:
        """
        Calculates the specified property of a spectrum from a data table.

        Args:
            datatable_name (str): The name of the data table.
            property (str): The property to calculate.

        Returns:
            tuple[float, float]: The calculated property values.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(datatable_name)
        binary_payload += SDK_Helper.EncodeString(property)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CalculateSpectrumProperty')
        
        if response.status_code == 200:
            print(f"CalculateSpectrumProperty: Success")

            # Decode the first double (8 bytes)
            value1 = SDK_Helper.DecodeDouble(response.content[:8])

            # Decode the second double (next 8 bytes)
            value2 = SDK_Helper.DecodeDouble(response.content[8:16])
            return (value1, value2)

        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CalculateTristimulusProperty(X: float, Y: float, Z: float, property: str) -> tuple[float, float]:
        """
        Calculates the specified property of a color defined by its tristimulus values.

        Args:
            X (float): The X tristimulus value.
            Y (float): The Y tristimulus value.
            Z (float): The Z tristimulus value.
            property (str): The property to calculate.

        Returns:
            tuple[float, float]: The calculated property values.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(X)
        binary_payload += SDK_Helper.EncodeDouble(Y)
        binary_payload += SDK_Helper.EncodeDouble(Z)
        binary_payload += SDK_Helper.EncodeString(property)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CalculateTristimulusProperty')
        
        if response.status_code == 200:
            print(f"CalculateTristimulusProperty: Success")

            # Decode the first double (8 bytes)
            value1 = SDK_Helper.DecodeDouble(response.content[:8])

            # Decode the second double (next 8 bytes)
            value2 = SDK_Helper.DecodeDouble(response.content[8:16])

            return (value1, value2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CallDllDataTableIo(DLL_handle: int, method_name: str, data_table_name: str) -> None:
        """
        Calls a Plug-in DLL with method text arguments, passing in a reference to data table data as a 2-D float array for reading and/or writing.

        Args:
            DLL_handle (int): The handle to the DLL.
            method_name (str): The name of the method to call.
            data_table_name (str): The name of the data table.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(DLL_handle)
        binary_payload += SDK_Helper.EncodeString(method_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CallDllDataTableIo')
        
        if response.status_code == 200:
            print(f"CallDllDataTableIo: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CallDllIntStr(DLL_handle: int, method_name: str, parameter: str) -> None:
        """
        Calls a Plug-in DLL with method and parameter text arguments and returns a integer value from the DLL.

        Args:
            DLL_handle (int): The handle to the DLL.
            method_name (str): The name of the method to call.
            parameter (str): The parameter to pass to the method.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(DLL_handle)
        binary_payload += SDK_Helper.EncodeString(method_name)
        binary_payload += SDK_Helper.EncodeString(parameter)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CallDllIntStr')
        
        if response.status_code == 200:
            print(f"CallDllIntStr: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CallDllMeasurementDataIo(DLL_handle: int, method_name: str, measurement_component: str) -> None:
        """
        Calls a Plug-in DLL with method text arguments, passing in a reference to measurement component data as a 2-D float array for reading and/or writing.
        If the DLL indicates that the measurement is modified, Photometrica® will update the measurement stats, workspace image and dependent calculations. Photometrica® will not automatically regenerate the derived color components (x,y, CCT, etc.). This must be done by a call to RegenerateComponents. This way all the Tristimulus components can be modified by a call to CallDllMeasurementDataIo without having to spend time regenerating the derived color components after each call.

        Args:
            DLL_handle (int): The handle to the DLL.
            method_name (str): The name of the method to call.
            measurement_component (str): The measurement component to operate on.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(DLL_handle)
        binary_payload += SDK_Helper.EncodeString(method_name)
        binary_payload += SDK_Helper.EncodeString(measurement_component)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CallDllMeasurementDataIo')
        
        if response.status_code == 200:
            print(f"CallDllMeasurementDataIo: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CallDllStrStr(DLL_handle: int, method_name: str, parameter: str, buffer_size: int) -> str:
        """
        Calls a Plug-in DLL with method and parameter text arguments and returns a string value from the DLL.

        Args:
            DLL_handle (int): The handle to the DLL.
            method_name (str): The name of the method to call.
            parameter (str): The parameter to pass to the method.
            buffer_size (int): The size of the buffer to allocate for the response.

        Returns:
            str: The string value returned by the DLL.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(DLL_handle)
        binary_payload += SDK_Helper.EncodeString(method_name)
        binary_payload += SDK_Helper.EncodeString(parameter)
        binary_payload += SDK_Helper.EncodeInt(buffer_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CallDllStrStr')
        
        if response.status_code == 200:
            print(f"CallDllStrStr: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CancelAllBackgroundTasks() -> None:
        """
        Cancels all background tasks.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CancelAllBackgroundTasks')
        
        if response.status_code == 200:
            print(f"CancelAllBackgroundTasks: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CancelBackgroundTask(global_var_name: str) -> None:
        """
        Cancels a background task.

        Args:
            global_var_name (str): The name of the global variable representing the background task.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(global_var_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CancelBackgroundTask')
        
        if response.status_code == 200:
            print(f"CancelBackgroundTask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def Capture(capture_scheme_name: str) -> None:
        """
        Performs a measurement capture operation using the parameters of a capture scheme. The 3 parameter call uses a UDW instead of the pop up progress window. The 4 parameter version is non-blocking and uses global variables instead of the progress window. It optionally runs a script when the capture is complete.
        A capture scheme may be created by calling AddCaptureScheme or AddColorCaptureScheme.

        Args:
            capture_scheme_name (str): The name of the capture scheme to use.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'Capture')
        
        if response.status_code == 200:
            print(f"Capture: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CaptureDarkCurrent() -> None:
        """
        Captures the set of dark current images for the active camera. When called with no parameters, all exposures are processed.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CaptureDarkCurrent')
        
        if response.status_code == 200:
            print(f"CaptureDarkCurrent: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CaptureDarkCurrentAveraged(averaging_count: int, spectrometer_averaging_count: int) -> None:
        """
        Captures the set of dark current images for the active camera, using averaging

        Args:
            averaging_count (int): The number of frames to average.
            spectrometer_averaging_count (int): The number of spectrometer frames to average.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(averaging_count)
        binary_payload += SDK_Helper.EncodeInt(spectrometer_averaging_count)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CaptureDarkCurrentAveraged')
        
        if response.status_code == 200:
            print(f"CaptureDarkCurrentAveraged: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CaptureExists(capture_scheme_name: str) -> bool:
        """
        Checks if a capture scheme exists.

        Args:
            capture_scheme_name (str): The name of the capture scheme to check.

        Returns:
            bool: True if the capture scheme exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CaptureExists')
        
        if response.status_code == 200:
            print(f"CaptureExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CaptureFfc(lens_ID: int, FoV_ID: int, iris_ID: int, exposure_time: float, averaging_count: int, filter_wheel_index: int) -> None:
        """
        Captures an FFC Image

        Args:
            lens_ID (int): The ID of the lens.
            FoV_ID (int): The ID of the field of view.
            iris_ID (int): The ID of the iris.
            exposure_time (float): The exposure time for the capture.
            averaging_count (int): The number of frames to average.
            filter_wheel_index (int): The index of the filter wheel position.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(lens_ID)
        binary_payload += SDK_Helper.EncodeInt(FoV_ID)
        binary_payload += SDK_Helper.EncodeInt(iris_ID)
        binary_payload += SDK_Helper.EncodeInt(exposure_time)
        binary_payload += SDK_Helper.EncodeInt(averaging_count)
        binary_payload += SDK_Helper.EncodeInt(filter_wheel_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CaptureFfc')
        
        if response.status_code == 200:
            print(f"CaptureFfc: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CaptureSpectrumToDataTable(
        dtName: str,
        gvPercentName: str,
        gvStatusName: str,
        scriptOnEnd: str,
        irisIdentifierCode: str,
        autoExpo: bool,
        exposureInMs: float,
        averaging: int,
        autoMinSignalLevel: bool,
        densityFilterPosition: int,
        specIndex: int
    ) -> None:
        """
        Uses the spectrometer to acquire a spectrum in a background thread to a data table. The background thread will periodically update the values of two global variables to indicate the progress and state of the acquisition. The background task can me canceled by calling CancelBackgroundTask. 

        Args:
            dtName (str): The name of the data table.
            gvPercentName (str): The name of the global variable for percent progress.
            gvStatusName (str): The name of the global variable for status.
            scriptOnEnd (str): The script to run on completion.
            irisIdentifierCode (str): The iris identifier code.
            autoExpo (bool): Whether to enable auto exposure.
            exposureInMs (float): The exposure time in milliseconds.
            averaging (int): The number of averages to take.
            autoMinSignalLevel (bool): Whether to enable automatic minimum signal level.
            densityFilterPosition (int): The position of the density filter.
            specIndex (int): The index of the spectrum.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dtName)
        binary_payload += SDK_Helper.EncodeString(gvPercentName)
        binary_payload += SDK_Helper.EncodeString(gvStatusName)
        binary_payload += SDK_Helper.EncodeString(scriptOnEnd)
        binary_payload += SDK_Helper.EncodeInt(irisIdentifierCode)
        binary_payload += SDK_Helper.EncodeBool(autoExpo)
        binary_payload += SDK_Helper.EncodeDouble(exposureInMs)
        binary_payload += SDK_Helper.EncodeInt(averaging)
        binary_payload += SDK_Helper.EncodeDouble(autoMinSignalLevel)
        binary_payload += SDK_Helper.EncodeInt(densityFilterPosition)
        binary_payload += SDK_Helper.EncodeInt(specIndex)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CaptureSpectrumToDataTable')
        
        if response.status_code == 200:
            print(f"CaptureSpectrumToDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ChangeLensConfig(lens_configuration_name: str, action: str, param: str) -> None:
        """
        Performs an action on a lens configuration

        Args:
            lens_configuration_name (str): The name of the lens configuration.
            action (str): The action to perform on the lens configuration.
            param (str): The parameter for the action.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(lens_configuration_name)
        binary_payload += SDK_Helper.EncodeString(action)
        binary_payload += SDK_Helper.EncodeString(param)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ChangeLensConfig')
        
        if response.status_code == 200:
            print(f"ChangeLensConfig: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ChangeMaskWithShape(
        shape_name: str,
        x: int,
        y: int,
        width: int,
        height: int,
        add_shape: bool,
        clear_first: bool
    ) -> None:
        """
        Changes the mask by adding or removing the shape.

        Args:
            shape_name (str): The name of the shape.
            x (int): The x position of the shape.
            y (int): The y position of the shape.
            width (int): The width of the shape.
            height (int): The height of the shape.
            add_shape (bool): Whether to add the shape.
            clear_first (bool): Whether to clear the mask first.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(shape_name)
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeBool(add_shape)
        binary_payload += SDK_Helper.EncodeBool(clear_first)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ChangeMaskWithShape')
        
        if response.status_code == 200:
            print(f"ChangeMaskWithShape: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ChangeMeasurementComponents(measurement_name: str, tab_delimited_component_names: str) -> None:
        """
        Changes the components of a measurement.

        Args:
            measurement_name (str): The name of the measurement.
            tab_delimited_component_names (str): The tab-delimited list of component names.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_component_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ChangeMeasurementComponents')
        
        if response.status_code == 200:
            print(f"ChangeMeasurementComponents: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CleanUpList(list_handle: int) -> None:
        """
        Cleans up the specified list.
        Args:
            list_handle (int): The handle of the list to clean up.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CleanUpList')
        if response.status_code == 200:
            print(f"CleanUpList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ClearDictionary(dictionary_name: str) -> None:
        """
        Clears the specified dictionary.

        Args:
            dictionary_name (str): The name of the dictionary to clear.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ClearDictionary')
        
        if response.status_code == 200:
            print(f"ClearDictionary: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def ClearList(list_handle: int) -> None:
        """

        Args:
            list_handle (int): The handle of the list to clear.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ClearList')
        if response.status_code == 200:
            print(f"ClearList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")

    @staticmethod
    def ClearMask() -> None:
        """
        Clears the current mask.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ClearMask')
        
        if response.status_code == 200:
            print(f"ClearMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ClearSelection() -> None:
        """
        Clears the current selection.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ClearSelection')
        
        if response.status_code == 200:
            print(f"ClearSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ClipAois(clipping_AOI_name: str, AOI_list: list[str], min_area: float) -> None:
        """
        Clips the AOIs specified using the region of an AOI, mask or selection. AOIs that are entirely outside the clip region or less than the minimum size are deleted.

        Args:
            clipping_AOI_name (str): The name of the clipping AOI.
            AOI_list (list[str]): The list of AOIs to clip.
            min_area (float): The minimum area for an AOI to be retained.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(clipping_AOI_name)
        binary_payload += SDK_Helper.EncodeString(AOI_list)
        binary_payload += SDK_Helper.EncodeInt(min_area)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ClipAois')
        
        if response.status_code == 200:
            print(f"ClipAois: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ClosePhotometrica(save_dirty_PMM: bool) -> None:
        """
        Closes the Photometrica application.

        Args:
            save_dirty_PMM (bool): Whether to save the current PMM if it is dirty.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(save_dirty_PMM)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ClosePhotometrica')
        
        if response.status_code == 200:
            print(f"ClosePhotometrica: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CloseSerialPort(serial_port_handle: int) -> None:
        """
        Close a connection to a serial port

        Args:
            serial_port_handle (int): The handle of the serial port to close.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(serial_port_handle)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CloseSerialPort')
        
        if response.status_code == 200:
            print(f"CloseSerialPort: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ColorCorrectMeasurement(color_correction_name: str, measurement_name: str) -> None:
        """
        Applies a Color Correction to a measurement. This call will fail if the source measurement already has been color corrected.

        Args:
            color_correction_name (str): The name of the color correction to apply.
            measurement_name (str): The name of the measurement to apply the color correction to.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_correction_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ColorCorrectMeasurement')
        
        if response.status_code == 200:
            print(f"ColorCorrectMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CombineAoi(AOI_name_tab_delimited_list: str) -> None:
        """
        Combines multiple AOIs into a single AOI.

        Args:
            AOI_name_tab_delimited_list (str): A tab-delimited list of AOI names to combine.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name_tab_delimited_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CombineAoi')
        
        if response.status_code == 200:
            print(f"CombineAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CombinePath(file_path_1: str, file_path_2: str) -> str:
        """
        Combines two file paths into a single path.

        Args:
            file_path_1 (str): The first file path to combine.
            file_path_2 (str): The second file path to combine.

        Returns:
            str: The combined file path.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path_1)
        binary_payload += SDK_Helper.EncodeString(file_path_2)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CombinePath')
        
        if response.status_code == 200:
            print(f"CombinePath: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ComputationExists(computation_name: str) -> bool:
        """
        Checks if a computation exists.

        Args:
            computation_name (str): The name of the computation to check.

        Returns:
            bool: True if the computation exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(computation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ComputationExists')
        
        if response.status_code == 200:
            print(f"ComputationExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def Compute(computation_name: str) -> None:
        """
        Performs a computation operation
        The target measurement defined in the compute scheme (or passed into the Script alternate form) will be updated with the results of the computation.

        Args:
            computation_name (str): The name of the computation to perform.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(computation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'Compute')
        
        if response.status_code == 200:
            print(f"Compute: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ConvertUnits(number: float, original_unit_name: str, new_unit_name: str) -> float:
        """
        Returns the number converted from one unit space to another. 
        Distance units supported are: µm, mm, cm, m, in, ft, px (also in the form micrometer, millimeter, centimeter, meter, inch, foot, ", ' ) 
        Area units are any distance unit with a 2 or ² suffix.

        Args:
            number (float): The number to convert.
            original_unit_name (str): The original unit of the number.
            new_unit_name (str): The new unit to convert the number to.

        Returns:
            float: The converted number.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(number)
        binary_payload += SDK_Helper.EncodeString(original_unit_name)
        binary_payload += SDK_Helper.EncodeString(new_unit_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ConvertUnits')
        
        if response.status_code == 200:
            print(f"ConvertUnits: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CopyDataTableRange(
        src_name: str,
        start_row: int,
        row_count: int,
        start_column: int,
        col_count: int,
        dest_table: str,
        dest_start_row: int,
        dest_start_col: int
    ) -> None:
        """
        Copies data from one table into another, replacing any cells that exist. If the destination table does not exist, it will be created. The destination table will automatically grow to contain the new content.

        Args:
            src_name (str): The name of the source table.
            start_row (int): The starting row of the source table.
            row_count (int): The number of rows to copy.
            start_column (int): The starting column of the source table.
            col_count (int): The number of columns to copy.
            dest_table (str): The name of the destination table.
            dest_start_row (int): The starting row of the destination table.
            dest_start_col (int): The starting column of the destination table.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(src_name)
        binary_payload += SDK_Helper.EncodeInt(start_row)
        binary_payload += SDK_Helper.EncodeInt(row_count)
        binary_payload += SDK_Helper.EncodeInt(start_column)
        binary_payload += SDK_Helper.EncodeInt(col_count)
        binary_payload += SDK_Helper.EncodeString(dest_table)
        binary_payload += SDK_Helper.EncodeInt(dest_start_row)
        binary_payload += SDK_Helper.EncodeInt(dest_start_col)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CopyDataTableRange')
        
        if response.status_code == 200:
            print(f"CopyDataTableRange: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def CopyList(list_handle: int) -> PM_List:
        """
        Creates a copy of the specified list.

        Args:
            list_handle (int): The handle of the list to copy.

        Returns:
            PM_List: A copy of the specified list.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CopyList')
        if response.status_code == 200:
            print(f"CopyList: Success")
            # Decode the response
            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def Correl(x_list: list[float], y_list: list[float]) -> float:
        """
        Returns the Pearson product-moment correlation coefficient for the set of (x,y) points.

        Args:
            x_list (list[float]): The list of x values.
            y_list (list[float]): The list of y values.

        Returns:
            float: The Pearson product-moment correlation coefficient.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDoubleArray(x_list)
        binary_payload += SDK_Helper.EncodeDoubleArray(y_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'Correl')
        
        if response.status_code == 200:
            print(f"Correl: Success")
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CreateColorGroup(color_group_name: str, color_space: str, comments: str) -> None:
        """
        Creates a new color group.

        Args:
            color_group_name (str): The name of the color group.
            color_space (str): The color space of the color group.
            comments (str): Any comments about the color group.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_group_name)
        binary_payload += SDK_Helper.EncodeString(color_space)
        binary_payload += SDK_Helper.EncodeString(comments)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CreateColorGroup')
        
        if response.status_code == 200:
            print(f"CreateColorGroup: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CreateList(list_length: int) -> int:
        """
        Creates a new list with the specified length.

        Args:
            list_length (int): The length of the list to create.

        Returns:
            int: The handle of the newly created list.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(list_length)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CreateList')
        if response.status_code == 200:
            print(f"CreateList: Success")
            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def CreateList(*args: list[str]) -> int:
        """
        Creates a new list with the specified elements.

        Args:
            *args (list[str]): The elements to include in the list.

        Returns:
            int: The handle of the newly created list.
        """
        binary_payload = b""
        for arg in args:
            # we should encode each of these as a string
            binary_payload += SDK_Helper.EncodeString(arg)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CreateList')
        if response.status_code == 200:
            print(f"CreateList: Success")
            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")


    @staticmethod
    def CropToDut(threshold: float, exposure_time_microseconds: int) -> None:
        """
        Crops the document to the bounding box of the pixels above the threshold specified when a single exposure is performed.
        Args:
            threshold (float): The threshold value.
            exposure_time_microseconds (int): The exposure time in microseconds.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(threshold)
        binary_payload += SDK_Helper.EncodeInt(exposure_time_microseconds)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CropToDut')
        
        if response.status_code == 200:
            print(f"CropToDut: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CropToSelection() -> None:
        """
        Crops the document to the currently selected area.

        Args:
            None

        Returns:
            None

        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CropToSelection')
        
        if response.status_code == 200:
            print(f"CropToSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CropToTheta(theta: float) -> None:
        """
        Crops the document to the specified theta value

        Args:
            theta (float): The theta value to crop to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(theta)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CropToTheta')
        
        if response.status_code == 200:
            print(f"CropToTheta: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CxToX(cx: float) -> float:
        """
        Converts a centered based x coordinate to a top-left based x coordinate.

        Args:
            cx (float): The centered x coordinate.

        Returns:
            float: The top-left based x coordinate.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(cx)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CxToX')
        
        if response.status_code == 200:
            print(f"CxToX: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def CyToY(cy: float) -> float:
        """
        Converts a centered based y coordinate to a top-left based y coordinate.

        Args:
            cy (float): The centered y coordinate.

        Returns:
            float: The top-left based y coordinate.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(cy)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'CyToY')
        
        if response.status_code == 200:
            print(f"CyToY: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteAllAoi() -> None:
        """
        Deletes all Areas of Interest (AOIs) from the document.

        Args:
            None
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteAllAoi')
        
        if response.status_code == 200:
            print(f"DeleteAllAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteAllIsolines(measurement_name: str) -> None:
        """
        Deletes all the isolines for all measurements or a specific one.

        Args:
            measurement_name (str): The name of the measurement to delete isolines for. Use the empty string for all measurements.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteAllIsolines')
        
        if response.status_code == 200:
            print(f"DeleteAllIsolines: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteAllObjects(object_type_name: str) -> None:
        """
        Deletes all objects of a specific type from the document.

        Args:
            object_type_name (str): The name of the object type to delete. ("colorcorrection", "colorgroup", "colorregion", "colorscheme", "metaplot", "presentation", "speceval")

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteAllObjects')
        
        if response.status_code == 200:
            print(f"DeleteAllObjects: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteAllProfiles() -> None:
        """
        Deletes all profile lines from the document

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteAllProfiles')
        
        if response.status_code == 200:
            print(f"DeleteAllProfiles: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteAoi(AOI_name: str) -> None:
        """
        Deletes a specific Area of Interest (AOI) from the document.

        Args:
            AOI_name (str): The name of the AOI to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteAoi')
        
        if response.status_code == 200:
            print(f"DeleteAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteCapture(capture_scheme_name: str) -> None:
        """
        Deletes a specific capture scheme from the document.

        Args:
            capture_scheme_name (str): The name of the capture scheme to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteCapture')
        
        if response.status_code == 200:
            print(f"DeleteCapture: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteColorGroups(color_group_name: str) -> None:
        """
        Deletes a specific color group from the document.

        Args:
            color_group_name (str): The name of the color group to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_group_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteColorGroups')
        
        if response.status_code == 200:
            print(f"DeleteColorGroups: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteComputation(computation_name: str) -> None:
        """
        Deletes a specific computation from the document.

        Args:
            computation_name (str): The name of the computation to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(computation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteComputation')
        
        if response.status_code == 200:
            print(f"DeleteComputation: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteCustomFilterRegistration(filter_registration_name: str) -> None:
        """
        Deletes a specific custom filter registration from the document.

        Args:
            filter_registration_name (str): The name of the filter registration to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(filter_registration_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteCustomFilterRegistration')
        
        if response.status_code == 200:
            print(f"DeleteCustomFilterRegistration: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteDictionary(dictionary_name: str) -> None:
        """
        Deletes a specific dictionary from the document.

        Args:
            dictionary_name (str): The name of the dictionary to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteDictionary')
        
        if response.status_code == 200:
            print(f"DeleteDictionary: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteFile(file_path: str) -> None:
        """
        Deletes a specific file on disk.

        Args:
            file_path (str): The path of the file to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteFile')
        
        if response.status_code == 200:
            print(f"DeleteFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteHighlightRule(highlight_scheme_name: str, rule_index: int) -> None:
        """
        Deletes a specific highlight rule from the document.

        Args:
            highlight_scheme_name (str): The name of the highlight scheme.
            rule_index (int): The index of the rule to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        binary_payload += SDK_Helper.EncodeInt(rule_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteHighlightRule')
        
        if response.status_code == 200:
            print(f"DeleteHighlightRule: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteHighlightScheme(highlight_scheme_name: str) -> None:
        """
        Deletes a specific highlight scheme from the document.

        Args:
            highlight_scheme_name (str): The name of the highlight scheme to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteHighlightScheme')
        
        if response.status_code == 200:
            print(f"DeleteHighlightScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteIsoline(value: float, measurement_name: str) -> None:
        """
        Deletes a specific isoline from the document.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(value)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteIsoline')
        
        if response.status_code == 200:
            print(f"DeleteIsoline: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def DeleteList(list_handle: int) -> None:
        """
        Deletes a specific list from the document.

        Args:
            list_handle (int): The handle of the list to delete.

        Returns:
            None
        """
        binary_payload = b""

        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteList')
        if response.status_code == 200:
            print(f"DeleteList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteMeasurement(measurement_name: str) -> None:
        """
        Deletes a specific measurement from the document.

        Args:
            measurement_name (str): The name of the measurement to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteMeasurement')
        
        if response.status_code == 200:
            print(f"DeleteMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteObject(object_type_name: str, object_name: str) -> None:
        """
        Deletes a specific object from the document.

        Args:
            object_type_name (str): The type of the object to delete.
            object_name (str): The name of the object to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(object_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteObject')
        
        if response.status_code == 200:
            print(f"DeleteObject: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteRefinementScheme(refinement: str) -> None:
        """
        Deletes a specific refinement scheme from the document.

        Args:
            refinement (str): The name of the refinement scheme to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(refinement)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteRefinementScheme')
        
        if response.status_code == 200:
            print(f"DeleteRefinementScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteReport(report_name: str) -> None:
        """
        Deletes a specific report from the document.

        Args:
            report_name (str): The name of the report to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteReport')
        
        if response.status_code == 200:
            print(f"DeleteReport: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DeleteUdwControls(UDW_name: str, UDW_panel_name: str) -> None:
        """
        Deletes a specific UDW control from the document.

        Args:
            UDW_name (str): The name of the UDW to delete.
            UDW_panel_name (str): The name of the UDW panel to delete.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_panel_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DeleteUdwControls')
        
        if response.status_code == 200:
            print(f"DeleteUdwControls: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DocumentHeight() -> int:
        """
        Returns the height of the document

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DocumentHeight')
        
        if response.status_code == 200:
            print(f"DocumentHeight: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DocumentWidth() -> int:
        """
        Returns the width of the document

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DocumentWidth')
        
        if response.status_code == 200:
            print(f"DocumentWidth: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DriverTransaction(DLL_name: str, request: str, input_dictionary_name: str, output_dictionary_name: str) -> None:
        """
        Initiates a driver transaction.

        Args:
            DLL_name (str): The name of the DLL to use.
            request (str): The request to send.
            input_dictionary_name (str): The name of the input dictionary.
            output_dictionary_name (str): The name of the output dictionary.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(DLL_name)
        binary_payload += SDK_Helper.EncodeString(request)
        binary_payload += SDK_Helper.EncodeString(input_dictionary_name)
        binary_payload += SDK_Helper.EncodeString(output_dictionary_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DriverTransaction')
        
        if response.status_code == 200:
            print(f"DriverTransaction: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DuplicateAoi(source_AOI_name: str, new_name: str) -> None:
        """
        Duplicates a specific area of interest (AOI) in the document.

        Args:
            source_AOI_name (str): The name of the AOI to duplicate.
            new_name (str): The name to give to the duplicated AOI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(source_AOI_name)
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DuplicateAoi')
        
        if response.status_code == 200:
            print(f"DuplicateAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DuplicateList(list_handle: int) -> PM_List:
        """
        Duplicates a list

        Args:
            list_handle (int): The handle of the list to duplicate.

        Returns:
            PM_List: A duplicate of the specified list.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DuplicateList')
        if response.status_code == 200:
            print(f"DuplicateList: Success")
            # Decode the response
            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DuplicateMeasurement(source_measurement_name: str, new_name: str) -> None:
        """
        Duplicates a specific measurement in the document.

        Args:
            source_measurement_name (str): The name of the measurement to duplicate.
            new_name (str): The name to give to the duplicated measurement.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(source_measurement_name)
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DuplicateMeasurement')
        
        if response.status_code == 200:
            print(f"DuplicateMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def DuplicatePresentation(source_presentation_name: str, new_name: str) -> None:
        """
        Duplicates a specific presentation in the document.

        Args:
            source_presentation_name (str): The name of the presentation to duplicate.
            new_name (str): The name to give to the duplicated presentation.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(source_presentation_name)
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'DuplicatePresentation')
        
        if response.status_code == 200:
            print(f"DuplicatePresentation: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def EnsureColorComponent(measurement_name: str, tab_delimited_type_names: str) -> None:
        """
        Regenerates the specified color components, if they do not currently exist.

        Args:
            measurement_name (str): The name of the measurement to ensure color components for.
            tab_delimited_type_names (str): A tab-delimited string of type names to ensure.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_type_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'EnsureColorComponent')
        
        if response.status_code == 200:
            print(f"EnsureColorComponent: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportAoi(AOI_name: str, measurement_name: str, reverse_rows: bool, output_file_path: str) -> None:
        """
        Exports AOI information to either the clipboard or a Comma Separated Value (CSV) file. 
        To specify a child AOI, you must prefix its name with its parent's name followed by a colon "parent_AOI_name:child_AOI_name". If the 'Target File' parameter is null or empty, then the target will be the clipboard.

        Args:
            AOI_name (str): The name of the AOI to export.
            measurement_name (str): The name of the measurement associated with the AOI.
            reverse_rows (bool): Whether to reverse the rows in the export.
            output_file_path (str): The file path to save the export to.
        
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(reverse_rows)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportAoi')
        
        if response.status_code == 200:
            print(f"ExportAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportAoiStats(AOI_name: str, measurement_name: str, output_file_path: str) -> None:
        """
        Export the statistics of an AOI to a Comma Separated Value (CSV) text file or the clipboard.

        Args:
            AOI_name (str): The name of the AOI to export.
            measurement_name (str): The name of the measurement associated with the AOI.
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportAoiStats')
        
        if response.status_code == 200:
            print(f"ExportAoiStats: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportAoiTable(output_file_path: str) -> None:
        """
        Exports the AOI table to a Comma Separated Value (CSV) file.

        Args:
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportAoiTable')
        
        if response.status_code == 200:
            print(f"ExportAoiTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportCameraProperties() -> None:
        """
        Copies a text summary of all the active camera's properties to the clipboard.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportCameraProperties')
        
        if response.status_code == 200:
            print(f"ExportCameraProperties: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportDataTable(data_table_name: str, output_file_path: str) -> None:
        """
        Exports the specified data table to a Comma Separated Value (CSV) file.

        Args:
            data_table_name (str): The name of the data table to export.
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportDataTable')
        
        if response.status_code == 200:
            print(f"ExportDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportEvaluationsTable(output_file_path: str) -> None:
        """
        Exports the evaluation results to a Comma Separated Value (CSV) file.

        Args:
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportEvaluationsTable')
        
        if response.status_code == 200:
            print(f"ExportEvaluationsTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportMeasurement(measurement_name: str, increment: int, output_file_path: str) -> None:
        """
        Exports the specified measurement to a Comma Separated Value (CSV) file.

        Args:
            measurement_name (str): The name of the measurement to export.
            increment (int): The increment value for the measurement.
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeInt(increment)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportMeasurement')
        
        if response.status_code == 200:
            print(f"ExportMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportMeasurementBitmap(
        output_file_path: str,
        measurement_name: str,
        show_measurement: bool,
        show_iso: bool,
        show_AOIs: bool,
        show_AOI_highlights: bool,
        show_AOI_labels: bool,
        show_annotation: bool,
        bounding_AOI_name: str
    ) -> None:
        """
        Exports the measurement bitmap to a file.

        Args:
            output_file_path (str): The file path to save the export to.
            measurement_name (str): The name of the measurement to export.
            show_measurement (bool): Whether to show the measurement.
            show_iso (bool): Whether to show the ISO.
            show_AOIs (bool): Whether to show the AOIs.
            show_AOI_highlights (bool): Whether to show the AOI highlights.
            show_AOI_labels (bool): Whether to show the AOI labels.
            show_annotation (bool): Whether to show the annotation.
            bounding_AOI_name (str): The name of the bounding AOI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(show_measurement)
        binary_payload += SDK_Helper.EncodeBool(show_iso)
        binary_payload += SDK_Helper.EncodeBool(show_AOIs)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_highlights)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_labels)
        binary_payload += SDK_Helper.EncodeBool(show_annotation)
        binary_payload += SDK_Helper.EncodeString(bounding_AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportMeasurementBitmap')
        
        if response.status_code == 200:
            print(f"ExportMeasurementBitmap: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportMeasurementToFile(measurement_name: str, output_file_path: str) -> None:
        """
        Exports the specified measurement to a file.

        Args:
            measurement_name (str): The name of the measurement to export.
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportMeasurementToFile')
        
        if response.status_code == 200:
            print(f"ExportMeasurementToFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportObjectTable(object_type_name: str, output_file_path: str, TDP_options: str) -> None:
        """
        Exports the specified object table to a Comma Separated Value (CSV) file.

        Args:
            object_type_name (str): The name of the object type to export.
            output_file_path (str): The file path to save the export to.
            TDP_options (str): The tab-delimited parameter options for the export. (see user manual)

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        binary_payload += SDK_Helper.EncodeString(TDP_options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportObjectTable')
        
        if response.status_code == 200:
            print(f"ExportObjectTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportProfile(profile_name: str, polar: bool, increment: float, output_file_path: str, options: str) -> None:
        """
        Exports the specified profile to a CSV file.

        Args:
            profile_name (str): The name of the profile to export.
            polar (bool): Whether the profile is polar.
            increment (float): The increment value for the profile.
            output_file_path (str): The file path to save the export to.
            options (str): The options for the export.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(profile_name)
        binary_payload += SDK_Helper.EncodeBool(polar)
        binary_payload += SDK_Helper.EncodeFloat(increment)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        binary_payload += SDK_Helper.EncodeString(options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportProfile')
        
        if response.status_code == 200:
            print(f"ExportProfile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportSpectrum(measurement_name: str, increment: float, output_file_path: str) -> None:
        """
        Exports the specified measurement spectrum to a CSV file.

        Args:
            measurement_name (str): The name of the measurement to export.
            increment (float): The increment value for the export.
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeFloat(increment)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportSpectrum')
        
        if response.status_code == 200:
            print(f"ExportSpectrum: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportSpectrumStats(measurement_name: str, output_file_path: str) -> None:
        """
        Exports spectral data to a CSV file

        Args:
            measurement_name (str): The name of the measurement to export.
            output_file_path (str): The file path to save the export to.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportSpectrumStats')
        
        if response.status_code == 200:
            print(f"ExportSpectrumStats: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ExportText(output_file_path: str, text: str) -> None:
        """
        Exports a text string to a file or the clipboard.

        Args:
            output_file_path (str): The file path to save the export to.
            text (str): The text string to export.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(output_file_path)
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ExportText')
        
        if response.status_code == 200:
            print(f"ExportText: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FillAoiHoles(AOI_name: str) -> None:
        """
        Fills holes in the specified Area of Interest (AOI).

        Args:
            AOI_name (str): The name of the AOI to fill holes in.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FillAoiHoles')
        
        if response.status_code == 200:
            print(f"FillAoiHoles: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FillDataTableRange(
        data_table_name: str,
        start_column: int,
        end_column: int,
        start_row: int,
        end_row: int,
        column_factor: float,
        row_factor: float,
        const_factor: float
    ) -> None:
        """
        Fills in the value, for a range of cells, of a data table, using the formula: ( column_index * column_factor + row_index * row_factor + constant ).

        Args:
            data_table_name (str): The name of the data table to fill.
            start_column (int): The starting column index.
            end_column (int): The ending column index.
            start_row (int): The starting row index.
            end_row (int): The ending row index.
            column_factor (float): The factor to multiply the column index by.
            row_factor (float): The factor to multiply the row index by.
            const_factor (float): The constant factor to add.
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(start_column)
        binary_payload += SDK_Helper.EncodeInt(end_column)
        binary_payload += SDK_Helper.EncodeInt(start_row)
        binary_payload += SDK_Helper.EncodeInt(end_row)
        binary_payload += SDK_Helper.EncodeDouble(column_factor)
        binary_payload += SDK_Helper.EncodeDouble(row_factor)
        binary_payload += SDK_Helper.EncodeDouble(const_factor)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FillDataTableRange')
        
        if response.status_code == 200:
            print(f"FillDataTableRange: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FilterExists(spatial_filter_name: str) -> bool:
        """
        Checks if a spatial filter exists.

        Args:
            spatial_filter_name (str): The name of the spatial filter to check.

        Returns:
            bool: True if the spatial filter exists, False otherwise.
        """

        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(spatial_filter_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FilterExists')
        
        if response.status_code == 200:
            print(f"FilterExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FilterList(list_handle: int, pattern: str, keep_matches: bool) -> None:
        """
        Filters the specified list based on a regular expression pattern.

        Args:
            list_handle (int): The handle of the list to filter.
            pattern (str): The regular expression pattern to match.
            keep_matches (bool): Whether to keep or remove matching items.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(pattern)
        binary_payload += SDK_Helper.EncodeBool(keep_matches)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FilterList')
        if response.status_code == 200:
            print(f"FilterList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def FilterList(list_handle: int, low: str, high: str, keep_between: bool) -> None:
        """
        Filters the specified list based on a range of values.

        Args:
            list_handle (int): The handle of the list to filter.
            low (str): The lower bound of the range.
            high (str): The upper bound of the range.
            keep_between (bool): Whether to keep or remove items within the range.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(low)
        binary_payload += SDK_Helper.EncodeString(high)
        binary_payload += SDK_Helper.EncodeBool(keep_between)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FilterList')
        if response.status_code == 200:
            print(f"FilterList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FilterMeasurementAoi(source_measurement_name: str, new_measurement_name: str, bounding_AOI_name: str, spatial_filter_name: str) -> None:
        """
        Creates a spatially filtered copy of a measurement where only the pixels within the AOI are processed. All pixels outside the AOI will be set to Invalid.

        Args:
            source_measurement_name (str): The name of the source measurement.
            new_measurement_name (str): The name of the new measurement.
            bounding_AOI_name (str): The name of the bounding area of interest.
            spatial_filter_name (str): The name of the spatial filter to apply.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(source_measurement_name)
        binary_payload += SDK_Helper.EncodeString(new_measurement_name)
        binary_payload += SDK_Helper.EncodeString(bounding_AOI_name)
        binary_payload += SDK_Helper.EncodeString(spatial_filter_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FilterMeasurementAoi')
        
        if response.status_code == 200:
            print(f"FilterMeasurementAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FilterMeasurements(spatial_filter_name: str) -> None:
        """
        Applies named filter to all measurements.
        When filtering is performed on color measurements, the filter is applied to the tristimulus components and the derivative components are then regenerated. If the source measurement had X1 and X2 components these will not exist in the filtered measurement.
        The default filters are:
        - box3x3mean
        - box5x5mean
        - circle5x5mean
        - circle7x7mean
        - circle11x11mean
        - circle15x15mean
        - box3x3median
        - box5x5median
        - circle7x7median

        see user manual for additional information about custom filters.

        Args:
            spatial_filter_name (str): The name of the spatial filter to apply.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(spatial_filter_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FilterMeasurements')
        
        if response.status_code == 200:
            print(f"FilterMeasurements: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindCell(data_table_name: str, row: int, column: int) -> str:
        """
        Returns the content (value) of a named data table's cell, identified by matching values in the first column's cells and first row's cells.

        Args:
            data_table_name (str): The name of the data table.
            row (int): The row index (0-based).
            column (int): The column index (0-based).
        Returns:
            str: The content of the cell.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(row)
        binary_payload += SDK_Helper.EncodeString(column)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindCell')
        
        if response.status_code == 200:
            print(f"FindCell: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindColumn(data_table_name: str, text_to_match: str, row_to_search: int) -> int:
        """
        Finds the specified column content on the specified row and returns the column index where the match occurred. If no match occurred, returns a negative one (-1).

        Args:
            data_table_name (str): The name of the data table.
            text_to_match (str): The text to match in the specified row.
            row_to_search (int): The row index (0-based) to search for the text.

        Returns:
            int: The column index where the match occurred, or -1 if no match was found.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(text_to_match)
        binary_payload += SDK_Helper.EncodeInt(row_to_search)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindColumn')
        
        if response.status_code == 200:
            print(f"FindColumn: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindGridAois(object_name: str, use_datatable: bool) -> None:
        """
        Using a grid pattern, find regions with the statistic requested and create output AOIs. 

        Args:
            object_name (str): The name of the object to find AOIs for.
            use_datatable (bool): true if name is a data table, false if name is a dictionary.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_name)
        binary_payload += SDK_Helper.EncodeBool(use_datatable)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindGridAois')
        
        if response.status_code == 200:
            print(f"FindGridAois: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindIntersectionOfLines(
        x1: float, y1: float, x2: float, y2: float,
        x3: float, y3: float, x4: float, y4: float
    ) -> tuple[float, float]:
        """
        Find the (x,y) intersection of two lines defined using points (x0,y0),(x1,y1) and (x2,y2),(x3,y3). NaN is returned when the lines are parallel.

        Args:
            x1 (float): The x-coordinate of the first point on the first line.
            y1 (float): The y-coordinate of the first point on the first line.
            x2 (float): The x-coordinate of the second point on the first line.
            y2 (float): The y-coordinate of the second point on the first line.
            x3 (float): The x-coordinate of the first point on the second line.
            y3 (float): The y-coordinate of the first point on the second line.
            x4 (float): The x-coordinate of the second point on the second line.
            y4 (float): The y-coordinate of the second point on the second line.

        Returns:
            Tuple[float, float]: The (x,y) coordinates of the intersection point, or (NaN, NaN) if the lines are parallel.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(x1)
        binary_payload += SDK_Helper.EncodeDouble(y1)
        binary_payload += SDK_Helper.EncodeDouble(x2)
        binary_payload += SDK_Helper.EncodeDouble(y2)
        binary_payload += SDK_Helper.EncodeDouble(x3)
        binary_payload += SDK_Helper.EncodeDouble(y3)
        binary_payload += SDK_Helper.EncodeDouble(x4)
        binary_payload += SDK_Helper.EncodeDouble(y4)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindIntersectionOfLines')
        
        if response.status_code == 200:
            print(f"FindIntersectionOfLines: Success")

            # Decode the response
            value1 = SDK_Helper.DecodeDouble(response.content[:8])

            value2 = SDK_Helper.DecodeDouble(response.content[8:16])
            return (value1, value2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindNearestRow(data_table_name: str, value: float, column_to_search: int) -> int:
        """
        Finds the row index with the value in the specified column that is nearest the specified value. The column MUST have values in numeric order to use this method.

        Args:
            data_table_name (str): The name of the data table to search.
            value (float): The value to find the nearest row for.
            column_to_search (int): The column index to search in.

        Returns:
            int: The index of the nearest row, or -1 if not found.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeDouble(value)
        binary_payload += SDK_Helper.EncodeInt(column_to_search)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindNearestRow')
        
        if response.status_code == 200:
            print(f"FindNearestRow: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindPointOnLine(x0: float, y0: float, x1: float, y1: float, x: float) -> int:
        """
        Using linear interpolation or linear extrapolation, finds the corresponding y value for a given x value on a line defined by points (x0,y0) and (x1,y1). NaN is returned if x1 and x0 are equal.
        The formula used is: y = y0 + (y1 - y0 ) * ( (x - x0 ) * (x1 - x0) ).

        Args:
            x0 (float): The x-coordinate of the first point on the line.
            y0 (float): The y-coordinate of the first point on the line.
            x1 (float): The x-coordinate of the second point on the line.
            y1 (float): The y-coordinate of the second point on the line.
            x (float): The x-coordinate for which to find the corresponding y-coordinate.
        
        Returns:
            int: The y-coordinate corresponding to the given x-coordinate, or NaN if the line is vertical.

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(x0)
        binary_payload += SDK_Helper.EncodeDouble(y0)
        binary_payload += SDK_Helper.EncodeDouble(x1)
        binary_payload += SDK_Helper.EncodeDouble(y1)
        binary_payload += SDK_Helper.EncodeDouble(x)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindPointOnLine')
        
        if response.status_code == 200:
            print(f"FindPointOnLine: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindPolygon(
        measurement_component: str,
        threshold: float,
        max_edge_angle: float,
        min_edge_length: float,
        expected_edge_count: int,
        start_x: float,
        start_y: float
    ) -> list[tuple[float, float]]:
        """
        Find the best fit polygon using threshold on measurement.

        Args:
            measurement_component (str): The measurement component to use.
            threshold (float): The threshold value for the measurement.
            max_edge_angle (float): The maximum edge angle for the polygon.
            min_edge_length (float): The minimum edge length for the polygon.
            expected_edge_count (int): The expected number of edges for the polygon.
            start_x (float): The starting x-coordinate for the polygon.
            start_y (float): The starting y-coordinate for the polygon.

        Returns:
            list[tuple[float, float]]: A list of (x, y) coordinates representing the vertices of the best fit polygon.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_component)
        binary_payload += SDK_Helper.EncodeDouble(threshold)
        binary_payload += SDK_Helper.EncodeDouble(max_edge_angle)
        binary_payload += SDK_Helper.EncodeInt(min_edge_length)
        binary_payload += SDK_Helper.EncodeInt(expected_edge_count)
        binary_payload += SDK_Helper.EncodeInt(start_x)
        binary_payload += SDK_Helper.EncodeInt(start_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindPolygon')
        
        if response.status_code == 200:
            print(f"FindPolygon: Success")

            # Decode the response

            # Read the size of the pointslist array as an int
            pointslist_size = SDK_Helper.DecodeInt(response.content[:4])

            # The array is written as x1,y1,x2,y2,x3,y3,...,xn,yn (each value is a float)
            pointslist = []
            for i in range(pointslist_size):
                x = SDK_Helper.DecodeFloat(response.content[4 + i * 8: 8 + i * 8])
                y = SDK_Helper.DecodeFloat(response.content[8 + i * 8: 12 + i * 8])
                
                pointslist.append((x, y))
            
            return pointslist
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FindRow(data_table_name: str, text_to_match: str, search_column: int) -> int:
        """
        Finds the specified row content on the specified column and returns the row index where the match occurred. If no match occurred, returns a negative one (-1).

        Args:
            data_table_name (str): The name of the data table to search.
            text_to_match (str): The text to match in the specified column.
            search_column (int): The index of the column to search in.

        Returns:
            int: The row index of the matching text, or -1 if not found.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(text_to_match)
        binary_payload += SDK_Helper.EncodeInt(search_column)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FindRow')
        
        if response.status_code == 200:
            print(f"FindRow: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FreeDll(DLL_handle: int) -> None:
        """
        Causes a plug-in DLL to be unloaded from memory.

        Args:
            DLL_handle (int): The handle of the DLL to unload.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(DLL_handle)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FreeDll')
        
        if response.status_code == 200:
            print(f"FreeDll: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FtpDownload(FTP_URL: str, destpath: str, username: str, password: str) -> str:
        """
        Downloads a file from an FTP server.

        Args:
            FTP_URL (str): The FTP URL of the file to download.
            destpath (str): The local path where the file should be saved.
            username (str): The username for FTP authentication.
            password (str): The password for FTP authentication.

        Returns:
            str: The result of the download operation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(FTP_URL)
        binary_payload += SDK_Helper.EncodeString(destpath)
        binary_payload += SDK_Helper.EncodeString(username)
        binary_payload += SDK_Helper.EncodeString(password)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FtpDownload')
        
        if response.status_code == 200:
            print(f"FtpDownload: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FtpGetDirectory(FTP_URL: str, username: str, password: str) -> str:
        """
        Retrieves the list of files and directories in a specified FTP directory.

        Args:
            FTP_URL (str): The FTP URL of the directory to list.
            username (str): The username for FTP authentication.
            password (str): The password for FTP authentication.

        Returns:
            str: The list of files and directories in the specified FTP directory.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(FTP_URL)
        binary_payload += SDK_Helper.EncodeString(username)
        binary_payload += SDK_Helper.EncodeString(password)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FtpGetDirectory')
        
        if response.status_code == 200:
            print(f"FtpGetDirectory: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def FtpUpload(FTP_URL: str, srcpath: str, username: str, password: str) -> None:
        """
        Uploads a file to an FTP server

        Args:
            FTP_URL (str): The FTP URL of the file to upload.
            srcpath (str): The local path of the file to upload.
            username (str): The username for FTP authentication.
            password (str): The password for FTP authentication.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(FTP_URL)
        binary_payload += SDK_Helper.EncodeString(srcpath)
        binary_payload += SDK_Helper.EncodeString(username)
        binary_payload += SDK_Helper.EncodeString(password)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'FtpUpload')
        
        if response.status_code == 200:
            print(f"FtpUpload: Success")

        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GamutArea(color_space_name: str, AOI_name: str, tab_delmited_measurement_names: str) -> float:
        """
        Returns the area of the gamut formed by a convex hull around the chromaticity points of the 3+ measurements specified.

        Args:
            color_space_name (str): The name of the color space.
            AOI_name (str): The name of the area of interest.
            tab_delmited_measurement_names (str): A tab-delimited string of measurement names.

        Returns:
            float: The area of the gamut.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_space_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(tab_delmited_measurement_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GamutArea')
        
        if response.status_code == 200:
            print(f"GamutArea: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetActiveInstrument() -> None:
        """
        Retrieves the currently active instrument.

        Args:
            None
        Returns:
            The serial number of the active instrument
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetActiveInstrument')
        
        if response.status_code == 200:
            print(f"GetActiveInstrument: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetActiveMeasurement() -> str:
        """
        Gets the name of the currently active measurement

        Args:
            None

        Returns:
            str: The name of the currently active measurement
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetActiveMeasurement')
        
        if response.status_code == 200:
            print(f"GetActiveMeasurement: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiCount(root_AOI_name: str) -> int:
        """
        Retrieves the count of AOIs meeting specific criteria.

        Args:
            root_AOI_name (str): If empty, output is the number of root level AOIs. If "*", output is the number of root and child AOIs. If the name is a root-level AOI, output is the number of children

        Returns:
            int: The count of areas of interest.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(root_AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiCount')
        
        if response.status_code == 200:
            print(f"GetAoiCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiCountInColorRegion(color_region_name: str, measurement_name: str, AOI_name: str) -> int:
        """
        Retrieves the count of AOIs within a specific color region.

        Args:
            color_region_name (str): The name of the color region.
            measurement_name (str): The name of the measurement.
            AOI_name (str): The name of the area of interest.

        Returns:
            int: The count of areas of interest within the color region.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_region_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiCountInColorRegion')
        
        if response.status_code == 200:
            print(f"GetAoiCountInColorRegion: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiData(aoiName: str, measurement_name: str, outside_value: float) -> list[float]:
        """
        Retrieves the data for a specific area of interest (AOI) within a measurement.

        Args:
            aoiName (str): The name of the area of interest.
            measurement_name (str): The name of the measurement.
            outside_value (float): The value to use for points outside the AOI.

        Returns:
            list[float]: The data for the specified area of interest.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(aoiName)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeFloat(outside_value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiData')
        
        if response.status_code == 200:
            print(f"GetAoiData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)

            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiDimensions(AOI_name: str) -> tuple[int, int]:
        """
        Retrieves the dimensions of a specific area of interest (AOI).

        Args:
            AOI_name (str): The name of the area of interest.

        Returns:
            tuple: A tuple containing the width and height of the AOI.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiDimensions')
        
        if response.status_code == 200:
            print(f"GetAoiDimensions: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeInt(response.content[:4])
            result2 = SDK_Helper.DecodeInt(response.content[4:8])
            return (result1, result2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiIntersectionStat(AOI_1_name: str, AOI_2_name: str, property_name: str, measurement_name: str) -> float:
        """
        Returns the AOI property of the AOI which is the intersection of the two specified AOIs. Returns NaN if there is no intersection.

        Args:
            AOI_1_name (str): The name of the first area of interest.
            AOI_2_name (str): The name of the second area of interest.
            property_name (str): The name of the property to retrieve.
            measurement_name (str): The name of the measurement.

        Returns:
            float: The value of the property for the intersection of the two AOIs, or NaN if there is no intersection.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_1_name)
        binary_payload += SDK_Helper.EncodeString(AOI_2_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiIntersectionStat')
        
        if response.status_code == 200:
            print(f"GetAoiIntersectionStat: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiName(root_index: int, child_index: int) -> str:
        """
        Retrieves the name of a specific area of interest (AOI) based on its indices.

        Args:
            root_index (int): The root index of the AOI.
            child_index (int): The child index of the AOI.

        Returns:
            str: The name of the AOI.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(root_index)
        binary_payload += SDK_Helper.EncodeInt(child_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiName')
        
        if response.status_code == 200:
            print(f"GetAoiName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiProperty(property_name: str, AOI_name: str, measurement_name: str) -> float:
        """
        Retrieves the value of a specific property for a given area of interest (AOI) and measurement.

        Args:
            property_name (str): The name of the property to retrieve.
            AOI_name (str): The name of the area of interest.
            measurement_name (str): The name of the measurement.

        Returns:
            float: The value of the property for the specified AOI and measurement.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiProperty')
        
        if response.status_code == 200:
            print(f"GetAoiProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloat(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiSummaryCount() -> int:
        """
        Retrieves the count of area of interest (AOI) summary entries.
        Args:
            None
        Returns:
            int: The count of AOI summary entries.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiSummaryCount')
        
        if response.status_code == 200:
            print(f"GetAoiSummaryCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiSummaryName(index: int) -> str:
        """
        Retrieves the name of a specific area of interest (AOI) summary based on its index.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiSummaryName')
        
        if response.status_code == 200:
            print(f"GetAoiSummaryName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiSummaryProperty(aoi_name: str, property_name: str) -> str:
        """
        Retrieves the value of a specific property for a given area of interest (AOI) summary.

        Args:
            aoi_name (str): The name of the area of interest.
            property_name (str): The name of the property to retrieve.

        Returns:
            str: The value of the property for the specified AOI summary.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(aoi_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiSummaryProperty')
        
        if response.status_code == 200:
            print(f"GetAoiSummaryProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiTableCellValue(AOI_name: str, column: str) -> float:
        """
        Retrieves the value of a specific cell in the AOI table.

        Args:
            AOI_name (str): The name of the area of interest.
            column (str): The name of the column to retrieve.

        Returns:
            float: The value of the specified cell in the AOI table.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(column)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiTableCellValue')
        
        if response.status_code == 200:
            print(f"GetAoiTableCellValue: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiTableData(delimter: str, linefeed: str) -> str:
        """
        Retrieves the table data for the area of interest (AOI).

        Args:
            delimter (str): The delimiter used in the table data. (defaults to tab)
            linefeed (str): The line feed character used in the table data. (defaults to crlf)

        Returns:
            str: The table data for the specified AOI.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(delimter)
        binary_payload += SDK_Helper.EncodeString(linefeed)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiTableData')
        
        if response.status_code == 200:
            print(f"GetAoiTableData: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiTableStat(column: str, stat_name: str, MMF_name: str, MMF_value: str) -> str:
        """
        Retrieves a statistic for a column of cells in the AOI table, filtered by meta field value, parent AOI, or name prefix.
        Note that values that appear in the GUI are rounded, but the results of GetAoiTableStat will not be.

        Args:
            column (str): The name of the column to retrieve.
            stat_name (str): The name of the statistic to retrieve. (see user manual for details)
            MMF_name (str): The name of the meta field to filter by. (see user manual for details)
            MMF_value (str): The value of the meta field to filter by.

        Returns:
            str: The value of the specified statistic for the AOI table.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(column)
        binary_payload += SDK_Helper.EncodeString(stat_name)
        binary_payload += SDK_Helper.EncodeString(MMF_name)
        binary_payload += SDK_Helper.EncodeString(MMF_value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiTableStat')
        
        if response.status_code == 200:
            print(f"GetAoiTableStat: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAoiTextProperty(property_name: str, AOI_name: str) -> str:
        """
        Retrieves a text property for a specific area of interest (AOI).

        Args:
            property_name (str): The name of the property to retrieve.
            AOI_name (str): The name of the AOI to retrieve the property from.

        Returns:
            str: The value of the specified property for the AOI.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAoiTextProperty')
        
        if response.status_code == 200:
            print(f"GetAoiTextProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetAutoResponse(popup_ID: int) -> int:
        """
        Retrieves the automatic response for a specific popup.

        Args:
            popup_ID (int): The ID of the popup to retrieve the response for.

        Returns:
            int: The automatic response for the specified popup. (see user manual for details)
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(popup_ID)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetAutoResponse')
        
        if response.status_code == 200:
            print(f"GetAutoResponse: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetCaptureCount() -> int:
        """
        Retrieves the total number of captures.
        
        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetCaptureCount')

        if response.status_code == 200:
            print(f"GetCaptureCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetCaptureName(index: int) -> str:
        """
        Retrieves the name of a specific capture.

        Args:
            index (int): The index of the capture to retrieve the name for.

        Returns:
            str: The name of the specified capture.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetCaptureName')
        
        if response.status_code == 200:
            print(f"GetCaptureName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetCaptureProperty(property_name: str, capture_scheme_name: str) -> str:
        """
        Retrieves a specific property for a capture scheme.

        Args:
            property_name (str): The name of the property to retrieve.
            capture_scheme_name (str): The name of the capture scheme to retrieve the property from.

        Returns:
            str: The value of the specified property for the capture scheme.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetCaptureProperty')
        
        if response.status_code == 200:
            print(f"GetCaptureProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetCaptureSetting(property_name: str) -> str:
        """
        Retrieves a specific setting for a capture.

        Args:
            property_name (str): The name of the setting to retrieve.

        Returns:
            str: The value of the specified setting for the capture.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetCaptureSetting')
        
        if response.status_code == 200:
            print(f"GetCaptureSetting: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetCell(data_table_name: str, row: int, column: int) -> str:
        """
        Retrieves the value of a specific cell in a data table.

        Args:
            data_table_name (str): The name of the data table.
            row (int): The row index of the cell.
            column (int): The column index of the cell.

        Returns:
            str: The value of the specified cell.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(row)
        binary_payload += SDK_Helper.EncodeInt(column)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetCell')
        
        if response.status_code == 200:
            print(f"GetCell: Success")

            
            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetColorSpaceBitmap(color_space_scheme_name: str, width: int, height: int) -> bytes:
        """
        Retrieves a bitmap representation of a specific color space.

        Args:
            color_space_scheme_name (str): The name of the color space scheme.
            width (int): The width of the bitmap.
            height (int): The height of the bitmap.

        Returns:
            bytes: The bitmap representation of the specified color space.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(color_space_scheme_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeString(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetColorSpaceBitmap')
        
        if response.status_code == 200:
            print(f"GetColorSpaceBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetComputationCount() -> int:
        """
        Retrieves the total number of computations.

        Args:
            None

        Returns:
            int: The total number of computations.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetComputationCount')
        
        if response.status_code == 200:
            print(f"GetComputationCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetComputationName(index: int) -> str:
        """
        Retrieves the name of a specific computation.

        Args:
            index (int): The index of the computation to retrieve.

        Returns:
            str: The name of the specified computation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetComputationName')
        
        if response.status_code == 200:
            print(f"GetComputationName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetComputationProperty(property_name: str, computation_name: str) -> str:
        """
        Retrieves the value of a specific property for a computation.

        Args:
            property_name (str): The name of the property to retrieve.
            computation_name (str): The name of the computation.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(computation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetComputationProperty')
        
        if response.status_code == 200:
            print(f"GetComputationProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetCountsFromLuminance(iris_ID: int, exposure_time: float, luminance: float) -> float:
        """
        Determines the sensor counts value which corresponds to a particular luminance for a specific exposure time and lens configuration.
        Only works with calibrations with second-order linearity

        Args:
            iris_ID (int): The ID of the iris.
            exposure_time (float): The exposure time.
            luminance (float): The luminance value.

        Returns:
            float: The corresponding sensor counts value.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(iris_ID)
        binary_payload += SDK_Helper.EncodeDouble(exposure_time)
        binary_payload += SDK_Helper.EncodeDouble(luminance)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetCountsFromLuminance')
        
        if response.status_code == 200:
            print(f"GetCountsFromLuminance: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetDataTableProperty(property_name: str, data_table_name: str) -> str:
        """
        Retrieves the value of a specific property for a data table.

        Args:
            property_name (str): The name of the property to retrieve.
            data_table_name (str): The name of the data table.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetDataTableProperty')
        
        if response.status_code == 200:
            print(f"GetDataTableProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetDataTableRange(
        data_table_name: str,
        start_column: int,
        end_column: int,
        start_row: int,
        end_row: int,
        param: str
    ) -> list[float]:
        """
        Returns a list with the values from a range of data table cells. By default the table to traversed by row from top to bottom and within each row from left to right.

        Args:
            data_table_name (str): The name of the data table.
            start_column (int): The starting column index.
            end_column (int): The ending column index.
            start_row (int): The starting row index.
            end_row (int): The ending row index.
            param (str): Additional parameter for the request.

        Returns:
            list[float]: A list of float values from the specified range.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(data_table_name)
        binary_payload += SDK_Helper.EncodeString(start_column)
        binary_payload += SDK_Helper.EncodeInt(end_column)
        binary_payload += SDK_Helper.EncodeInt(start_row)
        binary_payload += SDK_Helper.EncodeInt(end_row)
        binary_payload += SDK_Helper.EncodeInt(param)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetDataTableRange')
        
        if response.status_code == 200:
            print(f"GetDataTableRange: Success")

            # Decode the response
            result = SDK_Helper.DecodeDoubleArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetDataTableStat(
        data_table_name: str,
        stat_name: str,
        start_col: int,
        end_col: int,
        start_row: int,
        end_row: int
    ) -> float:
        """
        Retrieves a specific statistic from a data table.

        Args:
            data_table_name (str): The name of the data table.
            stat_name (str): The name of the statistic to retrieve.
            start_col (int): The starting column index.
            end_col (int): The ending column index.
            start_row (int): The starting row index.
            end_row (int): The ending row index.

        Returns:
            float: The value of the specified statistic.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(stat_name)
        binary_payload += SDK_Helper.EncodeInt(start_col)
        binary_payload += SDK_Helper.EncodeInt(end_col)
        binary_payload += SDK_Helper.EncodeInt(start_row)
        binary_payload += SDK_Helper.EncodeInt(end_row)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetDataTableStat')
        
        if response.status_code == 200:
            print(f"GetDataTableStat: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetDictionaryValue(dictionary_name: str, key: str) -> str:
        """
        Retrieve a value from a dictionary

        Args:
            dictionary_name (str): The name of the dictionary.
            key (str): The key of the value to retrieve.
        Returns:
            str: The value associated with the specified key in the dictionary.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        binary_payload += SDK_Helper.EncodeString(key)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetDictionaryValue')
        
        if response.status_code == 200:
            print(f"GetDictionaryValue: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetDocumentProperty(property_name: str) -> str:
        """
        Get a named property for the current document

        Args:
            property_name (str): The name of the property to retrieve. (see user manual)
        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetDocumentProperty')
        
        if response.status_code == 200:
            print(f"GetDocumentProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetDocumentVariable(name: str) -> str:
        """
        Returns the value of a document variable or a global variable. Document variables start with "@@" and global variables start with "$".

        Args:
            name (str): The name of the variable to retrieve.

        Returns:
            str: The value of the specified variable.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetDocumentVariable')
        
        if response.status_code == 200:
            print(f"GetDocumentVariable: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetEvaluationCount() -> int:
        """
        Get the total number of evaluations.

        Args:
            None
        Returns:
            int: The total number of evaluations.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetEvaluationCount')
        
        if response.status_code == 200:
            print(f"GetEvaluationCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetEvaluationName(index: int) -> str:
        """
        Get the name of an evaluation by its index.

        Args:
            index (int): The index of the evaluation.

        Returns:
            str: The name of the specified evaluation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetEvaluationName')
        
        if response.status_code == 200:
            print(f"GetEvaluationName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetEvaluationProperty(property_name: str, evaluation_name: str) -> str:
        """
        Get a specific property of an evaluation by its name.

        Args:
            property_name (str): The name of the property to retrieve.
            evaluation_name (str): The name of the evaluation to retrieve the property from.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(evaluation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetEvaluationProperty')
        
        if response.status_code == 200:
            print(f"GetEvaluationProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetEvaluationTableCellValue(evaluation_name: str) -> float:
        """
        Get the value of a specific cell in the evaluation table.

        Args:
            evaluation_name (str): The name of the evaluation.

        Returns:
            float: The value of the specified cell.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(evaluation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetEvaluationTableCellValue')
        
        if response.status_code == 200:
            print(f"GetEvaluationTableCellValue: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetFilterCount() -> int:
        """
        Get the total number of filters.

        Args:
            None

        Returns:
            int: The total number of filters.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetFilterCount')
        
        if response.status_code == 200:
            print(f"GetFilterCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetFilterName(index: int) -> str:
        """
        Get the name of a specific filter by its index.

        Args:
            index (int): The index of the filter to retrieve.
        
        Returns:
            str: The name of the specified filter.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetFilterName')
        
        if response.status_code == 200:
            print(f"GetFilterName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetFilterProperty(property_name: str, spatial_filter_name: str) -> str:
        """
        Get a specific property of a filter.

        Args:
            property_name (str): The name of the property to retrieve.
            spatial_filter_name (str): The name of the spatial filter.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(spatial_filter_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetFilterProperty')
        
        if response.status_code == 200:
            print(f"GetFilterProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetFolderPath(special_folder_name: str) -> str:
        """
        Gets the full path of a special folder
        
        Args:
            special_folder_name (str): The name of the special folder to retrieve the path for.

        Returns:
            str: The full path of the specified special folder.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(special_folder_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetFolderPath')
        
        if response.status_code == 200:
            print(f"GetFolderPath: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetGlobal(global_variable_name: str) -> str:
        """
        Retrieves the value of a global variable.

        Args:
            global_variable_name (str): The name of the global variable to retrieve.

        Returns:
            str: The value of the specified global variable.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(global_variable_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetGlobal')
        
        if response.status_code == 200:
            print(f"GetGlobal: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetHighlightRuleCount(highlight_scheme_name: str) -> int:
        """
        Returns the number of rules within a highlight schema
        
        Args:
            highlight_scheme_name (str): The name of the highlight scheme to retrieve the rule count for.

        Returns:
            int: The number of rules within the specified highlight scheme.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetHighlightRuleCount')
        
        if response.status_code == 200:
            print(f"GetHighlightRuleCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetHighlightRuleProperty(property_name: str, highlight_scheme_name: str, rule_index: int) -> str:
        """
        Retrieves the value of a specific property within a highlight rule.

        Args:
            property_name (str): The name of the property to retrieve.
            highlight_scheme_name (str): The name of the highlight scheme.
            rule_index (int): The index of the rule within the highlight scheme.

        Returns:
            str: The value of the specified property within the highlight rule.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        binary_payload += SDK_Helper.EncodeInt(rule_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetHighlightRuleProperty')
        
        if response.status_code == 200:
            print(f"GetHighlightRuleProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetHighlightSchemeCount() -> int:
        """
        Returns the number of highlight schemes available in the document.

        Args:
            None

        Returns:
            int: The number of highlight schemes available in the document.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetHighlightSchemeCount')
        
        if response.status_code == 200:
            print(f"GetHighlightSchemeCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetHighlightSchemeName(index: int) -> str:
        """
        Retrieves the name of a highlight scheme by its index.

        Args:
            index (int): The index of the highlight scheme to retrieve.

        Returns:
            str: The name of the highlight scheme.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetHighlightSchemeName')
        
        if response.status_code == 200:
            print(f"GetHighlightSchemeName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetHistogramData(measurement: str, aoi: str, bins: int, log: bool) -> list[float]:
        """
        Gets histogram data (counts in each bin). To get the bin start and end values as well use AddDataTableFromHistogram
        
        Args:
            measurement (str): The measurement to analyze.
            aoi (str): The area of interest.
            bins (int): The number of bins to use for the histogram.
            log (bool): Whether to use logarithmic scaling.

        Returns:
            list[float]: The histogram data (counts in each bin).
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement)
        binary_payload += SDK_Helper.EncodeString(aoi)
        binary_payload += SDK_Helper.EncodeInt(bins)
        binary_payload += SDK_Helper.EncodeBool(log)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetHistogramData')
        
        if response.status_code == 200:
            print(f"GetHistogramData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetHistogramProperty(property_name: str) -> str:
        """
        Gets a property for the histogram window
        
        Args:
            property_name (str): The name of the property to retrieve.
            
        Returns:
            str: The value of the requested property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetHistogramProperty')
        
        if response.status_code == 200:
            print(f"GetHistogramProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetLastError() -> str:
        """
        Retrieves the last error message.
        NOTE: The last error is set every time a function is called. 
        If the statement is embedded with a function call, such as "A( B() )", GetLastError will return the details for the outermost function "A" regardless of the result of "B". 
        
        To get the error text and the error code, call GetLastErrorCode followed by GetLastError. 
        GetLastError will reset the last error, but GetLastErrorCode will not.
        
        Args:
            None
        Returns:
            str: The last error message.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetLastError')
        
        if response.status_code == 200:
            print(f"GetLastError: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetLastFormResult() -> int:
        """
        Retrieves the result of the last form submission.
        
        Args:
            None

        Returns:
            int: The result of the last form submission.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetLastFormResult')
        
        if response.status_code == 200:
            print(f"GetLastFormResult: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def GetList(list_handle: int) -> PM_List:
        """
        Retrieves a list by its handle.

        Args:
            list_handle (int): The handle of the list to retrieve.

        Returns:
            PM_List: The requested list.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetList')

        if response.status_code == 200:
            print(f"GetList: Success")

            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def GetListCount(list_handle: int, value_to_count: str = None) -> int:
        """
        Retrieves the count of items in a list.

        Args:
            list_handle (int): The handle of the list to count items in.
            value_to_count (str, optional): A specific value to count occurrences of.

        Returns:
            int: The count of items in the list.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        if value_to_count is not None:
            binary_payload += SDK_Helper.EncodeString(value_to_count)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetListCount')

        if response.status_code == 200:
            print(f"GetListCount: Success")
            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetListIndex(list_handle: int, value_to_find: str, value_part_index: int = -1) -> int:
        """
        Retrieves the index of a specific value in a list.

        Args:
            list_handle (int): The handle of the list to search.
            value_to_find (str): The value to find in the list.
            value_part_index (int, optional): The part index of the value to find.

        Returns:
            int: The index of the value in the list, or -1 if not found.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(value_to_find)
        if value_part_index != -1:
            binary_payload += SDK_Helper.EncodeInt(value_part_index)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetListIndex')
        if response.status_code == 200:
            print(f"GetListIndex: Success")
            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def GetListRange(list_handle: int, start_index: int, count: int) -> PM_List:
        """
        Returns a new list with a copy of the specified number of elements from the source list starting at the start index.

        Args:
            list_handle (int): The handle of the list to copy elements from.
            start_index (int): The index to start copying from.
            count (int): The number of elements to copy.

        Returns:
            PM_List: A new list containing the copied elements.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeInt(start_index)
        binary_payload += SDK_Helper.EncodeInt(count)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetListRange')
        if response.status_code == 200:
            print(f"GetListRange: Success")
            # Decode the response
            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def GetListStat(list_handle: int, stat_name: str, param: float = 50) -> float:
        """
        Returns a statistical value from a list.

        Args:
            list_handle (int): The handle of the list to retrieve statistics from.
            stat_name (str): The name of the statistic to retrieve.
            param (float, optional): An optional parameter for the statistic.

        Returns:
            float: The requested statistical value.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(stat_name)
        binary_payload += SDK_Helper.EncodeDouble(param)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetListStat')
        if response.status_code == 200:
            print(f"GetListStat: Success")
            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def GetListSubset(list_handle: int, index_list_handle: int) -> PM_List:
        """
        Returns a list that contains a subset of the values from an input list according to a list of indices into the source list. 
        Indices outside the range of the source list are ignored.
        
        Args:
            list_handle (int): The handle of the list to retrieve a subset from.
            index_list_handle (int): The handle of the list containing the indices to use for the subset.

        Returns:
            PM_List: A new list containing the subset of values.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeInt(index_list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetListSubset')
        if response.status_code == 200:
            print(f"GetListSubset: Success")
            # Decode the response
            result = SDK_Helper.DecodePMList(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetListValue(list_handle: int, index: int, partIdx: int = -1) -> str | float:
        """
        Retrieves a value from a list.

        Args:
            list_handle (int): The handle of the list to retrieve the value from.
            index (int): The index of the value to retrieve.
            partIdx (int, optional): The part index of the value to retrieve.

        Returns:
            str | float: The retrieved value, which can be either a string or a float.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeInt(index)
        binary_payload += SDK_Helper.EncodeInt(partIdx)
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetListValue')
        if response.status_code == 200:
            print(f"GetListValue: Success")
            # Decode the response
            # We can do this by checking the first byte of the response
            type_id = SDK_Helper.DecodeInt(response.content[:4])
            if type_id == 1:  # String
                # Decode the 7-bit encoded length of the string
                value = SDK_Helper.DecodeString(response.content[4:])
            elif type_id == 2:  # Double
                value = SDK_Helper.DecodeDouble(response.content[4:])
            else:
                raise ValueError(f"Unknown type ID: {type_id}")
            return value
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")


    @staticmethod
    def GetLongestExposureForLuminanceMax(iris_ID: int, max_luminance: int, FoV_ID: int, lens_ID: float) -> float:
        """
        Returns the longest exposure time, which accommodates a given maximum luminance. 

        You can also query the camera for calibrated exposure set information using GetCameraProperty. 
        for properties "maxexposure", "minexposure", etc. Calling AddInstrumentDataTable( "exposure", ... ) will return a complete table of calibrated exposures with luminance range information for each.
        
        Args:
            iris_ID (int): The ID of the iris to query.
            max_luminance (int): The maximum luminance to accommodate.
            FoV_ID (int): The ID of the field of view to query.
            lens_ID (float): The ID of the lens to query.
        
        Returns:
            float: The longest exposure time that accommodates the given maximum luminance.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(iris_ID)
        binary_payload += SDK_Helper.EncodeInt(max_luminance)
        binary_payload += SDK_Helper.EncodeInt(FoV_ID)
        binary_payload += SDK_Helper.EncodeDouble(lens_ID)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetLongestExposureForLuminanceMax')
        
        if response.status_code == 200:
            print(f"GetLongestExposureForLuminanceMax: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementBitmap(name: str, show_isolines: bool, show_AOIs: bool, show_AOI_highlights: bool, show_AOI_labels: bool, show_annotation: bool) -> bytes:
        """
        Returns a bitmap of a measurement, with overlay and other optional graphics
        
        Args:
            name (str): The name of the measurement to retrieve.
            show_isolines (bool): Whether to show isolines in the bitmap.
            show_AOIs (bool): Whether to show areas of interest in the bitmap.
            show_AOI_highlights (bool): Whether to show highlights for areas of interest.
            show_AOI_labels (bool): Whether to show labels for areas of interest.
            show_annotation (bool): Whether to show annotations in the bitmap.
            
        Returns:
            bytes: The bitmap data of the measurement.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        binary_payload += SDK_Helper.EncodeBool(show_isolines)
        binary_payload += SDK_Helper.EncodeBool(show_AOIs)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_highlights)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_labels)
        binary_payload += SDK_Helper.EncodeBool(show_annotation)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementBitmap')
        
        if response.status_code == 200:
            print(f"GetMeasurementBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementBitmapEx(measurement_name: str, show_measurement: bool, show_isolines: bool, show_AOIs: bool, show_highlights: bool, show_AOI_labels: bool, show_annotation: bool, bounding_AOI_name: str) -> None:
        """
        Returns a bitmap of a measurement with extended options (optional clipping to an AOI's bounding box).
        
        Args:
            measurement_name (str): The name of the measurement to retrieve.
            show_measurement (bool): Whether to show the measurement in the bitmap.
            show_isolines (bool): Whether to show isolines in the bitmap.
            show_AOIs (bool): Whether to show areas of interest in the bitmap.
            show_highlights (bool): Whether to show highlights for areas of interest.
            show_AOI_labels (bool): Whether to show labels for areas of interest.
            show_annotation (bool): Whether to show annotations in the bitmap.
            bounding_AOI_name (str): The name of the bounding area of interest.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(show_measurement)
        binary_payload += SDK_Helper.EncodeBool(show_isolines)
        binary_payload += SDK_Helper.EncodeBool(show_AOIs)
        binary_payload += SDK_Helper.EncodeBool(show_highlights)
        binary_payload += SDK_Helper.EncodeBool(show_AOI_labels)
        binary_payload += SDK_Helper.EncodeBool(show_annotation)
        binary_payload += SDK_Helper.EncodeString(bounding_AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementBitmapEx')
        
        if response.status_code == 200:
            print(f"GetMeasurementBitmapEx: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementCount() -> int:
        """
        Returns the count of measurements.
        
        Args:
            None
        
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementCount')
        
        if response.status_code == 200:
            print(f"GetMeasurementCount: Success")
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementData(measurement_name: str) -> list[float]:
        """
        Returns the data for a measurement. It is a 1d array of floats of size DocumentWidth()xDocumentHeight().
        
        Args:
            measurement_name (str): The name of the measurement to retrieve.
        
        Returns:
            list[float]: The data for the measurement.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementData')
        
        if response.status_code == 200:
            print(f"GetMeasurementData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)
            return result
        
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementHistogramBitmap(measurement_name: str, width: int, height: int, y_axis_log: bool, x_axis_log: bool, zoom_horizontal: bool) -> bytes:
        """
        Returns a bitmap of a measurement's histogram graph

        Args:
            measurement_name (str): The name of the measurement to retrieve.
            width (int): The width of the bitmap.
            height (int): The height of the bitmap.
            y_axis_log (bool): Whether to use a logarithmic scale for the y-axis.
            x_axis_log (bool): Whether to use a logarithmic scale for the x-axis.
            zoom_horizontal (bool): Whether to zoom in on the horizontal axis.

        Returns:
            bytes: The bitmap of the measurement's histogram graph.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeBool(y_axis_log)
        binary_payload += SDK_Helper.EncodeBool(x_axis_log)
        binary_payload += SDK_Helper.EncodeBool(zoom_horizontal)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementHistogramBitmap')
        
        if response.status_code == 200:
            print(f"GetMeasurementHistogramBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementLineData(measurement_component_name: str, x0: float, y0: float, x1: float, y1: float) -> list[float]:
        """
        This method returns a list of measurement data values from a line with end point point coordinates listed. 
        The method uses a set of pixels that connect the two points. 
        If the line is on an angle, the set of pixels will follow a stair-case pattens where the x,y coordinates are rounded to the nearest pixel. 
        (This as opposed to interpolating values for sub-pixel coordinates.) The values returned are always from the top-left to bottom right.
        
        Args:
            measurement_component_name (str): The name of the measurement component.
            x0 (float): The x-coordinate of the start point.
            y0 (float): The y-coordinate of the start point.
            x1 (float): The x-coordinate of the end point.
            y1 (float): The y-coordinate of the end point.
        
        Returns:
            list[float]: A list of measurement data values from the specified line.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_component_name)
        binary_payload += SDK_Helper.EncodeInt(x0)
        binary_payload += SDK_Helper.EncodeInt(y0)
        binary_payload += SDK_Helper.EncodeInt(x1)
        binary_payload += SDK_Helper.EncodeInt(y1)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementLineData')
        
        if response.status_code == 200:
            print(f"GetMeasurementLineData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementLogData(measurement_name: str, log_section_name: str, log_subsection_name: str, item_name: str) -> str:
        """
        This method retrieves log data for a specific measurement.
        See user manual for parameters for the log section and subsection names.
        
        Args:
            measurement_name (str): The name of the measurement.
            log_section_name (str): The name of the log section.
            log_subsection_name (str): The name of the log subsection.
            item_name (str): The name of the item.

        Returns:
            str: The log data for the specified measurement.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(log_section_name)
        binary_payload += SDK_Helper.EncodeString(log_subsection_name)
        binary_payload += SDK_Helper.EncodeString(item_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementLogData')
        
        if response.status_code == 200:
            print(f"GetMeasurementLogData: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementName(index: int) -> str:
        """
        Retrieves the name of a measurement by its 0-based index.
        
        Args:
            index (int): The 0-based index of the measurement.
            
        Returns:
            str: The name of the measurement.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementName')
        
        if response.status_code == 200:
            print(f"GetMeasurementName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementProperty(property_name: str, measurement_name: str) -> str:
        """
        Returns the value of a measurement's built in property or custom property (meta field).
        See user manual for details on property names and their usage.
        
        Args:
            property_name (str): The name of the property.
            measurement_name (str): The name of the measurement.
        
        Returns:
            str: The value of the specified property for the given measurement.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementProperty')
        
        if response.status_code == 200:
            print(f"GetMeasurementProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMeasurementThetaHVBitmap(measurement_name: str) -> bytes:
        """
        Returns a bitmap of a measurement in ThetaH/ThetaV space.

        Args:
            measurement_name (str): The name of the measurement.
            
        Returns:
            bytes: The bitmap of the measurement in ThetaH/ThetaV space.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMeasurementThetaHVBitmap')
        
        if response.status_code == 200:
            print(f"GetMeasurementThetaHVBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMetaInfo(variable_name: str) -> str:
        """
        Retrieve a script variable value 
        
        Args:
            variable_name (str): The name of the variable to retrieve.
            
        Returns:
            str: The value of the specified variable.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(variable_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMetaInfo')
        
        if response.status_code == 200:
            print(f"GetMetaInfo: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMetaPlotBitmap(meta_plot_scheme_name: str, width: int, height: int, stat_name: int, y_axis_log: bool, x_axis_log: bool, normalize: bool, first_datum_as_baseline: bool) -> bytes:
        """
        Returns a bitmap of a meta-plot, showing change over a series measurements.

        Args:
            meta_plot_scheme_name (str): The name of the meta-plot scheme.
            width (int): The width of the bitmap.
            height (int): The height of the bitmap.
            stat_name (int): The statistic to plot.
            y_axis_log (bool): Whether to use a logarithmic scale for the Y axis.
            x_axis_log (bool): Whether to use a logarithmic scale for the X axis.
            normalize (bool): Whether to normalize the data.
            first_datum_as_baseline (bool): Whether to use the first datum as the baseline.
            
        Returns:
            bytes: The bitmap of the meta-plot.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(meta_plot_scheme_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeInt(stat_name)
        binary_payload += SDK_Helper.EncodeBool(y_axis_log)
        binary_payload += SDK_Helper.EncodeBool(x_axis_log)
        binary_payload += SDK_Helper.EncodeBool(normalize)
        binary_payload += SDK_Helper.EncodeBool(first_datum_as_baseline)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMetaPlotBitmap')
        
        if response.status_code == 200:
            print(f"GetMetaPlotBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMetaPlotData(meta_field_name: str, aoi_name: str) -> list[float]:
        """
        Gets an ordered sequence of values, which are the mean values, of a given AOI, for all measurements having the meta field specified.

        Args:
            meta_field_name (str): The name of the meta field.
            aoi_name (str): The name of the area of interest.

        Returns:
            list[float]: The data points for the meta-plot.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(meta_field_name)
        binary_payload += SDK_Helper.EncodeString(aoi_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMetaPlotData')
        
        if response.status_code == 200:
            print(f"GetMetaPlotData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetMmfProperty(MMF_property: str, MMF_name: str) -> str:
        """
        Gets the value of a specified MMF property.

        Args:
            MMF_property (str): The name of the MMF property.
            MMF_name (str): The name of the MMF.

        Returns:
            str: The value of the specified MMF property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(MMF_property)
        binary_payload += SDK_Helper.EncodeString(MMF_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetMmfProperty')
        
        if response.status_code == 200:
            print(f"GetMmfProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetObjectCount(object_type_name: str) -> int:
        """
        Gets the count of objects of a specific type.

        Args:
            object_type_name (str): The name of the object type.

        Returns:
            int: The count of objects of the specified type.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetObjectCount')
        
        if response.status_code == 200:
            print(f"GetObjectCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetObjectName(object_type: str, index: int, child_index: int) -> str:
        """
        Gets the name of a specific object.

        Args:
            object_type (str): The type of the object.
            index (int): The index of the object.
            child_index (int): For some objects, like AOI and measurements, the name of a specific child may be requested. Pass in negative one (-1) to get the parent name.

        Returns:
            str: The name of the specified object.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type)
        binary_payload += SDK_Helper.EncodeInt(index)
        binary_payload += SDK_Helper.EncodeInt(child_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetObjectName')
        
        if response.status_code == 200:
            print(f"GetObjectName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetObjectProperty(object_type_name: str, property_name: str, object_name: str) -> str:
        """
        Gets the value of a specific property of an object.

        Args:
            object_type_name (str): The name of the object type.
            property_name (str): The name of the property.
            object_name (str): The name of the object.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(object_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetObjectProperty')
        
        if response.status_code == 200:
            print(f"GetObjectProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetPerspectiveTransform(source_quad_point_list: list[float], target_quad_point_list: list[float]) -> list[float]:
        """
        Calculates the geographic transformation matrix, which maps the source quadrilateral to the destination quadrilateral. Usually the destination quadrilateral is a non-rotated rectangle.

        Args:
            source_quad_point_list (list[float]): The source quadrilateral points.
            target_quad_point_list (list[float]): The target quadrilateral points.

        Returns:
            list[float]: The transformation matrix.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloatArray(source_quad_point_list)
        binary_payload += SDK_Helper.EncodeFloatArray(target_quad_point_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetPerspectiveTransform')
        
        if response.status_code == 200:
            print(f"GetPerspectiveTransform: Success")

            # Decode the response
            result = SDK_Helper.DecodeDoubleArray(response.content)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetPhotometricaSetting(setting_name: str) -> str:
        """
        Gets the value of a specific setting in Photometrica.
        See the user manual for list of setting names
        
        Args:
            setting_name (str): The name of the setting to retrieve.

        Returns:
            str: The value of the specified setting.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(setting_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetPhotometricaSetting')
        
        if response.status_code == 200:
            print(f"GetPhotometricaSetting: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetPresentationCount() -> int:
        """
        Gets the count of presentations in the document
        
        Args:
            None
            
        Returns:
            int: The count of presentations.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetPresentationCount')
        
        if response.status_code == 200:
            print(f"GetPresentationCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetPresentationName(index: int) -> str:
        """
        Gets the name of a presentation by its index.

        Args:
            index (int): The index of the presentation.

        Returns:
            str: The name of the specified presentation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetPresentationName')
        
        if response.status_code == 200:
            print(f"GetPresentationName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetPresentationProperty(property_name: str, presentation_name: str) -> str:
        """
        Returns a property for a presentation
        
        Args:
            property_name (str): The name of the property to retrieve.
            presentation_name (str): The name of the presentation.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetPresentationProperty')
        
        if response.status_code == 200:
            print(f"GetPresentationProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetProfileCount() -> int:
        """
        Gets the count of profiles in the document

        Args:
            None

        Returns:
            int: The count of profiles.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetProfileCount')
        
        if response.status_code == 200:
            print(f"GetProfileCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetProfileData(profile_name: str, measurement_name: str, polar: bool, increment: float) -> list[float]:
        """
        Returns the profile line data
        
        Args:
            profile_name (str): The name of the profile.
            measurement_name (str): The name of the measurement.
            polar (bool): Whether the profile is polar.
            increment (float): The increment value.

        Returns:
            list[float]: The profile line data.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(profile_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(polar)
        binary_payload += SDK_Helper.EncodeFloat(increment)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetProfileData')
        
        if response.status_code == 200:
            print(f"GetProfileData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)
            return result

        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetProfileDataSize(profile_name: str, polar: bool, increment: float) -> int:
        """
        Returns the size of the profile data.

        Args:
            profile_name (str): The name of the profile.
            polar (bool): Whether the profile is polar.
            increment (float): The increment value.

        Returns:
            int: The size of the profile data.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(profile_name)
        binary_payload += SDK_Helper.EncodeBool(polar)
        binary_payload += SDK_Helper.EncodeFloat(increment)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetProfileDataSize')
        
        if response.status_code == 200:
            print(f"GetProfileDataSize: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetProfileName(index: int) -> str:
        """
        Gets the name of the profile at the specified index.

        Args:
            index (int): The index of the profile.

        Returns:
            str: The name of the profile.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetProfileName')
        
        if response.status_code == 200:
            print(f"GetProfileName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetProfilePlotBitmap(profile_name: str, width: int, height: int, measurement_name: str, y_axis_log: bool, x_axis_log: bool, smoothing_factor: float, polar: bool) -> bytes:
        """
        Returns a bitmap of a profile graph.

        Args:
            profile_name (str): The name of the profile.
            width (int): The width of the bitmap.
            height (int): The height of the bitmap.
            measurement_name (str): The name of the measurement.
            y_axis_log (bool): Whether to use a logarithmic scale for the y-axis.
            x_axis_log (bool): Whether to use a logarithmic scale for the x-axis.
            smoothing_factor (float): The smoothing factor to apply to the data.
            polar (bool): Whether the profile is polar.

        Returns:
            bytes: The bitmap data.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(profile_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(y_axis_log)
        binary_payload += SDK_Helper.EncodeBool(x_axis_log)
        binary_payload += SDK_Helper.EncodeInt(smoothing_factor)
        binary_payload += SDK_Helper.EncodeBool(polar)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetProfilePlotBitmap')
        
        if response.status_code == 200:
            print(f"GetProfilePlotBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetProfileProperty(property_name: str, profile_name: str, measurement_name: str) -> str:
        """
        Returns some information about a profile.

        Args:
            property_name (str): The name of the property.
            profile_name (str): The name of the profile.
            measurement_name (str): The name of the measurement.
            
        Returns:
            str: The value of the property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(profile_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetProfileProperty')
        
        if response.status_code == 200:
            print(f"GetProfileProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetReferenceSlope() -> float:
        """
        Retrieves the current reference angle

        Args:
            None
            
        Returns:
            float: The current reference angle.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetReferenceSlope')
        
        if response.status_code == 200:
            print(f"GetReferenceSlope: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloat(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetRefinementProperty(property_name: str, refinement_scheme_name: str) -> str:
        """
        Returns a property of a refinement scheme. Booleans will be returned capitalized.

        Args:
            property_name (str): The name of the property.
            refinement_scheme_name (str): The name of the refinement scheme.

        Returns:
            str: The value of the property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(refinement_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetRefinementProperty')
        
        if response.status_code == 200:
            print(f"GetRefinementProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetRefinementSchemeCount() -> int:
        """
        Returns the number of refinement schemes.

        Args:
            None
        Returns:
            int: The number of refinement schemes.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetRefinementSchemeCount')
        
        if response.status_code == 200:
            print(f"GetRefinementSchemeCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetRefinementSchemeName(index: int) -> str:
        """
        Retrieves the refinement scheme name given a specific index.

        Args:
            index (int): The index of the refinement scheme.

        Returns:
            str: The name of the refinement scheme.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetRefinementSchemeName')
        
        if response.status_code == 200:
            print(f"GetRefinementSchemeName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetReportCount() -> int:
        """
        Returns the number of reports in the current document.
        
        Args:
            None

        Returns:
            int: The number of reports in the current document.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetReportCount')
        
        if response.status_code == 200:
            print(f"GetReportCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetReportName(index: int) -> str:
        """
        Retrieves the report name given a specific index.

        Args:
            index (int): The index of the report.

        Returns:
            str: The name of the report.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetReportName')
        
        if response.status_code == 200:
            print(f"GetReportName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetScriptCode(script_name: str) -> str:
        """
        Returns the plaintext of a script given its name.

        Args:
            script_name (str): The name of the script.

        Returns:
            str: The plaintext of the script.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(script_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetScriptCode')
        
        if response.status_code == 200:
            print(f"GetScriptCode: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetScriptCount() -> int:
        """
        Returns the number of scripts in the current document.

        Args:
            None

        Returns:
            int: The number of scripts in the current document.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetScriptCount')
        
        if response.status_code == 200:
            print(f"GetScriptCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetScriptName(index: int) -> str:
        """
        Retrieves the script name given a specific index.

        Args:
            index (int): The index of the script.

        Returns:
            str: The name of the script.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetScriptName')
        
        if response.status_code == 200:
            print(f"GetScriptName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetSelectedAoiName() -> str:
        """
        Retrieves the name of the currently selected Area of Interest (AOI).

        Args:
            None
        Returns:
            str: The name of the currently selected AOI.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetSelectedAoiName')
        
        if response.status_code == 200:
            print(f"GetSelectedAoiName: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetSelectedPixelCount() -> int:
        """
        Returns the number of pixels in the currently selected region.

        Args:
            None

        Returns:
            int: The number of pixels in the currently selected region.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetSelectedPixelCount')
        
        if response.status_code == 200:
            print(f"GetSelectedPixelCount: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetShortestExposureForMidLuminance(iris_ID: int, luminance: float) -> float:
        """
        Returns the shortest exposure time such that the luminance is in the range of 20% to 80% of the sensor counts range.

        You can also query the camera for calibrated exposure set information using GetCameraProperty. 
        for properties "maxexposure", "minexposure", etc. Calling AddInstrumentDataTable( "exposure", ... ) will return a complete table of calibrated exposures with luminance range information for each.

        Args:
            iris_ID (int): The ID of the iris.
            luminance (float): The target luminance value.

        Returns:
            float: The shortest exposure time for the given iris ID and luminance.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(iris_ID)
        binary_payload += SDK_Helper.EncodeDouble(luminance)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetShortestExposureForMidLuminance')
        
        if response.status_code == 200:
            print(f"GetShortestExposureForMidLuminance: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetSoftwareInfo() -> tuple[int, int, int]:
        """
        Returns the software version information.

        Args:
            None

        Returns:
            tuple[int, int, int]: A tuple containing the major, minor, and build version numbers.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetSoftwareInfo')
        
        if response.status_code == 200:
            print(f"GetSoftwareInfo: Success")

            # Decode the response
            versionMajor = SDK_Helper.DecodeInt(response.content[:4])
            versionMinor = SDK_Helper.DecodeInt(response.content[4:8])
            versionBuild = SDK_Helper.DecodeInt(response.content[8:12])
            return (versionMajor, versionMinor, versionBuild)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetSurfacePlotBitmap(measurement_name: str, width: int, height: int, AOI_name: str) -> bytes:
        """
        Returns a bitmap image of the surface plot for the specified measurement and area of interest.

        Args:
            measurement_name (str): The name of the measurement.
            width (int): The width of the bitmap image.
            height (int): The height of the bitmap image.
            AOI_name (str): The name of the area of interest.

        Returns:
            bytes: The bitmap image data.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetSurfacePlotBitmap')
        
        if response.status_code == 200:
            print(f"GetSurfacePlotBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetThermometerBitmap(measurement_name: str, width: int, height: int) -> bytes:
        """
        Returns a bitmap image of the thermometer plot for the specified measurement.

        Args:
            measurement_name (str): The name of the measurement.
            width (int): The width of the bitmap image.
            height (int): The height of the bitmap image.

        Returns:
            bytes: The bitmap image data.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetThermometerBitmap')
        
        if response.status_code == 200:
            print(f"GetThermometerBitmap: Success")

            # Decode the response
            result = SDK_Helper.DecodeByteArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetTimePlotData(measurement_name: str, aoi_name: str) -> list[float]:
        """
        Gets an ordered sequence of values, which are the mean values of a given AOI, over all historic (timed) instances of a measurement.

        Args:
            measurement_name (str): The name of the measurement.
            aoi_name (str): The name of the area of interest.
            
        Returns:
            list[float]: A list of mean values for the specified AOI over all historic instances.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(aoi_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetTimePlotData')
        
        if response.status_code == 200:
            print(f"GetTimePlotData: Success")

            # Decode the response
            result = SDK_Helper.DecodeFloatArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetTranslatedText(row: str, table_name: str) -> str:
        """
        Gets the text translation for a specific row in the translation table.

        Args:
            row (str): The row to translate.
            table_name (str): The name of the translation table.

        Returns:
            str: The translated text.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(row)
        binary_payload += SDK_Helper.EncodeString(table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetTranslatedText')
        
        if response.status_code == 200:
            print(f"GetTranslatedText: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetTypeUnits(data_type_name: str) -> str:
        """
        Gets the units for a specific data type.

        Args:
            data_type_name (str): The name of the data type.

        Returns:
            str: The units for the specified data type.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_type_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetTypeUnits')
        
        if response.status_code == 200:
            print(f"GetTypeUnits: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetUdwCtrlProperty(UDW_name: str, UDW_control_name: str, property_name: str) -> str:
        """
        Gets a specific property value from a UDW control.
        See the user manual for a list of property names

        Args:
            UDW_name (str): The name of the UDW.
            UDW_control_name (str): The name of the UDW control.
            property_name (str): The name of the property.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetUdwCtrlProperty')
        
        if response.status_code == 200:
            print(f"GetUdwCtrlProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetUdwCtrlText(UDW_name: str, UDW_control_name: str) -> str:
        """
        Gets the text value from a UDW control.

        Args:
            UDW_name (str): The name of the UDW.
            UDW_control_name (str): The name of the UDW control.

        Returns:
            str: The text value of the specified UDW control.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetUdwCtrlText')
        
        if response.status_code == 200:
            print(f"GetUdwCtrlText: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetWindowProperty(window_name: str, property_name: str) -> str:
        """
        Returns a window's property. The window can be user-defined or one of the predefined windows below. 
        See the User Interface page in the user manual for more details on predefined windows.
        
        Args:
            window_name (str): The name of the window.
            property_name (str): The name of the property.

        Returns:
            str: The value of the specified property.
            
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(window_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetWindowProperty')
        
        if response.status_code == 200:
            print(f"GetWindowProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetWorkingFolder(get_name_only: bool) -> str:
        """
        Gets the current working folder.

        Args:
            get_name_only (bool): If True, only the name of the folder is returned.

        Returns:
            str: The current working folder.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(get_name_only)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetWorkingFolder')
        
        if response.status_code == 200:
            print(f"GetWorkingFolder: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GetWorkspaceProperty(property_name: str) -> str:
        """
        Gets a workspace property.

        Args:
            property_name (str): The name of the property.

        Returns:
            str: The value of the specified property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GetWorkspaceProperty')
        
        if response.status_code == 200:
            print(f"GetWorkspaceProperty: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GIArea(color_region_name: str, AOI_name: str, tab_delimited_measurement_names: str) -> float:
        """
        Returns the area of the gamut formed by a convex hull around the chromaticity points of the 3+ measurements specified intersected with the color region specified.

        Args:
            color_region_name (str): The name of the color region.
            AOI_name (str): The name of the area of interest.
            tab_delimited_measurement_names (str): The tab-delimited list of measurement names.
        
        Returns:
            float: The area of the specified region.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_region_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_measurement_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GIArea')
        
        if response.status_code == 200:
            print(f"GIArea: Success")

            # Decode the response
            result = SDK_Helper.DecodeDouble(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def GroupAoiByMetaField(AMF_name: str, reverse: bool) -> None:
        """
        Groups AOI in the AOI table according to their values for a specified AOI meta field.

        Args:
            AMF_name (str): The name of the AOI meta field.
            reverse (bool): If True, the grouping is reversed.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AMF_name)
        binary_payload += SDK_Helper.EncodeBool(reverse)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'GroupAoiByMetaField')
        
        if response.status_code == 200:
            print(f"GroupAoiByMetaField: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def HasDictionaryKey(dictionary_name: str, key: str) -> bool:
        """
        Checks if a dictionary has a specific key.

        Args:
            dictionary_name (str): The name of the dictionary.
            key (str): The key to check for.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        binary_payload += SDK_Helper.EncodeString(key)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'HasDictionaryKey')
        
        if response.status_code == 200:
            print(f"HasDictionaryKey: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def HighlightSchemeExists(highlight_scheme_name: str) -> bool:
        """
        Checks if a highlight scheme exists.

        Args:
            highlight_scheme_name (str): The name of the highlight scheme.

        Returns:
            bool: True if the highlight scheme exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'HighlightSchemeExists')
        
        if response.status_code == 200:
            print(f"HighlightSchemeExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def HttpRequest(URL: str) -> str:
        """
        Sends an HTTP request to the specified URL.

        Args:
            URL (str): The URL to send the HTTP request to.

        Returns:
            str: The response content from the HTTP request.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(URL)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'HttpRequest')
        
        if response.status_code == 200:
            print(f"HttpRequest: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ImportDocument(file_path: str, tab_delimited_measurement_names: str, measurements_only: bool) -> None:
        """
        Imports a PMM into the current document
        
        Args:
            file_path (str): The path to the PMM file to import.
            tab_delimited_measurement_names (str): The tab-delimited measurement names to import.
            measurements_only (bool): Whether to import measurements only.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_measurement_names)
        binary_payload += SDK_Helper.EncodeBool(measurements_only)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ImportDocument')
        
        if response.status_code == 200:
            print(f"ImportDocument: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ImportIntoDataTable(data_table_name: str, file_path: str, append: bool) -> None:
        """
        Imports data from a file into a data table.

        Args:
            data_table_name (str): The name of the data table to import into.
            file_path (str): The path to the file to import.
            append (bool): Whether to append the data to the existing table or replace it.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeBool(append)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ImportIntoDataTable')
        
        if response.status_code == 200:
            print(f"ImportIntoDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def InsertIntoList(list_handle: int, index: int, value: str) -> None:
        """
        Inserts a value into a list at the specified index.

        Args:
            list_handle (int): The handle of the list to insert into.
            index (int): The index at which to insert the value.
            value (str): The value to insert.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeInt(index)
        binary_payload += SDK_Helper.EncodeString(value)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'InsertIntoList')

        if response.status_code == 200:
            print(f"InsertIntoList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def InvertSelection() -> None:
        """
        Inverts the current selection.
        
        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'InvertSelection')
        
        if response.status_code == 200:
            print(f"InvertSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsAoiVisibleInWorkspace(aoi: str, measurement: str) -> bool:
        """
        Returns whether the specified AOI is visible in the workspace.
        
        Args:
            aoi (str): The name of the AOI to check.
            measurement (str): The name of the measurement to check.
            
        Returns:
            bool: True if the AOI is visible, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(aoi)
        binary_payload += SDK_Helper.EncodeString(measurement)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsAoiVisibleInWorkspace')
        
        if response.status_code == 200:
            print(f"IsAoiVisibleInWorkspace: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsContinuousMeasuringRunning() -> bool:
        """
        Checks if continuous measuring is currently running.

        Args:
            None
            
        Returns:
            bool: True if continuous measuring is running, False otherwise.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsContinuousMeasuringRunning')
        
        if response.status_code == 200:
            print(f"IsContinuousMeasuringRunning: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsFile(file_path: str) -> bool:
        """
        Checks if the specified path is a file.

        Args:
            file_path (str): The path to check.

        Returns:
            bool: True if the path is a file, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsFile')
        
        if response.status_code == 200:
            print(f"IsFile: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsFilterRegistrationIdentityMatrix(spectral_filter_name: str) -> bool:
        """
        Returns true if the filter has no registration applied when capturing.
        
        Args:
            spectral_filter_name (str): The name of the spectral filter to check.

        Returns:
            bool: True if the filter has no registration applied, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(spectral_filter_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsFilterRegistrationIdentityMatrix')
        
        if response.status_code == 200:
            print(f"IsFilterRegistrationIdentityMatrix: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsFolder(file_path: str) -> bool:
        """
        Checks if the specified path is a folder.

        Args:
            file_path (str): The path to check.

        Returns:
            bool: True if the path is a folder, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsFolder')
        
        if response.status_code == 200:
            print(f"IsFolder: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsInList(list_handle: int, value: str, start_index: int = -1, end_index: int = -1) -> bool:
        """
        Checks if the specified value is in the list.

        Args:
            list_handle (int): The handle of the list to check.
            value (str): The value to search for.
            start_index (int, optional): The index to start searching from. Defaults to -1.
            end_index (int, optional): The index to end searching at. Defaults to -1.

        Returns:
            bool: True if the value is found in the list, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(value)
        binary_payload += SDK_Helper.EncodeInt(start_index)
        binary_payload += SDK_Helper.EncodeInt(end_index)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsInList')

        if response.status_code == 200:
            print(f"IsInList: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsObjectNameLegal(name: str) -> bool:
        """
        Checks if the specified object name is legal.

        Args:
            name (str): The name of the object to check.

        Returns:
            bool: True if the object name is legal, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsObjectNameLegal')
        
        if response.status_code == 200:
            print(f"IsObjectNameLegal: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def IsPreviewRunning() -> bool:
        """
        Checks if the preview is currently running.

        Args:
            None
            
        Returns:
            bool: True if the preview is running, False otherwise.
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'IsPreviewRunning')
        
        if response.status_code == 200:
            print(f"IsPreviewRunning: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def LoadDll(file_path: str) -> int:
        """
        Loads a Plug In DLL into memory.
        If your DLL comes in 32 and 64 bit versions and you need to construct a file name based on the current system's CPU, call GetPhotometricaSetting("cpunits") which will return "32" for 32 bit systems and "64" for 64 bit systems.

        Args:
            file_path (str): The path to the DLL file to load.

        Returns:
            int: The handle of the loaded DLL, or -1 if the load failed.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'LoadDll')
        
        if response.status_code == 200:
            print(f"LoadDll: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def LoadDriverDll(file_path: str) -> None:
        """
        Loads a driver DLL into memory.

        Args:
            file_path (str): The path to the driver DLL file to load.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'LoadDriverDll')
        
        if response.status_code == 200:
            print(f"LoadDriverDll: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def LoadLayout(file_path: str) -> None:
        """
        Applies a saved workspace layout.
        
        Args:
            file_path (str): The path to the layout file to load.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'LoadLayout')
        
        if response.status_code == 200:
            print(f"LoadLayout: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def LoadPackage(file_path: str) -> None:
        """
        Loads a package file into memory.

        Args:
            file_path (str): The path to the package file to load.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'LoadPackage')
        
        if response.status_code == 200:
            print(f"LoadPackage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def LoadWorkspaceScheme(file_path: str) -> None:
        """
        Loads a workspace scheme file into the current document.

        Args:
            file_path (str): The path to the workspace scheme file to load.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'LoadWorkspaceScheme')
        
        if response.status_code == 200:
            print(f"LoadWorkspaceScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MakeChildAoi(parent_AOI_name: str, visible_in_table: bool, tab_delimited_AOI_name: str) -> None:
        """
        One or more AOI will be made into child AOI of a specified root level AOI. 
        The regions of the new children will be clipped to be within the parent AOI's region. 
        If clipping any AOI would result in no region, this method fails.
        
        Args:
            parent_AOI_name (str): The name of the parent AOI.
            visible_in_table (bool): Whether the child AOI should be visible in the table.
            tab_delimited_AOI_name (str): The tab-delimited AOI names to make children.
            
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(parent_AOI_name)
        binary_payload += SDK_Helper.EncodeBool(visible_in_table)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MakeChildAoi')
        
        if response.status_code == 200:
            print(f"MakeChildAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MakeFolder(file_path: str) -> str:
        """
        Creates a new folder at the specified file path.

        Args:
            file_path (str): The path to the folder to create.

        Returns:
            str: The path to the created folder.
        """

        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MakeFolder')
        
        if response.status_code == 200:
            print(f"MakeFolder: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MakeGridFromScatteredPoints(target_dt_name: str, input_dt_name: str, x0: int, y0: int, width: int, height: int, columns: int, rows: int, max_points: int, max_distance: int) -> str:
        """
        Creates a grid from scattered points in the specified input data table.

        Args:
            target_dt_name (str): The name of the target data table.
            input_dt_name (str): The name of the input data table.
            x0 (int): The x-coordinate of the top-left corner of the grid.
            y0 (int): The y-coordinate of the top-left corner of the grid.
            width (int): The width of the grid.
            height (int): The height of the grid.
            columns (int): The number of columns in the grid.
            rows (int): The number of rows in the grid.
            max_points (int): The maximum number of points to include in the grid.
            max_distance (int): The maximum distance between points in the grid.

        Returns:
            str: The name of the created target data table.
        """
        
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(target_dt_name)
        binary_payload += SDK_Helper.EncodeString(input_dt_name)
        binary_payload += SDK_Helper.EncodeInt(x0)
        binary_payload += SDK_Helper.EncodeInt(y0)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeInt(columns)
        binary_payload += SDK_Helper.EncodeInt(rows)
        binary_payload += SDK_Helper.EncodeInt(max_points)
        binary_payload += SDK_Helper.EncodeInt(max_distance)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MakeGridFromScatteredPoints')
        
        if response.status_code == 200:
            print(f"MakeGridFromScatteredPoints: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MakeNameSafe(text: str) -> str:
        """
        Creates a name-safe version of the input text.

        Args:
            text (str): The input text to make name-safe.

        Returns:
            str: The name-safe version of the input text.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MakeNameSafe')
        
        if response.status_code == 200:
            print(f"MakeNameSafe: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MakeNameUnique(object_type_name: str, proposed_name: str) -> str:
        """
        Creates a unique name for the specified object type by appending a numeric suffix if necessary.

        Args:
            object_type_name (str): The name of the object type.
            proposed_name (str): The proposed name for the object.

        Returns:
            str: The unique name for the object.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(proposed_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MakeNameUnique')
        
        if response.status_code == 200:
            print(f"MakeNameUnique: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MaskDrawImage(image_name: str, x: int, y: int, opacity_threshold: int) -> None:
        """
        Masks the specified image by drawing it at the given coordinates with the specified opacity threshold.

        Args:
            image_name (str): The name of the image to mask.
            x (int): The x-coordinate to draw the image.
            y (int): The y-coordinate to draw the image.
            opacity_threshold (int): The opacity threshold for masking.

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(image_name)
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        binary_payload += SDK_Helper.EncodeInt(opacity_threshold)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MaskDrawImage')
        
        if response.status_code == 200:
            print(f"MaskDrawImage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MeasurementCommit(name: str) -> None:
        """
        For use with the multi-file measurement documents. Commits a measurement to be saved to disk.
        
        Args:
            name (str): The name of the measurement to commit.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MeasurementCommit')
        
        if response.status_code == 200:
            print(f"MeasurementCommit: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MeasurementExists(name: str) -> bool:
        """
        Checks if a measurement with the specified name exists.

        Args:
            name (str): The name of the measurement to check.

        Returns:
            bool: True if the measurement exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MeasurementExists')
        
        if response.status_code == 200:
            print(f"MeasurementExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MoveAllAoi(delta_x: int, delta_y: int) -> None:
        """
        Translates all AOIs by the specified delta values.

        Args:
            delta_x (int): The change in the x-coordinate.
            delta_y (int): The change in the y-coordinate.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(delta_x)
        binary_payload += SDK_Helper.EncodeInt(delta_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MoveAllAoi')
        
        if response.status_code == 200:
            print(f"MoveAllAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def MoveAoi(delta_x: int, delta_y: int, AOI_name: str) -> None:
        """
        Moves a specific AOI (Area of Interest) by the specified delta values.

        Args:
            delta_x (int): The change in the x-coordinate.
            delta_y (int): The change in the y-coordinate.
            AOI_name (str): The name of the AOI to move.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(delta_x)
        binary_payload += SDK_Helper.EncodeInt(delta_y)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'MoveAoi')
        
        if response.status_code == 200:
            print(f"MoveAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def NewForInstrument(parameters: str) -> None:
        """
        Creates a new document for the specified instrument.
        See the user manual for the types of tab-delimited parameters.
        
        Args:
            parameters (str): The tab-delimited parameters for the new document.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(parameters)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'NewForInstrument')
        
        if response.status_code == 200:
            print(f"NewForInstrument: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def NewFromTemplate(file_path: str, save_dirty: bool) -> None:
        """
        Creates a new document from the specified template.

        Args:
            file_path (str): The path to the template file.
            save_dirty (bool): Whether to save the document if it is dirty.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeInt(save_dirty)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'NewFromTemplate')
        
        if response.status_code == 200:
            print(f"NewFromTemplate: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def NewPMM(save_dirty: bool) -> None:
        """
        Creates a new PMM document.

        Args:
            save_dirty (bool): Whether to save the document if it is dirty.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(save_dirty)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'NewPMM')
        
        if response.status_code == 200:
            print(f"NewPMM: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ObjectExists(object_type_name: str, object_name: str) -> bool:
        """
        Checks if an object exists in the specified object type.

        Args:
            object_type_name (str): The name of the object type.
            object_name (str): The name of the object.

        Returns:
            bool: True if the object exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(object_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ObjectExists')
        
        if response.status_code == 200:
            print(f"ObjectExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def OpenDocument(file_path: str, save_dirty: bool, only_measurements: bool) -> None:
        """
        Opens a document with the specified parameters.

        Args:
            file_path (str): The path to the document file.
            save_dirty (bool): Whether to save the document if it is dirty.
            only_measurements (bool): Whether to open the document in measurements-only mode.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeInt(save_dirty)
        binary_payload += SDK_Helper.EncodeBool(only_measurements)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'OpenDocument')
        
        if response.status_code == 200:
            print(f"OpenDocument: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def OpenFileInDefaultProgram(file_path: str) -> None:
        """
        Opens a file in the default program associated with its file type.

        Args:
            file_path (str): The path to the file to open.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'OpenFileInDefaultProgram')
        
        if response.status_code == 200:
            print(f"OpenFileInDefaultProgram: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def OpenPMM(file_path: str, save_dirty: bool, measurements_only: bool) -> None:
        """
        Opens a PMM (Project Management Module) document with the specified parameters.

        Args:
            file_path (str): The path to the PMM file.
            save_dirty (bool): Whether to save the document if it is dirty.
            measurements_only (bool): Whether to open the document in measurements-only mode.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeInt(save_dirty)
        binary_payload += SDK_Helper.EncodeBool(measurements_only)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'OpenPMM')
        
        if response.status_code == 200:
            print(f"OpenPMM: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def OpenSerialPort(port_name: str, bit_rate: int, data_bits: int, stop_bits: int, parity: str) -> int:
        """
        Opens a serial port with the specified parameters.

        Args:
            port_name (str): The name of the serial port.
            bit_rate (int): The bit rate for the serial communication.
            data_bits (int): The number of data bits.
            stop_bits (int): The number of stop bits.
            parity (str): The parity setting (e.g., "None", "Even", "Odd").

        Returns:
            int: The handle of the opened serial port, or -1 if failed.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(port_name)
        binary_payload += SDK_Helper.EncodeInt(bit_rate)
        binary_payload += SDK_Helper.EncodeInt(data_bits)
        binary_payload += SDK_Helper.EncodeString(stop_bits)
        binary_payload += SDK_Helper.EncodeString(parity)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'OpenSerialPort')
        
        if response.status_code == 200:
            print(f"OpenSerialPort: Success")

            # Decode the response
            result = SDK_Helper.DecodeInt(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def PolarToXY(theta: float, phi: float) -> tuple[float, float]:
        """
        Converts polar coordinates to Cartesian coordinates.

        Args:
            theta (float): The polar angle in radians.
            phi (float): The polar radius.

        Returns:
            tuple[float, float]: The Cartesian coordinates (x, y).
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(theta)
        binary_payload += SDK_Helper.EncodeDouble(phi)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'PolarToXY')
        
        if response.status_code == 200:
            print(f"PolarToXY: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeDouble(response.content[:8])
            result2 = SDK_Helper.DecodeDouble(response.content[8:])

            return (result1, result2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def PolynomialFit(x_list: list[float], y_list: list[float], degree: int) -> list[float]:
        """
        Fits a polynomial of the specified degree to the given data points.

        Args:
            x_list (list[float]): The x-coordinates of the data points.
            y_list (list[float]): The y-coordinates of the data points.
            degree (int): The degree of the polynomial to fit.

        Returns:
            list[float]: The coefficients of the fitted polynomial, ordered from highest to lowest degree.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDoubleArray(x_list)
        binary_payload += SDK_Helper.EncodeDoubleArray(y_list)
        binary_payload += SDK_Helper.EncodeInt(degree)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'PolynomialFit')
        
        if response.status_code == 200:
            print(f"PolynomialFit: Success")

            # Decode the response
            result = SDK_Helper.DecodeDoubleArray(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def PresentationExists(presentation_name: str) -> bool:
        """
        Checks if a presentation with the given name exists.

        Args:
            presentation_name (str): The name of the presentation to check.

        Returns:
            bool: True if the presentation exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'PresentationExists')
        
        if response.status_code == 200:
            print(f"PresentationExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def PrintReport(report_name: str) -> None:
        """
        Prints the specified report.

        Args:
            report_name (str): The name of the report to print.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'PrintReport')
        
        if response.status_code == 200:
            print(f"PrintReport: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ProfileExists(profile_name: str) -> bool:
        """
        Checks if a profile with the given name exists.

        Args:
            profile_name (str): The name of the profile to check.

        Returns:
            bool: True if the profile exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(profile_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ProfileExists')
        
        if response.status_code == 200:
            print(f"ProfileExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def PromoteAoi(child_AOI_name: str) -> None:
        """
        Promotes the specified AOI to the root level AOI. The new name for the child will be <parent-name>_<child-name>. 
        Name collisions with existing root level AOI are resolved by appending and incrementing a numeric suffix, as needed.

        Args:
            child_AOI_name (str): The name of the child AOI to promote.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(child_AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'PromoteAoi')
        
        if response.status_code == 200:
            print(f"PromoteAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ReadFromSerialPort(serial_port_handle: int, delimiter: str) -> str:
        """
        Reads data from a serial port.

        Args:
            serial_port_handle (int): The handle of the serial port to read from.
            delimiter (str): The delimiter to use for reading data.

        Returns:
            str: The data read from the serial port.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(serial_port_handle)
        binary_payload += SDK_Helper.EncodeString(delimiter)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ReadFromSerialPort')
        
        if response.status_code == 200:
            print(f"ReadFromSerialPort: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RedoRefinement(tab_delimited_AOI_names: str) -> None:
        """
        Re-performs the current refinement for each of the AOI specified. 
        To specify a child AOI, prefix its name with the name of its parent and a colon (i.e., "parent_AOI_name:child_AOI_name").
        
        Args:
            tab_delimited_AOI_names (str): The tab-delimited list of AOI names to re-perform the refinement on.
            
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(tab_delimited_AOI_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RedoRefinement')
        
        if response.status_code == 200:
            print(f"RedoRefinement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RefineAoi(AOI_name: str, measurement_name: str, use_min_value: bool, use_max_value: bool, min_value: float, max_value: float, erosion_amount: int, min_area: float, options_string: str) -> None:
        """
        Refines the specified AOI using the given parameters.

        Args:
            AOI_name (str): The name of the AOI to refine.
            measurement_name (str): The name of the measurement to use for refinement.
            use_min_value (bool): Whether to use the minimum value for refinement.
            use_max_value (bool): Whether to use the maximum value for refinement.
            min_value (float): The minimum value for refinement.
            max_value (float): The maximum value for refinement.
            erosion_amount (int): The amount of erosion to apply.
            min_area (float): The minimum area for refinement.
            options_string (str): Additional options for refinement.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(use_min_value)
        binary_payload += SDK_Helper.EncodeBool(use_max_value)
        binary_payload += SDK_Helper.EncodeFloat(min_value)
        binary_payload += SDK_Helper.EncodeFloat(max_value)
        binary_payload += SDK_Helper.EncodeInt(erosion_amount)
        binary_payload += SDK_Helper.EncodeInt(min_area)
        binary_payload += SDK_Helper.EncodeString(options_string)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RefineAoi')
        
        if response.status_code == 200:
            print(f"RefineAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RefinementSchemeExists(name: str) -> bool:
        """
        Checks if a refinement scheme with the given name exists.

        Args:
            name (str): The name of the refinement scheme to check.
            
        Returns:
            bool: True if the refinement scheme exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RefinementSchemeExists')
        
        if response.status_code == 200:
            print(f"RefinementSchemeExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RefineToMask(refinement_scheme_name: str, AOI_name: str, measurement_name: str) -> None:
        """
        Refines the specified AOI to the given mask using the specified refinement scheme.

        Args:
            refinement_scheme_name (str): The name of the refinement scheme to use.
            AOI_name (str): The name of the AOI to refine.
            measurement_name (str): The name of the measurement to use for refinement.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(refinement_scheme_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RefineToMask')
        
        if response.status_code == 200:
            print(f"RefineToMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RegenerateComponents(measurement_name: str) -> None:
        """
        Causes all derived components of a measurement to be regenerated from the Tristimulus components.

        Args:
            measurement_name (str): The name of the measurement to regenerate components for.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RegenerateComponents')
        
        if response.status_code == 200:
            print(f"RegenerateComponents: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveAoiFromMask(AOI_name: str) -> None:
        """
        Removes the AOI's region from the mask.

        Args:
            AOI_name (str): The name of the AOI to remove from the mask.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveAoiFromMask')
        
        if response.status_code == 200:
            print(f"RemoveAoiFromMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveColorRegionsFromGroup(color_group_name: str, color_region_name: str) -> None:
        """
        NOTE - DEPRECATED
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(color_group_name)
        binary_payload += SDK_Helper.EncodeString(color_region_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveColorRegionsFromGroup')
        
        if response.status_code == 200:
            print(f"RemoveColorRegionsFromGroup: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveColumn(data_table_name: str, column_index: int) -> None:
        """
        Removes a column from a data table.

        Args:
            data_table_name (str): The name of the data table to remove the column from.
            column_index (int): The index of the column to remove.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(column_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveColumn')
        
        if response.status_code == 200:
            print(f"RemoveColumn: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveCropping() -> None:
        """
        Removes the cropping from the document.
        
        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveCropping')
        
        if response.status_code == 200:
            print(f"RemoveCropping: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveDictionaryKey(dictionary_name: str, key: str) -> None:
        """
        Removes a key from a dictionary.

        Args:
            dictionary_name (str): The name of the dictionary to remove the key from.
            key (str): The key to remove from the dictionary.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        binary_payload += SDK_Helper.EncodeString(key)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveDictionaryKey')
        
        if response.status_code == 200:
            print(f"RemoveDictionaryKey: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def RemoveFromList(list_handle: int, index: int) -> None:
        """
        Removes an item from a list.

        Args:
            list_handle (int): The handle of the list to remove the item from.
            index (int): The index of the item to remove.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeInt(index)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveFromList')

        if response.status_code == 200:
            print(f"RemoveFromList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveRow(data_table_name: str, row_index: int) -> None:
        """
        Removes a row from a data table.

        Args:
            data_table_name (str): The name of the data table to remove the row from.
            row_index (int): The index of the row to remove.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(row_index)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveRow')
        
        if response.status_code == 200:
            print(f"RemoveRow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RemoveSelectionFromMask() -> None:
        """
        Removes the current selection from the mask.
        
        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveSelectionFromMask')
        
        if response.status_code == 200:
            print(f"RemoveSelectionFromMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def RemoveValueFromList(list_handle: int, value: str, remove_all_instances: bool = False) -> None:
        """
        Removes a value from a list.

        Args:
            list_handle (int): The handle of the list to remove the value from.
            value (str): The value to remove from the list.
            remove_all_instances (bool): Whether to remove all instances of the value or just the first one.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeString(value)
        binary_payload += SDK_Helper.EncodeBool(remove_all_instances)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RemoveValueFromList')

        if response.status_code == 200:
            print(f"RemoveValueFromList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RenameAoi(old_name: str, new_name: str) -> str:
        """
        Changes the name on an AOI.
        To specify a child AOI, you must prefix its name with its parent's name and a colon (i.e., "parent_AOI_name:child_AOI_name". Do NOT include the parent name/colon prefix in the the new child name.)

        Args:
            old_name (str): The current name of the AOI.
            new_name (str): The new name for the AOI.

        Returns:
            str: The new name of the AOI.
        """
        
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(old_name)
        binary_payload += SDK_Helper.EncodeInt(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RenameAoi')
        
        if response.status_code == 200:
            print(f"RenameAoi: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RenameObject(object_type_name: str, old_name: str, new_name: str) -> None:
        """
        Renames an object.

        Args:
            object_type_name (str): The type of the object to rename.
            old_name (str): The current name of the object.
            new_name (str): The new name for the object.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(old_name)
        binary_payload += SDK_Helper.EncodeString(new_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RenameObject')
        
        if response.status_code == 200:
            print(f"RenameObject: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ReportExists(report_name: str) -> bool:
        """
        Checks if a report exists.

        Args:
            report_name (str): The name of the report to check.

        Returns:
            bool: True if the report exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ReportExists')
        
        if response.status_code == 200:
            print(f"ReportExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ResetInstrumentMask() -> None:
        """
        Resets the instrument mask to the factory default.

        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ResetInstrumentMask')
        
        if response.status_code == 200:
            print(f"ResetInstrumentMask: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ResetWindows() -> None:
        """
        Resets the layout of your windows back to the default.

        Args:
            None
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ResetWindows')
        
        if response.status_code == 200:
            print(f"ResetWindows: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ResizeDataTable(data_table_name: str, new_row_count: int, new_column_count: int, clear_existing_data: bool) -> None:
        """
        Resizes a data table.

        Args:
            data_table_name (str): The name of the data table to resize.
            new_row_count (int): The new number of rows for the data table.
            new_column_count (int): The new number of columns for the data table.
            clear_existing_data (bool): Whether to clear existing data in the table.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(new_row_count)
        binary_payload += SDK_Helper.EncodeInt(new_column_count)
        binary_payload += SDK_Helper.EncodeBool(clear_existing_data)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ResizeDataTable')
        
        if response.status_code == 200:
            print(f"ResizeDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RevertToRestorePoint() -> None:
        """
        Reverts the document to the most recent restore point. That restore point is removed from the restore point queue.

        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RevertToRestorePoint')
        
        if response.status_code == 200:
            print(f"RevertToRestorePoint: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def ReverseList(list_handle: int) -> None:
        """
        Reverses the order of items in a list.

        Args:
            list_handle (int): The handle of the list to reverse.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ReverseList')

        if response.status_code == 200:
            print(f"ReverseList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")

    @staticmethod
    def RotateAllAoi(angle_in_degrees: float, center_x: float, center_y: float) -> None:
        """
        Rotates all areas of interest (AOIs) by a specified angle around a center point.

        Args:
            angle_in_degrees (float): The angle to rotate the AOIs.
            center_x (float): The x-coordinate of the center point.
            center_y (float): The y-coordinate of the center point.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(angle_in_degrees)
        binary_payload += SDK_Helper.EncodeInt(center_x)
        binary_payload += SDK_Helper.EncodeInt(center_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RotateAllAoi')
        
        if response.status_code == 200:
            print(f"RotateAllAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RotateAoi(angle_in_degrees: float, AOI_name: str, center_x: float, center_y: float) -> None:
        """
        Rotates a specific area of interest (AOI) by a specified angle around a center point.

        Args:
            angle_in_degrees (float): The angle to rotate the AOI.
            AOI_name (str): The name of the AOI to rotate.
            center_x (float): The x-coordinate of the center point.
            center_y (float): The y-coordinate of the center point.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(angle_in_degrees)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeInt(center_x)
        binary_payload += SDK_Helper.EncodeInt(center_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RotateAoi')
        
        if response.status_code == 200:
            print(f"RotateAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RunConsoleCommand(text: str) -> None:
        """
        Runs a console command with the specified text.

        Args:
            text (str): The text of the console command to run.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RunConsoleCommand')
        
        if response.status_code == 200:
            print(f"RunConsoleCommand: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RunNamedScript(script_name: str, parameter_values: list[str|float|int|bool|list]) -> str:
        """
        Runs a named script with the specified parameter values.

        Args:
            script_name (str): The name of the script to run.
            parameter_values (str): The parameter values to pass to the script.

        Returns:
            str: The result of the script execution.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(script_name)

        parameter_encoding = b""
        # define this array based on the formatting in the enum in c#
        parameter_type_int_array = []
        # then we need to encode the parameter_values based on what the types are that we encounter
        for i in range(len(parameter_values)):
            # is the parameter a string or a number?
            if isinstance(parameter_values[i], str):
                # if it is a string, we need to encode it as a string
                parameter_encoding += SDK_Helper.EncodeString(parameter_values[i])
                # and add the type to the array
                parameter_type_int_array.append(ParameterType.STRING.value)
            elif isinstance(parameter_values[i], int):
                # if it is an int, we need to encode it as an int
                parameter_encoding += SDK_Helper.EncodeInt(parameter_values[i])
                # and add the type to the array
                parameter_type_int_array.append(ParameterType.INT.value)
            elif isinstance(parameter_values[i], float):
                # if it is a float, we need to encode it as a float
                parameter_encoding += SDK_Helper.EncodeFloat(parameter_values[i])
                # and add the type to the array
                parameter_type_int_array.append(ParameterType.FLOAT.value)
            elif isinstance(parameter_values[i], bool):
                # if it is a bool, we need to encode it as a bool
                parameter_encoding += SDK_Helper.EncodeBool(parameter_values[i])
                # and add the type to the array
                parameter_type_int_array.append(ParameterType.BOOL.value)
            elif isinstance(parameter_values[i], list):
                # this is not supported
                raise ValueError("List type is not supported")
            else:
                # this is not supported
                raise ValueError("Unsupported type")
        
        # Encode the parameter type array as a list of ints
        binary_payload += SDK_Helper.EncodeIntArray(parameter_type_int_array)

        # Add the parameter encoding to the binary payload
        binary_payload += parameter_encoding
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RunNamedScript')
        
        if response.status_code == 200:
            print(f"RunNamedScript: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RunScript(script_text: str) -> str:
        """
        Runs a script with the specified text.

        Args:
            script_text (str): The text of the script to run.

        Returns:
            str: The result of the script execution.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(script_text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RunScript')
        
        if response.status_code == 200:
            print(f"RunScript: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RunUdwCtrlScript(UDW_name: str, UDW_control_name: str) -> None:
        """
        Runs a UDW control script with the specified names.

        Args:
            UDW_name (str): The name of the UDW to control.
            UDW_control_name (str): The name of the control to manipulate.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RunUdwCtrlScript')
        
        if response.status_code == 200:
            print(f"RunUdwCtrlScript: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def RwuToXY(real_world_x: float, real_world_y: float) -> tuple[float, float]:
        """
        Converts real-world coordinates to XY coordinates.

        Args:
            real_world_x (float): The real-world X coordinate.
            real_world_y (float): The real-world Y coordinate.

        Returns:
            tuple[float, float]: The corresponding XY coordinates.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(real_world_x)
        binary_payload += SDK_Helper.EncodeDouble(real_world_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'RwuToXY')
        
        if response.status_code == 200:
            print(f"RwuToXY: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeDouble(response.content[:8])
            result2 = SDK_Helper.DecodeDouble(response.content[8:])
            return (result1, result2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveGraphic(file_path: str) -> None:
        """
        Saves the currently visible measurement rendering as a bitmap graphic file.
        
        Args:
            file_path (str): The path to the file where the graphic will be saved.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveGraphic')
        
        if response.status_code == 200:
            print(f"SaveGraphic: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveGraphicAs() -> None:
        """
        Presents the user with the 'save as' dialog to save the currently visible measurement rendering.

        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveGraphicAs')
        
        if response.status_code == 200:
            print(f"SaveGraphicAs: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveLayout(file_path: str) -> None:
        """
        Saves a layout file to the specified file path
        
        Args:
            file_path (str): The path to the layout file to be saved.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveLayout')
        
        if response.status_code == 200:
            print(f"SaveLayout: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveObjects(object_type_name: str, object_name_list: str) -> None:
        """
        Saves the specified objects to a file.

        Args:
            object_type_name (str): The type of the objects to be saved.
            object_name_list (str): A list of object names to be saved.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(object_name_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveObjects')
        
        if response.status_code == 200:
            print(f"SaveObjects: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveObjectToFile(object_type_name: str, object_name: str, file_path: str) -> None:
        """
        Saves the specified object to a file.

        Args:
            object_type_name (str): The type of the object to be saved.
            object_name (str): The name of the object to be saved.
            file_path (str): The path to the file where the object will be saved.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(object_name)
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveObjectToFile')
        
        if response.status_code == 200:
            print(f"SaveObjectToFile: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SavePackage(target_package_name: str, object_type_name_and_object_name_list: str, tab_delimited_requirements: str, tab_delimited_options: str) -> None:
        """
        Saves the specified package to a file.
        See user manual for details on tab-delimited parameters.

        Args:
            target_package_name (str): The name of the target package.
            object_type_name_and_object_name_list (str): A list of object type names and object names.
            tab_delimited_requirements (str): Tab-delimited requirements for the package.
            tab_delimited_options (str): Tab-delimited options for the package.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(target_package_name)
        binary_payload += SDK_Helper.EncodeString(object_type_name_and_object_name_list)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_requirements)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SavePackage')
        
        if response.status_code == 200:
            print(f"SavePackage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SavePDFReport(report: str, file_path: str) -> None:
        """
        Save a report as a PDF on disk.

        Args:
            report (str): The report content to be saved.
            file_path (str): The path to the file where the report will be saved.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report)
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SavePDFReport')
        
        if response.status_code == 200:
            print(f"SavePDFReport: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SavePMM(file_path: str, use_save_as_dialog: bool) -> None:
        """
        Save a PMM file to disk.

        Args:
            file_path (str): The path to the PMM file to be saved.
            use_save_as_dialog (bool): Whether to use the "Save As" dialog.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeBool(use_save_as_dialog)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SavePMM')
        
        if response.status_code == 200:
            print(f"SavePMM: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveRestorePoint(text: str) -> None:
        """
        Save a restore point.
        
        Args:
            text (str): The text which describes the restore point in the Edit menu.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveRestorePoint')
        
        if response.status_code == 200:
            print(f"SaveRestorePoint: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveWorkspaceScheme(file_path: str) -> None:
        """
        Save a workspace scheme to disk.

        Args:
            file_path (str): The path to the workspace scheme file to be saved.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveWorkspaceScheme')
        
        if response.status_code == 200:
            print(f"SaveWorkspaceScheme: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveXLSXReport(report_name: str, file_path: str) -> None:
        """
        Save a report as an XLSX file on disk.

        Args:
            report_name (str): The name of the report to be saved.
            file_path (str): The path to the file where the report will be saved.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveXLSXReport')
        
        if response.status_code == 200:
            print(f"SaveXLSXReport: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SaveXPSReport(report_name: str, file_path: str) -> None:
        """
        Save a report as an XPS file on disk.

        Args:
            report_name (str): The name of the report to be saved.
            file_path (str): The path to the file where the report will be saved.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(report_name)
        binary_payload += SDK_Helper.EncodeString(file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SaveXPSReport')
        
        if response.status_code == 200:
            print(f"SaveXPSReport: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ScriptExists(script_name: str) -> bool:
        """
        Check if a script exists.

        Args:
            script_name (str): The name of the script to check.

        Returns:
            bool: True if the script exists, False otherwise.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(script_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ScriptExists')
        
        if response.status_code == 200:
            print(f"ScriptExists: Success")

            # Decode the response
            result = SDK_Helper.DecodeBool(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectAll() -> None:
        """
        Selects all the pixels in the measurement. If the document has a polar mask, this method selects the circular area defined by the polar mask.

        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectAll')
        
        if response.status_code == 200:
            print(f"SelectAll: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectAllAoi(include_children: bool) -> None:
        """
        Select all areas of interest (AOIs) in the measurement.

        Args:
            include_children (bool): Whether to include child AOIs in the selection.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(include_children)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectAllAoi')
        
        if response.status_code == 200:
            print(f"SelectAllAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectAoi(tab_delimited_AOI_names: str) -> None:
        """
        Select specific areas of interest (AOIs) in the measurement.

        Args:
            tab_delimited_AOI_names (str): A tab-delimited string of AOI names to select.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(tab_delimited_AOI_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectAoi')
        
        if response.status_code == 200:
            print(f"SelectAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectAoiIntersection(AOI_name_list: str) -> None:
        """
        Select the intersection of specific areas of interest (AOIs) in the measurement.

        Args:
            AOI_name_list (str): A list of AOI names to intersect.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectAoiIntersection')
        
        if response.status_code == 200:
            print(f"SelectAoiIntersection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectLine(point_list: str) -> None:
        """
        Changes the active selection to be a line (or series of line segments) specified by the points.
        All coordinates are in top-left pixel coordinate space. Use CxToX, CyToY, PolarToXY or RwuToXY to convert centered pixel, polar or linear coordinates to top-left pixel coordinate space.
        
        Args:
            point_list (str): A list of points defining the line segments.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(point_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectLine')
        
        if response.status_code == 200:
            print(f"SelectLine: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectObjects(object_type_name: str, object_name_list: str) -> None:
        """
        Select specific objects in the measurement.

        Args:
            object_type_name (str): The type of objects to select.
            object_name_list (str): A list of object names to select.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(object_name_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectObjects')
        
        if response.status_code == 200:
            print(f"SelectObjects: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectPolygon(point_list: str) -> None:
        """
        Select a polygon defined by a list of points in the measurement.
        
        Args:
            point_list (str): A list of points defining the polygon.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(point_list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectPolygon')
        
        if response.status_code == 200:
            print(f"SelectPolygon: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SelectRegion(measurement_name: str, use_min_value: bool, min_value: float, use_max_value: bool, max_value: float, include_underexposed: bool, include_overexposed: bool, include_invalid: bool, inside_existing_selection: bool) -> None:
        """
        Select a region in the measurement based on various criteria.

        Args:
            measurement_name (str): The name of the measurement.
            use_min_value (bool): Whether to use the minimum value.
            min_value (float): The minimum value.
            use_max_value (bool): Whether to use the maximum value.
            max_value (float): The maximum value.
            include_underexposed (bool): Whether to include underexposed areas.
            include_overexposed (bool): Whether to include overexposed areas.
            include_invalid (bool): Whether to include invalid areas.
            inside_existing_selection (bool): Whether to select inside the existing selection.

        Returns:
            None
        """
        
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(use_min_value)
        binary_payload += SDK_Helper.EncodeFloat(min_value)
        binary_payload += SDK_Helper.EncodeBool(use_max_value)
        binary_payload += SDK_Helper.EncodeFloat(max_value)
        binary_payload += SDK_Helper.EncodeBool(include_underexposed)
        binary_payload += SDK_Helper.EncodeBool(include_overexposed)
        binary_payload += SDK_Helper.EncodeBool(include_invalid)
        binary_payload += SDK_Helper.EncodeBool(inside_existing_selection)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SelectRegion')
        
        if response.status_code == 200:
            print(f"SelectRegion: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetActiveMeasurement(measurement_name: str) -> None:
        """
        Set the active measurement.

        Args:
            measurement_name (str): The name of the measurement.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetActiveMeasurement')
        
        if response.status_code == 200:
            print(f"SetActiveMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetActiveWhitePoint(tristimulus_X: float, tristimulus_Y: float, tristimulus_Z: float) -> None:
        """
        Sets the active white point.
        
        Args:
            tristimulus_X (float): The X tristimulus value.
            tristimulus_Y (float): The Y tristimulus value.
            tristimulus_Z (float): The Z tristimulus value.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(tristimulus_X)
        binary_payload += SDK_Helper.EncodeDouble(tristimulus_Y)
        binary_payload += SDK_Helper.EncodeDouble(tristimulus_Z)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetActiveWhitePoint')
        
        if response.status_code == 200:
            print(f"SetActiveWhitePoint: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiColumnVisible(column_number: int, boolean: bool) -> None:
        """
        Sets the visibility of a specific AOI column in the AOI Table.

        Args:
            column_number (int): The column number to modify.
            boolean (bool): The visibility state to set.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(column_number)
        binary_payload += SDK_Helper.EncodeBool(boolean)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiColumnVisible')
        
        if response.status_code == 200:
            print(f"SetAoiColumnVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiHighlightOpacity(alpha: int) -> None:
        """
        Sets the opacity of the AOI highlight.

        Args:
            alpha (int): The opacity value (0-255).
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeByte(alpha)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiHighlightOpacity')
        
        if response.status_code == 200:
            print(f"SetAoiHighlightOpacity: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiLabelProperties(show_root_AOIs: bool, show_child_AOIs: bool, font_size: int) -> None:
        """
        Sets the properties of the AOI labels.

        Args:
            show_root_AOIs (bool): Whether to show root AOIs.
            show_child_AOIs (bool): Whether to show child AOIs.
            font_size (int): The font size to use for AOI labels.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(show_root_AOIs)
        binary_payload += SDK_Helper.EncodeBool(show_child_AOIs)
        binary_payload += SDK_Helper.EncodeInt(font_size)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiLabelProperties')
        
        if response.status_code == 200:
            print(f"SetAoiLabelProperties: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiProperty(property_name: str, AOI_name: str, value: str) -> None:
        """
        Sets a specific property of an AOI.

        Args:
            property_name (str): The name of the property to set.
            AOI_name (str): The name of the AOI to modify.
            value (str): The value to set the property to.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiProperty')
        
        if response.status_code == 200:
            print(f"SetAoiProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiRegionProperties(alpha: int, r: int, g: int, b: int) -> None:
        """
        Sets the properties of the AOI region.

        Args:
            alpha (int): The opacity value (0-255).
            r (int): The red color value (0-255).
            g (int): The green color value (0-255).
            b (int): The blue color value (0-255).
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeByte(alpha)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiRegionProperties')
        
        if response.status_code == 200:
            print(f"SetAoiRegionProperties: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiSummaryProperty(property: str, name: str, value: str) -> None:
        """
        Sets a specific summary property of an AOI.

        Args:
            property (str): The name of the property to set.
            name (str): The name of the AOI to modify.
            value (str): The value to set the property to.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property)
        binary_payload += SDK_Helper.EncodeString(name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiSummaryProperty')
        
        if response.status_code == 200:
            print(f"SetAoiSummaryProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiVisibleInAoiTable(boolean: bool, tab_delimited_AOI_names: str) -> None:
        """
        Sets the visibility of AOIs in the AOI table.

        Args:
            boolean (bool): The visibility state to set.
            tab_delimited_AOI_names (str): A tab-delimited string of AOI names.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(boolean)
        binary_payload += SDK_Helper.EncodeBool(tab_delimited_AOI_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiVisibleInAoiTable')
        
        if response.status_code == 200:
            print(f"SetAoiVisibleInAoiTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAoiVisibleInWorkspace(boolean: bool, tab_delimited_AOI_names: str) -> None:
        """
        Sets the visibility of AOIs in the workspace.

        Args:
            boolean (bool): The visibility state to set.
            tab_delimited_AOI_names (str): A tab-delimited string of AOI names.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(boolean)
        binary_payload += SDK_Helper.EncodeBool(tab_delimited_AOI_names)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAoiVisibleInWorkspace')
        
        if response.status_code == 200:
            print(f"SetAoiVisibleInWorkspace: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetAutoResponse(popup_ID: int, response_code: int) -> None:
        """
        Sets the auto response for a specific popup.
        See the user manual for the list of response_codes

        Args:
            popup_ID (int): The ID of the popup to modify.
            response_code (int): The response code to set.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(popup_ID)
        binary_payload += SDK_Helper.EncodeInt(response_code)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetAutoResponse')
        
        if response.status_code == 200:
            print(f"SetAutoResponse: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCameraProperty(property_name: str, value: str) -> None:
        """
        Sets a property for the camera.
        See the user manual for the list of camera properties.

        Args:
            property_name (str): The name of the property to set.
            value (str): The value to set for the property.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCameraProperty')
        
        if response.status_code == 200:
            print(f"SetCameraProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCaptureExposureRange(capture_scheme_name: str, spectral_filter_name: str, range_min_value: float, range_max_value: float, padding_scalar: float, exposure_stepping: float) -> None:
        """
        Changes the exposure set, for a specific filter, to a custom set that can capture the specified range of values (Luminance in cd/m2 for Y) for the capture scheme specified.

        Args:
            capture_scheme_name (str): The name of the capture scheme to modify.
            spectral_filter_name (str): The name of the spectral filter to modify.
            range_min_value (float): The minimum value of the range.
            range_max_value (float): The maximum value of the range.
            padding_scalar (float): The padding scalar to apply.
            exposure_stepping (float): The exposure stepping value to apply.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        binary_payload += SDK_Helper.EncodeString(spectral_filter_name)
        binary_payload += SDK_Helper.EncodeDouble(range_min_value)
        binary_payload += SDK_Helper.EncodeDouble(range_max_value)
        binary_payload += SDK_Helper.EncodeDouble(padding_scalar)
        binary_payload += SDK_Helper.EncodeInt(exposure_stepping)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCaptureExposureRange')
        
        if response.status_code == 200:
            print(f"SetCaptureExposureRange: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCaptureProperty(property_name: str, capture_scheme_name: str, value: str) -> None:
        """
        Sets a property for a specific capture scheme.
        See user manual for a list of capture properties.

        Args:
            property_name (str): The name of the property to set.
            capture_scheme_name (str): The name of the capture scheme to modify.
            value (str): The value to set for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCaptureProperty')
        
        if response.status_code == 200:
            print(f"SetCaptureProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCaptureSettings(property_name: str, value: str) -> None:
        """
        Changes a capture setting. These apply to the whole document, unlike capture properties which apply to a single capture scheme.
        See user manual for a list of all capture properties

        Args:
            property_name (str): The name of the property to set.
            value (str): The value to set for the property.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCaptureSettings')
        
        if response.status_code == 200:
            print(f"SetCaptureSettings: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCaptureTestPattern(pattern: str) -> None:
        """
        Sets the pattern to use for the capture test window.
        
        Args:
            pattern (str): The pattern to set for the capture test window.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(pattern)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCaptureTestPattern')
        
        if response.status_code == 200:
            print(f"SetCaptureTestPattern: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCell(data_table_name: str, row: int, column: int, value: str) -> None:
        """
        Sets the value of a specific cell in a data table.

        Args:
            data_table_name (str): The name of the data table.
            row (int): The row index of the cell.
            column (int): The column index of the cell.
            value (str): The value to set for the cell.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeInt(row)
        binary_payload += SDK_Helper.EncodeInt(column)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCell')
        
        if response.status_code == 200:
            print(f"SetCell: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetComputationProperty(property_name: str, computation_name: str, value: str) -> None:
        """
        Changes a property for a computation scheme.
        See user manual for a list of property names
        
        Args:
            property_name (str): The name of the property to set.
            computation_name (str): The name of the computation scheme.
            value (str): The value to set for the property.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(computation_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetComputationProperty')
        
        if response.status_code == 200:
            print(f"SetComputationProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetContinuousMeasuringOverlay(image_file_path: str) -> None:
        """
        Sets the overlay image for continuous measuring.

        Args:
            image_file_path (str): The file path of the image to set as the overlay.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(image_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetContinuousMeasuringOverlay')
        
        if response.status_code == 200:
            print(f"SetContinuousMeasuringOverlay: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetContinuousMeasuringProperty(property_name: str, value: str) -> None:
        """
        Sets a continuous measuring property.

        Args:
            property_name (str): The name of the property to set.
            value (str): The value to set for the property.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetContinuousMeasuringProperty')
        
        if response.status_code == 200:
            print(f"SetContinuousMeasuringProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCoordinateShift(delta_x: float, delta_y: float) -> None:
        """
        The origin of the coordinate system may be simply translated using an X and/or Y delta. 
        It is important to set the Linear Dimensions before setting the coordinate shift.
        
        Args:
            delta_x (float): The delta X value to translate the coordinate system.
            delta_y (float): The delta Y value to translate the coordinate system.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(delta_x)
        binary_payload += SDK_Helper.EncodeFloat(delta_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCoordinateShift')
        
        if response.status_code == 200:
            print(f"SetCoordinateShift: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCustomFilterRegistration(
        spectral_filter_name: str,
        rotation_degrees: float,
        magnification_scalar: float,
        translation_x: float,
        translation_y: float
    ) -> None:
        """
        This method sets the custom filter registration parameters for the current instrument. 

        Args:
            spectral_filter_name (str): The name of the spectral filter.
            rotation_degrees (float): The rotation angle in degrees.
            magnification_scalar (float): The magnification scalar.
            translation_x (float): The translation in the X direction.
            translation_y (float): The translation in the Y direction.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(spectral_filter_name)
        binary_payload += SDK_Helper.EncodeDouble(rotation_degrees)
        binary_payload += SDK_Helper.EncodeDouble(magnification_scalar)
        binary_payload += SDK_Helper.EncodeDouble(translation_x)
        binary_payload += SDK_Helper.EncodeDouble(translation_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCustomFilterRegistration')
        
        if response.status_code == 200:
            print(f"SetCustomFilterRegistration: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCustomFilterRegistrationFromDataTable(data_table_name: str) -> None:
        """
        This method sets the custom filter registration from data, in a data table created, using AddCustomFilterRegistrationDataTable. 
        The active registration will be set to this new registration.
        
        Args:
            data_table_name (str): The name of the data table to use for the custom filter registration.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCustomFilterRegistrationFromDataTable')
        
        if response.status_code == 200:
            print(f"SetCustomFilterRegistrationFromDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCustomFilterRegistrationFromDutMeasurement(
        measurement_name: str,
        threshold_percentage: float,
        threshold_Xblue: float,
        threshold_Xred: float,
        threshold_Z: float,
        Y_behavior: int,
        custom_name: str
    ) -> None:
        """
        This method creates a custom filter registration based on a measurement of a Device Under Test (DUT) and threshold parameters which are used to identify the DUT within the measurement. 
        The resulting registration will have a transformation matrix for each component. 
        The active registration will be set to this new registration.

        Args:
            measurement_name (str): The name of the DUT measurement.
            threshold_percentage (float): The threshold percentage.
            threshold_Xblue (float): The threshold for the X blue channel.
            threshold_Xred (float): The threshold for the X red channel.
            threshold_Z (float): The threshold for the Z channel.
            Y_behavior (int): The Y behavior setting.
            custom_name (str): The custom name for the registration.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeDouble(threshold_percentage)
        binary_payload += SDK_Helper.EncodeDouble(threshold_Xblue)
        binary_payload += SDK_Helper.EncodeDouble(threshold_Xred)
        binary_payload += SDK_Helper.EncodeDouble(threshold_Z)
        binary_payload += SDK_Helper.EncodeInt(Y_behavior)
        binary_payload += SDK_Helper.EncodeString(custom_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCustomFilterRegistrationFromDutMeasurement')
        
        if response.status_code == 200:
            print(f"SetCustomFilterRegistrationFromDutMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetCustomWindow(user_docker_idx: int, user_window: int, caption: str) -> None:
        """
        Use this function to embed a COM/.NET user-defined window into the GUI of Photometrica®. 
        The (host) window is always made visible. To detach a window, pass the index of the window, and a value of null (zero) for HWND.

        Args:
            user_docker_idx (int): User defined host window index, zero-based, or -1. An index of -1 is equivalent to choosing the next free index.
            user_window (int): Handle to the user supplied window.
            caption (str): Caption to use for the host docking window.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(user_docker_idx)
        binary_payload += SDK_Helper.EncodeInt(user_window)
        binary_payload += SDK_Helper.EncodeString(caption)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetCustomWindow')
        
        if response.status_code == 200:
            print(f"SetCustomWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetDataTableProperty(table_name: str, property_name: str, value: str) -> None:
        """
        Changes a property for a data table
        
        Args:
            table_name (str): The name of the data table.
            property_name (str): The name of the property to change.
            value (str): The new value for the property.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(table_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetDataTableProperty')
        
        if response.status_code == 200:
            print(f"SetDataTableProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetDeviceParameter(device: str, param_name: str, value: str) -> None:
        """
        Sets a parameter for a device.

        Args:
            device (str): The name of the device.
            param_name (str): The name of the parameter to set.
            value (str): The value to set for the parameter.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(device)
        binary_payload += SDK_Helper.EncodeString(param_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetDeviceParameter')
        
        if response.status_code == 200:
            print(f"SetDeviceParameter: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetDictionaryValue(dictionary_name: str, key: str, value: str) -> None:
        """
        Sets a value in a dictionary.

        Args:
            dictionary_name (str): The name of the dictionary.
            key (str): The key for the value to set.
            value (str): The value to set.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(dictionary_name)
        binary_payload += SDK_Helper.EncodeString(key)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetDictionaryValue')
        
        if response.status_code == 200:
            print(f"SetDictionaryValue: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetDocumentProperty(document_property_name: str, value: str) -> None:
        """
        Sets a property for a document.
        see user manual for a list of all properties
        
        Args:
            document_property_name (str): The name of the document property.
            value (str): The value to set for the document property.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(document_property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetDocumentProperty')
        
        if response.status_code == 200:
            print(f"SetDocumentProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetDocumentVariable(document_variable_name: str, value: str) -> None:
        """
        Sets the value of a document (@@) variable. If the variable doesn't exist yet, it will be created.

        Args:
            document_variable_name (str): The name of the document variable.
            value (str): The value to set for the document variable.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(document_variable_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetDocumentVariable')
        
        if response.status_code == 200:
            print(f"SetDocumentVariable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetEvaluationProperty(property_name: str, evaluation_name: str, value: str) -> None:
        """
        Sets a property for an evaluation.

        Args:
            property_name (str): The name of the property to set.
            evaluation_name (str): The name of the evaluation.
            value (str): The value to set for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(evaluation_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetEvaluationProperty')
        
        if response.status_code == 200:
            print(f"SetEvaluationProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetEventScript(UDW_name: str, event_name: str, script_text: str) -> None:
        """
        Sets the event script associated with a UDW.
        
        Args:
            UDW_name (str): The name of the UDW.
            event_name (str): The name of the event.
            script_text (str): The script text to set for the event.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(event_name)
        binary_payload += SDK_Helper.EncodeString(script_text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetEventScript')
        
        if response.status_code == 200:
            print(f"SetEventScript: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetExportTargetExistsAction(action_name: str) -> None:
        """
        Changes how Photometrica® handles exporting to a Comma Separated Value (CSV) file which already exists.
        See the list of actions in the user manual

        Args:
            action_name (str): The name of the action to set.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(action_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetExportTargetExistsAction')
        
        if response.status_code == 200:
            print(f"SetExportTargetExistsAction: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetFilterProperty(property_name: str, spatial_filter_name: str, value: str) -> None:
        """
        Sets a property for a spatial filter.

        Args:
            property_name (str): The name of the property to set.
            spatial_filter_name (str): The name of the spatial filter.
            value (str): The value to set for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(spatial_filter_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetFilterProperty')
        
        if response.status_code == 200:
            print(f"SetFilterProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetFocusIndicatorProperty() -> None:
        """
        Sets the focus indicator property.
        
        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetFocusIndicatorProperty')
        
        if response.status_code == 200:
            print(f"SetFocusIndicatorProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetGlobal(global_variable_name: str, value: str) -> None:
        """
        Sets the value of a global variable

        Args:
            global_variable_name (str): The name of the global variable to set.
            value (str): The value to set for the global variable.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(global_variable_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetGlobal')
        
        if response.status_code == 200:
            print(f"SetGlobal: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetGridVisible(boolean: bool) -> None:
        """
        Changes the pixel grid's visibility.
        The pixel grid is the outline that is drawn around individual pixels (samples) at high zoom levels. 
        This is separate from the grid overlay which is user-defined and appears at all zoom levels.
        
        Args:
            boolean (bool): The visibility state of the pixel grid.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(boolean)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetGridVisible')
        
        if response.status_code == 200:
            print(f"SetGridVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetHighlightRule(
        highlight_scheme_name: str,
        rule_number: int,
        rule_name: str,
        formula: str,
        r: int,
        g: int,
        b: int
    ) -> None:
        """
        Adds or changes a highlight rule within an existing AOI highlight scheme.

        Args:
            highlight_scheme_name (str): The name of the highlight scheme.
            rule_number (int): The rule number to set.
            rule_name (str): The name of the rule.
            formula (str): The formula for the rule.
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        binary_payload += SDK_Helper.EncodeInt(rule_number)
        binary_payload += SDK_Helper.EncodeString(rule_name)
        binary_payload += SDK_Helper.EncodeString(formula)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetHighlightRule')
        
        if response.status_code == 200:
            print(f"SetHighlightRule: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetHighlightRuleProperty(property_name: str, highlight_scheme_name: str, rule_number: int, value: str) -> None:
        """
        Sets a property of a highlight rule within an existing AOI highlight scheme.

        Args:
            property_name (str): The name of the property to set.
            highlight_scheme_name (str): The name of the highlight scheme.
            rule_number (int): The rule number to modify.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(highlight_scheme_name)
        binary_payload += SDK_Helper.EncodeInt(rule_number)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetHighlightRuleProperty')
        
        if response.status_code == 200:
            print(f"SetHighlightRuleProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetHistogramProperty(property_name: str, value: float) -> None:
        """
        Sets a property of the histogram.

        Args:
            property_name (str): The name of the property to set.
            value (float): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeFloat(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetHistogramProperty')
        
        if response.status_code == 200:
            print(f"SetHistogramProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetIsolinesVisible(boolean: bool) -> None:
        """
        Sets the visibility of the isolines.

        Args:
            boolean (bool): The visibility state of the isolines.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(boolean)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetIsolinesVisible')
        
        if response.status_code == 200:
            print(f"SetIsolinesVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")
        
    @staticmethod
    def SetListValue(list_handle: int, index: int, value: str) -> None:
        """
        Sets the value of a specific item in a list.

        Args:
            list_handle (int): The handle of the list.
            index (int): The index of the item to modify.
            value (str): The new value for the item.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list_handle)
        binary_payload += SDK_Helper.EncodeInt(index)
        binary_payload += SDK_Helper.EncodeString(value)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetListValue')

        if (response.status_code == 200):
            print(f"SetListValue: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetMeasurementLogData(
        measurement_name: str,
        section_name: str,
        subsection_name: str,
        item_name: str,
        data: str,
        data_type_name: str
    ) -> None:
        """
        Sets the log data for a specific measurement.

        Args:
            measurement_name (str): The name of the measurement.
            section_name (str): The name of the section.
            subsection_name (str): The name of the subsection.
            item_name (str): The name of the item.
            data (str): The log data.
            data_type_name (str): The data type name.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(section_name)
        binary_payload += SDK_Helper.EncodeString(subsection_name)
        binary_payload += SDK_Helper.EncodeString(item_name)
        binary_payload += SDK_Helper.EncodeString(data)
        binary_payload += SDK_Helper.EncodeString(data_type_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetMeasurementLogData')
        
        if response.status_code == 200:
            print(f"SetMeasurementLogData: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetMeasurementProperty(measurement_name: str, property_name: str, value: str) -> None:
        """
        Sets a property of the measurement.

        Args:
            measurement_name (str): The name of the measurement.
            property_name (str): The name of the property to set.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetMeasurementProperty')
        
        if response.status_code == 200:
            print(f"SetMeasurementProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetMeasurementValue(measurement_name: str, value: float, restrict_to_selection: bool) -> None:
        """
        Sets the value of a specific measurement.

        Args:
            measurement_name (str): The name of the measurement.
            value (float): The new value for the measurement.
            restrict_to_selection (bool): Whether to restrict the measurement to the current selection.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeFloat(value)
        binary_payload += SDK_Helper.EncodeBool(restrict_to_selection)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetMeasurementValue')
        
        if response.status_code == 200:
            print(f"SetMeasurementValue: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetMeasurementValueInAoi(measurement_name: str, value: float, AOI_name: str) -> None:
        """
        Sets the value of a specific measurement within a given Area of Interest (AOI).

        Args:
            measurement_name (str): The name of the measurement.
            value (float): The new value for the measurement.
            AOI_name (str): The name of the Area of Interest.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeFloat(value)
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetMeasurementValueInAoi')
        
        if response.status_code == 200:
            print(f"SetMeasurementValueInAoi: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetMetaInfo(meta_info_name: str, meta_info_value: str) -> None:
        """
        Sets the value of a variable in the document.
        
        Args:
            meta_info_name (str): The name of the meta information variable.
            meta_info_value (str): The value to set for the meta information variable.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(meta_info_name)
        binary_payload += SDK_Helper.EncodeString(meta_info_value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetMetaInfo')
        
        if response.status_code == 200:
            print(f"SetMetaInfo: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetMmfProperty(property_name: str, MMF_name: str, property_value: str) -> None:
        """
        Changes a property of a measurement meta field.

        Args:
            property_name (str): The name of the property to set.
            MMF_name (str): The name of the measurement meta field.
            property_value (str): The new value for the property.
            
        Returns:    
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(MMF_name)
        binary_payload += SDK_Helper.EncodeString(property_value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetMmfProperty')
        
        if response.status_code == 200:
            print(f"SetMmfProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetNextCaptureMeasurementData(wpmd: str) -> None:
        """
        Sets the next capture measurement data.
        This is primarily used for debugging purposes.

        Args:
            wpmd (str): The next capture measurement data.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(wpmd)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetNextCaptureMeasurementData')
        
        if response.status_code == 200:
            print(f"SetNextCaptureMeasurementData: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetObjectProperty(object_type_name: str, property_name: str, object_name: str, value: str) -> None:
        """
        Sets a property of a specific object.
        See user manual for a list of all properties for each type

        Args:
            object_type_name (str): The type of the object.
            property_name (str): The name of the property to set.
            object_name (str): The name of the object.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(object_type_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(object_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetObjectProperty')
        
        if response.status_code == 200:
            print(f"SetObjectProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetOverlayGrid(
        spacing_x: int,
        spacing_y: int,
        center: bool,
        line_style: str,
        opacity: int,
        r: int,
        g: int,
        b: int
    ) -> None:
        """
        Sets the overlay grid properties.

        Args:
            spacing_x (int): The spacing between grid lines in the X direction.
            spacing_y (int): The spacing between grid lines in the Y direction.
            center (bool): Whether to center the grid.
            line_style (str): The style of the grid lines.
            opacity (int): The opacity of the grid lines (0-255).
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(spacing_x)
        binary_payload += SDK_Helper.EncodeInt(spacing_y)
        binary_payload += SDK_Helper.EncodeBool(center)
        binary_payload += SDK_Helper.EncodeString(line_style)
        binary_payload += SDK_Helper.EncodeByte(opacity)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetOverlayGrid')
        
        if response.status_code == 200:
            print(f"SetOverlayGrid: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetOverlayOff() -> None:
        """
        Toggles the grid overlay.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetOverlayOff')
        
        if response.status_code == 200:
            print(f"SetOverlayOff: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetOverlayPolar(
        ring_spacing: int,
        spoke_spacing: int,
        line_style_name: str,
        alpha: int,
        r: int,
        g: int,
        b: int
    ) -> None:
        """
        Sets the overlay polar properties.

        Args:
            ring_spacing (int): The spacing between rings.
            spoke_spacing (int): The spacing between spokes.
            line_style_name (str): The name of the line style.
            alpha (int): The alpha transparency (0-255).
            r (int): The red color component (0-255).
            g (int): The green color component (0-255).
            b (int): The blue color component (0-255).

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(ring_spacing)
        binary_payload += SDK_Helper.EncodeInt(spoke_spacing)
        binary_payload += SDK_Helper.EncodeString(line_style_name)
        binary_payload += SDK_Helper.EncodeByte(alpha)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetOverlayPolar')
        
        if response.status_code == 200:
            print(f"SetOverlayPolar: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetPhotometricaSetting(setting_name: str, value: str) -> None:
        """
        Sets a photometrica setting.
        See the user manual for a complete list of settings.

        Args:
            setting_name (str): The name of the setting to change.
            value (str): The new value for the setting.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(setting_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetPhotometricaSetting')
        
        if response.status_code == 200:
            print(f"SetPhotometricaSetting: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetPointOfView(delta_x: float, delta_y: float, delta_z: float, pov_direction: str) -> None:
        """
        When using a polar coordinate system, the position of the instrument may be virtually shifted in real world coordinates, with respect to the perceived polar coordinate space. 
        It is important to set the Linear Dimensions before adjusting the Point of View.
        
        Args:
            delta_x (float): The change in the x-coordinate.
            delta_y (float): The change in the y-coordinate.
            delta_z (float): The change in the z-coordinate.
            pov_direction (str): The direction of the point of view.
            
        Returns:
            None

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(delta_x)
        binary_payload += SDK_Helper.EncodeFloat(delta_y)
        binary_payload += SDK_Helper.EncodeFloat(delta_z)
        binary_payload += SDK_Helper.EncodeString(pov_direction)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetPointOfView')
        
        if response.status_code == 200:
            print(f"SetPointOfView: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetPresentationProperty(property_name: str, presentation_name: str, value: str) -> None:
        """
        Sets a presentation property.

        Args:
            property_name (str): The name of the property to change.
            presentation_name (str): The name of the presentation.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetPresentationProperty')
        
        if response.status_code == 200:
            print(f"SetPresentationProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetPreviewOverlay(image_file_path: str) -> None:
        """
        Sets the preview overlay image.

        Args:
            image_file_path (str): The file path of the image to use as the overlay.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(image_file_path)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetPreviewOverlay')
        
        if response.status_code == 200:
            print(f"SetPreviewOverlay: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetPreviewProperty(property_name: str, value: str) -> None:
        """
        Sets a preview property.

        Args:
            property_name (str): The name of the property to change.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetPreviewProperty')
        
        if response.status_code == 200:
            print(f"SetPreviewProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetProfileGraphProperty(property_name: str, value: str) -> None:
        """
        Sets a profile graph property.

        Args:
            property_name (str): The name of the property to change.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetProfileGraphProperty')
        
        if response.status_code == 200:
            print(f"SetProfileGraphProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetRealWorldUnits(pixel_distance: int, real_world_distance: float, unit: str) -> None:
        """
        Sets the real-world units for a given pixel distance.

        Args:
            pixel_distance (int): The pixel distance to convert.
            real_world_distance (float): The corresponding real-world distance.
            unit (str): The unit of measurement (e.g., "mm", "cm", "m").

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(pixel_distance)
        binary_payload += SDK_Helper.EncodeFloat(real_world_distance)
        binary_payload += SDK_Helper.EncodeString(unit)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetRealWorldUnits')
        
        if response.status_code == 200:
            print(f"SetRealWorldUnits: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetReferenceSlope(slope_value: float) -> None:
        """
        Sets the reference slope.

        Args:
            slope_value (float): The value of the slope to set.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(slope_value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetReferenceSlope')
        
        if response.status_code == 200:
            print(f"SetReferenceSlope: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetReferenceSlopeFromSelection() -> None:
        """
        Sets the reference slope from the current selection.

        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetReferenceSlopeFromSelection')
        
        if response.status_code == 200:
            print(f"SetReferenceSlopeFromSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetRefinementProperty(property_name: str, refinement_scheme_name: str, value: str) -> None:
        """
        Sets a refinement property.

        Args:
            property_name (str): The name of the property to change.
            refinement_scheme_name (str): The name of the refinement scheme.
            value (str): The new value for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(refinement_scheme_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetRefinementProperty')
        
        if response.status_code == 200:
            print(f"SetRefinementProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetRulerVisible(boolean: bool) -> None:
        """
        Sets the visibility of the ruler.

        Args:
            boolean (bool): The visibility state of the ruler.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(boolean)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetRulerVisible')
        
        if response.status_code == 200:
            print(f"SetRulerVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetSelection(shape_name: str, x: int, y: int, width: int, height: int) -> None:
        """
        Sets the selection rectangle.

        Args:
            shape_name (str): The name of the shape to select.
            x (int): The x-coordinate of the selection rectangle.
            y (int): The y-coordinate of the selection rectangle.
            width (int): The width of the selection rectangle.
            height (int): The height of the selection rectangle.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(shape_name)
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetSelection')
        
        if response.status_code == 200:
            print(f"SetSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetSelectionProperties(alpha: int, r: int, g: int, b: int) -> None:
        """
        Sets the properties of the selection.

        Args:
            alpha (int): The alpha value of the selection.
            r (int): The red component of the selection color.
            g (int): The green component of the selection color.
            b (int): The blue component of the selection color.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeByte(alpha)
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetSelectionProperties')
        
        if response.status_code == 200:
            print(f"SetSelectionProperties: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetSurfacePlotProperties(detail_level: int, max_contours: int) -> None:
        """
        Sets the properties of the surface plot.

        Args:
            detail_level (int): The detail level of the surface plot.
            max_contours (int): The maximum number of contours to display.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(detail_level)
        binary_payload += SDK_Helper.EncodeInt(max_contours)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetSurfacePlotProperties')
        
        if response.status_code == 200:
            print(f"SetSurfacePlotProperties: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetTableFailColor(r: int, g: int, b: int) -> None:
        """
        Sets the color to use for table cells that are considered to have a fail value.

        Args:
            r (int): The red component of the fail color.
            g (int): The green component of the fail color.
            b (int): The blue component of the fail color.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeByte(r)
        binary_payload += SDK_Helper.EncodeByte(g)
        binary_payload += SDK_Helper.EncodeByte(b)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetTableFailColor')
        
        if response.status_code == 200:
            print(f"SetTableFailColor: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetTableNumericFormat(number_of_significant_digits: int) -> None:
        """
        Sets the numeric format for table cells.

        Args:
            number_of_significant_digits (int): The number of significant digits to display.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(number_of_significant_digits)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetTableNumericFormat')
        
        if response.status_code == 200:
            print(f"SetTableNumericFormat: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetThermometerVisible(boolean: bool) -> None:
        """
        Toggles the visibility of the presentation thermometer.

        Args:
            boolean (bool): True to show the thermometer, False to hide it.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(boolean)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetThermometerVisible')
        
        if response.status_code == 200:
            print(f"SetThermometerVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")


    @staticmethod
    def SetUdwCtrlImage(UDW_name: str, UDW_control_name: str, image_name: str, width: int, height: int) -> None:
        """
        Sets the image for a control within a user-defined window.

        It is recommended that images used in UDWs be stored in memory - as part of the package or template or PMM. See Images Window. 
        Once an image is in memory, it can be referenced with a colon, followed by the name, without any file extension. 
        For example, if you have previously loaded "bird.png" into memory, it can then be referenced as ":bird".
        
        Args:
            UDW_name (str): The name of the user-defined window.
            UDW_control_name (str): The name of the control within the UDW.
            image_name (str): The name of the image to set.
            width (int): The width of the image.
            height (int): The height of the image.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(image_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetUdwCtrlImage')
        
        if response.status_code == 200:
            print(f"SetUdwCtrlImage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetUdwCtrlList(UDW_name: str, UDW_control_name: str, list: str) -> None:
        """
        Sets the list of items for a list control element.

        Args:
            UDW_name (str): The name of the user-defined window.
            UDW_control_name (str): The name of the control within the UDW.
            list (str): The list of items to set.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(list)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetUdwCtrlList')
        
        if response.status_code == 200:
            print(f"SetUdwCtrlList: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetUdwCtrlProperty(UDW_name: str, UDW_control_name: str, property_name: str, value: str) -> None:
        """
        Sets a property for a control within a user-defined window.
        See the user manual for a list of properties for each type of control.

        Args:
            UDW_name (str): The name of the user-defined window.
            UDW_control_name (str): The name of the control within the UDW.
            property_name (str): The name of the property to set.
            value (str): The value to set for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetUdwCtrlProperty')
        
        if response.status_code == 200:
            print(f"SetUdwCtrlProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetUdwCtrlText(UDW_name: str, UDW_control_name: str, text: str) -> None:
        """
        Sets the text for a control within a user-defined window.

        Args:
            UDW_name (str): The name of the user-defined window.
            UDW_control_name (str): The name of the control within the UDW.
            text (str): The text to set for the control.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetUdwCtrlText')
        
        if response.status_code == 200:
            print(f"SetUdwCtrlText: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetUdwGraphCtrlData(
        UDW_name: str,
        UDW_control_name: str,
        data_table_name: str,
        column_data: str,
        row_data: str,
        tab_delimited_params: str
    ) -> None:
        """
        Sets the data for a graph control within a user-defined window.

        Args:
            UDW_name (str): The name of the user-defined window.
            UDW_control_name (str): The name of the control within the UDW.
            data_table_name (str): The name of the data table.
            column_data (str): The column data to set.
            row_data (str): The row data to set.
            tab_delimited_params (str): Additional parameters for the request.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(column_data)
        binary_payload += SDK_Helper.EncodeString(row_data)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_params)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetUdwGraphCtrlData')
        
        if response.status_code == 200:
            print(f"SetUdwGraphCtrlData: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetUdwTableCtrlData(
        UDW_name: str,
        UDW_control_name: str,
        data_table_name: str,
        column_data: str,
        row_data: str,
        tab_delimited_extra_parameters: str
    ) -> None:
        """
        Sets the data for a table control within a user-defined window.

        Args:
            UDW_name (str): The name of the user-defined window.
            UDW_control_name (str): The name of the control within the UDW.
            data_table_name (str): The name of the data table.
            column_data (str): The column data to set.
            row_data (str): The row data to set.
            tab_delimited_extra_parameters (str): Additional parameters for the request.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeString(UDW_control_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeString(column_data)
        binary_payload += SDK_Helper.EncodeString(row_data)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_extra_parameters)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetUdwTableCtrlData')
        
        if response.status_code == 200:
            print(f"SetUdwTableCtrlData: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetWindowProperty(window_name: str, property_name: str, value: str) -> None:
        """
        Sets a property for a window.
        See the user manual for a list of all properties
        
        Args:
            window_name (str): The name of the window.
            property_name (str): The name of the property to set.
            value (str): The value to set for the property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(window_name)
        binary_payload += SDK_Helper.EncodeString(property_name)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetWindowProperty')
        
        if response.status_code == 200:
            print(f"SetWindowProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetWindowVisible(window_name: str, boolean: bool, position_name: str, size: int, sibling_window_name: str) -> None:
        """
        Toggles the visibility of a specified window
        
        Args:
            window_name (str): The name of the window.
            boolean (bool): The visibility state to set.
            position_name (str): The name of the position to set.
            size (int): The size to set.
            sibling_window_name (str): The name of the sibling window.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(window_name)
        binary_payload += SDK_Helper.EncodeBool(boolean)
        binary_payload += SDK_Helper.EncodeString(position_name)
        binary_payload += SDK_Helper.EncodeInt(size)
        binary_payload += SDK_Helper.EncodeString(sibling_window_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetWindowVisible')
        
        if response.status_code == 200:
            print(f"SetWindowVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetWorkingFolder(file_path: str, create_if_missing: bool) -> None:
        """
        Sets the working folder for the application.

        Args:
            file_path (str): The path to the working folder.
            create_if_missing (bool): Whether to create the folder if it doesn't exist.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(file_path)
        binary_payload += SDK_Helper.EncodeBool(create_if_missing)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetWorkingFolder')
        
        if response.status_code == 200:
            print(f"SetWorkingFolder: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetWorkspaceProperty(workspace_property: str, value: str) -> None:
        """
        Sets a property for the workspace.
        See the user manual for all properties

        Args:
            workspace_property (str): The name of the workspace property to set.
            value (str): The value to set for the workspace property.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(workspace_property)
        binary_payload += SDK_Helper.EncodeString(value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetWorkspaceProperty')
        
        if response.status_code == 200:
            print(f"SetWorkspaceProperty: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetWorkspaceTooltipVisible(boolean: bool) -> None:
        """
        Toggles the visibility of the tooltip in the workspace.
        
        Args:
            boolean (bool): The visibility state to set.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(boolean)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetWorkspaceTooltipVisible')
        
        if response.status_code == 200:
            print(f"SetWorkspaceTooltipVisible: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SetZoom(zoom_type_name: str, param: int) -> None:
        """
        Sets the zoom amount in the workspace
        
        Args:
            zoom_type_name (str): The type of zoom to set (e.g., "in", "out").
            param (int): The zoom level to set.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(zoom_type_name)
        binary_payload += SDK_Helper.EncodeInt(param)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SetZoom')
        
        if response.status_code == 200:
            print(f"SetZoom: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowAboutWindow() -> None:
        """
        Shows the 'about' popup window in the GUI
        
        Args:
            None
        
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowAboutWindow')
        
        if response.status_code == 200:
            print(f"ShowAboutWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowAoiCreateWindow(delete_existing_AOIs: bool, editor_style: str, AOI_name_prefix: str) -> None:
        """
        Shows the 'create AOI' popup window in the GUI

        Args:
            delete_existing_AOIs (bool): Whether to delete existing AOIs.
            editor_style (str): The style of the editor to use.
            AOI_name_prefix (str): The prefix for the AOI name.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(delete_existing_AOIs)
        binary_payload += SDK_Helper.EncodeString(editor_style)
        binary_payload += SDK_Helper.EncodeString(AOI_name_prefix)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowAoiCreateWindow')
        
        if response.status_code == 200:
            print(f"ShowAoiCreateWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowAoiPropertiesWindow(AOI_name: str) -> None:
        """
        Shows the 'AOI properties' popup window in the GUI

        Args:
            AOI_name (str): The name of the AOI to show properties for.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(AOI_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowAoiPropertiesWindow')
        
        if response.status_code == 200:
            print(f"ShowAoiPropertiesWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowCaptureEditorWindow(capture_scheme_name: str, tab_delimited_options: str) -> None:
        """
        Shows the 'capture editor' popup window in the GUI
        see the user manual for the 

        Args:
            capture_scheme_name (str): The name of the capture scheme to edit.
            tab_delimited_options (str): The tab-delimited options for the capture scheme.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        binary_payload += SDK_Helper.EncodeString(tab_delimited_options)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowCaptureEditorWindow')
        
        if response.status_code == 200:
            print(f"ShowCaptureEditorWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowCustomMessage(popup_ID: int, text: str) -> None:
        """
        Shows a custom message popup window in the GUI
        
        Args:
            popup_ID (int): The ID of the popup window.
            text (str): The text to display in the popup window.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(popup_ID)
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowCustomMessage')
        
        if response.status_code == 200:
            print(f"ShowCustomMessage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowHelp(topic: str, parameter: str) -> None:
        """
        Show the user manual popup
        
        Args:
            topic (str): The topic to show help for.
            parameter (str): The parameter to show help for.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(topic)
        binary_payload += SDK_Helper.EncodeString(parameter)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowHelp')
        
        if response.status_code == 200:
            print(f"ShowHelp: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowMeasurementEditorWindow(measurement_name: str) -> None:
        """
        Shows the 'measurement editor' popup window in the GUI

        Args:
            measurement_name (str): The name of the measurement to edit.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowMeasurementEditorWindow')
        
        if response.status_code == 200:
            print(f"ShowMeasurementEditorWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowMeasurementRegistrationWindow(measurement_name: str) -> None:
        """
        Shows the 'measurement registration' popup window in the GUI

        Args:
            measurement_name (str): The name of the measurement to register.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowMeasurementRegistrationWindow')
        
        if response.status_code == 200:
            print(f"ShowMeasurementRegistrationWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowMessage(text: str) -> None:
        """
        Shows a message popup window in the GUI

        Args:
            text (str): The text to display in the popup window.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowMessage')
        
        if response.status_code == 200:
            print(f"ShowMessage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowModalPopupWindow(UDW_name: str, width: int, height: int, sizeable: bool) -> None:
        """
        Shows a modal popup window in the GUI

        Args:
            UDW_name (str): The name of the user-defined window.
            width (int): The width of the popup window.
            height (int): The height of the popup window.
            sizeable (bool): Whether the popup window is sizeable.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(UDW_name)
        binary_payload += SDK_Helper.EncodeInt(width)
        binary_payload += SDK_Helper.EncodeInt(height)
        binary_payload += SDK_Helper.EncodeBool(sizeable)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowModalPopupWindow')
        
        if response.status_code == 200:
            print(f"ShowModalPopupWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowPmmManager() -> None:
        """
        Presents the user with the PMM Manager Window for opening and viewing PMMs.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowPmmManager')
        
        if response.status_code == 200:
            print(f"ShowPmmManager: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowPresentationEditorWindow(presentation_name: str) -> None:
        """
        Shows the 'presentation editor' popup window in the GUI

        Args:
            presentation_name (str): The name of the presentation to edit.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(presentation_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowPresentationEditorWindow')
        
        if response.status_code == 200:
            print(f"ShowPresentationEditorWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ShowProfileCreateWindow(delete_existing_AOIs: bool, thickness: int, show_thickness_UI: bool) -> None:
        """
        Shows the 'profile creation' popup window in the GUI

        Args:
            delete_existing_AOIs (bool): Whether to delete existing AOIs.
            thickness (int): The thickness of the profile.
            show_thickness_UI (bool): Whether to show the thickness UI.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeBool(delete_existing_AOIs)
        binary_payload += SDK_Helper.EncodeInt(thickness)
        binary_payload += SDK_Helper.EncodeBool(show_thickness_UI)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ShowProfileCreateWindow')
        
        if response.status_code == 200:
            print(f"ShowProfileCreateWindow: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SolveQuadratic(x0: float, y0: float, x1: float, y1: float, x2: float, y2: float) -> tuple[float, float, float]:
        """
        Solves a quadratic equation given three points.

        Args:
            x0 (float): The x-coordinate of the first point.
            y0 (float): The y-coordinate of the first point.
            x1 (float): The x-coordinate of the second point.
            y1 (float): The y-coordinate of the second point.
            x2 (float): The x-coordinate of the third point.
            y2 (float): The y-coordinate of the third point.

        Returns:
            tuple[float, float, float]: The coefficients (a, b, c) of the quadratic equation.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(x0)
        binary_payload += SDK_Helper.EncodeDouble(y0)
        binary_payload += SDK_Helper.EncodeDouble(x1)
        binary_payload += SDK_Helper.EncodeDouble(y1)
        binary_payload += SDK_Helper.EncodeDouble(x2)
        binary_payload += SDK_Helper.EncodeDouble(y2)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SolveQuadratic')
        
        if response.status_code == 200:
            print(f"SolveQuadratic: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeDouble(response.content[:8])
            result2 = SDK_Helper.DecodeDouble(response.content[8:16])
            result3 = SDK_Helper.DecodeDouble(response.content[16:])
            return (result1, result2, result3)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SortAois(
        tab_delimited_aoi_names: str,
        order: str,
        aoi_point: str,
        rename_parent: str,
        rename_children: str,
        cluster_proximity: int
    ) -> None:
        """
        Sorts the specified AOIs based on the given parameters.

        Args:
            tab_delimited_aoi_names (str): The tab-delimited list of AOI names.
            order (str): The order in which to sort the AOIs.
            aoi_point (str): The AOI point to use for sorting.
            rename_parent (str): The new name for the parent AOI.
            rename_children (str): The new names for the child AOIs.
            cluster_proximity (int): The proximity threshold for clustering AOIs.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(tab_delimited_aoi_names)
        binary_payload += SDK_Helper.EncodeString(order)
        binary_payload += SDK_Helper.EncodeString(aoi_point)
        binary_payload += SDK_Helper.EncodeString(rename_parent)
        binary_payload += SDK_Helper.EncodeString(rename_children)
        binary_payload += SDK_Helper.EncodeInt(cluster_proximity)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SortAois')
        
        if response.status_code == 200:
            print(f"SortAois: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SortDataTable(
        data_table_name: str,
        sort_columns_instead_of_rows: bool,
        skip_zeroth_row_or_column: bool,
        sory_by_arr: list[int],
        sort_order_is_rvs_array: list[bool]
    ) -> None:
        """
        Sorts the specified data table based on the given parameters.

        Args:
            data_table_name (str): The name of the data table to sort.
            sort_columns_instead_of_rows (bool): Whether to sort columns instead of rows.
            skip_zeroth_row_or_column (bool): Whether to skip the zeroth row or column.
            sory_by_arr (list[int]): The array of column/row indices to sort by.
            sort_order_is_rvs_array (list[bool]): The array of sort orders (True for descending, False for ascending).

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeBool(sort_columns_instead_of_rows)
        binary_payload += SDK_Helper.EncodeBool(skip_zeroth_row_or_column)
        binary_payload += SDK_Helper.EncodeIntArray(sory_by_arr)
        binary_payload += SDK_Helper.EncodeBoolArray(sort_order_is_rvs_array)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SortDataTable')
        
        if response.status_code == 200:
            print(f"SortDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def SplitList(list: int, count: int) -> PM_List:
        """
        Returns the handle to a list of strings created by splitting the source string into parts based on the delimiter supplied. 
        If the source string is empty, an empty list is returned; if the delimiter string is empty, a single-item list containing the source string is returned.
        
        Args:
            list (int): The handle to the list to split.
            count (int): The number of parts to split the list into.
        
        Returns:
            PM_List: The handle to the split list.

        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(list)
        binary_payload += SDK_Helper.EncodeInt(count)

        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'SplitList')

        if response.status_code == 200:
            print(f"SplitList: Success")
            result = SDK_Helper.DecodePMList(response.content)
            return result
            # Decode the response
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StartContinuousMeasuring(capture_scheme_name: str) -> None:
        """
        Starts continuous measuring with the specified capture scheme.

        Args:
            capture_scheme_name (str): The name of the capture scheme to use.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(capture_scheme_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StartContinuousMeasuring')
        
        if response.status_code == 200:
            print(f"StartContinuousMeasuring: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StartPreview(exposure_time: float) -> None:
        """
        Starts the preview with the specified exposure time.

        Args:
            exposure_time (float): The exposure time to use for the preview.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(exposure_time)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StartPreview')
        
        if response.status_code == 200:
            print(f"StartPreview: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StartScriptRecording() -> None:
        """
        Starts script recording.
        
        Args:
            None
            
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StartScriptRecording')
        
        if response.status_code == 200:
            print(f"StartScriptRecording: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StartSpectrometerPreview(exposure_time: float, use_bracketing: bool, auto_minimum_signal_percent: int) -> None:
        """
        Starts the spectrometer preview with the specified parameters.

        Args:
            exposure_time (float): The exposure time to use for the preview.
            use_bracketing (bool): Whether to use bracketing.
            auto_minimum_signal_percent (int): The auto minimum signal percent.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeFloat(exposure_time)
        binary_payload += SDK_Helper.EncodeBool(use_bracketing)
        binary_payload += SDK_Helper.EncodeInt(auto_minimum_signal_percent)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StartSpectrometerPreview')
        
        if response.status_code == 200:
            print(f"StartSpectrometerPreview: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StopContinuousMeasuring() -> None:
        """
        Stops continuous measuring.

        Args:
            None
        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StopContinuousMeasuring')
        
        if response.status_code == 200:
            print(f"StopContinuousMeasuring: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StopPreview() -> None:
        """
        Stops the preview.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StopPreview')
        
        if response.status_code == 200:
            print(f"StopPreview: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StopScriptRecording(script_name: str) -> None:
        """
        Stops recording actions for a script
        
        Args:
            script_name (str): The name of the script to stop recording.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(script_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StopScriptRecording')
        
        if response.status_code == 200:
            print(f"StopScriptRecording: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def StopSpectrometerPreview() -> None:
        """
        Stops the spectrometer preview.

        Args:
            None

        Returns:
            None
        """
        binary_payload = b""
        # No parameters to encode
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'StopSpectrometerPreview')
        
        if response.status_code == 200:
            print(f"StopSpectrometerPreview: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def TextVar(rowId: str, table_name: str) -> str:
        """
        Retrieves the text variable from a specific table and row.

        Args:
            rowId (str): The ID of the row to retrieve.
            table_name (str): The name of the data table to retrieve from.

        Returns:
            str: The text variable from the specified table and row.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(rowId)
        binary_payload += SDK_Helper.EncodeString(table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'TextVar')
        
        if response.status_code == 200:
            print(f"TextVar: Success")

            # Decode the response
            result = SDK_Helper.DecodeString(response.content)
            return result
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ThresholdMeasurement(
        measurement_name: str,
        apply_min_value: bool,
        min_value: float,
        apply_max_value: bool,
        max_value: float
    ) -> None:
        """
        Thresholds a measurement provided the min and max values.

        Args:
            measurement_name (str): The name of the measurement to threshold.
            apply_min_value (bool): Whether to apply the minimum value.
            min_value (float): The minimum value to apply.
            apply_max_value (bool): Whether to apply the maximum value.
            max_value (float): The maximum value to apply.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeBool(apply_min_value)
        binary_payload += SDK_Helper.EncodeFloat(min_value)
        binary_payload += SDK_Helper.EncodeBool(apply_max_value)
        binary_payload += SDK_Helper.EncodeFloat(max_value)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ThresholdMeasurement')
        
        if response.status_code == 200:
            print(f"ThresholdMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def ThresholdToSelection(measurement_name: str) -> None:
        """
        Thresholds a measurement to the current selection.

        Args:
            measurement_name (str): The name of the measurement to threshold.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'ThresholdToSelection')
        
        if response.status_code == 200:
            print(f"ThresholdToSelection: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def THTVToXY(theta_H: float, theta_V: float) -> tuple[float, float]:
        """
        Converts ThetaH and ThetaV coordinates to XY coordinates.

        Args:
            theta_H (float): The horizontal angle (ThetaH) in degrees.
            theta_V (float): The vertical angle (ThetaV) in degrees.

        Returns:
            tuple[float, float]: The corresponding XY coordinates.
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeDouble(theta_H)
        binary_payload += SDK_Helper.EncodeDouble(theta_V)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'THTVToXY')
        
        if response.status_code == 200:
            print(f"THTVToXY: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeDouble(response.content[:8])
            result2 = SDK_Helper.DecodeDouble(response.content[8:])
            return (result1, result2)

        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def TransformMeasurement(
        measurement_name: str,
        rotation_in_degrees: float,
        magnification_scalar: float,
        translation_x: float,
        translation_y: float
    ) -> None:
        """
        Transforms a measurement by applying rotation, magnification, and translation.

        Args:
            measurement_name (str): The name of the measurement to transform.
            rotation_in_degrees (float): The rotation angle in degrees.
            magnification_scalar (float): The magnification scalar.
            translation_x (float): The translation in the X direction.
            translation_y (float): The translation in the Y direction.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeDouble(rotation_in_degrees)
        binary_payload += SDK_Helper.EncodeDouble(magnification_scalar)
        binary_payload += SDK_Helper.EncodeDouble(translation_x)
        binary_payload += SDK_Helper.EncodeDouble(translation_y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'TransformMeasurement')
        
        if response.status_code == 200:
            print(f"TransformMeasurement: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def TransformMeasurementUsingDataTable(
        measurement_name: str,
        data_table_name: str,
        invalidate_values_outside_intersection: bool
    ) -> None:
        """
        Transforms a measurement using a data table.

        Args:
            measurement_name (str): The name of the measurement to transform.
            data_table_name (str): The name of the data table to use.
            invalidate_values_outside_intersection (bool): Whether to invalidate values outside the intersection.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        binary_payload += SDK_Helper.EncodeBool(invalidate_values_outside_intersection)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'TransformMeasurementUsingDataTable')
        
        if response.status_code == 200:
            print(f"TransformMeasurementUsingDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def TransposeDataTable(data_table_name: str) -> None:
        """
        Transposes the specified data table.

        Args:
            data_table_name (str): The name of the data table to transpose.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(data_table_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'TransposeDataTable')
        
        if response.status_code == 200:
            print(f"TransposeDataTable: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def UnloadPackage(package_name: str) -> None:
        """
        Unloads a package with the specified name
        
        Args:
            package_name (str): The name of the package to unload.
        
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(package_name)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'UnloadPackage')
        
        if response.status_code == 200:
            print(f"UnloadPackage: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def WriteToConsole(text: str) -> None:
        """
        Writes text to the Photometrica Console Window
        
        Args:
            text (str): The text to write to the console.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'WriteToConsole')
        
        if response.status_code == 200:
            print(f"WriteToConsole: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def WriteToMeasurementLog(measurement_name: str, text: str) -> None:
        """
        Writes text to the specified measurement log.

        Args:
            measurement_name (str): The name of the measurement.
            text (str): The text to write to the measurement log.

        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeString(measurement_name)
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'WriteToMeasurementLog')
        
        if response.status_code == 200:
            print(f"WriteToMeasurementLog: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def WriteToSerialPort(serial_port_handle: int, text: str) -> None:
        """
        Writes text to a serial port.

        Args:
            serial_port_handle (int): The handle of the serial port.
            text (str): The text to write to the serial port.
            
        Returns:
            None
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(serial_port_handle)
        binary_payload += SDK_Helper.EncodeString(text)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'WriteToSerialPort')
        
        if response.status_code == 200:
            print(f"WriteToSerialPort: Success")
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def XYToPolar(x: int, y: int) -> tuple[float, float]:
        """
        Converts XY Coordinates to Polar (Radius, Angle)

        Args:
            x (int): The X coordinate.
            y (int): The Y coordinate.

        Returns:
            tuple[float, float]: The Polar coordinates (Radius, Angle).
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'XYToPolar')
        
        if response.status_code == 200:
            print(f"XYToPolar: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeDouble(response.content[:8])
            result2 = SDK_Helper.DecodeDouble(response.content[8:])
            return (result1, result2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")

    @staticmethod
    def XYToTHTV(x: int, y: int) -> tuple[float, float]:
        """
        Converts XY Coordinates to THTV (ThetaH, ThetaV)
        
        Args:
            x (int): The X coordinate.
            y (int): The Y coordinate.
        
        Returns:
            tuple[float, float]: The THTV coordinates (ThetaH, ThetaV).
        """
        binary_payload = b""
        binary_payload += SDK_Helper.EncodeInt(x)
        binary_payload += SDK_Helper.EncodeInt(y)
        
        # Send the binary payload using PM.SendApiRequest
        response = PM.SendApiRequest(binary_payload, 'XYToTHTV')
        
        if response.status_code == 200:
            print(f"XYToTHTV: Success")

            # Decode the response
            result1 = SDK_Helper.DecodeDouble(response.content[:8])
            result2 = SDK_Helper.DecodeDouble(response.content[8:])
            return (result1, result2)
        else:
            print(f"Request failed with status code: {response.status_code}")
            raise ValueError("Request failed")