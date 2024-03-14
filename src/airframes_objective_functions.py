import numpy as np
import subprocess

def _target_LQR_control(target, render:bool):

    aerial_gym_dev_path="/home/paran/Dropbox/aerial_gym_dev/aerial_gym_dev"
    import sys
    import isaacgym
    sys.path.append(aerial_gym_dev_path)
    from aerial_gym_dev import AERIAL_GYM_ROOT_DIR
    file_path = AERIAL_GYM_ROOT_DIR + "/resources/robots/generalized_aerial_robot/generalized_model_wrench.urdf"
    from aerial_gym_dev.utils.urdf_creator import create_urdf_from_model
    from aerial_gym_dev.utils.task_registry import task_registry
    from aerial_gym_dev.utils import get_args, task_registry
    import torch
    import aerial_gym_dev.envs.base.generalized_aerial_robot_config 
    import aerial_gym_dev.envs.base.generalized_aerial_robot

    assert type(target)==list
    assert len(target)==3

    task_registry.register("gen_aerial_robot", aerial_gym_dev.envs.base.generalized_aerial_robot.GenAerialRobot, aerial_gym_dev.envs.base.generalized_aerial_robot_config.GenAerialRobotCfg())

    args = get_args()
    args.num_envs = 1
    args.task = 'gen_aerial_robot'
    args.headless = not render

    env, env_cfg = task_registry.make_env(name=args.task, args=args)
    assert env_cfg.control.controller == "LQR_control"
    env_cfg.num_actions = 12
    
    command_actions = torch.tensor(target+[0.,0.,0.7,0.,0.,0.,0.,0.,0.], dtype=torch.float32)
    command_actions = command_actions.reshape((1,env_cfg.control.num_actions))
    command_actions = command_actions.repeat(env_cfg.env.num_envs,1)
    
    episode_length = 300
    reward_list = []
    obs_list = []
    for i in range(0, episode_length):
        obs, priviliged_obs, rewards, resets, extras = env.step(command_actions)

        if bool(resets.cpu()[0]): # stop if the airframe is reinitialized
            break

        if render:
            env.render()

        r = rewards[0].item()
        pose = np.array(obs['obs'].cpu())[0][0:7]
        reward_list.append(r)
        obs_list.append(pose)

    env.reset()
    return np.array(reward_list), np.array(obs_list)



def target_lqr_objective_function(pars, target):

    print("save parameters to robotConfigFile.txt")
    with open('/home/paran/Dropbox/NTNU/11_constraints_encoding/code/robotConfigFile.txt','w') as f:
        print('pars.cq=',pars.cq, file=f, flush=True)
        print('pars.frame_mass=',pars.frame_mass, file=f)
        print('pars.motor_masses=',pars.motor_masses, file=f)

        print('pars.motor_translations=',pars.motor_translations, file=f)
        print('pars.motor_orientations=',pars.motor_orientations, file=f)
        print('pars.motor_directions=',pars.motor_directions, file=f)

        print('pars.max_u=',pars.max_u, file=f)
        print('pars.min_u=',pars.min_u, file=f)

    target_str = '[' + ','.join([str(el) for el in target]) + ']'

    cmd_str = f"python src/airframes_objective_functions.py {target_str}"
    from datetime import datetime
    current_time = datetime.now()
    print(">>", cmd_str, current_time.strftime("%Y-%m-%d %H:%M:%S"))
    output = subprocess.check_output(cmd_str, shell=True, text=True)
    rewards = np.array(eval(output.split("result:")[-1].split("\n")[1]))
    poses = np.array(eval(output.split("result:")[-1].split("\n")[2]))

    return rewards, poses





if __name__ == '__main__':
    # Call objective function from subprocess. Assumes robotConfigFile.txt has been previously written.
    import sys
    assert len(sys.argv) == 2
    target = eval(sys.argv[1])
    res = _target_LQR_control(target, False)
    print("result:")
    print(res[0].tolist())
    print(res[1].tolist())