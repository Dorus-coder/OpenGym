from stable_baselines3 import A2C, PPO
from stable_baselines3.common.evaluation import evaluate_policy
import gym
import os

pp = PPO.load()

ALG  = "A2C"
run = 3
models_dir = f"models/{ALG}_sb_env{run}"
logdir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

env = gym.make(f"layoutenv:LayoutEnv-v{3}")
env.render(mode="noHMI")

model = A2C("MlpPolicy", env, device="cpu", tensorboard_log=logdir)
# model= A2C.load(f"{models_dir}\\41400", env=env)

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

TIMESTEPS = 100
for i in range(400, 1000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env{run}")
    model.save(f"{models_dir}/{TIMESTEPS*i}")


