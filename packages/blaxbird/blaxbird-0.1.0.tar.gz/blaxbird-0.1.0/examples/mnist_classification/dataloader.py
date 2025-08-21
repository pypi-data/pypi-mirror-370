import tensorflow as tf
import tensorflow_datasets as tfds
from jax import numpy as jnp
from jax import random as jr


def data_loaders(
  rng_key,
  outfolder,
  *,
  batch_size=128,
  buffer_size=1,
  prefetch_size=1,
  shuffle=True,
  split="train",
):
  datasets = tfds.load(
    "mnist",
    try_gcs=False,
    split=split,
    data_dir=outfolder,
  )
  if isinstance(split, str):
    datasets = [datasets]
  itrs = []
  if isinstance(shuffle, bool):
    shuffle = [shuffle]
  assert len(datasets) == len(shuffle)
  for dataset, shuffle_me in zip(datasets, shuffle):
    itr_key, rng_key = jr.split(rng_key)
    itr = as_iterable(
      itr_key, dataset, batch_size, buffer_size, prefetch_size, shuffle_me
    )
    itrs.append(itr)
  return itrs


def _crop_resize(image, resolution):
  h, w = tf.shape(image)[0], tf.shape(image)[1]
  crop = tf.minimum(h, w)
  image = image[
    (h - crop) // 2 : (h + crop) // 2, (w - crop) // 2 : (w + crop) // 2
  ]
  image = tf.image.resize(
    image,
    size=(resolution, resolution),
    antialias=True,
    method=tf.image.ResizeMethod.BICUBIC,
  )
  return tf.cast(image, tf.float32)


def as_iterable(rng_key, itr, batch_size, buffer_size, prefetch_size, shuffle):
  def process_fn(batch):
    img = tf.cast(batch["image"], tf.float32) / 255.0
    img = _crop_resize(img, 32)
    img = 2.0 * img - 1.0
    return {"image": img, "label": batch["label"]}

  max_int32 = jnp.iinfo(jnp.int32).max
  seed = jr.randint(rng_key, shape=(), minval=0, maxval=max_int32)
  return (
    itr.repeat()
    .shuffle(
      buffer_size,
      reshuffle_each_iteration=shuffle,
      seed=int(seed),
    )
    .map(process_fn, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    .batch(batch_size, drop_remainder=True)
    .prefetch(prefetch_size)
    .as_numpy_iterator()
  )
