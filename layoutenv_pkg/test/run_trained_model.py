from stable_baselines3 import A2C
import gym


env = gym.make("layoutenv:LayoutEnv-v3")
model = A2C.load(r"models\PPO_sb_env6\30720.zip", env=env, device='cpu')

vec_env = model.get_env()

obs = vec_env.reset()

done = False

while not done:

    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, dones, info = vec_env.step(action)
  
    done = dones[0]


