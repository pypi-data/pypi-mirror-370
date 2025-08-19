"""
Advanced ID Generation and Fuzzing Module for LogicPWN.

Provides intelligent ID enumeration strategies including:
- Sequential and predictable ID generation
- Common ID pattern fuzzing (UUIDs, Base64, etc.)
- Context-aware ID generation based on discovered patterns
- Tenant-specific ID enumeration
- Privilege-based ID inference
- Smart ID validation and filtering
"""

import re
import uuid
import base64
import random
import string
import itertools
from typing import List, Set, Dict, Any, Optional, Union, Iterator, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import time
import math

from logicpwn.core.logging import log_info, log_warning, log_error


class IDType(Enum):
    """Enumeration of supported ID types for intelligent generation."""
    SEQUENTIAL = "sequential"
    UUID = "uuid"
    HASH = "hash"
    BASE64 = "base64"
    ALPHANUMERIC = "alphanumeric"
    CUSTOM_PATTERN = "custom_pattern"
    TENANT_ID = "tenant_id"
    USER_ID = "user_id"
    ADMIN_ID = "admin_id"
    SESSION_ID = "session_id"
    TOKEN = "token"


@dataclass
class IDPattern:
    """Represents a discovered or configured ID pattern."""
    pattern_type: IDType
    format_string: str
    length: int
    character_set: str
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    example_values: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    detection_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IDGenerationConfig:
    """Configuration for ID generation and fuzzing."""
    max_generated_ids: int = 1000
    sequential_range: int = 100
    random_sample_size: int = 50
    include_edge_cases: bool = True
    custom_patterns: List[str] = field(default_factory=list)
    tenant_aware: bool = True
    privilege_aware: bool = True
    character_sets: Dict[str, str] = field(default_factory=lambda: {
        'numeric': '0123456789',
        'alpha_lower': 'abcdefghijklmnopqrstuvwxyz',
        'alpha_upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'alphanumeric': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'hex': '0123456789abcdef',
        'base64': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/',
        'special': '!@#$%^&*()_+-=[]{}|;:,.<>?'
    })
    

