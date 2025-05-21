# Python code for load_image_with_metadata.py (V6.0: Compatible with existing workflow)
# Place this file in ComfyUI/custom_nodes/LoadImageWithMetadata/

import os
import numpy as np
import torch
import hashlib
import json
from PIL import Image, ImageOps, ImageSequence

import folder_paths
import node_helpers

class LoadImageWithMetadata:
    """
    Custom node that loads the most recently saved image and extracts its metadata.
    """
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        
        return {
            "required": {
                "source_type": (["direct_input", "file"], {"default": "direct_input"}),
            },
            "optional": {
                "image_file": (sorted(files), {"image_upload": True}),
                "image_input": ("IMAGE",),
                "metadata_input": ("DICT",),
            }
        }

    CATEGORY = "image/loading"
    RETURN_TYPES = ("IMAGE", "DICT")
    RETURN_NAMES = ("image", "metadata")
    FUNCTION = "load_image_with_metadata"

    def load_image_with_metadata(self, source_type, image_file=None, image_input=None, metadata_input=None):
        """
        Load image with metadata from either most recent file or specified file.
        """
        print(f"[LoadImageWithMetadata] Processing with source_type: {source_type}")
        
        if source_type == "direct_input":
            # Ignore the image_input parameter and find the most recent file instead
            # This allows us to maintain compatibility with the workflow
            output_path = folder_paths.get_output_directory()
            print(f"[LoadImageWithMetadata] Looking for most recent image in: {output_path}")
            
            # Find all PNG files in output directory and subdirectories
            png_files = []
            for root, dirs, files in os.walk(output_path):
                for file in files:
                    if file.lower().endswith('.png'):
                        full_path = os.path.join(root, file)
                        png_files.append((full_path, os.path.getmtime(full_path)))
            
            if not png_files:
                print("[LoadImageWithMetadata] No PNG files found in output directory")
                return self._create_error_output("No PNG files found in output directory")
            
            # Sort by modification time (newest first)
            png_files.sort(key=lambda x: x[1], reverse=True)
            most_recent_file = png_files[0][0]
            
            print(f"[LoadImageWithMetadata] Most recent PNG: {most_recent_file}")
            return self._process_image_file(most_recent_file)
        
        else:  # source_type == "file"
            if image_file is None:
                print("[LoadImageWithMetadata] No image file specified")
                return self._create_error_output("No image file specified")
            
            image_path = folder_paths.get_annotated_filepath(image_file)
            print(f"[LoadImageWithMetadata] Loading specified file: {image_path}")
            return self._process_image_file(image_path)

    def _process_image_file(self, image_path):
        """Process an image file and extract metadata."""
        try:
            # Open the image using PIL
            img = Image.open(image_path)
            
            # Get the metadata dictionary from the image
            raw_metadata = img.info or {}
            
            print(f"[LoadImageWithMetadata] Raw metadata contains {len(raw_metadata)} keys")
            if raw_metadata:
                print(f"[LoadImageWithMetadata] Raw metadata keys: {list(raw_metadata.keys())}")
            
            # Parse the raw metadata to extract workflow data
            metadata = self._parse_png_metadata(raw_metadata)
            
            # Process the image
            output_images = []
            w, h = None, None
            excluded_formats = ['MPO']

            for i in ImageSequence.Iterator(img):
                i = ImageOps.exif_transpose(i)
                if i.mode == 'I':
                    i = i.point(lambda i: i * (1 / 255))
                image_rgb = i.convert("RGB")

                if len(output_images) == 0:
                    w = image_rgb.size[0]
                    h = image_rgb.size[1]

                if image_rgb.size[0] != w or image_rgb.size[1] != h:
                    continue

                image_np = np.array(image_rgb).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np)[None,]
                output_images.append(image_tensor)

            if len(output_images) > 1 and img.format not in excluded_formats:
                output_image = torch.cat(output_images, dim=0)
            elif output_images:
                output_image = output_images[0]
            else:
                print(f"[LoadImageWithMetadata] Error: No valid image frames loaded from {image_path}")
                return self._create_error_output("Failed to load image frames")

            # If no workflow metadata was found, try to find a parallel JSON file
            if not metadata or metadata.get("info") == "No workflow metadata found":
                metadata_path = os.path.splitext(image_path)[0] + ".json"
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        print(f"[LoadImageWithMetadata] Loaded metadata from parallel JSON file")
                    except Exception as e:
                        print(f"[LoadImageWithMetadata] Error loading parallel JSON: {e}")

            # Add the image path to metadata for reference
            if isinstance(metadata, dict):
                metadata["image_path"] = image_path
                metadata["image_filename"] = os.path.basename(image_path)

            return (output_image, metadata)
            
        except Exception as e:
            print(f"[LoadImageWithMetadata] Error processing image: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_output(f"Error processing image: {str(e)}")

    def _parse_png_metadata(self, raw_metadata):
        """
        Parse PNG metadata to extract workflow data.
        ComfyUI stores workflow data in specific fields like 'prompt' or 'workflow'.
        """
        # Try to find 'prompt' or 'workflow' in the PNG metadata
        metadata = {}
        
        for key in raw_metadata:
            if key in ['prompt', 'workflow']:
                try:
                    # If it's a string that looks like JSON, parse it
                    if isinstance(raw_metadata[key], str):
                        print(f"[LoadImageWithMetadata] Found '{key}' as string in PNG metadata")
                        metadata[key] = json.loads(raw_metadata[key])
                    else:
                        print(f"[LoadImageWithMetadata] Found '{key}' as direct object in PNG metadata")
                        metadata[key] = raw_metadata[key]
                except Exception as e:
                    print(f"[LoadImageWithMetadata] Error parsing {key}: {e}")
                    # If it's not valid JSON, store as is
                    metadata[key] = raw_metadata[key]
            elif key == 'parameters':
                # A1111 WebUI style metadata
                print("[LoadImageWithMetadata] Found A1111-style 'parameters' in PNG metadata")
                metadata['parameters'] = raw_metadata[key]
                
        if not metadata:
            # No recognized workflow data found
            print("[LoadImageWithMetadata] No workflow metadata found in image")
            return {"info": "No workflow metadata found"}
            
        return metadata

    def _create_error_output(self, error_message):
        """Create a placeholder output with error message."""
        placeholder = torch.zeros((1, 3, 64, 64))
        return (placeholder, {"error": error_message})

    @classmethod
    def IS_CHANGED(s, source_type, image_file=None, image_input=None, metadata_input=None):
        """
        Determine if the node should be re-executed.
        Make sure to accept all parameters, even if we don't use them.
        """
        if source_type == "direct_input":
            # For 'direct_input' (most_recent) mode, always re-execute
            return float("nan")
        elif source_type == "file" and image_file is not None:
            image_path = folder_paths.get_annotated_filepath(image_file)
            m = hashlib.sha256()
            try:
                with open(image_path, 'rb') as f:
                    m.update(f.read())
                return m.digest().hex()
            except FileNotFoundError:
                return float('nan')
        return float("nan")

# --- Node Registration ---
NODE_CLASS_MAPPINGS = {
    "LoadImageWithMetadata": LoadImageWithMetadata
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImageWithMetadata": "Load Image w/ Metadata"
}
