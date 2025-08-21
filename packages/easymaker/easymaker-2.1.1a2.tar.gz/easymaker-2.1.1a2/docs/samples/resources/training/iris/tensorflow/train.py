import argparse
import os

os.environ["NCCL_DEBUG"] = "TRACE"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import pandas as pd
import tensorflow as tf

print("[train.py] start tensorflow training (2023.09.06 ver)")
tf_config = os.environ.get("TF_CONFIG", "{}")
print(f"tf_config: {tf_config}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning_rate", type=float, default=0.01)
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--batch_size", type=int, default=32)

    parser.add_argument("--dataset_train", type=str, default=os.environ.get("EM_DATASET_TRAIN"))
    parser.add_argument("--dataset_test", type=str, default=os.environ.get("EM_DATASET_TEST"))
    parser.add_argument("--model_dir", type=str, default=os.environ.get("EM_MODEL_DIR"))
    parser.add_argument("--checkpoint_dir", type=str, default=os.environ.get("EM_CHECKPOINT_DIR"))

    return parser.parse_known_args()


args, _ = parse_args()


def _is_gpu_available():
    print(f"[train.py] available gpu count : {len(tf.config.list_physical_devices('GPU'))}")
    return len(tf.config.list_physical_devices("GPU")) > 0


def _is_chief(task_type):
    # when the strategy is non-distributed one, task_type is None.
    return task_type is None or task_type == "chief"


def _get_temp_dir(dirpath, task_id):
    base_dirpath = "workertemp_" + str(task_id)
    temp_dir = os.path.join(dirpath, base_dirpath)
    tf.io.gfile.makedirs(temp_dir)
    return temp_dir


def write_filepath(filepath, task_type, task_id):
    dirpath = os.path.dirname(filepath)
    base = os.path.basename(filepath)
    if not _is_chief(task_type):
        dirpath = _get_temp_dir(dirpath, task_id)
    return os.path.join(dirpath, base)


def get_dataset(args):
    x_train = pd.read_csv(f"{args.dataset_train}/x_train.csv", header=None)
    y_train = pd.read_csv(f"{args.dataset_train}/y_train.csv", header=None)
    x_test = pd.read_csv(f"{args.dataset_test}/x_test.csv", header=None)
    y_test = pd.read_csv(f"{args.dataset_test}/y_test.csv", header=None)

    def preprocess(features, label):
        return features, label

    train_dataset = tf.data.Dataset.from_tensor_slices((x_train.values, y_train.values))
    test_dataset = tf.data.Dataset.from_tensor_slices((x_test.values, y_test.values))
    train_dataset = train_dataset.map(preprocess).batch(args.batch_size)
    test_dataset = test_dataset.map(preprocess).batch(args.batch_size)

    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA
    train_dataset = train_dataset.with_options(options)
    test_dataset = test_dataset.with_options(options)

    N, D = x_train.shape

    return train_dataset, test_dataset, D


# train
strategy = None
if _is_gpu_available():
    communication_options = tf.distribute.experimental.CommunicationOptions(implementation=tf.distribute.experimental.CommunicationImplementation.NCCL)
    strategy = tf.distribute.MultiWorkerMirroredStrategy(communication_options=communication_options)
else:
    strategy = tf.distribute.MultiWorkerMirroredStrategy()

train_dataset, test_dataset, D = get_dataset(args)

callbacks = [
    tf.keras.callbacks.ModelCheckpoint(filepath=f"{args.checkpoint_dir}/cp-{{epoch:04d}}.ckpt", save_freq="epoch", period=50),
]

task_type, task_id = (strategy.cluster_resolver.task_type, strategy.cluster_resolver.task_id)
if _is_chief(task_type):
    callbacks.append(tf.keras.callbacks.TensorBoard(log_dir=f'{os.environ.get("EM_TENSORBOARD_LOG_DIR")}'))

with strategy.scope():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(5, kernel_initializer="uniform", activation="relu", input_dim=D))
    model.add(tf.keras.layers.Dense(5, kernel_initializer="uniform", activation="relu"))
    model.add(tf.keras.layers.Dense(3, kernel_initializer="uniform", activation="softmax"))
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate), loss="sparse_categorical_crossentropy", metrics=["accuracy"])

input_checkpoint_path = os.environ.get("EM_CHECKPOINT_INPUT_DIR", None)
if input_checkpoint_path:
    print(f"Load Model from checkpoint {input_checkpoint_path}")
    if os.path.isdir(input_checkpoint_path):
        print(f"checkpoint file list : {os.listdir(input_checkpoint_path)}")
    model.load_weights(input_checkpoint_path)
    print("checkpoint load complete")

print(f"[train.py] model {model}")
r = model.fit(train_dataset, validation_data=test_dataset, epochs=args.epochs, callbacks=callbacks)

write_model_path = write_filepath(args.model_dir, task_type, task_id)
print(f"[train.py] model.save {write_model_path}")
model.save(write_model_path)

if not _is_chief(task_type):
    tf.io.gfile.rmtree(os.path.dirname(write_model_path))
print("[train.py] training complete")
