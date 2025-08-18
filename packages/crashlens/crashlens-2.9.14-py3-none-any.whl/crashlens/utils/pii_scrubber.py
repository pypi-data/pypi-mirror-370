"""
PII Scrubbing Utility
Masks or removes personally identifiable information from logs and outputs
"""

import re
from typing import Dict, Any, List


class PIIScrubber:
    """Scrubs PII from log data and outputs"""
    
    def __init__(self):
        # Fields to completely remove from output
        self.sensitive_fields = {
            'user_id', 'user_email', 'email', 'user_email', 'email_address',
            'phone', 'phone_number', 'mobile', 'telephone',
            'ssn', 'social_security', 'tax_id',
            'credit_card', 'card_number', 'cc_number',
            'password', 'secret', 'api_key', 'token',
            'address', 'street_address', 'home_address',
            'ip_address', 'ip', 'client_ip'
        }
        
        # Patterns to mask in text content
        self.mask_patterns = [
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
            # Phone numbers
            (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),
            # Credit card numbers
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]'),
            # SSN
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),
            # IP addresses
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]'),
            # API keys (common patterns)
            (r'\b(sk-|pk-)[a-zA-Z0-9]{20,}\b', '[API_KEY]'),
            # UUIDs (might contain sensitive info)
            (r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '[UUID]'),
        ]
    
    def scrub_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub PII from a single log record"""
        scrubbed = record.copy()
        
        # Remove sensitive fields
        for field in self.sensitive_fields:
            if field in scrubbed:
                del scrubbed[field]
        
        # Scrub metadata if present
        if 'metadata' in scrubbed and isinstance(scrubbed['metadata'], dict):
            scrubbed['metadata'] = self.scrub_metadata(scrubbed['metadata'])
        
        # Scrub prompt text
        if 'prompt' in scrubbed:
            scrubbed['prompt'] = self.scrub_text(scrubbed['prompt'])
        
        # Scrub any other text fields that might contain PII
        text_fields = ['completion', 'response', 'message', 'content', 'text']
        for field in text_fields:
            if field in scrubbed and isinstance(scrubbed[field], str):
                scrubbed[field] = self.scrub_text(scrubbed[field])
        
        return scrubbed
    
    def scrub_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub PII from metadata object"""
        scrubbed = {}
        
        for key, value in metadata.items():
            # Skip sensitive metadata keys
            if key.lower() in self.sensitive_fields:
                continue
            
            # Recursively scrub nested objects
            if isinstance(value, dict):
                scrubbed[key] = self.scrub_metadata(value)
            elif isinstance(value, str):
                scrubbed[key] = self.scrub_text(value)
            else:
                scrubbed[key] = value
        
        return scrubbed
    
    def scrub_text(self, text: str) -> str:
        """Scrub PII patterns from text content"""
        if not isinstance(text, str):
            return text
        
        scrubbed = text
        
        # Apply mask patterns
        for pattern, replacement in self.mask_patterns:
            scrubbed = re.sub(pattern, replacement, scrubbed, flags=re.IGNORECASE)
        
        return scrubbed
    
    def scrub_detection(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub PII from detection output"""
        scrubbed = detection.copy()
        
        # Scrub sample prompt
        if 'sample_prompt' in scrubbed:
            scrubbed['sample_prompt'] = self.scrub_text(scrubbed['sample_prompt'])
        
        # Scrub records if present
        if 'records' in scrubbed and isinstance(scrubbed['records'], list):
            scrubbed['records'] = [self.scrub_record(record) for record in scrubbed['records']]
        
        return scrubbed
    
    def scrub_traces(self, traces: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Scrub PII from traces dictionary"""
        scrubbed_traces = {}
        
        for trace_id, records in traces.items():
            scrubbed_records = [self.scrub_record(record) for record in records]
            scrubbed_traces[trace_id] = scrubbed_records
        
        return scrubbed_traces 