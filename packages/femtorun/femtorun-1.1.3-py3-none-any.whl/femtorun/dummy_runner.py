import femtorun as fr
import numpy as np
from typing import *


class DummyRunner(fr.FemtoRunner):
    """replies with supplied output dict, or random data
    useful in a variety of testing situations"""

    def __init__(self, replies: Dict[str, np.ndarray]):
        self.replies = replies
        self.reply_idx = 0
        super().__init__(input_padding=None, output_padding=None)

    def reset(self):
        self.reply_idx = 0

    def finish(self):
        pass

    def get_vars(self, set_vals):
        pass

    def set_vars(self, set_vals):
        pass

    def step(self, input_vals):
        out_step = {}
        for k, v in self.replies.items():
            if self.reply_idx > v.shape[0]:
                raise RuntimeError(
                    f"Dummy runner ran out of data. Only had {v.shape[0]} timesteps' worth"
                )
            out_step[k] = v[self.reply_idx]
        self.reply_idx += 1

        return out_step, {}
