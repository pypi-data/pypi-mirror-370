"""
PDF Conversion Module - Converts Multiple Image Files Into Single PDF File
"""

from pathlib import Path
from PIL import Image
import gc

# Import From General Conversion Module
from .general_conversion import SUPPORTED_OUT_FORMATS, generate_unique_filename

def convert_images_to_pdf(
    input_dir: str,
    output_dir: str = None,
    file_name: str = None,
    sort_order: str = "alphabetical",
    page_size: str = "A4",
    dpi: int = 300,
    fit_to_page: bool = True,
    center_image: bool = True,
    background_color: str = "white"
) -> str:
    """
    Convert multiple images from a folder into a single PDF file.
    
    Args:
        input_dir (str): Path to folder containing images
        output_dir (str): Output directory path (defaults to input folder)
        file_name (str): Custom output filename without extension
        sort_order (str): "alphabetical", "creation_time", or "modification_time"
        page_size (str): Page size - A-series (A4, A3, A5), B-series (B5, B4, B3), US standards (Letter, Legal, Executive, Tabloid), Digital (16:9, 4:3, Square)
        dpi (int): DPI for PDF (72-1200)
        fit_to_page (bool): Whether to fit images to page size
        center_image (bool): Whether to center images on page
        background_color (str): Page background color - Grayscale: white, light gray, gray, dark gray, black; Reds: dark red, red, light red; Colors: orange, yellow, lime; Greens: light green, green, dark green; Blues: light blue, blue, dark blue; Purples: dark purple, purple, light purple; Pinks: dark pink, pink, light pink; Browns: dark brown, brown, light brown
        
    Returns:
        str: Path to created PDF file
        
    Raises:
        RuntimeError: If PDF creation fails
    """
    try:
        # Validate Input Folder
        input_folder_path = Path(input_dir)
        if not input_folder_path.exists():
            raise ValueError(f"Input folder does not exist: {input_dir}")
        if not input_folder_path.is_dir():
            raise ValueError(f"Input path is not a folder: {input_folder_path}")
        
        # Set Output Directory
        if output_dir is None:
            output_dir_path = input_folder_path
        else:
            try:
                output_dir_path = Path(output_dir)
                # Try to Create Directory if it Doesn't Exist
                if not output_dir_path.exists():
                    output_dir_path.mkdir(parents=True, exist_ok=True)
                # Validate it's Actually a Directory and Accessible
                if not output_dir_path.is_dir():
                    print(f"(WARNING) Invalid output_dir '{output_dir}', using input folder")
                    output_dir_path = input_folder_path
                else:
                    # Test if We Can Actually Write to This Directory
                    try:
                        test_file = output_dir_path / ".test_write_access"
                        test_file.touch()
                        test_file.unlink()
                    except Exception:
                        print(f"(WARNING) Cannot write to output_dir '{output_dir}', using input folder")
                        output_dir_path = input_folder_path
            except Exception as e:
                print(f"(WARNING) Invalid output_dir '{output_dir}', using input folder")
                output_dir_path = input_folder_path
        
        print(f"OUTPUT: Output directory: {output_dir_path}")
        
        # Set Output Filename
        if file_name is None:
            # Use Default Naming Rule
            base_name = "Converted PDF"
        else:
            try:
                # Use Custom Name (Strip Any Extension if User Provided One)
                base_name = Path(file_name).stem
                # Validate the Name is Not Empty or Just Whitespace
                if not base_name or base_name.strip() == "":
                    print(f"(WARNING) Invalid file_name '{file_name}', using default")
                    base_name = "Converted PDF"
            except Exception as e:
                print(f"(WARNING) Invalid file_name '{file_name}', using default")
                base_name = "Converted PDF"
        
        # Create Base Output Path With .pdf Extension
        base_output_path = output_dir_path / f"{base_name}.pdf"
        final_output_path = generate_unique_filename(base_output_path)
        
        print(f"INFO: Output filename: {final_output_path.name}")
        
        # Validate Parameters with Type Checking
        
        # Validate Page Size (Must be String)
        if not isinstance(page_size, str):
            print(f"(WARNING) page_size must be string, got {type(page_size).__name__}, using A4")
            page_size = "A4"
        
        valid_page_sizes = ["A4", "A3", "A5", "Letter", "Legal", "B5", "B4", "B3", "16:9", "4:3", "Square", "Tabloid", "Executive"]
        if page_size not in valid_page_sizes:
            print(f"(WARNING) Invalid page_size '{page_size}', using A4")
            page_size = "A4"
        
        # Validate dpi (Must be Number)
        try:
            dpi = int(dpi)
            if not (72 <= dpi <= 1200):
                print(f"(WARNING) Invalid DPI {dpi}, using 300")
                dpi = 300
        except (ValueError, TypeError):
            print(f"(WARNING) DPI must be a number, got {type(dpi).__name__}, using 300")
            dpi = 300
        
        # Define Comprehensive Color Palette
        background_colors = {
            # Grayscale
            "white": (255, 255, 255),
            "light gray": (211, 211, 211),
            "gray": (128, 128, 128),
            "dark gray": (64, 64, 64),
            "black": (0, 0, 0),
            
            # Reds
            "dark red": (139, 0, 0),
            "red": (255, 0, 0),
            "light red": (255, 182, 193),
            
            # Orange & Yellow
            "orange": (255, 165, 0),
            "yellow": (255, 255, 0),
            "lime": (0, 255, 0),
            
            # Greens
            "light green": (144, 238, 144),
            "green": (0, 128, 0),
            "dark green": (0, 100, 0),
            
            # Blues
            "light blue": (173, 216, 230),
            "blue": (0, 0, 255),
            "dark blue": (0, 0, 139),
            
            # Purples
            "dark purple": (72, 61, 139),
            "purple": (128, 0, 128),
            "light purple": (221, 160, 221),
            
            # Pinks
            "dark pink": (199, 21, 133),
            "pink": (255, 192, 203),
            "light pink": (255, 182, 193),
            
            # Browns
            "dark brown": (101, 67, 33),
            "brown": (165, 42, 42),
            "light brown": (205, 133, 63)
        }
        
        # Validate background_color (must be string)
        if not isinstance(background_color, str):
            print(f"(WARNING) background_color must be string, got {type(background_color).__name__}, using white")
            background_color = "white"
        
        if background_color.lower() not in background_colors:
            print(f"(WARNING) Invalid background_color '{background_color}', using white")
            background_color = "white"
        else:
            background_color = background_color.lower()
        
        # Validate Sort Order (Must be String)
        if not isinstance(sort_order, str):
            print(f"(WARNING) sort_order must be string, got {type(sort_order).__name__}, using alphabetical")
            sort_order = "alphabetical"
        
        if sort_order not in ["alphabetical", "creation_time", "modification_time"]:
            print(f"(WARNING) Invalid sort_order '{sort_order}', using alphabetical")
            sort_order = "alphabetical"
        
        # Validate Boolean Parameters
        def validate_boolean_param(param, param_name, default=True):
            if isinstance(param, bool):
                return param
            try:
                if isinstance(param, str):
                    if param.lower() in ['true', '1', 'yes', 'on']:
                        return True
                    elif param.lower() in ['false', '0', 'no', 'off']:
                        return False
                    else:
                        print(f"(WARNING) Invalid {param_name} '{param}', using {default}")
                        return default
                else:
                    result = bool(param)
                    print(f"(WARNING) {param_name} converted from {type(param).__name__} to {result}")
                    return result
            except Exception as e:
                print(f"(WARNING) Invalid {param_name} '{param}': {e}, using {default}")
                return default
        
        fit_to_page = validate_boolean_param(fit_to_page, "fit_to_page", True)
        center_image = validate_boolean_param(center_image, "center_image", True)
        
        # Get Page Dimensions
        page_width, page_height = get_page_dimensions(page_size, dpi)
        
        # Get Image Files in Specified Order
        image_files = get_file_order(input_dir, sort_order)
        
        if not image_files:
            raise RuntimeError("No image files found in input folder")
        
        # Filter for Supported Image Formats
        supported_images = []
        # Get All Supported Image Extensions From the Main Conversion Module
        supported_extensions = set()
        for format_exts in SUPPORTED_OUT_FORMATS.values():
            supported_extensions.update(ext.lower() for ext in format_exts)
        
        for file_path in image_files:
            if file_path.suffix.lower() in supported_extensions:
                supported_images.append(file_path)
        
        if not supported_images:
            raise RuntimeError("No supported image files found in input folder")
        
        print(f"PROCESSING: Found {len(supported_images)} images to combine into single PDF")
        
        # Process Images
        processed_images = []
        for i, image_path in enumerate(supported_images, 1):
            try:
                print(f"PROCESSING: Processing {i}/{len(supported_images)}: {image_path.name}")
                
                # Open and Convert Image
                with Image.open(image_path) as img:
                    # Convert to RGB If Needed
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize If Fit_to_page Is Enabled
                    if fit_to_page:
                        new_size = fit_image_to_page(img.size, (page_width, page_height))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Create Page With Background Color
                    page = Image.new('RGB', (page_width, page_height), background_colors[background_color])
                    
                    # Calculate Position
                    if center_image:
                        x = (page_width - img.width) // 2
                        y = (page_height - img.height) // 2
                    else:
                        x = y = 0
                    
                    # Paste Image Onto Page
                    page.paste(img, (x, y))
                    
                    processed_images.append(page)
                    print(f"SUCCESS: Processed: {image_path.name}")
                    
            except Exception as e:
                print(f"(WARNING) Could not process {image_path.name}: {e}")
                continue
        
        if not processed_images:
            raise RuntimeError("No images were successfully processed")
        
        print(f"SAVING: Saving {len(processed_images)} pages to PDF...")
        
        # Save As PDF
        processed_images[0].save(
            final_output_path,
            'PDF',
            resolution=dpi,
            save_all=True,
            append_images=processed_images[1:]
        )
        
        print(f"SUCCESS: PDF created successfully: {final_output_path}")
        print(f"SUMMARY: Pages: {len(processed_images)}, Page size: {page_size} ({page_width}x{page_height} pixels at {dpi} DPI)")
        
        return str(final_output_path)
        
    except Exception as e:
        raise RuntimeError(f"Failed to create PDF: {e}")
    finally:
        # Simple Memory Cleanup
        gc.collect()

