import typing
import typing_extensions

from magic_hour.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
    type_utils,
)
from magic_hour.types import models, params


class TextToVideoClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(
        self,
        *,
        end_seconds: float,
        orientation: typing_extensions.Literal["landscape", "portrait", "square"],
        style: params.V1TextToVideoCreateBodyStyle,
        name: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        resolution: typing.Union[
            typing.Optional[typing_extensions.Literal["1080p", "480p", "720p"]],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.V1TextToVideoCreateResponse:
        """
        Text-to-Video

        Create a Text To Video video. The estimated frame cost is calculated using 30 FPS. This amount is deducted from your account balance when a video is queued. Once the video is complete, the cost will be updated based on the actual number of frames rendered.

        Get more information about this mode at our [product page](https://magichour.ai/products/text-to-video).


        POST /v1/text-to-video

        Args:
            name: The name of video. This value is mainly used for your own identification of the video.
            resolution: Controls the output video resolution. Defaults to `720p` if not specified.

        480p and 720p are available on Creator, Pro, or Business tiers. However, 1080p require Pro or Business tier.

        **Options:**
        - `480p` - Supports only 5 or 10 second videos. Output: 24fps. Cost: 120 credits per 5 seconds.
        - `720p` - Supports videos between 5-60 seconds. Output: 30fps. Cost: 300 credits per 5 seconds.
        - `1080p` - Supports videos between 5-60 seconds. Output: 30fps. Cost: 600 credits per 5 seconds.
            end_seconds: The total duration of the output video in seconds.

        The value must be greater than or equal to 5 seconds and less than or equal to 60 seconds.

        Note: For 480p resolution, the value must be either 5 or 10.
            orientation: Determines the orientation of the output video
            style: V1TextToVideoCreateBodyStyle
            request_options: Additional options to customize the HTTP request

        Returns:
            Success

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.v1.text_to_video.create(
            end_seconds=5.0,
            orientation="landscape",
            style={"prompt": "a dog running"},
            name="Text To Video video",
            resolution="720p",
        )
        ```
        """
        _json = to_encodable(
            item={
                "name": name,
                "resolution": resolution,
                "end_seconds": end_seconds,
                "orientation": orientation,
                "style": style,
            },
            dump_with=params._SerializerV1TextToVideoCreateBody,
        )
        return self._base_client.request(
            method="POST",
            path="/v1/text-to-video",
            auth_names=["bearerAuth"],
            json=_json,
            cast_to=models.V1TextToVideoCreateResponse,
            request_options=request_options or default_request_options(),
        )


class AsyncTextToVideoClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def create(
        self,
        *,
        end_seconds: float,
        orientation: typing_extensions.Literal["landscape", "portrait", "square"],
        style: params.V1TextToVideoCreateBodyStyle,
        name: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        resolution: typing.Union[
            typing.Optional[typing_extensions.Literal["1080p", "480p", "720p"]],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.V1TextToVideoCreateResponse:
        """
        Text-to-Video

        Create a Text To Video video. The estimated frame cost is calculated using 30 FPS. This amount is deducted from your account balance when a video is queued. Once the video is complete, the cost will be updated based on the actual number of frames rendered.

        Get more information about this mode at our [product page](https://magichour.ai/products/text-to-video).


        POST /v1/text-to-video

        Args:
            name: The name of video. This value is mainly used for your own identification of the video.
            resolution: Controls the output video resolution. Defaults to `720p` if not specified.

        480p and 720p are available on Creator, Pro, or Business tiers. However, 1080p require Pro or Business tier.

        **Options:**
        - `480p` - Supports only 5 or 10 second videos. Output: 24fps. Cost: 120 credits per 5 seconds.
        - `720p` - Supports videos between 5-60 seconds. Output: 30fps. Cost: 300 credits per 5 seconds.
        - `1080p` - Supports videos between 5-60 seconds. Output: 30fps. Cost: 600 credits per 5 seconds.
            end_seconds: The total duration of the output video in seconds.

        The value must be greater than or equal to 5 seconds and less than or equal to 60 seconds.

        Note: For 480p resolution, the value must be either 5 or 10.
            orientation: Determines the orientation of the output video
            style: V1TextToVideoCreateBodyStyle
            request_options: Additional options to customize the HTTP request

        Returns:
            Success

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.v1.text_to_video.create(
            end_seconds=5.0,
            orientation="landscape",
            style={"prompt": "a dog running"},
            name="Text To Video video",
            resolution="720p",
        )
        ```
        """
        _json = to_encodable(
            item={
                "name": name,
                "resolution": resolution,
                "end_seconds": end_seconds,
                "orientation": orientation,
                "style": style,
            },
            dump_with=params._SerializerV1TextToVideoCreateBody,
        )
        return await self._base_client.request(
            method="POST",
            path="/v1/text-to-video",
            auth_names=["bearerAuth"],
            json=_json,
            cast_to=models.V1TextToVideoCreateResponse,
            request_options=request_options or default_request_options(),
        )
