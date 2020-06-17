from int_phy_collect import SHAPE_TYPES
from torch.utils.data import Dataset
import torch
import os

N_TRAIN = 1600

def load_all_tensors(occluder_dir):
    occluder_tensor = []
    for t in SHAPE_TYPES:
        shape_dir = os.path.join("locomotion", "positions", occluder_dir, t)
        scene_dirs = os.listdir(shape_dir)
        for scene_dir in scene_dirs:
            scene_dir = os.path.join(shape_dir, scene_dir)
            tensor_files = os.listdir(scene_dir)
            for file in tensor_files:
                file = os.path.join(scene_dir, file)
                tensor = torch.load(file)
                occluder_tensor.append(tensor)
    return occluder_tensor


def get_train_test_dataset():
    with_occluder_tensor = torch.cat(load_all_tensors("with_occluder"))
    without_occluder_tensor = torch.cat(load_all_tensors("without_occluder"))
    assert with_occluder_tensor.size() == without_occluder_tensor.size()
    rand_permutation = torch.randperm(with_occluder_tensor.size()[0])
    without_occluder_tensor = without_occluder_tensor[rand_permutation]
    with_occluder_tensor = with_occluder_tensor[rand_permutation]
    train_set = TuplePositions(with_occluder_tensor[:N_TRAIN], without_occluder_tensor[:N_TRAIN])
    test_set = TuplePositions(with_occluder_tensor[N_TRAIN:], without_occluder_tensor[N_TRAIN:])
    return train_set, test_set


class TuplePositions(Dataset):
    def __init__(self, with_occluder, without_occluder):
        self.with_occluder_tensor = with_occluder
        self.without_occluder_tensor = without_occluder
        print(self.with_occluder_tensor.size(), self.without_occluder_tensor.size())
        assert self.with_occluder_tensor.size() == self.without_occluder_tensor.size()

    def __getitem__(self, index):
        return (self.with_occluder_tensor[index], self.without_occluder_tensor[index])

    def __len__(self):
        return self.with_occluder_tensor.size()[0]



if __name__ == "__main__":
    dataset = get_train_test_dataset()
