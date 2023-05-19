
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
import gym


env = gym.make("layoutenv:LayoutEnv-v3")
model = PPO.load(r"models\PPO_sb_6\19200.zip", env=env, device='cpu')

# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

# print(f"{mean_reward = }")
# print(f"{std_reward = }")


vec_env = model.get_env()

for episode in range(20):
    obs = vec_env.reset()

    done = False
    while not done:
        action, _states = model.predict(obs)
        print(f"{action = }")
        obs, rewards, dones, info = vec_env.step(action)
        done = dones[0]
        print(f"{done = }")
        print(f"{info = }")
