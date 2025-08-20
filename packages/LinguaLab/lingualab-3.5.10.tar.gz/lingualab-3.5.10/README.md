# LinguaLab

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/LinguaLab.svg)](https://pypi.org/project/LinguaLab/)

**LinguaLab** is a comprehensive multilingual text and voice processing toolkit designed for language translation, speech recognition, and text processing tasks. The package provides robust tools for translating text between languages and transcribing audio/video files using advanced AI services.

## Features

- **Text Translation**:
  - Multi-language text translation using Google Translate API
  - Automatic language detection
  - Fallback to alternative translation services
  - Support for bulk translations and nested text structures
  - Configurable translation providers and parameters

- **Speech Recognition**:
  - Audio/video file transcription using IBM Watson Speech-to-Text
  - Support for multiple audio formats (WAV, MP3, etc.)
  - High-accuracy transcription with confidence scoring
  - Batch processing capabilities
  - Configurable transcription parameters

- **Language Processing**:
  - Comprehensive language detection
  - Pronunciation assistance
  - Confidence scoring for translations
  - Error handling and fallback mechanisms

- **Defensive Programming**:
  - Automatic nested list flattening for text inputs
  - Comprehensive parameter validation
  - Enhanced error handling with detailed diagnostics
  - Type safety with modern Python annotations

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **External Tools** (required for full functionality):
  - Microphone access (for speech recognition features)
  - Internet connection (for translation services)

- **Required Third-Party Libraries**:

  ```bash
  pip install numpy pandas SpeechRecognition googletrans gTTS
  ```

  Or via Anaconda (recommended channel: `conda-forge`):

  ```bash
  conda install -c conda-forge numpy pandas
  pip install SpeechRecognition googletrans gTTS
  ```

- **Internal Package Dependencies**:

  ```bash
  pip install filewise paramlib
  pip install pygenutils                    # Core functionality
  pip install pygenutils[arrow]             # With arrow support (optional)
  ```

### For regular users (from PyPI)

```bash
pip install lingualab
```

### For contributors/developers (with latest Git versions)

```bash
# Install with development dependencies (includes latest Git versions)
pip install -e .[dev]

# Alternative: Use requirements-dev.txt for explicit Git dependencies
pip install -r requirements-dev.txt
pip install -e .
```

**Benefits of the new approach:**

- **Regular users**: Simple `pip install lingualab` with all dependencies included
- **Developers**: Access to latest Git versions for development and testing
- **PyPI compatibility**: All packages can be published without Git dependency issues

**If you encounter import errors:**

1. **For PyPI users**: The package should install all dependencies automatically. If you get import errors, try:

   ```bash
   pip install --upgrade lingualab
   ```

2. **For developers**: Make sure you've installed the development dependencies:

   ```bash
   pip install -e .[dev]
   ```

3. **Common issues**:
   - **Missing dependencies**: For regular users, all dependencies are included. For developers, use `pip install -e .[dev]`
   - **Python version**: Ensure you're using Python 3.10 or higher
   - **Speech recognition**: Ensure microphone access is granted for speech features

### Verify Installation

To verify that your installation is working correctly:

```python
try:
    import LinguaLab
    from filewise.file_operations.path_utils import find_files
    from pygenutils.arrays_and_lists.data_manipulation import flatten_list
    from paramlib.global_parameters import COMMON_DELIMITER_LIST
    
    print("✅ All imports successful!")
    print(f"✅ LinguaLab version: {LinguaLab.__version__}")
    print("✅ Installation is working correctly.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 For regular users: pip install lingualab")
    print("💡 For developers: pip install -e .[dev]")
```

## Usage

### Text Translation Example

```python
from LinguaLab.text_translations import translate_string

# Translate a single phrase
result = translate_string(
    phrase_or_words="Hello, how are you?",
    lang_origin="en",
    lang_translation="es"
)
print(result.text)  # "Hola, ¿cómo estás?"

# Translate multiple phrases
phrases = ["Good morning", "Good afternoon", "Good evening"]
results = translate_string(
    phrase_or_words=phrases,
    lang_origin="en",
    lang_translation="fr"
)
for result in results:
    print(result.text)

# Handle nested lists automatically
nested_phrases = [
    ["Hello", "Goodbye"],
    ["Thank you", "Please"],
    "Welcome"
]
results = translate_string(
    phrase_or_words=nested_phrases,
    lang_origin="en",
    lang_translation="de"
)
```

### Language Detection Example

```python
from LinguaLab.text_translations import translate_string

# Detect language of text
detection = translate_string(
    phrase_or_words="Bonjour, comment allez-vous?",
    lang_origin="auto",
    procedure="detect",
    text_which_language_to_detect="Bonjour, comment allez-vous?"
)
print(f"Detected language: {detection.lang}")
print(f"Confidence: {detection.confidence}")
```

### Speech Recognition Example

```python
from LinguaLab.transcribe_video_files import save_transcription_in_file

# Note: Requires IBM Watson API credentials
# Set up your API_KEY and SERVICE_ID in the module

# The module automatically processes WAV files in the specified directory
# and can save transcriptions to text files
```

## Project Structure

The package is organised as a focused language processing toolkit:

```text
LinguaLab/
├── text_translations.py      # Text translation and language detection
├── transcribe_video_files.py # Speech recognition and transcription
├── __init__.py              # Package initialisation
└── README.md                # Package documentation
```

## Key Functions

### `translate_string()`

**Purpose**: Translate text between languages using multiple translation services

**Key Features**:

- Supports single strings, lists, and nested lists of text
- Automatic fallback between translation services
- Language detection capabilities
- Configurable translation parameters
- Comprehensive error handling

**Parameters**:

- `phrase_or_words`: Text to translate (supports nested lists)
- `lang_origin`: Source language code
- `lang_translation`: Target language code (default: "en")
- `procedure`: "translate" or "detect"
- `provider`: Translation service provider
- `print_attributes`: Whether to print detailed results

### `save_transcription_in_file()`

**Purpose**: Save speech transcription results to text files

**Key Features**:

- Automatic file extension handling
- Progress reporting
- Error handling and validation
- Flexible output formatting

## Advanced Features

### Defensive Programming

- **Nested List Support**: Automatically flattens complex nested text structures
- **Parameter Validation**: Comprehensive input validation with detailed error messages
- **Type Safety**: Modern Python type annotations (PEP-604) for better IDE support
- **Error Handling**: Detailed error reporting for debugging

### Service Integration

- **Google Translate**: Primary translation service with automatic fallback
- **IBM Watson**: Speech-to-text transcription service
- **Alternative Services**: Support for multiple translation providers
- **Connection Management**: Robust handling of service availability

### Performance Optimisation

- **Batch Processing**: Efficient handling of multiple texts
- **Service Fallback**: Automatic switching between translation services
- **Resource Management**: Proper cleanup and memory management

## Supported Languages

### Translation Services

- **Google Translate**: 100+ languages supported
- **Microsoft Translator**: Enterprise-grade translation
- **MyMemory**: Free translation service
- **LibreTranslate**: Open-source translation

### Speech Recognition

- **IBM Watson**: 20+ languages supported
- **Multiple Audio Formats**: WAV, MP3, FLAC, etc.
- **Real-time Processing**: Stream-based transcription

## Version Information

Current version: **3.5.3**

### Recent Updates

- Enhanced defensive programming with nested list support
- Modern PEP-604 type annotations throughout
- Improved error handling and service fallback
- Comprehensive documentation and examples

## Error Handling

The package provides comprehensive error handling:

- **ValueError**: For invalid language codes or parameters
- **RuntimeError**: For service connection issues
- **AttributeError**: For service availability problems
- **SyntaxError**: For malformed input parameters

## System Requirements

- **Python**: 3.10 or higher
- **Internet Connection**: Required for translation and speech services
- **Memory**: Sufficient RAM for processing large text batches
- **Storage**: Space for transcription output files

## Dependencies

### Core Dependencies

- **SpeechRecognition**: Speech recognition capabilities
- **googletrans**: Google Translate integration
- **gTTS**: Google Text-to-Speech (if needed)

### Internal Dependencies

- **filewise**: File operations and path utilities
- **pygenutils**: Utility functions and data manipulation
- **paramlib**: Parameter and configuration management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Guidelines

- Follow existing code structure and language processing best practices
- Add comprehensive docstrings with parameter descriptions
- Include error handling for all service operations
- Test with various languages and text formats
- Update changelog for significant changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google Translate Team** for the translation API
- **IBM Watson Team** for speech recognition services
- **Python NLP Community** for ecosystem development
- **Open Source Translation Providers** for free services

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.

## Troubleshooting

### Common Issues

1. **Translation Service Errors**:
   - Check internet connection
   - Verify language codes are valid
   - Try alternative translation providers

2. **Speech Recognition Issues**:
   - Ensure IBM Watson credentials are set
   - Check audio file format compatibility
   - Verify API service availability

3. **Import Errors**:
   - Run `pip install -e .` for development setup
   - Check Python version compatibility
   - Verify all dependencies are installed

### Getting Help

- Check function docstrings for parameter details
- Review service provider documentation
- Open an issue on GitHub for bugs or feature requests
