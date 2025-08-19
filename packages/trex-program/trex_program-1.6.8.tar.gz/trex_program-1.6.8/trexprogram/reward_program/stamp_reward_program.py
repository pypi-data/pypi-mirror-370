'''
Created on 21 Apr 2021

@author: jacklok
'''

from trexprogram.reward_program.reward_program_base import SchemeRewardProgram,\
    GiveawayRewardBaseProgram
from trexmodel.models.datastore.reward_models import CustomerStampReward
from trexconf import program_conf
import logging
from trexprogram.utils.reward_program_helper import calculate_expiry_date

logger = logging.getLogger('reward-program-lib')

class StampSchemeProgram(SchemeRewardProgram):
    
    def __init__(self, merchant_acct, program_configuration):
        super(StampSchemeProgram, self).__init__(merchant_acct, program_configuration)
        self.reward_format          = program_configuration.get('reward_format')
        self.giveaway_method        = program_configuration.get('giveaway_method')
        
        if self.reward_format!=program_conf.REWARD_FORMAT_STAMP:
            raise Exception('Invalid program configuration')
    
    def get_reward_format(self):
        return program_conf.REWARD_FORMAT_STAMP
    
    def give(self, customer_acct, transaction_details, reward_set=1): 
        if self.is_eligible_based_on_exclusivity(customer_acct) \
            and self.is_eligible_for_limited_to_specific_day_condition(transaction_details) \
            and self.is_eligible_for_limited_to_specific_date_of_month_condition(transaction_details):
            
            logger.debug('StampSchemeProgram: Going to give reward')
            transact_datetime               = transaction_details.transact_datetime
            
            giveaway_reward_sales_amount    = self.get_giveaway_reward_sales_amount(transaction_details)
            
            reward_unit                     = self.calculate_reward_unit(giveaway_reward_sales_amount) * reward_set
            reward_amount                   = self.calculate_entitle_reward_amount(reward_unit=reward_unit)
            
            balance_of_reward_amount_limit  = self.get_balance_of_reward_amount_limit(customer_acct, transaction_details)
            
            logger.info('reward_amount=%f', reward_amount)
            logger.info('balance_of_reward_amount_limit=%f', balance_of_reward_amount_limit)
            
            is_reach_reward_limit = False
            
            if reward_amount > balance_of_reward_amount_limit:
                reward_amount = balance_of_reward_amount_limit
                logger.info('changed to balance of reward amount limit')
                
                is_reach_reward_limit = True
            
            if reward_amount>0 or is_reach_reward_limit:
            
                transaction_id                  = transaction_details.transaction_id
                invoice_id                      = transaction_details.invoice_id
                
                transact_by                     = transaction_details.transact_by_user
                
                transact_outlet                 = transaction_details.transact_outlet_details
                
                effective_date                  = transact_datetime.date()
                expiry_date                     = calculate_expiry_date(self.expiration_type, self.expiration_value, start_date=effective_date)
                
                reward_status = program_conf.REWARD_STATUS_VALID
                
                if is_reach_reward_limit and reward_amount==0:
                    reward_status = program_conf.REWARD_STATUS_REACH_LIMIT
                
                stamp_reward = CustomerStampReward.create( 
                                                customer_acct       = customer_acct, 
                                                reward_amount       = reward_amount,
                                                transact_outlet     = transact_outlet, 
                                                expiry_date         = expiry_date, 
                                                effective_date      = effective_date,
                                                transaction_id      = transaction_id, 
                                                invoice_id          = invoice_id, 
                                                rewarded_by         = transact_by,
                                                program_key         = self.program_key,
                                                rewarded_datetime   = transact_datetime,
                                                status              = reward_status,
                                                )
                
                return stamp_reward
        else:
            logger.debug('Not eligible to get reward')
            
class StampGiveawayProgram(GiveawayRewardBaseProgram):
    
    def __init__(self, merchant_acct, program_configuration, reward_set=1):
        super(StampGiveawayProgram, self).__init__(merchant_acct, program_configuration, reward_set=reward_set)
        self.reward_amount = self.scheme.get('reward_amount')
        
    def give(self, customer_acct, transaction_details, reward_set=1): 
        if self.is_eligible_based_on_exclusivity(customer_acct):
            
            logger.debug('PointRewardProgram: Going to give reward')
            transact_datetime               = transaction_details.transact_datetime
            
            reward_amount                   = self.calculate_entitle_reward_amount(reward_set=reward_set)
            
            logger.info('reward_amount=%f', reward_amount)
            
            if reward_amount>0:
                transaction_id                  = transaction_details.transaction_id
                invoice_id                      = transaction_details.invoice_id
                
                transact_by                     = transaction_details.transact_by_user
                
                transact_outlet                 = transaction_details.transact_outlet_details
                
                
                effective_date                  = transact_datetime.date()
                expiry_date                     = calculate_expiry_date(self.expiration_type, self.expiration_value, start_date=effective_date)
                 
                
                logger.debug('-------> Going to create point reward where reward amount=%f',reward_amount)
                
                reward_status = program_conf.REWARD_STATUS_VALID
                
                stamp_reward = CustomerStampReward.create( 
                                                customer_acct       = customer_acct, 
                                                reward_amount       = reward_amount,
                                                transact_outlet     = transact_outlet, 
                                                expiry_date         = expiry_date, 
                                                effective_date      = effective_date,
                                                transaction_id      = transaction_id, 
                                                invoice_id          = invoice_id, 
                                                rewarded_by         = transact_by,
                                                program_key         = self.program_key,
                                                rewarded_datetime   = transact_datetime,
                                                status              = reward_status,
                                                )
                
                return stamp_reward
            
                
        else:
            logger.debug('Not eligible to get reward')            
