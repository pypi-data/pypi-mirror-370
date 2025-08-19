'''
Created on 20 Apr 2021

@author: jacklok
'''
from datetime import datetime
from dateutil.relativedelta import relativedelta
from trexconf import conf as app_conf
from trexconf import program_conf
import logging
from trexlib.utils.string_util import is_empty, is_not_empty
from trexlib.utils.common.currency_util import currency_amount_based_on_currency
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from datetime import date, timedelta
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexconf.program_conf import REWARD_PROGRAM_DATE_FORMAT
from trexprogram.utils.reward_program_helper import calculate_expiry_date,\
    calculate_effective_date
from trexconf.config_util import get_currency_config_by_currency_code
from trexanalytics.bigquery_upstream_data_config import create_entitled_customer_voucher_upstream_for_merchant

#logger = logging.getLogger('reward-program-lib')
logger = logging.getLogger('target_debug')


#DATE_FORMAT = '%d-%m-%Y'

class RewardProgramBase(object):
    """
    Define the interface for reward program
    """

    def __init__(self, merchant_acct, program_configuration):
        self.merchant_acct          = merchant_acct
        self.currency_config        = get_currency_config_by_currency_code(merchant_acct.currency_code)
        self.program_configuration  = program_configuration
        self.program_label          = program_configuration.get('label')
        self.program_key            = self.program_configuration.get('program_key')
        self.desc                   = program_configuration.get('desc')
        self.program_settings       = program_configuration.get('program_settings')
        self.start_date             = program_configuration.get('start_date')
        self.end_date               = program_configuration.get('end_date')
        self.scheme                 = self.program_settings.get('scheme')
        
        logger.debug('----------------------------------------')
        logger.debug('self.program_configuration=%s', self.program_configuration)
        logger.debug('self.program_key=%s', self.program_key)
        logger.debug('self.program_settings=%s', self.program_settings)
        logger.debug('self.scheme=%s', self.scheme)
        
        self.start_date             = datetime.strptime(self.start_date, '%d-%m-%Y').date()
        self.end_date               = datetime.strptime(self.end_date, '%d-%m-%Y').date()
        self.limit_to_specific_day  = self.scheme.get('limit_to_specific_day', False) if is_not_empty(self.scheme) else False
        self.specified_days_list    = self.scheme.get('specified_days_list', []) if is_not_empty(self.scheme) else []
        
        self.limit_to_specific_date_of_month  = self.scheme.get('limit_to_specific_date_of_month', False) if is_not_empty(self.scheme) else False
        self.specified_dates_of_month_list    = self.scheme.get('specified_dates_of_month_list', []) if is_not_empty(self.scheme) else []
        
        self.is_recurring_scheme    = self.scheme.get('is_recurring_scheme', False) if is_not_empty(self.scheme) else False
        self.__process_exclusivity(self.program_settings.get('exclusivity'))

    def give(self, customer_acct, transaction_details): 
        pass
    
    def __process_exclusivity(self, exclusivity):
        
        if exclusivity and len(exclusivity)>0:
            tags                = exclusivity.get('tags')
            memberships         = exclusivity.get('memberships')
            tier_memberships    = exclusivity.get('tier_memberships')
            promotion_codes     = exclusivity.get('promotion_codes')
            
            if tags and tags!='None' and len(tags)>0:
                self.exclusivity_tags = tags
            else:
                self.exclusivity_tags = []
                
            if promotion_codes and promotion_codes!='None' and len(promotion_codes)>0:
                self.exclusivity_promotion_codes = promotion_codes
            else:
                self.exclusivity_promotion_codes = []    
            
            if memberships and memberships!='None' and len(memberships)>0:
                self.exclusivity_memberships = memberships
            else:
                self.exclusivity_memberships = []
            
            if tier_memberships and tier_memberships!='None' and len(tier_memberships)>0:
                self.exclusivity_tier_memberships = tier_memberships
            else:
                self.exclusivity_tier_memberships = []
        else:
            self.exclusivity_tags               = []
            self.exclusivity_memberships        = []
            self.exclusivity_tier_memberships   = []
            self.exclusivity_promotion_codes    = []
    
    def get_balance_of_reward_amount_limit(self, customer_acct, transaction_details):
        return program_conf.MAX_REWARD_AMOUNT
    
    def is_eligible_for_limited_to_specific_day_condition(self, transaction_details):
        logger.debug('is_eligible_for_limited_to_specific_day_condition(%s) debug: limit_to_specific_day=%s', self.program_label, self.limit_to_specific_day)
        
        if self.limit_to_specific_day:
            
            eligible_for_specific_day = False
            logger.debug('is_eligible_for_limited_to_specific_day_condition(%s) debug: specified_days_list=%s', self.program_label, self.specified_days_list)
            
            if is_not_empty(self.specified_days_list):
                transact_datetime               = transaction_details.transact_datetime
                logger.debug('is_eligible_for_limited_to_specific_day_condition(%s) debug: transact_datetime=%s', self.program_label, transact_datetime)
                
                gmt_hour = self.merchant_acct.gmt_hour
                
                transact_datetime_in_gmt = transact_datetime + timedelta(hours=gmt_hour)
                logger.debug('is_eligible_for_limited_to_specific_day_condition(%s) debug: transact_datetime_in_gmt=%s', self.program_label, transact_datetime_in_gmt)
                
                transact_weekday = transact_datetime_in_gmt.weekday()
                logger.debug('is_eligible_for_limited_to_specific_day_condition(%s) debug: transact_weekday=%s', self.program_label, transact_weekday)
                
                for weekday in self.specified_days_list:
                    if transact_weekday == int(weekday):
                        eligible_for_specific_day = True
                        break
                    
            if eligible_for_specific_day==False:
                logger.debug('Not eligible for specific day to get reward')
                return 
            else:
                logger.debug('Eligible for specific day to get reward')
            
            return eligible_for_specific_day
        else:
            logger.debug('Not limit to specific day condition')
            return True
        
    def is_eligible_for_limited_to_specific_date_of_month_condition(self, transaction_details):
        logger.debug('is_eligible_for_limited_to_specific_date_of_month_condition(%s) debug: limit_to_specific_date_of_month=%s', self.program_label, self.limit_to_specific_date_of_month)
        
        if self.limit_to_specific_date_of_month:
            
            eligible_for_specific_date_of_month = False
            logger.debug('is_eligible_for_limited_to_specific_date_of_month_condition(%s) debug: specified_dates_of_month_list=%s', self.program_label, self.specified_dates_of_month_list)
            
            if is_not_empty(self.specified_dates_of_month_list):
                transact_datetime               = transaction_details.transact_datetime
                logger.debug('is_eligible_for_limited_to_specific_date_of_month_condition(%s) debug: transact_datetime=%s', self.program_label, transact_datetime)
                
                gmt_hour = self.merchant_acct.gmt_hour
                
                transact_datetime_in_gmt = transact_datetime + timedelta(hours=gmt_hour)
                logger.debug('is_eligible_for_limited_to_specific_date_of_month_condition(%s) debug: transact_datetime_in_gmt=%s', self.program_label, transact_datetime_in_gmt)
                
                day_of_month = transact_datetime_in_gmt.day
                logger.debug('is_eligible_for_limited_to_specific_date_of_month_condition(%s) debug: day_of_month=%s', self.program_label, day_of_month)
                
                for date_in_string in self.specified_dates_of_month_list:
                    if day_of_month == int(date_in_string):
                        eligible_for_specific_date_of_month = True
                        break
                    
            if eligible_for_specific_date_of_month==False:
                logger.debug('Not eligible for specific date of month to get reward')
                return 
            else:
                logger.debug('Eligible for specific date of month to get reward')
            
            return eligible_for_specific_date_of_month
        else:
            logger.debug('Not limit to specific date of month condition')
            return True    
    
    def is_eligible_based_on_exclusivity(self, customer_acct):
        logger.debug('is_eligible_based_on_exclusivity: self.exclusivity_tags=%s', self.exclusivity_tags)
        logger.debug('is_eligible_based_on_exclusivity: self.exclusivity_memberships=%s', self.exclusivity_memberships)
        logger.debug('is_eligible_based_on_exclusivity: self.exclusivity_tier_memberships=%s', self.exclusivity_tier_memberships)
        logger.debug('is_eligible_based_on_exclusivity: self.exclusivity_promotion_codes=%s', self.exclusivity_promotion_codes)
        
        logger.debug('is_eligible_based_on_exclusivity: customer_acct.tags_list=%s', customer_acct.tags_list)
        logger.debug('is_eligible_based_on_exclusivity: customer_acct.memberships_list=%s', customer_acct.memberships_list)
        logger.debug('is_eligible_based_on_exclusivity: customer_acct.tier_membership=%s', customer_acct.tier_membership)
        
        if is_not_empty(self.exclusivity_tags) or is_not_empty(self.exclusivity_memberships) or is_not_empty(self.exclusivity_tier_memberships):  
            if is_not_empty(self.exclusivity_tags):
                for tag in customer_acct.tags_list:
                    if tag in self.exclusivity_tags:
                        return True
                    
            if is_not_empty(self.exclusivity_memberships):
                for m in customer_acct.memberships_list:
                    if m in self.exclusivity_memberships:
                        return True
                    
            if is_not_empty(self.exclusivity_tier_memberships):
                if customer_acct.tier_membership in self.exclusivity_tier_memberships:
                    return True
            
            return False
        else:
            return True        
        
    def get_giveaway_reward_sales_amount(self, transaction_details):
        
        transact_amount             = transaction_details.transact_amount
        tax_amount                  = transaction_details.tax_amount
        
        giveaway_reward_sales_amount = transact_amount - tax_amount
        
        return giveaway_reward_sales_amount 
    
    def get_reward_format(self):
        pass
    
    '''
    def calculate_expiry_date(self, expiration_type, expiration_value, start_date=None):
        expiry_date = None
        
        logger.debug('calculate_expiry_date: expiration_type=%s', expiration_type)
        logger.debug('calculate_expiry_date: expiration_value=%s', expiration_value)
        
        if start_date is None:
            start_date = datetime.utcnow().date()
        
        if expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_YEAR:
            expiry_date = start_date + relativedelta(years=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_MONTH:
            expiry_date =  start_date + relativedelta(months=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_WEEK:
            expiry_date =  start_date + relativedelta(weeks=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_AFTER_DAY:
            expiry_date =  start_date + relativedelta(days=expiration_value)
        
        elif expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE:
            expiry_date =  datetime.strptime(expiration_value, REWARD_PROGRAM_DATE_FORMAT)
        
        if isinstance(expiry_date, date):
            return expiry_date
        else:
            return expiry_date.date()   
    
    
    def calculate_effective_date(self, effective_type, effective_value, start_date=None):
        if start_date is None:
            start_date = datetime.utcnow().date()
        
        if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_MONTH:
            return start_date + relativedelta(months=effective_value)
        
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_WEEK:
            return start_date + relativedelta(weeks=effective_value)
        
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_AFTER_DAY:
            return start_date + relativedelta(days=effective_value)
        
        elif effective_type == program_conf.REWARD_EFFECTIVE_TYPE_IMMEDIATE:
            return start_date
    '''
