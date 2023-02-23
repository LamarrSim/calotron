import os
import yaml
import socket
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from datetime import datetime
from html_reports import Report
from sklearn.utils import shuffle
from argparse import ArgumentParser

from calotron.models import Transformer
from calotron.callbacks.schedulers import AttentionDecay
from calotron.simulators import Simulator, ExportSimulator
from calotron.utils import initHPSingleton, getSummaryHTML


DTYPE = tf.float32
TRAIN_RATIO = 0.75
BATCHSIZE = 128
EPOCHS = 500


# +------------------+
# |   Parser setup   |
# +------------------+

parser = ArgumentParser(description="scripts configuration")

parser.add_argument("--saving", action="store_true")
parser.add_argument("--no-saving", dest="saving", action="store_false")
parser.set_defaults(saving=True)

args = parser.parse_args()

# +-------------------+
# |   Initial setup   |
# +-------------------+

hp = initHPSingleton()

with open("config/directories.yml") as file:
  config_dir = yaml.full_load(file)

data_dir = config_dir["data_dir"]
export_dir = config_dir["export_dir"]
images_dir = config_dir["images_dir"]
report_dir = config_dir["report_dir"]

# +------------------+
# |   Data loading   |
# +------------------+

npzfile = np.load(f"{data_dir}/train-data-demo.npz")
photon = npzfile["photon"][:,::-1]
cluster = npzfile["cluster"][:,::-1]

#print(f"photon {photon.shape}\n", photon)
#print(f"cluster {cluster.shape}\n", cluster)

photon, cluster = shuffle(photon, cluster)

chunk_size = photon.shape[0]
train_size = int(TRAIN_RATIO * chunk_size)

# +-------------------------+
# |   Dataset preparation   |
# +-------------------------+

X = tf.cast(photon, dtype=DTYPE)
Y = tf.cast(cluster, dtype=DTYPE)

train_ds = (tf.data.Dataset.from_tensor_slices((X[:train_size], Y[:train_size]))
              .batch(hp.get("batch_size", BATCHSIZE), drop_remainder=True)
              .cache()
              .prefetch(tf.data.AUTOTUNE))

if TRAIN_RATIO != 1.0:
  val_ds = (tf.data.Dataset.from_tensor_slices((X[train_size:], Y[train_size:]))
              .batch(BATCHSIZE, drop_remainder=True)
              .cache()
              .prefetch(tf.data.AUTOTUNE))
else:
  val_ds = None

# +------------------------+
# |   Model construction   |
# +------------------------+

model = Transformer(output_depth=hp.get("t_output_depth", Y.shape[2]),
                    encoder_depth=hp.get("t_encoder_depth", 32),
                    decoder_depth=hp.get("t_decoder_depth", 32),
                    num_layers=hp.get("t_num_layers", 5),
                    num_heads=hp.get("t_num_heads", 4),
                    key_dim=hp.get("t_key_dim", 64),
                    encoder_pos_dim=hp.get("t_encoder_pos_dim", 32),
                    decoder_pos_dim=hp.get("t_decoder_pos_dim", 32),
                    encoder_pos_normalization=hp.get("t_encoder_pos_normalization", 128),
                    decoder_pos_normalization=hp.get("t_decoder_pos_normalization", 128),
                    encoder_max_length=hp.get("t_encoder_max_length", X.shape[1]),
                    decoder_max_length=hp.get("t_decoder_max_length", Y.shape[1]),
                    ff_units=hp.get("t_ff_units", 256),
                    dropout_rate=hp.get("t_dropout_rate", 0.1),
                    pos_sensitive=hp.get("t_pos_sensitive", True),
                    residual_smoothing=hp.get("t_residual_smoothing", True),
                    output_activations=hp.get("t_output_activations", ["linear", "linear", "sigmoid"]),
                    start_token_initializer=hp.get("t_start_toke_initializer", "zeros"),
                    dtype=DTYPE)

output = model((X, Y))
model.summary()

# +----------------------+
# |   Optimizers setup   |
# +----------------------+

lr0 = 1e-3
rms = tf.keras.optimizers.RMSprop(lr0)
hp.get("optimizer", "RMSprop")
hp.get("tlr0", lr0)

# +----------------------------+
# |   Training configuration   |
# +----------------------------+

mse = tf.keras.losses.MeanSquaredError()
hp.get("loss", mse.name)

model.compile(loss=mse, optimizer=rms, metrics=hp.get("metrics", ["mae"]))

