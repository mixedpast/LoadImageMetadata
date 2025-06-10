# Python code for final_metadata_reporter.py (Version 7.1: Robust Error Handling)
# Place this file in ComfyUI/custom_nodes/final_metadata_reporter/

import json
import traceback # Import traceback for better error printing

class FinalMetadataReporter:
    @classmethod
    def INPUT_TYPES(cls):
        """
        Defines the input types for the node. Expects a metadata dictionary.
        """
        return {
            "required": {
                "metadata": ("DICT",),
            },
            "optional": {
                "image": ("IMAGE",),  # Optional image input for future use
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("metadata_text",)
    FUNCTION = "report_metadata"
    CATEGORY = "utils/reporting"

    def report_metadata(self, metadata, image=None):
        """
        Receives a metadata dictionary, parses workflow data using simple direct access.
        """
        print("[FinalMetadataReporter V7.1] Node execution started.")
        print(f"[FinalMetadataReporter V7.1] Received metadata type: {type(metadata)}")
        
        # Print first few keys/values of metadata for debugging
        if isinstance(metadata, dict):
            print(f"[FinalMetadataReporter V7.1] Metadata keys: {list(metadata.keys())[:5]}")
            
            # Try to detect if this is a raw workflow metadata (not image metadata)
            if 'prompt' in metadata or 'workflow' in metadata:
                print("[FinalMetadataReporter V7.1] Detected workflow metadata structure")
            else:
                print("[FinalMetadataReporter V7.1] This appears to be direct image metadata, not workflow data")
        else:
            print(f"[FinalMetadataReporter V7.1] Metadata is not a dictionary: {metadata}")

        # Handle empty or invalid metadata more gracefully
        if not metadata or not isinstance(metadata, dict):
            print("[FinalMetadataReporter V7.1] Creating fallback metadata report for empty/invalid input")
            return ("Metadata report: No valid metadata was provided.\n\nIf this is unexpected, check that:\n1. The image has embedded metadata\n2. The LoadImageWithMetadata node is connected correctly\n3. The workflow has completed at least one execution",)

        # Get the basic prompt nodes structure
        nodes_dict = self._get_nodes_dict(metadata)
        if not nodes_dict:
            print("[FinalMetadataReporter V7.1] Could not find node structure in metadata")
            
            # If this is an image with direct metadata (not workflow), report it differently
            if isinstance(metadata, dict) and len(metadata) > 0:
                return (self._format_direct_image_metadata(metadata),)
                
            return ("Could not find workflow node structure in metadata.\n\nAvailable metadata keys: " + 
                    (", ".join(list(metadata.keys())[:10])) if isinstance(metadata, dict) else "None",)
            
        # Parse the data and format the output
        formatted_string = self._parse_and_format(nodes_dict)
        
        print("[FinalMetadataReporter V7.1] Output string generated successfully")
        return (formatted_string,)
    
    def _format_direct_image_metadata(self, metadata):
        """Format direct image metadata (not workflow metadata)"""
        output_lines = ["--- Image Metadata ---"]
        
        # Add each key/value pair to the output
        for key, value in metadata.items():
            # Format the key name to be more readable
            display_key = key.replace('_', ' ').title()
            
            # Format the value based on its type
            if isinstance(value, dict):
                formatted_value = json.dumps(value, indent=2)
                output_lines.append(f"{display_key}:\n{formatted_value}")
            elif isinstance(value, (list, tuple)):
                if len(value) > 5:
                    formatted_value = str(value[:5])[:-1] + ", ... ]"
                else:
                    formatted_value = str(value)
                output_lines.append(f"{display_key}: {formatted_value}")
            else:
                output_lines.append(f"{display_key}: {value}")
                
        return "\n".join(output_lines)
        
    def _get_nodes_dict(self, metadata_dict):
        """Simple direct access to nodes structure."""
        try:
            # Try to directly access prompt as JSON string or dict
            if 'prompt' in metadata_dict:
                if isinstance(metadata_dict['prompt'], dict):
                    return metadata_dict['prompt']
                elif isinstance(metadata_dict['prompt'], str):
                    try:
                        return json.loads(metadata_dict['prompt'])
                    except json.JSONDecodeError as e:
                        print(f"[FinalMetadataReporter V7.1] Failed to parse prompt JSON: {e}")
                        
            # Try workflow key
            if 'workflow' in metadata_dict:
                if isinstance(metadata_dict['workflow'], dict):
                    if 'nodes' in metadata_dict['workflow']:
                        return metadata_dict['workflow']['nodes']
                    return metadata_dict['workflow']
                elif isinstance(metadata_dict['workflow'], str):
                    try:
                        workflow_data = json.loads(metadata_dict['workflow'])
                        if isinstance(workflow_data, dict):
                            if 'nodes' in workflow_data:
                                return workflow_data['nodes']
                            return workflow_data
                    except json.JSONDecodeError as e:
                        print(f"[FinalMetadataReporter V7.1] Failed to parse workflow JSON: {e}")
            
            # Direct nodes field
            if 'nodes' in metadata_dict and isinstance(metadata_dict['nodes'], (dict, list)):
                return metadata_dict['nodes']
                
        except Exception as e:
            print(f"[FinalMetadataReporter V7.1] Error in _get_nodes_dict: {e}")
            traceback.print_exc()
            
        return None
        
    def _parse_and_format(self, nodes_dict):
        """Parse the node data and format output string."""
        output_lines = ["--- Workflow Metadata Report ---"]
        
        try:
            # 1. Find model checkpoint
            model_name = self._extract_model_name(nodes_dict)
            output_lines.append(f"Model: {model_name}")
            
            # 2. Find LoRA information
            loras = self._extract_loras(nodes_dict)
            if loras:
                output_lines.append("LoRAs:")
                for lora in loras:
                    output_lines.append(f"  - {lora['name']} (Model: {lora['strength']}, CLIP: {lora['strength']})")
                    
            # 3. Find resolution
            resolution = self._extract_resolution(nodes_dict)
            if resolution:
                output_lines.append(f"Resolution: {resolution}")
                        
            # 4. Find positive prompt
            pos_prompt, t5xxl_prompt = self._extract_prompts(nodes_dict)
            output_lines.append(f"\nPositive Prompt:\n  {pos_prompt}")
            
            if t5xxl_prompt:
                output_lines.append(f"\nT5XXL Prompt:\n  {t5xxl_prompt}")
                
            # 5. Negative prompt
            output_lines.append("\nNegative Prompt:\n  (Empty)")
            
            # 6. Find Sampler info
            sampler_info = self._extract_sampler_info(nodes_dict)
            if sampler_info:
                output_lines.append("\n--- Sampler Details ---")
                for key, value in sampler_info.items():
                    # Format the key name to be more readable
                    display_key = key.replace('_', ' ').title()
                    output_lines.append(f"{display_key}: {value}")
            
            # 7. Find additional components like ControlNet and IPAdapter
            additional_components = self._extract_additional_components(nodes_dict)
            for component_name, component_info in additional_components.items():
                if component_info:
                    output_lines.append(f"\n--- {component_name} ---")
                    for key, value in component_info.items():
                        # Format the key name to be more readable
                        display_key = key.replace('_', ' ').title()
                        output_lines.append(f"{display_key}: {value}")
                    
        except Exception as e:
            print(f"[FinalMetadataReporter V7.1] Error during parsing: {e}")
            traceback.print_exc()
            output_lines.append(f"\nError during metadata parsing: {e}")
            
        return "\n".join(output_lines)

    def _extract_model_name(self, nodes_dict):
        """Extract model checkpoint name."""
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "CheckpointLoaderSimple":
                if 'inputs' in node and 'ckpt_name' in node['inputs']:
                    return node['inputs']['ckpt_name']
        return "N/A"
        
    def _extract_loras(self, nodes_dict):
        """Extract LoRA information."""
        loras = []
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "Power Lora Loader (rgthree)":
                inputs = node.get('inputs', {})
                for key, value in inputs.items():
                    if key.startswith('lora_') and isinstance(value, dict) and value.get('on', False):
                        loras.append({
                            'name': value.get('lora', 'N/A'),
                            'strength': value.get('strength', 'N/A')
                        })
                break  # Found the LoRA node
        return loras
        
    def _extract_resolution(self, nodes_dict):
        """Extract resolution information."""
        # Try CascadeResolutions first
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "CascadeResolutions":
                if 'inputs' in node and 'size_selected' in node['inputs']:
                    return node['inputs']['size_selected']
                    
        # Try ImageScale node as alternative
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "ImageScale":
                inputs = node.get('inputs', {})
                width = inputs.get('width')
                height = inputs.get('height')
                if width and height:
                    return f"{width}x{height}"
                    
        return None
        
    def _extract_prompts(self, nodes_dict):
        """Extract positive and t5xxl prompts."""
        pos_prompt = "N/A"
        t5xxl_prompt = None
        
        # Find all CLIPTextEncodeFlux nodes
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "CLIPTextEncodeFlux":
                inputs = node.get('inputs', {})
                # Skip empty prompts (likely negative)
                if inputs.get('clip_l') == "":
                    continue
                    
                if 'clip_l' in inputs:
                    pos_prompt = inputs['clip_l']
                    if 't5xxl' in inputs:
                        t5xxl_prompt = inputs['t5xxl']
                    break  # Found non-empty prompt
                    
        return pos_prompt, t5xxl_prompt
        
    def _extract_sampler_info(self, nodes_dict):
        """Extract sampler parameters from KSampler or XlabsSampler."""
        sampler_info = {}
        
        # Check for KSampler
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "KSampler":
                inputs = node.get('inputs', {})
                
                # Get seed from Seed Everywhere node if needed
                seed_value = "N/A"
                seed_link = inputs.get('seed')
                if isinstance(seed_link, list) and len(seed_link) >= 1:
                    seed_node_id = seed_link[0]
                    seed_node = nodes_dict.get(seed_node_id)
                    if seed_node and seed_node.get('class_type') == "Seed Everywhere":
                        seed_value = seed_node.get('inputs', {}).get('seed', 'N/A')
                else:
                    # Direct seed value
                    seed_value = inputs.get('seed', 'N/A')
                
                sampler_info['seed'] = seed_value
                sampler_info['steps'] = inputs.get('steps', 'N/A')
                sampler_info['cfg'] = inputs.get('cfg', 'N/A')
                sampler_info['sampler_name'] = inputs.get('sampler_name', 'N/A')
                sampler_info['scheduler'] = inputs.get('scheduler', 'N/A')
                sampler_info['denoise'] = inputs.get('denoise', 'N/A')
                return sampler_info  # Found KSampler
        
        # Check for XlabsSampler
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "XlabsSampler":
                inputs = node.get('inputs', {})
                
                # XlabsSampler has slightly different parameters
                sampler_info['seed'] = inputs.get('noise_seed', 'N/A')
                sampler_info['steps'] = inputs.get('steps', 'N/A')
                sampler_info['true_gs'] = inputs.get('true_gs', 'N/A')  # Similar to cfg
                sampler_info['timestep_to_start_cfg'] = inputs.get('timestep_to_start_cfg', 'N/A')
                sampler_info['image_to_image_strength'] = inputs.get('image_to_image_strength', 'N/A')
                sampler_info['denoise'] = inputs.get('denoise_strength', 'N/A')
                return sampler_info  # Found XlabsSampler
                
        return None  # No sampler found
        
    def _extract_additional_components(self, nodes_dict):
        """Extract information about additional components like ControlNet and IPAdapter."""
        components = {}
        
        # Extract ControlNet information
        controlnet_info = {}
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "LoadFluxControlNet":
                inputs = node.get('inputs', {})
                controlnet_info['model_name'] = inputs.get('model_name', 'N/A')
                controlnet_info['controlnet_path'] = inputs.get('controlnet_path', 'N/A')
                
            elif isinstance(node, dict) and node.get('class_type') == "ApplyFluxControlNet":
                inputs = node.get('inputs', {})
                controlnet_info['strength'] = inputs.get('strength', 'N/A')
                
            elif isinstance(node, dict) and node.get('class_type') == "CannyEdgePreprocessor":
                inputs = node.get('inputs', {})
                controlnet_info['low_threshold'] = inputs.get('low_threshold', 'N/A')
                controlnet_info['high_threshold'] = inputs.get('high_threshold', 'N/A')
                controlnet_info['resolution'] = inputs.get('resolution', 'N/A')
                
        if controlnet_info:
            components['ControlNet Details'] = controlnet_info
            
        # Extract IPAdapter information
        ipadapter_info = {}
        for node_id, node in nodes_dict.items():
            if isinstance(node, dict) and node.get('class_type') == "LoadFluxIPAdapter":
                inputs = node.get('inputs', {})
                ipadapter_info['adapter'] = inputs.get('ipadatper', 'N/A')
                ipadapter_info['clip_vision'] = inputs.get('clip_vision', 'N/A')
                ipadapter_info['provider'] = inputs.get('provider', 'N/A')
                
            elif isinstance(node, dict) and node.get('class_type') == "ApplyFluxIPAdapter":
                inputs = node.get('inputs', {})
                ipadapter_info['ip_scale'] = inputs.get('ip_scale', 'N/A')
                
        if ipadapter_info:
            components['IPAdapter Details'] = ipadapter_info
            
        # Future: Add other component extractors here
            
        return components

# --- ComfyUI Registration ---
NODE_CLASS_MAPPINGS = {
    "FinalMetadataReporter": FinalMetadataReporter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FinalMetadataReporter": "Final Metadata Reporter 📝"
}
