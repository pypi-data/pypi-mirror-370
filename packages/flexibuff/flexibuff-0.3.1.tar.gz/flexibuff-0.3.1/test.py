from src.flexibuff import FlexibleBuffer
import torch


class index_tester:
    def __init__(self, mem_size=10):
        self.episode_inds = None
        self.episode_lens = None
        self.mem_size = 10
        self.steps_recorded = 0

    def _between(self, num, lastidx, idx):
        lower = lastidx
        upper = idx
        if idx < lastidx:
            upper = lastidx + idx + self.mem_size - lastidx
            if num < idx:
                return True
        if num < upper and num >= lower:
            return True
        return False

    def _update_episode_index(self, idx):
        if idx < self.steps_recorded:
            self.steps_recorded = self.mem_size
        else:
            self.steps_recorded = idx
        # If nothing has been recorded yet, initialize things
        if self.episode_lens is None or self.episode_inds is None:
            self.episode_inds = [0]
            self.episode_lens = []
            self.episode_lens.append(idx)
            self.episode_inds.append(idx)
        else:
            while self._between(self.episode_inds[0], self.episode_inds[-1], idx):
                self.episode_inds.pop(0)
                self.episode_lens.pop(0)
            if idx < self.episode_inds[-1]:
                self.episode_lens.append(idx + self.mem_size - self.episode_inds[-1])
            else:
                self.episode_lens.append(idx - self.episode_inds[-1])
            self.episode_inds.append(idx)

    def report(self):
        print(f"mem_size: {self.mem_size}, recorded: {self.steps_recorded}")
        print(f"idxs: {self.episode_inds}")
        print(f"size: {self.episode_lens}")


