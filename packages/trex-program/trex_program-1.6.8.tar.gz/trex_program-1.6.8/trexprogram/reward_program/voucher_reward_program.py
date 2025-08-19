'''
Created on 21 Apr 2021

@author: jacklok
'''

from trexprogram.reward_program.reward_program_base import VoucherRewardProgramBase,\
    GiveawayRewardBaseProgram, VoucherSchemeRewardProgramBase
from trexconf import program_conf

class VoucherProgram(VoucherRewardProgramBase):
    
    def __init__(self, merchant_acct, program_configuration):
        super(VoucherProgram, self).__init__(merchant_acct, program_configuration)
        
class VoucherSchemeProgram(VoucherSchemeRewardProgramBase):
    
    def __init__(self, merchant_acct, program_configuration):
        super(VoucherSchemeProgram, self).__init__(merchant_acct, program_configuration)
        
        
class VoucherGiveawayProgram(VoucherProgram, GiveawayRewardBaseProgram):
    
    def __init__(self, program_configuration):
        super(VoucherGiveawayProgram, self).__init__(program_configuration)
        self.reward_format          = self.get_reward_format()
        self.giveaway_method        = program_configuration.get('giveaway_method')
        
        
        if self.reward_format!=self.get_reward_format():
            raise Exception('Invalid program configuration')    
    
    def get_reward_format(self):
        return program_conf.REWARD_FORMAT_VOUCHER        
    