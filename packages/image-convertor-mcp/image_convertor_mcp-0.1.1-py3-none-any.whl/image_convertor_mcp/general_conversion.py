#!/usr/bin/env python3
"""
General Conversion Module - Convertable Formats: JPEG, PNG, BMP, TIFF, ICO, WEBP, HEIC/HEIF, AVIF
"""

from pathlib import Path
from typing import Optional, List, Dict, Tuple, Iterable

from PIL import Image, UnidentifiedImageError

# --- Optional: Register HEIF/AVIF Decoders/Encoders if Available ---
_HEIF_AVAILABLE = False
try:
    import pillow_heif  # type: ignore
    # Register Encoders so Pillow can open .heic/.heif/.avif files
    pillow_heif.register_heif_opener()
    try:
        pillow_heif.register_avif_opener()
    except Exception:
        # Older Versions Only Need/Register_heif_opener; AVIF May Already be Covered
        pass
    _HEIF_AVAILABLE = True
except Exception:
    _HEIF_AVAILABLE = False


SUPPORTED_OUT_FORMATS = {
    "JPEG": (".jpg", ".jpeg"),
    "PNG": (".png",),
    "BMP": (".bmp",),
    "TIFF": (".tif", ".tiff"),
    "ICO": (".ico",),
    "WEBP": (".webp",),
    "HEIF": (".heif", ".heic"),   # via pillow-heif
    "AVIF": (".avif",),           # via pillow-heif
}

# Map Common Aliases to Pillow's Format Names
FORMAT_ALIASES = {
    "JPG": "JPEG",
    "JPEG": "JPEG",
    "PNG": "PNG",
    "BMP": "BMP",
    "TIF": "TIFF",
    "TIFF": "TIFF",
    "ICO": "ICO",
    "WEBP": "WEBP",
    "HEIC": "HEIF",
    "HEIF": "HEIF",
    "AVIF": "AVIF",
}

DEFAULT_ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 72, 80, 96, 128, 160, 192, 256, 320, 384, 512)


def normalize_format(fmt: str) -> str:
    key = fmt.strip().upper()
    if key not in FORMAT_ALIASES:
        raise ValueError(f"Unknown/unsupported format: {fmt}")
    norm = FORMAT_ALIASES[key]
    # Guard HEIF/AVIF if Plugin Missing
    if norm in {"HEIF", "AVIF"} and not _HEIF_AVAILABLE:
        raise RuntimeError(
            f"{norm} support requires 'pillow-heif'. Install with: pip install pillow-heif"
        )
    return norm


def ensure_rgb_without_alpha(img: Image.Image, background=(255, 255, 255)) -> Image.Image:
    """JPEG does not support alpha; flatten transparent or LA/P modes."""
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        # Convert with Alpha Compositing onto Background
        bg = Image.new("RGB", img.size, background)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.getchannel("A"))
        return bg
    elif img.mode in ("P", "L"):
        return img.convert("RGB")
    elif img.mode == "CMYK":
        return img.convert("RGB")
    return img


def build_ico_images(img: Image.Image, sizes: Iterable[int]) -> List[Image.Image]:
    """Create resized copies for ICO multi-resolution icon."""
    images = []
    src = img
    # Prefer RGBA for Icons to Keep Transparency
    if src.mode not in ("RGBA", "RGB"):
        try:
            src = src.convert("RGBA")
        except Exception:
            src = src.convert("RGB")
    for s in sizes:
        if src.size == (s, s):
            images.append(src.copy())
        else:
            images.append(src.resize((s, s), Image.LANCZOS))
    return images


def save_image(
    img: Image.Image,
    out_path: Path,
    out_fmt: str,
    *,
    quality: Optional[int],
    optimize: bool,
    progressive: bool,
    background_for_jpeg: Tuple[int, int, int],
    ico_sizes: Tuple[int, ...],
    extra_save_kwargs: Optional[Dict] = None,
) -> None:
    exif = img.info.get("exif")
    save_kwargs = dict(extra_save_kwargs or {})

    if out_fmt == "JPEG":
        img = ensure_rgb_without_alpha(img, background=background_for_jpeg)
        if quality is not None:
            save_kwargs["quality"] = quality
        save_kwargs["optimize"] = optimize
        save_kwargs["progressive"] = progressive
        if exif:
            save_kwargs["exif"] = exif
        img.save(out_path, format="JPEG", **save_kwargs)

    elif out_fmt == "PNG":
        # Keep Alpha if Present
        if img.mode == "P" and "transparency" not in img.info:
            img = img.convert("RGBA")  # Safer Default
        save_kwargs["optimize"] = optimize
        img.save(out_path, format="PNG", **save_kwargs)

    elif out_fmt == "BMP":
        # BMP Doesn't Support Alpha; Drop It
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.save(out_path, format="BMP", **save_kwargs)

    elif out_fmt == "TIFF":
        # Preserve Exif if Present
        if exif:
            save_kwargs["exif"] = exif
        # Default to Lossless Compression
        save_kwargs.setdefault("compression", "tiff_lzw")
        img.save(out_path, format="TIFF", **save_kwargs)

    elif out_fmt == "WEBP":
        # WebP Supports Alpha + Lossy/Lossless
        if quality is not None:
            save_kwargs["quality"] = quality
        # Supports Lossless Mode via Extra_save_kwargs
        img.save(out_path, format="WEBP", **save_kwargs)

    elif out_fmt == "ICO":
        # Build Multi-res Icon
        images = build_ico_images(img, ico_sizes)
        # Pillow Expects "sizes" kw OR a List via "append_images" (for .ico it’s "sizes")
        save_kwargs["sizes"] = [(im.width, im.height) for im in images]
        # Save Using the Largest as Base; Pillow Constructs ICO from it.
        images[0].save(out_path, format="ICO", **save_kwargs)

    elif out_fmt in {"HEIF", "AVIF"}:
        # Pillow-heif Handles Both; Quality Applies
        if quality is not None:
            save_kwargs["quality"] = quality
        # Advanced Options Available via Extra_save_kwargs
        img.save(out_path, format=out_fmt, **save_kwargs)

    else:
        raise ValueError(f"Unsupported output format: {out_fmt}")


