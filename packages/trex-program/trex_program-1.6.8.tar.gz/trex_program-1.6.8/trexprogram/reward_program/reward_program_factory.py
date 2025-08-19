'''
Created on 21 Apr 2021

@author: jacklok
'''
from trexconf import program_conf
from trexprogram.reward_program.point_reward_program import PointSchemeProgram,\
    PointGiveawayProgram
from trexprogram.reward_program.stamp_reward_program import StampSchemeProgram,\
    StampGiveawayProgram
import logging
from datetime import datetime
from trexprogram.reward_program.voucher_reward_program import VoucherProgram,\
    VoucherSchemeProgram
from trexmodel.models.datastore.reward_models import CustomerCountableReward,\
    VoucherRewardDetailsForUpstreamData
from trexmodel.models.datastore.customer_model_helpers import update_reward_summary_with_new_reward,\
    update_customer_entiteld_voucher_summary_with_new_voucher_info,\
    update_prepaid_summary_with_new_prepaid
from trexprogram.reward_program.reward_program_base import EntitledVoucherSummary
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_reward_upstream_for_merchant,\
    create_merchant_customer_prepaid_upstream_for_merchant
from collections import OrderedDict
import time
from trexlib.utils.string_util import is_not_empty
from trexprogram.reward_program.tier_reward_program import TierRewardProgram
from trexprogram.reward_program.prepaid_program import PrepaidSchemeProgram,\
    PrepaidGiveawayProgram
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from _datetime import timedelta
from trexprogram.reward_program.promotion_reward_program import PromotionRewardProgram

#logger = logging.getLogger('reward-program-lib')
logger = logging.getLogger('target_debug')

