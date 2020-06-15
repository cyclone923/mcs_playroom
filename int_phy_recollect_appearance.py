from gym_ai2thor.envs.mcs_env import McsEnv
from int_phy.object_state import ObjectState, pre_process_cropped_img, IMAGE_CROP_SIZE, get_object_match_pixels
from PIL import Image
import numpy as np
import torch
import os, sys

SHAPE_TYPES = ["cylinder", "sphere", "cube"]
# all_scene = ["object_permanence", "shape_constancy", "spatio_temporal_continuity"]
all_scene = ["object_permanence"]

SAVE_SCENE_LENGTH = 1
TOTAL_SCENE = 3 # max 1080
assert TOTAL_SCENE % SAVE_SCENE_LENGTH == 0
N_RESTART = TOTAL_SCENE // SAVE_SCENE_LENGTH

if __name__ == "__main__":

    for scene_type in all_scene:
        for _, shape_type in enumerate(SHAPE_TYPES):
            os.makedirs(os.path.join("appearance", "object_mask_frame", shape_type ,scene_type), exist_ok=True)

        start_scene_number = 0
        for n_restart in range(N_RESTART):

            object_frames = {}
            for _, shape_type in enumerate(SHAPE_TYPES):
                object_frames[shape_type] = []

            env = McsEnv(task="intphys_scenes", scene_type=scene_type, start_scene_number=start_scene_number)
            start_scene_number += SAVE_SCENE_LENGTH
            for _ in range(SAVE_SCENE_LENGTH):
                env.reset(random_init=False)
                env_new_objects = []
                for obj in env.scene_config['objects']:
                    if "occluder" not in obj['id']:
                        env_new_objects.append(obj)
                for one_obj in env_new_objects:
                    env.scene_config['objects']  = [one_obj]
                    env.step_output = env.controller.start_scene(env.scene_config)
                    obj_in = False
                    for i, action in enumerate(env.scene_config['goal']['action_list']):
                        env.step(action=action[0])
                        if len(env.step_output.object_list) == 1:
                            obj_in = True
                            try:
                                obj_state = ObjectState(
                                    env.step_output.object_list[0], env.step_output.depth_mask_list[-1], env.step_output.object_mask_list[-1]
                                )
                                x_s = obj_state.edge_pixels['x_min']
                                x_e = obj_state.edge_pixels['x_max']
                                y_s = obj_state.edge_pixels['y_min']
                                y_e = obj_state.edge_pixels['y_max']
                                if x_s == 0 or y_s == 0 or x_e == env.step_output.camera_aspect_ratio[0] - 1 or x_e == env.step_output.camera_aspect_ratio[1] - 1:
                                    continue
                                new_size = (IMAGE_CROP_SIZE, IMAGE_CROP_SIZE)
                                obj_frame = np.array(env.step_output.object_mask_list[-1])
                                pixels_on_frame = get_object_match_pixels(env.step_output.object_list[0].color, obj_frame)
                                obj_frame[:,:] = [255, 255, 255]
                                for x,y in pixels_on_frame:
                                    obj_frame[x,y,:] = [0, 0, 0]
                                obj_frame = obj_frame[y_s:y_e, x_s:x_e, :]
                                obj_frame = Image.fromarray(obj_frame).convert('L').resize(new_size)
                                # obj_frame.show()
                                obj_frame = np.array(obj_frame)
                                object_frames[one_obj['type']].append(pre_process_cropped_img(obj_frame))
                            except:
                                print("Unexpected error:\n {}".format(sys.exc_info()))
                        if obj_in and len(env.step_output.object_list) == 0:
                            break

            for _, shape_type in enumerate(SHAPE_TYPES):
                one_type_frames = object_frames[shape_type]
                if len(one_type_frames) == 0:
                    continue
                one_type_frames = torch.stack(one_type_frames)
                print(shape_type)
                print(one_type_frames.size())
                torch.save(one_type_frames, os.path.join("appearance", "object_mask_frame", shape_type, scene_type, "{}.pth".format(n_restart)))


            env.controller.end_scene(None, None)






