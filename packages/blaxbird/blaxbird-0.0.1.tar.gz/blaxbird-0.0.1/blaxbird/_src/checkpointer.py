import os

import jax
import orbax.checkpoint as ocp
from absl import logging
from flax import nnx


def get_default_checkpointer(
  outfolder,
  *,
  save_frequency=1,
  max_to_keep=5,
  best_mode="min",
  best_fn=lambda x: x["val/loss"],
):
  checkpointer = ocp.PyTreeCheckpointer()
  options = ocp.CheckpointManagerOptions(
    max_to_keep=max_to_keep, create=True, best_mode=best_mode, best_fn=best_fn
  )
  checkpoint_manager = ocp.CheckpointManager(
    os.path.join(outfolder, "best"),
    options=options,
    item_names=("state", "opt_state"),
  )

  def save_fn(step, *, model, optimizer, metrics):
    if step % save_frequency != 0:
      return

    _, state = nnx.split(model)
    _, opt_state = nnx.split(optimizer.opt_state)
    try:
      logging.info("saving best checkpoint")
      checkpoint_manager.save(
        step=step,
        args=ocp.args.Composite(
          state=ocp.args.StandardSave(state),
          opt_state=ocp.args.StandardSave(opt_state),
        ),
        metrics=metrics,
        force=True,
      )
      checkpoint_manager.wait_until_finished()
    except Exception as e:
      logging.error(f"could not save checkpoint because of: {e}")
      logging.error("resuming nonetheless")
    try:
      logging.info("saving last checkpoint")
      checkpointer.save(
        os.path.join(outfolder, "last"), (state, opt_state), force=True
      )
    except Exception as e:
      logging.error(f"could not last checkpoint because of: {e}")
      logging.error("resuming nonetheless")

  def restore_best_fn(model, optimizer):
    graph_def, state = nnx.split(model)
    opt_def, opt_state = nnx.split(optimizer.opt_state)
    restored = checkpoint_manager.restore(
      checkpoint_manager.best_step(),
      args=ocp.args.Composite(
        state=ocp.args.StandardRestore(nnx.eval_shape(lambda: state)),
        opt_state=ocp.args.StandardRestore(nnx.eval_shape(lambda: opt_state)),
      ),
    )
    model = nnx.merge(graph_def, restored["state"])
    optimizer.opt_state = nnx.merge(opt_def, restored["opt_state"])
    return model, optimizer

  def restore_last_fn(model, optimizer):
    graphdef, state = nnx.split(model)
    optdef, opt_state = nnx.split(optimizer.opt_state)
    state = nnx.eval_shape(lambda: state)
    opt_state = nnx.eval_shape(lambda: opt_state)
    try:
      logging.info("trying to restore last checkpoint")
      restored = checkpointer.restore(
        os.path.join(outfolder, "last"), (state, opt_state)
      )
      model = nnx.merge(graphdef, restored[0])
      optimizer.opt_state = nnx.merge(optdef, restored[1])
    except FileNotFoundError:
      logging.warning("could not find last checkpoint. resuming with blank state")
    return model, optimizer

  return save_fn, restore_best_fn, restore_last_fn
