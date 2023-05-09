from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import StopTrainingOnRewardThreshold, EvalCallback
from stable_baselines3.common.logger import configure
import gym
import os
import datetime

ALG  = "PPO"
run = 2

models_dir = f"C:\\Dorus\\models\\{ALG}_sb_env{run}"
logdir = "logs"
tmp_path = "tmp/sb3_log/"
new_logger = configure(tmp_path, ["stdout", "csv", "tensorboard"])


if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

env = gym.make("layoutenv:LayoutEnv-v3")
callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=10, verbose=1)
eval_callback = EvalCallback(env, callback_on_new_best=callback_on_best, verbose=1)

n_steps = 256
n_envs = 1
n_epochs = 5

# with open(f"training_parameters\\{ALG}_{run}", 'w') as txt_file:
#     txt_file.write(f"training run {run} on {datetime.datetime.now()}\n"
#                    f'\tn_steps: {n_steps}\n'
#                    f"\tn_envs: {n_envs}\n"
#                    f"\tn_epochs: {n_epochs}\n"          
#                    )

# model = PPO(policy="MlpPolicy", 
#             n_epochs=n_epochs, 
#             n_steps=n_steps, 
#             env=env, 
#             device="cpu", 
#             tensorboard_log=logdir, 
#             verbose=1,
#             batch_size=n_steps*n_envs)

model = PPO.load(r"models\PPO_sb_env2\24320.zip", env=env, device='cpu')
model.set_logger(new_logger)

# model= A2C.load(f"{models_dir}\\41400", env=env)

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

TIMESTEPS = n_steps * n_envs * n_epochs
for i in range(1, 1000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env{run}", callback=eval_callback)
    model.save(f"{models_dir}/{TIMESTEPS*i}")



