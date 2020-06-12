from gym_ai2thor.envs.mcs_env import McsEnv
from meta_ontroller.meta_controller import MetaController
import sys


from frame_colletor import FrameCollector
# from array2gif import write_gif

if __name__ == "__main__":
    # c = FrameCollector()

    env = McsEnv(task="interaction_scenes", scene_type="transferral_next_to", start_scene_number=53)
    metaController = MetaController(env)

    while env.current_scene < len(env.all_scenes) - 1:
        env.reset()
        # print(env.current_scene)
        metaController.get_inital_planner_state()
        result = metaController.excecute()
        sys.stdout.flush()
        exit(0)
    # print(len(c.frames))
    # write_gif(c.frames, 'original.gif', fps=5)


