import torch
from torch.optim import lr_scheduler
import torch.optim as optim

from int_phy.appearance.trainer import fit
from int_phy.appearance.datasets import Objects, TripletObjects, DATA_SAVE_DIR
from int_phy.appearance.utils import cuda, plot_embeddings, extract_embeddings
import os

# Set up the network and training parameters
from int_phy.appearance.networks import EmbeddingNet, TripletNet
from int_phy.appearance.losses import TripletLoss


MODEL_SAVE_DIR = os.path.join("int_phy", "appearance", "pre_trained")

if __name__ == "__main__":
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    train_dataset = Objects()
    print(len(train_dataset))
    triplet_train_dataset = TripletObjects(train_dataset) # Returns triplets of images
    batch_size = 400
    kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}
    triplet_train_loader = torch.utils.data.DataLoader(triplet_train_dataset, batch_size=batch_size, shuffle=True, **kwargs)

    margin = 1
    embedding_net = EmbeddingNet()
    model = TripletNet(embedding_net)
    if cuda:
        print("Using GPU")
        model.cuda()
    loss_fn = TripletLoss(margin)
    lr = 1e-3
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = lr_scheduler.StepLR(optimizer, 10, gamma=0.1, last_epoch=-1)
    n_epochs = 100
    log_interval = 400

    # %%
    fit(triplet_train_loader, None, model, loss_fn, optimizer, scheduler, n_epochs, cuda, log_interval)

    batch_size = 256
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, **kwargs)

    train_embeddings_tl, train_labels_tl = extract_embeddings(train_loader, model)
    plot_embeddings(train_embeddings_tl, train_labels_tl)

    torch.save(model.embedding_net.state_dict(), os.path.join(MODEL_SAVE_DIR, "model.pth"))

