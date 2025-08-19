'''
Created on 15 Sep 2021

@author: jacklok
'''
from trexconf import program_conf
import logging
from trexprogram.reward_program.giveaway_reward_program import GiveawayRewardProgram

logger = logging.getLogger('reward-program-lib')

class BirthdayRewardProgram(GiveawayRewardProgram):
    
    def __init__(self, program_configuration, currency=None):
        super(BirthdayRewardProgram, self).__init__(program_configuration, currency=currency)
        
        self.reward_format          = program_configuration.get('reward_format')
        self.giveaway_method        = program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM
        
        logger.debug('GiveawayRewardProgram: reward_format=%s', self.reward_format)
        
        if not self.reward_format in (program_conf.REWARD_FORMAT_POINT, 
                                      program_conf.REWARD_FORMAT_STAMP, 
                                      program_conf.REWARD_FORMAT_VOUCHER):
            raise Exception('Invalid program configuration') 