def test_truncation_and_returns():
    fb = FlexibleBuffer(
        num_steps=15,
        track_action_mask=False,
        path="./test_truncate/",
        name="reward_calculator",
        n_agents=2,
        global_registered_vars={
            "global_reward": (None, np.float32),
            "state": ([3], np.float32),
        },
        individual_registered_vars={},
    )
    print(fb)

    bootstrap_vals = [
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
        0.2,
    ]
    global_rewards = [
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ]
    terminated = [
        False,
        False,
        False,
        True,
        False,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    truncated = [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        False,
        False,
    ]

    for i in range(len(truncated)):
        fb.save_transition(
            terminated=terminated[i],
            registered_vals={
                "global_reward": global_rewards[i],
                "state": np.ones(3),
            },
            truncated=truncated[i],
            bootstrap_values=bootstrap_vals[i],
        )

    FlexibleBuffer.save(fb)
    fb = FlexibleBuffer.load("./test_truncate/", "reward_calculator")
    print(fb)

    batch = fb.sample_transitions(idx=np.arange(0, 12), as_torch=True)

    print(batch)
    gamma = 0.9

    g = FlexibleBuffer.G(
        rewards=batch.global_reward,
        terminated=batch.terminated,
        last_value=9.0,
        gamma=gamma,
        truncated=batch.truncated,
        bootstrap_values=batch.bootstrap_values[:, 0],
    )

    print(g.flatten())

    g2, adv = FlexibleBuffer.GAE(
        rewards=batch.global_reward,
        values=torch.from_numpy(np.ones(12) * 2).to("cuda:0"),
        terminated=batch.terminated,
        last_value=9.0,
        gamma=gamma,
        truncated=batch.truncated,
        bootstrap_values=batch.bootstrap_values[:, 0],
    )

    print(g2.flatten())
    print(adv.flatten())

    g2, adv = FlexibleBuffer.K_Step_TD(
        rewards=batch.global_reward,
        values=torch.from_numpy(np.ones(12) * 2).to("cuda:0"),
        terminated=batch.terminated,
        last_value=9.0,
        gamma=gamma,
        k=3,
        truncated=batch.truncated,
        bootstrap_values=batch.bootstrap_values[:, 0],
    )

    print(g2.flatten())
    print(adv.flatten())

    exit()


if __name__ == "__main__":
    import numpy as np

    test_truncation_and_returns()
    input("back to regular tests?")
    obs = np.array(
        [  # [agent, timestep, obs]
            [
                [0.0, 1.0, 2.0],
                [1.0, 2.0, 3.0],
                [2.0, 3.0, 4.0],
                [3.0, 4.0, 5.0],
            ],
            [
                [0.1, 1.1, 2.1],
                [1.1, 2.1, 3.1],
                [2.1, 3.1, 4.1],
                [3.1, 4.1, 5.1],
            ],
        ]
    )

    fb = FlexibleBuffer(
        num_steps=5,
        track_action_mask=True,
        discrete_action_cardinalities=[2, 3],
        path="./test_save/",
        name="all_attributes",
        n_agents=2,
        memory_weights=True,
        global_registered_vars={
            "global_rewards": (None, np.float32),
            "global_auxiliary_rewards": (None, np.float32),
            "state": ([3], np.float32),
            "state_": ([3], np.float32),
        },
        individual_registered_vars={
            "individual_rewards": (None, np.float32),
            "individual_auxiliary_rewards": (None, np.float32),
            "discrete_actions": ([2], np.int64),
            "continuous_actions": ([2], np.float32),
            "continuous_log_probs": ([1], np.float32),
            "discrete_log_probs": ([2], np.float32),
            "obs": ([3], np.float32),
            "obs_": ([3], np.float32),
        },
    )

    print(obs[:, 0, :])
    print(obs[:, 1, :])
    print(obs[:, 2, :])
    print(fb)

    fb.save_transition(
        terminated=False,
        action_mask=[np.array([[0, 1], [1, 0]]), np.array([[0, 0, 1], [0, 1, 0]])],
        action_mask_=[np.array([[0, 0], [0, 0]]), np.array([[0, 1, 0], [1, 0, 0]])],
        memory_weight=1.5,
        registered_vals={
            "obs": np.copy(obs[:, 1, :]),
            "obs_": np.copy(obs[:, 2, :]),
            "discrete_actions": np.array([[0, 1], [1, 2]]),
            "continuous_actions": np.array([[0.1, 0.5], [0.2, 1.0]]),
            "global_rewards": 1.0,
            "global_auxiliary_rewards": 0.1,
            "individual_rewards": np.array([0.5, 0.5]),
            "individual_auxiliary_rewards": np.array([0.4, 0.4]),
            "continuous_log_probs": np.array([[-0.1], [-0.2]]),
            "discrete_log_probs": np.array([[-0.1, -0.1], [-0.2, -0.2]]),
            "state": np.copy(obs[0, 0, :]),
            "state_": np.copy(obs[1, 0, :]),
        },
    )

    fb.save_transition(
        terminated=True,
        action_mask=[np.array([[0, 1], [1, 0]]), np.array([[0, 0, 1], [0, 1, 0]])],
        action_mask_=[np.array([[0, 0], [0, 0]]), np.array([[0, 1, 0], [1, 0, 0]])],
        memory_weight=1.1,
        registered_vals={
            "obs": np.copy(obs[:, 0, :]),
            "obs_": np.copy(obs[:, 1, :]),
            "discrete_actions": np.array([[1, 1], [1, 2]]),
            "continuous_actions": np.array([[0.2, 0.6], [0.3, 1.1]]),
            "global_rewards": 1.1,
            "global_auxiliary_rewards": 0.2,
            "individual_rewards": np.array([0.6, 0.6]),
            "individual_auxiliary_rewards": np.array([0.5, 0.5]),
            "continuous_log_probs": np.array([[-0.2], [-0.3]]),
            "discrete_log_probs": np.array([[-0.2, -0.2], [-0.3, -0.3]]),
            "state": np.copy(obs[0, 0, :]),
            "state_": np.copy(obs[1, 0, :]),
        },
    )
    fb.save_transition(
        terminated=True,
        action_mask=[np.array([[0, 1], [1, 0]]), np.array([[0, 0, 1], [0, 1, 0]])],
        action_mask_=[np.array([[0, 0], [0, 0]]), np.array([[0, 1, 0], [1, 0, 0]])],
        memory_weight=1.1,
        registered_vals={
            "obs": np.copy(obs[:, 0, :]),
            "obs_": np.copy(obs[:, 1, :]),
            "discrete_actions": np.array([[1, 1], [1, 2]]),
            "continuous_actions": np.array([[0.2, 0.6], [0.3, 1.1]]),
            "global_rewards": 1.1,
            "global_auxiliary_rewards": 0.2,
            "individual_rewards": np.array([0.6, 0.6]),
            "individual_auxiliary_rewards": np.array([0.5, 0.5]),
            "continuous_log_probs": np.array([[-0.2], [-0.3]]),
            "discrete_log_probs": np.array([[-0.2, -0.2], [-0.3, -0.3]]),
            "state": np.copy(obs[0, 0, :]),
            "state_": np.copy(obs[1, 0, :]),
        },
    )

    FlexibleBuffer.save(fb)

    fb2: FlexibleBuffer = FlexibleBuffer.load(
        path="./test_save/",
        name="all_attributes",
    )

    samp = fb2.sample_transitions(2, as_torch=False)
    print(samp)
    samp.to_torch("cuda")
    print(samp)

    samp2 = fb2.sample_episodes(2)
    print(samp2[0])
    # print(fb2)
    test_buff = index_tester(10)
    test_buff.report()
    while True:
        idx = int(input("input idx: "))
        test_buff._update_episode_index(idx)
        test_buff.report()
