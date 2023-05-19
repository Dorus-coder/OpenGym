import numpy as np
import random

random.seed(10)
np.random.seed(1)

for val in range(20):
    print(f"{random.random() = }")
    print(f"{np.random.random() = }")
print("next loop")
random.seed(10)
np.random.seed(1)
for val in range(20):
    print(f"{random.random() = }")
    print(f"{np.random.random() = }")