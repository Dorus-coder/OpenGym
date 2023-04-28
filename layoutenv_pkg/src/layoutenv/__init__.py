from gym.envs.registration import register

register(id="LayoutEnv-v2", entry_point="layoutenv.envs:LayoutEnv2",
    # Max number of steps per episode, using a `TimeLimitWrapper`
    max_episode_steps=50,
)

register(id="LayoutEnv-v3", entry_point="layoutenv.envs:LayoutEnv3",
    # Max number of steps per episode, using a `TimeLimitWrapper`
    max_episode_steps=50,
)