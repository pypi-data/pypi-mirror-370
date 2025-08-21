"""
Local Bloom Filter implementation for privacy-preserving attestation.
Data never leaves the user's system - only the bloom filter bytes are sent.
"""

import hashlib
import math
from typing import Optional


class BloomFilter:
    """
    Privacy-preserving bloom filter that runs entirely locally.
    Creates a one-way transformation of training data that can't be reversed.
    """
    
    def __init__(self, expected_items: int = 1_000_000, fp_rate: float = 0.0001):
        """
        Initialize bloom filter with optimal parameters.
        
        Args:
            expected_items: Expected number of items to add
            fp_rate: Desired false positive rate (0.0001 = 0.01%)
        """
        # Calculate optimal size and hash functions
        self.size_bits = int(-expected_items * math.log(fp_rate) / (math.log(2) ** 2))
        self.num_hashes = max(1, int(self.size_bits / expected_items * math.log(2)))
        
        # Initialize bit array
        self.size_bytes = (self.size_bits + 7) // 8
        self.bit_array = bytearray(self.size_bytes)
        self.items_added = 0
        self.expected_items = expected_items
        self.fp_rate = fp_rate
        
        # Silent initialization - no technical details shown
    
    def add(self, item: str):
        """
        Add item to bloom filter (runs entirely locally).
        
        Args:
            item: Text to add to filter
        """
        item_bytes = item.encode('utf-8')
        
        for i in range(self.num_hashes):
            # Create hash for this item
            hash_obj = hashlib.sha256(item_bytes + str(i).encode())
            hash_val = int.from_bytes(hash_obj.digest()[:8], 'big')
            
            # Set bit in array
            bit_pos = hash_val % self.size_bits
            byte_pos = bit_pos // 8
            bit_offset = bit_pos % 8
            self.bit_array[byte_pos] |= (1 << bit_offset)
        
        self.items_added += 1
    
    def contains(self, item: str) -> bool:
        """
        Check if item might be in bloom filter (local check).
        
        Args:
            item: Text to check
            
        Returns:
            True if item might be present, False if definitely not
        """
        item_bytes = item.encode('utf-8')
        
        for i in range(self.num_hashes):
            # Create hash for this item
            hash_obj = hashlib.sha256(item_bytes + str(i).encode())
            hash_val = int.from_bytes(hash_obj.digest()[:8], 'big')
            
            # Check bit in array
            bit_pos = hash_val % self.size_bits
            byte_pos = bit_pos // 8
            bit_offset = bit_pos % 8
            
            if not (self.bit_array[byte_pos] & (1 << bit_offset)):
                return False
        
        return True
    
    def to_bytes(self) -> bytes:
        """
        Serialize bloom filter to bytes for sending to cloud.
        This is a one-way transformation - original data cannot be recovered.
        
        Returns:
            Bloom filter as bytes
        """
        return bytes(self.bit_array)
    
    @classmethod
    def from_bytes(cls, data: bytes, expected_items: int = 1_000_000, 
                   fp_rate: float = 0.0001) -> 'BloomFilter':
        """
        Deserialize bloom filter from bytes.
        
        Args:
            data: Bloom filter bytes
            expected_items: Expected items (must match original)
            fp_rate: False positive rate (must match original)
            
        Returns:
            BloomFilter instance
        """
        bloom = cls(expected_items, fp_rate)
        bloom.bit_array = bytearray(data)
        return bloom
    
    def add_text_content(self, text: str, include_ngrams: bool = True):
        """
        Add text content to bloom filter with smart processing.
        
        Args:
            text: Text content to add
            include_ngrams: Whether to include n-grams for phrase detection
        """
        # Split into words
        words = text.split()
        
        # Add individual words (for word-level detection)
        for word in words:
            if len(word) > 2:  # Skip very short words
                self.add(word.lower())
        
        if include_ngrams:
            # Add 3-word phrases (for copyright phrase detection)
            for i in range(len(words) - 2):
                trigram = ' '.join(words[i:i+3]).lower()
                self.add(trigram)
            
            # Add 5-word phrases (for longer phrase detection)
            for i in range(len(words) - 4):
                fivegram = ' '.join(words[i:i+5]).lower()
                self.add(fivegram)
        
        # Processing complete - no verbose output