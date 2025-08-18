from functools import partial
from tensorflow.python.framework import ops
from tensorflow.python.ops import random_ops
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import cond as tf_cond
from tensorflow.python.ops.image_ops_impl import _AssertAtLeast3DImage
import tensorflow as tf
from math import pi


""" RANDOM ROTATION DATA AUGMENTATION """
AFFINE_TRANSFORM_INTERPOLATIONS = (
    "nearest",
    "bilinear",
)
AFFINE_TRANSFORM_FILL_MODES = (
    "constant",
    "nearest",
    "wrap",
    "reflect",
)


def _deg_to_rad(deg: float):
    return deg * pi / 180


def affine_transform(
    image,
    transform,
    interpolation="bilinear",
    fill_mode="constant",
    fill_value=0,
    data_format="channels_last",
):
    if interpolation not in AFFINE_TRANSFORM_INTERPOLATIONS:
        raise ValueError(
            "Invalid value for argument `interpolation`. Expected of one "
            f"{AFFINE_TRANSFORM_INTERPOLATIONS}. Received: "
            f"interpolation={interpolation}"
        )
    if fill_mode not in AFFINE_TRANSFORM_FILL_MODES:
        raise ValueError(
            "Invalid value for argument `fill_mode`. Expected of one "
            f"{AFFINE_TRANSFORM_FILL_MODES}. Received: fill_mode={fill_mode}"
        )
    if len(image.shape) not in (3, 4):
        raise ValueError(
            "Invalid image rank: expected rank 3 (single image) "
            "or rank 4 (batch of images). Received input with shape: "
            f"image.shape={image.shape}"
        )
    if len(transform.shape) not in (1, 2):
        raise ValueError(
            "Invalid transform rank: expected rank 1 (single transform) "
            "or rank 2 (batch of transforms). Received input with shape: "
            f"transform.shape={transform.shape}"
        )
    # unbatched case
    need_squeeze = False
    if len(image.shape) == 3:
        image = tf.expand_dims(image, axis=0)
        need_squeeze = True
    if len(transform.shape) == 1:
        transform = tf.expand_dims(transform, axis=0)

    if data_format == "channels_first":
        image = tf.transpose(image, (0, 2, 3, 1))

    affined = tf.raw_ops.ImageProjectiveTransformV3(
        images=image,
        transforms=tf.cast(transform, dtype=tf.float32),
        output_shape=tf.shape(image)[1:-1],
        fill_value=fill_value,
        interpolation=interpolation.upper(),
        fill_mode=fill_mode.upper(),
    )
    affined = tf.ensure_shape(affined, image.shape)

    if data_format == "channels_first":
        affined = tf.transpose(affined, (0, 3, 1, 2))
    if need_squeeze:
        affined = tf.squeeze(affined, axis=0)
    return affined


def _get_rotation_matrix(image: tf.Tensor, angle: int | float, rank: int):
    shape = array_ops.shape(image)
    if rank == 4:
        b = shape[0]
        h = shape[1]
        w = shape[2]
    
    elif rank == 3:
        b = 1
        h = shape[0]
        w = shape[1]
    else:
        raise ValueError(f"Random rotation only supports batched (4D) or unbatched (3D) tensors!")
    
    cos_theta = tf.math.cos(angle)
    sin_theta = tf.math.sin(angle)
    image_height = tf.cast(h, dtype=cos_theta.dtype)
    image_width = tf.cast(w, dtype=cos_theta.dtype)

    x_offset = (
        (image_width - 1) - (cos_theta * (image_width - 1) - sin_theta * (image_height - 1))
    ) / 2.0
    
    y_offset = (
        (image_height - 1) - (sin_theta * (image_width - 1) + cos_theta * (image_height - 1))
    ) / 2.0

    outputs = tf.concat([
        tf.math.cos(angle)[:, tf.newaxis],
        -tf.math.sin(angle)[:, tf.newaxis],
        x_offset[:, tf.newaxis],
        tf.math.sin(angle)[:, tf.newaxis],
        tf.math.cos(angle)[:, tf.newaxis],
        y_offset[:, tf.newaxis],
        tf.zeros((b, 2))
    ], axis=1)

    if rank == 3:
        outputs = tf.squeeze(outputs, axis=0)
    return outputs


def _random_rotation(image: tf.Tensor, random_func: callable, scope_name: str):
    with ops.name_scope(None, scope_name, [image]) as scope:
        image = ops.convert_to_tensor(image, name="image")
        image = _AssertAtLeast3DImage(image)
        shape = image.get_shape()

        def fn_rank3():
            # rotation last dimension
            angle = random_func(shape=[1, ])

            rotation_matrix = _get_rotation_matrix(image, angle, rank=3)
            rotated_image = affine_transform(
                image=image,
                transform=rotation_matrix,
                interpolation="bilinear",
                fill_mode="constant",
                fill_value=0.0,
                data_format="channels_last"
            )
            return rotated_image

        def fn_rank4():
            # rotation along last dimension, too!
            batch_size = array_ops.shape(image)[0]
            angle = random_func(shape=[batch_size, ])

            rotation_matrix = _get_rotation_matrix(image, angle, rank=4)
            rotated_image = affine_transform(
                image=image,
                transform=rotation_matrix,
                interpolation="bilinear",
                fill_mode="constant",
                fill_value=0.0,
                data_format="channels_last"
            )
            return rotated_image

        if shape.ndims is None:
            rank = array_ops.rank(image)
            return tf_cond.cond(math_ops.equal(rank, 3), fn_rank3, fn_rank4)
        if shape.ndims == 3:
            return fn_rank3()
        elif shape.ndims == 4:
            return fn_rank4()
        else:
            raise ValueError(
                '\'image\' (shape %s) must have either 3 or 4 dimensions.' % shape)


def random_rotation(image, angle, seed=None):
    """
    Apply random rotation to an image or 2-D tensor.
    Can be savely used within `tf.data.Dataset.map()`.

    Parameters
    ----------
    image : tf.Tensor
        image or 2-D tensor to rotate
    angle : int | tuple | list
        (min_angle, max_angle) rotation angle in degree for random rotation. A single value results in `angle=(-angle, angle)`.
    seed : int
        Random seed, defaults to `None`.

    Returns
    -------
    image : tf.Tensor
        Randomly rotated `image`.

    Raises
    ------
    ValueError
        If more than 2 values for `angle` are provided.
    ValueError
        If unsupported type for `angle` is provided.

    """

    if angle is None or angle == 0.0:
        return image
    
    if isinstance(angle, (int, float)):
        # only allow positive rotation
        minval = min(0.0, angle)
        maxval = max(0.0, angle)
    elif isinstance(angle, (list, tuple)):
        if len(angle) > 2:
            raise ValueError(f"Too many values for rotation angle, received angle={angle}, expected 2 values.")
        if len(angle) == 2:
            minval = min(angle)
            maxval = max(angle)
        else:
            # only allow positive rotation
            minval = min(0.0, *angle)
            maxval = max(0.0, *angle)
    else:
        raise ValueError(f"Unsupported type for angle {type(angle)}. Expected (int, float, tuple, list)")
    
    random_func = partial(random_ops.random_uniform, minval=_deg_to_rad(minval), maxval=_deg_to_rad(maxval), seed=seed)
    return _random_rotation(image=image, random_func=random_func, scope_name="random_rotation")
