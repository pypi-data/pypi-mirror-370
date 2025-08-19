'''
Created on 30 Jun 2023

@author: jacklok
'''
import logging
from trexconf import program_conf
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerEntitledVoucher, CustomerStampReward,\
    VoucherRewardDetailsForUpstreamData
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexprogram.reward_program.reward_program_base import EntitledVoucherSummary
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from datetime import datetime
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.customer_model_helpers import update_prepaid_summary_with_new_prepaid,\
    update_reward_summary_with_new_reward,\
    update_customer_entiteld_voucher_summary_with_new_voucher_info
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_reward_upstream_for_merchant,\
    create_entitled_customer_voucher_upstream_for_merchant
from trexprogram.utils.reward_program_helper import calculate_expiry_date,\
    calculate_effective_date

logger = logging.getLogger('reward-program-lib')

class LuckyDrawRewardProgram():
    
    def __init__(self, program_key=None, drawed_details=None, transact_outlet=None, transaction_details=None, customer_acct=None):
        
        self.drawed_details         = drawed_details
        self.won_prize              = self.drawed_details['won_prize']
        self.prize_type             = self.won_prize['prize_type']
        self.transact_outlet        = transact_outlet
        self.transaction_details    = transaction_details
        self.customer_acct          = customer_acct
        self.program_key            = program_key
        
        logger.debug('LuckyDrawRewardProgram debug: prize_type=%s', self.prize_type)
    
        logger.debug('LuckyDrawRewardProgram debug: customer_acct name=%s', customer_acct.name)
        
    def give(self): 
        transact_datetime   = datetime.utcnow()
        transaction_id      = self.transaction_details.transaction_id
        
        transaction_reward_summary          = self.transaction_details.entitled_reward_summary or {}
        transaction_voucher_summary         = self.transaction_details.entitled_voucher_summary or {}
        transaction_prepaid_summary         = self.transaction_details.entitled_prepaid_summary or {}
        
        customer_reward_summary             = self.customer_acct.reward_summary
        customer_entitled_voucher_summary   = self.customer_acct.entitled_voucher_summary
        customer_prepaid_summary            = self.customer_acct.prepaid_summary
        
        if self.prize_type == program_conf.REWARD_FORMAT_POINT:
            reward_amount       = self.won_prize.get('amount')
            effective_date      = datetime.today()
            expiration_type     = self.won_prize.get('expiration_type')
            expiration_value    = self.won_prize.get('expiration_value')    
            expiry_date         = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
            
            point_reward = CustomerPointReward.create( 
                                            customer_acct       = self.customer_acct, 
                                            reward_amount       = reward_amount,
                                            transact_outlet     = self.transact_outlet, 
                                            effective_date      = effective_date,
                                            expiry_date         = expiry_date, 
                                            transaction_id      = transaction_id, 
                                            rewarded_datetime   = transact_datetime,
                                            )
            
            point_reward_summary          = point_reward.to_reward_summary()
            
            if is_not_empty(point_reward_summary):
                
                customer_reward_summary     = update_reward_summary_with_new_reward(customer_reward_summary, point_reward_summary)
                transaction_reward_summary  = update_reward_summary_with_new_reward(transaction_reward_summary, point_reward_summary)
                
                create_merchant_customer_reward_upstream_for_merchant(self.transaction_details, point_reward, )
            
        elif self.prize_type == program_conf.REWARD_FORMAT_PREPAID:
            reward_amount           = self.won_prize.get('amount')
            prepaid_reward          = CustomerPrepaidReward.topup(self.customer_acct, 
                                                               reward_amount, 
                                                               None, 
                                                               topup_outlet     = self.transact_outlet, 
                                                               transaction_id   = transaction_id,
                                                               )

            
            new_prepaid_summary         = prepaid_reward.to_prepaid_summary()
            if is_not_empty(new_prepaid_summary):
                
                customer_prepaid_summary    = update_prepaid_summary_with_new_prepaid(customer_prepaid_summary, new_prepaid_summary)
                transaction_prepaid_summary = update_prepaid_summary_with_new_prepaid(transaction_prepaid_summary, new_prepaid_summary)
                
                create_merchant_customer_reward_upstream_for_merchant(self.transaction_details, prepaid_reward,)
        
        
        elif self.prize_type == program_conf.REWARD_FORMAT_STAMP:
            reward_amount       = self.won_prize.get('voucher_amount')
            effective_date      = datetime.today()
            expiration_type     = self.won_prize.get('expiration_type')
            expiration_value    = self.won_prize.get('expiration_value')    
            expiry_date         = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
            
            stamp_reward    = CustomerStampReward.create( 
                                        customer_acct       = self.customer_acct, 
                                        reward_amount       = reward_amount,
                                        transact_outlet     = self.transact_outlet, 
                                        expiry_date         = expiry_date, 
                                        effective_date      = effective_date,
                                        transaction_id      = transaction_id, 
                                        rewarded_datetime   = transact_datetime,
                                        )
        
            stamp_reward_summary          = stamp_reward.to_reward_summary()
            
            if is_not_empty(stamp_reward_summary):
                
                customer_reward_summary     = update_reward_summary_with_new_reward(customer_reward_summary, stamp_reward_summary)
                transaction_reward_summary  = update_reward_summary_with_new_reward(transaction_reward_summary, stamp_reward_summary)
                
                create_merchant_customer_reward_upstream_for_merchant(self.transaction_details, stamp_reward, )
        
        elif self.prize_type == program_conf.REWARD_FORMAT_VOUCHER:
            voucher_key         = self.won_prize.get('voucher_key')
            voucher_amount      = self.won_prize.get('voucher_amount')
            effective_type      = self.won_prize.get('effective_type')
            effective_value     = self.won_prize.get('effective_value')
            effective_date      = self.won_prize.get('effective_date')
            expiration_type     = self.won_prize.get('expiration_type')
            expiration_value    = self.won_prize.get('expiration_value')
            
            if effective_date is not None:
                effective_date = datetime.strptime('%d-%m-%Y', effective_date).date()
            else:
                effective_date  = calculate_effective_date(effective_type, effective_value)
            
            merchant_voucher = MerchantVoucher.fetch(voucher_key)
            
            entiteld_voucher_brief  = EntitledVoucherSummary(transaction_id=transaction_id)
            customer_voucher_list   = []
            
            if merchant_voucher:
                
                expiry_date   = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
                
                logger.debug('LuckyDrawRewardProgram debug: merchant_voucher=%s', merchant_voucher)
                
                for v in range(voucher_amount):
                    
                    customer_voucher = CustomerEntitledVoucher.create(
                                                                merchant_voucher,
                                                                self.customer_acct, 
                                                                transact_outlet     = self.transact_outlet,
                                                                transaction_id      = transaction_id,
                                                                rewarded_datetime   = transact_datetime,
                                                                effective_date      = effective_date,
                                                                expiry_date         = expiry_date,
                                                                program_key         = self.program_key,
                                                                
                                                                )
                    customer_voucher_list.append(customer_voucher)
                    create_entitled_customer_voucher_upstream_for_merchant(customer_voucher)
            
                entiteld_voucher_brief.add(merchant_voucher, customer_voucher_list)    
                
                
                voucher_summary_list = entiteld_voucher_brief.entitled_voucher_summary_list
                '''
                if is_not_empty(voucher_summary_list):
                    is_new_reward_gave = True
                '''
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
                                                                                #'voucher_key'       : voucher_key,
                                                                                #'amount'            : voucher_summary.get('amount'),
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
                            
                            create_merchant_customer_reward_upstream_for_merchant(self.transaction_details, 
                                                                                  voucher_reward_brief, )
            
            
        self.customer_acct.reward_summary            = customer_reward_summary
        self.customer_acct.entitled_voucher_summary  = customer_entitled_voucher_summary
        self.customer_acct.prepaid_summary           = customer_prepaid_summary
        
        
        self.customer_acct.put()
        
        self.transaction_details.entitled_reward_summary     = transaction_reward_summary
        self.transaction_details.entitled_prepaid_summary    = transaction_prepaid_summary
        self.transaction_details.entitled_voucher_summary    = transaction_voucher_summary    
        
        self.transaction_details.put()
            
    '''    
    def calculate_expiry_date(self, expiration_type, expiration_value, start_date=None):
        expiry_date = None
        
        logger.debug('calculate_expiry_date: expiration_type=%s', expiration_type)
        logger.debug('calculate_expiry_date: expiration_value=%s', expiration_value)
        
        if start_date is None:
            start_date = datetime.now().date()
        
        if expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR:
            expiry_date = start_date + relativedelta(years=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH:
            expiry_date =  start_date + relativedelta(months=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK:
            expiry_date =  start_date + relativedelta(weeks=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY:
            expiry_date =  start_date + relativedelta(days=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE:
            expiry_date =  datetime.strptime(expiration_value, DATE_FORMAT)
        
        if isinstance(expiry_date, date):
            return expiry_date
        else:
            return expiry_date.date()   
    
    def calculate_effective_date(self, effective_type, effective_value, start_date=None):
        if start_date is None:
            start_date = datetime.now().date()
        
        if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH:
            return start_date + relativedelta(months=effective_value)
        
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK:
            return start_date + relativedelta(weeks=effective_value)
        
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY:
            return start_date + relativedelta(days=effective_value)
        
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_IMMEDIATE:
            return start_date
    '''