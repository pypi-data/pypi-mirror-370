# RichdaleAI MCP Server

A Model Context Protocol (MCP) server for AI image generation using RunPod's Stable Diffusion API.

## Features

- Generate images using Stable Diffusion 3.5 Large model
- MCP-compatible server architecture
- Fast image generation with configurable parameters
- Support for various aspect ratios and style presets

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd MCP-API

# Install build dependencies
pip install build

# Build the package
python -m build

# Install locally
pip install dist/richdaleai_mcp-0.1.0-py3-none-any.whl
```

### From TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ richdaleai-mcp
```

## Usage
### From Terminal
Run the MCP server:

```bash
richdaleai-mcp
```

Set your RunPod API key in a `.env` file:

```env
RUNPOD_API_KEY=your_api_key_here
RUNPOD_ENDPOINT_ID=your_endpoint_id_here
```

### RUN From MCP Configuration

First install package.

```bash
pip install richdaleai-mcp
```


Configure the server in your `mcp.json` file:

```json
{
  "mcpServers": {
    "richdaleai_mcp": {
      "command": "python",
      "args": ["-m", "richdaleai_mcp"],
      "env": {
        "RUNPOD_API_KEY": "your_runpod_api_key_here",
        "RUNPOD_ENDPOINT": "https://api.runpod.ai/v2/your_endpoint_id/runsync",
        "IMAGE_STORAGE_DIRECTORY": "/path/to/image/storage"
      }
    }
  }
}
```

**Environment Variables:**
- `RUNPOD_API_KEY`: Your RunPod API key
- `RUNPOD_ENDPOINT`: RunPod endpoint URL for image generation
- `IMAGE_STORAGE_DIRECTORY`: Directory to store generated images

## Development

### Dependencies

- Python 3.11+
- fastmcp
- requests
- python-dotenv

### Building

```bash
python -m build
```

### Testing

```bash
# Install in development mode
pip install -e .
```

## License

This project is licensed under the GNU Affero General Public License v3 - see the [LICENSE](LICENSE) file for details.

## API Response Example

```json
{"delayTime":1036,"executionTime":8805,"id":"sync-2f895f28-d6be-4264-a978-657041fe1754-e1","output":{"images":["data:image/png;base64,iVBORw0KJwFmxrbRK5CYII="],"images_info":{"count":1,"seed":15121496791610440000,"shape":"torch.Size([1, 3, 1024, 1024])"},"input_parameters":{"batch_count":1,"batch_size":1,"build_dynamic_shape":false,"build_static_batch":true,"denoising_steps":30,"framework_model_dir":null,"guidance_scale":3.5,"height":1024,"low_vram":false,"max_sequence_length":256,"negative_prompt":"","num_warmup_runs":0,"prompt":"A simple blue circle on a white background","seed":null,"use_cuda_graph":false,"version":"3.5-large","width":1024},"job_id":"sync-2f895f28-d6be-4264-a978-657041fe1754-e1","message":"Images generated successfully in 7631.47ms","status":"success"},"status":"COMPLETED","workerId":"gz8euubmvp42dr"}
```