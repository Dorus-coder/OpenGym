from stable_baselines3 import A2C
from stable_baselines3.common.evaluation import evaluate_policy
import gym
import os

ALG  = "A2C"

models_dir = f"models/{ALG}_sb_env"
logdir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)



env = gym.make("layoutenv:LayoutEnv-v1")
env.render(mode="noHMI")

model = A2C("MlpPolicy", env, device="cpu", tensorboard_log=logdir)
model= A2C.load("models\\A2C_sb_env\\250.zip", env=env)

mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
print(f"{mean_reward = }")
print(f"{std_reward = }")

TIMESTEPS = 50
for i in range(6, 10):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env")
    model.save(f"{models_dir}/{TIMESTEPS*i}")