class RewardProgramFactory:
    
    def __init__(self, merchant_acct):
        self.merchant_acct  = merchant_acct
        
    
    def create_program_list(self):
        programs_list = []
        published_program_configurations = self.merchant_acct.published_program_configuration.get('programs')
        
        for program_configuration in  published_program_configurations:
            program = self.__construct_reward_program(program_configuration)
            if program is not None:
                programs_list.append(program) 
        
        return programs_list
    
    def __get_spending_mechanism_reward_program(self, program_configuration, currency=None):
        desc            = program_configuration.get('desc')
        reward_base     = program_configuration.get('reward_base')
        reward_format   = program_configuration.get('reward_format')
        
        logger.debug('--------> desc=%s', desc)
        logger.debug('--------> reward_base=%s', reward_base)
        logger.debug('--------> reward_format=%s', reward_format)
        
        if reward_base == program_conf.REWARD_BASE_ON_SPENDING:
            if reward_format == program_conf.REWARD_FORMAT_POINT:
                return PointSchemeProgram(self.merchant_acct, program_configuration, currency=currency)
            
            elif reward_format == program_conf.REWARD_FORMAT_STAMP:
                return StampSchemeProgram(self.merchant_acct, program_configuration, currency=currency)
            
            elif reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                return VoucherProgram(self.merchant_acct, program_configuration, currency=currency)
        
        elif reward_base == program_conf.REWARD_BASE_ON_PROMOTION_SPENDING:
            return PromotionRewardProgram(self.merchant_acct, program_configuration, currency=currency)
            
            
    def __get_giveaway_mechanism_reward_program(self, program_configuration, currency=None):
        desc            = program_configuration.get('desc')
        reward_base     = program_configuration.get('reward_base')
        reward_format   = program_configuration.get('reward_format')
        
        logger.debug('--------> desc=%s', desc)
        logger.debug('--------> reward_base=%s', reward_base)
        logger.debug('--------> reward_format=%s', reward_format)
        
        if reward_base == program_conf.REWARD_BASE_ON_GIVEAWAY or reward_base == program_conf.REWARD_BASE_ON_BIRTHDAY:
            if reward_format == program_conf.REWARD_FORMAT_POINT:
                return PointGiveawayProgram(self.merchant_acct, program_configuration, currency=currency)
            
            elif reward_format == program_conf.REWARD_FORMAT_STAMP:
                return StampGiveawayProgram(self.merchant_acct, program_configuration, currency=currency)
            
            elif reward_format == program_conf.REWARD_FORMAT_PREPAID:
                return PrepaidGiveawayProgram(self.merchant_acct, program_configuration, currency=currency)
            
            elif reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                return VoucherProgram(self.merchant_acct, program_configuration, currency=currency)
        
        elif reward_base == program_conf.REWARD_BASE_ON_TIER:
            return TierRewardProgram(self.merchant_acct, program_configuration)
        
    def __construct_reward_program(self, program_configuration, transact_datetime=None, promotion_code=None):
        desc                    = program_configuration.get('desc')
        reward_base             = program_configuration.get('reward_base')
        reward_format           = program_configuration.get('reward_format')
        start_date              = program_configuration.get('start_date')
        end_date                = program_configuration.get('end_date') 
        
        logger.debug('--------> start_date=%s', start_date)
        logger.debug('--------> end_date=%s', end_date)
        
        start_date      = datetime.strptime(start_date, '%d-%m-%Y').date()
        end_date        = datetime.strptime(end_date, '%d-%m-%Y').date()
        
        if transact_datetime is None:
            transact_datetime = datetime.utcnow()
            transact_datetime = transact_datetime + timedelta(hours=self.merchant_acct.gmt_hour)
        
        transact_date = transact_datetime.date()
        
        if transact_date>=start_date and transact_date<=end_date:
            logger.debug('--------> desc=%s', desc)
            logger.debug('--------> reward_base=%s', reward_base)
            logger.debug('--------> reward_format=%s', reward_format)
            
            if reward_base in (program_conf.REWARD_BASE_ON_GIVEAWAY, program_conf.REWARD_BASE_ON_BIRTHDAY):
            
                if reward_format == program_conf.REWARD_FORMAT_POINT:
                    return PointGiveawayProgram(self.merchant_acct, program_configuration)
                
                elif reward_format == program_conf.REWARD_FORMAT_STAMP:
                    return StampGiveawayProgram(self.merchant_acct, program_configuration)
                
                elif reward_format == program_conf.REWARD_FORMAT_PREPAID:
                    return PrepaidGiveawayProgram(self.merchant_acct, program_configuration)
                
                elif reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                    return VoucherProgram(self.merchant_acct, program_configuration)    
            
            elif reward_base == program_conf.REWARD_BASE_ON_SPENDING:
                if reward_format == program_conf.REWARD_FORMAT_POINT:
                    return PointSchemeProgram(self.merchant_acct, program_configuration)
                
                elif reward_format == program_conf.REWARD_FORMAT_STAMP:
                    return StampSchemeProgram(self.merchant_acct, program_configuration)
                
                elif reward_format == program_conf.REWARD_FORMAT_PREPAID:
                    return PrepaidSchemeProgram(self.merchant_acct, program_configuration)
                
                elif reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                    return VoucherSchemeProgram(self.merchant_acct, program_configuration)
                
            elif reward_base == program_conf.REWARD_BASE_ON_TIER:
                return TierRewardProgram(self.merchant_acct, program_configuration)
            
            elif reward_base == program_conf.REWARD_BASE_ON_PROMOTION_SPENDING:
                return PromotionRewardProgram(self.merchant_acct, program_configuration)
            
        
    def get_giveaway_reward(self, customer_acct, transaction_details, program_configuration_list=None, 
                            reward_set=1, create_upstream=True):
        
        logger.debug('---get_giveaway_reward---')
        
        if program_configuration_list is None:
            merchant_acct                   = customer_acct.registered_merchant_acct
            published_program_configuration = merchant_acct.published_program_configuration
            program_configuration_list      = published_program_configuration.get('programs')
        
        if is_not_empty(program_configuration_list):
            
            logger.debug('**********************************************************************************')
            logger.debug('get_giveaway_reward: program_configuration_list=%s', program_configuration_list)
            logger.debug('**********************************************************************************')
                
            return self.__give_reward_based_on_reward_base(customer_acct, transaction_details, 
                                                           program_configuration_list, 
                                                               program_conf.REWARD_BASE_ON_GIVEAWAY, 
                                                               reward_set=reward_set, 
                                                               create_upstream=create_upstream)
    
    def get_birthday_reward(self, customer_acct, transaction_details, program_configuration_list=None, reward_set=1):
        
        logger.debug('---get_birthday_reward---')
        
        if program_configuration_list is None:
            merchant_acct                   = customer_acct.registered_merchant_acct
            published_program_configuration = merchant_acct.published_program_configuration
            program_configuration_list      = published_program_configuration.get('programs')
        
        if is_not_empty(program_configuration_list):
            
            logger.debug('**********************************************************************************')
            logger.debug('get_giveaway_based_reward: program_configuration_list=%s', program_configuration_list)
            logger.debug('**********************************************************************************')
                
            return self.__give_reward_based_on_reward_base(customer_acct, transaction_details, program_configuration_list, 
                                                               program_conf.REWARD_BASE_ON_BIRTHDAY, 
                                                               reward_set=reward_set)
    
    def get_spending_reward(self, customer_acct, transaction_details, program_configuration_list=None, ):
        logger.debug('---get_spending_reward---')
        
        if program_configuration_list is None:
            merchant_acct                   = customer_acct.registered_merchant_acct
            published_program_configuration = merchant_acct.published_program_configuration
            if published_program_configuration is not None:
                program_configuration_list      = published_program_configuration.get('programs')
        
        if is_not_empty(program_configuration_list):
            logger.debug('**********************************************************************************')
            for pc in program_configuration_list:
                logger.debug('program=%s', pc.get('desc'))
            logger.debug('**********************************************************************************')
            
            if is_not_empty(transaction_details.promotion_code):
                return self.__give_reward_based_on_reward_base(customer_acct, transaction_details, program_configuration_list, 
                                                               program_conf.REWARD_BASE_ON_PROMOTION_SPENDING)
            else:    
                return self.__give_reward_based_on_reward_base(customer_acct, transaction_details,
                                                               program_configuration_list, 
                                                               program_conf.REWARD_BASE_ON_SPENDING)
            
        return False 
            
    def get_tier_reward(self, customer_acct, transaction_details, program_configuration_list=None):
        logger.debug('---get_tier_reward---')
        
        if program_configuration_list is None:
            merchant_acct                   = customer_acct.registered_merchant_acct
            published_program_configuration = merchant_acct.published_program_configuration
            program_configuration_list      = published_program_configuration.get('programs')
        
        if is_not_empty(program_configuration_list):
            
            logger.debug('**********************************************************************************')
            logger.debug('get_tier_reward: program_configuration_list=%s', program_configuration_list)
            logger.debug('**********************************************************************************')
            
            return self.__give_reward_based_on_reward_base(customer_acct, transaction_details, program_configuration_list, 
                                                               program_conf.REWARD_BASE_ON_TIER
                                                               )          
            
    
    def get_purchase_membership_giveaway_reward(self, customer_acct, transaction_details, program_configuration_list=None, reward_set=1):
        
        logger.debug('---get_purchase_membership_giveaway_reward---')
        
        if program_configuration_list is None:
            merchant_acct                   = customer_acct.registered_merchant_acct
            published_program_configuration = merchant_acct.published_program_configuration
            program_configuration_list      = published_program_configuration.get('programs')
        
        if is_not_empty(program_configuration_list):
            
            logger.debug('**********************************************************************************')
            logger.debug('get_membership_giveaway_reward: program_configuration_list=%s', program_configuration_list)
            logger.debug('**********************************************************************************')
                
            return self.__give_purchase_membership_reward_by_program_configuration(customer_acct, transaction_details, program_configuration_list, 
                                                              reward_set=reward_set)
    

                
    def __give_reward_based_on_reward_base(self, customer_acct, transaction_details, program_configuration_list, 
                                               reward_base, reward_set=1, create_upstream=True):
        
        
        
        is_new_reward_gave = False
                    
        for program_configuration in program_configuration_list:
            if reward_base == program_configuration.get('reward_base'):  
                
            
                logger.debug('--> program_configuration=%s', program_configuration)
                reward_program = self.__construct_reward_program(program_configuration)
                
                logger.debug('--> reward_program=%s desc=%s', reward_program, program_configuration.get('desc'))    
                
                if reward_program:
                    _is_new_reward_gave = give_reward(customer_acct, program_configuration, transaction_details, 
                                                      reward_program, reward_set=reward_set, 
                                                      create_upstream=create_upstream)
                    if _is_new_reward_gave:
                        is_new_reward_gave = True
                    
                else:
                    logger.debug('reward giveaway not found or it is expired')
        
        
        if is_new_reward_gave:
            customer_acct.put()
            transaction_details.put()
        
        logger.debug('is_new_reward_gave=%s', is_new_reward_gave)
        
        return is_new_reward_gave
    
    def __give_purchase_membership_reward_by_program_configuration(self, customer_acct, transaction_details, program_configuration_list, reward_set=1):
        
        logger.debug('is_membership_purchase=%s', transaction_details.is_membership_purchase)
        
        if transaction_details.is_membership_purchase:
            purchased_customer_membership = transaction_details.purchased_customer_membership_entity
            logger.debug('purchased_customer_membership=%s', purchased_customer_membership)
            
            if purchased_customer_membership:
                merchant_membership_key = purchased_customer_membership.merchant_membership_key
                if purchased_customer_membership.is_new_joined:
                    is_new_reward_gave = False
                    
                    for program_configuration in program_configuration_list:
                        #MUST be giveaway
                        program_label               = program_configuration.get('label')
                        reward_base                 = program_configuration.get('reward_base')
                        reward_format               = program_configuration.get('reward_format')
                        
                        giveaway_system_settings    = program_configuration.get('program_settings').get('giveaway_system_settings')
                        
                        is_giveaway_reward_base_match       = program_conf.REWARD_BASE_ON_GIVEAWAY == reward_base
                        is_new_membership_condition_match   = False
                        is_merchant_membership_match        = False
                        giveaway_system_condition           = None
                        
                        if is_not_empty(giveaway_system_settings):
                            giveaway_system_condition   = giveaway_system_settings.get('giveaway_system_condition')
                            
                            is_new_membership_condition_match   = program_conf.GIVEAWAY_SYSTEM_CONDITION_NEW_MEMBERSHIP==giveaway_system_condition
                            
                            if is_not_empty(giveaway_system_settings.get('giveaway_memberships')):  
                                is_merchant_membership_match = merchant_membership_key in giveaway_system_settings.get('giveaway_memberships')
                        
                        logger.debug('program label=%s', program_label)
                        logger.debug('reward_base=%s, reward_format=%s, giveaway_system_condition=%s, is_giveaway_reward_base=%s, is_new_membership_condition_match=%s, is_merchant_membership_match=%s', reward_base, reward_format, giveaway_system_condition, is_giveaway_reward_base_match, is_new_membership_condition_match, is_merchant_membership_match)
                        
                        if is_giveaway_reward_base_match and \
                            is_new_membership_condition_match and \
                            is_merchant_membership_match:  
                            
                        
                            logger.debug('--> program_configuration=%s', program_configuration)
                            
                            reward_program = self.__construct_reward_program(program_configuration)
                                
                            
                            if reward_program:
                                _is_new_reward_gave = give_reward(customer_acct, program_configuration, transaction_details, reward_program, reward_set=reward_set)
                                if _is_new_reward_gave:
                                    is_new_reward_gave = True
                                
                            else:
                                logger.debug('reward giveaway not found')
                        else:
                            logger.debug('program_configuration condition not match')        
                    
                    if is_new_reward_gave:
                        customer_acct.put()
                        transaction_details.put()
                    
                    logger.debug('is_new_reward_gave=%s', is_new_reward_gave)
                    
                    return is_new_reward_gave
                else:
                    logger.debug('Membership is not new joined')
            else:
                logger.debug('Membership purchase not found in transaction')
        else:
            logger.debug('Not membership purchase transaction') 
        return False

