'''
Created on 2 May 2024

@author: jacklok
'''

from datetime import datetime
from trexlib.utils.string_util import is_not_empty
from trexconf import program_conf, conf 
import logging
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexprogram.utils.reward_program_helper import calculate_effective_date,\
    calculate_expiry_date
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher,\
    CustomerPointReward, CustomerStampReward,\
    VoucherRewardDetailsForUpstreamData
from trexconf.program_conf import REWARD_PROGRAM_DATE_FORMAT
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexmodel.models.datastore.customer_model_helpers import update_reward_summary_with_new_reward,\
    update_customer_entiteld_voucher_summary_with_new_voucher_info
from trexprogram.reward_program.reward_program_base import EntitledVoucherSummary
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_reward_upstream_for_merchant
from trexmodel.models.datastore.message_model_helper import create_transaction_message

logger = logging.getLogger('reward-program-lib')


def giveaway_referral_program_reward(merchant_acct, referrer_customer_acct, referee_cusstomer_acct, transact_outlet, create_upstream=True):
    merchant_referral_programs_list = merchant_acct.published_referral_program_configuration
    if is_not_empty(merchant_referral_programs_list):
        for program_configuration in merchant_referral_programs_list.get('programs'):
            ReferralProgram(program_configuration, create_upstream=create_upstream).give_reward(referrer_customer_acct, referee_cusstomer_acct, transact_outlet)
            
            

