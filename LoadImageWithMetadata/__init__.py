# __init__.py inside custom_nodes/LoadImageWithMetadata/

# Import the mappings from our main node file (load_image_with_metadata.py)
from .load_image_with_metadata import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# Make the mappings available for ComfyUI discovery
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("[LoadImageWithMetadata] Custom node package loaded.") # Optional: confirmation message
