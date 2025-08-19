import os

import dataloader
import jax
import optax
from flax import nnx
from jax import random as jr
from jax.experimental import mesh_utils
from train_state import get_optimizer

from examples.flow_matching import FlowMatching
from examples.model import SmallDiT
from fll import get_default_checkpointer, train_fn


def get_optimizer(model, lr=1e-04):
  tx = optax.adamw(lr)
  tx = nnx.Optimizer(model, tx=tx)
  return tx


def get_sharding():
  num_devices = jax.local_device_count()
  mesh = jax.sharding.Mesh(
    mesh_utils.create_device_mesh((num_devices,)), ("data",)
  )
  model_sharding = jax.NamedSharding(mesh, jax.sharding.PartitionSpec())
  data_sharding = jax.NamedSharding(mesh, jax.sharding.PartitionSpec("data"))
  return model_sharding, data_sharding


def get_hooks(module, outfolder):
  checkpointer = get_default_checkpointer(outfolder, module)
  return [checkpointer]


def get_train_and_val_iters(rng_key, outfolder):
  return dataloader.data_loaders(rng_key, outfolder)


def run():
  outfolder = "./"
  rngs = nnx.rnglib.Rngs(jr.key(0))

  model = SmallDiT(rngs=rngs)
  optimizer = get_optimizer(model)
  model_sharding, data_sharding = get_sharding()
  module = FlowMatching(model, optimizer=optimizer, sharding=model_sharding)

  hooks = [
    get_default_checkpointer(module, os.path.join(outfolder, "checkpoints"))
  ]
  train_itr, val_itr = get_train_and_val_iters(
    jr.key(1), os.path.join(outfolder, "data")
  )

  train = train_fn(
    n_steps=100,
    n_eval_frequency=10,
    n_eval_batches=10,
    sharding=data_sharding,
    hooks=hooks,
    log_to_wandb=True,
  )
  train(jax.key(2), module, train_itr, val_itr)


if __name__ == "__main__":
  run()