def generate_unique_filename(base_path: Path) -> Path:
    """
    Generate a unique filename by adding sequential numbers if file already exists.
    
    Args:
        base_path (Path): Base path with target extension
    
    Returns:
        Path: Unique filename that doesn't exist
    """
    if not base_path.exists():
        return base_path
    
    # Get Base Name and Extension
    base_name = base_path.stem
    extension = base_path.suffix
    
    # Try Sequential Numbers: 01, 02, 03, etc.
    counter = 1
    while True:
        new_name = f"{base_name} {counter:02d}{extension}"
        new_path = base_path.parent / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def get_format_from_extension(extension: str) -> Optional[str]:
    """
    Get format name from file extension using the global SUPPORTED_OUT_FORMATS.
    
    Args:
        extension (str): File extension (e.g., '.jpg', '.png')
    
    Returns:
        Optional[str]: Format name or None if not found
    """
    extension = extension.lower()
    for format_name, extensions in SUPPORTED_OUT_FORMATS.items():
        if extension in extensions:
            return format_name
    return None


def generate_unique_folder_name(base_folder: Path, folder_name: str) -> Path:
    """
    Generate a unique folder name by adding sequential numbers if folder already exists.
    
    Args:
        base_folder (Path): Base directory where folder will be created
        folder_name (str): Base folder name
    
    Returns:
        Path: Unique folder path that doesn't exist
    """
    folder_path = base_folder / folder_name
    if not folder_path.exists():
        return folder_path
    
    # Try Sequential Numbers: 01, 02, 03, etc.
    counter = 1
    while True:
        new_folder_name = f"{folder_name} {counter:02d}"
        new_folder_path = base_folder / new_folder_name
        if not new_folder_path.exists():
            return new_folder_path
        counter += 1


def auto_convert_folder(
    input_dir: str, 
    target_format: str, 
    **kwargs
) -> Dict[str, List[str]]:
    """
    Convert all supported images in a folder to the specified format.
    
    Args:
        input_dir (str): Path to folder containing images
        target_format (str): Target format (jpeg, png, webp, heic, avif, bmp, tiff, ico)
        **kwargs: Additional conversion options (quality, optimize, etc.)
    
    Returns:
        Dict[str, List[str]]: {"converted": [list of converted files], "skipped": [list of skipped files]}
        
    Raises:
        ValueError: If input folder doesn't exist or is not a directory
        RuntimeError: If no images are found or conversion fails
    """
    # Validate Input Folder
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_dir}")
    if not input_path.is_dir():
        raise ValueError(f"Input path is not a directory: {input_path}")
    
    # Validate Target Format
    try:
        normalized_target = normalize_format(target_format)
    except Exception as e:
        raise ValueError(f"Unsupported target format '{target_format}': {e}")
    
    # Create Output Folder with Smart Naming
    base_folder_name = "Converted Images"
    output_folder = generate_unique_folder_name(input_path, base_folder_name)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Get Supported Image Extensions
    supported_extensions = set()
    for format_exts in SUPPORTED_OUT_FORMATS.values():
        supported_extensions.update(ext.lower() for ext in format_exts)
    
    # Find All Image Files in the Folder
    image_files = []
    already_target_format = []
    
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            # Check if File is Already in Target Format
            if file_path.suffix.lower() in [ext.lower() for ext in SUPPORTED_OUT_FORMATS[normalized_target]]:
                already_target_format.append(str(file_path))
                continue
            image_files.append(file_path)
    
    if not image_files:
        print(f"ℹ️  No images need conversion - all files are already {normalized_target}")
        return {
            "converted": [],
            "skipped": already_target_format,
            "output_folder": str(output_folder)
        }
    
    print(f"🔄 Found {len(image_files)} images to convert to {normalized_target}")
    if already_target_format:
        print(f"⏭️  Skipping {len(already_target_format)} files already in {normalized_target} format")
    print(f"📁 Output folder: {output_folder.name}")
    
    # Convert Images
    converted_files = []
    failed_files = []
    
    for image_file in image_files:
        try:
            # Convert the Image Directly - Auto_convert_image Handles Unique Naming
            result = auto_convert_image(
                str(image_file), 
                target_format, 
                output_dir=str(output_folder),
                file_name=image_file.stem,
                **kwargs
            )
            
            if result:
                converted_files.append(result)
            
        except Exception as e:
            print(f"⚠️  Failed to convert {image_file.name}: {e}")
            failed_files.append(str(image_file))
    
    # Summary Report
    print(f"\n✅ Conversion completed!")
    print(f"📊 Converted: {len(converted_files)} images")
    if failed_files:
        print(f"❌ Failed: {len(failed_files)} images")
    if already_target_format:
        print(f"⏭️  Skipped (already {normalized_target}): {len(already_target_format)} files")
    print(f"📁 Output location: {output_folder}")
    
    return {
        "converted": converted_files,
        "failed": failed_files,
        "skipped_already_target": already_target_format,
        "output_folder": str(output_folder)
    }


