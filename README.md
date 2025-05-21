# Metadata Reporter for ComfyUI
A custom ComfyUI node designed to extract and display detailed workflow information from generated or loaded images. This node provides an easy way to view the generation parameters associated with an image directly within the ComfyUI interface.

## 🌟 Features

- **Extract Complete Metadata**: Captures positive/negative prompts, seed, steps, sampler name, model used, LoRAs, and all other metadata embedded in images
- **Clean Presentation**: Displays formatted metadata text directly within the ComfyUI interface
- **Multiple Sources**: Works with both images generated in the current workflow AND loaded images from external sources
- **Save to File**: Option to export metadata as a clean, plain-text file
- **Smart Detection**: Attempts multiple methods to retrieve metadata for maximum compatibility

## 📋 Requirements

- ComfyUI
- Python 3.8 or higher
- PIL/Pillow library (typically included with ComfyUI)

## 💾 Installation

### Method 1: Manual Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/mixedpast/LoadImageMetadata.git
   ```

3. Restart ComfyUI to load the new node.

### Method 2: Using ComfyUI Manager

1. Open ComfyUI
2. Open the Manager tab
3. Search for "Final Metadata Reporter"
4. Click the Install button
5. Restart ComfyUI

## 🚀 Usage

### Basic Workflow

1. **For Generated Images**:
   - Create your image generation workflow
   - Add the "Final Metadata Reporter" node
   - Connect the output IMAGE from your final generation node to the "image" input
   - Run your workflow to see the metadata

2. **For Loaded Images**:
   - Add a "Load Image" node to your workflow
   - Add the "Final Metadata Reporter" node
   - Connect the "image" output from Load Image to the "image" input of the reporter
   - Run your workflow to see the metadata

### Saving Metadata to File

To save the metadata to a text file:

1. Set the "save_to_file" parameter to True
2. Optionally, customize the "output_filename" parameter
3. Run your workflow
4. The metadata will be saved to the ComfyUI output directory

## 📊 Example Output

```
=== Image Metadata ===

Prompt: portrait of a woman with blue eyes, detailed face, freckles, natural lighting, detailed skin
Negative Prompt: blurry, bad anatomy, disfigured, poorly drawn face, extra limb, ugly, poorly drawn hands
Seed: 1234567890
Steps: 30
Sampler Name: euler_a
Model: dreamshaper_8.safetensors
Cfg Scale: 7.0
Width: 512
Height: 768

=== LoRAs ===
lora_1: more_details:0.6
lora_2: realistic_lighting:0.4

=== Other Parameters ===
Clip Skip: 2
Denoising Strength: 0.7
Upscaler: ESRGAN_4x
Version: ComfyUI 1.5.2
```

## 🔧 How It Works

The Final Metadata Reporter node extracts metadata through several methods:

1. First, it attempts to access the metadata directly from the image tensor object
2. If unsuccessful, it looks for a filename attribute and reads metadata from the image file
3. It handles both string and dictionary metadata formats
4. The extracted metadata is organized into sections (important parameters, LoRAs, and other parameters) and formatted for easy reading

## ⚠️ Compatibility Notes

- Works with most standard ComfyUI workflows and standard nodes
- Compatible with both PNG and JPEG images (though PNG is recommended for metadata preservation)
- Some complex workflows with custom nodes may have limited metadata extraction capabilities
- For best results with loaded images, use images that were originally generated with Stable Diffusion tools that embed metadata (ComfyUI, A1111, etc.)

## 🔍 Troubleshooting

### No Metadata Found

If you see "No metadata found in image":

- Ensure the image was generated with a tool that embeds metadata (ComfyUI, A1111, etc.)
- Check that the image hasn't been modified or re-saved with a tool that strips metadata
- Try using a "Load Image With Metadata" node instead of the regular "Load Image" node

### Incomplete Metadata

If you're getting partial metadata:

- Some complex workflows may not properly record all parameters
- Try using a simpler workflow to generate the image
- Consider using additional metadata saving extensions like "ComfyUI-SaveImageWithMetaData"

## 🤝 Contributing

Contributions are welcome! If you have improvements or bug fixes:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Thanks to the ComfyUI team for creating an amazing platform
- Inspired by the need for better metadata visualization in AI image generation
- Built with ❤️ for the AI art community

---

If you find this node useful, please consider starring the repository and sharing it with others!
