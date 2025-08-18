from __future__ import annotations
from collections.abc import Callable, Sequence
from pathlib import Path
from PIL import Image
import numpy as np
from typing import TYPE_CHECKING, Any, Literal
from gradio_client import handle_file
from gradio.components.base import Component
from gradio.data_classes import Base64ImageData, ImageData
from gradio.events import Events, EventListener
from gradio import image_utils, utils
from gradio.i18n import I18nData

if TYPE_CHECKING:
    from gradio.components import Timer

Image.init()

class ImageMetaData(ImageData):
    """Custom data model for image data with metadata support."""
    pass

class ImageMeta(Component):
    """
    A Gradio component for uploading or displaying images, with support for metadata extraction and a custom load_metadata event.

    This component allows users to upload images (as input) or display images (as output). It includes a custom event for loading metadata, triggered by a 'Load Metadata' button in the UI, which expects ImageMetaData as input.
    """
    load_metadata = EventListener(
        "load_metadata",
        doc="Triggered when the user clicks the 'Load Metadata' button, expecting ImageMetaData as input."
    )

    EVENTS = [
        Events.clear,
        Events.change,
        Events.select,
        Events.upload,
        Events.input,
        load_metadata,
    ]

    data_model = ImageMetaData
    image_mode: Literal["1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"] | None
    type: Literal["numpy", "pil", "filepath"]

    def __init__(
        self,
        value: str | Image.Image | np.ndarray | Callable | None = None,
        *,
        format: str = "webp",
        height: int | str | None = None,
        width: int | str | None = None,
        image_mode: Literal["1", "L", "P", "RGB", "RGBA", "CMYK", "YCbCr", "LAB", "HSV", "I", "F"] | None = "RGB",
        type: Literal["numpy", "pil", "filepath"] = "numpy",
        label: str | I18nData | None = None,
        every: Timer | float | None = None,
        inputs: Component | Sequence[Component] | set[Component] | None = None,
        show_label: bool | None = None,
        show_download_button: bool = True,
        container: bool = True,
        scale: int | None = None,
        min_width: int = 160,
        interactive: bool | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        render: bool = True,
        key: int | str | tuple[int | str, ...] | None = None,
        preserved_by_key: list[str] | str | None = "value",
        show_share_button: bool | None = None,
        placeholder: str | None = None,
        show_fullscreen_button: bool = True,
        only_custom_metadata: bool = True,
        disable_preprocess: bool = True,
        popup_metadata_width: int | str = 400,
        popup_metadata_height: int | str = 300,
    ):
        """
        Initializes the ImageMeta component.

        Args:
            value: A PIL Image, numpy array, path or URL for the default value that Image component is going to take. If a function is provided, the function will be called each time the app loads to set the initial value of this component.
            format: File format (e.g. "png" or "gif"). Used to save image if it does not already have a valid format (e.g. if the image is being returned to the frontend as a numpy array or PIL Image). The format should be supported by the PIL library. Applies both when this component is used as an input or output. This parameter has no effect on SVG files.
            height: The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.
            width: The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.
            image_mode: The pixel format and color depth that the image should be loaded and preprocessed as. "RGB" will load the image as a color image, or "L" as black-and-white. See https://pillow.readthedocs.io/en/stable/handbook/concepts.html for other supported image modes and their meaning. This parameter has no effect on SVG or GIF files. If set to None, the image_mode will be inferred from the image file type (e.g. "RGBA" for a .png image, "RGB" in most other cases).
            type: The format the image is converted before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. To support animated GIFs in input, the `type` should be set to "filepath" or "pil". To support SVGs, the `type` should be set to "filepath".
            label: The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.
            every: Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.
            inputs: Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.
            show_label: If True, will display label.
            show_download_button: If True, will display button to download image. Only applies if interactive is False (e.g. if the component is used as an output).
            container: If True, will place the component in a container - providing some extra padding around the border.
            scale: Relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.
            min_width: Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.
            interactive: If True, will allow users to upload and edit an image; if False, can only be used to display images. If not provided, this is inferred based on whether the component is used as an input or output.
            visible: If False, component will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.
            render: If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.
            key: In a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.
            preserved_by_key: A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.
            show_share_button: If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.
            placeholder: Custom text for the upload area. Overrides default upload messages when provided. Accepts new lines and `#` to designate a heading.
            show_fullscreen_button: If True, will show a fullscreen icon in the corner of the component that allows user to view the image in fullscreen mode. If False, icon does not appear.
            only_custom_metadata: If True, extracts only custom metadata, excluding technical metadata like ImageWidth or ImageHeight. Defaults to True.
            disable_preprocess: If True, skips preprocessing and returns the raw ImageMetaData payload. Defaults to True.
            popup_metadata_width: Metadata popup width in pixels or CSS units. Defaults to 400.
            popup_metadata_height: Metadata popup height in pixels or CSS units. Defaults to 300.
        """
        self.format = format
        self.height = height
        self.width = width
        self.image_mode = image_mode
        valid_types = ["numpy", "pil", "filepath"]
        if type not in valid_types:
            raise ValueError(f"Invalid value for parameter `type`: {type}. Please choose from one of: {valid_types}")
        self.type = type
        self.show_download_button = show_download_button
        self.show_share_button = (utils.get_space() is not None) if show_share_button is None else show_share_button
        self.show_fullscreen_button = show_fullscreen_button
        self.placeholder = placeholder
        self.only_custom_metadata = only_custom_metadata
        self.disable_preprocess = disable_preprocess
        self.popup_metadata_width = popup_metadata_width
        self.popup_metadata_height = popup_metadata_height

        super().__init__(
            label=label,
            every=every,
            inputs=inputs,
            show_label=show_label,
            container=container,
            scale=scale,
            min_width=min_width,
            interactive=interactive,
            visible=visible,
            elem_id=elem_id,
            elem_classes=elem_classes,
            render=render,
            key=key,
            preserved_by_key=preserved_by_key,
            value=value,
        )
        self._value_description = (
            "a filepath to an image" if self.type == "filepath" else
            ("a numpy array representing an image" if self.type == "numpy" else "a PIL Image")
        )

    def preprocess(
        self, payload: ImageMetaData | None
    ) -> np.ndarray | Image.Image | str | ImageMetaData | None:
        """
        Preprocesses the input image data for use in the application.

        Args:
            payload: ImageMetaData object containing image data and metadata, or None.

        Returns:
            Preprocessed image as a NumPy array, PIL Image, filepath, ImageMetaData, or None.
        """
        if payload is None or not hasattr(payload, "path"):
            return None
        
        if self.disable_preprocess:
            return payload
                                
        return image_utils.preprocess_image(
            payload,
            cache_dir=self.GRADIO_CACHE,
            format=self.format,
            image_mode=self.image_mode,
            type=self.type,
        )

    def postprocess(
        self, value: np.ndarray | Image.Image | str | Path | None
    ) -> ImageMetaData | Base64ImageData | None:
        """
        Post-processes the input image to prepare it for rendering, preserving the original format when interactive=False.

        Args:
            value: Input image as a NumPy array, PIL Image, string (file path or URL), Path object, or None.

        Returns:
            Processed image data as ImageMetaData, Base64ImageData, or None.
        """
        format = self.format
        if not self.interactive:
            if isinstance(value, Image.Image) and value.format:
                format = value.format.lower()
            elif isinstance(value, (str, Path)):
                ext = str(value).rsplit(".", 1)[-1].lower() if "." in str(value) else None
                if ext in ["png", "jpg", "jpeg", "webp", "gif"]:
                    format = ext
        
        return image_utils.postprocess_image(
            value,
            cache_dir=self.GRADIO_CACHE,
            format=format,
        )

    def api_info_as_output(self) -> dict[str, Any]:
        """
        Provides API information for the component as an output.

        Returns:
            A dictionary containing API metadata for the component.
        """
        return self.api_info()

    def example_payload(self) -> Any:
        """
        Returns an example payload for testing the component.

        Returns:
            A processed file object for a sample image.
        """
        return handle_file(
            "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"
        )

    def example_value(self) -> Any:
        """
        Returns an example value for the component.

        Returns:
            A URL to a sample image.
        """
        return "https://raw.githubusercontent.com/gradio-app/gradio/main/test/test_files/bus.png"