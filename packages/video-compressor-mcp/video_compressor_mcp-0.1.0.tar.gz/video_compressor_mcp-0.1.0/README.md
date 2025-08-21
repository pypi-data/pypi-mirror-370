# Video Compressor MCP

A Model Context Protocol (MCP) server for video compression and optimization: bitrate, resolution, frame rate, and codec adjustment.

## Features

- **Bitrate Control**: Adjust video bitrate for size optimization
- **Resolution Scaling**: Change video resolution with aspect ratio preservation
- **Frame Rate Adjustment**: Modify video frame rates
- **Codec Selection**: Choose optimal video codecs for different use cases
- **Smart Fallback**: Automatic audio copy with re-encoding fallback

## Installation

Install via uvx (recommended):

```bash
uvx video-compressor-mcp
```

Or install via pip:

```bash
pip install video-compressor-mcp
```

## Usage

Run the MCP server:

```bash
video-compressor-mcp
```

## Requirements

- Python >=3.12
- FFmpeg installed on your system

## Tools Available

1. `set_video_bitrate` - Adjust video bitrate
2. `set_video_resolution` - Change video resolution
3. `set_video_frame_rate` - Modify frame rate
4. `set_video_codec` - Change video codec

## License

MIT License