def give_reward(customer_acct, program_configuration, transaction_details, reward_program, reward_set=1, create_upstream=True):
    logger.debug('================================================')
    logger.debug('program_configuration desc=%s', program_configuration.get('desc'))
    logger.debug('reward_base=%s', program_configuration.get('reward_base'))
    logger.debug('giveaway method=%s', program_configuration.get('giveaway_method'))
    logger.debug('reward_program =%s', reward_program.__class__.__name__)
    logger.debug('================================================')
    
    today               = datetime.today().date()
    giveaway_datetime   = transaction_details.transact_datetime
    is_new_reward_gave  = False
    
    if today>=reward_program.start_date and today<=reward_program.end_date:
    
        reward = reward_program.give(customer_acct, transaction_details, reward_set=reward_set)
        
        if reward:
            
            logger.debug('================>>>> %s', reward.reward_brief)
            logger.debug('reward= %s', reward)
            
            customer_reward_summary             = customer_acct.reward_summary
            customer_entitled_voucher_summary   = customer_acct.entitled_voucher_summary
            customer_prepaid_summary            = customer_acct.prepaid_summary
            
            
            logger.debug('customer_reward_summary before=%s', customer_reward_summary)
            logger.debug('customer_entitled_voucher_summary before=%s', customer_entitled_voucher_summary)
            logger.debug('customer_prepaid_summary before=%s', customer_prepaid_summary)
            
            transaction_reward_summary          = transaction_details.entitled_reward_summary or {}
            transaction_voucher_summary         = transaction_details.entitled_voucher_summary or {}
            transaction_prepaid_summary         = transaction_details.entitled_prepaid_summary or {}
            
            logger.debug('transaction_reward_summary before=%s', customer_reward_summary)
            logger.debug('transaction_voucher_summary before=%s', transaction_voucher_summary)
            logger.debug('transaction_prepaid_summary before=%s', transaction_prepaid_summary)
            
            
            if isinstance(reward, CustomerCountableReward):
                if reward.reward_format in (program_conf.REWARD_FORMAT_POINT, program_conf.REWARD_FORMAT_STAMP):
                    new_reward_summary          = reward.to_reward_summary()
                    
                    if is_not_empty(new_reward_summary):
                        is_new_reward_gave = True
                    
                        customer_reward_summary     = update_reward_summary_with_new_reward(customer_reward_summary, new_reward_summary)
                        transaction_reward_summary  = update_reward_summary_with_new_reward(transaction_reward_summary, new_reward_summary)
                    
                if create_upstream:
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, reward, )
            
            elif isinstance(reward, CustomerPrepaidReward):
                new_prepaid_summary         = reward.to_prepaid_summary()
                if is_not_empty(new_prepaid_summary):
                    is_new_reward_gave = True
                    
                    customer_prepaid_summary    = update_prepaid_summary_with_new_prepaid(customer_prepaid_summary, new_prepaid_summary)
                    transaction_prepaid_summary = update_prepaid_summary_with_new_prepaid(transaction_prepaid_summary, new_prepaid_summary)
                    
                if create_upstream:        
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, reward, )
                    create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, reward)                        
                    
            
            elif isinstance(reward, EntitledVoucherSummary):
                
                voucher_summary_list = reward.entitled_voucher_summary_list
                
                logger.info('voucher_summary_list=%s', voucher_summary_list)
                
                if is_not_empty(voucher_summary_list):
                    is_new_reward_gave = True
                
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
                            
                            voucher_reward_brief = VoucherRewardDetailsForUpstreamData(voucher_key, voucher_amount, expiry_date, giveaway_datetime) 
                            
                            logger.debug('voucher_reward_brief=%s', voucher_reward_brief)
                            
                            if create_upstream:
                                create_merchant_customer_reward_upstream_for_merchant(transaction_details, 
                                                                                  voucher_reward_brief, )
                                
                                    
                    
            if is_new_reward_gave:
            
                customer_acct.reward_summary            = customer_reward_summary
                customer_acct.entitled_voucher_summary  = customer_entitled_voucher_summary
                customer_acct.prepaid_summary           = customer_prepaid_summary
                
                
                transaction_details.entitled_reward_summary     = transaction_reward_summary
                transaction_details.entitled_prepaid_summary    = transaction_prepaid_summary
                transaction_details.entitled_voucher_summary    = transaction_voucher_summary
                
                
                logger.debug('transaction_reward_summary after=%s', customer_reward_summary)
                logger.debug('transaction_voucher_summary after=%s', transaction_voucher_summary)
                logger.debug('transaction_prepaid_summary after=%s', transaction_prepaid_summary)

            
            
            logger.debug('customer_reward_summary after=%s', customer_reward_summary)
            logger.debug('customer_entitled_voucher_summary after=%s', customer_entitled_voucher_summary)
            logger.debug('customer_prepaid_summary after=%s', customer_prepaid_summary)
            
                            
    else:
        logger.debug('reward is not yet started or already after end date or not eligible')
        logger.debug('today=%s', today)
        logger.debug('reward_giveaway.start_date=%s', reward_program.start_date)
        logger.debug('reward_giveaway.end_date=%s', reward_program.end_date)
    
    
    return is_new_reward_gave


def sort_entitled_voucher_summary(entitled_voucher_summary):
    return OrderedDict(sorted(entitled_voucher_summary.items(), key=lambda x: time.mktime(datetime.strptime(x[1].get('effective_date'), '%d-%m-%Y').timetuple()) ))



        
        