"""
C.A.B.E.K. Python SDK
Official Python SDK for integrating C.A.B.E.K. biometric authentication

Installation:
    pip install cabek-sdk

Usage:
    from cabek_sdk import CABEK
    
    cabek = CABEK(api_key="your_api_key")
    result = await cabek.authenticate(ecg_data)
"""

import asyncio
import aiohttp
import hashlib
import hmac
import json
import time
import numpy as np
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from datetime import datetime, timedelta


class AuthenticationState(Enum):
    """Authentication states"""
    IDLE = "idle"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    FAILED = "failed"
    LOCKED = "locked"


@dataclass
class AuthenticationResult:
    """Result of an authentication attempt"""
    success: bool
    confidence: float
    ephemeral_token: Optional[str] = None
    expires_ms: int = 100
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[int] = None
    
    def is_valid(self) -> bool:
        """Check if authentication is still valid"""
        if not self.success or not self.timestamp:
            return False
        
        elapsed_ms = (time.time_ns() - self.timestamp) / 1_000_000
        return elapsed_ms < self.expires_ms


@dataclass
class EnrollmentResult:
    """Result of biometric enrollment"""
    success: bool
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class DeviceInfo:
    """Information about a connected device"""
    device_id: str
    device_type: str  # "smartwatch", "chest_strap", "patch", "web"
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    battery_level: Optional[float] = None
    sampling_rate: int = 256
    is_connected: bool = False
    last_seen: Optional[datetime] = None


class CABEKException(Exception):
    """Base exception for C.A.B.E.K. SDK"""
    pass


class AuthenticationException(CABEKException):
    """Authentication failed exception"""
    pass


class ConnectionException(CABEKException):
    """Connection to C.A.B.E.K. API failed"""
    pass


class SignalQualityException(CABEKException):
    """ECG signal quality too poor for authentication"""
    pass