class SchemeBaseRewardProgram(RewardProgramBase):
    
    def __init__(self, merchant_acct, program_configuration):
        super(SchemeBaseRewardProgram, self).__init__(merchant_acct, program_configuration)
        
        self.is_recurring_scheme    = self.program_settings.get('is_recurring_scheme')
        self.spending_currency      = self.program_settings.get('scheme').get('spending_currency')
        self.reward_amount          = self.program_settings.get('scheme').get('reward_amount')
        self.is_recurring_scheme    = self.program_settings.get('scheme').get('is_recurring_scheme')
        self.rounding_type          = self.program_settings.get('rounding_type') or app_conf.ROUNDING_TYPE_ROUND_DOWN
        self.currency               = self.currency_config
        self.expiration_type        = self.program_settings.get('scheme').get('expiration_type')
        self.expiration_value       = self.program_settings.get('scheme').get('expiration_value')
        self.expiration_date        = self.program_settings.get('scheme').get('expiration_date')
        self.reward_limit_type      = self.program_settings.get('scheme').get('reward_limit_type')
        self.reward_limit_amount    = self.program_settings.get('scheme').get('reward_limit_amount')
        self.program_key            = program_configuration.get('program_key')
    
    def get_balance_of_reward_amount_limit(self, customer_acct, transaction_details):
        if is_not_empty(self.reward_limit_type) and self.reward_limit_type!=program_conf.REWARD_LIMIT_TYPE_NO_LIMIT:
            if self.reward_limit_type == program_conf.REWARD_LIMIT_TYPE_BY_TRANSACTION:
                balance_of_maximum_reward_amount = float(self.reward_limit_amount)
            else:
                checking_transact_datetime_from = None
                
                transact_datetime = transaction_details.transact_datetime
                transaction_id    = transaction_details.transaction_id
                logger.debug('reward_limit_type=%s', self.reward_limit_type)    
                
                if self.reward_limit_type == program_conf.REWARD_LIMIT_TYPE_BY_DAY:
                    #checking_transact_datetime_from = transact_datetime - relativedelta(days=1)
                    checking_transact_datetime_from = transact_datetime
                    
                elif self.reward_limit_type == program_conf.REWARD_LIMIT_TYPE_BY_WEEK:
                    #checking_transact_datetime_from = transact_datetime - relativedelta(weeks=1)
                    checking_transact_datetime_from = transact_datetime - relativedelta(weeks=1)
                    
                    
                elif self.reward_limit_type == program_conf.REWARD_LIMIT_TYPE_BY_MONTH:
                    checking_transact_datetime_from = transact_datetime - relativedelta(months=1)        
                
                #change checking_transact_datetime_from start from date 00:00 datetime
                checking_transact_datetime_from = datetime.combine(checking_transact_datetime_from.date(), datetime.min.time())
                
                tansaction_list = CustomerTransaction.list_customer_transaction_by_transact_datetime(customer_acct, 
                                                                                   transact_datetime_from   = checking_transact_datetime_from, 
                                                                                   transact_datetime_to     = transact_datetime)
                checking_reward_format = self.get_reward_format()
                
                logger.debug('checking program_key=%s', self.program_key)
                logger.debug('checking_reward_format=%s', checking_reward_format)
                
                accumulated_reward_amount = .0
                for transaction in tansaction_list:
                    if transaction.is_revert == False:
                        if transaction_id!=transaction.transaction_id:
                            transaction_reward_summary = transaction.entitled_reward_summary
                            if transaction_reward_summary:
                                logger.info('>>> passed transaction_reward_summary=%s', transaction_reward_summary)
                                target_reward_summary = transaction_reward_summary.get(checking_reward_format)
                                if target_reward_summary:
                                    
                                    reward_source_list = target_reward_summary.get('sources')
                                    if reward_source_list:
                                        for reward_source in reward_source_list:
                                            program_key = reward_source.get('program_key')
                                            if program_key == self.program_key:
                                                transaction_reward_amount = reward_source.get('amount') or .0
                                                accumulated_reward_amount += transaction_reward_amount
                                    '''
                                    transaction_reward_amount = target_reward_summary.get('amount')
                                    accumulated_reward_amount += transaction_reward_amount
                                    '''
                                    logger.debug('accumulated_reward_amount=%f', accumulated_reward_amount)
                    
                balance_of_maximum_reward_amount = float(self.reward_limit_amount) - accumulated_reward_amount
                
                logger.debug('balance_of_maximum_reward_amount=%f from %s till %s', balance_of_maximum_reward_amount, checking_transact_datetime_from, transact_datetime)
            
                if balance_of_maximum_reward_amount<0:
                    return .0
            
            return balance_of_maximum_reward_amount
        else:
            return program_conf.MAX_REWARD_AMOUNT 
    
    def calculate_reward_unit(self, transaction_amount ):

        
        logger.debug('transaction_amount=%s', transaction_amount)
        logger.debug('self.spending_currency=%s', self.spending_currency)
        logger.debug('currency=%s', self.currency)
        
        
        if self.spending_currency and transaction_amount >= self.spending_currency:
            
            if self.is_recurring_scheme:
                logger.debug('recurring scheme program')    
                currency_amount = currency_amount_based_on_currency(self.currency, self.spending_currency)
    
                if self.rounding_type == app_conf.ROUNDING_TYPE_ROUND_DOWN or is_empty(self.rounding_type):
                    logger.debug('round down')
                    reward_unit = int(transaction_amount/self.spending_currency)
    
                elif self.rounding_type == app_conf.ROUNDING_TYPE_ROUND_UP:
                    logger.debug('round up')
                    round_up_unit       = currency_amount / 2
    
                    decimal_remaining   = transaction_amount % currency_amount
                    decimal_remaining   = currency_amount_based_on_currency(self.currency, decimal_remaining)
    
                    decimal_remaining_difference = currency_amount - decimal_remaining
    
                    if round_up_unit>0.5:
                        round_up_unit = 0.5
    
                    round_up_half_unit       = currency_amount_based_on_currency(self.currency, round_up_unit)
    
                    logger.debug('transaction_amount=%s', transaction_amount)
                    logger.debug('currency_amount=%s', currency_amount)
                    logger.debug('decimal_remaining=%s', decimal_remaining)
                    logger.debug('round_up_half_unit=%s', round_up_half_unit)
                    logger.debug('decimal_remaining_difference=%s', decimal_remaining_difference)
                    logger.debug('decimal_remaining_difference > round_up_half_unit=%s', (decimal_remaining_difference > round_up_half_unit))
    
                    if decimal_remaining_difference > round_up_half_unit:
                        logger.debug('have to round down')
                        reward_unit = int(transaction_amount/currency_amount)
                    else:
                        logger.debug('yes, round up')
                        is_two_decimal_currency_amount = (currency_amount*100) <10
                        logger.debug('is_two_decimal_currency_amount=%s', is_two_decimal_currency_amount)
                        
                        if is_two_decimal_currency_amount:
                            reward_unit = int(transaction_amount/currency_amount)
                        else:
                            reward_unit = int(transaction_amount/currency_amount) + 1
                            
            else:
                logger.debug('not recurring scheme program')
                
                reward_unit = 1
            
            return reward_unit
          
        else:
            return 1
        
    
    
