from stable_baselines3 import PPO
from stable_baselines3.ppo import PPO as P
import gym
import os

PPO
P

ALG  = "PPO"
run = 1

models_dir = f"C:\\Users\\cursist\\Dorus\\OpenGym\\models\\{ALG}_sb_env{run}"
logdir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

env = gym.make("layoutenv:LayoutEnv-v3")
env.render(mode="noHMI")

model = PPO("MlpPolicy", env, device="cpu", tensorboard_log=logdir, verbose=1)
# model= A2C.load(f"{models_dir}\\41400", env=env)

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

TIMESTEPS = 1
for i in range(3):
    print("LEARNING !!!")
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env{run}")
    print("SAVING !!!")
    model.save(f"{models_dir}/{TIMESTEPS*i}")
    print("Model saved !!!!!!!!!!!!!!!!!!!!!!!!!!!!")


