"""Main entry point for the Image Convertor MCP server."""

from .general_conversion import auto_convert_image, auto_convert_folder
from .gif_conversion import convert_images_to_gif
from .pdf_conversion import convert_images_to_pdf

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


mcp = FastMCP("image-convertor-mcp")


def ok(msg: str) -> TextContent:
    """Create a success response."""
    return TextContent(type="text", text=msg)


def error(msg: str) -> TextContent:
    """Create an error response."""
    return TextContent(type="text", text=f"❌ Error: {msg}")


@mcp.tool("auto_convert_image", description="Convert a single image to target format with smart naming")
def auto_convert_image_tool(input_path: str, target_format: str, output_dir: str = None, file_name: str = None) -> TextContent:
    """Convert a single image to target format."""
    try:
        result = auto_convert_image(input_path, target_format, output_dir, file_name)
        return ok(f"✅ Successfully converted image to: {result}")
    except Exception as e:
        return error(f"Failed to convert image: {str(e)}")


@mcp.tool("auto_convert_folder", description="Convert all images in a folder to target format with batch processing")
def auto_convert_folder_tool(input_folder: str, target_format: str, output_dir: str = None) -> TextContent:
    """Convert all images in a folder to target format."""
    try:
        result = auto_convert_folder(input_folder, target_format, output_dir)
        return ok(f"✅ Successfully converted folder. Output: {result}")
    except Exception as e:
        return error(f"Failed to convert folder: {str(e)}")


@mcp.tool("convert_images_to_gif", description="Convert multiple images to animated GIF with customization options")
def convert_images_to_gif_tool(
    input_folder: str,
    custom_name: str = None,
    duration: int = 100,
    loop: int = 0,
    color_mode: str = "RGB",
    color_count: int = 256,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    ping_pong: bool = False,
    easing: str = "none",
    easing_strength: float = 1.0
) -> TextContent:
    """Convert multiple images to animated GIF."""
    try:
        result = convert_images_to_gif(
            input_folder, custom_name, duration, loop, color_mode, color_count,
            brightness, contrast, saturation, ping_pong, easing, easing_strength
        )
        return ok(f"✅ Successfully created GIF: {result}")
    except Exception as e:
        return error(f"Failed to create GIF: {str(e)}")


@mcp.tool("convert_images_to_pdf", description="Combine multiple images into a single PDF document")
def convert_images_to_pdf_tool(
    input_folder: str,
    output_dir: str = None,
    output_name: str = None,
    sort_order: str = "alphabetical",
    page_size: str = "A4",
    dpi: int = 300,
    fit_to_page: bool = True,
    center_image: bool = True,
    background_color: str = "white"
) -> TextContent:
    """Combine multiple images into PDF."""
    try:
        result = convert_images_to_pdf(
            input_folder, output_dir, output_name, sort_order, page_size,
            dpi, fit_to_page, center_image, background_color
        )
        return ok(f"✅ Successfully created PDF: {result}")
    except Exception as e:
        return error(f"Failed to create PDF: {str(e)}")


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