class SchemeRewardProgram(SchemeBaseRewardProgram):
    
    def __init__(self, merchant_acct, program_configuration):
        super(SchemeRewardProgram, self).__init__(merchant_acct, program_configuration)
        self.expiration_type        = self.program_settings.get('scheme').get('expiration_type')
        self.expiration_value       = self.program_settings.get('scheme').get('expiration_value')
        
        
    def calculate_entitle_reward_amount(self, reward_unit=1):
        logger.debug('calculate_entitle_reward_amount reward_amount=%s', self.reward_amount)
        if reward_unit and self.reward_amount:
            if self.is_recurring_scheme:
                reward_value = self.reward_amount * reward_unit
                return reward_value
            else:
                return reward_unit
        else:
            return 0
    
class GiveawayRewardBaseProgram(RewardProgramBase):
    def __init__(self, merchant_acct, program_configuration, reward_set=1):
        super(GiveawayRewardBaseProgram, self).__init__(merchant_acct, program_configuration)
        
        if self.program_settings.get('scheme') is not None:
            self.expiration_type        = self.program_settings.get('scheme').get('expiration_type')
            self.expiration_value       = self.program_settings.get('scheme').get('expiration_value')   
        self.reward_set             = reward_set 
    
    
    def calculate_entitle_reward_amount(self, reward_set=1):
        return self.reward_amount * reward_set
         
    
    def calculate_reward_unit(self, transaction_amount):
        return 1
    
    def __repr__(self):
        return "%s - reward_set=%d, " % (self.__class__.__name__, self.reward_set)
        
