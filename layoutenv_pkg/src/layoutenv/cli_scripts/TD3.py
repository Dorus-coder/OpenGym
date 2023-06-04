from stable_baselines3 import TD3
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import StopTrainingOnRewardThreshold, EvalCallback
from stable_baselines3.common.logger import configure
import layoutenv.utils as lutils 
import numpy as np
import gym
import os

ALG  = "TD3"
run = "5/5_6"

models_dir = f"C:\\Dorus\\models\\{ALG}_sb_env{run}"
logdir = "logs"
tmp_path = f"tmp/sb3_log_{ALG}/run_{run}/"
new_logger = configure(tmp_path, ["stdout", "csv", "tensorboard", "log"])

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(logdir):
    os.makedirs(logdir)
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

env = gym.make("layoutenv:LayoutEnv-v3")
env.seed(1)

callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=10, verbose=1)
eval_callback = EvalCallback(env, callback_on_new_best=callback_on_best, verbose=1)
# action_noise = NormalActionNoise(mean=np.array([0]), sigma=np.array([0.1]))
action_noise = NormalActionNoise(mean=np.array([0]), sigma=np.array([0.8]))

initial_val_learning_rate = 0.003

# model = TD3(policy="MlpPolicy", 
#             env=env, 
#             device="cpu", 
#             tensorboard_log=logdir, 
#             verbose=1,
#             learning_rate=initial_val_learning_rate,
#             seed=1,
#             action_noise=action_noise)

model = TD3.load(r"models\TD3_sb_env5\5_4\5000.zip", env=env, device='cpu')

model.set_logger(new_logger)

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

TIMESTEPS = 500
for i in range(1, 1000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env{run}", callback=eval_callback)
    model.save(f"{models_dir}/{TIMESTEPS*i}")



