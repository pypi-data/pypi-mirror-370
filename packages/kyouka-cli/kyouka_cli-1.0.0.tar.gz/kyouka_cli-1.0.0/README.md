# Kyouka - YouTube Downloader and Media Player

Kyouka is a command-line tool for downloading YouTube videos and playing media files.

## Features
- Download YouTube videos as MP4
- Download audio as high-quality MP3
- Play media files with different player options
- Rename and manage downloaded files

## Installation

### Basic Installation (audio only)
```bash
pip install kyouka
```
Full Installation (with video support)
```bash
pip install kyouka[full]
```
Note: For full video playback support, you'll need:

VLC media player installed on your system

Tkinter (usually included with Python)

Usage
Run the CLI interface:

```bash
kyouka
```
Command-line options:
```bash
kyouka --download "https://youtube.com/..."         # Download video
kyouka --download_audio "https://youtube.com/..."   # Download audio only
kyouka --list                                       # List downloaded media
kyouka --play "filename.mp4"                        # Play a media file
kyouka --rename "oldname.mp4" "newname.mp4"         # Rename a file
kyouka --delete "filename.mp4"                      # Delete a file
```
Player Options:
Player (Audio and Video - Recommended) - Requires VLC

Built-in Video Player (no audio) - Requires OpenCV

Audio Player (no video) - Requires VLC

Troubleshooting
If video players don't work, install VLC: https://www.videolan.org/

On Linux, install Tkinter: sudo apt install python3-tk

### Installation Instructions for Users

1. **Install Python** (if not already installed):
   - Download from https://python.org/downloads
   - Make sure to check "Add Python to PATH" during installation

2. **Install Kyouka**:
```bash
# For basic audio functionality:
pip install kyouka

# For full video support:
pip install kyouka[full]
```
Install VLC (for best experience):

Download from https://www.videolan.org/vlc/

Run Kyouka:

```bash
kyouka
```
For Developers
To install from source:

```bash
git clone https://github.com/lyraxial/kyouka.git
cd kyouka
pip install .[full]  # For full features
```
