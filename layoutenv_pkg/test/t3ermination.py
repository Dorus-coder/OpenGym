import unittest
from layoutenv.envs.sb_layout_env import terminated

class TestMyTerminationFunction(unittest.TestCase):
    def test_termination(self):
        # Test case 1: Negative first reward, positive second reward, and num_neg_rewards >= num_pos_rewards
        rewards1 = [-1, 1, -1, -1, 1, 1, -1]
        self.assertTrue(terminated(rewards1))
        
        # Test case 2: Negative first reward, positive second reward, but num_neg_rewards < num_pos_rewards
        rewards2 = [-1, 1, -1, -1, 1, 1, -1, 1]
        self.assertFalse(terminated(rewards2))
        
        # Test case 3: No negative rewards
        rewards3 = [1, 1, 1, 1, 1]
        self.assertFalse(terminated(rewards3))
        
        # Test case 4: More positive rewards than negative rewards
        rewards4 = [-1, 1, 1, 1, -1, 1]
        self.assertFalse(terminated(rewards4))
        
        # Test case 5: More negative rewards than positive rewards
        rewards5 = [-1, 1, -1, 1, -1, 1, -1]
        self.assertTrue(terminated(rewards5))


TestMyTerminationFunction()
print('test succesfull')