class CABEK:
    """
    Main C.A.B.E.K. SDK client
    
    Provides easy integration with C.A.B.E.K. biometric authentication system
    """
    
    def __init__(self, 
                 api_key: str,
                 api_url: str = "https://api.cabek.io",
                 timeout: float = 30.0,
                 auto_reconnect: bool = True):
        """
        Initialize C.A.B.E.K. client
        
        Args:
            api_key: Your C.A.B.E.K. API key
            api_url: Base URL for C.A.B.E.K. API
            timeout: Request timeout in seconds
            auto_reconnect: Automatically reconnect on connection loss
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.auto_reconnect = auto_reconnect
        
        # Session management
        self._session: Optional[aiohttp.ClientSession] = None
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None
        
        # State tracking
        self.state = AuthenticationState.IDLE
        self.current_session_id: Optional[str] = None
        self.connected_devices: Dict[str, DeviceInfo] = {}
        
        # Callbacks
        self.on_authenticated: Optional[Callable] = None
        self.on_locked: Optional[Callable] = None
        self.on_device_connected: Optional[Callable] = None
        self.on_device_disconnected: Optional[Callable] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Connect to C.A.B.E.K. API"""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'X-SDK-Version': '1.0.0',
                    'X-SDK-Language': 'Python'
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def disconnect(self):
        """Disconnect from C.A.B.E.K. API"""
        if self._websocket:
            await self._websocket.close()
            self._websocket = None
        
        if self._session:
            await self._session.close()
            self._session = None
    
    async def _request(self, 
                      method: str, 
                      endpoint: str, 
                      data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to C.A.B.E.K. API
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        if not self._session:
            await self.connect()
        
        url = f"{self.api_url}{endpoint}"
        
        try:
            async with self._session.request(method, url, json=data) as response:
                if response.status == 401:
                    raise AuthenticationException("Invalid API key")
                elif response.status == 429:
                    raise CABEKException("Rate limit exceeded")
                elif response.status >= 400:
                    error_data = await response.json()
                    raise CABEKException(f"API error: {error_data.get('error', 'Unknown')}")
                
                return await response.json()
                
        except aiohttp.ClientError as e:
            raise ConnectionException(f"Connection failed: {str(e)}")
    
    async def enroll(self, 
                    user_id: str,
                    ecg_data: Union[List[float], np.ndarray],
                    device_id: Optional[str] = None,
                    device_type: str = "web") -> EnrollmentResult:
        """
        Enroll a user for biometric authentication
        
        Args:
            user_id: Unique user identifier (e.g., email)
            ecg_data: ECG signal data for enrollment
            device_id: Optional device identifier
            device_type: Type of device used for enrollment
            
        Returns:
            EnrollmentResult object
        """
        # Convert numpy array to list if needed
        if isinstance(ecg_data, np.ndarray):
            ecg_data = ecg_data.tolist()
        
        # Validate ECG data
        if len(ecg_data) < 256:
            raise SignalQualityException("Insufficient ECG data for enrollment (minimum 256 samples)")
        
        data = {
            'user_id': user_id,
            'ecg_data': ecg_data[:2048],  # Use up to 8 seconds at 256Hz
            'device_id': device_id or self._generate_device_id(),
            'device_type': device_type,
            'timestamp_ns': time.time_ns()
        }
        
        try:
            response = await self._request('POST', '/users/enroll', data)
            
            return EnrollmentResult(
                success=response.get('enrolled', False),
                user_id=response.get('user_id'),
                device_id=data['device_id'],
                message=response.get('message'),
                error=response.get('error')
            )
            
        except Exception as e:
            return EnrollmentResult(
                success=False,
                error=str(e)
            )
    
    async def authenticate(self,
                          ecg_data: Union[List[float], np.ndarray],
                          user_id: Optional[str] = None,
                          device_id: Optional[str] = None) -> AuthenticationResult:
        """
        Authenticate using ECG biometric data
        
        Args:
            ecg_data: ECG signal data
            user_id: Optional user identifier
            device_id: Optional device identifier
            
        Returns:
            AuthenticationResult object
        """
        self.state = AuthenticationState.AUTHENTICATING
        
        # Convert numpy array to list if needed
        if isinstance(ecg_data, np.ndarray):
            ecg_data = ecg_data.tolist()
        
        # Validate ECG data
        if len(ecg_data) < 128:
            self.state = AuthenticationState.FAILED
            raise SignalQualityException("Insufficient ECG data (minimum 128 samples)")
        
        data = {
            'ecg_data': ecg_data[:512],  # Use up to 2 seconds at 256Hz
            'user_id': user_id,
            'device_id': device_id or self._generate_device_id(),
            'timestamp_ns': time.time_ns()
        }
        
        try:
            response = await self._request('POST', '/auth/verify', data)
            
            result = AuthenticationResult(
                success=response.get('authenticated', False),
                confidence=response.get('confidence', 0.0),
                ephemeral_token=response.get('ephemeral_token'),
                expires_ms=response.get('expires_ms', 100),
                user_id=response.get('user_id'),
                device_id=data['device_id'],
                error=response.get('error'),
                timestamp=time.time_ns()
            )
            
            if result.success:
                self.state = AuthenticationState.AUTHENTICATED
                if self.on_authenticated:
                    self.on_authenticated(result)
            else:
                self.state = AuthenticationState.FAILED
                
            return result
            
        except Exception as e:
            self.state = AuthenticationState.FAILED
            return AuthenticationResult(
                success=False,
                confidence=0.0,
                error=str(e),
                timestamp=time.time_ns()
            )
    
    async def start_continuous_auth(self,
                                   ecg_stream_callback: Callable,
                                   user_id: str,
                                   device_id: Optional[str] = None,
                                   auth_frequency_hz: float = 10.0):
        """
        Start continuous authentication stream
        
        Args:
            ecg_stream_callback: Async function that yields ECG data
            user_id: User identifier
            device_id: Optional device identifier
            auth_frequency_hz: Authentication frequency in Hz
        """
        device_id = device_id or self._generate_device_id()
        
        # Create continuous authentication session
        session_data = {
            'user_id': user_id,
            'device_id': device_id,
            'auth_frequency_hz': auth_frequency_hz
        }
        
        response = await self._request('POST', '/auth/continuous/start', session_data)
        self.current_session_id = response.get('session_id')
        
        # Connect WebSocket for real-time updates
        ws_url = self.api_url.replace('http', 'ws') + f'/ws/auth/{self.current_session_id}'
        # Note: websockets library uses 'extra_headers' in newer versions, 'subprotocols' in older
        try:
            # Try newer version syntax first
            self._websocket = await websockets.connect(
                ws_url,
                extra_headers={'Authorization': f'Bearer {self.api_key}'}
            )
        except TypeError:
            # Fall back to adding auth in URL or using subprotocols
            ws_url_with_auth = f"{ws_url}?api_key={self.api_key}"
            self._websocket = await websockets.connect(ws_url_with_auth)
        
        # Start authentication loop
        auth_interval = 1.0 / auth_frequency_hz
        
        try:
            async for ecg_data in ecg_stream_callback():
                # Authenticate
                result = await self.authenticate(ecg_data, user_id, device_id)
                
                # Send to WebSocket
                await self._websocket.send(json.dumps({
                    'type': 'auth_result',
                    'session_id': self.current_session_id,
                    'result': asdict(result)
                }))
                
                # Check for lock condition
                if not result.success:
                    self.state = AuthenticationState.LOCKED
                    if self.on_locked:
                        self.on_locked(result)
                    break
                
                # Wait for next interval
                await asyncio.sleep(auth_interval)
                
        finally:
            # End session
            if self.current_session_id:
                await self._request('POST', f'/auth/continuous/end/{self.current_session_id}')
                self.current_session_id = None
    
    async def connect_device(self, 
                            device_type: str,
                            connection_params: Dict[str, Any]) -> DeviceInfo:
        """
        Connect to a biometric device
        
        Args:
            device_type: Type of device (smartwatch, chest_strap, etc.)
            connection_params: Device-specific connection parameters
            
        Returns:
            DeviceInfo object
        """
        device_id = connection_params.get('device_id', self._generate_device_id())
        
        device = DeviceInfo(
            device_id=device_id,
            device_type=device_type,
            model=connection_params.get('model'),
            firmware_version=connection_params.get('firmware_version'),
            sampling_rate=connection_params.get('sampling_rate', 256),
            is_connected=True,
            last_seen=datetime.now()
        )
        
        self.connected_devices[device_id] = device
        
        if self.on_device_connected:
            self.on_device_connected(device)
        
        return device
    
    async def disconnect_device(self, device_id: str):
        """Disconnect a biometric device"""
        if device_id in self.connected_devices:
            device = self.connected_devices[device_id]
            device.is_connected = False
            
            if self.on_device_disconnected:
                self.on_device_disconnected(device)
            
            del self.connected_devices[device_id]
    
    def _generate_device_id(self) -> str:
        """Generate unique device ID"""
        return hashlib.sha256(
            f"{time.time_ns()}{id(self)}".encode()
        ).hexdigest()[:16]
    
    async def get_session_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for authentication session"""
        session_id = session_id or self.current_session_id
        if not session_id:
            return {}
        
        return await self._request('GET', f'/auth/sessions/{session_id}/stats')
    
    async def validate_signal_quality(self, 
                                     ecg_data: Union[List[float], np.ndarray]) -> Dict[str, Any]:
        """
        Validate ECG signal quality before authentication
        
        Args:
            ecg_data: ECG signal data
            
        Returns:
            Signal quality metrics
        """
        if isinstance(ecg_data, np.ndarray):
            ecg_data = ecg_data.tolist()
        
        response = await self._request('POST', '/signals/validate', {
            'ecg_data': ecg_data[:512]
        })
        
        return response


# Convenience functions for synchronous usage
def create_client(api_key: str, **kwargs) -> CABEK:
    """Create C.A.B.E.K. client"""
    return CABEK(api_key, **kwargs)


async def quick_authenticate(api_key: str, 
                            ecg_data: Union[List[float], np.ndarray],
                            user_id: Optional[str] = None) -> AuthenticationResult:
    """Quick authentication without managing client lifecycle"""
    async with CABEK(api_key) as client:
        return await client.authenticate(ecg_data, user_id)


# Example usage
async def example_usage():
    """Example of using C.A.B.E.K. SDK"""
    
    # Initialize client
    cabek = CABEK(api_key="sk_live_your_api_key_here")
    
    try:
        # Connect to API
        await cabek.connect()
        
        # Generate sample ECG data (in production, this comes from a device)
        ecg_data = np.random.randn(512) * 0.1  # 2 seconds at 256Hz
        
        # Enroll a new user
        print("Enrolling user...")
        enrollment = await cabek.enroll(
            user_id="user@example.com",
            ecg_data=ecg_data,
            device_type="smartwatch"
        )
        
        if enrollment.success:
            print(f"✅ Enrollment successful: {enrollment.message}")
        else:
            print(f"❌ Enrollment failed: {enrollment.error}")
        
        # Authenticate the user
        print("\nAuthenticating...")
        auth_result = await cabek.authenticate(
            ecg_data=ecg_data,
            user_id="user@example.com"
        )
        
        if auth_result.success:
            print(f"✅ Authentication successful!")
            print(f"   Confidence: {auth_result.confidence:.2%}")
            print(f"   Token expires in: {auth_result.expires_ms}ms")
        else:
            print(f"❌ Authentication failed: {auth_result.error}")
        
        # Continuous authentication example
        async def ecg_stream():
            """Simulate ECG data stream"""
            for _ in range(20):  # 20 authentications
                yield np.random.randn(256) * 0.1
                await asyncio.sleep(0.1)  # 10Hz
        
        # Set up callbacks
        cabek.on_authenticated = lambda r: print(f"🔓 Authenticated: {r.confidence:.2%}")
        cabek.on_locked = lambda r: print(f"🔒 Locked: {r.error}")
        
        # Start continuous authentication
        print("\nStarting continuous authentication...")
        await cabek.start_continuous_auth(
            ecg_stream_callback=ecg_stream,
            user_id="user@example.com",
            auth_frequency_hz=10.0
        )
        
    finally:
        # Clean up
        await cabek.disconnect()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
