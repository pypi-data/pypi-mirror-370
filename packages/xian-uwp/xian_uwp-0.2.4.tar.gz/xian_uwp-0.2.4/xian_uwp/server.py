"""
Xian Wallet Protocol Server
Universal HTTP API server for all wallet implementations
"""

import asyncio
import hashlib
import json
import secrets
import logging
import uvicorn

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Set
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from xian_py.wallet import Wallet
from xian_py.xian import Xian
from xian_py.transaction import simulate_tx, get_nonce, create_tx, broadcast_tx_sync

from .models import (
    WalletType, Permission, ProtocolConfig, Endpoints, ErrorCodes, CORSConfig,
    AuthorizationRequest, TransactionRequest, SignMessageRequest, AddTokenRequest, UnlockRequest,
    WalletInfo, BalanceResponse, TransactionResult, SignatureResponse, 
    AuthorizationResponse, StatusResponse,
    Session, PendingRequest
)

from .client import WalletProtocolError
from .server_utils import RobustServerManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WalletProtocolServer:
    """Universal Wallet Protocol Server"""
    
    def __init__(
        self, 
        wallet_type: WalletType = WalletType.DESKTOP,
        cors_config: Optional[CORSConfig] = None,
        network_url: Optional[str] = None,
        chain_id: Optional[str] = None,
        wallet: Optional[Wallet] = None
    ):
        self.wallet_type = wallet_type
        self.uvicorn_server = None
        self.server_task = None
        self.is_running = False
        self.wallet = wallet
        self.xian_client: Optional[Xian] = None
        self.is_locked = True
        self.password_hash: Optional[str] = None
        
        # Robust server management
        self.server_manager: Optional[RobustServerManager] = None
        
        # CORS configuration
        self.cors_config = cors_config or CORSConfig.localhost_dev()
        
        # Network configuration (configurable, must be set before use)
        self.network_url = network_url
        self.chain_id = chain_id
        
        # Session management
        self.sessions: Dict[str, Session] = {}
        self.pending_requests: Dict[str, PendingRequest] = {}
        self.websocket_connections: Set[WebSocket] = set()
        self.websocket_subscriptions: Dict[WebSocket, Set[str]] = {}  # websocket -> set of request_ids
        
        # Cache and activity tracking
        self.cache: Dict[str, tuple] = {}  # (data, timestamp)
        self.last_activity = datetime.now()
        
        # Background task management
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Initialize FastAPI app
        self.app = self._create_app()
    
    def configure_network(self, network_url: str, chain_id: str):
        """Configure network settings"""
        self.network_url = network_url
        self.chain_id = chain_id
        logger.info(f"🌐 Network configured: {network_url} (chain: {chain_id})")
    
    def _validate_network_config(self):
        """Validate that network configuration is set"""
        if not self.network_url or not self.chain_id:
            raise WalletProtocolError("Network configuration not set. Call configure_network() first.")
    
    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(_: FastAPI):
            logger.info("🚀 Xian Wallet Protocol Server starting...")
            # Initialize network client if wallet and network are configured
            if self.wallet and self.network_url:
                self.xian_client = Xian(self.network_url, wallet=self.wallet)
                logger.info(f"📍 Wallet initialized: {self.wallet.public_key}")
            # Start background tasks
            cleanup_task = asyncio.create_task(self._cleanup_task())
            self.background_tasks.add(cleanup_task)
            
            yield
            
            logger.info("💤 Xian Wallet Protocol Server shutting down...")
            # Cancel all background tasks gracefully
            for task in self.background_tasks:
                task.cancel()
            
            # Wait for all tasks to complete cancellation
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
            self.background_tasks.clear()
        
        app = FastAPI(
            title="Xian Wallet Protocol Server",
            description="Universal HTTP API for Xian wallet operations",
            version=ProtocolConfig.PROTOCOL_VERSION,
            lifespan=lifespan
        )
        
        # CORS middleware with configurable settings
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_config.allow_origins,
            allow_credentials=self.cors_config.allow_credentials,
            allow_methods=self.cors_config.allow_methods,
            allow_headers=self.cors_config.allow_headers,
            expose_headers=self.cors_config.expose_headers,
            max_age=self.cors_config.max_age,
        )
        
        # Register routes
        self._register_routes(app)
        
        return app
    
    def _register_routes(self, app: FastAPI):
        """Register API routes"""
        security = HTTPBearer()
        
        # Helper functions
        def verify_session(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Session:
            """Verify and return session"""
            token = credentials.credentials
            session = self.sessions.get(token)
            
            if not session:
                raise HTTPException(status_code=401, detail=ErrorCodes.UNAUTHORIZED)
            
            if datetime.now() > session.expires_at:
                del self.sessions[token]
                raise HTTPException(status_code=401, detail=ErrorCodes.SESSION_EXPIRED)
            
            # Update activity
            session.last_activity = datetime.now()
            self.last_activity = datetime.now()
            return session
        
        def require_permission(permission: Permission):
            """Decorator to require specific permission"""
            def wrapper(session: Session = Depends(verify_session)):
                if permission not in session.permissions:
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                return session
            return wrapper
        
        def check_wallet_unlocked():
            """Check if wallet is unlocked"""
            if self.is_locked:
                raise HTTPException(status_code=423, detail=ErrorCodes.WALLET_LOCKED)
            if not self.wallet:
                raise HTTPException(status_code=404, detail=ErrorCodes.WALLET_NOT_FOUND)
        
        # Status endpoint (no auth required)
        @app.get(Endpoints.WALLET_STATUS, response_model=StatusResponse)
        async def get_wallet_status():
            """Get wallet status"""
            return StatusResponse(
                available=self.wallet is not None,
                locked=self.is_locked,
                wallet_type=self.wallet_type,
                network=self.network_url,
                chain_id=self.chain_id,
                version=ProtocolConfig.PROTOCOL_VERSION
            )
        
        # Authorization endpoints
        @app.post(Endpoints.AUTH_REQUEST)
        async def request_authorization(request: AuthorizationRequest):
            """Request DApp authorization"""
            request_id = secrets.token_urlsafe(16)
            
            pending_request = PendingRequest(
                request_id=request_id,
                app_name=request.app_name,
                app_url=request.app_url,
                permissions=request.permissions,
                description=request.description,
                created_at=datetime.now()
            )
            
            self.pending_requests[request_id] = pending_request
            
            # Notify wallet UI via WebSocket
            await self._broadcast_to_wallet({
                "type": "authorization_request",
                "request": pending_request.model_dump()
            })
            
            # Auto-cleanup after 5 minutes
            cleanup_task = asyncio.create_task(self._cleanup_request(request_id))
            self.background_tasks.add(cleanup_task)
            
            return {
                "request_id": request_id, 
                "status": "pending",
                "app_name": request.app_name
            }
        
        @app.get(Endpoints.AUTH_STATUS.replace("{request_id}", "{request_id}"))
        async def get_auth_status(request_id: str):
            """Get authorization request status"""
            pending_request = self.pending_requests.get(request_id)
            if not pending_request:
                # Check if it was approved (in sessions)
                for session in self.sessions.values():
                    if session.request_id == request_id:
                        return {"request_id": request_id, "status": "approved"}
                
                # Not found anywhere, might be denied or expired
                raise HTTPException(status_code=404, detail="Request not found")
            
            return {
                "request_id": request_id,
                "status": "pending",
                "app_name": pending_request.app_name,
                "app_url": pending_request.app_url,
                "permissions": pending_request.permissions,
                "description": pending_request.description
            }
        
        @app.get(Endpoints.AUTH_PENDING)
        async def list_pending_requests():
            """List all pending authorization requests"""
            pending_list = []
            for request_id, request in self.pending_requests.items():
                pending_list.append({
                    "request_id": request_id,
                    "status": "pending",
                    "app_name": request.app_name,
                    "app_url": request.app_url,
                    "permissions": request.permissions,
                    "description": request.description
                })
            return {"pending_requests": pending_list}
        
        @app.post(Endpoints.AUTH_APPROVE.replace("{request_id}", "{request_id}"))
        async def approve_authorization(request_id: str):
            """Approve authorization request"""
            pending_request = self.pending_requests.get(request_id)
            if not pending_request:
                raise HTTPException(status_code=404, detail="Request not found")
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(minutes=ProtocolConfig.SESSION_TIMEOUT_MINUTES)
            
            session = Session(
                token=session_token,
                app_name=pending_request.app_name,
                app_url=pending_request.app_url,
                permissions=pending_request.permissions,
                created_at=datetime.now(),
                expires_at=expires_at,
                last_activity=datetime.now(),
                request_id=request_id
            )
            
            self.sessions[session_token] = session
            del self.pending_requests[request_id]
            
            # Broadcast approval via WebSocket
            await self._broadcast_to_wallet({
                "type": "authorization_approved",
                "request_id": request_id,
                "session_token": session_token,
                "app_name": pending_request.app_name
            })
            
            return AuthorizationResponse(
                session_token=session_token,
                expires_at=expires_at,
                permissions=pending_request.permissions
            )
        
        @app.post(Endpoints.AUTH_DENY.replace("{request_id}", "{request_id}"))
        async def deny_authorization(request_id: str):
            """Deny authorization request"""
            if request_id in self.pending_requests:
                pending_request = self.pending_requests[request_id]
                del self.pending_requests[request_id]
                
                # Broadcast denial via WebSocket
                await self._broadcast_to_wallet({
                    "type": "authorization_denied",
                    "request_id": request_id,
                    "app_name": pending_request.app_name
                })
                
            return {"status": "denied"}
        
        # Wallet endpoints
        @app.get(Endpoints.WALLET_INFO, response_model=WalletInfo)
        async def get_wallet_info(_: Session = Depends(require_permission(Permission.WALLET_INFO))):
            """Get wallet information"""
            # Wallet info should be available even when locked - only check wallet exists
            if not self.wallet:
                raise HTTPException(status_code=404, detail=ErrorCodes.WALLET_NOT_FOUND)
            
            cache_key = "wallet_info"
            cached_data = self._get_cached(cache_key, ttl_seconds=60)
            
            if cached_data:
                return cached_data
            
            wallet_info = WalletInfo(
                address=self.wallet.public_key,
                truncated_address=f"{self.wallet.public_key[:8]}...{self.wallet.public_key[-8:]}",
                locked=self.is_locked,
                chain_id=self.chain_id,
                network=self.network_url,
                wallet_type=self.wallet_type
            )
            
            self._set_cache(cache_key, wallet_info)
            return wallet_info
        
        @app.post(Endpoints.WALLET_UNLOCK)
        async def unlock_wallet(request: UnlockRequest):
            """Unlock wallet"""
            if not self.password_hash:
                raise HTTPException(status_code=400, detail="No password set")
            
            password_hash = hashlib.sha256(request.password.encode()).hexdigest()
            if password_hash != self.password_hash:
                raise HTTPException(status_code=401, detail="Invalid password")
            
            self.is_locked = False
            self.last_activity = datetime.now()
            self._clear_cache()
            
            return {"status": "unlocked"}
        
        @app.post(Endpoints.WALLET_LOCK)
        async def lock_wallet():
            """Lock wallet"""
            self.is_locked = True
            self._clear_cache()
            return {"status": "locked"}
        
        # Balance endpoints
        @app.get(Endpoints.BALANCE.replace("{contract}", "{contract}"), response_model=BalanceResponse)
        async def get_balance(contract: str, _: Session = Depends(require_permission(Permission.BALANCE))):
            """Get token balance"""
            # Balance contains sensitive financial information - require unlocked wallet
            check_wallet_unlocked()
            
            cache_key = f"balance_{contract}_{self.wallet.public_key}"
            cached_data = self._get_cached(cache_key, ttl_seconds=10)
            
            if cached_data:
                return cached_data
            
            try:
                if not self.xian_client:
                    raise HTTPException(status_code=503, detail="Network client not configured")
                
                balance = self.xian_client.get_balance(self.wallet.public_key, contract=contract)
                response = BalanceResponse(balance=balance, contract=contract)
                self._set_cache(cache_key, response)
                return response
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Transaction endpoints
        @app.post(Endpoints.TRANSACTION, response_model=TransactionResult)
        async def send_transaction(request: TransactionRequest, _: Session = Depends(require_permission(Permission.TRANSACTIONS))):
            """Send transaction"""
            check_wallet_unlocked()
            self._validate_network_config()
            
            try:
                nonce = get_nonce(self.network_url, self.wallet.public_key)
                
                payload = {
                    "chain_id": self.chain_id,
                    "contract": request.contract,
                    "function": request.function,
                    "kwargs": request.kwargs,
                    "nonce": nonce,
                    "sender": self.wallet.public_key,
                    "stamps_supplied": request.stamps_supplied or 0
                }
                
                # Estimate stamps if not provided
                if not request.stamps_supplied:
                    simulated = simulate_tx(self.network_url, payload)
                    payload["stamps_supplied"] = simulated.get("stamps_used", 50000)
                
                # Create and broadcast transaction
                tx = create_tx(payload, self.wallet)
                result = broadcast_tx_sync(self.network_url, tx)
                
                # Clear balance cache after transaction
                self._clear_cache_pattern("balance_")
                
                return TransactionResult(
                    success=True,
                    transaction_hash=tx.get("hash"),
                    result=result,
                    gas_used=payload["stamps_supplied"]
                )
            except Exception as e:
                return TransactionResult(
                    success=False,
                    errors=[str(e)]
                )
        
        @app.post(Endpoints.SIGN_MESSAGE, response_model=SignatureResponse)
        async def sign_message(request: SignMessageRequest, _: Session = Depends(require_permission(Permission.SIGN_MESSAGE))):
            """Sign message"""
            check_wallet_unlocked()
            
            try:
                signature = self.wallet.sign_msg(request.message)
                return SignatureResponse(
                    signature=signature,
                    message=request.message,
                    address=self.wallet.public_key
                )
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Token management
        @app.post(Endpoints.ADD_TOKEN)
        async def add_token(request: AddTokenRequest, _: Session = Depends(require_permission(Permission.ADD_TOKEN))):
            """Add token to wallet"""
            # In full implementation, this would add to wallet's token list
            return {"accepted": True, "contract": request.contract_address}
        
        # WebSocket endpoint
        @app.websocket(Endpoints.WEBSOCKET)
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time communication"""
            await websocket.accept()
            self.websocket_connections.add(websocket)
            self.websocket_subscriptions[websocket] = set()
            
            try:
                while True:
                    data = await websocket.receive_text()
                    try:
                        message = json.loads(data)
                        
                        # Handle ping/pong
                        if message.get("type") == "ping":
                            await websocket.send_text('{"type":"pong"}')
                        
                        # Handle subscription to authorization requests
                        elif message.get("type") == "subscribe":
                            request_id = message.get("request_id")
                            if request_id:
                                self.websocket_subscriptions[websocket].add(request_id)
                                await websocket.send_text(json.dumps({
                                    "type": "subscribed",
                                    "request_id": request_id
                                }))
                        
                        # Handle unsubscription
                        elif message.get("type") == "unsubscribe":
                            request_id = message.get("request_id")
                            if request_id and websocket in self.websocket_subscriptions:
                                self.websocket_subscriptions[websocket].discard(request_id)
                                await websocket.send_text(json.dumps({
                                    "type": "unsubscribed",
                                    "request_id": request_id
                                }))
                                
                    except json.JSONDecodeError:
                        # Invalid JSON message, ignore
                        pass
                            
            except WebSocketDisconnect:
                self.websocket_connections.discard(websocket)
                if websocket in self.websocket_subscriptions:
                    del self.websocket_subscriptions[websocket]
    
    # Cache management
    def _get_cached(self, key: str, ttl_seconds: int) -> Optional[Any]:
        """Get cached data if still valid"""
        if key not in self.cache:
            return None
        
        data, timestamp = self.cache[key]
        if (datetime.now() - timestamp).total_seconds() > ttl_seconds:
            del self.cache[key]
            return None
        
        return data
    
    def _set_cache(self, key: str, data: Any):
        """Set cache data"""
        self.cache[key] = (data, datetime.now())
    
    def _clear_cache(self):
        """Clear all cache"""
        self.cache.clear()
    
    def _clear_cache_pattern(self, pattern: str):
        """Clear cache entries matching pattern"""
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.cache[key]
    
    # WebSocket helpers
    async def _broadcast_to_wallet(self, message: dict):
        """Broadcast message to wallet UI and subscribed clients"""
        
        if self.websocket_connections:
            disconnected = set()
            message_str = json.dumps(message)
            
            # Check if this is an authorization-related message
            message_type = message.get("type", "")
            request_id = message.get("request_id")
            
            for websocket in self.websocket_connections:
                try:
                    # For authorization messages, only send to subscribed clients
                    if message_type in ["authorization_approved", "authorization_denied"] and request_id:
                        if websocket in self.websocket_subscriptions and request_id in self.websocket_subscriptions[websocket]:
                            await websocket.send_text(message_str)
                    else:
                        # For other messages (like authorization_request), broadcast to all
                        await websocket.send_text(message_str)
                except:
                    disconnected.add(websocket)
            
            # Remove disconnected websockets
            self.websocket_connections -= disconnected
            for ws in disconnected:
                if ws in self.websocket_subscriptions:
                    del self.websocket_subscriptions[ws]
    
    # Background tasks
    async def _cleanup_task(self):
        """Background cleanup task"""
        try:
            while True:
                await asyncio.sleep(60)  # Run every minute
                
                # Clean expired sessions
                now = datetime.now()
                expired_tokens = [
                    token for token, session in self.sessions.items()
                    if now > session.expires_at
                ]
                for token in expired_tokens:
                    del self.sessions[token]
                
                # Clean old pending requests
                expired_requests = [
                    req_id for req_id, request in self.pending_requests.items()
                    if (now - request.created_at).total_seconds() > 300  # 5 minutes
                ]
                for req_id in expired_requests:
                    del self.pending_requests[req_id]
                
                # Auto-lock on inactivity
                if not self.is_locked and self.last_activity:
                    inactive_time = now - self.last_activity
                    if inactive_time.total_seconds() > ProtocolConfig.AUTO_LOCK_MINUTES * 60:
                        self.is_locked = True
                        self._clear_cache()
                        logger.info("Wallet auto-locked due to inactivity")
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled during shutdown")
            raise
    
    async def _cleanup_request(self, request_id: str):
        """Cleanup specific request after timeout"""
        try:
            await asyncio.sleep(300)  # 5 minutes
            self.pending_requests.pop(request_id, None)
        except asyncio.CancelledError:
            # Clean up the request immediately on cancellation
            self.pending_requests.pop(request_id, None)
            # Remove self from background tasks
            current_task = asyncio.current_task()
            self.background_tasks.discard(current_task)
    
    # Wallet management
    def set_wallet(self, wallet: Wallet, password_hash: Optional[str] = None):
        """Set the wallet instance and optional password hash"""
        self.wallet = wallet
        if password_hash:
            self.password_hash = password_hash
        
        # Initialize network client if network is configured
        if self.network_url:
            self.xian_client = Xian(self.network_url, wallet=self.wallet)
            logger.info(f"📍 Wallet configured: {self.wallet.public_key}")
    
    def lock_wallet(self):
        """Lock the wallet"""
        self.is_locked = True
        logger.info("🔒 Wallet locked")
    
    def unlock_wallet(self, password: str) -> bool:
        """Unlock the wallet with password"""
        if not self.password_hash:
            raise HTTPException(status_code=400, detail="No password set for wallet")
        
        provided_hash = hashlib.sha256(password.encode()).hexdigest()
        if provided_hash == self.password_hash:
            self.is_locked = False
            logger.info("🔓 Wallet unlocked")
            return True
        return False
    
    def run(
        self, 
        host: str = ProtocolConfig.DEFAULT_HOST, 
        port: int = ProtocolConfig.DEFAULT_PORT,
        allow_any_host: bool = False,
        force_cleanup: bool = False
    ):
        """Run the server (blocking call) with robust startup"""
        # Allow binding to any host for web deployment scenarios
        if allow_any_host:
            host = "0.0.0.0"

        # Use asyncio to handle robust startup
        asyncio.run(self._run_with_robust_startup(host, port, force_cleanup))

    async def _run_with_robust_startup(self, host: str, port: int, force_cleanup: bool):
        """Internal method to run server with robust startup"""
        self.server_manager = RobustServerManager(host, port)
        
        # Ensure port is available
        success, message = await self.server_manager.prepare_startup(force_cleanup)
        logger.info(self.server_manager.get_startup_message(success, message))
        
        if not success and not force_cleanup:
            raise RuntimeError(f"Cannot start server: {message}")
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"🔒 CORS origins: {self.cors_config.allow_origins}")

        # Create uvicorn server instance with socket reuse
        config = uvicorn.Config(
            self.app, 
            host=host, 
            port=port, 
            log_level="info",
            # Enable socket reuse for robust restarts
            access_log=False  # Reduce log noise
        )
        self.uvicorn_server = uvicorn.Server(config)
        self.is_running = True

        # Run the server (blocking)
        await self.uvicorn_server.serve()
        
    async def start_async(
        self,
        host: str = ProtocolConfig.DEFAULT_HOST,
        port: int = ProtocolConfig.DEFAULT_PORT,
        allow_any_host: bool = False,
        force_cleanup: bool = False
    ):
        """Start the server asynchronously with robust startup"""
        if allow_any_host:
            host = "0.0.0.0"
        
        # Initialize server manager
        self.server_manager = RobustServerManager(host, port)
        
        # Ensure port is available
        success, message = await self.server_manager.prepare_startup(force_cleanup)
        logger.info(self.server_manager.get_startup_message(success, message))
        
        if not success and not force_cleanup:
            raise RuntimeError(f"Cannot start server: {message}")
            
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"🔒 CORS origins: {self.cors_config.allow_origins}")
        
        # Create uvicorn server instance with socket reuse
        config = uvicorn.Config(
            self.app, 
            host=host, 
            port=port, 
            log_level="info",
            access_log=False  # Reduce log noise
        )
        self.uvicorn_server = uvicorn.Server(config)
        self.is_running = True
        
        # Start server in background task
        self.server_task = asyncio.create_task(self.uvicorn_server.serve())
        
    async def stop_async(self):
        """Stop the server asynchronously"""
        if self.uvicorn_server and self.is_running:
            logger.info("🛑 Stopping server...")
            self.uvicorn_server.should_exit = True
            
            if self.server_task:
                self.server_task.cancel()
                try:
                    await asyncio.wait_for(self.server_task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
                    
            logger.info("✅ Server stopped")
        
        # Always set is_running to False when stop is called
        self.is_running = False
            
    def stop(self):
        """Stop the server (synchronous wrapper)"""
        if self.uvicorn_server and self.is_running:
            logger.info("🛑 Stopping server...")
            self.is_running = False
            self.uvicorn_server.should_exit = True
            logger.info("✅ Server stop requested")
            
    def is_server_running(self):
        """Check if server is currently running"""
        return self.is_running and self.uvicorn_server is not None
    
    def run_robust(
        self,
        host: str = ProtocolConfig.DEFAULT_HOST,
        port: int = ProtocolConfig.DEFAULT_PORT,
        allow_any_host: bool = False,
        max_retries: int = 3
    ):
        """
        Run server with robust startup that handles port conflicts automatically
        
        This method will:
        1. Check if port is in use
        2. If in use, check if existing server is responsive
        3. If unresponsive, clean up and start new server
        4. Retry up to max_retries times
        """
        for attempt in range(max_retries):
            try:
                # On first attempt, try without force cleanup
                # On subsequent attempts, use force cleanup
                force_cleanup = attempt > 0
                
                logger.info(f"🚀 Server startup attempt {attempt + 1}/{max_retries}")
                self.run(host=host, port=port, allow_any_host=allow_any_host, force_cleanup=force_cleanup)
                return  # Success!
                
            except Exception as e:
                logger.warning(f"Startup attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Failed to start server after {max_retries} attempts")
                    raise
                else:
                    logger.info(f"🔄 Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
    
    async def start_async_robust(
        self,
        host: str = ProtocolConfig.DEFAULT_HOST,
        port: int = ProtocolConfig.DEFAULT_PORT,
        allow_any_host: bool = False,
        max_retries: int = 3
    ):
        """
        Start server asynchronously with robust startup that handles port conflicts automatically
        """
        for attempt in range(max_retries):
            try:
                # On first attempt, try without force cleanup
                # On subsequent attempts, use force cleanup
                force_cleanup = attempt > 0
                
                logger.info(f"🚀 Async server startup attempt {attempt + 1}/{max_retries}")
                await self.start_async(host=host, port=port, allow_any_host=allow_any_host, force_cleanup=force_cleanup)
                return  # Success!
                
            except Exception as e:
                logger.warning(f"Async startup attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ Failed to start async server after {max_retries} attempts")
                    raise
                else:
                    logger.info(f"🔄 Retrying in 2 seconds...")
                    await asyncio.sleep(2)


def create_server(
    wallet_type: WalletType = WalletType.DESKTOP,
    cors_config: Optional[CORSConfig] = None
) -> WalletProtocolServer:
    """Factory function to create server instance"""
    return WalletProtocolServer(wallet_type=wallet_type, cors_config=cors_config)


if __name__ == "__main__":
    server = create_server()
    server.run()
