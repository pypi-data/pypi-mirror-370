# Microsoft Presidio Integration Strategy

## Overview

Microsoft Presidio is an open-source (MIT licensed) framework for PII detection and anonymization. This document outlines our strategy for **immediately replacing** our homegrown PII detection with Presidio before the v0.1.0 release.

## Current Status

- **Current Implementation**: Custom regex-based PII detection in `watchgate/plugins/security/pii.py`
- **Limitations**: No context awareness, limited patterns, no NLP support
- **Decision**: **IMMEDIATE REPLACEMENT** - Microsoft Presidio will replace our homegrown PII detection

## Integration Approach: Progressive Enhancement

### Core Strategy

Use Presidio WITHOUT requiring NLP models by default, but allow users to progressively enhance detection capabilities by installing spaCy models.

### Dependency Analysis

#### Base Installation (~50MB)
```bash
pip install presidio-analyzer
```
- Includes spaCy library (required dependency)
- NO language models downloaded
- Supports regex-based pattern detection only

#### Progressive Model Options

| Mode | Additional Size | Total Size | Command |
|------|----------------|------------|---------|
| Regex-only | 0MB | ~50MB | None (default) |
| Small NLP | +15MB | ~65MB | `python -m spacy download en_core_web_sm` |
| Large NLP | +750MB | ~800MB | `python -m spacy download en_core_web_lg` |

### Why spaCy is Required

Despite not using NLP features in regex mode, Presidio has a hard dependency on spaCy because:
1. The codebase imports spaCy types even when `nlp_engine=None`
2. This is an architectural decision by Microsoft
3. Cannot be avoided without forking Presidio

## Implementation Design

### Plugin Architecture

```python
class PresidioPIIPlugin(SecurityPlugin):
    """
    PII detection powered by Microsoft Presidio.
    Progressive enhancement from regex → NLP.
    """
    
    def __init__(self, config):
        mode = config.get("mode", "regex")
        
        if mode == "regex":
            # No NLP, patterns only
            self.analyzer = AnalyzerEngine(nlp_engine=None)
            self._add_pattern_recognizers()
            
        elif mode == "nlp_small":
            # Requires: en_core_web_sm (15MB)
            nlp = spacy.load("en_core_web_sm")
            self.analyzer = AnalyzerEngine(nlp_engine=nlp)
            
        elif mode == "nlp_large":
            # Requires: en_core_web_lg (750MB)
            nlp = spacy.load("en_core_web_lg")
            self.analyzer = AnalyzerEngine(nlp_engine=nlp)
            
        elif mode == "auto":
            # Detect best available
            self._auto_detect_mode()
```

### Configuration Schema

```yaml
# Default - Minimal dependencies (NO OLD "pii" POLICY NAME)
plugins:
  security:
    - policy: "presidio_pii"  # NOT "pii" - that's deleted
      config:
        mode: "regex"  # No models needed
        entities:
          - CREDIT_CARD
          - US_SSN
          - EMAIL_ADDRESS
          - PHONE_NUMBER
        confidence_threshold: 0.7
        action: "block"  # or "redact", "audit_only"

# Enhanced - With NLP
plugins:
  security:
    - policy: "presidio_pii"  # Single consistent name
      config:
        mode: "nlp_small"  # or "nlp_large", "auto"
        entities:
          - CREDIT_CARD
          - US_SSN
          - PERSON  # NLP helps detect names
          - LOCATION  # NLP helps detect places
          - ORGANIZATION
        confidence_threshold: 0.6
        action: "redact"
```

### Graceful Fallback

The plugin will automatically fall back to available modes:
1. User requests `nlp_large` but it's not installed → try `nlp_small`
2. No NLP models available → fall back to `regex`
3. Clear logging about what mode is active and how to upgrade

## Benefits of Presidio Integration

### Technical Benefits
1. **Battle-tested patterns**: Microsoft has refined these patterns over years
2. **Validation logic**: Luhn algorithm for credit cards, checksum validation
3. **Confidence scoring**: Each detection has a confidence score (0.0-1.0)
4. **Overlap handling**: Properly handles overlapping entity detections
5. **Context enhancement**: Can use surrounding words to improve accuracy
6. **Language support**: Multi-language detection capabilities

### Business Benefits
1. **Credibility**: "Powered by Microsoft Presidio"
2. **Reduced maintenance**: Outsource pattern updates to Microsoft
3. **Compliance**: Industry-standard PII detection
4. **Future-proof**: Can upgrade to NLP when needed

## Trade-offs

