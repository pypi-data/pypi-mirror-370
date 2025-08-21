# Video Content Extractor MCP

A Model Context Protocol (MCP) server for video content extraction: audio extraction, video trimming, frame extraction, and scene detection.

## Features

- **Audio Extraction**: Extract audio tracks from video files in various formats
- **Video Trimming**: Cut video segments by time ranges with smart codec copying
- **Frame Extraction**: Extract frames at intervals, first/last frames, or by scene changes
- **Scene Detection**: Automatically detect scene changes and extract key frames

## Installation

Install via uvx (recommended):

```bash
uvx video-content-extractor-mcp
```

Or install via pip:

```bash
pip install video-content-extractor-mcp
```

## Usage

Run the MCP server:

```bash
video-content-extractor-mcp
```

## Requirements

- Python >=3.12
- FFmpeg installed on your system

## Tools Available

1. `extract_audio_from_video` - Extract audio tracks from video files
2. `trim_video` - Trim video segments by time range
3. `extract_video_frames` - Extract frames at intervals or specific positions
4. `extract_scene_change_frames` - Extract frames based on scene change detection

## License

MIT License
