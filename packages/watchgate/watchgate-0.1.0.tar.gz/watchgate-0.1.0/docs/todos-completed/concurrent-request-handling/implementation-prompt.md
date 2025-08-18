# Concurrent Request Handling Implementation Prompt

## CRITICAL INSTRUCTIONS

**YOU MUST FOLLOW TEST-DRIVEN DEVELOPMENT (TDD) METHODOLOGY**
- Write tests FIRST (RED phase)
- Make tests pass with minimal code (GREEN phase)  
- Improve code while keeping tests green (REFACTOR phase)
- **DO NOT STOP UNTIL ALL TESTS PASS**

## Context

You are implementing concurrent request handling for Watchgate's MCPProxy. Currently, the proxy processes requests sequentially. Your task is to enable it to handle multiple requests concurrently by leveraging the existing infrastructure in StdioTransport.

**Current Problem**: 
```python
# In MCPProxy.handle_request() - lines 240-241
await self._upstream_transport.send_message(upstream_request)
response = await self._upstream_transport.receive_message()  # This returns ANY response, not the specific one!
```

## Prerequisites

Before starting, verify:
1. All existing tests pass: `pytest tests/`
2. You're in the project root: `/Users/dbright/mcp/watchgate`
3. You have the requirements document: `docs/todos/concurrent-request-handling/requirements.md`

## Phase 1: Enable Existing Concurrent Tests (RED Phase)

### Step 1.1: Update Test File
**File**: `tests/integration/test_concurrent_requests.py`

**Action**: Remove the `@pytest.mark.xfail` decorators from all test methods.

**Change lines 79, 135, 197, 258, 319, 386, 450**:
```python
# REMOVE this line:
@pytest.mark.xfail(reason="MCPProxy does not yet support concurrent requests - see docs/todos/concurrent-request-handling/")

# So the test declaration looks like:
@pytest.mark.asyncio
async def test_basic_concurrent_requests_10(self, concurrent_test_config, temp_work_directory):
```

### Step 1.2: Run Tests to Confirm They Fail
```bash
pytest tests/integration/test_concurrent_requests.py -v
```

**Expected**: All 7 tests should FAIL (not xfail). If they still show as 'xfail', double-check you removed all decorators.

## Phase 2: Enhance Transport Interface (GREEN Phase - Part 1)

### Step 2.1: Add New Method to Base Transport
**File**: `watchgate/transport/base.py`

**Add this method to the Transport class** (after the existing abstract methods):
```python
async def send_and_receive(self, request: MCPRequest) -> MCPResponse:
    """Send a request and wait for its specific response.
    
    This method ensures correct request/response correlation for concurrent requests.
    
    Args:
        request: The MCP request to send
        
    Returns:
        The specific response for this request
        
    Raises:
        RuntimeError: If not connected or request fails
        asyncio.TimeoutError: If response timeout occurs
    """
    # Default implementation for backward compatibility
    await self.send_message(request)
    return await self.receive_message()
```

### Step 2.2: Implement in StdioTransport
**File**: `watchgate/transport/stdio.py`

**Add these imports at the top** (around line 10):
```python
from typing import Dict, Any, Optional, Union
```

**Add this method to StdioTransport class** (after the `receive_message` method, around line 410):
```python
async def send_and_receive(self, request: MCPRequest) -> MCPResponse:
    """Send a request and wait for its specific response.
    
    This method uses the existing request tracking infrastructure to ensure
    we get the correct response even when multiple requests are in flight.
    
    Args:
        request: The MCP request to send
        
    Returns:
        The specific response for this request
        
    Raises:
        RuntimeError: If not connected or request fails
        asyncio.TimeoutError: If response timeout occurs
    """
    if not self.is_connected():
        raise RuntimeError("Not connected")
    
    # Check if process has exited
    if self._process.returncode is not None:
        raise RuntimeError("MCP server process has exited")
    
    # Register this request for response correlation
    async with self._request_lock:
        future = asyncio.Future()
        self._pending_requests[request.id] = future
    
    # Serialize and send the request
    message_dict = {
        "jsonrpc": request.jsonrpc,
        "method": request.method,
        "id": request.id
    }
    if request.params is not None:
        message_dict["params"] = request.params
    
    json_data = json.dumps(message_dict) + "\n"
    
    try:
        logger.debug(f"Sending request {request.id}: {json_data.strip()}")
        self._process.stdin.write(json_data.encode('utf-8'))
        await self._process.stdin.drain()
        
        # Wait for the specific response for this request
        try:
            response_dict = await asyncio.wait_for(
                future,
                timeout=self.request_timeout
            )
            
            # Parse response
            if "error" in response_dict and response_dict["error"] is not None:
                return MCPResponse(
                    jsonrpc=response_dict["jsonrpc"],
                    id=response_dict["id"],
                    error=response_dict["error"]
                )
            else:
                return MCPResponse(
                    jsonrpc=response_dict["jsonrpc"],
                    id=response_dict["id"],
                    result=response_dict.get("result")
                )
                
        except asyncio.TimeoutError:
            # Clean up on timeout
            async with self._request_lock:
                self._pending_requests.pop(request.id, None)
            raise RuntimeError(f"Request {request.id} timed out")
            
    except Exception as e:
        # Clean up on failure
        async with self._request_lock:
            self._pending_requests.pop(request.id, None)
        logger.error(f"Failed to send request {request.id}: {e}")
        raise RuntimeError(f"Failed to send request: {e}")
```

