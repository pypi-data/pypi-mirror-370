"""Main Entry Point for the Image Convertor MCP Server."""

import logging
import sys
import traceback
import signal
import os
import time
import gc
from .general_conversion import auto_convert_image, auto_convert_folder
from .gif_conversion import convert_images_to_gif
from .pdf_conversion import convert_images_to_pdf

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Global flag to track server state
server_running = True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global server_running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    server_running = False
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

mcp = FastMCP("image-convertor-mcp")


def ok(msg: str) -> TextContent:
    """Create a Success Response."""
    logger.info(f"Tool completed successfully: {msg}")
    return TextContent(type="text", text=msg)


def error(msg: str) -> TextContent:
    """Create an Error Response."""
    logger.error(f"Tool failed: {msg}")
    return TextContent(type="text", text=f"❌ Error: {msg}")


def cleanup_resources():
    """Force cleanup of resources and memory."""
    try:
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection completed, collected {collected} objects")
        
        # Force memory cleanup
        if hasattr(gc, 'garbage'):
            logger.info(f"Clearing garbage references: {len(gc.garbage)} items")
            gc.garbage.clear()
            
    except Exception as e:
        logger.warning(f"Resource cleanup warning: {e}")


def safe_tool_execution(func, *args, **kwargs):
    """Safely execute a tool function with proper error handling and completion signaling."""
    func_name = func.__name__ if hasattr(func, '__name__') else str(func)
    start_time = time.time()
    
    # Pre-execution cleanup
    cleanup_resources()
    
    try:
        logger.info(f"Starting tool execution: {func_name}")
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"Tool execution completed successfully: {func_name} in {execution_time:.2f}s")
        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Tool execution failed: {func_name} after {execution_time:.2f}s - {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise
    finally:
        # Post-execution cleanup
        cleanup_resources()


def ensure_completion(func):
    """Decorator to ensure proper completion of MCP tool functions."""
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Tool wrapper starting: {func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"Tool wrapper completed successfully: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Tool wrapper failed: {func.__name__} - {str(e)}", exc_info=True)
            # Ensure we return an error response even if something goes wrong
            return error(f"Tool execution failed: {str(e)}")
        finally:
            # Always cleanup after tool execution
            cleanup_resources()
    return wrapper


@mcp.tool("auto_convert_image", description="Converts a single image to a specified format (jpeg, png, webp, heic, avif, bmp, tiff, ico) and saves the converted image to the output directory if provided, otherwise same location as input. Args: input_dir (str) = absolute path to source image file || target_format (str) = desired output format (jpeg, png, webp, heic, avif, bmp, tiff, ico) || output_dir (str)(optional): optional output directory path (without filename), defaults to same directory as input file || file_name (str)(optional) = optional custom filename, defaults to auto naming.")
@ensure_completion
def auto_convert_image_tool(input_dir: str, target_format: str, output_dir: str = None, file_name: str = None) -> TextContent:
    """Convert a Single Image to Target Format."""
    tool_start_time = time.time()
    logger.info(f"Starting auto_convert_image tool with input_dir={input_dir}, target_format={target_format}")
    
    try:
        result = safe_tool_execution(auto_convert_image, input_dir, target_format, output_dir, file_name)
        tool_execution_time = time.time() - tool_start_time
        logger.info(f"auto_convert_image tool completed successfully in {tool_execution_time:.2f}s: {result}")
        return ok(f"✅ Successfully converted image to: {result}")
    except Exception as e:
        tool_execution_time = time.time() - tool_start_time
        logger.error(f"auto_convert_image tool failed after {tool_execution_time:.2f}s with exception: {str(e)}", exc_info=True)
        return error(f"Failed to convert image: {str(e)}")


@mcp.tool("auto_convert_folder", description="Converts all images in the input folder to a specified format (jpeg, png, webp, heic, avif, bmp, tiff, ico). Saves the converted images in a new subfolder inside the input folder. Args: input_dir (str) = absolute path to input folder || target_format (str) = desired output format (jpeg, png, webp, heic, avif, bmp, tiff, ico).")
@ensure_completion
def auto_convert_folder_tool(input_dir: str, target_format: str) -> TextContent:
    """Convert All Images in a Folder to Target Format."""
    tool_start_time = time.time()
    logger.info(f"Starting auto_convert_folder tool with input_dir={input_dir}, target_format={target_format}")
    
    try:
        result = safe_tool_execution(auto_convert_folder, input_dir, target_format)
        tool_execution_time = time.time() - tool_start_time
        logger.info(f"auto_convert_folder tool completed successfully in {tool_execution_time:.2f}s: {result}")
        return ok(f"✅ Successfully converted folder. Output: {result}")
    except Exception as e:
        tool_execution_time = time.time() - tool_start_time
        logger.error(f"auto_convert_folder tool failed after {tool_execution_time:.2f}s with exception: {str(e)}", exc_info=True)
        return error(f"Failed to convert folder: {str(e)}")


@mcp.tool("convert_images_to_gif", description="Creates a GIF by combining all supported images (jpeg, png, webp, heic, avif, bmp, tiff, ico) found in the input folder and saves the GIF to the output directory if provided, otherwise same location as input. Args: input_dir (str) = absolute path to input folder || output_dir (str)(optional): optional output directory path (without filename), defaults to input folder || file_name (str)(optional) = optional custom filename, defaults to auto naming || duration (int)(optional) = optional duration per frame via milliseconds (accept 1-10,000ms), defaults to 100 || loop (int)(optional) = optional number of playback loops (0 = infinite), defaults to 0 || color_mode (str)(optional) = optional between 'RGB' (full color), 'P' (indexed color) or 'L' (grayscale), defaults to 'RGB' || color_count (int)(optional) = optional number of colors (accept 2-256) for 'P' and 'L' color modes (ignored for 'RGB'), defaults to 256 || brightness (float)(optional) = optional between 0.0 (darkest) to 5.0 (brightest), defaults to 1.0 || contrast (float)(optional) = optional between 0.0 (least) to 5.0 (most), defaults to 1.0 || saturation (float)(optional) = optional between 0.0 (least) to 5.0 (most), defaults to 1.0 || ping_pong (bool)(optional) = optional playback loop via forward→backward→forward, defaults to False || easing (str)(optional) = optional easing curve between 'none', 'ease-in', 'ease-out' and 'ease-in-out', defaults to 'none' || easing_strength (float)(optional) = optional easing intensity between 0.1 (subtle) to 5.0 (strong), defaults to 1.0.")
@ensure_completion
def convert_images_to_gif_tool(
    input_dir: str,
    file_name: str = None,
    output_dir: str = None,
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
    """Convert Multiple Images to Animated GIF."""
    tool_start_time = time.time()
    logger.info(f"Starting convert_images_to_gif tool with input_dir={input_dir}, file_name={file_name}")
    
    try:
        result = safe_tool_execution(
            convert_images_to_gif,
            input_dir, file_name, output_dir, duration, loop, color_mode, color_count,
            brightness, contrast, saturation, ping_pong, easing, easing_strength
        )
        tool_execution_time = time.time() - tool_start_time
        logger.info(f"convert_images_to_gif tool completed successfully in {tool_execution_time:.2f}s: {result}")
        return ok(f"✅ Successfully created GIF: {result}")
    except Exception as e:
        tool_execution_time = time.time() - tool_start_time
        logger.error(f"convert_images_to_gif tool failed after {tool_execution_time:.2f}s with exception: {str(e)}", exc_info=True)
        return error(f"Failed to create GIF: {str(e)}")


@mcp.tool("convert_images_to_pdf", description="Creates a PDF by combining all supported images (jpeg, png, webp, heic, avif, bmp, tiff, ico), one image per PDF page, found in the input folder and saves the PDF to the output directory if provided, otherwise same location as input. Args: input_dir (str) = absolute path to input folder || output_dir (str)(optional) = optional output directory path (without filename), defaults to input folder || file_name (str)(optional) = optional custom filename, defaults to auto naming || sort_order (str)(optional) = optional image file combination (page) order between 'alphabetical' (a-z & 0-9), 'creation_time' (latest-earliest), 'modification_time' (latest-earliest), defaults to 'alphabetical' || page_size (str)(optional) = optional PDF page size between A3/A4/A5/B3/B4/B5/Letter/Legal/Executive/Tabloid/16:9/4:3/Square, defaults to 'A4' || dpi (int)(optional) = optional PDF resolution (accept 72-1200), defaults to 300 || fit_to_page (bool)(optional) = optional scale images to exactly fit PDF pages, defaults to True || center_image (bool)(optional) = optional center images on PDF pages, defaults to True || background_color (str)(optional) = optional background color between 'white', 'light gray', 'gray', 'dark gray', 'black', 'light red', 'red', 'dark red', 'yellow', 'orange', 'lime', 'light green', 'green', 'dark green', 'light blue', 'blue', 'dark blue', 'light purple', 'purple', 'dark purple', 'light pink', 'pink', 'dark pink', 'light brown', 'brown', 'dark brown', defaults to 'white'.")
@ensure_completion
def convert_images_to_pdf_tool(
    input_dir: str,
    output_dir: str = None,
    file_name: str = None,
    sort_order: str = "alphabetical",
    page_size: str = "A4",
    dpi: int = 300,
    fit_to_page: bool = True,
    center_image: bool = True,
    background_color: str = "white"
) -> TextContent:
    """Combine Multiple Images into PDF."""
    tool_start_time = time.time()
    logger.info(f"Starting convert_images_to_pdf tool with input_dir={input_dir}, file_name={file_name}")
    
    try:
        result = safe_tool_execution(
            convert_images_to_pdf,
            input_dir, output_dir, file_name, sort_order, page_size,
            dpi, fit_to_page, center_image, background_color
        )
        tool_execution_time = time.time() - tool_start_time
        logger.info(f"convert_images_to_pdf tool completed successfully in {tool_execution_time:.2f}s: {result}")
        return ok(f"✅ Successfully created PDF: {result}")
    except Exception as e:
        tool_execution_time = time.time() - tool_start_time
        logger.error(f"convert_images_to_pdf tool failed after {tool_execution_time:.2f}s with exception: {str(e)}", exc_info=True)
        return error(f"Failed to create PDF: {str(e)}")


def main():
    """Run the MCP Server."""
    logger.info("Starting Image Convertor MCP Server")
    logger.info(f"Process ID: {os.getpid()}")
    logger.info(f"Python version: {sys.version}")
    
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server failed to start: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
