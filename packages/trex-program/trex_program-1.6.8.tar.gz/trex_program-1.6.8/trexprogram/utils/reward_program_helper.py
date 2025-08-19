'''
Created on 2 May 2024

@author: jacklok
'''
import logging
from trexconf import program_conf
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from trexconf.program_conf import REWARD_PROGRAM_DATE_FORMAT
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_redemption_upstream_for_merchant

logger = logging.getLogger('reward-program-lib')

def calculate_expiry_date(expiration_type, expiration_value, start_date=None):
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
        
def calculate_effective_date(effective_type, effective_value, start_date=None):
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


def consume_customer_reward(customer_acct, transaction_id, redeem_reward_details):
     
    db_client = create_db_client(caller_info="consumer_customer_reward")
    
    with db_client.context():
        customer_transaction    = CustomerTransaction.get_by_transaction_id(transaction_id)
        
        if customer_transaction:
            __consume_customer_reward_transaction(customer_acct, customer_transaction, redeem_reward_details)                    

#@model_transactional(desc='tier_program_reward_consume_for_transaction')
def __consume_customer_reward_transaction(customer_acct, customer_transaction, redeem_reward_details):
    
    transact_outlet = customer_transaction.transact_outlet_entity
    
    for reward_format, reward_amount_to_redeem in redeem_reward_details.items():
        logger.debug('to redeem: reward_format=%s, reward_amount_to_redeem=%s', reward_format, reward_amount_to_redeem)
        customer_redemption = CustomerRedemption.create(customer_acct, reward_format, 
                                                                          redeemed_outlet               = transact_outlet,
                                                                          redeemed_amount               = reward_amount_to_redeem,            
                                                                          invoice_id                    = customer_transaction.invoice_id, 
                                                                          redeemed_by                   = customer_transaction.transact_by_user, 
                                                                          redeemed_datetime             = customer_transaction.transact_datetime,
                                                                          is_tier_program_redemption    = True,
                                                                          tier_program_transaction_id   = customer_transaction.transaction_id,
                                                                          )
                
    if customer_redemption:
        #create_redemption_message(customer_redemption)
        create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, )
        
        
        