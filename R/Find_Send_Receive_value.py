# The equation to determine how to get the probability of a given number of send and receive slots the minimal value of send and receive slots can be found assuming that the send and receive slots need to be equal and the probability of success should be over 98%.
import math


def ProbabilitySuccess(listens: int, sends: int, blocks: int):
    prob = listens / blocks
    sends = float(sends)
    prob = 1 - math.pow(1 - prob, sends)
    return prob


def MinNumberOfSendReceiveSlots(
    totalTimeForSuccessMS: int,
    numberOfRelays: int,
    blockSize: int,
    probability: float = 0.97,
):
    # calculate the number of blocks
    blocks = totalTimeForSuccessMS // blockSize

    blocks = blocks // numberOfRelays

    for _ in range(1, blocks):
        # now we run the probability values from 1 to the total number of simulations and create a list of probabilities
        prob = ProbabilitySuccess(_, _, blocks)
        # check if the probability is greater than 97%
        if prob > 0.97:
            # if it is, return the number of send and receive slots
            return _, _

    return "No solution found"


# total number of slots and simulations
minSendReceive = MinNumberOfSendReceiveSlots(300_000, 30, 3, 0.97)

print(f"Minimum number of send and receive slots: {minSendReceive}")
