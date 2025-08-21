# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from string import ascii_lowercase

import gymnasium as gym
import numpy as np


class BitFlippingSim:
    """
    Bit Flipping is a common game where the goal is to transform one to the other in as few
    moves as possible by inverting the whole numbered rows or whole lettered columns at once
    (one move).

    The game is played on a 2D board of size n x n, where n is the number of rows and columns.

    Sensor Space:
    Action Space:

    Example:

    Your task is to change your board so as match the board on the right (the objective)

        You      The objective

       a  b  c     a  b  c
    1  1  1  1     0  1  1
    2  0  0  0     1  0  0
    3  1  1  1     1  0  0

    Please type a row number or column letter whose bits you want to flip: "3"
        You      The objective
       a  b  c     a  b  c
    1  1  1  1     0  1  1
    2  0  0  0     1  0  0
    3  0  0  0     1  0  0

    Please type a row number or column letter whose bits you want to flip: "a"

        You      The objective
       a  b  c     a  b  c
    1  0  1  1     0  1  1
    2  1  0  0     1  0  0
    3  1  0  0     1  0  0

    Congratulations. You solved it in 2 moves.
    """

    def __init__(self, N=6):
        self.N = N
        self.board = np.zeros((N, N), dtype=int)
        self.target = np.zeros((N, N), dtype=int)
        self.action_space = gym.spaces.Discrete(N * N)  # idx of the el to switch
        self.sensor_space = gym.spaces.Dict(
            {
                "is_solved": gym.spaces.Discrete(2),  # 0: False, 1: True
                "steps": gym.spaces.Box(1, 100),  # Number of steps taken
                "state": gym.spaces.MultiBinary(N * N),  # Current state of the board
                "target": gym.spaces.MultiBinary(N * N),  # Target state of the board
                "sim_reward": gym.spaces.Box(0, N * N),  # Reward from the simulator
            }
        )

        self.action_taken = None
        self.steps_taken = 0

        self.reset()

    def _get_reward(self):
        """
        The reward is the number of 1s that match
        if there is a 1 that doesn't match, it uses -1
        """
        return np.sum(self.board == self.target)

    def reset(self):
        self.steps_taken = 0
        self.board = np.zeros((self.N, self.N), dtype=int)
        self.setbits(self.board, count=np.random.randint(1, self.N + 1))
        self.target = np.copy(self.board)

        while np.array_equal(self.board, self.target):
            self.shuffle(self.board, count=2 * self.N)

        return self._get_sensors(), {}

    def compute_reward(self):
        return np.sum(self.board == self.target)

    def _get_sensors(self):
        return {
            "state": self.board.flatten(),
            "target": self.target.flatten(),
            "reward": self.compute_reward(),
        }

    def setbits(self, board, count=1):
        for _ in range(count):
            row = np.random.randint(0, self.N)
            col = np.random.randint(0, self.N)
            board[row, col] ^= 1

    def shuffle(self, board, count=1):
        for _ in range(count):
            if np.random.randint(0, 2):
                self.fliprow(board, np.random.randint(0, self.N))
            else:
                self.flipcol(board, np.random.randint(0, self.N))

    def fliprow(self, board, i):
        board[i, :] ^= 1

    def flipcol(self, board, i):
        board[:, i] ^= 1

    def flipbit(self, board, i, j):
        board[i, j] ^= 1

    def step(self, action):
        self.steps_taken += 1
        self.action_taken = action

        self.flipbit(self.board, action // self.N, action % self.N)

        is_done = np.array_equal(self.board, self.target)
        is_terminated = is_done or np.sum(self.board == self.target) == self.N * self.N
        reward = 1 if is_done else -1

        return self._get_sensors(), reward, is_done, is_terminated, {}

    def render(self):
        def format_board(board, title):
            res = [title]

            res.append("     " + " ".join(ascii_lowercase[i] for i in range(self.N)))

            for j, line in enumerate(board):
                res.append("  " + " ".join(["%2s" % (j + 1)] + [str(i) for i in line]))

            return "\n".join(res)

        current_board_str = format_board(self.board, "Current configuration:")
        target_board_str = format_board(self.target, "\nTarget configuration:")

        if self.action_taken is None:
            return f"Flipped: (row: ?, col: ?), Total Actions Taken: {self.steps_taken}\n\n{current_board_str}\n{target_board_str}"

        # flipped = ascii_lowercase[self.action_taken - self.N] if self.action_taken >= self.N else str(self.action_taken + 1)
        flipped_col = ascii_lowercase[self.action_taken % self.N]
        flipped_row = str(self.action_taken // self.N + 1)

        return f"Flipped: (row: {flipped_row}, col: {flipped_col}), Total Actions Taken: {self.steps_taken}\n\n{current_board_str}\n{target_board_str}"