class IDGenerator(ABC):
    """Abstract base class for ID generators."""
    
    @abstractmethod
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate IDs based on the given pattern and configuration."""
        pass
    
    @abstractmethod
    def supports_pattern(self, pattern: IDPattern) -> bool:
        """Check if this generator supports the given pattern."""
        pass


class SequentialIDGenerator(IDGenerator):
    """Generator for sequential numeric IDs."""
    
    def supports_pattern(self, pattern: IDPattern) -> bool:
        return pattern.pattern_type == IDType.SEQUENTIAL
    
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate sequential IDs with intelligent range detection."""
        ids = []
        
        # Extract base numbers from example values
        base_numbers = []
        for example in pattern.example_values:
            match = re.search(r'\d+', example)
            if match:
                base_numbers.append(int(match.group()))
        
        if not base_numbers:
            # Default sequential generation
            start = 1
            end = config.sequential_range
        else:
            # Generate around discovered numbers
            min_num = min(base_numbers)
            max_num = max(base_numbers)
            
            # Expand range intelligently
            range_size = max_num - min_num if max_num > min_num else config.sequential_range
            start = max(1, min_num - range_size // 2)
            end = max_num + range_size // 2
        
        # Generate sequential IDs
        for i in range(start, min(end + 1, start + config.max_generated_ids)):
            if pattern.prefix:
                id_val = f"{pattern.prefix}{i}"
            elif pattern.suffix:
                id_val = f"{i}{pattern.suffix}"
            else:
                id_val = str(i)
            ids.append(id_val)
        
        # Add edge cases
        if config.include_edge_cases:
            edge_cases = ['0', '-1', '999999999', '2147483647', '-2147483648']
            if pattern.prefix:
                edge_cases = [f"{pattern.prefix}{case}" for case in edge_cases]
            elif pattern.suffix:
                edge_cases = [f"{case}{pattern.suffix}" for case in edge_cases]
            ids.extend(edge_cases)
        
        return ids[:config.max_generated_ids]


class UUIDGenerator(IDGenerator):
    """Generator for UUID-based IDs."""
    
    def supports_pattern(self, pattern: IDPattern) -> bool:
        return pattern.pattern_type == IDType.UUID
    
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate various UUID formats and variations."""
        ids = []
        
        # Generate standard UUIDs
        for _ in range(min(config.random_sample_size, config.max_generated_ids // 4)):
            ids.extend([
                str(uuid.uuid4()),
                str(uuid.uuid4()).replace('-', ''),
                str(uuid.uuid4()).upper(),
                str(uuid.uuid4()).replace('-', '').upper()
            ])
        
        # Generate predictable UUIDs based on patterns
        if pattern.example_values:
            for example in pattern.example_values[:10]:
                try:
                    # Try to find patterns in existing UUIDs
                    uuid_obj = uuid.UUID(example.replace('-', ''))
                    # Generate variants by modifying last bytes
                    for i in range(5):
                        variant = str(uuid_obj).replace(str(uuid_obj)[-1], str(i))
                        ids.append(variant)
                except ValueError:
                    continue
        
        # Generate sequential-like UUIDs
        base_uuid = "00000000-0000-4000-8000-000000000000"
        for i in range(min(20, config.max_generated_ids // 10)):
            sequential_uuid = base_uuid[:-3] + f"{i:03d}"
            ids.append(sequential_uuid)
        
        return ids[:config.max_generated_ids]


class HashIDGenerator(IDGenerator):
    """Generator for hash-based IDs."""
    
    def supports_pattern(self, pattern: IDPattern) -> bool:
        return pattern.pattern_type == IDType.HASH
    
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate hash-like IDs with various algorithms."""
        ids = []
        
        # Determine hash length from examples
        hash_length = pattern.length or 32
        if pattern.example_values:
            hash_length = len(pattern.example_values[0])
        
        # Generate common hash formats
        for i in range(min(config.random_sample_size, config.max_generated_ids // 3)):
            # MD5-like (32 chars)
            if hash_length == 32:
                ids.append(hashlib.md5(f"test{i}".encode()).hexdigest())
            # SHA1-like (40 chars)
            elif hash_length == 40:
                ids.append(hashlib.sha1(f"test{i}".encode()).hexdigest())
            # SHA256-like (64 chars)
            elif hash_length == 64:
                ids.append(hashlib.sha256(f"test{i}".encode()).hexdigest())
            else:
                # Custom length hash
                full_hash = hashlib.sha256(f"test{i}".encode()).hexdigest()
                ids.append(full_hash[:hash_length])
        
        # Generate predictable hashes
        common_inputs = ['admin', 'user', 'guest', 'test', 'demo', 'root', '1', '0']
        for input_val in common_inputs:
            if hash_length == 32:
                ids.append(hashlib.md5(input_val.encode()).hexdigest())
            elif hash_length == 40:
                ids.append(hashlib.sha1(input_val.encode()).hexdigest())
            elif hash_length == 64:
                ids.append(hashlib.sha256(input_val.encode()).hexdigest())
        
        return ids[:config.max_generated_ids]


class Base64IDGenerator(IDGenerator):
    """Generator for Base64-encoded IDs."""
    
    def supports_pattern(self, pattern: IDPattern) -> bool:
        return pattern.pattern_type == IDType.BASE64
    
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate Base64-encoded IDs."""
        ids = []
        
        # Determine typical payload for Base64 encoding
        common_payloads = [
            'admin', 'user', 'guest', 'test', 'root', '1', '0',
            '{"user_id": 1}', '{"role": "admin"}', 'user:1', 'id=1'
        ]
        
        for payload in common_payloads:
            encoded = base64.b64encode(payload.encode()).decode().rstrip('=')
            ids.append(encoded)
            # Add with padding
            ids.append(base64.b64encode(payload.encode()).decode())
        
        # Generate sequential Base64 IDs
        for i in range(min(config.sequential_range, config.max_generated_ids // 2)):
            payload = f"id:{i}"
            encoded = base64.b64encode(payload.encode()).decode().rstrip('=')
            ids.append(encoded)
        
        # Generate random-looking Base64
        for _ in range(min(config.random_sample_size, config.max_generated_ids // 4)):
            random_bytes = bytes([random.randint(0, 255) for _ in range(12)])
            encoded = base64.b64encode(random_bytes).decode().rstrip('=')
            ids.append(encoded)
        
        return ids[:config.max_generated_ids]


class AlphanumericIDGenerator(IDGenerator):
    """Generator for alphanumeric IDs."""
    
    def supports_pattern(self, pattern: IDPattern) -> bool:
        return pattern.pattern_type == IDType.ALPHANUMERIC
    
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate alphanumeric IDs based on discovered patterns."""
        ids = []
        
        # Determine length and character set
        length = pattern.length or 8
        charset = config.character_sets.get('alphanumeric', string.ascii_letters + string.digits)
        
        # Generate based on examples
        if pattern.example_values:
            for example in pattern.example_values[:5]:
                # Generate variations
                for i in range(5):
                    variant = list(example)
                    # Modify random positions
                    for _ in range(min(2, len(variant))):
                        pos = random.randint(0, len(variant) - 1)
                        variant[pos] = random.choice(charset)
                    ids.append(''.join(variant))
        
        # Generate common patterns
        common_prefixes = ['user', 'admin', 'test', 'demo', 'guest', 'api', 'sys']
        for prefix in common_prefixes:
            for i in range(10):
                suffix = ''.join(random.choices(charset, k=length - len(prefix)))
                ids.append(f"{prefix}{suffix}")
        
        # Generate purely random IDs
        for _ in range(min(config.random_sample_size, config.max_generated_ids // 2)):
            random_id = ''.join(random.choices(charset, k=length))
            ids.append(random_id)
        
        return ids[:config.max_generated_ids]


class TenantIDGenerator(IDGenerator):
    """Generator for tenant-specific IDs."""
    
    def supports_pattern(self, pattern: IDPattern) -> bool:
        return pattern.pattern_type == IDType.TENANT_ID
    
    def generate_ids(self, config: IDGenerationConfig, pattern: IDPattern) -> List[str]:
        """Generate tenant IDs with common patterns."""
        ids = []
        
        # Common tenant naming patterns
        tenant_patterns = [
            'tenant-{}', 'org-{}', 'company-{}', 'client-{}',
            'account-{}', 'workspace-{}', 'team-{}', 'group-{}'
        ]
        
        # Common tenant names
        tenant_names = [
            'admin', 'test', 'demo', 'default', 'system', 'root',
            'acme', 'example', 'sample', 'trial', 'beta', 'staging'
        ]
        
        # Generate pattern-based tenant IDs
        for pattern_template in tenant_patterns:
            for i in range(1, min(21, config.sequential_range)):
                ids.append(pattern_template.format(i))
            for name in tenant_names:
                ids.append(pattern_template.format(name))
        
        # Generate domain-based tenant IDs
        domains = ['acme.com', 'test.org', 'demo.net', 'example.com']
        for domain in domains:
            ids.extend([
                domain,
                domain.split('.')[0],
                domain.replace('.', '-'),
                domain.replace('.', '_')
            ])
        
        # Generate based on discovered examples
        if pattern.example_values:
            for example in pattern.example_values:
                # Extract patterns and generate variations
                if '-' in example:
                    parts = example.split('-')
                    if len(parts) >= 2:
                        prefix = parts[0]
                        for i in range(1, 21):
                            ids.append(f"{prefix}-{i}")
        
        return ids[:config.max_generated_ids]


class PatternDetector:
    """Detects ID patterns from example values."""
    
    def __init__(self):
        self.pattern_matchers = {
            IDType.UUID: self._detect_uuid_pattern,
            IDType.HASH: self._detect_hash_pattern,
            IDType.BASE64: self._detect_base64_pattern,
            IDType.SEQUENTIAL: self._detect_sequential_pattern,
            IDType.ALPHANUMERIC: self._detect_alphanumeric_pattern,
            IDType.TENANT_ID: self._detect_tenant_pattern
        }
    
    def detect_patterns(self, example_ids: List[str]) -> List[IDPattern]:
        """Detect patterns from a list of example IDs."""
        if not example_ids:
            return []
        
        patterns = []
        for pattern_type, detector in self.pattern_matchers.items():
            pattern = detector(example_ids)
            if pattern and pattern.confidence_score > 0.5:
                patterns.append(pattern)
        
        # Sort by confidence score
        patterns.sort(key=lambda p: p.confidence_score, reverse=True)
        return patterns
    
    def _detect_uuid_pattern(self, examples: List[str]) -> Optional[IDPattern]:
        """Detect UUID patterns."""
        uuid_regex = re.compile(
            r'^[0-9a-f]{8}-?[0-9a-f]{4}-?[1-5][0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        matches = [ex for ex in examples if uuid_regex.match(ex)]
        if not matches:
            return None
        
        confidence = len(matches) / len(examples)
        has_dashes = any('-' in m for m in matches)
        
        return IDPattern(
            pattern_type=IDType.UUID,
            format_string="xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx" if has_dashes else "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            length=36 if has_dashes else 32,
            character_set="0123456789abcdef-",
            example_values=matches[:5],
            confidence_score=confidence,
            detection_metadata={"has_dashes": has_dashes}
        )
    
    def _detect_hash_pattern(self, examples: List[str]) -> Optional[IDPattern]:
        """Detect hash patterns."""
        hash_lengths = {32: "MD5", 40: "SHA1", 64: "SHA256"}
        length_counts = {}
        
        for ex in examples:
            if re.match(r'^[0-9a-f]+$', ex, re.IGNORECASE):
                length = len(ex)
                length_counts[length] = length_counts.get(length, 0) + 1
        
        if not length_counts:
            return None
        
        most_common_length = max(length_counts.keys(), key=lambda k: length_counts[k])
        matching_examples = [ex for ex in examples if len(ex) == most_common_length]
        
        confidence = len(matching_examples) / len(examples)
        if confidence < 0.3:
            return None
        
        return IDPattern(
            pattern_type=IDType.HASH,
            format_string="x" * most_common_length,
            length=most_common_length,
            character_set="0123456789abcdef",
            example_values=matching_examples[:5],
            confidence_score=confidence,
            detection_metadata={
                "hash_type": hash_lengths.get(most_common_length, "Custom"),
                "case": "lower" if all(ex.islower() for ex in matching_examples) else "mixed"
            }
        )
    
    def _detect_base64_pattern(self, examples: List[str]) -> Optional[IDPattern]:
        """Detect Base64 patterns."""
        base64_regex = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        matches = []
        
        for ex in examples:
            if base64_regex.match(ex) and len(ex) % 4 in [0, 2, 3]:
                try:
                    # Try to decode to verify it's valid base64
                    base64.b64decode(ex + '==')
                    matches.append(ex)
                except:
                    continue
        
        if not matches:
            return None
        
        confidence = len(matches) / len(examples)
        avg_length = sum(len(m) for m in matches) // len(matches)
        
        return IDPattern(
            pattern_type=IDType.BASE64,
            format_string="x" * avg_length,
            length=avg_length,
            character_set="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
            example_values=matches[:5],
            confidence_score=confidence,
            detection_metadata={"average_length": avg_length}
        )
    
    def _detect_sequential_pattern(self, examples: List[str]) -> Optional[IDPattern]:
        """Detect sequential numeric patterns."""
        numeric_values = []
        prefix = ""
        suffix = ""
        
        for ex in examples:
            match = re.search(r'^([^0-9]*)(\d+)([^0-9]*)$', ex)
            if match:
                curr_prefix, num_str, curr_suffix = match.groups()
                if not prefix:
                    prefix = curr_prefix
                if not suffix:
                    suffix = curr_suffix
                
                if curr_prefix == prefix and curr_suffix == suffix:
                    numeric_values.append(int(num_str))
        
        if len(numeric_values) < 2:
            return None
        
        # Check for sequential pattern
        sorted_values = sorted(numeric_values)
        is_sequential = all(
            sorted_values[i] - sorted_values[i-1] <= 10 
            for i in range(1, len(sorted_values))
        )
        
        confidence = len(numeric_values) / len(examples)
        if is_sequential:
            confidence *= 1.5  # Boost confidence for sequential patterns
        
        return IDPattern(
            pattern_type=IDType.SEQUENTIAL,
            format_string=f"{prefix}{{}}{{suffix}}",
            length=len(examples[0]) if examples else 1,
            character_set="0123456789",
            prefix=prefix if prefix else None,
            suffix=suffix if suffix else None,
            example_values=examples[:5],
            confidence_score=min(confidence, 1.0),
            detection_metadata={
                "is_sequential": is_sequential,
                "min_value": min(numeric_values),
                "max_value": max(numeric_values)
            }
        )
    
    def _detect_alphanumeric_pattern(self, examples: List[str]) -> Optional[IDPattern]:
        """Detect alphanumeric patterns."""
        if not examples:
            return None
        
        # Check if all examples are alphanumeric
        alphanumeric_examples = [
            ex for ex in examples 
            if re.match(r'^[a-zA-Z0-9]+$', ex)
        ]
        
        if not alphanumeric_examples:
            return None
        
        confidence = len(alphanumeric_examples) / len(examples)
        avg_length = sum(len(ex) for ex in alphanumeric_examples) // len(alphanumeric_examples)
        
        # Analyze character distribution
        has_upper = any(any(c.isupper() for c in ex) for ex in alphanumeric_examples)
        has_lower = any(any(c.islower() for c in ex) for ex in alphanumeric_examples)
        has_digits = any(any(c.isdigit() for c in ex) for ex in alphanumeric_examples)
        
        charset = ""
        if has_digits:
            charset += "0123456789"
        if has_lower:
            charset += "abcdefghijklmnopqrstuvwxyz"
        if has_upper:
            charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        return IDPattern(
            pattern_type=IDType.ALPHANUMERIC,
            format_string="x" * avg_length,
            length=avg_length,
            character_set=charset,
            example_values=alphanumeric_examples[:5],
            confidence_score=confidence,
            detection_metadata={
                "has_upper": has_upper,
                "has_lower": has_lower,
                "has_digits": has_digits,
                "average_length": avg_length
            }
        )
    
    def _detect_tenant_pattern(self, examples: List[str]) -> Optional[IDPattern]:
        """Detect tenant ID patterns."""
        tenant_keywords = ['tenant', 'org', 'company', 'client', 'account', 'workspace', 'team']
        domain_pattern = re.compile(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$')
        
        tenant_examples = []
        for ex in examples:
            ex_lower = ex.lower()
            if (any(keyword in ex_lower for keyword in tenant_keywords) or
                domain_pattern.match(ex) or
                '-' in ex or '_' in ex):
                tenant_examples.append(ex)
        
        if not tenant_examples:
            return None
        
        confidence = len(tenant_examples) / len(examples)
        avg_length = sum(len(ex) for ex in tenant_examples) // len(tenant_examples)
        
        return IDPattern(
            pattern_type=IDType.TENANT_ID,
            format_string="tenant-pattern",
            length=avg_length,
            character_set="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.",
            example_values=tenant_examples[:5],
            confidence_score=confidence,
            detection_metadata={"average_length": avg_length}
        )


class EnhancedIDGenerator:
    """Enhanced ID generator with intelligent pattern detection and fuzzing."""
    
    def __init__(self, config: Optional[IDGenerationConfig] = None):
        self.config = config or IDGenerationConfig()
        self.pattern_detector = PatternDetector()
        self.generators = [
            SequentialIDGenerator(),
            UUIDGenerator(),
            HashIDGenerator(),
            Base64IDGenerator(),
            AlphanumericIDGenerator(),
            TenantIDGenerator()
        ]
        # Add max_generated_ids attribute for performance tracking
        self.max_generated_ids = self.config.max_ids_per_pattern if hasattr(self.config, 'max_ids_per_pattern') else 1000
    
    def generate_intelligent_ids(
        self, 
        example_ids: List[str], 
        additional_patterns: Optional[List[IDPattern]] = None
    ) -> Dict[str, List[str]]:
        """Generate IDs based on detected patterns and additional configurations."""
        result = {}
        
        # Detect patterns from examples
        detected_patterns = self.pattern_detector.detect_patterns(example_ids)
        log_info(f"Detected {len(detected_patterns)} ID patterns")
        
        # Combine with additional patterns
        all_patterns = detected_patterns + (additional_patterns or [])
        
        # Generate IDs for each pattern
        for pattern in all_patterns:
            generator = self._get_generator_for_pattern(pattern)
            if generator:
                generated_ids = generator.generate_ids(self.config, pattern)
                pattern_name = f"{pattern.pattern_type.value}_confidence_{pattern.confidence_score:.2f}"
                result[pattern_name] = generated_ids
                log_info(f"Generated {len(generated_ids)} IDs for pattern {pattern_name}")
        
        # Always include some basic fuzzing if no patterns detected
        if not detected_patterns:
            basic_patterns = [
                IDPattern(IDType.SEQUENTIAL, "numeric", 10, "0123456789"),
                IDPattern(IDType.ALPHANUMERIC, "alphanum", 8, "abcdefghijklmnopqrstuvwxyz0123456789")
            ]
            
            for pattern in basic_patterns:
                generator = self._get_generator_for_pattern(pattern)
                if generator:
                    generated_ids = generator.generate_ids(self.config, pattern)
                    result[f"basic_{pattern.pattern_type.value}"] = generated_ids
        
        return result
    
    def _get_generator_for_pattern(self, pattern: IDPattern) -> Optional[IDGenerator]:
        """Get the appropriate generator for a given pattern."""
        for generator in self.generators:
            if generator.supports_pattern(pattern):
                return generator
        return None
    
    def generate_privilege_aware_ids(
        self, 
        known_user_ids: List[str], 
        privilege_indicators: List[str] = None
    ) -> Dict[str, List[str]]:
        """Generate IDs with privilege escalation awareness."""
        privilege_indicators = privilege_indicators or [
            'admin', 'root', 'super', 'manager', 'owner', 'god', 'system',
            'administrator', 'superuser', 'su', '0', '1'
        ]
        
        result = {}
        
        # Generate admin-like IDs based on user patterns
        detected_patterns = self.pattern_detector.detect_patterns(known_user_ids)
        
        for pattern in detected_patterns:
            admin_ids = []
            
            if pattern.pattern_type == IDType.SEQUENTIAL:
                # Generate admin IDs around common admin ranges
                admin_ranges = [0, 1, 999, 1000, 9999, -1]
                for admin_id in admin_ranges:
                    if pattern.prefix:
                        admin_ids.append(f"{pattern.prefix}{admin_id}")
                    elif pattern.suffix:
                        admin_ids.append(f"{admin_id}{pattern.suffix}")
                    else:
                        admin_ids.append(str(admin_id))
            
            elif pattern.pattern_type in [IDType.ALPHANUMERIC, IDType.TENANT_ID]:
                # Generate admin-themed variations
                for indicator in privilege_indicators:
                    if pattern.prefix:
                        admin_ids.append(f"{pattern.prefix}{indicator}")
                    elif pattern.suffix:
                        admin_ids.append(f"{indicator}{pattern.suffix}")
                    else:
                        admin_ids.append(indicator)
            
            if admin_ids:
                result[f"admin_{pattern.pattern_type.value}"] = admin_ids
        
        return result
    
    def generate_tenant_isolation_ids(
        self, 
        known_tenant_ids: List[str],
        target_tenant: str = None
    ) -> Dict[str, List[str]]:
        """Generate IDs for tenant isolation testing."""
        result = {}
        
        # Detect tenant patterns
        tenant_patterns = self.pattern_detector.detect_patterns(known_tenant_ids)
        
        for pattern in tenant_patterns:
            generator = self._get_generator_for_pattern(pattern)
            if generator and hasattr(generator, 'generate_ids'):
                # Generate additional tenant IDs
                tenant_ids = generator.generate_ids(self.config, pattern)
                result[f"tenant_{pattern.pattern_type.value}"] = tenant_ids
        
        # Generate cross-tenant test IDs
        if target_tenant:
            cross_tenant_ids = []
            
            # Generate variations of the target tenant
            for i in range(1, 11):
                cross_tenant_ids.extend([
                    f"{target_tenant}_{i}",
                    f"{target_tenant}-{i}",
                    f"{i}_{target_tenant}",
                    f"{target_tenant}{i}"
                ])
            
            result["cross_tenant_variations"] = cross_tenant_ids
        
        return result

    def generate_smart_id_list(
        self,
        known_ids: List[str],
        target_count: int = 1000,
        include_edge_cases: bool = True,
        include_privilege_escalation: bool = True,
        include_tenant_testing: bool = True
    ) -> List[str]:
        """
        Generate a comprehensive list of test IDs based on known examples.
        
        Args:
            known_ids: List of known/example IDs to analyze
            target_count: Maximum number of IDs to generate
            include_edge_cases: Whether to include edge case IDs
            include_privilege_escalation: Whether to include privilege escalation IDs
            include_tenant_testing: Whether to include tenant isolation IDs
            
        Returns:
            List of generated test IDs
        """
        all_ids = set()
        
        # Generate based on detected patterns
        pattern_results = self.generate_intelligent_ids(known_ids)
        for pattern_name, ids in pattern_results.items():
            all_ids.update(ids[:target_count // 4])  # Limit per pattern
            log_info(f"Added {len(ids)} IDs from pattern: {pattern_name}")
        
        # Add privilege escalation IDs
        if include_privilege_escalation:
            privilege_results = self.generate_privilege_aware_ids(known_ids)
            for pattern_name, ids in privilege_results.items():
                all_ids.update(ids[:target_count // 8])  # Smaller portion for privilege IDs
                log_info(f"Added {len(ids)} privilege escalation IDs: {pattern_name}")
        
        # Add tenant isolation IDs
        if include_tenant_testing:
            tenant_results = self.generate_tenant_isolation_ids(known_ids)
            for pattern_name, ids in tenant_results.items():
                all_ids.update(ids[:target_count // 8])  # Smaller portion for tenant IDs
                log_info(f"Added {len(ids)} tenant isolation IDs: {pattern_name}")
        
        # Add edge cases if requested
        if include_edge_cases:
            edge_cases = [
                "0", "1", "-1", "999999999", "2147483647", "-2147483648",
                "admin", "root", "null", "undefined", "", " ",
                "../../", "../admin", "admin..", ".admin"
            ]
            all_ids.update(edge_cases)
            log_info(f"Added {len(edge_cases)} edge case IDs")
        
        # Convert to list and limit size
        final_ids = list(all_ids)[:target_count]
        log_info(f"Generated {len(final_ids)} total unique IDs for testing")
        
        return final_ids


def create_id_generation_config(
    max_ids: int = 1000,
    enable_edge_cases: bool = True,
    custom_patterns: List[str] = None
) -> IDGenerationConfig:
    """Create a standard ID generation configuration."""
    return IDGenerationConfig(
        max_generated_ids=max_ids,
        include_edge_cases=enable_edge_cases,
        custom_patterns=custom_patterns or [],
        tenant_aware=True,
        privilege_aware=True
    )


def generate_smart_id_list(
    example_ids: List[str],
    max_total_ids: int = 1000,
    include_privilege_escalation: bool = True,
    include_tenant_testing: bool = True
) -> List[str]:
    """
    High-level function to generate a comprehensive list of test IDs.
    
    This is the main entry point for intelligent ID generation.
    """
    config = create_id_generation_config(max_ids=max_total_ids)
    generator = EnhancedIDGenerator(config)
    
    all_ids = set()
    
    # Generate based on detected patterns
    pattern_results = generator.generate_intelligent_ids(example_ids)
    for pattern_name, ids in pattern_results.items():
        all_ids.update(ids)
        log_info(f"Added {len(ids)} IDs from pattern: {pattern_name}")
    
    # Add privilege escalation IDs
    if include_privilege_escalation:
        privilege_results = generator.generate_privilege_aware_ids(example_ids)
        for pattern_name, ids in privilege_results.items():
            all_ids.update(ids)
            log_info(f"Added {len(ids)} privilege escalation IDs: {pattern_name}")
    
    # Add tenant isolation IDs
    if include_tenant_testing:
        tenant_results = generator.generate_tenant_isolation_ids(example_ids)
        for pattern_name, ids in tenant_results.items():
            all_ids.update(ids)
            log_info(f"Added {len(ids)} tenant isolation IDs: {pattern_name}")
    
    # Convert to list and limit size
    final_ids = list(all_ids)[:max_total_ids]
    log_info(f"Generated {len(final_ids)} total unique IDs for testing")
    
    return final_ids
