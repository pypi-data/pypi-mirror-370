import argparse
import os
import subprocess
import sys

import pandas as pd
import torch
import torch.distributed as dist
import torch.nn as nn
from model import Model
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.distributed import DistributedSampler
from torch.utils.tensorboard import SummaryWriter

print(f"Verify installation...\n\tTensor:\t{torch.rand(5, 3)}\n\tGPU:\t{torch.cuda.is_available()}\nDone.")
os.environ["NCCL_DEBUG"] = "TRACE"
WORLD_SIZE = int(os.environ.get("WORLD_SIZE", 1))
RANK = int(os.environ.get("RANK", 0))


def should_distribute():
    return dist.is_available() and WORLD_SIZE > 1


def is_distributed():
    return dist.is_available() and dist.is_initialized()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--model_version", type=str, default="1.0.0")
    parser.add_argument("--input_checkpoint_name", type=str, default="cp.0050.pt")

    parser.add_argument("--dataset_train", type=str, default=os.environ.get("EM_DATASET_TRAIN"))
    parser.add_argument("--dataset_test", type=str, default=os.environ.get("EM_DATASET_TEST"))
    parser.add_argument("--source_dir", type=str, default=os.environ.get("EM_SOURCE_DIR"))
    parser.add_argument("--model_dir", type=str, default=os.environ.get("EM_MODEL_DIR"))
    parser.add_argument("--checkpoint_dir", type=str, default=os.environ.get("EM_CHECKPOINT_DIR"))
    parser.add_argument("--tensorboard_dir", type=str, default=os.environ.get("EM_TENSORBOARD_LOG_DIR"))

    return parser.parse_known_args()


args, _ = parse_args()

# train

x_train = pd.read_csv(f"{args.dataset_train}/x_train.csv", header=None)
y_train = pd.read_csv(f"{args.dataset_train}/y_train.csv", header=None).squeeze("columns")
x_test = pd.read_csv(f"{args.dataset_test}/x_test.csv", header=None)
y_test = pd.read_csv(f"{args.dataset_test}/y_test.csv", header=None).squeeze("columns")

N, D = x_train.shape

train_dataset = TensorDataset(torch.FloatTensor(x_train.values), torch.LongTensor(y_train.values))
test_dataset = TensorDataset(torch.FloatTensor(x_test.values), torch.LongTensor(y_test.values))


def train(model, device, train_data_loader, eval_data_loader, criterion, optimizer):
    model.train()
    train_loss = 0
    train_correct = 0
    for _batch_idx, (data, target) in enumerate(train_data_loader):
        print(f"RANK : {RANK}, len_target : {len(target)}")
        data, target = data.to(device), target.to(device)
        # feedforward
        optimizer.zero_grad()
        out = model(data)
        loss = criterion(out, target)
        train_loss += loss.item()
        train_correct += (torch.argmax(out, dim=1) == target).sum().item()
        # backpropagate
        loss.backward()
        optimizer.step()

    model.eval()
    eval_loss = 0
    eval_correct = 0
    for _batch_idx, (data, target) in enumerate(eval_data_loader):
        data, target = data.to(device), target.to(device)
        output = model(data)
        loss = criterion(output, target)
        eval_loss += loss.item()
        eval_correct += (torch.argmax(output, dim=1) == target).sum().item()

    # Return loss
    train_avg_loss = train_loss / len(train_data_loader.dataset)
    train_accuracy = train_correct / len(train_data_loader.dataset)
    eval_avg_loss = eval_loss / len(eval_data_loader.dataset)
    eval_accuracy = eval_correct / len(eval_data_loader.dataset)
    return train_avg_loss, train_accuracy, eval_avg_loss, eval_accuracy


use_cuda = torch.cuda.is_available()
if use_cuda:
    print("Using CUDA")
device = torch.device("cuda" if use_cuda else "cpu")

