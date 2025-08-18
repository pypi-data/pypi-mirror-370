from dataclasses import dataclass, field
from typing import List, Any
import gradio as gr
from gradio_imagemeta import ImageMeta
from gradio_imagemeta.helpers import extract_metadata, add_metadata, transfer_metadata
from gradio_propertysheet import PropertySheet
from gradio_propertysheet.helpers import build_dataclass_fields, create_dataclass_instance
from pathlib import Path


output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

@dataclass
class ImageSettings:
    """Configuration for image metadata settings."""
    model: str = field(default="", metadata={"label": "Model"})
    f_number: str = field(default="", metadata={"label": "FNumber"})
    iso_speed_ratings: str = field(default="", metadata={"label": "ISOSpeedRatings"})
    s_churn: float = field(
        default=0.0,
        metadata={"component": "slider", "label": "Schurn", "minimum": 0.0, "maximum": 1.0, "step": 0.01},
    )

@dataclass
class PropertyConfig:
    """Root configuration for image properties, including nested image settings."""
    image_settings: ImageSettings = field(default_factory=ImageSettings)
    description: str = field(default="", metadata={"label": "Description"})

def infer_type(s: str):
    """
    Infers and converts a string to the most likely data type.

    It attempts conversions in the following order:
    1. Integer
    2. Float
    3. Boolean (case-insensitive 'true' or 'false')
    If all conversions fail, it returns the original string.

    Args:
        s: The input string to be converted.

    Returns:
        The converted value (int, float, bool) or the original string.
    """
    if not isinstance(s, str):
        # If the input is not a string, return it as is.
        return s

    # 1. Try to convert to an integer
    try:
        return int(s)
    except ValueError:
        # Not an integer, continue...
        pass

    # 2. Try to convert to a float
    try:
        return float(s)
    except ValueError:
        # Not a float, continue...
        pass
    
    # 3. Check for a boolean value
    # This explicit check is important because bool('False') evaluates to True.
    s_lower = s.lower()
    if s_lower == 'true':
        return True
    if s_lower == 'false':
        return False
        
    # 4. If nothing else worked, return the original string
    return s

def handle_load_metadata(image_data: ImageMeta | None) -> List[Any]:
    """
    Processes image metadata and maps it to output components.

    Args:
        image_data: ImageMeta object containing image data and metadata, or None.

    Returns:
        A list of values for output components (Textbox, Slider, or PropertySheet instances).
    """
    if not image_data:
        return [gr.Textbox(value="") for _ in output_fields]

    metadata = extract_metadata(image_data, only_custom_metadata=True)
    dataclass_fields = build_dataclass_fields(PropertyConfig)
    raw_values = transfer_metadata(output_fields, metadata, dataclass_fields)

    output_values = [gr.skip()] * len(output_fields)
    for i, (component, value) in enumerate(zip(output_fields, raw_values)):        
        if hasattr(component, 'root_label'):
            output_values[i] = create_dataclass_instance(PropertyConfig, value)
        else:
            output_values[i] = gr.update(value=infer_type(value))
    
    return output_values

def save_image_with_metadata(image_data: Any, *inputs: Any) -> str | None:
    """
    Saves an image with updated metadata to a file.

    Args:
        image_data: Input image data (e.g., file path or PIL Image).
        *inputs: Variable number of input values from UI components (Textbox, Slider).

    Returns:
        The file path of the saved image, or None if no image is provided.
    """
    if not image_data:
        return None
    
    params = list(inputs)
    image_params = dict(zip(input_fields.keys(), params))
    #dataclass_fields = build_dataclass_fields(PropertyConfig)
    metadata = {label: image_params.get(label, "") for label in image_params.keys()}
    
    new_filepath = output_dir / "image_with_meta.png"
    
    add_metadata(image_data, metadata, new_filepath)
    
    return str(new_filepath)

initial_property_from_meta_config = PropertyConfig()

with gr.Blocks() as demo:
    gr.Markdown("# ImageMeta Component Demo")
    gr.Markdown(
        """
        **To Test:**
        1. Upload an image with EXIF or PNG metadata using either the "Upload Imagem (Custom metadata only)" component or the "Upload Imagem (all metadata)" component.
        2. Click the 'Info' icon (ⓘ) in the top-left of the image component to view the metadata panel.
        3. Click 'Load Metadata' in the popup to populate the fields below with metadata values (`Model`, `FNumber`, `ISOSpeedRatings`, `Schurn`, `Description`).
        4. The section below displays how metadata is rendered in components and the `PropertySheet` custom component, showing the hierarchical structure of the image settings.
        5. In the "Metadata Viewer" section, you can add field values as metadata to a previously uploaded image in "Upload Image (Custom metadata only)." Then click 'Add metadata and save image' to save a new image with the metadata.
        """
    )
    property_sheet_state = gr.State(value=initial_property_from_meta_config)
    with gr.Row():
        img_custom = ImageMeta(
            label="Upload Image (Custom metadata only)",
            type="filepath",
            width=300,
            height=400,            
            interactive=True
        )
        img_all = ImageMeta(
            label="Upload Image (All metadata)",
            only_custom_metadata=False,
            type="filepath",
            width=300,
            height=400,            
            popup_metadata_height=400,
            popup_metadata_width=500,
            interactive=True
        )

    gr.Markdown("## Metadata Viewer")
    gr.Markdown("### Individual Components")
    with gr.Row():
        model_box = gr.Textbox(label="Model")
        fnumber_box = gr.Textbox(label="FNumber")
        iso_box = gr.Textbox(label="ISOSpeedRatings")
        s_churn = gr.Slider(label="Schurn", value=1.0, minimum=0.0, maximum=1.0, step=0.1)
        description_box = gr.Textbox(label="Description")
    
    gr.Markdown("### PropertySheet Component")
    with gr.Row():
        property_sheet = PropertySheet(
            value=initial_property_from_meta_config,
            label="Image Settings",
            width=400,
            height=550,
            visible=True,
            root_label="General"
        )    
    gr.Markdown("## Metadata Editor")
    with gr.Row():
        save_button = gr.Button("Add Metadata and Save Image")
        saved_file_output = gr.File(label="Download Image")
   
        
    input_fields = {
        "Model": model_box,
        "FNumber": fnumber_box,
        "ISOSpeedRatings": iso_box,
        "Schurn": s_churn,
        "Description": description_box
    }
    
    output_fields = [
        property_sheet,
        model_box,
        fnumber_box,
        iso_box,
        s_churn,
        description_box
    ]
    
    img_custom.load_metadata(handle_load_metadata, inputs=img_custom, outputs=output_fields)
    img_all.load_metadata(handle_load_metadata, inputs=img_all, outputs=output_fields)
    
    def handle_render_change(updated_config: PropertyConfig, current_state: PropertyConfig):
        """
        Updates the PropertySheet state when its configuration changes.

        Args:
            updated_config: The new PropertyConfig instance from the PropertySheet.
            current_state: The current PropertyConfig state.

        Returns:
            A tuple of (updated_config, updated_config) or (current_state, current_state) if updated_config is None.
        """
        if updated_config is None:
            return current_state, current_state
        return updated_config, updated_config
    
    property_sheet.change(
        fn=handle_render_change,
        inputs=[property_sheet, property_sheet_state],
        outputs=[property_sheet, property_sheet_state]
    )
    save_button.click(
        save_image_with_metadata,
        inputs=[img_custom, *input_fields.values()],
        outputs=[saved_file_output]
    )
    
if __name__ == "__main__":
    demo.launch()