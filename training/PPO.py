import os
from stable_baselines3 import PPO
from layoutenv.envs.sb_layout_env import LayoutEnv


models_dir = "models/PPO_sb_env"
logdir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

env = LayoutEnv()
env._render()

model = PPO("MlpPolicy", env, verbose=1)
TIMESTEPS = 500
for i in range(30):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO_sb_env")
    model.save(f"{models_dir}/{TIMESTEPS*i}")


# model = PPO.load("models//ppo_cartpole")
# env.render()
# obs = env.reset()
# done = False
# while not done:
#     action, _states = model.predict(obs)
#     obs, rewards, dones, info = env.step(action)
    