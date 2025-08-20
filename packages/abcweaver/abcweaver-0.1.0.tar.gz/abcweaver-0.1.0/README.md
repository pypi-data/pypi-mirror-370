# 🎼 ABCWeaver - ABC ↔ MusicXML Transformation Engine

**ABCWeaver** is a powerful Python package for bidirectional transformation between ABC notation and MusicXML format, enhanced with Redis stream processing capabilities through the `nyro` package.

## ✨ Features

- **Bidirectional Conversion**: ABC ↔ MusicXML with full musical integrity
- **Redis Streams**: Enhanced processing through `nyro` package integration
- **CLI Interface**: Intuitive command-line tools for all operations
- **Customer Processing**: Stream-based customer-specific enhancements
- **Validation**: Comprehensive syntax checking for both formats
- **Batch Operations**: Process multiple files efficiently

## 🚀 Installation

```bash
pip install abcweaver
```

For development:
```bash
pip install abcweaver[dev]
```

## 📖 Quick Start

### Create MusicXML from ABC
```bash
abcweaver create "C D E F G A B c" --output melody.musicxml --title "Simple Scale"
```

### Insert ABC into existing MusicXML
```bash
abcweaver insert score.musicxml "G2 A2 B2 c2" --part "Melody" --instrument "Flute"
```

### Extract ABC from MusicXML
```bash
abcweaver extract score.musicxml --part "P1" --output melody.abc
```

### Stream Processing with Redis
```bash
# Send ABC to Redis stream
abcweaver stream-send "C D E F" --stream "song_evolution" 

# Consume and process
abcweaver stream-consume --stream "song_evolution" --target output.musicxml
```

## 🏗️ Architecture

ABCWeaver is built with modular architecture:

- **Core**: ABC parsing, MusicXML handling, format conversion
- **Streams**: Redis integration via `nyro` package
- **Commands**: CLI interface for all operations
- **Utils**: Helper functions and constants

## 🔧 Dependencies

- `click`: CLI framework
- `lxml`: XML processing
- `nyro`: Redis stream management
- `pydantic`: Data validation
- `rich`: Beautiful CLI output

## 🎼 Use Cases

- **Music Composition**: Convert ABC notation to professional MusicXML scores
- **Score Analysis**: Extract ABC patterns from existing MusicXML files
- **Stream Processing**: Real-time musical data transformation via Redis
- **Batch Conversion**: Process large collections of musical notation
- **Educational Tools**: Bridge between simple ABC and complex MusicXML formats

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📡 G.Music Assembly

Part of the G.Music Assembly ecosystem - transforming musical creativity through collaborative AI orchestration.

**♠️🌿🎸🧵 Assembly Mode Engaged**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.