#iwbsSARC#sarc
from .sb_layout_env import LayoutEnv2


class LayoutEnv3(LayoutEnv2):
    # Add class id here and create an isolated pias environment in the form of an isolated file.
    def __init__(self) -> None:
        """
        This environment has an improved reward function
        """
        super().__init__()
        # Fix default HOST in client app first.....

        # config_file = Path(r"OpenGym\\layoutenv_pkg\\src\\configs\\config_env2.json").open('r')
        # self.config = json.loads(config_file.read())
        # self.episode_count = 1754

    def reward(self, att_idx: float, layout: dict) -> float:
        try:
            volume = max(layout.values(), key=lambda x: x['volume'])['volume']
        except ValueError as e:
            self.logger.exception(f"{e}")
            self.logger.error(f"lenght layout {len(layout.values())}")
            volume = 0.0

        NEGATIVE_REWARD = float(-1.0)
        POSITIVE_REWARD = float(1.0)
        VOLUMETRIC_REWARD = (volume - self.config['min_compartment_volume_a']) * 0.01
        NEUTRAL_REWARD = float(0.0)

        if att_idx < self.req_idx and att_idx > self.previous_att_idx:
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {POSITIVE_REWARD} \nthe biggest compartment volume is {volume}")
            self.max_volume = volume
            return POSITIVE_REWARD
        elif att_idx < self.req_idx and att_idx <= self.previous_att_idx:
            self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {NEGATIVE_REWARD} \nthe biggest compartment volume is {volume}")
            self.max_volume = volume
            return NEGATIVE_REWARD 
        elif att_idx >= self.req_idx:
            if self.max_volume and volume > self.max_volume:
                # The biggest compartment volume is bigger as the biggest compartment volume in the previous timestep
                self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {VOLUMETRIC_REWARD} \nthe biggest - is {volume}")
                self.max_volume = volume
                return VOLUMETRIC_REWARD
            elif self.max_volume and volume <= self.max_volume:
                self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {VOLUMETRIC_REWARD} \nthe biggest compartment volume is {volume}")
                self.max_volume = volume
                return NEUTRAL_REWARD             
            elif not self.max_volume:
                # This is the first timesteps
                self.logger.info(f"reward(att_idx, req_idx, layout, volume_limit) -> reward = {VOLUMETRIC_REWARD} \nthe biggest compartment volume is {volume}")
                self.max_volume = volume
                return VOLUMETRIC_REWARD
            else:
                # There were previous volumetric rewards only the biggest compartment is equal or smaller as the biggest
                # compartment in the previous timestep.
                self.max_volume = volume
                return NEUTRAL_REWARD
        else:
            self.logger.error('No reward given')
            return -10  


    

        
    