# +------------------------------+
# |   Learning rate scheduling   |
# +------------------------------+

d_model = 64
warmup_steps = 2_000
sched = AttentionDecay(model.optimizer,
                       d_model=d_model,
                       warmup_steps=warmup_steps,
                       verbose=True)
hp.get("sched", "AttentionDecay")
hp.get("d_model", d_model)
hp.get("warmup_steps", warmup_steps)

# +------------------------+
# |   Training procedure   |
# +------------------------+

start = datetime.now()
train = model.fit(train_ds,
                  epochs=hp.get("epochs", EPOCHS),
                  validation_data=val_ds,
                  callbacks=[sched])
stop = datetime.now()

duration = str(stop-start).split(".")[0].split(":")   # [HH, MM, SS]
duration = f"{duration[0]}h {duration[1]}min {duration[2]}s"
print(f"[INFO] Model training completed in {duration}")

# +------------------+
# |   Model export   |
# +------------------+

start_token = model.get_start_token(Y)
sim = Simulator(model, start_token=start_token)
exp_sim = ExportSimulator(sim, max_length=Y.shape[1])
out = exp_sim(X)

timestamp = str(datetime.now())
date, hour = timestamp.split(" ")
date = date.replace("-", "/")
hour = hour.split(".")[0]

prefix = ""
timestamp = timestamp.split(".")[0].replace("-", "").replace(" ", "-")
for time, unit in zip(timestamp.split(":"), ["h", "m", "s"]):
  prefix += time + unit   # YYYYMMDD-HHhMMmSSs
prefix += "_transformer"

if args.saving:
  export_model_fname = f"{export_dir}/{prefix}_model"
  tf.saved_model.save(exp_sim, export_dir=export_model_fname)
  hp.dump(f"{export_model_fname}/hyperparams.yml")   # export also list of hyperparams
  print(f"[INFO] Trained model correctly exported to {export_model_fname}")
  export_img_fname = f"{images_dir}/{prefix}_img"
  os.makedirs(export_img_fname)   # need to save images

# +---------------------+
# |   Training report   |
# +---------------------+

report = Report()
report.add_markdown('<h1 align="center">Transformer training report</h1>')

report.add_markdown(
  f"""
    - Script executed on {socket.gethostname()}
    - Model training completed in {duration}
    - Report generated on {date} at {hour}
  """
)
report.add_markdown("---")

## Hyperparameters and other details
report.add_markdown('<h2 align="center">Hyperparameters and other details</h2>')
content = ""
for k, v in hp.get_dict().items():
  content += f"\t- {k} : {v}\n"
report.add_markdown(content)
report.add_markdown("---")

## Transformer architecture
report.add_markdown('<h2 align="center">Transformer architecture</h2>')
html_table, num_params = getSummaryHTML(model)
report.add_markdown(html_table)
report.add_markdown(f"**Total params** : {num_params}")
report.add_markdown("---")

## Training plots
report.add_markdown('<h2 align="center">Training plots</h2>')

#### Learning curves
plt.figure(figsize=(8,5), dpi=100)
plt.title("Learning curves", fontsize=14)
plt.xlabel("Training epochs", fontsize=12)
plt.ylabel("Loss", fontsize=12)
plt.plot(
  np.array(train.history["loss"]), 
  lw=1.5, color="#3288bd", label="MSE"
)
plt.yscale("log")
plt.legend(loc="upper left", fontsize=10)
if args.saving:
  plt.savefig(fname=f"{export_img_fname}/learn-curves.png")
report.add_figure(options="width=45%")
plt.close()

#### Learning rate scheduling
plt.figure(figsize=(8,5), dpi=100)
plt.title("Learning rate scheduling", fontsize=14)
plt.xlabel("Training epochs", fontsize=12)
plt.ylabel("Learning rate", fontsize=12)
plt.plot(
  np.array(train.history["lr"]),
  lw=1.5, color="#3288bd", label="transformer"
)
plt.yscale("log")
plt.legend(loc="upper right", fontsize=10)
if args.saving:
  plt.savefig(fname=f"{export_img_fname}/lr-sched.png")
report.add_figure(options="width=45%")
plt.close()

#### MAE curves
plt.figure(figsize=(8,5), dpi=100)
plt.title("Metric curves", fontsize=14)
plt.xlabel("Training epochs", fontsize=12)
plt.ylabel("Mean absolute error", fontsize=12)
plt.plot(
  np.array(train.history["mae"]),
  lw=1.5, color="#4dac26", label="training set"
)
if TRAIN_RATIO != 1.0:
  plt.plot(
    np.array(train.history["val_mae"]),
    lw=1.5, color="#d01c8b", label="validation set"
  )
