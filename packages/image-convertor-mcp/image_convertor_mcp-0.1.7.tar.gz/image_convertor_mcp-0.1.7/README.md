# Image Convertor MCP

A Model Context Protocol (MCP) server that provides comprehensive image conversion and processing tools.

## Features

- **General Image Conversion**: Convert between various image formats (JPEG, PNG, BMP, TIFF, ICO, WEBP, HEIC/HEIF, AVIF, GIF)
- **Batch Processing**: Convert entire folders of images to a target format
- **GIF Creation**: Convert multiple images to animated GIFs with customization options
- **PDF Generation**: Combine multiple images into a single PDF document
- **Smart Naming**: Automatic file naming with duplicate prevention
- **Format Detection**: Auto-detect input image formats
- **Quality Control**: Optimize ICO files with multiple resolutions

## Installation

### From PyPI
```bash
pip install image-convertor-mcp
```

### Development Installation
```bash
git clone https://github.com/beta/image-convertor-mcp
cd image-convertor-mcp
pip install -e .
```

## Configuration

No special configuration required. The server runs with default settings.

### Example MCP Configuration

```json
{
  "mcpServers": {
    "Image Convertor MCP": {
      "command": "uvx",
      "args": ["image-convertor-mcp"],
      "env": {}
    }
  }
}
```

## Available Tools

### General Image Conversion
- `auto_convert_image(input_path:str, target_format:str, output_dir:str=None, file_name:str=None)` - Convert a single image to target format
- `auto_convert_folder(input_folder:str, target_format:str, output_dir:str=None)` - Convert all images in a folder to target format

### GIF Creation
- `convert_images_to_gif(input_folder:str, custom_name:str=None, duration:int=100, loop:int=0, color_mode:str="RGB", color_count:int=256, brightness:float=1.0, contrast:float=1.0, saturation:float=1.0, ping_pong:bool=False, easing:str="none", easing_strength:float=1.0)` - Convert multiple images to animated GIF

### PDF Generation
- `convert_images_to_pdf(input_folder:str, output_dir:str=None, output_name:str=None, sort_order:str="alphabetical", page_size:str="A4", dpi:int=300, fit_to_page:bool=True, center_image:bool=True, background_color:str="white")` - Combine multiple images into PDF

## Supported Formats

### Input Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tif, .tiff)
- ICO (.ico)
- WEBP (.webp)
- HEIC/HEIF (.heic, .heif)
- AVIF (.avif)
- GIF (.gif)

### Output Formats
- JPEG (.jpg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tif)
- ICO (.ico)
- WEBP (.webp)
- HEIC/HEIF (.heic)
- AVIF (.avif)
- GIF (.gif)
- PDF (.pdf)

## Usage

### Command Line
```bash
image-convertor-mcp
```

### As MCP Server
The server runs over stdio and can be integrated with any MCP-compatible client.

## Requirements

- Python 3.9+
- Pillow (PIL) for image processing
- pillow-heif for HEIC/HEIF support
- reportlab for PDF generation
- Internet connection (for some format conversions)

## Changelog

### Version 0.1.7
- **Enhancement**: Improved error handling and user feedback for better MCP tool reliability
- **Performance**: Further optimized memory management and resource cleanup
- **Documentation**: Updated project metadata and PyPI package information

### Version 0.1.6
- **Bug Fix**: Fixed MCP server completion issue where tools would appear "stuck" in processing state
- **Bug Fix**: Fixed argument error in MCP tool execution that was preventing tools from running
- **Performance**: Optimized memory usage and resource management via garbage collection
- **Performance**: Added comprehensive warning capture and reporting for MCP tools with optional parameters

### Version 0.1.1
- Initial release with core image conversion functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.