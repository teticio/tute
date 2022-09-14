"""RLCard module
"""
from rlcard.envs.registration import register

register(
    env_id='tute',
    entry_point='tute.rlcard.env:TuteEnv',
)