### Step 2.3: Add Concurrent Request Tracking
**File**: `watchgate/transport/stdio.py`

**Add these instance variables in `__init__`** (around line 77, after `self._last_request_id`):
```python
self._concurrent_request_count = 0
self._max_concurrent_requests = 100  # Default limit
```

**Update the `send_and_receive` method** to track concurrent requests:
```python
# Add at the beginning of send_and_receive, after connection check:
async with self._request_lock:
    if self._concurrent_request_count >= self._max_concurrent_requests:
        raise RuntimeError(f"Maximum concurrent requests ({self._max_concurrent_requests}) exceeded")
    self._concurrent_request_count += 1

# Add in the finally block at the end of send_and_receive:
finally:
    async with self._request_lock:
        self._concurrent_request_count -= 1
```

## Phase 3: Update MCPProxy (GREEN Phase - Part 2)

### Step 3.1: Update handle_request Method
**File**: `watchgate/proxy/server.py`

**Find lines 240-242** (in the handle_request method):
```python
# OLD CODE:
await self._upstream_transport.send_message(upstream_request)
response = await self._upstream_transport.receive_message()
logger.debug(f"Received response for request {request_id}")
```

**Replace with**:
```python
# NEW CODE:
# Use send_and_receive for proper request/response correlation
response_dict = await self._upstream_transport.send_and_receive(upstream_request)
logger.debug(f"Received response for request {request_id}")
response = response_dict  # The response is already an MCPResponse object
```

### Step 3.2: Add Concurrent Request Metrics
**File**: `watchgate/proxy/server.py`

**Add these instance variables in `__init__`** (around line 54, after `self._client_requests = 0`):
```python
self._concurrent_requests = 0
self._max_concurrent_observed = 0
```

**Add tracking in handle_request** (at the beginning, around line 175):
```python
# Add after self._client_requests += 1
self._concurrent_requests += 1
self._max_concurrent_observed = max(self._max_concurrent_observed, self._concurrent_requests)
```

**Add cleanup in handle_request** (in the finally block of the main try, add at line 303):
```python
finally:
    self._concurrent_requests -= 1
```

**You need to restructure the error handling**. Wrap the entire method body (after the running check) in try/finally:
```python
async def handle_request(self, request: MCPRequest) -> MCPResponse:
    if not self._is_running:
        raise RuntimeError("Proxy is not running")
    
    self._client_requests += 1
    self._concurrent_requests += 1
    self._max_concurrent_observed = max(self._max_concurrent_observed, self._concurrent_requests)
    
    try:
        # ... all the existing code ...
    finally:
        self._concurrent_requests -= 1
```

## Phase 4: Fix Mock Transport (GREEN Phase - Part 3)

### Step 4.1: Implement send_and_receive in MockTransport
**File**: `tests/mocks/transport.py`

**Add this method** (after the `receive_message` method):
```python
async def send_and_receive(self, request: MCPRequest) -> MCPResponse:
    """Send request and wait for its specific response."""
    if not self._connected:
        raise RuntimeError("Not connected")
    
    # Register pending request
    async with self._request_lock:
        future = asyncio.Future()
        self._pending_requests[request.id] = future
        self.active_requests += 1
        self.max_concurrent = max(self.max_concurrent, self.active_requests)
    
    # Queue request for processing
    await self._request_queue.put(request)
    
    try:
        # Wait for specific response
        response = await asyncio.wait_for(future, timeout=10.0)
        return response
    except asyncio.TimeoutError:
        raise RuntimeError(f"Request {request.id} timed out")
    finally:
        async with self._request_lock:
            self.active_requests -= 1
```

### Step 4.2: Fix Response Processing in MockTransport
**File**: `tests/mocks/transport.py`

