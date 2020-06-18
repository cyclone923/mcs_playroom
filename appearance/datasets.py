import numpy as np
from int_phy_recollect_appearance import SHAPE_TYPES, SCENE_TYPES
from torch.utils.data import Dataset
import torch
import os

np.random.seed(0)

class Objects(Dataset):
    def __init__(self):
        image_tensor = []
        target_tensor = []
        for i, t0 in enumerate(SCENE_TYPES):
            for j, t1 in enumerate(SHAPE_TYPES):
                image_dir = os.path.join("appearance", "object_mask_frame", t1, t0)
                for file in os.listdir(image_dir):
                    image = torch.load(os.path.join(image_dir, file))
                    target = torch.zeros(size=(image.size()[0],))
                    target.fill_(j)
                    image_tensor.append(image)
                    target_tensor.append(target)
        self.data = torch.cat(image_tensor)
        self.targets = torch.cat(target_tensor)
        print(self.data.size())
        print(self.targets.size())
        assert self.data.size()[0] == self.targets.size()[0]

    def __getitem__(self, index):
        return (self.data[index], self.targets[index])

    def __len__(self):
        return self.data.size()[0]


class TripletObjects(Dataset):
    """
    Train: For each sample (anchor) randomly chooses a positive and negative samples
    Test: Creates fixed triplets for testing
    """

    def __init__(self, object_dataset):
        self.object_dataset = object_dataset
        self.transform = None

        self.train_labels = self.object_dataset.targets
        self.train_data = self.object_dataset.data
        self.labels_set = set(self.train_labels.numpy())
        self.label_to_indices = {label: np.where(self.train_labels.numpy() == label)[0] for label in self.labels_set}


    def __getitem__(self, index):
        img1, label1 = self.train_data[index], self.train_labels[index].item()
        positive_index = index
        while positive_index == index:
            positive_index = np.random.choice(self.label_to_indices[label1])
        negative_label = np.random.choice(list(self.labels_set - set([label1])))
        negative_index = np.random.choice(self.label_to_indices[negative_label])
        img2 = self.train_data[positive_index]
        img3 = self.train_data[negative_index]

        return (img1, img2, img3), []

    def __len__(self):
        return len(self.object_dataset)

if __name__ == "__main__":
    dataset = Objects()
    print(len(dataset))