train_sampler = None
test_sampler = None
if should_distribute():
    backend = None
    if use_cuda:
        backend = dist.Backend.NCCL
    else:
        backend = dist.Backend.GLOO
    dist.init_process_group(backend=backend)
    print(f"Using distributed PyTorch with {backend} backend")
    train_sampler = DistributedSampler(train_dataset)
    test_sampler = DistributedSampler(test_dataset)

kwargs = {"num_workers": 1, "pin_memory": True} if use_cuda else {}

train_loader = DataLoader(train_dataset, sampler=train_sampler, batch_size=args.batch_size, **kwargs)
test_loader = DataLoader(test_dataset, sampler=test_sampler, batch_size=args.batch_size, **kwargs)

epoch_nums = []
training_loss = []
training_accuracy = []
validation_loss = []
validation_accuracy = []

model = Model(input_features=D).to(device)

input_checkpoint_path = os.environ.get("EM_CHECKPOINT_INPUT_DIR", None)
if input_checkpoint_path:
    print(f"EM_CHECKPOINT_INPUT_DIR file list : {os.listdir(input_checkpoint_path)}")
    checkpoint_file_path = os.path.join(input_checkpoint_path, args.input_checkpoint_name)  # checkpoint 파일 이름 지정 필요
    print(f"Load Model from checkpoint {checkpoint_file_path}")
    model.load_state_dict(torch.load(checkpoint_file_path))

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.RMSprop(model.parameters(), lr=args.lr)

writer = None
if RANK == 0 and args.model_dir:
    os.makedirs(args.model_dir, exist_ok=True)
    writer = SummaryWriter(f"{args.tensorboard_dir}/")

if is_distributed():
    model = nn.parallel.DistributedDataParallel(model)

if args.checkpoint_dir:
    os.makedirs(args.checkpoint_dir, exist_ok=True)

# Train over set epochs
for epoch in range(1, args.epochs + 1):
    # Feed the training data into the model to optimize the weights
    train_loss, train_accuracy, eval_loss, eval_accuracy = train(model, device, train_loader, test_loader, criterion, optimizer)

    # Log the metrcs for this epoch
    epoch_nums.append(epoch)
    training_loss.append(train_loss)
    training_accuracy.append(train_accuracy)
    validation_loss.append(eval_loss)
    validation_accuracy.append(eval_accuracy)

    if writer is not None:
        writer.add_scalar("Loss/train", train_loss, epoch)
        writer.flush()

    print(f"Epoch {epoch:d}: Training-loss={train_loss:.4f}, Training-accuracy={train_accuracy:.4f}, Validation-loss= {eval_loss:.4f}, Validation-accuracy={eval_accuracy:.4f}")

    if epoch % 50 == 0 and RANK == 0 and args.checkpoint_dir:
        os.makedirs(args.checkpoint_dir, exist_ok=True)
        if should_distribute():
            torch.save(model.module.state_dict(), f"{args.checkpoint_dir}/cp.{epoch:04d}.pt")
        else:
            torch.save(model.state_dict(), f"{args.checkpoint_dir}/cp.{epoch:04d}.pt")

        print(f"checkpoint saved at {args.checkpoint_dir}/cp-{epoch:04d}.pt")

if writer is not None:
    writer.close()

if RANK == 0 and args.model_dir:
    os.makedirs(args.model_dir, exist_ok=True)
    if should_distribute():
        torch.save(model.module.state_dict(), f"{args.model_dir}/iris.pt")
    else:
        torch.save(model.state_dict(), f"{args.model_dir}/iris.pt")

    os.makedirs(f"{args.model_dir}/model-store", exist_ok=True)

    cmd = " ".join(
        [
            "torch-model-archiver",
            "--model-name",
            "iris",
            "--serialized-file",
            f"{args.model_dir}/iris.pt",
            "--model-file",
            f"{args.source_dir}/model.py",
            "--handler",
            f"{args.source_dir}/handler.py",
            "--export-path",
            f"{args.model_dir}/model-store/",
            "--version",
            f"{args.model_version}",
            "--force",
        ]
    )

    try:
        retcode = subprocess.call(cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        elif retcode != 0:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
