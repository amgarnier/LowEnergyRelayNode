import numpy as np

# Constants
total_time_ms = 300000
sender_time_ms = 3
sender_blocks = np.arange(1, 2001)  # 1 to 2000
receiver_time_ms = 30
prob_success_total = 0.98
simulations = 1000

# Calculate probability of detection in one receiver block
prob_detection_one_rec = (sender_blocks * sender_time_ms) / total_time_ms

# Calculate the number of receiver blocks for a given success probability
receiver_blocks = np.log(1 - prob_success_total) / np.log(1 - prob_detection_one_rec)

# Assuming we want the send and receive times to be the same
prob = 1 - (1 - prob_detection_one_rec) ** (
    sender_blocks * (receiver_time_ms / sender_time_ms)
)

# Find when the probability first exceeds 0.98
i = 0
for element in prob:
    if element > prob_success_total:
        print(f"Index when probability exceeds 0.98: {i}")
        break
    i += 1


# assume 173 listen messages and 1730 send blocks