### Pros
- Enterprise-grade PII detection
- Optional NLP enhancement
- Well-maintained by Microsoft
- Clear upgrade path
- Professional credibility

### Cons
- 50MB minimum dependency (spaCy library)
- Cannot completely avoid spaCy dependency
- More complex than pure regex
- Potential supply chain risk (though from Microsoft)

## Migration Strategy

### Immediate Replacement Plan

Since we haven't released v0.1.0 yet, we will **immediately replace** our homegrown PII detection with Presidio:

1. **Remove current implementation**: Delete `watchgate/plugins/security/pii.py`
2. **Add Presidio plugin**: Create `watchgate/plugins/security/presidio_pii.py`
3. **Single policy name**: Only use `"presidio_pii"` (no aliases for old `"pii"` name)
4. **No backward compatibility**: We're pre-release, clean break is fine

### Implementation Note

This change is being considered for a future release:
- Would eliminate maintenance burden of custom regex patterns
- Would provide enterprise-grade PII detection
- Would give us credibility with "Powered by Microsoft Presidio"
- Still maintains minimal dependencies (regex-only mode by default)

## Security Considerations

### Supply Chain Risk Assessment

#### Low Risk Factors
- Microsoft-maintained (reputable source)
- MIT licensed (can audit/fork)
- Active maintenance and security updates
- No binary blobs in regex-only mode

#### Medium Risk Factors
- spaCy dependency adds attack surface
- ~50MB of additional code to audit
- Complex C extensions in spaCy

#### High Risk Factors (NLP mode only)
- 750MB binary models (if using large NLP)
- Pickled models can execute code
- Models downloaded separately from PyPI

### Mitigation Strategies
1. Default to regex-only mode (no models)
2. Document security implications of NLP models
3. Verify package signatures when possible
4. Regular security updates

## User Documentation

### Installation Guide

```markdown
## Presidio PII Detection

### Quick Start (Regex-only)
pip install watchgate[presidio]
# Uses Microsoft Presidio patterns without NLP models

### Upgrade to NLP (Optional)

#### Small Model (+15MB)
python -m spacy download en_core_web_sm
# Edit config: mode: "nlp_small"

#### Large Model (+750MB) - Best Accuracy
python -m spacy download en_core_web_lg  
# Edit config: mode: "nlp_large"
```

## Future Implementation Timeline

When implemented:
1. Create basic Presidio adapter plugin
2. Add progressive enhancement logic
3. Testing and validation
4. Documentation and examples

## Open Questions

1. Should we make Presidio an optional dependency?
   - Pro: Smaller default install
   - Con: Users need extra step to enable

2. Should we bundle small NLP model?
   - Pro: Better detection out of box
   - Con: +15MB to package size

3. How to handle Presidio version updates?
   - Pin to specific version for stability?
   - Allow minor updates automatically?

## Practical Implementation: Chain of Trust

### Default Installation Strategy

Include Presidio by default in pyproject.toml but NOT the models:

```toml
[project]
dependencies = [
    "presidio-analyzer>=2.2.0",  # Includes spaCy (~50MB)
    "detect-secrets>=1.4.0",     # Only 97KB
    # ... other deps
]
# No model dependencies - users install directly from spaCy
```

### Simple Implementation Approach

```python
def __init__(self, config):
    """Initialize plugin with automatic fallback to regex mode if NLP unavailable."""
    mode = config.get("mode", "regex")
    
    if mode in ["nlp_small", "nlp_large"]:
        model_name = "en_core_web_sm" if mode == "nlp_small" else "en_core_web_lg"
        try:
            import spacy
            nlp = spacy.load(model_name)
            self.analyzer = AnalyzerEngine(nlp_engine=nlp)
            logger.info(f"Presidio initialized with {model_name} NLP model")
        except OSError:
            # Let spaCy's error message guide the user - it already says:
            # "python -m spacy download en_core_web_sm"
            logger.info(f"NLP model '{model_name}' not installed, using regex-only mode (still detects credit cards, SSNs, emails, etc.)")
            self.analyzer = AnalyzerEngine(nlp_engine=None)
            self._add_pattern_recognizers()
    else:
        # Regex mode explicitly requested or default
        self.analyzer = AnalyzerEngine(nlp_engine=None)
        self._add_pattern_recognizers()
```

**Key Points:**
- No special CLI commands or health checks
- Standard Python error handling
- spaCy already tells users exactly what command to run
- Graceful fallback to regex mode
- Treat it like any other plugin - no architectural special cases

### Automatic Fallback Behavior

