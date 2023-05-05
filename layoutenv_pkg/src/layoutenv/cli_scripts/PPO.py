from stable_baselines3 import PPO
import gym
import os

ALG  = "PPO"
run = 1

models_dir = f"C:\\Dorus\\models\\{ALG}_sb_env{run}"
logdir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logdir):
    os.makedirs(logdir)

env = gym.make("layoutenv:LayoutEnv-v3")

n_steps = 128
n_envs = 1
n_epochs = 3

model = PPO(policy="MlpPolicy", 
            n_epochs=n_epochs, 
            n_steps=n_steps, 
            env=env, 
            device="cpu", 
            tensorboard_log=logdir, 
            verbose=1,
            batch_size=n_steps*n_envs)

# model = A2C(policy="MlpPolicy", env=env, device="cpu", tensorboard_log=logdir, verbose=1)

# model= A2C.load(f"{models_dir}\\41400", env=env)

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

TIMESTEPS = n_steps * n_envs * n_epochs
for i in range(1000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"{ALG}_sb_env{run}")
    model.save(f"{models_dir}/{TIMESTEPS*i}")