class EntitledVoucherSummary(object):
    
    def __init__(self, transaction_id=None):
        self.__vouchers_label_list              = []
        self.__entitled_voucher_summary_list    = []
        self.__voucher_mapping                  = {}
        self.reach_limit                        = False
        self.transaction_id                     = transaction_id
        
    def add(self, voucher, customer_voucher_list):
        voucher_key     = voucher.key_in_str
        voucher_details = self.__voucher_mapping.get(voucher_key)
        
        if voucher_details:
            voucher_details['amount'] += len(customer_voucher_list)
            
            redeem_info_list = voucher_details.get('redeem_info_list')
            
            for v in customer_voucher_list:
                voucher_redeem_info = {
                                        'redeem_code'       : v.redeem_code,
                                        'effective_date'    : v.effective_date.strftime('%d-%m-%Y'),
                                        'expiry_date'       : v.expiry_date.strftime('%d-%m-%Y'),
                                        'is_redeem'         : False, 
                                    }
                
                redeem_info_list.append(voucher_redeem_info)
            
        else:
            voucher_details = {
                                'key'           : voucher_key,
                                'label'         : voucher.label,
                                'configuration' : voucher.configuration,
                                'image_url'     : voucher.image_public_url,
                                'amount'        : len(customer_voucher_list),
                                }
            
            redeem_info_list = []
            
            for v in customer_voucher_list:
                voucher_redeem_info = {
                                        'redeem_code'       : v.redeem_code,
                                        'effective_date'    : v.effective_date.strftime('%d-%m-%Y'),
                                        'expiry_date'       : v.expiry_date.strftime('%d-%m-%Y'),
                                        'is_redeem'         : False, 
                                    }
                
                redeem_info_list.append(voucher_redeem_info)
                
            voucher_details['redeem_info_list'] = redeem_info_list
        
        self.__voucher_mapping[voucher_key] = voucher_details
                
    def __voucher_label_and_amount_brief(self):
        return ['{} x {}'.format(v.get('label'), v.get('amount')) for v in self.entitled_voucher_summary_list  ]
    
    @property
    def reward_brief(self):
        return 'Entitled {voucher_list}'.format(voucher_list=self.entitled_voucher_summary_list)
    
    @property
    def entitled_voucher_summary_list(self):
        return self.__voucher_mapping.values()
    
    @property
    def entitled_voucher_summary(self):
        return self.__voucher_mapping
    
    def __str__(self):
        return self.reward_brief

    def __repr__(self):
        return self.__voucher_label_and_amount_brief
        
        
