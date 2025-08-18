# Yelp detect-secrets Integration Strategy

## Overview

detect-secrets is an open-source (Apache 2.0 licensed) enterprise-grade secret detection tool developed and battle-tested at Yelp. This document outlines our strategy for **immediately replacing** our homegrown secrets detection with detect-secrets before the v0.1.0 release.

## Current Status

- **Current Implementation**: Custom entropy + regex detection in `watchgate/plugins/security/secrets.py`
- **Limitations**: Limited secret patterns, basic entropy detection, manual pattern maintenance
- **Decision**: **IMMEDIATE REPLACEMENT** - Yelp's detect-secrets will replace our homegrown secrets detection

## Why detect-secrets?

### Advantages Over Current Implementation

1. **Battle-tested at Scale**: Used in production at Yelp for years
2. **Lightweight**: Only ~97KB package size (vs Presidio's 50MB+)
3. **Minimal Dependencies**: Pure Python, no binary dependencies
4. **Extensive Detectors**: 20+ built-in detector plugins
5. **Active Maintenance**: Regular updates and new detector additions
6. **Enterprise Features**: Audit workflows, baseline support, pre-commit integration

### Comparison with Other Tools

| Tool | Size | License | Strengths | Weaknesses |
|------|------|---------|-----------|------------|
| detect-secrets | ~97KB | Apache 2.0 | Lightweight, comprehensive | Python-only |
| TruffleHog | Go binary | AGPL 3.0 | 800+ patterns, verification | AGPL license, Go dependency |
| Gitleaks | Go binary | MIT | Fast, extensive rules | Go dependency |
| **Our Current** | 0KB | - | No dependencies | Limited patterns |

## Integration Approach

### Architecture Design

```python
class DetectSecretsPlugin(SecurityPlugin):
    """
    Secret detection powered by Yelp detect-secrets.
    
    Provides enterprise-grade secret detection with minimal dependencies.
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Initialize detect-secrets settings
        self.detectors = self._init_detectors(config)
        self.action = config.get("action", "block")
        self.custom_patterns = config.get("custom_patterns", [])
        
    def _init_detectors(self, config):
        """Initialize selected detectors based on configuration."""
        from detect_secrets.core import scan
        from detect_secrets.settings import default_settings
        
        # Configure which detectors to use
        enabled_detectors = config.get("detectors", [
            "AWSKeyDetector",
            "AzureStorageKeyDetector",
            "BasicAuthDetector",
            "CloudantDetector",
            "DiscordBotTokenDetector",
            "GitHubTokenDetector",
            "GitLabTokenDetector",
            "IbmCloudIamDetector",
            "JwtTokenDetector",
            "MailchimpDetector",
            "NpmDetector",
            "PrivateKeyDetector",
            "SendGridDetector",
            "SlackDetector",
            "StripeDetector",
            "TwilioKeyDetector",
        ])
        
        # Note: Can disable high-noise detectors
        if not config.get("include_entropy_detectors", False):
            # These can be noisy
            enabled_detectors = [d for d in enabled_detectors 
                                if "Entropy" not in d]
        
        return enabled_detectors
```

### Available Detectors

detect-secrets includes the following detector plugins:

#### Cloud Provider Secrets
- `AWSKeyDetector` - AWS Access Keys
- `AzureStorageKeyDetector` - Azure Storage Account Keys
- `IbmCloudIamDetector` - IBM Cloud IAM Keys
- `IbmCosHmacDetector` - IBM Cloud Object Storage HMAC

#### Version Control & CI/CD
- `GitHubTokenDetector` - GitHub Personal Access Tokens
- `GitLabTokenDetector` - GitLab Tokens
- `NpmDetector` - NPM Registry Tokens

#### Communication Platforms
- `SlackDetector` - Slack Webhooks and Tokens
- `DiscordBotTokenDetector` - Discord Bot Tokens
- `TwilioKeyDetector` - Twilio API Keys
- `SendGridDetector` - SendGrid API Keys
- `MailchimpDetector` - Mailchimp API Keys

#### Authentication & Encryption
- `BasicAuthDetector` - Basic Auth Credentials in URLs
- `JwtTokenDetector` - JSON Web Tokens
- `PrivateKeyDetector` - SSH/SSL Private Keys

#### Payment & Commerce
- `StripeDetector` - Stripe API Keys
- `SquareOAuthDetector` - Square OAuth Secrets
- `PayPalBraintreeAccessTokenDetector` - PayPal/Braintree Tokens

#### Database & Infrastructure
- `CloudantDetector` - Cloudant/CouchDB Credentials
- `ArtifactoryDetector` - Artifactory API Keys

#### Entropy-Based (Optional)
- `Base64HighEntropyString` - High entropy base64 strings
- `HexHighEntropyString` - High entropy hex strings
- `KeywordDetector` - Keyword-based detection (password=, key=, etc.)

### Configuration Schema

```yaml
# Minimal configuration (NO OLD "secrets" POLICY NAME)
plugins:
  security:
    - policy: "detect_secrets"  # NOT "secrets" - that's deleted
      config:
        action: "block"  # or "redact", "audit_only"
        
# Advanced configuration
plugins:
  security:
    - policy: "detect_secrets"  # Single consistent name
      config:
        action: "block"
        detectors:
          # Explicitly list which detectors to enable
          - AWSKeyDetector
          - GitHubTokenDetector
          - PrivateKeyDetector
          - JwtTokenDetector
        
        # Entropy detection settings
        include_entropy_detectors: false  # Default: false (too noisy)
        entropy_settings:
          base64_limit: 4.5
          hex_limit: 3.0
        
        # Keyword detector settings
        keyword_settings:
          keywords:
            - password
            - secret
            - key
            - token
            - api_key
        
        # Custom patterns (extend built-in detectors)
        custom_patterns:
          - name: "internal_api_key"
            pattern: "INT_API_[A-Z0-9]{32}"
          - name: "database_url"
            pattern: "postgres://[^@]+@[^/]+/\\w+"
        
        # Exemptions
        exemptions:
          paths:
            - "tests/*"
            - "docs/*"
          tools:
            - "read_file"  # Don't scan file reads
```

## Implementation Strategy

### Phase 1: Core Integration

```python
# watchgate/plugins/security/trusted/yelp_secrets.py

try:
    from detect_secrets import SecretsCollection
    from detect_secrets.core import scan
    from detect_secrets.settings import default_settings
    DETECT_SECRETS_AVAILABLE = True
except ImportError:
    DETECT_SECRETS_AVAILABLE = False

class DetectSecretsPlugin(SecurityPlugin):
    """Secret detection powered by Yelp detect-secrets."""
    
    __vendor__ = "Yelp"
    __library__ = "detect-secrets"
    __license__ = "Apache-2.0"
    
    def _scan_text(self, text: str) -> List[Dict]:
        """Scan text for secrets using detect-secrets."""
        from detect_secrets.core.scan import scan_line
        
        secrets = []
        for line_num, line in enumerate(text.split('\n'), 1):
            for detector in self.enabled_detectors:
                found_secrets = detector.analyze_line(
                    line, 
                    line_num,
                    filename="<input>"
                )
                secrets.extend(found_secrets)
        
        return secrets
```

### Phase 2: Custom Pattern Support

Add ability to define organization-specific patterns that work alongside detect-secrets built-in detectors.

### Phase 3: Baseline Support

Implement baseline functionality to track known secrets (useful for gradual rollout).

## Benefits

### Technical Benefits

1. **Comprehensive Coverage**: 20+ detector types out of the box
2. **Low False Positives**: Each detector is tuned for specific secret formats
3. **Flexible Configuration**: Enable/disable individual detectors
4. **Custom Patterns**: Extend with organization-specific patterns
5. **Verification Support**: Some detectors can verify if secrets are active
6. **Minimal Dependencies**: Pure Python, no binary dependencies

### Operational Benefits

1. **Enterprise Proven**: Battle-tested at Yelp
2. **Active Development**: Regular updates and new detectors
3. **Community**: Large user base, good issue support
4. **Documentation**: Comprehensive docs and examples
5. **Integration**: Pre-commit hooks, CI/CD support

## Trade-offs

### Pros
- Lightweight (~97KB)
- No binary dependencies
- Apache 2.0 license (permissive)
- Extensive detector library
- Minimal supply chain risk
- Easy to audit (pure Python)

### Cons
- Python-only (no other language support)
- No ML/NLP features (pattern-based only)
- Less extensive than TruffleHog (800+ patterns)
- No built-in remediation features

## Migration Strategy

### Compatibility Mapping

Map our current detection to detect-secrets detectors:

| Our Current | detect-secrets Equivalent |
|-------------|---------------------------|
| AWS Access Keys | AWSKeyDetector |
| GitHub Tokens | GitHubTokenDetector |
| Google API Keys | (Custom pattern needed) |
| JWT Tokens | JwtTokenDetector |
| SSH Private Keys | PrivateKeyDetector |
| Entropy Detection | Base64HighEntropyString |

### Immediate Replacement Plan

Since we haven't released v0.1.0 yet, we will **immediately replace** our homegrown secrets detection:

1. **Remove current implementation**: Delete `watchgate/plugins/security/secrets.py`
2. **Add detect-secrets plugin**: Create `watchgate/plugins/security/detect_secrets.py`
3. **Single policy name**: Only use `"detect_secrets"` (no aliases for old `"secrets"` name)
4. **No backward compatibility**: We're pre-release, clean break is fine

### Why Immediate Replacement?

- **Zero maintenance burden**: No more manually updating regex patterns
- **Enterprise credibility**: "Powered by Yelp detect-secrets"
- **Minimal risk**: Only 97KB dependency, pure Python
- **Better coverage**: 20+ detectors vs our handful of patterns
- **Pre-release timing**: No users to migrate

## Security Considerations

### Supply Chain Risk Assessment

#### Very Low Risk
- Pure Python (no binary components)
- Small codebase (~97KB)
- Apache 2.0 license
- Maintained by Yelp (reputable company)
- Easy to audit and understand
- No external API calls

#### Mitigation
- Pin to specific version
- Review updates before upgrading
- Monitor for security advisories

## Comparison with Current Implementation

| Feature | Current (secrets.py) | detect-secrets |
|---------|---------------------|----------------|
| Package Size | 0KB | ~97KB |
| Dependencies | None | Minimal |
| AWS Keys | ✅ Basic | ✅ Advanced |
| GitHub Tokens | ✅ Basic | ✅ Multiple types |
| Google API Keys | ✅ Basic | ❌ Need custom |
| JWT | ✅ Basic | ✅ Advanced |
| SSH Keys | ✅ Basic | ✅ Comprehensive |
| Entropy | ✅ Basic | ✅ Configurable |
| Cloud Providers | ❌ | ✅ Multiple |
| Slack/Discord | ❌ | ✅ |
| Payment (Stripe) | ❌ | ✅ |
| Custom Patterns | ✅ | ✅ |
| Verification | ❌ | ⚠️ Some detectors |
| Baseline Support | ❌ | ✅ |

## Installation & Usage

### Installation

```bash
# Basic installation
pip install watchgate[detect-secrets]

# Or manually
pip install detect-secrets
```

### Example Usage

```python
# Quick detection
from detect_secrets.core.scan import scan_line

line = "aws_access_key_id=AKIAIOSFODNN7EXAMPLE"
secrets = scan_line(line)
if secrets:
    print(f"Found secret: {secrets}")

# With specific detectors
from detect_secrets.plugins.aws import AWSKeyDetector

detector = AWSKeyDetector()
result = detector.analyze_line(line, line_number=1)
```

## Decision: APPROVED FOR IMMEDIATE IMPLEMENTATION

**detect-secrets will immediately replace our homegrown secrets detection** before v0.1.0 release.

### Rationale for Immediate Replacement

1. **Minimal risk**: Only 97KB, pure Python, Apache 2.0 license
2. **Massive improvement**: 20+ detectors vs our ~5 patterns
3. **Zero users affected**: We're pre-release
4. **Reduced liability**: Outsource security to Yelp's expertise
5. **Easy implementation**: Simple Python API, good documentation

## Implementation Timeline

**TARGET: Before v0.1.0 Release**

1. **Immediate**: Create detect-secrets adapter plugin
2. **Replace**: Remove `secrets.py`, add `detect_secrets.py`
3. **Test**: Ensure all existing tests pass with new implementation
4. **Document**: Update user docs to mention "Powered by Yelp detect-secrets"

### Priority Order

1. **detect-secrets** (THIS): Immediate replacement - tiny dependency, huge benefit
2. **Presidio** (NEXT): Also replace before v0.1.0 - larger dependency but acceptable

## References

- [detect-secrets GitHub](https://github.com/Yelp/detect-secrets)
- [detect-secrets PyPI](https://pypi.org/project/detect-secrets/)
- [detect-secrets Documentation](https://github.com/Yelp/detect-secrets#usage)
- [Yelp Engineering Blog on detect-secrets](https://engineeringblog.yelp.com/)