class ReferralProgram(object):
    def __init__(self, program_configuration, create_upstream=True):
        self.program_configuration  = program_configuration
        self.program_key            = self.program_configuration.get('program_key')
        self.desc                   = program_configuration.get('desc')
        self.program_settings       = program_configuration.get('program_settings')
        self.start_date             = program_configuration.get('start_date')
        self.end_date               = program_configuration.get('end_date')
        self.start_date             = datetime.strptime(self.start_date, '%d-%m-%Y').date()
        self.end_date               = datetime.strptime(self.end_date, '%d-%m-%Y').date()
        self.create_upstream        = create_upstream
        
    def give_reward(self, referrer_customer_acct, referee_cusstomer_acct, transact_outlet):
        transact_datetime       = datetime.utcnow()
        referrer_reward_items   = self.program_settings.get('referrer_reward_items')
        referee_reward_items    = self.program_settings.get('referee_reward_items')
        
        if is_not_empty(referrer_reward_items):
            self.__give_reward(referrer_customer_acct, referrer_reward_items, transact_outlet, transact_datetime)
        
        if is_not_empty(referee_reward_items):
            self.__give_reward(referee_cusstomer_acct, referee_reward_items, transact_outlet, transact_datetime)
        
    def __give_reward(self, customer_acct, reward_items, transact_outlet, transact_datetime):
        referral_reward_transaction = CustomerTransaction.create_referral_transaction(
                                           customer_acct, 
                                           transact_outlet      = transact_outlet,
                                           transact_datetime    = transact_datetime,
                                           )
        for reward in reward_items:
            self.__give_reward_by_type(customer_acct, reward, reward.get('reward_type'), referral_reward_transaction, transact_outlet)
        
        customer_acct.put()
        referral_reward_transaction.put()
        create_transaction_message(referral_reward_transaction, message_category=conf.MESSAGE_CATEGORY_REFERRAL)
    
    def __give_reward_by_type(self, customer_acct, reward_details, reward_type, referral_reward_transaction, transact_outlet):
        if reward_type==program_conf.REWARD_FORMAT_VOUCHER:
            self.__give_voucher_reward(customer_acct, reward_details, referral_reward_transaction, transact_outlet)
        
        elif reward_type==program_conf.REWARD_FORMAT_POINT:
            self.__give_point_reward(customer_acct, reward_details, referral_reward_transaction, transact_outlet)
        
        elif reward_type==program_conf.REWARD_FORMAT_STAMP:
            self.__give_stamp_reward(customer_acct, reward_details, referral_reward_transaction, transact_outlet)
        
        elif reward_type==program_conf.REWARD_FORMAT_PREPAID:
            self.__give_prepaid_reward(customer_acct, reward_details, referral_reward_transaction, transact_outlet)    
    
    def __give_voucher_reward(self, customer_acct, defined_reward_item, referral_reward_transaction, transact_outlet):
        transaction_id      = referral_reward_transaction.transaction_id
        transact_datetime   = referral_reward_transaction.transact_datetime
        
        voucher_details = self.__construct_voucher_details(defined_reward_item, referral_reward_transaction)
        
        logger.debug('customer_acct=%s', customer_acct)
        logger.debug('voucher_details=%s', voucher_details)
        
        merchant_voucher = MerchantVoucher.fetch(voucher_details.get('voucher_key'))
        if merchant_voucher:
            
            effective_date              = voucher_details.get('effective_date')
            expiry_date                 = voucher_details.get('expiry_date')
            voucher_amount              = voucher_details.get('voucher_amount')
            
            customer_entitled_vouchers_list       = []
            
            transaction_voucher_summary         = referral_reward_transaction.entitled_voucher_summary or {}
            customer_entitled_voucher_summary   = customer_acct.entitled_voucher_summary
            
            for v in range(voucher_amount):
                logger.debug('referral program debug: giveaway %s to %s', merchant_voucher.label, customer_acct.name)
                entiteld_voucher_brief  = EntitledVoucherSummary(transaction_id=transaction_id)
                entitled_voucher = CustomerEntitledVoucher.create(
                                            merchant_voucher,
                                            customer_acct, 
                                            transact_outlet     = transact_outlet,
                                            transaction_id      = transaction_id,
                                            rewarded_datetime   = transact_datetime,
                                            effective_date      = effective_date,
                                            expiry_date         = expiry_date,
                                            
                                            )
                customer_entitled_vouchers_list.append(entitled_voucher)
                
            entiteld_voucher_brief.add(merchant_voucher, customer_entitled_vouchers_list)
            
            voucher_summary_list = entiteld_voucher_brief.entitled_voucher_summary_list
                
            for voucher_summary in voucher_summary_list:
                
                logger.debug('>>>>>>>>>>>>> voucher_summary=%s', voucher_summary)
                
                voucher_key         = voucher_summary.get('key')
                voucher_label       = voucher_summary.get('label')
                voucher_image_url   = voucher_summary.get('image_url')
                voucher_amoumt      = voucher_summary.get('amount')
                redeem_info_list    = voucher_summary.get('redeem_info_list')
                configuration       = voucher_summary.get('configuration')
                
                customer_entitled_voucher_summary = update_customer_entiteld_voucher_summary_with_new_voucher_info(customer_entitled_voucher_summary,
                                                                                                              voucher_key, 
                                                                                                              voucher_label,
                                                                                                              voucher_image_url,
                                                                                                              redeem_info_list,
                                                                                                              configuration,
                                                                                                              )
                
                logger.debug('========================================')
                logger.debug('customer_entitled_voucher_summary=%s', customer_entitled_voucher_summary)
                logger.debug('========================================')
                
                if(voucher_amoumt>0):
                    
                    
                    found_voucher_summary = transaction_voucher_summary.get(voucher_key)
                    
                    if found_voucher_summary:
                        transaction_voucher_summary[voucher_key]['amount'] += voucher_amoumt
                        if transaction_voucher_summary[voucher_key].get('label') is None:
                            transaction_voucher_summary[voucher_key]['key']          = voucher_key
                            transaction_voucher_summary[voucher_key]['image_url']    = voucher_image_url
                            transaction_voucher_summary[voucher_key]['label']        = voucher_label   
                         
                    else:
                        transaction_voucher_summary[voucher_key] = {
                                                                            'key'               : voucher_key,
                                                                            'redeem_info_list'  : redeem_info_list,
                                                                            'label'             : voucher_label,
                                                                            'image_url'         : voucher_image_url,
                                                                            'amount'            : len(redeem_info_list), 
                                                                        }
                            
                    #rearrange voucher with expiry date 
                    voucher_amount_by_expiry_date = {}   
                    for redeem_info in redeem_info_list: 
                        expiry_date     = redeem_info.get('expiry_date')
                        
                        found_voucher_amount = voucher_amount_by_expiry_date.get(expiry_date)
                        if found_voucher_amount:
                            found_voucher_amount+=1
                        else:
                            found_voucher_amount = 1 
                        
                        voucher_amount_by_expiry_date[expiry_date] = found_voucher_amount
                    
                    for expiry_date, voucher_amount in voucher_amount_by_expiry_date.items():
                        
                        voucher_reward_brief = VoucherRewardDetailsForUpstreamData(voucher_key, voucher_amount, expiry_date, transact_datetime) 
                        
                        logger.debug('voucher_reward_brief=%s', voucher_reward_brief)
                        
                        if self.create_upstream:
                            create_merchant_customer_reward_upstream_for_merchant(referral_reward_transaction, 
                                                                          voucher_reward_brief,)  
            
                referral_reward_transaction.entitled_voucher_summary    = transaction_voucher_summary
                customer_acct.entitled_voucher_summary                  = customer_entitled_voucher_summary
        
        logger.debug('after gave voucher referral reward to %s', customer_acct.name)
                    
                    
    
    def __give_point_reward(self, customer_acct, defined_reward_item, referral_reward_transaction, transact_outlet):
        
        transaction_id      = referral_reward_transaction.transaction_id
        transact_datetime   = referral_reward_transaction.transact_datetime
        expiration_type     = defined_reward_item.get('expiration_type')
        expiration_value    = defined_reward_item.get('expiration_value')
        effective_date      = transact_datetime.date()
        expiry_date         = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
        
        reward_amount       = defined_reward_item.get('point_amount')
        
        reward              = CustomerPointReward.create( 
                                customer_acct           = customer_acct, 
                                reward_amount           = reward_amount,
                                transact_outlet         = transact_outlet, 
                                effective_date          = effective_date,
                                expiry_date             = expiry_date, 
                                transaction_id          = transaction_id, 
                                program_key             = self.program_key,
                                rewarded_datetime       = transact_datetime,
                                        
                                )
        
        new_reward_summary          = reward.to_reward_summary()
                    
        if is_not_empty(new_reward_summary):
            #update customer reward summary here
            customer_reward_summary         = customer_acct.reward_summary
            transaction_reward_summary      = referral_reward_transaction.entitled_reward_summary or {}
            
            customer_reward_summary         = update_reward_summary_with_new_reward(customer_reward_summary, new_reward_summary)
            transaction_reward_summary      = update_reward_summary_with_new_reward(transaction_reward_summary, new_reward_summary)
            
            customer_acct.reward_summary                        = customer_reward_summary
            referral_reward_transaction.entitled_reward_summary = transaction_reward_summary
        
            if self.create_upstream:
                create_merchant_customer_reward_upstream_for_merchant(referral_reward_transaction, reward, )
        
        logger.debug('after gave %s point referral reward to %s', reward_amount, customer_acct.name)
    
    def __give_stamp_reward(self, customer_acct, defined_reward_item, referral_reward_transaction, transact_outlet): 
        transaction_id      = referral_reward_transaction.transaction_id
        transact_datetime   = referral_reward_transaction.transact_datetime
        expiration_type     = defined_reward_item.get('expiration_type')
        expiration_value    = defined_reward_item.get('expiration_value')
        effective_date      = transact_datetime.date()
        expiry_date         = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
        
        reward_amount       = defined_reward_item.get('stamp_amount')
        
        reward              = CustomerStampReward.create( 
                                customer_acct           = customer_acct, 
                                reward_amount           = reward_amount,
                                transact_outlet         = transact_outlet, 
                                effective_date          = effective_date,
                                expiry_date             = expiry_date, 
                                transaction_id          = transaction_id, 
                                program_key             = self.program_key,
                                rewarded_datetime       = transact_datetime,
                                )
        
        new_reward_summary          = reward.to_reward_summary()
                    
        if is_not_empty(new_reward_summary):
            #update customer reward summary here
            customer_reward_summary         = customer_acct.reward_summary
            transaction_reward_summary      = referral_reward_transaction.entitled_reward_summary or {}
            
            customer_reward_summary         = update_reward_summary_with_new_reward(customer_reward_summary, new_reward_summary)
            transaction_reward_summary      = update_reward_summary_with_new_reward(transaction_reward_summary, new_reward_summary)
            
            customer_acct.reward_summary                        = customer_reward_summary
            referral_reward_transaction.entitled_reward_summary = transaction_reward_summary
            
            if self.create_upstream:
                create_merchant_customer_reward_upstream_for_merchant(referral_reward_transaction, reward,)
        
        logger.debug('after gave %d stamp referral reward to %s', reward_amount, customer_acct.name)
                                  
    
    def __give_prepaid_reward(self, customer_acct, defined_reward_item, referral_reward_transaction, transact_outlet): 
        transaction_id      = referral_reward_transaction.transaction_id
        transact_datetime   = referral_reward_transaction.transact_datetime
        
        reward_amount       = defined_reward_item.get('prepaid_amount')
        
        reward              = CustomerPrepaidReward.create(
                                customer_acct           = customer_acct, 
                                prepaid_amount          = reward_amount,
                                topup_outlet            = transact_outlet, 
                                transaction_id          = transaction_id, 
                                topup_datetime          = transact_datetime,
                                )
        new_reward_summary          = reward.to_reward_summary()
                    
        if is_not_empty(new_reward_summary):
            #update customer reward summary here
            customer_reward_summary         = customer_acct.reward_summary
            transaction_prepaid_summary     = referral_reward_transaction.entitled_prepaid_summary or {}
            
            customer_reward_summary         = update_reward_summary_with_new_reward(customer_reward_summary, new_reward_summary)
            transaction_prepaid_summary     = update_reward_summary_with_new_reward(transaction_prepaid_summary, new_reward_summary)
            
            customer_acct.prepaid_summary                        = customer_reward_summary
            referral_reward_transaction.entitled_prepaid_summary = transaction_prepaid_summary
            
            if self.create_upstream:
                create_merchant_customer_reward_upstream_for_merchant(referral_reward_transaction, reward, )
        
        logger.debug('after gave %s prepaid referral reward to %s', reward_amount, customer_acct.name)
    
    def __construct_voucher_details(self, voucher_reward_item, transaction_details):
        if transaction_details:
            transact_datetime = transaction_details.transact_datetime
        else:
            transact_datetime = datetime.now()
        
        transact_date       = transact_datetime.date()
        
        effective_date          = None 
        effective_type          = voucher_reward_item.get('effective_type')
        effective_value         = voucher_reward_item.get('effective_value')
        effective_date_str      = voucher_reward_item.get('effective_date')
        
         
        if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE:
            if is_not_empty(effective_date_str):
                effective_date = datetime.strptime(effective_date_str, REWARD_PROGRAM_DATE_FORMAT)
        else:
            effective_date = calculate_effective_date(effective_type, effective_value, start_date = transact_date)
         
        expiration_type         = voucher_reward_item.get('expiration_type')
        expiration_value        = voucher_reward_item.get('expiration_value')
         
        expiry_date             = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
        
        voucher_amount          = voucher_reward_item.get('voucher_amount')
         
        voucher_details         = {
                                    'voucher_key'       : voucher_reward_item.get('voucher_key'),
                                    'use_in_store'      : voucher_reward_item.get('use_in_store'),
                                    'use_online'        : voucher_reward_item.get('use_online'),
                                    'voucher_amount'    : voucher_amount,
                                    'effective_date'    : effective_date,
                                    'expiry_date'       : expiry_date,
                                    }
         
        logger.debug('__construct_voucher_details_list: voucher_details=%s', voucher_details) 
         
        return voucher_details
            
        
        
    
            