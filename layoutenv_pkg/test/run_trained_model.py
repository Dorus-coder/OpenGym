from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
import gym


env = gym.make("layoutenv:LayoutEnv-v3")

model = PPO.load(r"models\PPO_sb_env4\3840.zip", env=env, device='cpu')


mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)
print(f"{mean_reward = }")
print(f"{std_reward = }")

vec_env = model.get_env()

obs = vec_env.reset(seed=1)

done = False

while not done:
    for i in range(15):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = vec_env.step(action)
        done = dones[0]
        print(f"{action = }")
        print(f"{rewards = }")
        print(f"{info = }")

print(done)