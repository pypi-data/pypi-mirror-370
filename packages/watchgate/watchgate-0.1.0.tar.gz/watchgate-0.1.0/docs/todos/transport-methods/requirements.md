# Transport Methods Technical Requirements

## Overview

This document defines technical requirements for implementing network transport methods in Watchgate's auditing plugins. Following the log format separation architecture where each format has its own dedicated plugin (CefAuditingPlugin, SyslogAuditingPlugin, JsonAuditingPlugin, etc.), these transport methods enable each plugin to deliver audit logs and security events to external systems for compliance, monitoring, and analysis.

**Key Principle**: Watchgate auditing plugins should support multiple transport methods to integrate with existing enterprise infrastructure while maintaining security and performance standards. Transport capabilities are implemented in the BaseAuditingPlugin and inherited by all format-specific plugins.

## Transport Method Categories

### Priority Order (Based on Financial Services Requirements)

#### Priority 1: Syslog with Full Transport Support
**Primary Use Case**: Centralized logging and SIEM integration
**Protocol**: RFC 5424/3164 over UDP/TCP/TLS (ports 514/6514)
**Rationale**: Syslog is designed for network transport; file-only defeats its purpose
**Formats**: SyslogAuditingPlugin (native), all others via syslog bridge

#### Priority 2: CEF/LEEF Network Transport  
**Primary Use Case**: Direct SIEM integration (Splunk, QRadar, ArcSight)
**Protocol**: TCP/TLS to SIEM collectors
**Rationale**: CEF/LEEF are primarily used for SIEM integration requiring network delivery
**Formats**: CefAuditingPlugin, future LeefAuditingPlugin

#### Priority 3: Apache Kafka Integration
**Primary Use Case**: High-volume transaction logging and event streaming
**Protocol**: Kafka producer API with SASL/SSL
**Rationale**: Enterprise event streaming for real-time analytics
**Formats**: All plugins via JSON serialization

#### Priority 4: HTTPS API Endpoints
**Primary Use Case**: Modern GRC platform and cloud service integration
**Protocol**: HTTP/1.1 and HTTP/2 over TLS (REST/Webhook)
**Rationale**: Modern platforms expect JSON over HTTPS/REST APIs
**Formats**: JsonAuditingPlugin (native), all others via JSON conversion

#### Priority 5: Message Queue Support
**Primary Use Case**: Complex routing and reliable delivery
**Protocol**: AMQP 0-9-1 (RabbitMQ, Azure Service Bus)
**Rationale**: Enterprise message bus integration
**Formats**: All plugins

#### Priority 6: Future Format Transport
**Planned Formats**:
- **GELF**: UDP/TCP/TLS to Graylog (port 12201)
- **OpenTelemetry**: gRPC/HTTP to collectors
- **File-Based**: Local/network filesystem (already implemented)

## Implementation Architecture

### Plugin Integration Model

Transport methods will be implemented in the **BaseAuditingPlugin** class and inherited by all format-specific plugins:

```python
# Enhanced BaseAuditingPlugin with transport support
from watchgate.plugins.auditing.base import BaseAuditingPlugin

class BaseAuditingPlugin(AuditingPlugin, PathResolvablePlugin):
    """Base class with shared transport functionality for all auditing plugins."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Existing file-based configuration
        self.output_file = config.get('output_file', 'watchgate.log')
        
        # New transport configuration
        self.transport_config = config.get('transport', {})
        self.transport_type = self.transport_config.get('type', 'file')
        self.transport_handler = self._create_transport_handler()
    
    def _create_transport_handler(self) -> TransportHandler:
        """Factory method for transport handlers"""
        transport_map = {
            'file': FileTransportHandler,
            'udp': UDPTransportHandler,
            'tcp': TCPTransportHandler,
            'tls': TLSTransportHandler,
            'kafka': KafkaTransportHandler,
            'https': HTTPSTransportHandler,
            'amqp': AMQPTransportHandler,
            'multi': MultiDestinationHandler
        }
        
        handler_class = transport_map.get(self.transport_type)
        if not handler_class:
            raise ValueError(f"Unsupported transport type: {self.transport_type}")
        
        return handler_class(self.transport_config)

# Example format-specific plugin inheriting transport
class SyslogAuditingPlugin(BaseAuditingPlugin):
    """Syslog format plugin with native network transport support."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Syslog-specific configuration
        self.rfc_format = config.get('rfc_format', '5424')
        self.facility = config.get('facility', 16)
```

