import math
import random


class prob_model:
    """
    This is the probability model which is used to determine the send or receive blocks for the device a
    """

    def __init__(
        self,
        total_time_before_success_ms: int = 300_000,
        number_of_relays: int = 2,
        block_size_ms: int = 30,
        probability: float = 0.97,
        send_blocks: list[int] = [],
    ):
        """
        Initialize the ProbModel class.

        Args:
            total_time_before_success_ms (int): Total time before success in milliseconds. Default is 300,000 ms.
            number_of_relays (int): Number of relays. Default is 2.
            block_size_ms (int): Size of each block in milliseconds. Default is 30 ms.
            probability (float): Probability of success. Default is 0.97.
            send_blocks (list[int]): List of blocks to send. Default is an empty list.
        """
        self._total_time_before_success_ms = total_time_before_success_ms
        self._number_of_relays = number_of_relays
        self._block_size = block_size_ms
        self._probability = probability
        self._send_blocks = send_blocks

    def probability_of_success(self, listens: int, sends: float, blocks: int):
        """
        Calculate the probability of success based on the number of listens, sends, and blocks.

        Args:
            listens (int): The number of listens.
            sends (float): The number of sends.
            blocks (int): The number of blocks.

        Returns:
            float: The calculated probability of success.
        """
        prob = listens / blocks
        prob = 1 - math.pow(1 - prob, sends)
        return prob

    def min_number_of_slots(self):
        """
        Calculate the minimum number of slots required to achieve a specified probability of success.

        This method calculates the minimum number of slots (listens and sends) needed to achieve a
        probability of success that meets or exceeds the specified threshold (_probability). It does
        this by iterating through possible slot counts and computing the probability of success for
        each count until the threshold is met or exceeded.

        Returns:
            int: The minimum number of slots required to achieve the specified probability of success.
        """
        blocks = self._total_time_before_success_ms // self._block_size
        blocks = blocks // self._number_of_relays
        for _ in range(1, blocks):
            prob = self.probability_of_success(listens=_, sends=_, blocks=blocks)
            if prob >= self._probability:
                return _

    def find_delay_values(self):
        """
        Calculate the delay values between consecutive send blocks and update the send blocks list.

        This method iterates through the list of send blocks, calculates the delay between each
        consecutive pair of blocks, and updates the send blocks list with these delay values.

        Returns:
            self: The instance of the class with the updated send blocks list.
        """
        new_table = []
        increment = 0
        for i in self._send_blocks:
            if increment < len(self._send_blocks) - 1:
                increment += 1
                left = i
                right = self._send_blocks[increment]
                delay = right - left
                new_table.append(delay)
        self._send_blocks = new_table
        return self

    # given the number of send blocks find a random value to send the message
    # example out of 30_0000 ms blocks that last around 30 ms each we have to pick 135 random numbers
    def create_send_blocks(self):
        """
        Creates and populates the `_send_blocks` list with unique random time slots.

        This method calculates the minimum number of slots required and generates
        unique random time slots within the range of `_total_time_before_success_ms`.
        The generated time slots are then sorted and stored in the `_send_blocks` list.
        Finally, it calls `find_delay_values()` to process the delay values and prints
        the `_send_blocks` list.

        Returns:
            list: A sorted list of unique random time slots.
        """
        slots = self.min_number_of_slots()
        if slots != None:
            while len(self._send_blocks) < slots:
                send_block = random.randrange(0, self._total_time_before_success_ms)
                if send_block not in self._send_blocks:
                    self._send_blocks.append(send_block)
        self._send_blocks = sorted(self._send_blocks)
        self.find_delay_values()
        return self._send_blocks