def get_file_order(folder_path: str, sort_order: str) -> list:
    """
    Get files in the specified order.
    
    Args:
        folder_path (str): Path to the folder
        sort_order (str): Order type - "alphabetical", "creation_time", or "modification_time"
        
    Returns:
        list: List of Path objects in the specified order
    """
    try:
        folder_path_obj = Path(folder_path)
        if not folder_path_obj.exists() or not folder_path_obj.is_dir():
            print(f"(WARNING) Invalid folder path, using alphabetical order")
            return []
        
        # Get All Files
        image_files = []
        for item in folder_path_obj.iterdir():
            if item.is_file():
                image_files.append(item)
        
        try:
            if sort_order.lower() == "alphabetical":
                # Sort By Filename For Consistent Alphabetical Ordering
                image_files.sort(key=lambda x: x.name)
                print(f"SORTING: Alphabetical order by filename")
            elif sort_order.lower() == "creation_time":
                # Sort By Creation Time (Newest First)
                image_files.sort(key=lambda x: x.stat().st_ctime, reverse=True)
                print(f"SORTING: Creation time order (newest first)")
            elif sort_order.lower() == "modification_time":
                # Sort By Modification Time (Newest First)
                image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                print(f"SORTING: Modification time order (newest first)")
            else:
                # Default To Alphabetical
                image_files.sort(key=lambda x: x.name)
                print(f"SORTING: Default alphabetical order")
        except Exception as e:
            print(f"(WARNING) Sorting failed: {e}, using alphabetical order")
            image_files.sort(key=lambda x: x.name)
        
        return image_files
        
    except Exception as e:
        print(f"(WARNING) File ordering failed: {e}, using alphabetical order")
        # Fallback to Simple Alphabetical Sorting
        try:
            image_files = [item for item in folder_path_obj.iterdir() if item.is_file()]
            image_files.sort(key=lambda x: x.name)
            return image_files
        except:
            return []

