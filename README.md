# 🌊 PeeDoFile 初春 (Hatsuharu/First Spring) - PDF Editor and Annotator �Rising Sun

<div align="center">

![PeeDoFile Banner](https://i.imgur.com/placeholder.png)

[![License](https://img.shields.io/badge/license-MIT-red.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt-5.15+-orange.svg?style=flat-square)](https://pypi.org/project/PyQt5/)

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
- Python 3.9+
- PyInstaller
- Virtual environment (recommended)

### Build Steps

1. Ensure you're in your virtual environment
```bash
# For Windows
.venv\Scripts\activate
```

2. Install PyInstaller if not already installed
```bash
pip install pyinstaller
```

3. Build the executable
```bash
pyinstaller PeeDoFile.spec
```

4. Find the executable in the `dist` folder

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
│   ├── viewer.py       # PDF viewing components
│   └── saver.py        # File saving operations
├── requirements.txt    # Project dependencies
└── PeeDoFile.spec     # PyInstaller specification
```

## 🌊 Technical Details

### Dependencies

- **PyQt5**: GUI framework
- **PyMuPDF**: PDF manipulation
- **PyInstaller**: Executable creation

### Key Components

- **PDFViewer**: Main window and PDF display
- **PDFAnnotator**: Drawing and annotation handling
- **PDFSaver**: File operations and saving

## 🎨 Customization

The application uses a minimalist design inspired by Japanese aesthetics:

- Clean interface
- Minimal controls
- Focus on content
- Efficient workflow

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🌟 Acknowledgments

- Inspired by Japanese minimalism
- Built with PyQt5 and PyMuPDF
- PDF handling powered by MuPDF

---

<div align="center">

Made with ❤️ and 🍵

</div>
