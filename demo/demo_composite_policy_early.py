import argparse
import time
from typing import Dict, List, Union

import numpy as np

import robosuite as suite
from robosuite.controllers import load_composite_controller_config
from robosuite.robots import ROBOT_CLASS_MAPPING
from robosuite.utils.robot_composition_utils import create_composite_robot

# Stable Baselines3
from stable_baselines3 import PPO
from robosuite.wrappers import GymWrapper
from gymnasium.wrappers import FlattenObservation

# Vision-language stub (for demonstration)
def add_language_to_obs(obs, instruction="Lift the block"):
    if isinstance(obs, dict):
        obs["language_instruction"] = instruction
    return obs

def create_and_train_policy(
    env: str,
    robots: Union[str, List[str]],
    controller_config: Dict,
    total_timesteps: int = 100_000,
    headless: bool = True,
):
    config = {
        "env_name": env,
        "robots": robots,
        "controller_configs": controller_config,
        "has_renderer": not headless,
        "has_offscreen_renderer": headless,
        "ignore_done": False,
        "use_camera_obs": True,
        "camera_names": ["agentview"],
        "camera_heights": 84,
        "camera_widths": 84,
        "camera_depths": False,
        "reward_shaping": True,
        "control_freq": 20,
    }

    # Create robosuite environment
    robosuite_env = suite.make(**config)

    # Save initial environment state
    initial_state = robosuite_env.sim.get_state().flatten()
    np.save("../models/env_initial_state_early.npy", initial_state)

    # Wrap robosuite environment with Gym interface
    env = GymWrapper(robosuite_env)
    env = FlattenObservation(env)

    # Create and train PPO model (with early stopping simulation)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./tb_logs/")
    model.learn(total_timesteps=10_000)  # Early stop to quickly test the rest of the code
    model.save("../models/ppo_lift_vla_model")

    # Evaluation run
    obs = env.reset()
    obs = add_language_to_obs(obs)
    if isinstance(obs, tuple):
        obs = obs[0]  # unwrap obs if (obs, info)

    for _ in range(50):  # Shortened for test
        action, _states = model.predict(obs, deterministic=True)

        step_result = env.step(action)
        if len(step_result) == 5:
            obs, reward, terminated, truncated, info = step_result
            done = terminated or truncated
        else:
            obs, reward, done, info = step_result

        obs = add_language_to_obs(obs)
        if isinstance(obs, tuple):
            obs = obs[0]  # unwrap again if needed

        if not headless:
            env.render()

        if done:
            obs = env.reset()
            obs = add_language_to_obs(obs)
            if isinstance(obs, tuple):
                obs = obs[0]

    env.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--robot", type=str, required=True)
    parser.add_argument("--base", type=str, default=None)
    parser.add_argument("--grippers", nargs="+", type=str, default=["PandaGripper"])
    parser.add_argument("--env", type=str, default="Lift")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--timesteps", type=int, default=250_000)

    args = parser.parse_args()

    if args.robot not in ROBOT_CLASS_MAPPING:
        raise ValueError(f"Robot {args.robot} not found in ROBOT_CLASS_MAPPING \n" f"{ROBOT_CLASS_MAPPING.keys()}")

    name = f"Custom{args.robot}"
    create_composite_robot(name, base=args.base, robot=args.robot, grippers=args.grippers)
    controller_config = load_composite_controller_config(controller="BASIC", robot=name)

    create_and_train_policy(
        env="Lift",
        robots=name,
        controller_config=controller_config,
        total_timesteps=args.timesteps,
        headless=args.headless,
    )
