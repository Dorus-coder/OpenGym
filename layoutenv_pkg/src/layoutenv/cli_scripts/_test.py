from stable_baselines3 import PPO
import stable_baselines3
import gym
import os


if __name__ == "__main__":
    env = gym.make("layoutenv:LayoutEnv-v3")
    env.seed(0)
    stable_baselines3.common.utils.set_random_seed(0)

    from stable_baselines3 import PPO
    model = PPO("MlpPolicy", n_epochs=1 env, verbose=1, n_steps=20, batch_size=2, n_epochs=1)
    model.learn(total_timesteps=1)  # 000)
    obs = env.reset()
    for _ in range(1):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
