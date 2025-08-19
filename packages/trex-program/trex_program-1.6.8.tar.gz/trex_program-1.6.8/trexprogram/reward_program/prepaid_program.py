'''
Created on 13 Mar 2023

@author: jacklok
'''

from trexprogram.reward_program.reward_program_base import SchemeRewardProgram,\
    GiveawayRewardBaseProgram
from trexconf import program_conf
import logging
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward

#logger = logging.getLogger('reward-program-lib')
logger = logging.getLogger('debug')

class PrepaidSchemeProgram(SchemeRewardProgram):
    
    def __init__(self, merchant_acct, program_configuration):
        super(PrepaidSchemeProgram, self).__init__(merchant_acct, program_configuration)
        
        self.reward_format          = program_configuration.get('reward_format')
        self.giveaway_method        = program_configuration.get('giveaway_method')
        
        
        if self.reward_format!=self.get_reward_format():
            raise Exception('Invalid program configuration')    
    
    def get_reward_format(self):
        return program_conf.REWARD_FORMAT_PREPAID
    
    def give(self, customer_acct, transaction_details, reward_set=1): 
        if self.is_eligible_based_on_exclusivity(customer_acct) \
            and self.is_eligible_for_limited_to_specific_day_condition(transaction_details) \
            and self.is_eligible_for_limited_to_specific_date_of_month_condition(transaction_details):
            
            logger.debug('PrepaidSchemeProgram: Going to give reward')
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
                
                
                logger.debug('-------> Going to create prepaid reward where reward amount=%f',reward_amount)
                
                prepaid_topup_reward = CustomerPrepaidReward.topup(customer_acct, reward_amount, None, 
                                                                   topup_outlet=transact_outlet, 
                                                                   topup_by=transact_by, 
                                                                   invoice_id=invoice_id,
                                                                   transaction_id=transaction_id,
                                                                   topup_datetime=transact_datetime,
                                                                   )
                
                return prepaid_topup_reward
            
                
        else:
            logger.debug('Not eligible to get reward')
            
class PrepaidGiveawayProgram(GiveawayRewardBaseProgram):
    
    def __init__(self, merchant_acct, program_configuration, reward_set=1):
        super(PrepaidGiveawayProgram, self).__init__(merchant_acct, program_configuration, reward_set=reward_set)
        self.reward_amount = self.scheme.get('reward_amount')
    
    def give(self, customer_acct, transaction_details, reward_set=1): 
        is_eligible =  self.is_eligible_based_on_exclusivity(customer_acct)
        
        logger.debug('is_eligible=%s', is_eligible)
        
        if is_eligible:    
            logger.debug('PrepaidGiveawayProgram: Going to give reward')
            transact_datetime               = transaction_details.transact_datetime
            
            reward_amount                   = self.calculate_entitle_reward_amount(reward_set=reward_set)
            
            logger.info('reward_amount=%f', reward_amount)
            
            if reward_amount>0:
                transaction_id                  = transaction_details.transaction_id
                invoice_id                      = transaction_details.invoice_id
                
                transact_by                     = transaction_details.transact_by_user
                
                transact_outlet                 = transaction_details.transact_outlet_details
                
                
                logger.debug('-------> Going to create prepaid reward where reward amount=%f',reward_amount)
                
                prepaid_topup_reward = CustomerPrepaidReward.topup(customer_acct, 
                                                                   reward_amount, 
                                                                   None, 
                                                                   topup_outlet=transact_outlet, 
                                                                   topup_by=transact_by, 
                                                                   invoice_id=invoice_id,
                                                                   transaction_id=transaction_id,
                                                                   topup_datetime=transact_datetime,
                                                                   )
                
                logger.debug('prepaid_topup_reward=%s', prepaid_topup_reward)
                
                return prepaid_topup_reward
            
                
        else:
            logger.debug('Not eligible to get reward')            
    
