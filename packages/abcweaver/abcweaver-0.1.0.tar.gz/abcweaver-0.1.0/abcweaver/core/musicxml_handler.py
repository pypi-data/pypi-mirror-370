"""
📡 Caelus MusicXML Handler

Robust MusicXML file reading, writing, and manipulation.
Based on proven abc_inserter.py XML handling.
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from ..utils.exceptions import MusicXMLError
from ..utils.constants import CLEF_SIGNS, DEFAULT_DIVISIONS, KEY_SIGNATURES, TIME_SIGNATURES
from ..utils.helpers import validate_file_path, get_default_clef_for_instrument, sanitize_part_name


class MusicXMLHandler:
    """
    Handles MusicXML file operations including reading, writing, and manipulation.
    """
    
    def __init__(self):
        self.root = None
        self.tree = None
        self.file_path = None
    
    def load_file(self, file_path: str) -> None:
        """
        Load MusicXML file for processing.
        
        Args:
            file_path: Path to MusicXML file
            
        Raises:
            MusicXMLError: If file cannot be loaded or parsed
        """
        try:
            path = validate_file_path(file_path, must_exist=True)
            self.file_path = path
            self.tree = ET.parse(str(path))
            self.root = self.tree.getroot()
            
            # Validate it's a MusicXML file
            if self.root.tag not in ['score-partwise', 'score-timewise']:
                raise MusicXMLError(f"Not a valid MusicXML file: {file_path}")
                
        except ET.ParseError as e:
            raise MusicXMLError(f"XML parsing error in {file_path}: {e}")
        except Exception as e:
            raise MusicXMLError(f"Failed to load MusicXML file {file_path}: {e}")
    
    def create_new_score(self, title: str = "Untitled", composer: str = "Caelus") -> None:
        """
        Create a new empty MusicXML score.
        
        Args:
            title: Score title
            composer: Composer name
        """
        # Create root element
        self.root = ET.Element('score-partwise', version="3.1")
        
        # Add work information
        work = ET.SubElement(self.root, 'work')
        ET.SubElement(work, 'work-title').text = title
        
        # Add identification
        identification = ET.SubElement(self.root, 'identification')
        creator = ET.SubElement(identification, 'creator', type="composer")
        creator.text = composer
        
        encoding = ET.SubElement(identification, 'encoding')
        software = ET.SubElement(encoding, 'software')
        software.text = "Caelus Music Engine"
        
        # Create empty part-list
        part_list = ET.SubElement(self.root, 'part-list')
        
        self.tree = ET.ElementTree(self.root)
    
    def save_file(self, output_path: Optional[str] = None) -> None:
        """
        Save current MusicXML to file with pretty formatting.
        
        Args:
            output_path: Output file path (uses loaded file path if None)
            
        Raises:
            MusicXMLError: If save operation fails
        """
        if not self.root:
            raise MusicXMLError("No MusicXML data to save")
        
        save_path = output_path or self.file_path
        if not save_path:
            raise MusicXMLError("No output path specified")
        
        try:
            # Create pretty-formatted XML
            rough_string = ET.tostring(self.root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_string = reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')
            
            # Remove blank lines that minidom adds
            pretty_string = "\\n".join(line for line in pretty_string.split('\\n') if line.strip())
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(pretty_string)
                
        except Exception as e:
            raise MusicXMLError(f"Failed to save MusicXML file: {e}")
    
    def get_parts_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all parts in the score.
        
        Returns:
            List of dictionaries with part information
        """
        if not self.root:
            raise MusicXMLError("No MusicXML data loaded")
        
        part_list = self.root.find('part-list')
        if part_list is None:
            return []
        
        parts_info = []
        for score_part in part_list.findall('score-part'):
            part_id = score_part.get('id', '')
            part_name = score_part.findtext('part-name', 'Unknown Part')
            instrument_name = score_part.findtext('.//instrument-name', 'Unknown Instrument')
            
            # Get part data statistics
            part_element = self.root.find(f".//part[@id='{part_id}']")
            measure_count = len(part_element.findall('measure')) if part_element is not None else 0
            
            parts_info.append({
                'id': part_id,
                'name': part_name,
                'instrument': instrument_name,
                'measures': measure_count
            })
        
        return parts_info
    
    def add_new_part(self, part_name: str, instrument_name: str, 
                     clef_sign: str = 'G', clef_line: str = '2') -> str:
        """
        Add a new empty part to the score.
        
        Args:
            part_name: Name of the new part
            instrument_name: Instrument name
            clef_sign: Clef sign (G, F, C)
            clef_line: Clef line number
            
        Returns:
            New part ID
            
        Raises:
            MusicXMLError: If part cannot be added
        """
        if not self.root:
            raise MusicXMLError("No MusicXML data loaded")
        
        part_list = self.root.find('part-list')
        if part_list is None:
            raise MusicXMLError("No part-list found in MusicXML")
        
        # Determine new part ID
        existing_parts = part_list.findall('score-part')
        new_part_id = f"P{len(existing_parts) + 1}"
        
        # Sanitize names
        clean_name, abbreviation = sanitize_part_name(part_name)
        
        # Add to part-list
        new_score_part = ET.Element('score-part', id=new_part_id)
        ET.SubElement(new_score_part, 'part-name').text = clean_name
        ET.SubElement(new_score_part, 'part-abbreviation').text = abbreviation
        
        score_instrument = ET.SubElement(new_score_part, 'score-instrument', id=f"{new_part_id}-I1")
        ET.SubElement(score_instrument, 'instrument-name').text = instrument_name
        
        part_list.append(new_score_part)
        
        # Create empty part with basic attributes
        new_part = ET.Element('part', id=new_part_id)
        measure = ET.SubElement(new_part, 'measure', number='1')
        
        # Copy attributes from P1 if it exists, otherwise create basic ones
        p1_attributes = self.root.find(".//part[@id='P1']//attributes")
        if p1_attributes is not None:
            attributes = ET.fromstring(ET.tostring(p1_attributes))  # Deep copy
            
            # Update clef
            clef_element = attributes.find('clef')
            if clef_element is not None:
                clef_element.find('sign').text = clef_sign
                clef_element.find('line').text = clef_line
        else:
            # Create basic attributes
            attributes = ET.Element('attributes')
            ET.SubElement(attributes, 'divisions').text = str(DEFAULT_DIVISIONS)
            
            # Add key signature (default C major)
            key = ET.SubElement(attributes, 'key')
            ET.SubElement(key, 'fifths').text = '0'
            
            # Add time signature (default 4/4)
            time = ET.SubElement(attributes, 'time')
            ET.SubElement(time, 'beats').text = '4'
            ET.SubElement(time, 'beat-type').text = '4'
            
            # Add clef
            clef = ET.SubElement(attributes, 'clef')
            ET.SubElement(clef, 'sign').text = clef_sign
            ET.SubElement(clef, 'line').text = clef_line
        
        measure.append(attributes)
        self.root.append(new_part)
        
        return new_part_id
    
    def extract_part_as_abc(self, part_id: str) -> str:
        """
        Extract a part and convert to ABC notation.
        
        Args:
            part_id: ID of part to extract
            
        Returns:
            ABC notation string
            
        Raises:
            MusicXMLError: If part extraction fails
        """
        if not self.root:
            raise MusicXMLError("No MusicXML data loaded")
        
        part_element = self.root.find(f".//part[@id='{part_id}']")
        if part_element is None:
            raise MusicXMLError(f"Part {part_id} not found")
        
        abc_notes = []
        
        # Process each measure
        for measure in part_element.findall('measure'):
            # Process each note
            for note in measure.findall('note'):
                if note.find('rest') is not None:
                    # Rest
                    duration = self._get_note_duration(note)
                    abc_notes.append(f"z{duration}")
                else:
                    # Regular note
                    pitch_element = note.find('pitch')
                    if pitch_element is not None:
                        step = pitch_element.findtext('step', 'C')
                        octave = int(pitch_element.findtext('octave', '4'))
                        duration = self._get_note_duration(note)
                        
                        # Convert to ABC notation
                        abc_pitch = self._musicxml_to_abc_pitch(step, octave)
                        abc_notes.append(f"{abc_pitch}{duration}")
        
        return ' '.join(abc_notes)
    
    def _get_note_duration(self, note_element: ET.Element) -> str:
        """Convert MusicXML duration to ABC duration string"""
        duration = int(note_element.findtext('duration', '1'))
        
        # Convert based on divisions (assuming DEFAULT_DIVISIONS = 2)
        if duration == 1:
            return '1'  # eighth note
        elif duration == 2:
            return '2'  # quarter note
        elif duration == 4:
            return '4'  # half note
        elif duration == 8:
            return '8'  # whole note
        else:
            return str(duration // DEFAULT_DIVISIONS)
    
    def _musicxml_to_abc_pitch(self, step: str, octave: int) -> str:
        """Convert MusicXML pitch to ABC notation"""
        # ABC uses C,D,E,F,G,A,B for octave 3, c,d,e,f,g,a,b for octave 4
        if octave <= 3:
            abc_pitch = step.upper()
            # Add commas for lower octaves
            commas = 3 - octave
            abc_pitch += ',' * commas
        elif octave == 4:
            abc_pitch = step.upper()
        elif octave == 5:
            abc_pitch = step.lower()
        else:
            abc_pitch = step.lower()
            # Add apostrophes for higher octaves
            apostrophes = octave - 5
            abc_pitch += "'" * apostrophes
        
        return abc_pitch
    
    def get_divisions(self) -> int:
        """Get the divisions value from the first part"""
        if not self.root:
            return DEFAULT_DIVISIONS
        
        divisions_text = self.root.findtext(".//divisions", str(DEFAULT_DIVISIONS))
        return int(divisions_text)
    
    def validate_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate MusicXML structure.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not self.root:
            errors.append("No MusicXML data loaded")
            return False, errors
        
        # Check root element
        if self.root.tag not in ['score-partwise', 'score-timewise']:
            errors.append(f"Invalid root element: {self.root.tag}")
        
        # Check for part-list
        part_list = self.root.find('part-list')
        if part_list is None:
            errors.append("Missing part-list element")
        else:
            # Check that all parts in part-list have corresponding part elements
            for score_part in part_list.findall('score-part'):
                part_id = score_part.get('id')
                if not part_id:
                    errors.append("score-part missing id attribute")
                    continue
                
                part_element = self.root.find(f".//part[@id='{part_id}']")
                if part_element is None:
                    errors.append(f"Part {part_id} declared in part-list but not found in score")
        
        return len(errors) == 0, errors