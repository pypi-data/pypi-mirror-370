# Audio Processor MCP

A Model Context Protocol (MCP) server for comprehensive audio processing: format conversion, metadata editing, volume adjustment, and audio analysis.

## Features

- **Audio Format Conversion**: Convert between different audio formats (MP3, WAV, FLAC, AAC, OGG, etc.)
- **Metadata Management**: Read and write audio metadata (title, artist, album, genre, etc.)
- **Volume Control**: Adjust audio volume levels and apply normalization
- **Audio Analysis**: Extract detailed audio information (duration, bitrate, sample rate, channels)
- **Quality Processing**: Apply audio filters and enhancement options

## Installation

Install via uvx (recommended):

```bash
uvx audio-processor-mcp
```

Or install via pip:

```bash
pip install audio-processor-mcp
```

## Usage

Run the MCP server:

```bash
audio-processor-mcp
```

## Requirements

- Python >=3.12
- FFmpeg installed on your system

## Tools Available

1. `convert_audio_properties` - Convert audio with custom properties (format, bitrate, sample rate, channels)
2. `convert_audio_format` - Convert audio files between different formats
3. `set_audio_bitrate` - Adjust audio bitrate with codec optimization
4. `set_audio_sample_rate` - Change audio sample rate
5. `set_audio_channels` - Set number of audio channels (mono/stereo/surround)
6. `get_audio_info` - Get detailed audio file information and metadata

## Supported Audio Formats

- **Input/Output**: MP3, WAV, FLAC, AAC, OGG, M4A, WMA, AIFF
- **Metadata**: ID3v1, ID3v2, Vorbis Comments, APE tags

## License

MIT License
