"""
📡 Caelus Helper Functions

Utility functions for common operations.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ValidationError
from .constants import ABC_DURATIONS, DEFAULT_DIVISIONS


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """
    Validate file path and return Path object.
    
    Args:
        file_path: Path to validate
        must_exist: Whether file must already exist
        
    Returns:
        Path object
        
    Raises:
        ValidationError: If path is invalid
    """
    path = Path(file_path)
    
    if must_exist and not path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    
    if must_exist and not path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")
    
    # Check parent directory exists for new files
    if not must_exist and not path.parent.exists():
        raise ValidationError(f"Parent directory does not exist: {path.parent}")
    
    return path


def format_duration(abc_duration: str, divisions: int = DEFAULT_DIVISIONS) -> int:
    """
    Convert ABC duration to MusicXML duration.
    
    Args:
        abc_duration: ABC duration string (e.g., '2', '4', '/2')
        divisions: MusicXML divisions per quarter note
        
    Returns:
        MusicXML duration value
    """
    if not abc_duration:
        abc_duration = '1'  # Default to eighth note
    
    # Handle fraction durations
    if abc_duration.startswith('/'):
        denominator = int(abc_duration[1:])
        base_duration = 1.0 / denominator
    else:
        base_duration = ABC_DURATIONS.get(abc_duration, 1)
    
    # Convert to MusicXML duration
    # In ABC, '1' = eighth note, '2' = quarter note
    # In MusicXML with divisions=2, quarter note = 2
    return int(base_duration * divisions)


def parse_metadata(metadata_str: Optional[str]) -> Dict[str, Any]:
    """
    Parse metadata string (JSON format) into dictionary.
    
    Args:
        metadata_str: JSON metadata string
        
    Returns:
        Parsed metadata dictionary
    """
    if not metadata_str:
        return {}
    
    try:
        return json.loads(metadata_str)
    except json.JSONDecodeError:
        # Try to parse simple key=value pairs
        metadata = {}
        for pair in metadata_str.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                metadata[key.strip()] = value.strip()
        return metadata


def get_default_clef_for_instrument(instrument: str) -> Dict[str, str]:
    """
    Get default clef configuration for instrument.
    
    Args:
        instrument: Instrument name
        
    Returns:
        Dictionary with clef sign and line
    """
    from .constants import INSTRUMENTS, CLEF_SIGNS
    
    instrument_lower = instrument.lower()
    
    if instrument_lower in INSTRUMENTS:
        clef_name = INSTRUMENTS[instrument_lower]['clef']
        return CLEF_SIGNS[clef_name]
    
    # Default to treble clef
    return CLEF_SIGNS['treble']


def sanitize_part_name(name: str, max_length: int = 20) -> str:
    """
    Sanitize part name for use in MusicXML.
    
    Args:
        name: Original part name
        max_length: Maximum length for abbreviation
        
    Returns:
        Sanitized name and abbreviation
    """
    # Remove invalid characters
    sanitized = ''.join(c for c in name if c.isalnum() or c in ' -_')
    
    # Create abbreviation
    words = sanitized.split()
    if len(words) > 1:
        abbrev = ''.join(word[:2].capitalize() for word in words[:2])
    else:
        abbrev = sanitized[:4].capitalize()
    
    return sanitized, abbrev + '.'


def detect_file_format(file_path: str) -> str:
    """
    Detect file format based on extension and content.
    
    Args:
        file_path: Path to file
        
    Returns:
        File format ('abc' or 'musicxml')
    """
    path = Path(file_path)
    
    # Check extension first
    if path.suffix.lower() in ['.abc']:
        return 'abc'
    elif path.suffix.lower() in ['.xml', '.musicxml', '.mxl']:
        return 'musicxml'
    
    # Check content if extension is ambiguous
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(100).strip()
            
        if content.startswith('<?xml') or '<score-partwise' in content:
            return 'musicxml'
        elif any(line.startswith(('X:', 'T:', 'M:', 'K:')) for line in content.split('\n')[:5]):
            return 'abc'
            
    except Exception:
        pass
    
    raise ValidationError(f"Cannot determine file format for: {file_path}")