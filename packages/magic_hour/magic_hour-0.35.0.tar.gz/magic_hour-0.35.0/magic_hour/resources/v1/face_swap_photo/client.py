import typing

from magic_hour.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
    type_utils,
)
from magic_hour.types import models, params


class FaceSwapPhotoClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(
        self,
        *,
        assets: params.V1FaceSwapPhotoCreateBodyAssets,
        name: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.V1FaceSwapPhotoCreateResponse:
        """
        Face Swap Photo

        Create a face swap photo. Each photo costs 5 credits. The height/width of the output image depends on your subscription. Please refer to our [pricing](https://magichour.ai/pricing) page for more details

        POST /v1/face-swap-photo

        Args:
            name: The name of image. This value is mainly used for your own identification of the image.
            assets: Provide the assets for face swap photo
            request_options: Additional options to customize the HTTP request

        Returns:
            Success

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.v1.face_swap_photo.create(
            assets={
                "face_mappings": [
                    {
                        "new_face": "api-assets/id/1234.png",
                        "original_face": "api-assets/id/0-0.png",
                    }
                ],
                "face_swap_mode": "all-faces",
                "source_file_path": "api-assets/id/1234.png",
                "target_file_path": "api-assets/id/1234.png",
            },
            name="Face Swap image",
        )
        ```
        """
        _json = to_encodable(
            item={"name": name, "assets": assets},
            dump_with=params._SerializerV1FaceSwapPhotoCreateBody,
        )
        return self._base_client.request(
            method="POST",
            path="/v1/face-swap-photo",
            auth_names=["bearerAuth"],
            json=_json,
            cast_to=models.V1FaceSwapPhotoCreateResponse,
            request_options=request_options or default_request_options(),
        )


class AsyncFaceSwapPhotoClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def create(
        self,
        *,
        assets: params.V1FaceSwapPhotoCreateBodyAssets,
        name: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.V1FaceSwapPhotoCreateResponse:
        """
        Face Swap Photo

        Create a face swap photo. Each photo costs 5 credits. The height/width of the output image depends on your subscription. Please refer to our [pricing](https://magichour.ai/pricing) page for more details

        POST /v1/face-swap-photo

        Args:
            name: The name of image. This value is mainly used for your own identification of the image.
            assets: Provide the assets for face swap photo
            request_options: Additional options to customize the HTTP request

        Returns:
            Success

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.v1.face_swap_photo.create(
            assets={
                "face_mappings": [
                    {
                        "new_face": "api-assets/id/1234.png",
                        "original_face": "api-assets/id/0-0.png",
                    }
                ],
                "face_swap_mode": "all-faces",
                "source_file_path": "api-assets/id/1234.png",
                "target_file_path": "api-assets/id/1234.png",
            },
            name="Face Swap image",
        )
        ```
        """
        _json = to_encodable(
            item={"name": name, "assets": assets},
            dump_with=params._SerializerV1FaceSwapPhotoCreateBody,
        )
        return await self._base_client.request(
            method="POST",
            path="/v1/face-swap-photo",
            auth_names=["bearerAuth"],
            json=_json,
            cast_to=models.V1FaceSwapPhotoCreateResponse,
            request_options=request_options or default_request_options(),
        )
