from a3c.policy import ResNetPolicy

import numpy as np
from skimage import transform
import torch
from gym.spaces import Box
from copy import deepcopy

import torch
torch.set_printoptions(profile="full", precision=5, linewidth=5000)
torch.set_printoptions()

class ObeserationSpace:
    def __init__(self):
        self.spaces = {}

class TaskResNet:

    RESOLUTION = (256, 256)

    def __init__(self, rgb_sensor, depth_sensor):
        self.observation_spaces = ObeserationSpace()
        self.actor_critic = None

        if rgb_sensor:
            self.observation_spaces.spaces['rgb'] = \
                Box(
                    low=0, high=255, dtype=np.uint8, shape=(self.RESOLUTION[0], self.RESOLUTION[1], 3)
                )
        if depth_sensor:
            self.observation_spaces.spaces['depth'] = \
                Box(
                    low=0, high=255, dtype=np.uint8, shape=(self.RESOLUTION[0], self.RESOLUTION[1], 1)
                )

    def set_up_resnet_actor_critic(self, action_space, goal_sensor_uuid, **kwargs):
        self.actor_critic = ResNetPolicy(
            self.observation_spaces,
            action_space,
            goal_sensor_uuid,
            **kwargs
        )

    def act(self, obs, hidden_states, prev_action, mask, deterministic=False):
        _, action, _, rnn_hidden_states = self.actor_critic.act(
            obs, hidden_states, prev_action, mask, deterministic=deterministic
        )
        return action[0].item(), rnn_hidden_states

    def load_checkpoint(self, checkpoint_path):
        ckpt = torch.load(checkpoint_path, map_location='cpu')
        # self.actor_critic.load_state_dict(ckpt)
        self.actor_critic.load_state_dict(
            {
                k[len("actor_critic."):]: v
                for k, v in ckpt["state_dict"].items()
                if "actor_critic" in k
            },
        )

    def preprocess(self, img, img_name):
        # img = deepcopy(img)
        img = np.array(img)
        img = img.astype(np.float32) / 256
        if img_name == 'rgb':
            img = img.astype(np.float32) / 256
        else:
            img = img.astype(np.float32) / 256
            img = torch.tensor(img).unsqueeze(0).unsqueeze(0)
            img = torch.nn.functional.interpolate(img, size=(256, 256))
            img = img.squeeze().unsqueeze(-1)
        return img


























