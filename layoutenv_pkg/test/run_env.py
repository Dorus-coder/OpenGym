import gym

env = gym.make("layoutenv:LayoutEnv-v3")


number_of_episodes = 5
total_reward = []
env.render(mode="GUIviewer")

for episode in range(number_of_episodes):
    ob = env.reset()
    
    done = False
    while not done:

        action = env.action_space.sample()
        obs, reward, done, info = env.step(action)