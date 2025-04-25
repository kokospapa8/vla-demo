import argparse
import numpy as np
from stable_baselines3 import PPO
from robosuite import make
from robosuite.wrappers import GymWrapper
from gymnasium.wrappers import FlattenObservation

def add_language_to_obs(obs, instruction="Lift the block"):
    if isinstance(obs, dict):
        obs["language_instruction"] = instruction
    return obs


def run_saved_policy(env_name, robot_name, model_path, headless):
    # Create robosuite environment
    robosuite_env = make(
        env_name=env_name,
        robots=robot_name,
        has_renderer=not headless,
        has_offscreen_renderer=True,       # ✅ 카메라 쓰려면 무조건 True
        use_camera_obs=True,
        camera_names=["agentview"],
        camera_heights=84,
        camera_widths=84,
        camera_depths=False,
        reward_shaping=True,
        control_freq=20,
    )

    # Save initial environment state
    initial_state = robosuite_env.sim.get_state().flatten()
    np.save("../models/env_initial_state_load.npy", initial_state)

    # Wrap robosuite environment with Gym interface
    env = GymWrapper(robosuite_env)
    env = FlattenObservation(env)

    # ✅ 모델 불러오기
    model = PPO.load(model_path)

    # ✅ 실행 루프
    obs = env.reset()
    obs = add_language_to_obs(obs)
    if isinstance(obs, tuple):
        obs = obs[0]

    for _ in range(300):
        action, _ = model.predict(obs, deterministic=True)
        step_result = env.step(action)

        if len(step_result) == 5:
            obs, reward, terminated, truncated, info = step_result
            done = terminated or truncated
        else:
            obs, reward, done, info = step_result

        if isinstance(obs, tuple):
            obs = obs[0]

        if not headless:
            env.render()

        if done:
            obs = env.reset()
            if isinstance(obs, tuple):
                obs = obs[0]

    env.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--robot", type=str, required=True)
    parser.add_argument("--env", type=str, default="Lift")
    parser.add_argument("--model_path", type=str, default="../models/ppo_lift_vla_model")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    run_saved_policy(
        env_name=args.env,
        robot_name=args.robot,
        model_path=args.model_path,
        headless=args.headless,
    )
