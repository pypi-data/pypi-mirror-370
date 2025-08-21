#!/usr/bin/env python3
"""
GIF Creation Module - Convert Multiple Images to GIF Format
"""

from pathlib import Path
from PIL import Image

# Import Supported Formats and Utility Functions From the Main Conversion Module
from .general_conversion import SUPPORTED_OUT_FORMATS, generate_unique_filename


def calculate_easing_durations(num_frames: int, base_duration: int, easing: str, easing_strength: float = 1.0) -> list:
    """
    Calculate frame durations based on easing curve.
    
    Args:
        num_frames (int): Number of frames in the animation
        base_duration (int): Base duration in milliseconds
        easing (str): Easing type: "ease-in", "ease-out", "ease-in-out"
        easing_strength (float): Strength of easing effect (0.5 = subtle, 1.0 = normal, 2.0 = extreme)
        
    Returns:
        list: List of frame durations in milliseconds
    """
    if num_frames <= 1:
        return [base_duration]
    
    durations = []
    
    if easing == "ease-in":
        # Start Slow, End Fast
        for i in range(num_frames):
            # Quadratic Ease-in: t²
            progress = (i / (num_frames - 1)) ** 2
            # Apply Easing Strength: Stronger = More Dramatic Timing Difference
            strength_factor = 0.5 + (0.5 * progress * easing_strength)
            duration = int(base_duration * max(0.1, min(2.0, strength_factor)))
            durations.append(duration)
    
    elif easing == "ease-out":
        # Start Fast, End Slow
        for i in range(num_frames):
            # Quadratic Ease-out: 1 - (1-t)²
            progress = i / (num_frames - 1)
            ease_progress = 1 - (1 - progress) ** 2
            # Apply Easing Strength: Stronger = More Dramatic Timing Difference
            strength_factor = 0.5 + (0.5 * ease_progress * easing_strength)
            duration = int(base_duration * max(0.1, min(2.0, strength_factor)))
            durations.append(duration)
    
    elif easing == "ease-in-out":
        # Start Slow, Middle Fast, End Slow
        for i in range(num_frames):
            progress = i / (num_frames - 1)
            if progress < 0.5:
                # First Half: Ease-in
                ease_progress = 2 * progress ** 2
            else:
                # Second Half: Ease-out
                ease_progress = 1 - 2 * (1 - progress) ** 2
            
            # Apply Easing Strength: Stronger = More Dramatic Timing Difference
            strength_factor = 0.5 + (0.5 * ease_progress * easing_strength)
            duration = int(base_duration * max(0.1, min(2.0, strength_factor)))
            durations.append(duration)
    
    else:
        # No Easing: Uniform Duration
        durations = [base_duration] * num_frames
    
    return durations


