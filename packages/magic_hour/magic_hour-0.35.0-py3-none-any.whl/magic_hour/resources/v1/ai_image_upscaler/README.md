
### AI Image Upscaler <a name="create"></a>

Upscale your image using AI. Each 2x upscale costs 50 credits, and 4x upscale costs 200 credits.

**API Endpoint**: `POST /v1/ai-image-upscaler`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `assets` | ✓ | Provide the assets for upscaling | `{"image_file_path": "api-assets/id/1234.png"}` |
| `scale_factor` | ✓ | How much to scale the image. Must be either 2 or 4.              Note: 4x upscale is only available on Creator, Pro, or Business tier. | `2.0` |
| `style` | ✓ |  | `{"enhancement": "Balanced"}` |
| `name` | ✗ | The name of image. This value is mainly used for your own identification of the image. | `"Image Upscaler image"` |

#### Synchronous Client

```python
from magic_hour import Client
from os import getenv

client = Client(token=getenv("API_TOKEN"))
res = client.v1.ai_image_upscaler.create(
    assets={"image_file_path": "api-assets/id/1234.png"},
    scale_factor=2.0,
    style={"enhancement": "Balanced"},
    name="Image Upscaler image",
)

```

#### Asynchronous Client

```python
from magic_hour import AsyncClient
from os import getenv

client = AsyncClient(token=getenv("API_TOKEN"))
res = await client.v1.ai_image_upscaler.create(
    assets={"image_file_path": "api-assets/id/1234.png"},
    scale_factor=2.0,
    style={"enhancement": "Balanced"},
    name="Image Upscaler image",
)

```

#### Response

##### Type
[V1AiImageUpscalerCreateResponse](/magic_hour/types/models/v1_ai_image_upscaler_create_response.py)

##### Example
`{"credits_charged": 50, "frame_cost": 50, "id": "cuid-example"}`
