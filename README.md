# PNG to JPEG Batch Converter

A Python tool for batch converting PNG images to JPEG format with configurable quality settings and background color options for transparent images. Available as a standalone macOS app, command-line tool, or graphical user interface.

## Features

- Batch convert PNG files to JPEG format
- Configurable JPEG quality (1-100)
- Handle transparent PNGs with customizable background color
- Recursive directory processing
- Progress display and conversion summary
- Graceful error handling for corrupted files
- Cross-platform GUI (macOS, Windows, Linux)
- Standalone macOS app (no Python required)

## Installation (macOS App)

### Download Pre-built DMG (Recommended)

1. Go to the [Actions tab](../../actions) of this repository
2. Click on the latest successful "Build macOS DMG" workflow run
3. Scroll down to "Artifacts"
4. Download `PNG-to-JPEG-Converter-macOS`
5. Unzip the downloaded file to get the DMG
6. Double-click the DMG to open it
7. Drag "PNG to JPEG Converter" to the Applications folder
8. Eject the disk image

**First Launch Security Note:** macOS may show a security warning for unsigned apps. To open:
- Right-click the app and select "Open", then click "Open" in the dialog
- Or go to System Preferences > Security & Privacy and click "Open Anyway"

**Note:** The pre-built DMG is for Apple Silicon Macs (arm64). It will also run on Intel Macs if built locally.

### Building the macOS App Locally

To build the DMG installer yourself on your Mac:

1. Ensure you have Python 3.8+ with tkinter support (download from [python.org](https://www.python.org/downloads/))
2. Clone or download this repository
3. Run the build script:
   ```bash
   chmod +x build_installer.sh
   ./build_installer.sh
   ```

The script will create:
- `dist/PNG to JPEG Converter.app` - The macOS application
- `PNG-to-JPEG-Converter-1.0.0.dmg` - The installer disk image

**Note:** Building locally will create a native build for your Mac's architecture (Apple Silicon or Intel).

## Installation (From Source)

If you prefer to run from source code:

1. Ensure you have Python 3.8 or higher installed:
   ```bash
   python --version
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the GUI:
   ```bash
   python png2jpg_gui.py
   ```

## GUI Application

### Launching the GUI

Run the graphical interface with:
```bash
python png2jpg_gui.py
```

### GUI Features

The GUI provides an intuitive interface with the following elements:

- **Input Folder**: Click "Browse..." to select the folder containing PNG files
- **Output Folder**: Click "Browse..." to select where JPEG files will be saved
- **Quality Slider**: Adjust JPEG quality from 1-100 (default: 85)
- **Include subfolders**: Check to process PNG files in subdirectories
- **Background Color**: Choose white, black, or custom RGB color for transparent PNGs
- **Status Log**: View real-time conversion progress and any errors
- **Convert Button**: Start the conversion process

### GUI Usage Tips

1. Select both input and output folders before the Convert button becomes active
2. The GUI remains responsive during conversion (runs in background thread)
3. Errors for individual files are logged but don't stop the batch process
4. The status area shows a summary when conversion completes

## Command-Line Interface

### Basic Usage

Convert all PNG files in a directory with default quality (85):
```bash
python png2jpg.py -i ./input_images -o ./output_images
```

### Custom Quality

Specify JPEG quality (1-100, higher = better quality, larger file):
```bash
python png2jpg.py -i ./input_images -o ./output_images -q 90
```

### Recursive Processing

Process PNG files in subdirectories as well:
```bash
python png2jpg.py -i ./photos -o ./converted -q 80 -r
```

### Custom Background Color

Set a custom background color for transparent PNGs (RGB values 0-255):
```bash
python png2jpg.py -i ./input -o ./output -b 0,0,0      # Black background
python png2jpg.py -i ./input -o ./output -b 128,128,128  # Gray background
```

### Help

Display all available options:
```bash
python png2jpg.py --help
```

## Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--input` | `-i` | Yes | - | Input directory path containing PNG files |
| `--output` | `-o` | Yes | - | Output directory path for JPEG files |
| `--quality` | `-q` | No | 85 | JPEG quality (1-100) |
| `--recursive` | `-r` | No | False | Process subdirectories |
| `--background` | `-b` | No | 255,255,255 | RGB background color for transparent PNGs |

## Output

The tool displays progress during conversion:
```
Starting PNG to JPEG conversion...
Input directory: ./input_images
Output directory: ./output_images
Quality: 90
Recursive: False
Background color: RGB(255, 255, 255)
--------------------------------------------------
Converting: image1.png -> image1.jpg
Converting: image2.png -> image2.jpg
Warning: Skipping non-PNG file: readme.txt
--------------------------------------------------
Converted 2 files. 1 files skipped.
```

## Error Handling

- Invalid input directory: Displays error and exits (CLI) or shows error dialog (GUI)
- Invalid quality value: Displays error and exits
- Invalid background color format: Displays error and exits
- Corrupted image files: Logs error and continues with remaining files
- Non-PNG files: Displays warning and skips

## File Structure

```
png2jpg_tool/
├── .github/
│   └── workflows/
│       └── build-macos-dmg.yml  # GitHub Actions workflow
├── png2jpg.py                    # Command-line interface
├── png2jpg_gui.py                # Graphical user interface
├── requirements.txt              # Python dependencies
├── PNG2JPG.spec                  # PyInstaller build specification
├── build_installer.sh            # macOS DMG build script
├── AppIcon.icns                  # App icon (optional)
└── README.md                     # This file
```

## License

MIT License
