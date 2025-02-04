import math

# Configuration
TOTAL_TIME_MS = 300_000  # 5 minutes
SEND_BLOCK_SIZE = 5  # 5 ms per send block
RECEIVE_BLOCK_SIZE = 30  # 30 ms per receive block
TOTAL_SEND_SLOTS = TOTAL_TIME_MS // SEND_BLOCK_SIZE  # 60,000 slots
TOTAL_LISTEN_SLOTS = TOTAL_TIME_MS // RECEIVE_BLOCK_SIZE  # 10,000 slots
TARGET_PROBABILITY = 0.97  # Desired probability


def probability_of_success(S, L, N_s):
    """Computes the probability using binomial approximation."""
    return 1 - (1 - L / N_s) ** S


def find_minimum_blocks():
    """Finds the minimum send & listen blocks using direct probability calculation."""
    for send_blocks in range(1, TOTAL_SEND_SLOTS):  # Step in 10s for efficiency
        listen_blocks = (
            send_blocks * SEND_BLOCK_SIZE
        ) // RECEIVE_BLOCK_SIZE  # Keep active times equal

        if listen_blocks > TOTAL_LISTEN_SLOTS or listen_blocks <= 0:
            continue

        prob = probability_of_success(send_blocks, listen_blocks, TOTAL_SEND_SLOTS)

        if prob >= TARGET_PROBABILITY:
            return send_blocks, listen_blocks, prob  # Return first valid solution

    return None  # No valid configuration found


# Run optimization
result = find_minimum_blocks()

# Print results
if result:
    send_blocks, listen_blocks, probability = result
    print(f"Minimum Send Blocks: {send_blocks}")
    print(f"Minimum Listen Blocks: {listen_blocks}")
    print(f"Success Probability: {probability:.4f}")
else:
    print("No valid configuration found!")
