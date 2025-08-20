"""
📡 Caelus ABC Parser

Enhanced ABC notation parsing with comprehensive note and duration support.
Based on proven abc_inserter.py logic.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from ..utils.exceptions import ABCParseError
from ..utils.constants import ABC_DURATIONS, ABC_OCTAVE_MODIFIERS, DEFAULT_DIVISIONS
from ..utils.helpers import format_duration


class ABCNote:
    """Represents a single ABC note with pitch and duration"""
    
    def __init__(self, pitch: str, duration: str = '1', is_rest: bool = False):
        self.pitch = pitch
        self.duration = duration
        self.is_rest = is_rest
        self.step = None
        self.octave = None
        
        if not is_rest:
            self._parse_pitch()
    
    def _parse_pitch(self):
        """Parse ABC pitch notation into step and octave"""
        if not self.pitch:
            return
            
        # Extract base note (first character)
        self.step = self.pitch[0].upper()
        
        # Determine base octave (C = 4, c = 5)
        if self.pitch[0].islower():
            self.octave = 5
        else:
            self.octave = 4
        
        # Apply octave modifiers
        apostrophes = self.pitch.count("'")
        commas = self.pitch.count(",")
        
        self.octave += apostrophes
        self.octave -= commas
    
    def get_musicxml_duration(self, divisions: int = DEFAULT_DIVISIONS) -> int:
        """Convert ABC duration to MusicXML duration"""
        return format_duration(self.duration, divisions)
    
    def __repr__(self):
        return f"ABCNote(pitch='{self.pitch}', duration='{self.duration}', rest={self.is_rest})"


class ABCParser:
    """
    Enhanced ABC notation parser for converting ABC strings to structured data.
    """
    
    def __init__(self):
        # Regex patterns for ABC parsing
        self.note_pattern = re.compile(r"([a-gA-GzZ][',]*)(\d*|/\d*)")
        self.header_pattern = re.compile(r"^([A-Z]):\s*(.+)$")
        
    def parse_abc_string(self, abc_string: str) -> List[ABCNote]:
        """
        Parse ABC notation string into list of ABCNote objects.
        
        Args:
            abc_string: ABC notation string
            
        Returns:
            List of ABCNote objects
            
        Raises:
            ABCParseError: If parsing fails
        """
        if not abc_string or not abc_string.strip():
            raise ABCParseError("Empty ABC string")
        
        notes = []
        
        try:
            # Find all notes and rests in the ABC string
            matches = self.note_pattern.findall(abc_string)
            
            for pitch, duration in matches:
                # Handle rests (z or Z)
                if pitch.lower().startswith('z'):
                    notes.append(ABCNote('', duration or '1', is_rest=True))
                else:
                    notes.append(ABCNote(pitch, duration or '1', is_rest=False))
            
            if not notes:
                raise ABCParseError("No valid notes found in ABC string")
                
            return notes
        
        except Exception as e:
            raise ABCParseError(f"Failed to parse ABC string: {e}")
    
    def parse_abc_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse complete ABC file with headers and multiple tunes.
        
        Args:
            file_path: Path to ABC file
            
        Returns:
            Dictionary with parsed ABC data
            
        Raises:
            ABCParseError: If file parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            raise ABCParseError(f"Cannot read ABC file {file_path}: {e}")
        
        return self.parse_abc_content(content)
    
    def parse_abc_content(self, content: str) -> Dict[str, Any]:
        """
        Parse ABC content with headers and music.
        
        Args:
            content: ABC file content
            
        Returns:
            Dictionary with headers and parsed notes
        """
        lines = content.strip().split('\n')
        headers = {}
        music_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
                
            # Check for header line
            header_match = self.header_pattern.match(line)
            if header_match:
                key, value = header_match.groups()
                headers[key] = value
            else:
                # Music line
                music_lines.append(line)
        
        # Parse music content
        music_content = ' '.join(music_lines)
        notes = self.parse_abc_string(music_content)
        
        return {
            'headers': headers,
            'notes': notes,
            'raw_music': music_content
        }
    
    def validate_abc_syntax(self, abc_string: str) -> Tuple[bool, List[str]]:
        """
        Validate ABC notation syntax.
        
        Args:
            abc_string: ABC notation to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not abc_string or not abc_string.strip():
            errors.append("Empty ABC string")
            return False, errors
        
        try:
            notes = self.parse_abc_string(abc_string)
            
            # Check for common issues
            if not notes:
                errors.append("No valid notes found")
            
            # Validate each note
            for i, note in enumerate(notes):
                if not note.is_rest:
                    if not note.step:
                        errors.append(f"Invalid note at position {i}: {note.pitch}")
                    if note.octave < 0 or note.octave > 9:
                        errors.append(f"Invalid octave at position {i}: {note.octave}")
        
        except ABCParseError as e:
            errors.append(str(e))
        
        return len(errors) == 0, errors
    
    def get_abc_info(self, abc_content: str) -> Dict[str, Any]:
        """
        Extract metadata and statistics from ABC content.
        
        Args:
            abc_content: ABC notation content
            
        Returns:
            Dictionary with ABC information
        """
        try:
            parsed = self.parse_abc_content(abc_content)
            notes = parsed['notes']
            
            # Count different elements
            note_count = len([n for n in notes if not n.is_rest])
            rest_count = len([n for n in notes if n.is_rest])
            
            # Get pitch range
            pitches = [n.octave * 12 + ord(n.step) - ord('C') 
                      for n in notes if not n.is_rest and n.octave is not None]
            
            info = {
                'headers': parsed['headers'],
                'total_notes': len(notes),
                'note_count': note_count,
                'rest_count': rest_count,
                'title': parsed['headers'].get('T', 'Untitled'),
                'key': parsed['headers'].get('K', 'C major'),
                'meter': parsed['headers'].get('M', '4/4'),
            }
            
            if pitches:
                info['pitch_range'] = {
                    'lowest': min(pitches),
                    'highest': max(pitches),
                    'span': max(pitches) - min(pitches)
                }
            
            return info
            
        except Exception as e:
            raise ABCParseError(f"Failed to analyze ABC content: {e}")
    
    def suggest_corrections(self, abc_string: str) -> List[str]:
        """
        Suggest corrections for common ABC notation errors.
        
        Args:
            abc_string: ABC notation with potential errors
            
        Returns:
            List of suggested corrections
        """
        suggestions = []
        
        # Check for common patterns that might be mistakes
        if re.search(r'[a-g][A-G]', abc_string):
            suggestions.append("Mixed case notes found - consider consistent octave notation")
        
        if re.search(r'\d{2,}', abc_string):
            suggestions.append("Multiple digit durations found - consider using standard durations (1,2,4,8)")
        
        if '|' not in abc_string and len(abc_string) > 20:
            suggestions.append("Long phrase without bar lines - consider adding | for measures")
        
        if abc_string.count('(') != abc_string.count(')'):
            suggestions.append("Unmatched parentheses for grace notes or tuplets")
        
        return suggestions