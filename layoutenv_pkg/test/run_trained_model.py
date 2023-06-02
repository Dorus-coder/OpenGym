from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
import gym


env = gym.make("layoutenv:LayoutEnv-v3")


#peek of run 2
model = PPO.load(r"models\PPO_sb_env6\2560.zip", env=env, device='cpu')
# model = TD3.load(r"models\TD3_sb_env4\7500.zip", env=env, device='cpu')
# model = PPO.load(r"models\PPO_sb_env6\30720.zip", env=env, device='cpu')


# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
# print(f"{mean_reward = }")
# print(f"{std_reward = }")

vec_env = model.get_env()


obs = vec_env.reset()



done = False

while not done:

    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, dones, info = vec_env.step(action)
  
    done = dones[0]


print(f"done {done}") 