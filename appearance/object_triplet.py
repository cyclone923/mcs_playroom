import torch
from torch.optim import lr_scheduler
import torch.optim as optim

from appearance.trainer import fit
from appearance.datasets import Objects, TripletObjects
from appearance.utils import cuda, plot_embeddings, extract_embeddings
import os

train_dataset = Objects()
triplet_train_dataset = TripletObjects(train_dataset) # Returns triplets of images
batch_size = 48
kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}
triplet_train_loader = torch.utils.data.DataLoader(triplet_train_dataset, batch_size=batch_size, shuffle=True, **kwargs)

# Set up the network and training parameters
from appearance.networks import EmbeddingNet, TripletNet
from appearance.losses import TripletLoss

margin = 1
embedding_net = EmbeddingNet()
model = TripletNet(embedding_net)
if cuda:
    model.cuda()
loss_fn = TripletLoss(margin)
lr = 1e-3
optimizer = optim.Adam(model.parameters(), lr=lr)
scheduler = lr_scheduler.StepLR(optimizer, 10, gamma=0.1, last_epoch=-1)
n_epochs = 100
log_interval = 1

# %%
fit(triplet_train_loader, None, model, loss_fn, optimizer, scheduler, n_epochs, cuda, log_interval)

batch_size = 256
kwargs = {'num_workers': 1, 'pin_memory': True} if cuda else {}


train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, **kwargs)

train_embeddings_tl, train_labels_tl = extract_embeddings(train_loader, model)
plot_embeddings(train_embeddings_tl, train_labels_tl)

torch.save(model.embedding_net.state_dict(), os.path.join("appearance", "pre_trained", "model.pth"))

