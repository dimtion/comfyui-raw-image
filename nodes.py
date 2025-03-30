import folder_paths
import hashlib
import numpy as np
import os
import rawpy
import torch

from PIL import Image

HIGHLIGHT_MODES = {
    "clip": rawpy.HighlightMode.Clip,
    "ignore": rawpy.HighlightMode.Ignore,
    "blend": rawpy.HighlightMode.Blend,
    "reconstruct": rawpy.HighlightMode.ReconstructDefault,
}


class LoadRawImage:
    """Load a RAW image."""

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "load_img"
    CATEGORY = "image"
    DESCRIPTION = "Load a RAW image into ComfyUI."

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]

        return {
            "required": {
                "image": (
                    sorted(files),
                    {"image_upload": True, "tooltip": "Image to load."},
                ),
            },
            "optional": {
                "use_auto_bright": (
                    "BOOLEAN",
                    {"default": True, "tooltip": "automatic increase of brightness"},
                ),
                "bright_adjustment": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.1, "max": 3.0, "step": 0.1},
                ),
                "highlight_mode": (list(HIGHLIGHT_MODES.keys()), {"default": "clip"}),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True

    @classmethod
    def IS_CHANGED(cls, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    def load_img(
        self, image, use_auto_bright=True, bright_adjustment=1.0, highlight_mode="clip"
    ):
        """Load a raw image."""
        image_path = folder_paths.get_annotated_filepath(image)

        try:
            with rawpy.imread(image_path) as raw:
                rgb = raw.postprocess(
                    bright=bright_adjustment,
                    highlight_mode=HIGHLIGHT_MODES[highlight_mode],
                    no_auto_bright=not use_auto_bright,
                    output_bps=8,
                )

            img = Image.fromarray(rgb)

            if img.mode != "RGB":
                img = img.convert("RGB")

            # Convert to numpy array normalized to 0-1 range as expected by ComfyUI
            img_array = np.array(img).astype(np.float32) / 255.0
            img_array = torch.from_numpy(img_array).unsqueeze(0)

            return (img_array,)

        except Exception as e:
            raise RuntimeError(f"Failed to load RAW image: {str(e)}")


NODE_CLASS_MAPPINGS = {"Load Raw Image": LoadRawImage}
