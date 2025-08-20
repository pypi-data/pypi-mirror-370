"""Serialization utilities for Avro messages."""

import io
import os
import struct
import json
import logging
import avro.schema
import avro.io
import lz4.frame
from avro.io import DatumWriter, DatumReader, BinaryEncoder, BinaryDecoder
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class AvroSerializer:
    """Utility class for serializing and deserializing Avro messages."""
    
    def __init__(self, schema_id: int, schema: avro.schema.Schema):
        """
        Initialize the Avro serializer.
        
        Args:
            schema_id: Schema ID
            schema: Avro schema
        """
        self.schema_id = schema_id
        self.schema = schema
    
    def serialize(self, data: dict) -> bytes:
        """
        Serialize data using Avro schema without compression.
        
        Args:
            data: Data to serialize
        Returns:
            Serialized bytes
        """
        try:
            # Create a buffer to write the serialized data
            buffer = io.BytesIO()
            
            # Write the magic byte (0) and schema ID (4 bytes)
            buffer.write(struct.pack('>bI', 0, self.schema_id))
            
            # Create Avro writer and encoder
            writer = DatumWriter(self.schema)
            # Write the data
            writer.write(data, BinaryEncoder(buffer))
            return buffer.getvalue()

            
        except Exception as e:
            raise RuntimeError(f"Failed to serialize data: {str(e)}")
    
    def deserialize(self, message_value: bytes) -> Dict[str, Any]:
        """
        Deserialize Avro message without LZ4 decompression.
        
        Args:
            message_value: Serialized message bytes

        Returns:
            Deserialized data dictionary
        """
        try:
            # Skip the magic byte (1 byte) and schema ID (4 bytes)
            if len(message_value) < 5:
                raise ValueError("Message too short to contain magic byte and schema ID")
            
            # Extract magic byte and schema ID
            magic_byte, schema_id = struct.unpack('>bI', message_value[:5])
            
            if magic_byte != 0:
                raise ValueError(f"Invalid magic byte: {magic_byte}")
            
            # Get the actual Avro data (skip the first 5 bytes)
            avro_data = message_value[5:]
            
            # Create Avro reader and decoder
            reader = DatumReader(self.schema)
            decoder = BinaryDecoder(io.BytesIO(avro_data))
            # Read the data
            return reader.read(decoder)
            
        except Exception as e:
            raise RuntimeError(f"Failed to deserialize message: {str(e)}")
    
    def serialize_with_compression(self, data: dict) -> bytes:
        """
        Serialize data using Avro schema with LZ4 compression.
        
        Args:
            data: Data to serialize
        Returns:
            Serialized and compressed bytes
        """
        try:
            # First serialize without compression
            serialized_data = self.serialize(data)
            
            # Then compress with LZ4
            compressed_data = lz4.frame.compress(serialized_data)
            return compressed_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to serialize and compress data: {str(e)}")
    
    def deserialize_with_decompression(self, message_value: bytes) -> Dict[str, Any]:
        """
        Deserialize Avro message with LZ4 decompression.
        
        Args:
            message_value: Compressed and serialized message bytes

        Returns:
            Deserialized data dictionary
        """
        try:
            # First decompress with LZ4
            decompressed_data = lz4.frame.decompress(message_value)
            
            # Then deserialize
            return self.deserialize(decompressed_data)
            
        except Exception as e:
            raise RuntimeError(f"Failed to decompress and deserialize message: {str(e)}")

