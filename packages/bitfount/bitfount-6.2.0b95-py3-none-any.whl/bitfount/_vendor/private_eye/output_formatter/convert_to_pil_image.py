from io import BytesIO
from typing import Dict, List

import numpy as np
from PIL import Image
from ...private_eye.data import (
    BaseImageDataBytes,
    ImageProcessingOptions,
    ImageSourceDataType,
    ImageTransform,
    PhotoImageData,
)
from pydicom.dataset import Dataset, FileMetaDataset
from tifffile import imread


def apply_transforms(image_array: np.ndarray, transforms: List[ImageTransform]) -> np.ndarray:
    for transform in transforms:
        image_array = transform(image_array)
    return image_array


def decompress_image(image: BaseImageDataBytes) -> np.ndarray:
    output_bytes = image.image
    if not output_bytes:
        # We should never be calling this function if we do not have the image_bytes.
        raise ValueError("Image output called on image with not image data")
    if image.image_byte_format in (
        ImageSourceDataType.JPEG2000,
        ImageSourceDataType.IMAGENET2000,
        ImageSourceDataType.JPEG,
    ):
        # Need to decompress any encoding. PIl is the best way to handle this.
        image_pil = Image.open(BytesIO(output_bytes))
        image_array = np.asarray(image_pil)
    elif image.image_byte_format == ImageSourceDataType.UINT16:
        image_array = np.frombuffer(output_bytes, dtype=np.uint16)
    elif image.image_byte_format == ImageSourceDataType.TIFF:
        # Use the tifffile library instead of Pillow as it has better support
        # for TIFF compression formats.
        # In particular, it supports JPEG Lossless (Note: not the same as as JPEG-LS!),
        # which is old, rare and poorly supported.
        # The first series is a black 8x8 square for colour images, so we ignore it.
        image_array = imread(BytesIO(output_bytes), series=-1)
    elif image.image_byte_format == ImageSourceDataType.DICOM:
        # It is best to let pydicom handle the decompression here. Pydicom requires a dataset so build one.
        if not image.extras:
            # This should never occur, we will always set extras when the type is DICOM
            raise ValueError("ImageByteType.Dicom must have extras set")
        if not isinstance(image, PhotoImageData):
            # As of yet all zeiss files return PhotoImageData should this not be the case we will need
            # to update this code.
            raise NotImplementedError("Only support DICOM -> PhotoImageData")
        dicom_pixel_data = Dataset()
        dicom_pixel_data.file_meta = FileMetaDataset()
        dicom_pixel_data.file_meta.TransferSyntaxUID = image.extras["file_transfer_syntax"]
        dicom_pixel_data.PixelData = image.image or b""
        dicom_pixel_data.PhotometricInterpretation = image.extras["photometric_interpretation"]
        dicom_pixel_data.Rows = image.height
        dicom_pixel_data.Columns = image.width
        dicom_pixel_data.PixelRepresentation = image.extras["pixel_representation"]
        dicom_pixel_data.BitsAllocated = image.colour_depth
        dicom_pixel_data.BitsStored = image.colour_depth
        dicom_pixel_data.SamplesPerPixel = image.extras["samples_per_pixel"]
        image_array = dicom_pixel_data.pixel_array
    else:
        if image.height is None or image.width is None:
            raise ValueError(f"Invalid dimensions: ({image.height}, {image.width})")
        image_array = np.frombuffer(output_bytes, dtype=np.uint8).reshape(image.height, image.width)
    return image_array


def get_pil_images(image: BaseImageDataBytes) -> Dict[ImageProcessingOptions, Image.Image]:
    image_array = decompress_image(image)
    return {
        image_output_params.image_processing_options: Image.fromarray(
            apply_transforms(image_array, image_output_params.image_transform_functions)
        )
        for image_output_params in image.image_output_params
    }
