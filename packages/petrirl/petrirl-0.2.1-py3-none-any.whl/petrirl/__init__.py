from gymnasium.envs.registration import register


register(
    id="petrirl-fms-v0",
    entry_point="petrirl.envs.fms.gym_env:FmsEnv",
    )

register(
    id="petrirl-dft-v0",
    entry_point="petrirl.envs.dft.gym_env:DftEnv",
    )



