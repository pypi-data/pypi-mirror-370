from dataclasses import fields
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image, PngImagePlugin, ExifTags
import numpy as np
from gradio import image_utils

def extract_metadata(image_data: str | Path | Image.Image | np.ndarray | None, only_custom_metadata: bool = True) -> Dict[str, Any]:
    """
    Extracts metadata from an image.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, NumPy array, or None.
        only_custom_metadata: If True, excludes technical metadata (e.g., ImageWidth, ImageHeight). Defaults to True.

    Returns:
        Dictionary of extracted metadata. Returns empty dictionary if no metadata is available or extraction fails.
    """
    if not image_data:
        return {}

    try:
        # Convert image_data to PIL.Image
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        elif hasattr(image_data, 'path'):  # For ImageMetaData
            image = Image.open(image_data.path)
        else:
            return {}

        decoded_meta = {}
        if image.format == "PNG":
            if not only_custom_metadata:
                decoded_meta["ImageWidth"] = image.width
                decoded_meta["ImageHeight"] = image.height
            metadata = image.info
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    decoded_meta[str(key)] = value
        else:
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        value = value.decode(errors='ignore')
                    decoded_meta[str(tag)] = value
            if not only_custom_metadata:
                decoded_meta["ImageWidth"] = image.width
                decoded_meta["ImageHeight"] = image.height

        return decoded_meta
    except Exception:
        return {}

def preprocess_image(image_data: str | Path | Image.Image | np.ndarray, type: str = "numpy") -> np.ndarray | Image.Image:
    """
    Processes an image to the specified format.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, or NumPy array.
        type: Output format, either "numpy" (array with shape (height, width, 3)) or "pil" (PIL Image). Defaults to "numpy".

    Returns:
        Processed image as a NumPy array or PIL Image.

    Raises:
        ValueError: If image_data type or output type is unsupported.
    """
    if isinstance(image_data, (str, Path)):
        payload = image_data
    elif isinstance(image_data, Image.Image):
        payload = image_data
    elif isinstance(image_data, np.ndarray):
        payload = image_data
    elif hasattr(image_data, 'path'):  # For ImageMetaData
        payload = image_data.path
    else:
        raise ValueError(f"Unsupported image_data type: {type(image_data)}")

    if type == "numpy":
        return image_utils.preprocess_image(payload, type="numpy")
    elif type == "pil":
        return image_utils.preprocess_image(payload, type="pil")
    else:
        raise ValueError(f"Unsupported type: {type}")

def add_metadata(image_data: str | Path | Image.Image | np.ndarray, metadata: Dict[str, Any], save_path: str) -> bool:
    """
    Adds metadata to an image and saves it to the specified path.

    Args:
        image_data: Image data as a filepath, Path, PIL Image, or NumPy array.
        metadata: Dictionary of metadata to add to the image.
        save_path: Filepath where the modified image will be saved.

    Returns:
        True if metadata was added and image was saved successfully, False otherwise.
    """
    try:
        if not bool(save_path):
            return False
        
        
        # Convert image_data to PIL.Image
        if isinstance(image_data, (str, Path)):
            image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        elif hasattr(image_data, 'path'):  # For ImageMetaData
            image = Image.open(image_data.path)
        else:
            return False

        image_copy = image.copy()
        if image.format == "PNG":
            meta = PngImagePlugin.PngInfo()
            for key, value in metadata.items():
                meta.add_text(str(key), str(value))
            image_copy.info.update(metadata)  # For reference, but requires pnginfo when saving
            image_copy.save(save_path, pnginfo=meta)
        else:
            exif = image_copy.getexif() or Image.Exif()
            for key, value in metadata.items():
                tag_id = next((k for k, v in ExifTags.TAGS.items() if v == key), None)
                if tag_id:
                    exif[tag_id] = value
            image_copy.exif = exif
            image_copy.save(save_path)    
        return True
    except Exception:
        return False
    
def transfer_metadata(output_fields: List[Any], metadata: Dict[str, Any], dataclass_fields: Dict[str, str]) -> List[Any]:
    """
    Maps metadata to a list of output components based on their labels.

    Args:
        output_fields: List of components (e.g., Textbox, PropertySheet).
        metadata: Dictionary of extracted image metadata.
        dataclass_fields: Dictionary mapping component labels (e.g., 'Model') to field paths (e.g., 'image_settings.model' or 'description').

    Returns:
        List of values (strings for Textbox, nested dictionary for PropertySheet) in the same order as output_fields.
    """
    output_values = [None] * len(output_fields)
    for i, component in enumerate(output_fields):
        label = getattr(component, 'label', None)

        # Check if the component is a PropertySheet via root_label attribute
        is_property_sheet = hasattr(component, 'root_label')
        if is_property_sheet:
            # Create nested dictionary for PropertySheet
            updated_config = {}
            for dataclass_label, field_path in dataclass_fields.items():
                value = str(metadata.get(dataclass_label, 'None'))
                value = None if value == 'None' else value
                # Split field_path into parts (e.g., 'image_settings.model' -> ['image_settings', 'model'])
                parts = field_path.split('.')
                # Build nested structure in dictionary
                current = updated_config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                # Assign value to final field
                current[parts[-1]] = value
            output_values[i] = updated_config
        else:
            # For other components (e.g., Textbox), assign raw value
            value = str(metadata.get(label, None)) if label else None
            value = None if value == 'None' else value
            output_values[i] = value
    
    return output_values