# Simulation to see if the model is working properly w/ results

import random

# total number of slots and simulations
totalSlots = 10000
simulations = 20000

# chosen number of send and listen slots
send_slots = 150
listen_slots = 150

# initiate the number of successes
successes = 0

# code needs to iterate over the total number of simulations and check if the send and listen slots overlap
for _ in range(simulations):
    # randomly select the send and listen slots
    sent_blocks = set(random.sample(range(totalSlots), send_slots))
    listen_blocks = set(random.sample(range(totalSlots), listen_slots))
    # check if the send and listen slots overlap
    if sent_blocks & listen_blocks:
        # if they do, increment the number of successes
        successes += 1

print(f"Success rate is : {(successes/simulations)*100}%")

print(f"Total time for send_receive_slots in 5 minutes: {(send_slots*30)/1000}s")