def get_page_dimensions(page_size: str, dpi: int) -> tuple:
    """
    Get page dimensions in pixels for a given page size and DPI.
    
    Args:
        page_size (str): Page size - A-series (A4, A3, A5), B-series (B5, B4, B3), 
                        US standards (Letter, Legal, Executive, Tabloid), 
                        Digital (16:9, 4:3, Square)
        dpi (int): Dots per inch
        
    Returns:
        tuple: (width, height) in pixels
    """
    # Standard Page Sizes in Inches
    page_sizes_inches = {
        "A4": (8.27, 11.69),
        "A3": (11.69, 16.54),
        "A5": (5.83, 8.27),
        "Letter": (8.5, 11.0),
        "Legal": (8.5, 14.0),
        
        # B-Series Sizes (Popular in Asia and Technical Documents)
        "B5": (6.93, 9.84),
        "B4": (9.84, 13.90),
        "B3": (13.90, 19.69),
        
        # Digital/Web Optimized Sizes
        "16:9": (11.0, 6.19),
        "4:3": (10.0, 7.5),
        "Square": (8.5, 8.5),
        
        # Print Industry Standards
        "Tabloid": (11.0, 17.0),
        "Executive": (7.25, 10.5)
    }
    
    try:
        if page_size in page_sizes_inches:
            width_in, height_in = page_sizes_inches[page_size]
            width_px = int(width_in * dpi)
            height_px = int(height_in * dpi)
            return (width_px, height_px)
        else:
            # Default to A4
            width_in, height_in = page_sizes_inches["A4"]
            width_px = int(width_in * dpi)
            height_px = int(height_in * dpi)
            return (width_px, height_px)
    except Exception as e:
        print(f"(WARNING) Page dimension calculation failed: {e}, using A4 default")
        # Fallback to A4 with Default DPI
        width_in, height_in = page_sizes_inches["A4"]
        width_px = int(width_in * 300)  # Default DPI
        height_px = int(height_in * 300)
        return (width_px, height_px)

def fit_image_to_page(image_size: tuple, page_size: tuple) -> tuple:
    """
    Calculate image dimensions to fit within page while maintaining aspect ratio.
    
    Args:
        image_size (tuple): Original image dimensions (width, height)
        page_size (tuple): Page dimensions (width, height)
        
    Returns:
        tuple: New image dimensions (width, height)
    """
    try:
        img_width, img_height = image_size
        page_width, page_height = page_size
        
        # Validate Dimensions Are Positive
        if img_width <= 0 or img_height <= 0 or page_width <= 0 or page_height <= 0:
            print(f"(WARNING) Invalid dimensions, returning original size")
            return image_size
        
        # Calculate Scaling Factors
        scale_x = page_width / img_width
        scale_y = page_height / img_height
        
        # Use The Smaller Scale To Fit Within Page Bounds
        scale = min(scale_x, scale_y)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Ensure Minimum Size
        if new_width < 1 or new_height < 1:
            print(f"(WARNING) Calculated size too small, using original")
            return image_size
        
        return (new_width, new_height)
        
    except Exception as e:
        print(f"(WARNING) Image fitting calculation failed: {e}, returning original size")
        return image_size
