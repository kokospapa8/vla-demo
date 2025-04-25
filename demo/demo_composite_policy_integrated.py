import argparse
import time
from typing import Dict, List, Union
import imageio
import numpy as np

import robosuite as suite
from robosuite.controllers import load_composite_controller_config
from robosuite.robots import ROBOT_CLASS_MAPPING
from robosuite.utils.robot_composition_utils import create_composite_robot

# Stable Baselines3
from stable_baselines3 import PPO
from robosuite.wrappers import GymWrapper
from gymnasium.wrappers import FlattenObservation

import os
print("MUJOCO_GL =", os.environ.get("MUJOCO_GL"))

def create_env(env_name: str, robot_name: str,
               controller_config: Dict, headless: bool,
               use_camera_obs: bool):
    config = {
        "env_name": env_name,
        "robots": robot_name,
        "controller_configs": controller_config,
        "has_renderer": False,
        "has_offscreen_renderer": use_camera_obs,  # ✅ 항상 True (camera obs를 위해)
        "ignore_done": False,
        "use_camera_obs": use_camera_obs,
        "camera_names": ["agentview"],
        "camera_heights": 64,
        "camera_widths": 64,
        "camera_depths": False,
        "reward_shaping": True,
        "control_freq": 20,
    }
    return FlattenObservation(GymWrapper(suite.make(**config)))

def train_policy(env, model_path, total_timesteps=100_000):
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./tb_logs/")
    model.learn(total_timesteps=total_timesteps)
    model.save(model_path)
    return model

def run_policy(env, model, headless):
    frames = []
    obs = env.reset()
    if isinstance(obs, tuple):
        obs = obs[0]

    for _ in range(200):
        action, _ = model.predict(obs, deterministic=True)
        step_result = env.step(action)

        if len(step_result) == 5:
            obs, reward, terminated, truncated, info = step_result
            done = terminated or truncated
        else:
            obs, reward, done, info = step_result

        if isinstance(obs, tuple):
            obs = obs[0]

        # frame = env.render(mode="rgb_array")  # or env.sim.render(...)
        # frame = env.unwrapped.render(mode="rgb_array")
        frame = env.env.env.sim.render(
            width=512,
            height=512,
            camera_name="birdview",
            depth=False
        )
        frames.append(frame)

        # if not headless:
        #     env.render()

        if done:
            obs = env.reset()
            if isinstance(obs, tuple):
                obs = obs[0]

    env.close()
    imageio.mimsave("out/demo.gif", frames, fps=30)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", type=str, required=True)
    parser.add_argument("--base", type=str, default=None)
    parser.add_argument("--grippers", nargs="+", type=str, default=["PandaGripper"])
    parser.add_argument("--env", type=str, default="Lift")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--timesteps", type=int, default=250_000)
    parser.add_argument("--run_only", action="store_true")
    parser.add_argument("--model_path", type=str, default="../models/ppo_lift_vla_model")

    args = parser.parse_args()

    if args.robot not in ROBOT_CLASS_MAPPING:
        raise ValueError(f"Robot {args.robot} not found in ROBOT_CLASS_MAPPING \n" f"{ROBOT_CLASS_MAPPING.keys()}")

    name = f"Custom{args.robot}"
    create_composite_robot(name, base=args.base, robot=args.robot, grippers=args.grippers)
    controller_config = load_composite_controller_config(controller="BASIC", robot=name)
    use_camera_obs = True
    print("use_camera_obs", use_camera_obs)
    env = create_env(args.env, name, controller_config, headless=args.headless, use_camera_obs=use_camera_obs)

    if args.run_only:
        model = PPO.load(args.model_path)
        run_policy(env, model, args.headless)
    else:
        model = train_policy(env, args.model_path, args.timesteps)
        run_policy(env, model, args.headless)
