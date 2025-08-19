import dataclasses

import numpy as np
from flax import nnx
from jax import numpy as jnp
from jax import random as jr

import fll


def _forward_process(inputs, times, noise):
  new_shape = (-1,) + tuple(np.ones(inputs.ndim - 1, dtype=np.int32).tolist())
  times = times.reshape(new_shape)
  inputs_t = times * inputs + (1.0 - times) * noise
  return inputs_t


@dataclasses.dataclass
class FlowMatchingConfig:
  n_sampling_steps: int
  time_eps: float = 1e-3
  time_max: float = 1.0


class FlowMatching(fll.Module):
  def __init__(
    self, model, config=FlowMatchingConfig(10), *, optimizer, sharding
  ):
    super().__init__(model, optimizer, sharding)
    self.config = config

  def __call__(self, inputs, times):
    return self.model(inputs=inputs, times=times * 999.0)

  def _loss_fn(self, rng_key, inputs):
    time_key, noise_key = jr.split(rng_key)
    times = jr.uniform(time_key, shape=(inputs.shape[0],))
    times = (
      times * (self.config.time_max - self.config.time_eps)
      + self.config.time_eps
    )
    noise = jr.normal(noise_key, inputs.shape)
    inputs_t = _forward_process(inputs, times, noise)
    vs = self(inputs_t, times)
    target = inputs - noise
    loss = jnp.mean(jnp.square(target - vs))
    return loss

  @nnx.jit
  def train_step(self, rng_key, batch):
    loss, grads = nnx.value_and_grad(self._loss_fn)((rng_key, batch["inputs"]))
    return loss, grads

  @nnx.jit
  def eval_step(self, rng_key, batch):
    loss = self._loss_fn(rng_key, batch["inputs"])
    return loss

  @nnx.jit
  def sample(self, rng_key, sample_shape):
    n = sample_shape[0]
    dt = 1.0 / self.config.n_sampling_steps
    samples = jr.normal(rng_key, sample_shape)
    for i in range(self.config.n_sampling_steps):
      times = i / self.config.n_sampling_steps
      times = (
        times * (self.config.time_max - self.config.time_eps)
        + self.config.time_eps
      )
      times = jnp.repeat(times, n)
      vt = self(
        inputs=samples,
        times=times * 999.0,
      )
      samples = samples + vt * dt
    return samples