### Transport Handler Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class TransportHandler(ABC):
    """Abstract base class for transport handlers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.is_connected = False
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to transport destination"""
        pass
    
    @abstractmethod
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send formatted message via transport"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Clean up transport connection"""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """Check transport health status"""
        pass
```

## Transport Method Specifications

### 1. TLS-Encrypted Syslog Transport

#### Technical Requirements
- **Protocol**: RFC 5424 over TLS 1.3 (minimum TLS 1.2)
- **Default Port**: 6514
- **Connection**: Persistent TCP connection with automatic reconnection
- **Reliability**: Store-and-forward with local buffering

#### Security Requirements
- **Encryption**: TLS 1.3 with strong cipher suites
- **Authentication**: Client certificate authentication
- **Validation**: Server certificate validation with custom CA support
- **Integrity**: Message-level checksums

#### Implementation Details
```python
class SyslogTLSTransportHandler(TransportHandler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.server_host = config['server_host']
        self.server_port = config.get('server_port', 6514)
        self.client_cert = config.get('client_cert')
        self.client_key = config.get('client_key')
        self.ca_cert = config.get('ca_cert')
        self.buffer_size = config.get('buffer_size', 1024)
        self.message_buffer = []
        self.ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with security configuration"""
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        if self.ca_cert:
            context.load_verify_locations(cafile=self.ca_cert)
        
        if self.client_cert and self.client_key:
            context.load_cert_chain(self.client_cert, self.client_key)
        
        return context
    
    async def connect(self) -> None:
        """Establish TLS connection to syslog server"""
        try:
            self.connection = await asyncio.open_connection(
                self.server_host, 
                self.server_port,
                ssl=self.ssl_context
            )
            self.is_connected = True
            await self._flush_buffer()
        except Exception as e:
            self.is_connected = False
            raise TransportError(f"Failed to connect to syslog server: {e}")
    
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send syslog message with TLS encryption"""
        if not self.is_connected:
            self.message_buffer.append(message)
            if len(self.message_buffer) > self.buffer_size:
                self.message_buffer.pop(0)  # Remove oldest message
            await self._attempt_reconnect()
            return
        
        try:
            writer = self.connection[1]
            writer.write(f"{message}\n".encode('utf-8'))
            await writer.drain()
        except Exception as e:
            self.is_connected = False
            self.message_buffer.append(message)
            raise TransportError(f"Failed to send syslog message: {e}")
```

#### Configuration Schema
```yaml
plugins:
  auditing:
    - policy: "syslog_auditing"
      config:
        transport:
          type: "syslog_tls"
          server_host: "log.company.com"
          server_port: 6514
          client_cert: "/path/to/client.crt"
          client_key: "/path/to/client.key"
          ca_cert: "/path/to/ca.crt"
          buffer_size: 1024
          reconnect_interval: 30
          message_timeout: 5
```

#### Performance Characteristics
- **Throughput**: 10,000+ messages/second
- **Latency**: <10ms per message
- **Buffer Capacity**: 1,000 messages (configurable)
- **Reconnection**: Exponential backoff with max 60s interval

### 2. Apache Kafka Integration

#### Technical Requirements
- **Protocol**: Kafka producer API with SASL/SSL
- **Serialization**: JSON with optional schema registry
- **Partitioning**: Configurable partitioning strategy
- **Reliability**: At-least-once delivery with idempotent producer

#### Security Requirements
- **Authentication**: SASL/PLAIN, SASL/SCRAM, or mTLS
- **Authorization**: Kafka ACLs for topic access
- **Encryption**: SSL/TLS for data in transit
- **Schema**: Schema registry integration for data governance

#### Implementation Details
```python
class KafkaTransportHandler(TransportHandler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bootstrap_servers = config['bootstrap_servers']
        self.topic = config['topic']
        self.security_protocol = config.get('security_protocol', 'SSL')
        self.sasl_mechanism = config.get('sasl_mechanism', 'PLAIN')
        self.sasl_username = config.get('sasl_username')
        self.sasl_password = config.get('sasl_password')
        self.ssl_cafile = config.get('ssl_cafile')
        self.ssl_certfile = config.get('ssl_certfile')
        self.ssl_keyfile = config.get('ssl_keyfile')
        self.partition_key = config.get('partition_key', 'request_id')
        self.producer = None
    
    async def connect(self) -> None:
        """Initialize Kafka producer"""
        # Note: Using kafka-python-ng for async support
        producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
            'enable_idempotence': True,
            'acks': 'all',
            'retries': 3,
            'max_in_flight_requests_per_connection': 5,
            'compression_type': 'gzip'
        }
        
        if self.security_protocol in ['SASL_SSL', 'SASL_PLAINTEXT']:
            producer_config.update({
                'sasl_mechanism': self.sasl_mechanism,
                'sasl_plain_username': self.sasl_username,
                'sasl_plain_password': self.sasl_password
            })
        
        if self.security_protocol in ['SSL', 'SASL_SSL']:
            producer_config.update({
                'ssl_cafile': self.ssl_cafile,
                'ssl_certfile': self.ssl_certfile,
                'ssl_keyfile': self.ssl_keyfile
            })
        
        try:
            # Import here to avoid dependency in base class
            from kafka import KafkaProducer
            self.producer = KafkaProducer(**producer_config)
            self.is_connected = True
        except Exception as e:
            raise TransportError(f"Failed to initialize Kafka producer: {e}")
    
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send message to Kafka topic"""
        if not self.is_connected:
            raise TransportError("Kafka producer not connected")
        
        try:
            # Determine partition key
            partition_key = None
            if metadata and self.partition_key in metadata:
                partition_key = metadata[self.partition_key].encode('utf-8')
            
            # Send message
            future = self.producer.send(
                self.topic,
                value=message.encode('utf-8'),
                key=partition_key
            )
            
            # Wait for send completion (with timeout)
            record_metadata = future.get(timeout=10)
            
        except Exception as e:
            raise TransportError(f"Failed to send Kafka message: {e}")
```

#### Configuration Schema
```yaml
plugins:
  auditing:
    - policy: "json_auditing"  # or any format plugin
      config:
        transport:
          type: "kafka"
          bootstrap_servers: "kafka-1:9092,kafka-2:9092,kafka-3:9092"
          topic: "watchgate-audit-logs"
          security_protocol: "SASL_SSL"
          sasl_mechanism: "SCRAM-SHA-256"
          sasl_username: "watchgate"
          sasl_password: "${KAFKA_PASSWORD}"
          ssl_cafile: "/path/to/ca.pem"
          partition_key: "request_id"
          compression_type: "gzip"
```

#### Performance Characteristics
- **Throughput**: 100,000+ messages/second
- **Latency**: <5ms per message
- **Batching**: Configurable batch size and linger time
- **Ordering**: Per-partition ordering guarantees

### 3. HTTPS API Endpoints

#### Technical Requirements
- **Protocol**: HTTP/1.1 and HTTP/2 over TLS
- **Methods**: POST for log submission
- **Content-Type**: application/json, application/x-ndjson
- **Authentication**: Bearer tokens, API keys, or mTLS
- **Reliability**: Retry logic with exponential backoff

#### Security Requirements
- **Transport Security**: TLS 1.3 with certificate pinning
- **Authentication**: OAuth 2.0, API keys, or client certificates
- **Authorization**: Role-based access control
- **Rate Limiting**: Configurable rate limits per endpoint

#### Implementation Details
```python
class HTTPSTransportHandler(TransportHandler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoint_url = config['endpoint_url']
        self.auth_type = config.get('auth_type', 'bearer')
        self.auth_token = config.get('auth_token')
        self.api_key = config.get('api_key')
        self.client_cert = config.get('client_cert')
        self.client_key = config.get('client_key')
        self.ca_cert = config.get('ca_cert')
        self.timeout = config.get('timeout', 30)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 1)
        self.session = None
    
    async def connect(self) -> None:
        """Initialize HTTP session"""
        import aiohttp
        
        # Create SSL context
        ssl_context = None
        if self.ca_cert or self.client_cert:
            ssl_context = ssl.create_default_context()
            if self.ca_cert:
                ssl_context.load_verify_locations(cafile=self.ca_cert)
            if self.client_cert and self.client_key:
                ssl_context.load_cert_chain(self.client_cert, self.client_key)
        
        # Create session with timeout
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector
        )
        
        self.is_connected = True
    
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send message via HTTPS POST"""
        if not self.is_connected:
            raise TransportError("HTTPS session not connected")
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'Watchgate/{get_watchgate_version()}'
        }
        
        # Add authentication headers
        if self.auth_type == 'bearer' and self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        elif self.auth_type == 'api_key' and self.api_key:
            headers['X-API-Key'] = self.api_key
        
        # Prepare payload
        payload = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': 'watchgate',
            'message': message,
            'metadata': metadata or {}
        }
        
        # Send with retry logic
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                async with self.session.post(
                    self.endpoint_url,
                    json=payload,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    return
                    
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    
        raise TransportError(f"Failed to send HTTPS message after {self.retry_attempts} attempts: {last_exception}")
```

#### Configuration Schema
```yaml
plugins:
  auditing:
    - policy: "json_auditing"
      config:
        transport:
          type: "https"
          endpoint_url: "https://api.compliance.com/v1/logs"
          auth_type: "bearer"
          auth_token: "${COMPLIANCE_API_TOKEN}"
          timeout: 30
          retry_attempts: 3
          retry_delay: 1
          ca_cert: "/path/to/ca.pem"
```

#### Performance Characteristics
- **Throughput**: 1,000+ messages/second
- **Latency**: <100ms per message
- **Connection Pooling**: Persistent connections
- **Compression**: gzip/deflate support

### 4. Message Queue Support (AMQP)

#### Technical Requirements
- **Protocol**: AMQP 0-9-1 (RabbitMQ, Azure Service Bus)
- **Exchange Types**: Direct, topic, fanout, headers
- **Routing**: Configurable routing keys
- **Reliability**: Persistent messages with acknowledgments

#### Security Requirements
- **Authentication**: Username/password or certificate-based
- **Authorization**: Queue and exchange permissions
- **Encryption**: TLS for connections
- **Message Security**: Optional message-level encryption

#### Implementation Details
```python
class AMQPTransportHandler(TransportHandler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection_url = config['connection_url']
        self.exchange_name = config['exchange_name']
        self.exchange_type = config.get('exchange_type', 'direct')
        self.routing_key = config.get('routing_key', 'watchgate.audit')
        self.queue_name = config.get('queue_name', 'watchgate-audit-queue')
        self.durable = config.get('durable', True)
        self.persistent = config.get('persistent', True)
        self.connection = None
        self.channel = None
    
    async def connect(self) -> None:
        """Establish AMQP connection"""
        try:
            # Using aio-pika for async AMQP
            import aio_pika
            
            self.connection = await aio_pika.connect_robust(
                self.connection_url,
                heartbeat=600  # 10 minutes
            )
            
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)
            
            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name,
                type=aio_pika.ExchangeType(self.exchange_type),
                durable=self.durable
            )
            
            # Declare queue
            self.queue = await self.channel.declare_queue(
                self.queue_name,
                durable=self.durable
            )
            
            # Bind queue to exchange
            await self.queue.bind(self.exchange, routing_key=self.routing_key)
            
            self.is_connected = True
            
        except Exception as e:
            raise TransportError(f"Failed to connect to AMQP broker: {e}")
    
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Send message via AMQP"""
        if not self.is_connected:
            raise TransportError("AMQP connection not established")
        
        try:
            import aio_pika
            
            # Prepare message
            amqp_message = aio_pika.Message(
                message.encode('utf-8'),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT if self.persistent else aio_pika.DeliveryMode.NOT_PERSISTENT,
                timestamp=datetime.utcnow(),
                headers=metadata or {}
            )
            
            # Send message
            await self.exchange.publish(
                amqp_message,
                routing_key=self.routing_key
            )
            
        except Exception as e:
            raise TransportError(f"Failed to send AMQP message: {e}")
```

#### Configuration Schema
```yaml
plugins:
  auditing:
    - policy: "json_auditing"  # or any format plugin
      config:
        transport:
          type: "amqp"
          connection_url: "amqp://user:pass@rabbitmq.company.com:5672/"
          exchange_name: "watchgate-audit"
          exchange_type: "topic"
          routing_key: "watchgate.audit.${SERVER_NAME}"
          queue_name: "watchgate-audit-queue"
          durable: true
          persistent: true
```

#### Performance Characteristics
- **Throughput**: 10,000+ messages/second
- **Latency**: <10ms per message
- **Reliability**: Message persistence and acknowledgments
- **Ordering**: FIFO within queues

### 5. File-Based Transport

#### Technical Requirements
- **Formats**: CSV, JSON Lines, custom delimited
- **Rotation**: Size-based, time-based, or manual
- **Compression**: gzip, bzip2, xz support
- **Locations**: Local filesystem or network mounts

#### Security Requirements
- **File Permissions**: Restrictive permissions (600/640)
- **Path Validation**: Prevent directory traversal
- **Encryption**: Optional at-rest encryption
- **Integrity**: File checksums and validation

#### Implementation Details
```python
class FileTransportHandler(TransportHandler):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.output_file = config['output_file']
        self.format = config.get('format', 'csv')
        self.rotation_size = config.get('rotation_size', 100 * 1024 * 1024)  # 100MB
        self.rotation_time = config.get('rotation_time', 'daily')
        self.compression = config.get('compression', None)
        self.permissions = config.get('permissions', 0o600)
        self.file_handle = None
        self.writer = None
    
    async def connect(self) -> None:
        """Open file for writing"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            # Open file with appropriate mode
            if self.compression == 'gzip':
                import gzip
                self.file_handle = gzip.open(self.output_file, 'at', encoding='utf-8')
            elif self.compression == 'bzip2':
                import bz2
                self.file_handle = bz2.open(self.output_file, 'at', encoding='utf-8')
            else:
                self.file_handle = open(self.output_file, 'a', encoding='utf-8')
            
            # Set file permissions
            os.chmod(self.output_file, self.permissions)
            
            # Initialize CSV writer if needed
            if self.format == 'csv':
                import csv
                self.writer = csv.writer(self.file_handle)
                
                # Write header if file is new
                if os.path.getsize(self.output_file) == 0:
                    self.writer.writerow(['timestamp', 'level', 'event_type', 'message', 'metadata'])
            
            self.is_connected = True
            
        except Exception as e:
            raise TransportError(f"Failed to open file for writing: {e}")
    
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Write message to file"""
        if not self.is_connected:
            raise TransportError("File not open for writing")
        
        try:
            if self.format == 'csv':
                # Parse message for CSV format
                timestamp = datetime.utcnow().isoformat() + 'Z'
                level = metadata.get('level', 'INFO') if metadata else 'INFO'
                event_type = metadata.get('event_type', 'UNKNOWN') if metadata else 'UNKNOWN'
                metadata_str = json.dumps(metadata) if metadata else '{}'
                
                self.writer.writerow([timestamp, level, event_type, message, metadata_str])
            else:
                # Write as-is for other formats
                self.file_handle.write(f"{message}\n")
            
            self.file_handle.flush()
            
            # Check for rotation
            await self._check_rotation()
            
        except Exception as e:
            raise TransportError(f"Failed to write to file: {e}")
    
    async def _check_rotation(self) -> None:
        """Check if file rotation is needed"""
        if self.rotation_size and os.path.getsize(self.output_file) > self.rotation_size:
            await self._rotate_file()
    
    async def _rotate_file(self) -> None:
        """Rotate log file"""
        try:
            self.file_handle.close()
            
            # Generate rotated filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            rotated_name = f"{self.output_file}.{timestamp}"
            
            # Rename current file
            os.rename(self.output_file, rotated_name)
            
            # Compress rotated file if needed
            if self.compression:
                await self._compress_file(rotated_name)
            
            # Reopen file
            await self.connect()
            
        except Exception as e:
            raise TransportError(f"Failed to rotate file: {e}")
```

#### Configuration Schema
```yaml
plugins:
  auditing:
    - policy: "csv_auditing"
      config:
        transport:
          type: "file"
          output_file: "/var/log/watchgate/audit.csv"
          rotation_size: 104857600  # 100MB
          rotation_time: "daily"
          compression: "gzip"
          permissions: 0o640
```

#### Performance Characteristics
- **Throughput**: 50,000+ messages/second
- **Latency**: <1ms per message
- **Storage**: Configurable compression ratios
- **Reliability**: Filesystem-dependent

## Integration Patterns

### 1. Enterprise SIEM Integration

**Pattern**: Transport → SIEM → Analysis → Alerting

```yaml
# Splunk Integration via CEF
plugins:
  auditing:
    - policy: "cef_auditing"
      config:
        transport:
          type: "tls"
          server_host: "splunk-hec.company.com"
          server_port: 6514

# QRadar Integration via LEEF (future)
plugins:
  auditing:
    - policy: "leef_auditing"  # Future plugin
      config:
        transport:
          type: "tls"
          server_host: "qradar.company.com"
          server_port: 6514
```

### 2. Cloud-Native Observability

**Pattern**: Transport → Metrics/Logs → Dashboards → Alerts

```yaml
# Kafka + OpenTelemetry
transport:
  type: "kafka"
  bootstrap_servers: "kafka.observability.com:9092"
  topic: "watchgate-telemetry"
  format: "otel"  # OpenTelemetry format

# Graylog Integration
transport:
  type: "https"
  endpoint_url: "https://graylog.company.com/gelf"
  format: "gelf"  # Graylog Extended Log Format
```

### 3. Compliance Data Lake

**Pattern**: Transport → Data Lake → Analytics → Reporting

```yaml
# AWS S3 via HTTPS
transport:
  type: "https"
  endpoint_url: "https://s3.amazonaws.com/compliance-bucket/watchgate/"
  auth_type: "aws_iam"
  format: "json"
  compression: "gzip"
```

### 4. Multi-Destination Routing

**Pattern**: Single Source → Multiple Destinations

```yaml
# Multiple transport configurations
plugins:
  auditing:
    - policy: "json_auditing"  # or any format plugin
      config:
        transport:
          type: "multi"
          destinations:
            - type: "syslog_tls"
              server_host: "primary-siem.company.com"
              server_port: 6514
            - type: "kafka"
              bootstrap_servers: "kafka.analytics.com:9092"
              topic: "watchgate-audit"
            - type: "file"
              output_file: "/backup/audit.log"
              compression: "gzip"
```

## Transport Selection Guide

| Format Plugin | Primary Use Case | Recommended Transport | Fallback |
|--------------|------------------|----------------------|----------|
| SyslogAuditingPlugin | Centralized logging | TLS (port 6514) | TCP/UDP |
| CefAuditingPlugin | SIEM integration | TLS to SIEM | Syslog TLS |
| JsonAuditingPlugin | API/GRC integration | HTTPS POST | File |
| CsvAuditingPlugin | Compliance reports | File | N/A |
| LineAuditingPlugin | Human reading | File | N/A |
| DebugAuditingPlugin | Troubleshooting | File | N/A |
| GelfAuditingPlugin* | Graylog | UDP (port 12201) | TCP |
| OtelAuditingPlugin* | Observability | gRPC | HTTP |
| LeefAuditingPlugin* | QRadar | TLS | Syslog TLS |

*Future plugins to be implemented

## Error Handling and Reliability

### Transport Error Hierarchy

```python
class TransportError(Exception):
    """Base transport error"""
    pass

class ConnectionError(TransportError):
    """Connection-related errors"""
    pass

class AuthenticationError(TransportError):
    """Authentication failures"""
    pass

class MessageFormatError(TransportError):
    """Message formatting errors"""
    pass

class DeliveryError(TransportError):
    """Message delivery failures"""
    pass
```

### Reliability Patterns

#### 1. Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise TransportError("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

#### 2. Dead Letter Queue Pattern
```python
class DeadLetterQueue:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.messages = []
        self.lock = asyncio.Lock()
    
    async def add_message(self, message: str, metadata: Dict[str, Any]):
        """Add failed message to dead letter queue"""
        async with self.lock:
            if len(self.messages) >= self.max_size:
                self.messages.pop(0)  # Remove oldest message
            
            self.messages.append({
                'message': message,
                'metadata': metadata,
                'timestamp': datetime.utcnow(),
                'attempts': 1
            })
    
    async def retry_messages(self, transport_handler: TransportHandler):
        """Retry messages in dead letter queue"""
        async with self.lock:
            retry_messages = []
            for msg in self.messages:
                try:
                    await transport_handler.send(msg['message'], msg['metadata'])
                    # Success - don't add to retry list
                except Exception:
                    msg['attempts'] += 1
                    if msg['attempts'] < 3:  # Max 3 attempts
                        retry_messages.append(msg)
            
            self.messages = retry_messages
```

## Performance Optimization

### 1. Batching Strategy
```python
class BatchingTransportHandler:
    def __init__(self, underlying_handler: TransportHandler, batch_size: int = 100, flush_interval: int = 5):
        self.underlying_handler = underlying_handler
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.message_batch = []
        self.last_flush = time.time()
        self.lock = asyncio.Lock()
    
    async def send(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add message to batch and send when full"""
        async with self.lock:
            self.message_batch.append((message, metadata))
            
            # Send batch if full or flush interval exceeded
            if (len(self.message_batch) >= self.batch_size or 
                time.time() - self.last_flush > self.flush_interval):
                await self._flush_batch()
    
    async def _flush_batch(self):
        """Send accumulated batch"""
        if not self.message_batch:
            return
        
        batch = self.message_batch
        self.message_batch = []
        self.last_flush = time.time()
        
        try:
            # Send batch to underlying handler
            await self.underlying_handler.send_batch(batch)
        except Exception as e:
            # Handle batch failure
            raise TransportError(f"Batch send failed: {e}")