def convert_images_to_gif(
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
) -> str:
    """
    Create a GIF from all supported images found in a folder.
    
    Args:
        input_dir (str): Path to folder containing images
        file_name (str, optional): Custom name for the GIF file (without extension). If None, uses automatic naming.
        output_dir (str, optional): Output directory path. If None or invalid, uses input folder.
        duration (int): Duration per frame in milliseconds (default: 100)
        loop (int): Number of loops (0 = infinite, default: 0)
        color_mode (str): Color mode for GIF conversion. Options: "RGB" (default), "P" (Indexed), "L" (Grayscale)
        color_count (int): Number of colors for P and L modes. Range: 2-256. RGB mode ignores this parameter.
        brightness (float): Brightness multiplier (0.0 = black, 1.0 = normal, 2.0 = twice as bright, default: 1.0)
        contrast (float): Contrast multiplier (0.0 = no contrast, 1.0 = normal, 2.0 = high contrast, default: 1.0)
        saturation (float): Saturation multiplier (0.0 = grayscale, 1.0 = normal, 2.0 = oversaturated, default: 1.0)
        ping_pong (bool): Enable ping-pong loop (forward→backward→forward, default: False)
        easing (str): Easing curve for timing. Options: "none" (default), "ease-in", "ease-out", "ease-in-out"
        easing_strength (float): Strength of easing effect (0.5 = subtle, 1.0 = normal, 2.0 = extreme, default: 1.0)
        
    Returns:
        str: Path to the created GIF file
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_dir}")
    if not input_path.is_dir():
        raise ValueError(f"Input path is not a directory: {input_path}")
    
    # Set Output Directory with Fallback Logic
    if output_dir is None:
        output_dir_path = input_path
    else:
        try:
            output_dir_path = Path(output_dir)
            # Try to create directory if it doesn't exist
            if not output_dir_path.exists():
                output_dir_path.mkdir(parents=True, exist_ok=True)
            # Validate it's actually a directory and accessible
            if not output_dir_path.is_dir():
                print(f"⚠️  Warning: Invalid output_dir '{output_dir}', using input folder")
                output_dir_path = input_path
            else:
                # Test if we can actually write to this directory
                try:
                    test_file = output_dir_path / ".test_write_access"
                    test_file.touch()
                    test_file.unlink()
                except Exception:
                    print(f"⚠️  Warning: Cannot write to output_dir '{output_dir}', using input folder")
                    output_dir_path = input_path
        except Exception as e:
            print(f"⚠️  Warning: Invalid output_dir '{output_dir}', using input folder")
            output_dir_path = input_path
    
    print(f"📁 Output directory: {output_dir_path}")
    
    # Validate Color Mode
    valid_color_modes = ["RGB", "P", "L"]
    if color_mode.upper() not in valid_color_modes:
        raise ValueError(f"Invalid color_mode: {color_mode}. Must be one of: {', '.join(valid_color_modes)}")
    
    color_mode = color_mode.upper()  # Normalize to Uppercase
    
    # Validate Easing Parameter
    valid_easing = ["none", "ease-in", "ease-out", "ease-in-out"]
    if easing.lower() not in valid_easing:
        raise ValueError(f"Invalid easing: {easing}. Must be one of: {', '.join(valid_easing)}")
    
    easing = easing.lower()  # Normalize to Lowercase
    
    # Validate and Auto-Correct Duration Parameter
    original_duration = duration
    if duration < 1 or duration > 10000:
        duration = 100  # Default Value
        print(f"⚠️  Warning: Invalid duration {original_duration}ms. Setting to default {duration}ms and continuing.")
    
    # Validate and Auto-Correct Loop Parameter
    original_loop = loop
    if loop < 0:
        loop = 0  # Default Value (Infinite)
        print(f"⚠️  Warning: Invalid loop {original_loop}. Setting to default {loop} (infinite) and continuing.")
    
    # Validate and Auto-Correct file_name Parameter
    original_file_name = file_name
    if file_name is not None and (not isinstance(file_name, str) or file_name.strip() == ""):
        file_name = None  # Default Value (Automatic Naming)
        print(f"⚠️  Warning: Invalid file_name '{original_file_name}'. Using automatic naming instead.")
    
    # Validate and Auto-Correct Easing Strength Parameter
    original_easing_strength = easing_strength
    if easing_strength < 0.1 or easing_strength > 5.0:
        easing_strength = 1.0  # Default Value
        print(f"⚠️  Warning: Invalid easing_strength {original_easing_strength}. Setting to default {easing_strength}x and continuing.")
    
    # Validate and Auto-Correct Effect Parameters
    original_brightness = brightness
    if brightness < 0.0 or brightness > 5.0:
        brightness = 1.0  # Default Value
        print(f"⚠️  Warning: Invalid brightness {original_brightness}. Setting to default {brightness}x and continuing.")
    
    original_contrast = contrast
    if contrast < 0.0 or contrast > 5.0:
        contrast = 1.0  # Default value
        print(f"⚠️  Warning: Invalid contrast {original_contrast}. Setting to default {contrast}x and continuing.")
    
    original_saturation = saturation
    if saturation < 0.0 or saturation > 5.0:
        saturation = 1.0  # Default Value
        print(f"⚠️  Warning: Invalid saturation {original_saturation}. Setting to default {saturation}x and continuing.")
    
    # Show Effect Settings if Any Are Modified
    effects_applied = []
    if brightness != 1.0:
        effects_applied.append(f"Brightness: {brightness}x")
    if contrast != 1.0:
        effects_applied.append(f"Contrast: {contrast}x")
    if saturation != 1.0:
        effects_applied.append(f"Saturation: {saturation}x")
    
    if effects_applied:
        print(f"🎨 Effects: {', '.join(effects_applied)}")
    
    # Show Animation Settings if Any Are Modified
    animation_settings = []
    if ping_pong:
        animation_settings.append("Ping-pong loop")
    if easing != "none":
        strength_text = f" (strength: {easing_strength}x)"
        animation_settings.append(f"Easing: {easing}{strength_text}")
    
    if animation_settings:
        print(f"🎬 Animation: {', '.join(animation_settings)}")
    
    # Smart Color Count Handling With Fallback Logic
    if color_mode == "RGB":
        # RGB Mode Ignores Color_count - Always Use Full Color
        print(f"🎨 Color mode: {color_mode} (ignoring color_count parameter)")
    else:
        # P and L Modes Validate and Use Color_count
        original_color_count = color_count
        if color_count < 2 or color_count > 256:
            color_count = 256  # Default Value
            print(f"⚠️  Warning: Invalid color_count {original_color_count}. Setting to default {color_count} and continuing.")
        
        print(f"🎨 Color mode: {color_mode}, Color count: {color_count}")
    
    # Generate Output Path Based on file_name or Automatic Naming
    if file_name is not None:
        # Use file_name with .gif Extension
        base_output_path = output_dir_path / f"{file_name}.gif"
        output_path = generate_unique_filename(base_output_path)
        print(f"📝 Custom name output path: {output_path}")
    else:
        # Use Automatic Naming (Animation.gif, Animation 01.gif, etc.)
        base_output_path = output_dir_path / "Animation.gif"
        output_path = generate_unique_filename(base_output_path)
        print(f"📝 Auto-generated output path: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get All Supported Image Extensions From the Main Conversion Module
    supported_extensions = set()
    for format_exts in SUPPORTED_OUT_FORMATS.values():
        supported_extensions.update(ext.lower() for ext in format_exts)
    
    # Find All Image Files in the Folder
    image_files = []
    skipped_files = []
    
    for file_path in input_path.iterdir():
        if file_path.is_file():
            file_ext = file_path.suffix.lower()
            
            # Skip if Not an Image File
            if file_ext not in supported_extensions:
                continue
            
            # Skip Existing GIF Files
            if file_ext == '.gif':
                skipped_files.append(f"GIF file: {file_path.name}")
                continue
            
            image_files.append(file_path)
    
    if not image_files:
        raise RuntimeError(f"No supported images found in {input_dir}")
    
    # Sort Files by Name for Consistent Ordering
    image_files.sort(key=lambda x: x.name)
    
    print(f"🔄 Found {len(image_files)} images to combine into GIF")
    if skipped_files:
        print(f"⏭️  Skipped: {len(skipped_files)} files")
        for skipped in skipped_files:
            print(f"   - {skipped}")
    
    # Load All Images
    images = []
    failed_images = []
    
    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                # Convert to Specified Color Mode
                if img.mode != color_mode:
                    if color_mode == "RGB":
                        # For RGB, Convert RGBA/LA to RGB, Others as-is
                        if img.mode in ('RGBA', 'LA'):
                            img = img.convert('RGB')
                    elif color_mode == "L":
                        # For Grayscale, Convert Any Mode to L
                        img = img.convert('L')
                    elif color_mode == "P":
                        # For Indexed, Convert to P
                        img = img.convert('P', palette=Image.ADAPTIVE)
                
                # Apply Brightness, Contrast, and Saturation Effects
                if brightness != 1.0 or contrast != 1.0 or saturation != 1.0:
                    # Convert to RGB for Color Processing
                    if img.mode not in ('RGB', 'RGBA'):
                        img = img.convert('RGB')
                    
                    # Apply Brightness
                    if brightness != 1.0:
                        img = img.point(lambda p: int(p * brightness))
                    
                    # Apply Contrast
                    if contrast != 1.0:
                        img = img.point(lambda p: int(128 + (p - 128) * contrast))
                    
                    # Apply Saturation
                    if saturation != 1.0:
                        hsv_img = img.convert('HSV')
                        h, s, v = hsv_img.split()
                        s = s.point(lambda p: int(p * saturation))
                        img = Image.merge('HSV', (h, s, v)).convert('RGB')
                
                # Apply Color Count Reduction for P and L Modes
                if color_mode == "L" and color_count < 256:
                    img = img.quantize(colors=color_count)
                elif color_mode == "P" and color_count < 256:
                    img = img.quantize(colors=color_count)
                
                images.append(img.copy())
                print(f"✅ Loaded: {img_path.name} (converted to {color_mode})")
        except Exception as e:
            print(f"⚠️  Warning: Could not load {img_path.name}: {e}")
            failed_images.append(str(img_path))
    
    if not images:
        raise RuntimeError("No valid images could be loaded")
    
    if failed_images:
        print(f"⚠️  Warning: Failed to load {len(failed_images)} images")
    
    # Save as GIF
    try:
        # Create a Copy of Images List to Avoid Modifying the Original
        gif_images = images.copy()
        
        # Apply Ping-pong Effect if Requested
        if ping_pong and len(gif_images) > 1:
            # Create Ping-pong Sequence: Forward → Backward → Forward
            # Example: [1,2,3,4] Becomes [1,2,3,4,3,2,1,2,3,4,3,2,1...]
            forward_frames = gif_images
            backward_frames = gif_images[-2:0:-1]  # Reverse, excluding first and last
            
            # Combine: Forward + Backward + Forward (for Smooth Loop)
            gif_images = forward_frames + backward_frames + forward_frames
            print(f"🔄 Ping-pong: {len(images)} frames → {len(gif_images)} frames")
        
        # Calculate Easing-Based Frame Durations if Requested
        frame_durations = []
        if easing != "none" and len(gif_images) > 1:
            frame_durations = calculate_easing_durations(len(gif_images), duration, easing, easing_strength)
            print(f"⏱️  Easing: {easing} timing applied")
        else:
            # Use Uniform Duration for All Frames
            frame_durations = [duration] * len(gif_images)
        
        # Use Simple PIL Method for All Loop Scenarios
        save_kwargs = {
            'format': 'GIF',
            'save_all': True,
            'append_images': gif_images[1:],
            'duration': frame_durations,
            'loop': loop,
            'optimize': True
        }
        
        images[0].save(output_path, **save_kwargs)
        
        print(f"🎬 GIF created successfully: {output_path}")
        print(f"📊 Frames: {len(gif_images)}, Duration: {duration}ms, Loop: {'infinite' if loop == 0 else loop}")
        return str(output_path)
    
    except Exception as e:
        raise RuntimeError(f"Failed to create GIF: {e}")
