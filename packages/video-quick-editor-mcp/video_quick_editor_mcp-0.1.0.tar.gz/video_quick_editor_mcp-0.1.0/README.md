# Video Editor MCP

A Model Context Protocol (MCP) server for advanced video editing operations including aspect ratio adjustment, subtitles, overlays, concatenation, speed changes, and transitions.

## Features

- **Aspect Ratio Adjustment**: Change video aspect ratios with padding or cropping
- **Subtitle Integration**: Burn SRT subtitles with customizable styling
- **Text & Image Overlays**: Add text and image overlays with positioning and timing
- **Video Concatenation**: Join multiple videos with optional transitions
- **Speed Control**: Adjust video playback speed with proper audio sync
- **Silence Removal**: Automatically remove silent segments
- **B-roll Integration**: Add B-roll footage with positioning and transitions
- **Basic Transitions**: Apply fade-in/fade-out effects

## Installation

Install via uvx (recommended):

```bash
uvx video-editor-mcp
```

Or install via pip:

```bash
pip install video-editor-mcp
```

## Usage

Run the MCP server:

```bash
video-editor-mcp
```

## Requirements

- Python >=3.12
- FFmpeg installed on your system

## Tools Available

1. `change_aspect_ratio` - Adjust video aspect ratio
2. `add_subtitles` - Burn SRT subtitles to video
3. `add_text_overlay` - Add timed text overlays
4. `add_image_overlay` - Add image watermarks/logos
5. `concatenate_videos` - Join videos with transitions
6. `change_video_speed` - Adjust playback speed
7. `remove_silence` - Remove silent segments
8. `add_b_roll` - Overlay B-roll footage
9. `add_basic_transitions` - Add fade effects

## License

MIT License
