"""
📡 Caelus Format Converter

Bidirectional conversion between ABC notation and MusicXML.
Integrates ABCParser and MusicXMLHandler for seamless transformation.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from .abc_parser import ABCParser, ABCNote
from .musicxml_handler import MusicXMLHandler
from ..utils.exceptions import ConversionError
from ..utils.constants import DEFAULT_DIVISIONS
from ..utils.helpers import get_default_clef_for_instrument


class Converter:
    """
    Handles bidirectional conversion between ABC and MusicXML formats.
    """
    
    def __init__(self):
        self.abc_parser = ABCParser()
        self.musicxml_handler = MusicXMLHandler()
    
    def abc_to_musicxml_notes(self, abc_string: str, divisions: int = DEFAULT_DIVISIONS) -> List[ET.Element]:
        """
        Convert ABC notation string to MusicXML note elements.
        
        Args:
            abc_string: ABC notation string
            divisions: MusicXML divisions per quarter note
            
        Returns:
            List of MusicXML note elements
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            # Parse ABC string
            abc_notes = self.abc_parser.parse_abc_string(abc_string)
            xml_notes = []
            
            for abc_note in abc_notes:
                note_element = ET.Element('note')
                
                if abc_note.is_rest:
                    # Create rest
                    ET.SubElement(note_element, 'rest')
                else:
                    # Create pitch
                    pitch_element = ET.SubElement(note_element, 'pitch')
                    ET.SubElement(pitch_element, 'step').text = abc_note.step
                    ET.SubElement(pitch_element, 'octave').text = str(abc_note.octave)
                
                # Add duration
                duration = abc_note.get_musicxml_duration(divisions)
                ET.SubElement(note_element, 'duration').text = str(duration)
                
                xml_notes.append(note_element)
            
            return xml_notes
            
        except Exception as e:
            raise ConversionError(f"Failed to convert ABC to MusicXML notes: {e}")
    
    def insert_abc_into_musicxml(self, musicxml_file: str, abc_string: str, 
                                part_name: str, instrument_name: str,
                                clef_sign: str = 'G', clef_line: str = '2') -> str:
        """
        Insert ABC notation as a new part in existing MusicXML file.
        
        Args:
            musicxml_file: Path to MusicXML file
            abc_string: ABC notation to insert
            part_name: Name for the new part
            instrument_name: Instrument name
            clef_sign: Clef sign (G, F, C)
            clef_line: Clef line number
            
        Returns:
            ID of the newly created part
            
        Raises:
            ConversionError: If insertion fails
        """
        try:
            # Load MusicXML file
            self.musicxml_handler.load_file(musicxml_file)
            
            # Get default clef for instrument if not specified
            if clef_sign == 'G' and clef_line == '2':
                default_clef = get_default_clef_for_instrument(instrument_name)
                clef_sign = default_clef['sign']
                clef_line = default_clef['line']
            
            # Add new part
            new_part_id = self.musicxml_handler.add_new_part(
                part_name, instrument_name, clef_sign, clef_line
            )
            
            # Convert ABC to MusicXML notes
            divisions = self.musicxml_handler.get_divisions()
            xml_notes = self.abc_to_musicxml_notes(abc_string, divisions)
            
            # Find the new part and its first measure
            part_element = self.musicxml_handler.root.find(f".//part[@id='{new_part_id}']")
            measure = part_element.find('measure[@number="1"]')
            
            # Add notes to the measure
            for note in xml_notes:
                measure.append(note)
            
            # Save the file
            self.musicxml_handler.save_file()
            
            return new_part_id
            
        except Exception as e:
            raise ConversionError(f"Failed to insert ABC into MusicXML: {e}")
    
    def create_musicxml_from_abc(self, abc_content: str, output_path: str,
                                title: str = "Untitled", composer: str = "Caelus") -> None:
        """
        Create a new MusicXML file from ABC notation.
        
        Args:
            abc_content: ABC notation content (with or without headers)
            output_path: Output MusicXML file path
            title: Score title
            composer: Composer name
            
        Raises:
            ConversionError: If creation fails
        """
        try:
            # Parse ABC content
            parsed_abc = self.abc_parser.parse_abc_content(abc_content)
            
            # Use headers from ABC if available
            headers = parsed_abc['headers']
            actual_title = headers.get('T', title)
            actual_composer = headers.get('C', composer)
            
            # Create new MusicXML score
            self.musicxml_handler.create_new_score(actual_title, actual_composer)
            
            # Add the ABC content as the first part
            part_id = self.musicxml_handler.add_new_part(
                actual_title, "Piano", 'G', '2'
            )
            
            # Convert ABC notes to MusicXML
            xml_notes = self.abc_to_musicxml_notes(parsed_abc['raw_music'])
            
            # Add notes to the part
            part_element = self.musicxml_handler.root.find(f".//part[@id='{part_id}']")
            measure = part_element.find('measure[@number="1"]')
            
            for note in xml_notes:
                measure.append(note)
            
            # Save the file
            self.musicxml_handler.save_file(output_path)
            
        except Exception as e:
            raise ConversionError(f"Failed to create MusicXML from ABC: {e}")
    
    def extract_abc_from_musicxml(self, musicxml_file: str, part_id: Optional[str] = None,
                                 measures: Optional[str] = None) -> str:
        """
        Extract ABC notation from MusicXML file.
        
        Args:
            musicxml_file: Path to MusicXML file
            part_id: Specific part ID to extract (None for all parts)
            measures: Measure range (e.g., "1-8")
            
        Returns:
            ABC notation string
            
        Raises:
            ConversionError: If extraction fails
        """
        try:
            # Load MusicXML file
            self.musicxml_handler.load_file(musicxml_file)
            
            if part_id:
                # Extract specific part
                abc_content = self.musicxml_handler.extract_part_as_abc(part_id)
                
                # Get part info for headers
                parts_info = self.musicxml_handler.get_parts_info()
                part_info = next((p for p in parts_info if p['id'] == part_id), {})
                
                # Create ABC with headers
                abc_lines = [
                    "X:1",
                    f"T:{part_info.get('name', 'Extracted Part')}",
                    "M:4/4",
                    "L:1/8", 
                    "K:C major",
                    abc_content
                ]
                
                return "\\n".join(abc_lines)
            else:
                # Extract all parts
                parts_info = self.musicxml_handler.get_parts_info()
                all_abc_parts = []
                
                for i, part_info in enumerate(parts_info, 1):
                    abc_content = self.musicxml_handler.extract_part_as_abc(part_info['id'])
                    
                    abc_lines = [
                        f"X:{i}",
                        f"T:{part_info['name']}",
                        "M:4/4",
                        "L:1/8",
                        "K:C major",
                        abc_content,
                        ""  # Blank line between tunes
                    ]
                    
                    all_abc_parts.extend(abc_lines)
                
                return "\\n".join(all_abc_parts)
                
        except Exception as e:
            raise ConversionError(f"Failed to extract ABC from MusicXML: {e}")
    
    def convert_file(self, input_path: str, output_path: str, 
                    input_format: str, output_format: str,
                    part_id: Optional[str] = None) -> None:
        """
        Convert between ABC and MusicXML file formats.
        
        Args:
            input_path: Input file path
            output_path: Output file path  
            input_format: Input format ('abc' or 'musicxml')
            output_format: Output format ('abc' or 'musicxml')
            part_id: Specific part for MusicXML → ABC conversion
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            if input_format == 'abc' and output_format == 'musicxml':
                # ABC → MusicXML
                with open(input_path, 'r', encoding='utf-8') as f:
                    abc_content = f.read()
                
                self.create_musicxml_from_abc(abc_content, output_path)
                
            elif input_format == 'musicxml' and output_format == 'abc':
                # MusicXML → ABC
                abc_content = self.extract_abc_from_musicxml(input_path, part_id)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(abc_content)
            
            else:
                raise ConversionError(f"Unsupported conversion: {input_format} → {output_format}")
                
        except Exception as e:
            raise ConversionError(f"File conversion failed: {e}")
    
    def batch_insert_abc(self, musicxml_file: str, abc_files: List[str],
                        instrument_names: Optional[List[str]] = None) -> List[str]:
        """
        Insert multiple ABC files as parts in MusicXML.
        
        Args:
            musicxml_file: Target MusicXML file
            abc_files: List of ABC file paths
            instrument_names: Optional list of instrument names
            
        Returns:
            List of created part IDs
            
        Raises:
            ConversionError: If batch insertion fails
        """
        part_ids = []
        
        try:
            # Load MusicXML once
            self.musicxml_handler.load_file(musicxml_file)
            
            for i, abc_file in enumerate(abc_files):
                # Read ABC file
                with open(abc_file, 'r', encoding='utf-8') as f:
                    abc_content = f.read()
                
                # Parse for title
                parsed = self.abc_parser.parse_abc_content(abc_content)
                part_name = parsed['headers'].get('T', f'Part {i+1}')
                
                # Determine instrument
                if instrument_names and i < len(instrument_names):
                    instrument = instrument_names[i]
                else:
                    instrument = 'Piano'
                
                # Get clef for instrument
                clef_info = get_default_clef_for_instrument(instrument)
                
                # Add part
                part_id = self.musicxml_handler.add_new_part(
                    part_name, instrument, clef_info['sign'], clef_info['line']
                )
                
                # Convert and add notes
                divisions = self.musicxml_handler.get_divisions()
                xml_notes = self.abc_to_musicxml_notes(parsed['raw_music'], divisions)
                
                # Add to part
                part_element = self.musicxml_handler.root.find(f".//part[@id='{part_id}']")
                measure = part_element.find('measure[@number="1"]')
                
                for note in xml_notes:
                    measure.append(note)
                
                part_ids.append(part_id)
            
            # Save once at the end
            self.musicxml_handler.save_file()
            
            return part_ids
            
        except Exception as e:
            raise ConversionError(f"Batch ABC insertion failed: {e}")