plt.legend(loc="upper right", fontsize=10)
if args.saving:
  plt.savefig(fname=f"{export_img_fname}/metric-curves.png")
report.add_figure(options="width=45%")
plt.close()

report.add_markdown("---")

## Validation plots
report.add_markdown('<h2 align="center">Validation plots</h2>')

#### X histogram
plt.figure(figsize=(8,5), dpi=100)
plt.xlabel("$x$ coordinate", fontsize=12)
plt.ylabel("Candidates", fontsize=12)
x_min = Y[:,:,0].numpy().flatten().min()
x_max = Y[:,:,0].numpy().flatten().max()
x_bins = np.linspace(x_min, x_max, 101)
plt.hist(
  Y[:,:,0].numpy().flatten(),
  bins=x_bins, color="#3288bd",
  label="Training data"
)
plt.hist(
  out[:,:,0].numpy().flatten(),
  bins=x_bins, histtype="step", color="#fc8d59",
  lw=2, label="Transformer output"
)
plt.yscale("log")
plt.legend(loc="upper left", fontsize=10)
if args.saving:
  plt.savefig(f"{export_img_fname}/x-hist.png")
report.add_figure(options="width=45%")
plt.close()

#### Y histogram
plt.figure(figsize=(8,5), dpi=100)
plt.xlabel("$y$ coordinate", fontsize=12)
plt.ylabel("Candidates", fontsize=12)
y_min = Y[:,:,1].numpy().flatten().min()
y_max = Y[:,:,1].numpy().flatten().max()
y_bins = np.linspace(y_min, y_max, 101)
plt.hist(
  Y[:,:,1].numpy().flatten(), 
  bins=y_bins, color="#3288bd",
  label="Training data"
)
plt.hist(
  out[:,:,1].numpy().flatten(),
  bins=y_bins, histtype="step", color="#fc8d59",
  lw=2, label="Transformer output"
)
plt.yscale("log")
plt.legend(loc="upper left", fontsize=10)
if args.saving:
  plt.savefig(f"{export_img_fname}/y-hist.png")
report.add_figure(options="width=45%")
plt.close()

#### X-Y histogram
plt.figure(figsize=(16,5), dpi=100)
plt.subplot(1,2,1)
plt.title("Training data", fontsize=14)
plt.xlabel("$x$ coordinate", fontsize=12)
plt.ylabel("$y$ coordinate", fontsize=12)
plt.hist2d(
  Y[:,:,0].numpy().flatten(),
  Y[:,:,1].numpy().flatten(), 
  bins=(x_bins, y_bins), cmin=0, cmap="gist_heat"
)
plt.subplot(1,2,2)
plt.title("Transformer output", fontsize=14)
plt.xlabel("$x$ coordinate", fontsize=12)
plt.ylabel("$y$ coordinate", fontsize=12)
plt.hist2d(
  out[:,:,0].numpy().flatten(),
  out[:,:,1].numpy().flatten(), 
  bins=(x_bins, y_bins), cmin=0, cmap="gist_heat"
)
if args.saving:
  plt.savefig(f"{export_img_fname}/x-y-hist2d.png")
report.add_figure(options="width=95%")
plt.close()

#### Event examples
for i in range(4):
  evt = int(np.random.uniform(0, chunk_size))
  plt.figure(figsize=(8,6), dpi=100)
  plt.xlabel("$x$ coordinate", fontsize=12)
  plt.ylabel("$y$ coordinate", fontsize=12)
  plt.scatter(
    X[evt,:,0].numpy().flatten(),
    X[evt,:,1].numpy().flatten(),
    s=50 * X[evt,:,2].numpy().flatten() / Y[evt,:,2].numpy().flatten().max(),
    marker="o", facecolors="none", edgecolors="#d7191c",
    lw=0.75, label="True photon"
  )
  plt.scatter(
    Y[evt,:,0].numpy().flatten(),
    Y[evt,:,1].numpy().flatten(),
    s=50 * Y[evt,:,2].numpy().flatten() / Y[evt,:,2].numpy().flatten().max(),
    marker="s", facecolors="none", edgecolors="#2b83ba", 
    lw=0.75, label="Calo neutral cluster"
  )
  plt.scatter(
    out[evt,:,0].numpy().flatten(),
    out[evt,:,1].numpy().flatten(),
    s=50 * out[evt,:,2].numpy().flatten() / Y[evt,:,2].numpy().flatten().max(),
    marker="^", facecolors="none", edgecolors="#1a9641",
    lw=0.75, label="Transformer output"
  )
  plt.legend()
  if args.saving:
    plt.savefig(f"{export_img_fname}/evt-example-{i}.png")
  report.add_figure(options="width=45%")
