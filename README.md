# ApproveIT

A simple and efficient tool for quickly sorting and organizing images through an intuitive approval/disapproval workflow.

![Python](https://img.shields.io/badge/python-3.6%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Overview

ApproveIT helps you quickly review large collections of images and sort them into "approved" and "disapproved" categories. This tool is perfect for:
- Cleaning up photo collections
- Organizing design assets
- Reviewing generated images from AI tools
- Managing large batches of photos

## Features

- **Intuitive UI**: Clean and simple interface for quick decision making
- **Keyboard Shortcuts**: Navigate and sort images without touching the mouse
- **Zoom Controls**: Built-in zoom functionality for detailed image inspection
- **Undo Capability**: Easily undo your last action
- **Progress Tracking**: See how many images are left to review
- **Non-destructive**: Original images are moved to separate folders, preserving your source directory

## Pain Points Addressed

### 1. Slow Image Review Process
Traditional image management requires opening each image individually in a viewer, making decisions, and then manually moving files. ApproveIT streamlines this by presenting one image at a time with quick action buttons.

### 2. UI Becomes Unusable During Zoom Operations
Fixed in v1.0: Earlier versions had issues with the UI expanding during zoom operations. This has been resolved with a proper canvas implementation that maintains UI stability.

### 3. Unpredictable Zoom Behavior
Fixed in v1.0: The zoom functionality now properly scales images without affecting the canvas size or button visibility.

### 4. Losing Track of Progress
The application now shows clear progress indicators, including how many images remain to be processed.

### 5. No Way to Undo Actions
Added undo functionality that allows you to reverse up to 10 recent actions.

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### On Windows:
Double-click `run.bat` or run:
```cmd
python image_approver.py
```

#### On macOS/Linux:
Run:
```bash
chmod +x run.sh
./run.sh
```
or
```bash
python3 image_approver.py
```

## Usage

1. Click "Select Folder" to choose a directory containing images you want to sort
2. The application will create "approved" and "disapproved" subfolders in the selected directory
3. Review images one by one and:
   - Press **→** or click "Approve" to move the image to the "approved" folder
   - Press **←** or click "Disapprove" to move the image to the "disapproved" folder
   - Press **↑** or click "Previous" to go back to the previous image
   - Press **↓** or click "Next" to skip to the next image
   - Press **Z** or click "Undo" to undo your last action (up to 10 actions)
   - Press **+** or click "Zoom In" to enlarge the image
   - Press **-** or click "Zoom Out" to shrink the image
   - Press **Space** to reset zoom to the default 40%

## Default Settings

- **Starting Zoom Level**: 40% (improves initial viewing experience for large images)
- **Minimum Zoom**: 10%
- **Maximum Zoom**: 500%
- **Zoom Step**: 10% per increment

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ← | Disapprove image |
| → | Approve image |
| ↑ | Previous image |
| ↓ | Next image |
| Z | Undo last action |
| + | Zoom in |
| - | Zoom out |
| Space | Reset zoom |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version History

### v1.0 (Current)
- Initial release
- Fixed UI stability issues with zoom operations
- Implemented 40% default zoom for better initial viewing experience
- Added undo functionality
- Improved keyboard navigation
- Enhanced progress tracking

## Support

If you encounter any issues or have feature requests, please open an issue on the GitHub repository.