**Update the `_process_requests` method** (around line 130):
```python
async def _process_requests(self):
    """Process requests and generate responses."""
    while self._connected:
        try:
            # Get next request
            request = await asyncio.wait_for(
                self._request_queue.get(),
                timeout=0.1
            )
            
            # Track request
            self.request_count += 1
            self.processed_requests.append({
                "id": request.id,
                "method": request.method,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Simulate processing delay
            if self.response_delay > 0:
                await asyncio.sleep(self.response_delay)
            
            # Generate response
            if self.response_handler:
                response = await self.response_handler(request)
            else:
                # Default response
                response = MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={"status": "ok", "echo": request.method}
                )
            
            # Deliver response to waiting future
            async with self._request_lock:
                if request.id in self._pending_requests:
                    future = self._pending_requests.pop(request.id)
                    if not future.done():
                        future.set_result(response)
                        
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in mock request processor: {e}")
```

## Phase 5: Run Tests and Fix Issues

### Step 5.1: Run the Concurrent Tests
```bash
pytest tests/integration/test_concurrent_requests.py -v
```

**Common Issues and Fixes**:

1. **If you get "AttributeError: 'dict' object has no attribute 'id'"**:
   - The response from send_and_receive should already be an MCPResponse object
   - Don't try to parse it again in MCPProxy

2. **If you get timeout errors**:
   - Check that the MockTransport._process_requests is running
   - Ensure futures are being resolved correctly

3. **If you get "Response for unknown request ID"**:
   - Make sure you're not popping from _pending_requests too early
   - The dispatcher should handle cleanup

### Step 5.2: Run ALL Tests
```bash
pytest tests/
```

**CRITICAL**: You MUST ensure ALL tests pass, not just the concurrent ones!

## Phase 6: Add Additional Tests (REFACTOR Phase)

### Step 6.1: Add Edge Case Tests
**File**: `tests/integration/test_concurrent_requests.py`

**Add this test** at the end of the TestConcurrentRequests class:
```python
@pytest.mark.asyncio
async def test_concurrent_request_limit(self, concurrent_test_config, temp_work_directory):
    """Test enforcement of maximum concurrent requests."""
    config_loader = ConfigLoader()
    config = config_loader.load_from_file(concurrent_test_config)
    
    # Create mock transport with very slow responses
    mock_transport = MockTransport(response_delay=10.0)
    mock_transport._max_concurrent_requests = 5  # Low limit for testing
    
    proxy = MCPProxy(
        config,
        config_directory=concurrent_test_config.parent,
        transport=mock_transport,
        stdio_server=AsyncMock()
    )
    await proxy.start()
    
    # Try to send more than the limit
    requests = []
    for i in range(10):
        request = MCPRequest(
            jsonrpc="2.0",
            method="test_method",
            id=f"limit_test_{i}",
            params={"index": i}
        )
        requests.append(proxy.handle_request(request))
    
    # Some should succeed, some should fail
    results = await asyncio.gather(*requests, return_exceptions=True)
    
    # Count successes and failures
    successes = sum(1 for r in results if not isinstance(r, Exception))
    failures = sum(1 for r in results if isinstance(r, Exception))
    
    assert successes <= 5  # At most the limit
    assert failures > 0    # Some should have failed
    
    await proxy.stop()
```

## Verification Checklist

Before declaring complete, verify:

1. **All concurrent tests pass**:
   ```bash
   pytest tests/integration/test_concurrent_requests.py -v
   ```
   Expected: 8 tests passed (7 original + 1 new)

2. **All existing tests still pass**:
   ```bash
   pytest tests/
   ```
   Expected: 888+ tests passed (no failures)

3. **Manual verification** - Create a test script:
   ```python
   # test_concurrent_manual.py
   import asyncio
   from watchgate.protocol.messages import MCPRequest
   
   async def test_concurrent():
       # Create 10 requests
       requests = []
       for i in range(10):
           req = MCPRequest(
               jsonrpc="2.0",
               method=f"test_{i}",
               id=f"req_{i}",
               params={}
           )
           requests.append(proxy.handle_request(req))
       
       # They should all complete
       responses = await asyncio.gather(*requests)
       assert len(responses) == 10
       print("Concurrent test passed!")
   ```

## Success Criteria

You are DONE when:
1. ✅ All tests in `test_concurrent_requests.py` pass
2. ✅ All existing tests continue to pass  
3. ✅ No memory leaks (mock transport cleans up)
4. ✅ Proper error handling for exceeded limits
5. ✅ Clear logging of concurrent behavior

## Debugging Tips

1. **Add debug logging**:
   ```python
   logger.debug(f"Concurrent requests: {self._concurrent_requests}")
   logger.debug(f"Pending requests: {list(self._pending_requests.keys())}")
   ```

2. **Check future states**:
   ```python
   print(f"Future done: {future.done()}, cancelled: {future.cancelled()}")
   ```

3. **Monitor the message flow**:
   ```python
   # In StdioTransport._route_response
   logger.info(f"Routing response for request {request_id}")
   ```

## DO NOT STOP until you see:
```
=================== 888 passed, 4 warnings in 45.32s ===================
```

Remember: Follow TDD strictly. If tests fail, fix the implementation. Do not modify tests to make them pass unless they have actual bugs.