plt.close()

#### Energy histogram
plt.figure(figsize=(8,5), dpi=100)
plt.xlabel("Preprocessed energy [a.u]", fontsize=12)
plt.ylabel("Candidates", fontsize=12)
e_min = Y[:,:,2].numpy().flatten().min()
e_max = Y[:,:,2].numpy().flatten().max()
e_bins = np.linspace(e_min, e_max, 101)
plt.hist(
  Y[:,:,2].numpy().flatten(),
  bins=e_bins, color="#3288bd",
  label="Training data"
)
plt.hist(
  out[:,:,2].numpy().flatten(),
  bins=e_bins, histtype="step", color="#fc8d59",
  lw=2, label="Transformer output"
)
plt.yscale("log")
plt.legend(loc="upper left", fontsize=10)
if args.saving:
  plt.savefig(f"{export_img_fname}/energy-hist.png")
report.add_figure(options="width=45%")
plt.close()

#### X-energy histogram
plt.figure(figsize=(16,5), dpi=100)
plt.subplot(1,2,1)
plt.title("Training data", fontsize=14)
plt.xlabel("$x$ coordinate", fontsize=12)
plt.ylabel("Preprocessed energy [a.u]", fontsize=12)
plt.hist2d(
  Y[:,:,0].numpy().flatten(),
  Y[:,:,2].numpy().flatten(), 
  bins=(x_bins, e_bins), cmin=0, cmap="gist_heat"
)
plt.subplot(1,2,2)
plt.title("Transformer output", fontsize=14)
plt.xlabel("$x$ coordinate", fontsize=12)
plt.ylabel("Preprocessed energy [a.u]", fontsize=12)
plt.hist2d(
  out[:,:,0].numpy().flatten(),
  out[:,:,2].numpy().flatten(), 
  bins=(x_bins, y_bins), cmin=0, cmap="gist_heat"
)
if args.saving:
  plt.savefig(f"{export_img_fname}/x-energy-hist2d.png")
report.add_figure(options="width=95%")
plt.close()

#### Y-energy histogram
plt.figure(figsize=(16,5), dpi=100)
plt.subplot(1,2,1)
plt.title("Training data", fontsize=14)
plt.xlabel("$y$ coordinate", fontsize=12)
plt.ylabel("Preprocessed energy [a.u]", fontsize=12)
plt.hist2d(
  Y[:,:,1].numpy().flatten(),
  Y[:,:,2].numpy().flatten(), 
  bins=(x_bins, e_bins), cmin=0, cmap="gist_heat"
)
plt.subplot(1,2,2)
plt.title("Transformer output", fontsize=14)
plt.xlabel("$y$ coordinate", fontsize=12)
plt.ylabel("Preprocessed energy [a.u]", fontsize=12)
plt.hist2d(
  out[:,:,1].numpy().flatten(),
  out[:,:,2].numpy().flatten(), 
  bins=(x_bins, y_bins), cmin=0, cmap="gist_heat"
)
if args.saving:
  plt.savefig(f"{export_img_fname}/y-energy-hist2d.png")
report.add_figure(options="width=95%")
plt.close()

#### Energy batches plot
plt.figure(figsize=(16,10), dpi=100)
plt.subplot(1,2,1)
plt.title("Training data", fontsize=14)
plt.xlabel("Cluster energy deposits", fontsize=12)
plt.ylabel("Events", fontsize=12)
plt.imshow(
  Y[:128,:,2].numpy(),
  aspect="auto", interpolation="none"
)
plt.subplot(1,2,2)
plt.title("Transformer output", fontsize=14)
plt.xlabel("Cluster energy deposits", fontsize=12)
plt.ylabel("Events", fontsize=12)
plt.imshow(
  out[:128,:,2].numpy(),
  aspect="auto", interpolation="none"
)
if args.saving:
  plt.savefig(f"{export_img_fname}/energy-batches.png")
report.add_figure(options="width=95%")
plt.close()

report.add_markdown("---")

report_fname = f"{report_dir}/{prefix}_train-report.html"
report.write_report(filename=report_fname)
print(f"[INFO] Training report correctly exported to {report_fname}")