class VoucherRewardProgramBase(GiveawayRewardBaseProgram):
    
    def __init__(self, merchant_acct, program_configuration):
        super(VoucherRewardProgramBase, self).__init__(merchant_acct, program_configuration)
        self.voucher_details_list   = self.program_settings.get('reward_items') or []
        self.reward_format          = program_configuration.get('reward_format')
        self.giveaway_method        = program_configuration.get('giveaway_method')
        self.program_key                = program_configuration.get('program_key')
        
    def construct_giveaway_voucher_details_list(self, transaction_details, reward_unit):
        voucher_giveaway_list = []
        logger.debug('self.voucher_details_list=%s', self.voucher_details_list)
        logger.debug('self.reward_unit=%s', reward_unit)
        if is_not_empty(self.voucher_details_list):
            
            if transaction_details:
                transact_datetime = transaction_details.transact_datetime
            else:
                transact_datetime = datetime.now()
            
            transact_date       = transact_datetime.date()
            
            for voucher in self.voucher_details_list:
                
                effective_date          = None 
                effective_type          = voucher.get('effective_type')
                effective_value         = voucher.get('effective_value')
                effective_date_str      = voucher.get('effective_date')
                
                 
                if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE:
                    if is_not_empty(effective_date_str):
                        effective_date = datetime.strptime(effective_date_str, REWARD_PROGRAM_DATE_FORMAT)
                else:
                    effective_date = calculate_effective_date(effective_type, effective_value, start_date = transact_date)
                 
                expiration_type         = voucher.get('expiration_type')
                expiration_value        = voucher.get('expiration_value')
                 
                expiry_date             = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
                
                voucher_amount          = voucher.get('voucher_amount')
                final_voucher_amount    = voucher_amount * reward_unit
                
                logger.debug('final_voucher_amount=%s', final_voucher_amount)
                
                voucher_details         = {
                                            'voucher_key'       : voucher.get('voucher_key'),
                                            'use_in_store'      : voucher.get('use_in_store'),
                                            'use_online'        : voucher.get('use_online'),
                                            'voucher_amount'    : final_voucher_amount,
                                            'effective_date'    : effective_date,
                                            'expiry_date'       : expiry_date,
                                             
                                            }
                 
                logger.debug('construct_giveaway_voucher_details_list2: voucher_details=%s', voucher_details) 
                 
                voucher_giveaway_list.append(voucher_details)
        
        return voucher_giveaway_list
    
    def give(self, customer_acct, transaction_details, reward_set=1):
        if self.is_eligible_based_on_exclusivity(customer_acct) \
            and self.is_eligible_for_limited_to_specific_day_condition(transaction_details) \
            and self.is_eligible_for_limited_to_specific_date_of_month_condition(transaction_details):
            
            transaction_id          = transaction_details.transaction_id
            entiteld_voucher_brief  = EntitledVoucherSummary(transaction_id=transaction_id)
            logger.debug('VoucherRewardGiveawayBase: Going to give reward')
            
            sales_amount            = self.get_giveaway_reward_sales_amount(transaction_details) if transaction_details else 0
            reward_unit             = self.calculate_reward_unit(sales_amount)

            balance_of_reward_unit_limit    = self.get_balance_of_reward_amount_limit(customer_acct, transaction_details)
                
            logger.info('reward_unit=%s', reward_unit)
            logger.info('balance_of_reward_unit_limit=%s', balance_of_reward_unit_limit)
            
            if reward_unit > balance_of_reward_unit_limit:
                reward_unit = balance_of_reward_unit_limit
                logger.info('changed to balance of reward unit limit')
                
                entiteld_voucher_brief.reach_limit = True
            
            if reward_unit>0:
                logger.info('going to construct giveaway voucher details')
                vouchers_list = self.construct_giveaway_voucher_details_list(transaction_details, reward_unit)
                
                transact_outlet     = transaction_details.transact_outlet_details
                invoice_id          = transaction_details.invoice_id
                transact_by_user    = transaction_details.transact_by_user
                transact_datetime   = transaction_details.transact_datetime
                
                for voucher in vouchers_list:
                    merchant_voucher = MerchantVoucher.fetch(voucher.get('voucher_key'))
                    if merchant_voucher:
                        
                        effective_date              = voucher.get('effective_date')
                        expiry_date                 = voucher.get('expiry_date')
                        voucher_amount              = voucher.get('voucher_amount') * reward_set
                        
                        customer_voucher_list       = [] 
                        voucher_amount_int = int(voucher_amount)
                        
                        logger.info('voucher_amount_int=%d', voucher_amount_int)
                        
                        
                        for v in range(voucher_amount_int):
                            customer_voucher = CustomerEntitledVoucher.create(
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
                            
                            customer_voucher_list.append(customer_voucher)
                            create_entitled_customer_voucher_upstream_for_merchant(customer_voucher) 
                            
                        entiteld_voucher_brief.add(merchant_voucher, 
                                                   customer_voucher_list)
                            
                    else:
                        logger.warn('Voucher is not found for voucher_key=%s', voucher.get('voucher_key'))
            else:
                logger.info('not voucher to giveaway')
            
            logger.info('entiteld_voucher_brief=%s', entiteld_voucher_brief)    
            
            return entiteld_voucher_brief
            
        else:
            logger.debug('Not eligible to get reward')
            
            
class VoucherSchemeRewardProgramBase(SchemeRewardProgram, VoucherRewardProgramBase):
    def __init__(self, merchant_acct, program_configuration):
        super(VoucherSchemeRewardProgramBase, self).__init__(merchant_acct, program_configuration)
    