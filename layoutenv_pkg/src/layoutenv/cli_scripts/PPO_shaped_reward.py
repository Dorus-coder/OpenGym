from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import StopTrainingOnRewardThreshold, EvalCallback
from stable_baselines3.common.logger import configure
import gym
import os
import layoutenv.utils as lutils

ALG  = "PPO"
run = 6

models_dir = f"C:\\Dorus\\models\\{ALG}_sb_env{run}"
logdir = "logs"
tmp_path = f"tmp/sb3_log_{run}/"
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

n_steps = 128
n_envs = 1
n_epochs = 5
initial_val_learning_rate = 0.003

# model = PPO(policy="MlpPolicy", 
#             n_epochs=n_epochs, 
#             n_steps=n_steps, 
#             env=env, 
#             device="cpu", 
#             tensorboard_log=logdir, 
#             verbose=1,
#             batch_size=n_steps*n_envs,
#             learning_rate=lutils.linear_schedule(initial_val_learning_rate))

model = PPO.load(r"models\PPO_sb_env6\3200.zip", env=env, device='cpu')
model.set_logger(new_logger)

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

TIMESTEPS = n_steps * n_envs * n_epochs
for i in range(26, 1000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env{run}", callback=eval_callback)
    model.save(f"{models_dir}/{TIMESTEPS*i}")



