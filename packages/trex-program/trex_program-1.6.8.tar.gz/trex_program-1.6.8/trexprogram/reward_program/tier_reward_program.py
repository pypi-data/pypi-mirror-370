'''
Created on 4 Oct 2021

@author: jacklok
'''
from trexprogram.reward_program.reward_program_base import RewardProgramBase, EntitledVoucherSummary
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher
from trexconf import program_conf
from datetime import datetime
import logging
from trexmodel.models.datastore.program_models import MerchantTierRewardProgram
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexprogram.utils.tier_reward_program_helper import update_and_get_unlock_tier_index_list
from trexconf import conf as lib_conf 
from trexlib.utils.google.cloud_tasks_util import create_task
import json
from trexprogram.utils.reward_program_helper import calculate_expiry_date,\
    calculate_effective_date, __consume_customer_reward_transaction
from trexconf.conf import DEFAULT_DATE_FORMAT

logger = logging.getLogger('reward-program-lib')
#logger = logging.getLogger('target_debug')

class TierRewardProgram(RewardProgramBase):
    
    def __init__(self, merchant_acct, program_configuration):
        super(TierRewardProgram, self).__init__(merchant_acct, program_configuration)
        
        self.reward_format          = program_configuration.get('reward_format')
        self.giveaway_method        = program_configuration.get('giveaway_method')
        
        
        if self.reward_format != program_conf.REWARD_FORMAT_VOUCHER:
            raise Exception('Invalid program configuration')    
    
    def get_reward_format(self):
        return program_conf.REWARD_FORMAT_VOUCHER
    
    def __construct_giveaway_voucher_details_list(self, unlocked_voucher_details_list, transaction_details, reward_set):
        giveaway_voucher_details_list = []
        
        for voucher_details in unlocked_voucher_details_list:
            logger.debug('voucher_details=%s', voucher_details)    
            effective_date          = None 
            effective_type          = voucher_details.get('effective_type')
            effective_value         = voucher_details.get('effective_value')
            effective_date_str      = voucher_details.get('effective_date')
            
             
            if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE:
                if is_not_empty(effective_date_str):
                    effective_date = datetime.strptime(effective_date_str, DEFAULT_DATE_FORMAT)
            else:
                effective_date  = calculate_effective_date(effective_type, effective_value, start_date = transaction_details.transact_datetime.date())
             
            expiration_type         = voucher_details.get('expiration_type')
            expiration_value        = voucher_details.get('expiration_value')
             
            expiry_date             = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
            
            voucher_amount          = voucher_details.get('voucher_amount')
            
            voucher_details         = {
                                        'voucher_key'       : voucher_details.get('voucher_key'),
                                        'use_in_store'      : voucher_details.get('use_in_store'),
                                        'use_online'        : voucher_details.get('use_online'),
                                        'voucher_amount'    : voucher_amount * reward_set,
                                        'effective_date'    : effective_date,
                                        'expiry_date'       : expiry_date,
                                        }
             
            logger.debug('construct_giveaway_voucher_details_list: voucher_details=%s', voucher_details) 
             
            giveaway_voucher_details_list.append(voucher_details)
            
        return giveaway_voucher_details_list
    
    def give(self, customer_acct, transaction_details, reward_set=1): 
        if self.is_eligible_based_on_exclusivity(customer_acct):
            logger.debug('TierRewardProgram: Going to give reward')
            transact_outlet     = transaction_details.transact_outlet_details
            transaction_id      = transaction_details.transaction_id
            invoice_id          = transaction_details.invoice_id
            transact_by_user    = transaction_details.transact_by_user
            transact_datetime   = transaction_details.transact_datetime
            
            entiteld_voucher_brief = EntitledVoucherSummary(transaction_id=transaction_id)
            
            unlocked_tier_index_list  = []
            tier_reward_program     = MerchantTierRewardProgram.fetch(self.program_key)
            
            if tier_reward_program:
                unlocked_tier_index_list = update_and_get_unlock_tier_index_list(customer_acct, tier_reward_program, transaction_details, customer_acct.reward_summary)
             
            logger.debug('unlocked_tier_index_list=%s', unlocked_tier_index_list) 
                
            if unlocked_tier_index_list:
                program_tiers                   = tier_reward_program.program_tiers
                unlocked_voucher_details_list   = []
                redeem_reward_dict              = {}
                
                for tier_index in unlocked_tier_index_list:
                    logger.debug('prepare %s action after unlocked', tier_index)
                    
                    for tier_reward_setting in program_tiers:
                        
                        if tier_reward_setting.get('tier_index') == tier_index:
                            unlocked_voucher_details_list.extend(tier_reward_setting.get('reward_items'))
                            if tier_reward_setting.get('action_after_unlock')==program_conf.ACTION_AFTER_UNLOCK_TIER_CONSUME_REWARD:
                                #check whether there is reward to consume
                                redeem_reward_dict[tier_reward_setting.get('consume_reward_format')]     = (redeem_reward_dict.get(tier_reward_setting.get('consume_reward_format')) or .0) + float(tier_reward_setting.get('consume_reward_amount'))
                            break
                            
                
                if unlocked_voucher_details_list:
                    giveaway_voucher_details_list = self.__construct_giveaway_voucher_details_list(unlocked_voucher_details_list, 
                                                                                                   transaction_details, 
                                                                                                   reward_set)
                    
                    if giveaway_voucher_details_list:
                        
                        for voucher in giveaway_voucher_details_list:
                            merchant_voucher = MerchantVoucher.fetch(voucher.get('voucher_key'))
                            if merchant_voucher:
                                
                                effective_date              = voucher.get('effective_date')
                                expiry_date                 = voucher.get('expiry_date')
                                voucher_amount              = voucher.get('voucher_amount') * reward_set
                                
                                customer_voucher_list       = [] 
                                
                                for v in range(voucher_amount):
                                    customer_voucher_brief = CustomerEntitledVoucher.create(
                                                                                    merchant_voucher,
                                                                                    customer_acct, 
                                                                                    transact_outlet     = transact_outlet,
                                                                                    transaction_id      = transaction_id,
                                                                                    invoice_id          = invoice_id,
                                                                                    rewarded_by         = transact_by_user,
                                                                                    rewarded_datetime   = transact_datetime,
                                                                                    effective_date      = effective_date,
                                                                                    expiry_date         = expiry_date,
                                                                                    program_key         = self.program_key,
                                                                                    )
                                    
                                    customer_voucher_list.append(customer_voucher_brief)
                                    
                                entiteld_voucher_brief.add(merchant_voucher, 
                                                           customer_voucher_list)
                                    
                            else:
                                logger.warn('Voucher is not found for voucher_key=%s', voucher.get('voucher_key'))
                
                #this is only applicable for reward to consume
                logger.debug('to consume redeem_reward_dict=%s', redeem_reward_dict)
                if redeem_reward_dict:
                    logger.debug('to consume redeem_reward_dict=%s', redeem_reward_dict)
                    
                    customer_reward_summary = customer_acct.reward_summary
                    condition_match = True
                    for reward_format, reward_amount_to_redeem in redeem_reward_dict.items():
                        logger.debug('to redeem: reward_format=%s, reward_amount_to_redeem=%s', reward_format, reward_amount_to_redeem)
                        
                        target_customer_reward_summary = customer_reward_summary.get(reward_format)
                        logger.debug('target_customer_reward_summary=%s', target_customer_reward_summary)
                        
                        if target_customer_reward_summary:
                            target_reward_amount = target_customer_reward_summary.get('amount')
                            
                            if target_reward_amount <reward_amount_to_redeem:
                                
                                
                                logger.debug('target reward amount to redeem is not sufficient')
                                condition_match = False
                                #redeem_reward_dict[reward_format]=target_reward_amount
                                break
                            
                                
                        else:
                            condition_match = False
                            #raise Exception('Failed to complete tier reward redemption part due to target reward is not found')
                            break
                    
                    logger.debug('condition_match=%s', condition_match)
                    
                    if condition_match==False:
                        raise Exception('Failed to complete tier reward redemption part due to target reward is not found or reward amount to redeem is not sufficient')
                    else:
                        '''
                        task_url    = '%s%s' % (lib_conf.SYSTEM_BASE_URL, '/program/task/tier-program/reward-consume')
                        queue_name  = 'giveaway-reward'
                        
                        payload = {
                                    'customer_key'              : customer_acct.key_in_str,
                                    'transaction_id'            : transaction_id,
                                    'invoice_id'                : invoice_id, 
                                    'redeem_reward_details'     : json.dumps(redeem_reward_dict),
                                    'task_url'                  : task_url,
                                    }
                        
                        create_task(task_url, queue_name, 
                                    in_seconds      = 1,
                                    http_method     = 'post', 
                                    payload         = payload,
                                    credential_path = lib_conf.SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                                    project_id      = lib_conf.SYSTEM_TASK_GCLOUD_PROJECT_ID,
                                    location        = lib_conf.SYSTEM_TASK_GCLOUD_LOCATION,
                                    service_email   = lib_conf.SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                                    )  
                        '''
                        __consume_customer_reward_transaction(customer_acct, transaction_id, redeem_reward_dict)
                '''
                if True:
                    raise Exception('Completed')
                '''                
            return entiteld_voucher_brief        
                    
            
            
            
                
        else:
            logger.debug('Not eligible to get reward')