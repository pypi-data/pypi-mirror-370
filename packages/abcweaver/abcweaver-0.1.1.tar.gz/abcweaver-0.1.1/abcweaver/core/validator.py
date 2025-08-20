"""
📡 Caelus Format Validator

Comprehensive validation for ABC and MusicXML formats.
"""

from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
from .abc_parser import ABCParser
from .musicxml_handler import MusicXMLHandler
from ..utils.exceptions import ValidationError
from ..utils.helpers import detect_file_format


class ValidationResult:
    """Represents validation results with details"""
    
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings or []
        self.suggestions = []
    
    def add_suggestion(self, suggestion: str):
        """Add a suggestion for improvement"""
        self.suggestions.append(suggestion)
    
    def __str__(self):
        result = f"Valid: {self.is_valid}\\n"
        if self.errors:
            result += f"Errors: {len(self.errors)}\\n"
            for error in self.errors:
                result += f"  - {error}\\n"
        if self.warnings:
            result += f"Warnings: {len(self.warnings)}\\n"
            for warning in self.warnings:
                result += f"  - {warning}\\n"
        if self.suggestions:
            result += f"Suggestions: {len(self.suggestions)}\\n"
            for suggestion in self.suggestions:
                result += f"  - {suggestion}\\n"
        return result


