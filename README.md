# 🌊 PeeDoFile 初春 (Hatsuharu/First Spring) - PDF Editor and Annotator

<div align="center">

![PeeDoFile Banner](https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80)

[![License](https://img.shields.io/badge/license-GPL--3.0-red.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13.5-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt-5.15.11-orange.svg?style=flat-square)](https://pypi.org/project/PyQt5/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.26.1-green.svg?style=flat-square)](https://pypi.org/project/PyMuPDF/)

*A minimalist yet powerful PDF editor inspired by the simplicity of Japanese design*

</div>

---

## 🎨 Features

- **清潔** (Cleanliness)
  - Clean and intuitive interface
  - Distraction-free PDF viewing

- **調和** (Harmony)
  - Seamless annotation integration
  - Fluid drawing experience

- **実用性** (Practicality)
  - Easy file handling
  - Quick save and overwrite capabilities

## 🚀 Quick Start

### Installation from Source

1. Clone the repository
```bash
git clone https://github.com/yourusername/PeeDoFile.git
cd PeeDoFile
```

2. Create and activate virtual environment
```bash
python -m venv .venv
# For Windows
.venv\Scripts\activate
# For Unix/MacOS
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
python app.py
```

### Running the Executable

1. Download the latest release from the [releases page](https://github.com/yourusername/PeeDoFile/releases)
2. Extract the zip file
3. Run `PeeDoFile.exe`

## 🛠️ Building the Executable

### Prerequisites
- Python 3.13.5
- PyInstaller 6.14.1
- Virtual environment (recommended)

### Build Steps

1. Ensure you're in your virtual environment
```bash
# For Windows
.venv\Scripts\activate
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Create the spec file
```bash
# First, create a basic spec file
pyinstaller --name PeeDoFile --onefile --windowed app.py

# This will create PeeDoFile.spec
```

4. Edit the `PeeDoFile.spec` file with these contents:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PeeDoFile',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)
```

5. Build the executable
```bash
pyinstaller PeeDoFile.spec
```

6. Find the executable in the `dist` folder

### Important Notes:
- The spec file configuration ensures:
  - Single-file executable (`--onefile`)
  - No console window (`--windowed`)
  - Proper handling of PyQt5 dependencies
  - Optimized packaging with UPX compression
- You can customize the spec file further:
  - Add an application icon
  - Include additional data files
  - Modify hidden imports
  - Configure debugging options

## 💫 Usage

### Basic Operations

1. **Open PDF**
   - Use File > Open PDF (Ctrl+O)
   - Select your PDF file

2. **Annotation Mode**
   - Toggle: Tools > Toggle Annotation Mode (Ctrl+A)
   - Use the Color button to select drawing color
   - Click and drag to draw
   - Use Clear button to remove annotations

3. **Save Files**
   - File > Save As... (Ctrl+S)
   - Choose location and save

## 🎯 Project Structure

```
PeeDoFile/
├── app.py              # Main application entry
├── features/
│   ├── annotator.py    # Annotation functionality
│   └── viewer.py       # PDF viewing components
├── requirements.txt    # Project dependencies
└── PeeDoFile.spec     # PyInstaller specification
```

## 🌊 Technical Details

### Dependencies

- **PyQt5**: GUI framework (v5.15.11)
- **PyMuPDF**: PDF manipulation (v1.26.1)
- **PyInstaller**: Executable creation (v6.14.1)

### Key Components

- **PDFViewer**: Main window and PDF display with integrated saving functionality
- **PDFAnnotator**: Drawing and annotation handling with color selection

## 🎨 Design Philosophy

The application embodies Japanese minimalist design principles:

- Clean interface with essential controls
- Distraction-free viewing experience
- Intuitive annotation workflow
- Efficient file operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Inspired by Japanese minimalism and efficiency
- Built with PyQt5 and PyMuPDF

---

<div align="center">

Made with ❤️ and 🍵 by the seven and only Debaditya M. and the multiple AI agents on trial mode.

</div>
