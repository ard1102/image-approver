# ApproveIT v2.0 ✨

A simple and efficient tool for quickly sorting and organizing images through an intuitive approval/disapproval workflow.

_**Note:** The UI has been completely revamped in v2.0 for a modern look and feel. The screenshot will be updated shortly._

**[Screenshot Placeholder: A new screenshot of the v2.0 UI will be added here]**

![Python](https://img.shields.io/badge/python-3.6%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Overview

ApproveIT helps you quickly review large collections of images and sort them into "approved" and "disapproved" categories. This tool is perfect for:
- 🖼️ Cleaning up photo collections
- 🎨 Organizing design assets
- 🤖 Reviewing generated images from AI tools
- 📂 Managing large batches of photos

## 🚀 Features

- **🎨 Modern UI**: A professional and clean interface with customizable themes.
- **🌓 Theme Toggle**: Switch between light and dark themes with a single click.
- **🖌️ Colored Action Buttons**: Green approve and red disapprove buttons for clear visual feedback.
- **💡 Icon-Based Buttons**: Intuitive icons for all major actions.
- **⌨️ Keyboard Shortcuts**: Navigate and sort images without touching the mouse.
- **🔍 Zoom Controls**: Built-in zoom functionality for detailed image inspection.
- **↩️ Undo Capability**: Easily undo your last action.
- **📊 Progress Bar**: A visual indicator to track your sorting progress.
- **🛡️ Non-destructive**: Original images are moved to separate folders, preserving your source directory.

## ❤️‍🩹 Pain Points Addressed

### 1. Slow Image Review Process
Traditional image management requires opening each image individually, making decisions, and then manually moving files. ApproveIT streamlines this by presenting one image at a time with quick action buttons.

### 2. UI Becomes Unusable During Zoom Operations
Fixed in v1.0: Earlier versions had issues with the UI expanding during zoom operations. This has been resolved with a proper canvas implementation that maintains UI stability.

### 3. Unpredictable Zoom Behavior
Fixed in v1.0: The zoom functionality now properly scales images without affecting the canvas size or button visibility.

### 4. Losing Track of Progress
The application now shows clear progress indicators, including how many images remain to be processed.

### 5. No Way to Undo Actions
Added undo functionality that allows you to reverse up to 10 recent actions.

## 💻 Installation

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

## 🎮 Usage

1. Click **📂 Select Folder** to choose a directory containing the images you want to sort.
2. The application will create "approved" and "disapproved" subfolders in the selected directory.
3. Use the **🌓 Toggle Theme** button to switch between light and dark themes.
4. Review images one by one and use the buttons or keyboard shortcuts:
   - **✔ Approve** (Green): Move the image to the "approved" folder.
   - **❌ Disapprove** (Red): Move the image to the "disapproved" folder.
   - **🔼 / 🔽**: Navigate to the previous or next image.
   - **↩️ Undo**: Revert the last move action.
   - **➕ / ➖**: Zoom in or out of the image.
   - **`Spacebar`**: Reset the zoom to the default level.

## ⚙️ Default Settings

- **Starting Zoom Level**: 40% (improves initial viewing experience for large images)
- **Minimum Zoom**: 10%
- **Maximum Zoom**: 500%
- **Zoom Step**: 10% per increment

## ⌨️ Keyboard Shortcuts

| Key | Action | Button |
|-----|--------|--------|
| ← | ❌ Disapprove image | ❌ Disapprove (Red) |
| → | ✔️ Approve image | ✔ Approve (Green) |
| ↑ | 🔼 Previous image | ↑ |
| ↓ | 🔽 Next image | ↓ |
| Z | ↩️ Undo last action | ↩ Undo |
| + | ➕ Zoom in | ＋ |
| - | ➖ Zoom out | － |
| T | 🌓 Toggle theme | 🌓 Toggle Theme |
| Space | 🔄 Reset zoom | (No button) |

## 🙌 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📜 Version History

### v2.0 (Current)
- Complete UI overhaul with a modern interface.
- **Theme Toggle**: Added light/dark theme switching functionality.
- **Colored Buttons**: Green approve and red disapprove buttons for better visual feedback.
- Replaced standard `tkinter` widgets with `tkinter.ttk` themed widgets.
- Added intuitive icons to all buttons.
- Implemented a progress bar for better progress tracking.
- Improved layout, spacing, and fonts for a professional look.
- Enhanced user experience with dynamic styling.

### v1.0
- Initial release
- Fixed UI stability issues with zoom operations
- Implemented 40% default zoom for better initial viewing experience
- Added undo functionality
- Improved keyboard navigation
- Enhanced progress tracking

## 💬 Support

If you encounter any issues or have feature requests, please open an issue on the GitHub repository.