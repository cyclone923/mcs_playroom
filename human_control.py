from gym_ai2thor.envs.mcs_env import McsEnv
import numpy as np

class McsHumanControlEnv(McsEnv):
    def __init__(self,  **args):
        super().__init__(**args)
        self.hand_object = None

    def step(self, action_str, **args):
        print("Action you entered: {} {}".format(action_str, args))
        if "Move" in action_str:
            self.step_output = self.controller.step(action=action_str)
        elif "Look" in action_str:
            if action_str == "LookUp":
                self.step_output = self.controller.step(action="RotateLook", **args)
            elif action_str == "LookDown":
                self.step_output = self.controller.step(action="RotateLook", **args)
            else:
                raise NotImplementedError
        elif "Rotate" in action_str:
            if action_str == "RotateLeft":
                self.step_output = self.controller.step(action="RotateLook", **args)
            elif action_str == "RotateRight":
                self.step_output = self.controller.step(action="RotateLook", **args)
            else:
                self.step_output = self.controller.step(action="RotateObject", objectId=args['objectId'], rotationY=10)
        elif action_str == "PickupObject":
            self.step_output = self.controller.step(action="PickupObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = args['objectId']
        elif action_str == "PutObject":
            args["objectId"] = self.hand_object
            self.step_output = self.controller.step(action="PutObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = None
        elif action_str == "DropObject":
            args["objectId"] = self.hand_object
            self.step_output = self.controller.step(action="DropObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = None
        elif action_str == "ThrowObject":
            args["objectId"] = self.hand_object
            self.step_output = self.controller.step(action="ThrowObject", **args)
            if self.step_output.return_status == "SUCCESSFUL":
                self.hand_object = None
        elif action_str == "PushObject":
            self.step_output = self.controller.step(action="PushObject", **args)
        elif action_str == "PullObject":
            self.step_output = self.controller.step(action="PullObject", **args)
        elif action_str == "OpenObject":
            self.step_output = self.controller.step(action="OpenObject", **args)
        elif action_str == "CloseObject":
            self.step_output = self.controller.step(action="CloseObject", **args)
        else:
            self.step_output = self.controller.step(action=action_str)


    def print_step_output(self):
        print("- " * 20)
        print("Previous Action Status: {}".format(self.step_output.return_status))
        if hasattr(self.step_output, "reward"):
            print("Previous Reward: {}".format(self.step_output.reward))
        print(
            "Agent at: ({:.2f}, {:.2f}, {:.2f}), HeadTilt: {:.2f}, Rotation: {:.2f}, HandObject: {}".format(
                self.step_output.position['x'],
                self.step_output.position['y'],
                self.step_output.position['z'],
                self.step_output.head_tilt,
                self.step_output.rotation,
                self.hand_object
            )
        )
        print("Camera Field of view {}".format(self.step_output.camera_field_of_view))
        print("Visible Objects:")
        for obj in self.step_output.object_list:
            print("Distance {:.3f} to {} ({:.3f},{:.3f},{:.3f})".format(
                obj.distance_in_world, obj.uuid, obj.position['x'], obj.position['y'], obj.position['z'])
            )

        for obj in self.step_output.structural_object_list:
            if "wall" not in obj.uuid:
                continue
            print("Distance {:.3f} to {} ({:.3f},{:.3f},{:.3f})".format(
                obj.distance_in_world, obj.uuid, obj.position['x'], obj.position['y'], obj.position['z'])
            )
            # for one_dim in obj.dimensions:
            #     print(one_dim)









if __name__ == '__main__':
    env = McsHumanControlEnv(task="interaction_scenes", scene_type="traversal", start_scene_number=0)
    env.reset()

    while True:
        env.print_step_output()
        print("- "*10)
        action = input("Enter Action: ")
        if action == "w":
            env.step("MoveAhead", amount=0.5)
        elif action == "s":
            env.step("MoveBack", amount=0.5)
        elif action == "a":
            env.step("MoveLeft", amount=0.5)
        elif action == "d":
            env.step("MoveRight", amount=0.5)
        elif action == "q":
            # rt = input("RotateLeft! Enter the rotation: ")
            rt = 10
            env.step("RotateLeft", rotation=-float(rt))
        elif action == "e":
            # rt = input("RotateRight! Enter the rotation: ")
            rt = 10
            env.step("RotateRight", rotation=float(rt))
        elif action == "r":
            hrz = input("Look Up! Enter the horizon: ")
            env.step("LookUp", horizon=-float(hrz))
        elif action == "f":
            hrz = input("Look Down! Enter the horizon: ")
            env.step("LookDown", horizon=float(hrz))
        elif action == "U":
            obj = input("Pickup Object! Enter the object ID: ")
            env.step("PickupObject", objectId=obj)
        elif action == "I":
            rec = input("Put Object! Enter the receptacle ID: ")
            env.step("PutObject", receptacleObjectId=rec)
        elif action == "O":
            print("Drop Object!")
            env.step("DropObject")
        elif action == "P":
            print("Throw Object!")
            force = input("Throw Object! Enter the force: ")
            env.step("ThrowObject", force=int(force), objectDirectionY=env.step_output.head_tilt)
        elif action == "J":
            obj = input("Push Object! Enter the object ID: ")
            env.step("PushObject", objectId=obj)
        elif action == "K":
            obj = input("Pull Object! Enter the object ID: ")
            env.step("PullObject", objectId=obj)
        elif action == "L":
            obj = input("Rotate Object! Enter the object ID: ")
            env.step("RotateObject", objectId=obj)
        elif action == "N":
            obj = input("Open Object! Enter the object ID: ")
            env.step("OpenObject", objectId=obj)
        elif action == "M":
            obj = input("Close Object! Enter the object ID: ")
            env.step("CloseObject", objectId=obj)
        elif action == "Y":
            action_command = input("Input pose action:")
            env.step(action_command)
        elif action == "z":
            break
        else:
            print("Invalid Action")