```

### 2. Connection Pooling
```python
class ConnectionPool:
    def __init__(self, transport_class: Type[TransportHandler], config: Dict[str, Any], pool_size: int = 10):
        self.transport_class = transport_class
        self.config = config
        self.pool_size = pool_size
        self.connections = []
        self.available_connections = asyncio.Queue()
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            connection = self.transport_class(self.config)
            await connection.connect()
            self.connections.append(connection)
            await self.available_connections.put(connection)
    
    async def get_connection(self) -> TransportHandler:
        """Get connection from pool"""
        return await self.available_connections.get()
    
    async def return_connection(self, connection: TransportHandler):
        """Return connection to pool"""
        if connection.is_healthy():
            await self.available_connections.put(connection)
        else:
            # Replace unhealthy connection
            async with self.lock:
                try:
                    new_connection = self.transport_class(self.config)
                    await new_connection.connect()
                    await self.available_connections.put(new_connection)
                except Exception:
                    # Log connection replacement failure
                    pass
```

## Security Considerations

### 1. Credential Management
- **Environment Variables**: Use environment variables for secrets
- **Key Rotation**: Support credential rotation without restart
- **Encryption**: Encrypt credentials at rest
- **Audit**: Log credential usage (without values)

### 2. Network Security
- **TLS Configuration**: Enforce strong TLS versions and cipher suites
- **Certificate Validation**: Validate server certificates
- **Connection Limits**: Implement connection rate limiting
- **Firewall Rules**: Document required network access

### 3. Data Protection
- **PII Filtering**: Apply PII filters before transport
- **Message Encryption**: Optional message-level encryption
- **Compression**: Secure compression algorithms
- **Checksums**: Message integrity verification

## Testing Strategy

### 1. Unit Tests
- Transport handler initialization
- Message formatting and sending
- Error handling and recovery
- Configuration validation

### 2. Integration Tests
- End-to-end message delivery
- Authentication and authorization
- Connection failure scenarios
- Performance under load

### 3. Security Tests
- TLS configuration validation
- Authentication bypass attempts
- Message tampering detection
- Credential exposure prevention

### 4. Load Tests
- High-volume message sending
- Connection pool exhaustion
- Memory usage under load
- Latency measurement

## Implementation Priority

### Phase 1: Core Transport Framework (Week 1-2)
- Abstract TransportHandler interface
- Basic error handling and logging
- Configuration schema design
- File transport implementation (reference)

### Phase 2: Priority Transports (Week 3-6)
- TLS-encrypted syslog transport
- Kafka integration
- HTTPS API endpoint support
- Basic reliability patterns

### Phase 3: Advanced Features (Week 7-10)
- AMQP message queue support
- Multi-destination routing
- Circuit breaker implementation
- Dead letter queue handling

### Phase 4: Performance and Security (Week 11-12)
- Batching and connection pooling
- Comprehensive security testing
- Performance optimization
- Documentation and examples

## Success Metrics

### Functionality
- **Transport Coverage**: 5 transport methods implemented
- **Format Support**: All log formats work with all transports
- **Configuration**: Zero-config defaults with full customization
- **Reliability**: >99.9% message delivery success rate

### Performance
- **Throughput**: Meets or exceeds specifications per transport
- **Latency**: <100ms end-to-end for most transports
- **Resource Usage**: <100MB memory per transport handler
- **Scalability**: Linear performance scaling with load

### Security
- **Encryption**: All network transports use TLS 1.2+
- **Authentication**: All transport methods support authentication
- **Data Protection**: PII filtering works with all transports
- **Audit**: Complete audit trail for all transport operations

## Risk Assessment

### High Risk
- **Complex Integration**: Multiple transport protocols and formats
- **Security Vulnerabilities**: Network protocols and authentication
- **Performance Impact**: Additional overhead on audit logging
- **Operational Complexity**: Multiple failure modes and recovery

### Medium Risk
- **Dependency Management**: External libraries for transport protocols
- **Configuration Complexity**: Many options and combinations
- **Testing Coverage**: Complex integration scenarios
- **Documentation**: Comprehensive configuration examples

### Low Risk
- **Backward Compatibility**: New features don't break existing functionality
- **Resource Consumption**: Well-defined resource limits
- **Monitoring**: Built-in health checks and metrics
- **Maintenance**: Modular design for easy updates

## Acceptance Criteria

### Core Framework
- [ ] TransportHandler interface implemented and documented
- [ ] Error handling hierarchy defined and tested
- [ ] Configuration schema supports all transport methods
- [ ] Transport integration completed in BaseAuditingPlugin
- [ ] All format-specific plugins inherit transport capabilities

### Transport Implementations
- [ ] TLS-encrypted syslog transport with certificate authentication
- [ ] Kafka integration with SASL/SSL support
- [ ] HTTPS API endpoint with OAuth 2.0 authentication
- [ ] AMQP message queue with persistent delivery
- [ ] Enhanced file transport with CSV format and rotation

### Reliability Features
- [ ] Circuit breaker pattern implemented
- [ ] Dead letter queue for failed messages
- [ ] Automatic reconnection with exponential backoff
- [ ] Multi-destination routing support

### Security Features
- [ ] TLS 1.2+ enforcement for all network transports
- [ ] Certificate validation and pinning
- [ ] Credential management with environment variables
- [ ] PII filtering integration with all transports

### Performance Features
- [ ] Batching support for high-throughput scenarios
- [ ] Connection pooling for HTTP/HTTPS transports
- [ ] Asynchronous I/O for all transport methods
- [ ] Configurable buffering and timeouts

### Testing and Documentation
- [ ] Unit tests for all transport handlers (>90% coverage)
- [ ] Integration tests with real transport endpoints
- [ ] Security tests for authentication and encryption
- [ ] Performance benchmarks for all transport methods
- [ ] Configuration examples for common use cases
- [ ] Troubleshooting guide for transport issues

This comprehensive transport methods implementation will enable Watchgate to integrate with enterprise infrastructure while maintaining security, performance, and reliability standards required for compliance and monitoring use cases.