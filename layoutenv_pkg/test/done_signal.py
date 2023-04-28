from layoutenv.envs import LayoutEnv1

env = LayoutEnv1()
reward = 0
terminated = env._terminated(reward)

env.time_step = 30

assert env._terminated(0) == False, "Should return False"
assert env._terminated(1) == True, "Should return True"
assert env._terminated(2) == True, "Should return True"
assert env._truncated(30) == True, "Should return True"
assert env._truncated(33) == False, "Should return False"
assert env._truncated(15) == True, "Should return True"

# False | False
done = env._terminated(0) | env._truncated(33)
assert done == False

# True | False
done = env._terminated(1) | env._truncated(33)
assert done == True

# False | True
done = env._terminated(0) | env._truncated(15)
assert done == True

# True | True
done = env._terminated(2) | env._truncated(15)
assert done == True