def auto_convert_image(input_dir: str, target_format: str, output_dir: str = None, file_name: str = None, **kwargs) -> str:
    """
    Auto-convert an image file to the specified format.
    
    Args:
        input_dir (str): Full path to the input image file
        target_format (str): Target format (jpeg, png, webp, heic, avif, bmp, tiff, ico)
        output_dir (str, optional): Output directory path (without filename). If None, uses input file's directory.
        file_name (str, optional): Custom filename without extension (e.g., "my file"). If None, uses input filename.
        **kwargs: Additional conversion options (quality, optimize, etc.)
    
    Returns:
        str: Path to the converted image file
        
    Raises:
        ValueError: If input file doesn't exist or format is unsupported
        RuntimeError: If conversion fails
    """
    # Validate Input File
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input file does not exist: {input_dir}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")
    
    # Auto-detect Input Format from File Extension Using Unified Mapping
    input_extension = input_path.suffix.lower()
    input_format = get_format_from_extension(input_extension)
    
    if input_format:
        print(f"✓ Auto-detected input format: {input_format}")
    else:
        print(f"⚠️  Unknown input format: {input_extension}")
    
    # Validate Target Format
    try:
        normalized_target = normalize_format(target_format)
        print(f"✓ Target format: {normalized_target}")
    except Exception as e:
        raise ValueError(f"Unsupported target format '{target_format}': {e}")
    
    # Check if Input Format Matches Target Format (Skip Unnecessary Conversion)
    if input_format and input_format == normalized_target:
        print(f"ℹ️  File is already in {normalized_target} format - no conversion needed")
        return str(input_path)  # Return Original File Path
    
    # Generate Output Path Using Separated Directory and Filename Parameters
    if output_dir is None:
        # Use Input File's Directory
        output_dir_path = input_path.parent
    else:
        # Use Specified Output Directory
        output_dir_path = Path(output_dir)
        # Create Directory if it Doesn't Exist
        output_dir_path.mkdir(parents=True, exist_ok=True)
    
    if file_name is None:
        # Use Input Filename (Without Extension)
        base_name = input_path.stem
    else:
        # Use Custom Filename (Strip Any Extension if User Provided One)
        base_name = Path(file_name).stem
    
    # Get the Appropriate Extension for the Target Format
    target_ext = SUPPORTED_OUT_FORMATS[normalized_target][0]
    
    # Create the Base Output Path
    base_output_path = output_dir_path / f"{base_name}{target_ext}"
    
    # Generate Unique Filename to Avoid Overwriting
    final_output_path = generate_unique_filename(base_output_path)
    if final_output_path != base_output_path:
        print(f"📝 File exists, generating unique name: {final_output_path.name}")
    
    print(f"📁 Output directory: {output_dir_path}")
    print(f"📝 Output filename: {final_output_path.name}")
    
    # Set Default Conversion Options
    conversion_options = {
        'overwrite': kwargs.get('overwrite', False),  # Changed Default to False
        'quality': kwargs.get('quality', None),
        'optimize': kwargs.get('optimize', True),
        'progressive': kwargs.get('progressive', True),
        'background_for_jpeg': kwargs.get('jpeg_bg', (255, 255, 255)),
        'ico_sizes': kwargs.get('ico_sizes', DEFAULT_ICO_SIZES),
        'extra_save_kwargs': kwargs.get('extra_save_kwargs', {})
    }
    
    print(f"🔄 Converting {input_path.name} ({input_format or 'unknown'}) → {normalized_target}")
    
    # Perform Conversion Using Save_image Directly
    try:
        with Image.open(input_path) as im:
            im.load()
            save_image(
                im,
                final_output_path,
                normalized_target,
                quality=conversion_options['quality'],
                optimize=conversion_options['optimize'],
                progressive=conversion_options['progressive'],
                background_for_jpeg=conversion_options['background_for_jpeg'],
                ico_sizes=conversion_options['ico_sizes'],
                extra_save_kwargs=conversion_options['extra_save_kwargs']
            )
        print(f"✅ Conversion successful: {final_output_path}")
        return str(final_output_path)
    except Exception as e:
        raise RuntimeError(f"Conversion failed: {input_path} → {normalized_target}: {e}")