class Validator:
    """
    Validates ABC and MusicXML files for syntax and structural correctness.
    """
    
    def __init__(self):
        self.abc_parser = ABCParser()
        self.musicxml_handler = MusicXMLHandler()
    
    def validate_file(self, file_path: str, file_format: Optional[str] = None) -> ValidationResult:
        """
        Validate a file (auto-detects format if not specified).
        
        Args:
            file_path: Path to file to validate
            file_format: File format ('abc' or 'musicxml'), auto-detected if None
            
        Returns:
            ValidationResult with detailed results
            
        Raises:
            ValidationError: If validation cannot be performed
        """
        try:
            # Detect format if not specified
            if not file_format:
                file_format = detect_file_format(file_path)
            
            if file_format == 'abc':
                return self.validate_abc_file(file_path)
            elif file_format == 'musicxml':
                return self.validate_musicxml_file(file_path)
            else:
                raise ValidationError(f"Unsupported file format: {file_format}")
                
        except Exception as e:
            return ValidationResult(False, [f"Validation failed: {e}"])
    
    def validate_abc_file(self, file_path: str) -> ValidationResult:
        """
        Validate ABC notation file.
        
        Args:
            file_path: Path to ABC file
            
        Returns:
            ValidationResult with detailed results
        """
        errors = []
        warnings = []
        
        try:
            # Check file exists and is readable
            if not Path(file_path).exists():
                return ValidationResult(False, [f"File does not exist: {file_path}"])
            
            # Parse ABC file
            parsed_abc = self.abc_parser.parse_abc_file(file_path)
            
            # Validate headers
            headers = parsed_abc['headers']
            if 'X' not in headers:
                warnings.append("Missing X: (index number) header")
            if 'T' not in headers:
                warnings.append("Missing T: (title) header")
            if 'K' not in headers:
                warnings.append("Missing K: (key signature) header")
            
            # Validate music content
            is_valid, syntax_errors = self.abc_parser.validate_abc_syntax(parsed_abc['raw_music'])
            errors.extend(syntax_errors)
            
            # Get suggestions
            suggestions = self.abc_parser.suggest_corrections(parsed_abc['raw_music'])
            
            # Additional checks
            if len(parsed_abc['notes']) == 0:
                errors.append("No musical notes found")
            elif len(parsed_abc['notes']) > 1000:
                warnings.append("Very long tune (>1000 notes) - consider splitting")
            
            # Check for common issues
            if '|' not in parsed_abc['raw_music'] and len(parsed_abc['notes']) > 8:
                warnings.append("No bar lines found in music - consider adding | for readability")
            
            result = ValidationResult(len(errors) == 0, errors, warnings)
            for suggestion in suggestions:
                result.add_suggestion(suggestion)
            
            return result
            
        except Exception as e:
            return ValidationResult(False, [f"ABC validation failed: {e}"])
    
    def validate_musicxml_file(self, file_path: str) -> ValidationResult:
        """
        Validate MusicXML file.
        
        Args:
            file_path: Path to MusicXML file
            
        Returns:
            ValidationResult with detailed results
        """
        errors = []
        warnings = []
        
        try:
            # Load and validate structure
            self.musicxml_handler.load_file(file_path)
            is_valid, structure_errors = self.musicxml_handler.validate_structure()
            errors.extend(structure_errors)
            
            # Get parts information
            parts_info = self.musicxml_handler.get_parts_info()
            
            if not parts_info:
                errors.append("No parts found in score")
            else:
                # Validate each part
                for part_info in parts_info:
                    part_id = part_info['id']
                    
                    if not part_info['name'] or part_info['name'] == 'Unknown Part':
                        warnings.append(f"Part {part_id} has no name")
                    
                    if part_info['measures'] == 0:
                        warnings.append(f"Part {part_id} has no measures")
                    elif part_info['measures'] > 200:
                        warnings.append(f"Part {part_id} has many measures ({part_info['measures']}) - file may be large")
            
            # Check for missing elements
            if not self.musicxml_handler.root.find('work'):
                warnings.append("Missing work information")
            
            if not self.musicxml_handler.root.find('identification'):
                warnings.append("Missing identification information")
            
            # Validate divisions consistency
            divisions_elements = self.musicxml_handler.root.findall('.//divisions')
            if divisions_elements:
                divisions_values = [int(elem.text) for elem in divisions_elements if elem.text]
                if len(set(divisions_values)) > 1:
                    warnings.append("Inconsistent divisions values across parts")
            
            result = ValidationResult(len(errors) == 0, errors, warnings)
            
            # Add suggestions
            if len(parts_info) == 1:
                result.add_suggestion("Single part score - consider adding harmony or accompaniment")
            
            return result
            
        except Exception as e:
            return ValidationResult(False, [f"MusicXML validation failed: {e}"])
    
    def validate_abc_string(self, abc_string: str) -> ValidationResult:
        """
        Validate ABC notation string.
        
        Args:
            abc_string: ABC notation string
            
        Returns:
            ValidationResult with results
        """
        try:
            is_valid, errors = self.abc_parser.validate_abc_syntax(abc_string)
            suggestions = self.abc_parser.suggest_corrections(abc_string)
            
            result = ValidationResult(is_valid, errors)
            for suggestion in suggestions:
                result.add_suggestion(suggestion)
            
            return result
            
        except Exception as e:
            return ValidationResult(False, [f"ABC string validation failed: {e}"])
    
    def repair_abc_file(self, file_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Attempt to repair common ABC file issues.
        
        Args:
            file_path: Path to ABC file
            output_path: Output path for repaired file (overwrites original if None)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Read original file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\\n')
            repaired_lines = []
            has_x_header = False
            has_t_header = False
            has_k_header = False
            
            # Track what headers we have
            for i, line in enumerate(lines):
                line = line.strip()
                
                if line.startswith('X:'):
                    has_x_header = True
                elif line.startswith('T:'):
                    has_t_header = True
                elif line.startswith('K:'):
                    has_k_header = True
                
                # Fix common issues
                if line and not line.startswith('%'):
                    # Fix spacing around colons in headers
                    if ':' in line and line[1] == ':' and not line[2:3].isspace():
                        parts = line.split(':', 1)
                        line = f"{parts[0]}: {parts[1]}"
                
                repaired_lines.append(line)
            
            # Add missing essential headers
            if not has_x_header:
                repaired_lines.insert(0, "X:1")
            if not has_t_header:
                repaired_lines.insert(-1 if has_k_header else len(repaired_lines), "T:Untitled")
            if not has_k_header:
                repaired_lines.insert(len(repaired_lines), "K:C major")
            
            # Write repaired file
            output = output_path or file_path
            with open(output, 'w', encoding='utf-8') as f:
                f.write('\\n'.join(repaired_lines))
            
            return True, f"File repaired and saved to {output}"
            
        except Exception as e:
            return False, f"Repair failed: {e}"
    
    def get_file_info(self, file_path: str, file_format: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive information about a music file.
        
        Args:
            file_path: Path to file
            file_format: File format, auto-detected if None
            
        Returns:
            Dictionary with file information
        """
        try:
            if not file_format:
                file_format = detect_file_format(file_path)
            
            file_stats = Path(file_path).stat()
            base_info = {
                'file_path': file_path,
                'format': file_format,
                'size_bytes': file_stats.st_size,
                'modified': file_stats.st_mtime,
            }
            
            if file_format == 'abc':
                abc_info = self.abc_parser.get_abc_info(
                    Path(file_path).read_text(encoding='utf-8')
                )
                base_info.update(abc_info)
            
            elif file_format == 'musicxml':
                self.musicxml_handler.load_file(file_path)
                parts_info = self.musicxml_handler.get_parts_info()
                base_info.update({
                    'parts_count': len(parts_info),
                    'parts': parts_info,
                    'total_measures': sum(p['measures'] for p in parts_info)
                })
            
            return base_info
            
        except Exception as e:
            return {'error': f"Failed to get file info: {e}"}