The plugin automatically detects available models and falls back gracefully:
- If NLP model requested but not installed → falls back to regex mode
- Clear log message shows the exact command to install missing models
- No special CLI commands needed - standard plugin loading handles everything

### Progressive Enhancement Flow

1. **Default Install**: `pip install watchgate` includes Presidio (regex mode)
2. **Works immediately**: No additional setup required
3. **Optional enhancement**: Users can add NLP models if desired
4. **Chain of trust**: Models downloaded directly from spaCy, not through us
5. **Clear feedback**: Informative messages, not error-like warnings

### Key User Experience Principles

- **Let Python/spaCy provide the error messages** - They already know how to tell users what to do
- **Simple fallback** - If NLP model not found, use regex mode
- **Log at INFO level** - This is expected behavior, not an error
- **No special tooling** - Standard plugin initialization handles everything

## Decision

**Proceed with Chain of Trust approach**: Ship with Presidio by default but let users install models themselves. Use positive, enhancement-focused messaging that doesn't sound like errors.

## Configuration Reference

### Configuration Example

```yaml
- policy: "presidio_pii"
  config:
    mode: "regex"  # "regex" (default), "nlp_small", "nlp_large", "auto"
    action: "redact"  # "block", "redact", or "audit_only"
    entities:  # Which PII types to detect
      - CREDIT_CARD
      - US_SSN
      - EMAIL_ADDRESS
      - PHONE_NUMBER
      - PERSON  # Requires NLP mode
      - LOCATION  # Requires NLP mode
    confidence_threshold: 0.7
    exemptions:
      tools: ["trusted_tool"]
      paths: ["safe/path/*"]
```

### Configuration Options

- `mode`: Detection mode (powered by Microsoft Presidio)
  - `"regex"`: Pattern-based detection only (default, no NLP models needed)
  - `"nlp_small"`: Uses small NLP model (requires `en_core_web_sm`, 15MB)
  - `"nlp_large"`: Uses large NLP model (requires `en_core_web_lg`, 750MB)
  - `"auto"`: Automatically uses best available mode
- `action`: Controls how PII is handled when detected
  - `"block"`: Prevents transmission of any content containing PII
  - `"redact"`: Replaces PII with placeholder text
  - `"audit_only"`: Logs PII detections but allows content to pass through unchanged
- `entities`: List of PII entity types to detect (Presidio format)
  - Pattern-based (work in regex mode): CREDIT_CARD, US_SSN, EMAIL_ADDRESS, PHONE_NUMBER, etc.
  - NLP-based (require NLP mode): PERSON, LOCATION, ORGANIZATION, etc.
- `confidence_threshold`: Minimum confidence score (0.0-1.0) for detections
- `exemptions`: Tools or paths that bypass PII filtering
- `priority`: Plugin execution priority (optional, range: 0-100, default: 50)

### Credit Card Detection Behavior

The plugin uses **Luhn algorithm validation** for credit card detection to reduce false positives. This means:

- ✅ **Valid credit cards are detected**: Numbers that pass Luhn validation (e.g., `4532015112830366`)
- ❌ **Invalid credit cards are NOT detected**: Random 16-digit numbers that fail Luhn validation (e.g., `4532123456789012`)
- 🔒 **Security benefit**: Prevents false positives from random numbers that happen to match credit card patterns

### Example Detection Results

```yaml
# These will be detected and handled according to your action setting:
"4532 0151 1283 0366"  # Valid Visa (passes Luhn)
"5555 5555 5555 4444"  # Valid MasterCard (passes Luhn)

# These will NOT be detected (invalid Luhn checksums):
"4532 1234 5678 9012"  # Invalid Visa
"5555 4444 3333 2222"  # Invalid MasterCard
```

### Common Use Cases

1. **Basic PII Protection** (redact sensitive data):
```yaml
config:
  action: "redact"
  entities:
    - CREDIT_CARD
    - EMAIL_ADDRESS
    - US_SSN
```

2. **Strict Security** (block any PII):
```yaml
config:
  action: "block"
  entities:
    - CREDIT_CARD
    - EMAIL_ADDRESS
    - PHONE_NUMBER
```

3. **Compliance Monitoring** (log but allow):
```yaml
config:
  action: "audit_only"
  entities:
    - CREDIT_CARD
    - EMAIL_ADDRESS
```

## References

- [Microsoft Presidio GitHub](https://github.com/microsoft/presidio)
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- [spaCy Models](https://spacy.io/models)
- [Presidio PyPI Package](https://pypi.org/project/presidio-analyzer/)