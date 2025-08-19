'''
Created on 5 Oct 2021

@author: jacklok
'''
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.reward_models import CustomerEntitledTierRewardSummary
from trexconf import program_conf 
import logging
from trexlib.utils.string_util import is_empty
from _datetime import timedelta, datetime

logger = logging.getLogger('helper')
#logger = logging.getLogger('target_debug')

def update_and_get_unlock_tier_index_list(customer, tier_reward_program, transaction_details, customer_reward_summary):
    logger.debug('---update_and_get_unlock_tier_index_list---, transaction_id=%s, tier program.end_date=%s', transaction_details.transaction_id, tier_reward_program.end_date)
    
    customer_tier_reward_summary    = CustomerEntitledTierRewardSummary.get_customer_tier_reward_program_summary(customer, tier_reward_program)
    transact_datetime               = transaction_details.transact_datetime
    cycle_start_datetime            = None
    checking_transaction_list       = []
    unlock_reward_tier_index_list   = []
    is_new_cycle                    = False
    allow_recycle                   = False
    is_cycle_completed              = False
    entitled_reward_summary         = transaction_details.entitled_reward_summary
    latest_transaction_id           = transaction_details.transaction_id
    
    logger.debug('customer_reward_summary=%s', customer_reward_summary)
    logger.debug('customer_tier_reward_summary=%s', customer_tier_reward_summary)
    logger.debug('latest_transaction_id=%s', latest_transaction_id)
    logger.debug('entitled_reward_summary=%s', entitled_reward_summary)
    
    
    if customer_tier_reward_summary is None:
        logger.debug('no customer_tier_reward_summary yet')
        checking_transaction_list   = None
        is_new_cycle                = True
        cycle_start_datetime        = transact_datetime
        #cycle_start_datetime        = datetime.combine(tier_reward_program.start_date, time())
        
        customer_tier_reward_summary = CustomerEntitledTierRewardSummary.create(customer, 
                                                                                tier_reward_program, 
                                                                                cycle_start_datetime = cycle_start_datetime)
        logger.debug('Created csutomer entitled tier reward summary')
        
    else:
        logger.debug('found customer_tier_reward_summary')
        is_cycle_completed = customer_tier_reward_summary.is_cycle_completed 
        is_cyccle_start_datetime_passed = transact_datetime >= customer_tier_reward_summary.cycle_start_datetime
        
        logger.debug('is_cycle_completed=%s', is_cycle_completed)
        logger.debug('is_cyccle_start_datetime_passed=%s', is_cyccle_start_datetime_passed)
        
        if is_cycle_completed and is_cyccle_start_datetime_passed:
            logger.debug('cycle have completed, thus going to restart cycle')
            allow_recycle = tier_reward_program.is_tier_recycle
            if allow_recycle:
                is_cycle_completed      = False
                #cycle_start_datetime    = transact_datetime
                CustomerEntitledTierRewardSummary.restart_cycle(customer_tier_reward_summary, cycle_start_datetime=customer_tier_reward_summary.cycle_start_datetime)
                logger.debug('Change is_cycle_completed to False after restart cycle')
                
        else:
            #follow existing cycle start datetime
            cycle_start_datetime        = customer_tier_reward_summary.cycle_start_datetime
            logger.debug('Follow existing cycle start datetime')
            
    customer_tier_summary_list  = customer_tier_reward_summary.tier_summary.get('tiers') or [] if customer_tier_reward_summary.tier_summary else []
    
    logger.debug('========================================================================')
    logger.debug('cycle_start_datetime=%s', cycle_start_datetime)
    logger.debug('transact_datetime=%s', transact_datetime)
    
    if is_cycle_completed == False:
        logger.debug('cycle is not yet completed')
        if is_new_cycle:
            logger.debug('it is new cycle')
            #checking_transaction_list   = [transaction_details]
        else:
            logger.debug('it is existing cycle, cycle_start_datetime=%s, transact_datetime=%s', cycle_start_datetime, transact_datetime)
            '''
            checking_transaction_list = CustomerTransaction.list_customer_transaction_by_transact_datetime(customer, 
                                                                                                           transact_datetime_from   = cycle_start_datetime, 
                                                                                                           transact_datetime_to     = transact_datetime
                                                                                                           )
            
             
            if checking_transaction_list is None:
                checking_transaction_list = []
            '''
            #else:
            #    checking_transaction_list.append(transaction_details)
        
        #process transaction history to accumulate by reward format
        accumulated_transaction_summary = {
                                            program_conf.SALES_AMOUNT : {
                                                                        'amount': .0,
                                                                        'sources':[],
                                                                        },
                                           }
        if checking_transaction_list:
            logger.debug('checking_transaction_list count=%d', len(checking_transaction_list))
        
            found_latest_transaction = list(filter(lambda item: item.transaction_id == latest_transaction_id, checking_transaction_list))
            
            logger.debug('found_latest_transaction=%s', found_latest_transaction)
            
            if is_empty(found_latest_transaction):
                checking_transaction_list.append(transaction_details)
            
            for _transaction_details in checking_transaction_list:
                if _transaction_details.is_revert == False:
                    entitled_reward_summary = _transaction_details.entitled_reward_summary
                    logger.debug('reading accumulated reward for transact_datetime=%s, transaction_id=%s', _transaction_details.transact_datetime, _transaction_details.transaction_id)
                    if entitled_reward_summary:
                        for reward_format, reward_summary in entitled_reward_summary.items():
                            if reward_format in program_conf.SUPPORT_TIER_REWARD_PROGRAM_CONDITION_REWARD_FORMAT:
                                accumualated_amount = .0
                                found_reward        = False
                                
                                if accumulated_transaction_summary.get(reward_format) is not None:
                                    accumualated_amount    = accumulated_transaction_summary.get(reward_format).get('amount')
                                    found_reward = True
                                
                                
                                transaction_reward_amount       = reward_summary.get('amount')
                                
                                if transaction_reward_amount>0:
                                    accumualated_amount    += transaction_reward_amount
                                    
                                    transaction_source_details = {
                                                                'transaction_id': _transaction_details.transaction_id,
                                                                'amount':transaction_reward_amount,    
                                                                }
                                    
                                    if found_reward:
                                        reward_sources_list = accumulated_transaction_summary.get(reward_format).get('sources')
                                        reward_sources_list.append(transaction_source_details)
                                        accumulated_transaction_summary[reward_format] = {
                                                                                        'amount' : accumualated_amount,   
                                                                                        'sources': reward_sources_list,
                                                                                        }
                                    else:
                                        accumulated_transaction_summary[reward_format] = {
                                                                                    'amount' : accumualated_amount,
                                                                                    'sources': [
                                                                                                transaction_source_details
                                                                                                ]
                                                                                            
                                                                                               
                                    
                                                                                }
                    
                    
                    if _transaction_details.transact_amount>0:
                        transaction_sales_details   = {
                                                                'transaction_id': _transaction_details.transaction_id,
                                                                'amount'        : _transaction_details.transact_amount,    
                                                                }
                        
                        sales_sources_list = accumulated_transaction_summary.get(program_conf.SALES_AMOUNT).get('sources')
                        sales_sources_list.append(transaction_sales_details)
                        sales_accumualated_amount   = accumulated_transaction_summary.get(program_conf.SALES_AMOUNT).get('amount')
                        sales_accumualated_amount   += _transaction_details.transact_amount
                        
                        accumulated_transaction_summary[program_conf.SALES_AMOUNT] = {
                                                                        'amount' : sales_accumualated_amount,   
                                                                        'sources': sales_sources_list,
                                                                        }
            
            
        logger.debug('accumulated_transaction_summary=%s', accumulated_transaction_summary)
        total_tier_count = len(customer_tier_summary_list)
        
        #continue_check_tier_reward      = True
        max_unlock_tier_count_per_trax  = tier_reward_program.max_unlock_tier_count_per_trax
        unlock_tier_count               = 0
        is_cycle_completed              = False
        
        logger.debug('max_unlock_tier_count_per_trax=%s', max_unlock_tier_count_per_trax)
        
        #while continue_check_tier_reward:
        for tier_no, tier_summary in enumerate(customer_tier_summary_list, start=1):
            is_unlock = tier_summary.get('unlock_status', False)
            consume_reward_format = tier_summary.get('consume_reward_format')
            
            logger.debug('tier_no=%d, is_unlock=%s, consume_reward_format=%s', tier_no, is_unlock, consume_reward_format)
            
            if is_unlock:
                continue
            else:
                #checking for not unlock tier
                target_checking_format              = None
                accumualated_checking_amount        = .0
                unlock_condition                    = tier_summary.get('unlock_condition')
                unlock_condition_value              = float(tier_summary.get('unlock_condition_value'))
                unlock_value                        = float(tier_summary.get('unlock_value') or .0)
                        
                
                logger.debug('unlock_condition=%s, unlock_condition_value=%d, unlock_value=%s, consume_reward_format=%s', unlock_condition, unlock_condition_value, unlock_value, consume_reward_format)
                
                if tier_summary.get('unlock_condition') in program_conf.ENTITLE_REWARD_CONDITION_ACCUMULATE_TYPES: 
                    if program_conf.ENTITLE_REWARD_CONDITION_ACCUMULATE_POINT == unlock_condition:
                        
                        if accumulated_transaction_summary.get(program_conf.REWARD_FORMAT_POINT) is not None:
                            reward_amount = accumulated_transaction_summary.get(program_conf.REWARD_FORMAT_POINT).get('amount')
                            accumualated_checking_amount    = reward_amount or .0
                        else:
                            accumualated_checking_amount = .0
                        
                        target_checking_format          = program_conf.REWARD_FORMAT_POINT
                        
                    elif program_conf.ENTITLE_REWARD_CONDITION_ACCUMULATE_STAMP == unlock_condition:
                        
                        if accumulated_transaction_summary.get(program_conf.REWARD_FORMAT_STAMP) is not None:
                            reward_amount = accumulated_transaction_summary.get(program_conf.REWARD_FORMAT_STAMP).get('amount')
                            accumualated_checking_amount    = reward_amount or .0
                        else:
                            accumualated_checking_amount = .0
                        
                        target_checking_format          = program_conf.REWARD_FORMAT_STAMP
                        
                        
                    elif program_conf.ENTITLE_REWARD_CONDITION_ACCUMULATE_SALES_AMOUNT == unlock_condition: 
                        
                        accumualated_checking_amount    = accumulated_transaction_summary.get(program_conf.SALES_AMOUNT).get('amount') or .0 
                        target_checking_format          = program_conf.SALES_AMOUNT
                    
                    is_condition_match = accumualated_checking_amount >= unlock_condition_value
                    
                    logger.debug('tier_no=%s, unlock_tier_count=%s, unlock_value=%s target_checking_format=%s', tier_no, unlock_tier_count, unlock_value, target_checking_format)
                    logger.debug('accumualated_checking_amount=%d, is_condition_match=%s', accumualated_checking_amount, is_condition_match)       
                        
                    if is_condition_match==True:
                        logger.debug('OKAY, found unlock matched condition tier no=%d', tier_no)
                        unlock_tier_count+=1
                        tier_summary['unlock_status']           = True
                        tier_summary['unlock_value']            = unlock_condition_value
                        tier_summary['unlock_datetime']         = transact_datetime.strftime('%d-%m-%Y %H:%M:%S')
                        tier_summary['unlock_source_details']   = accumulated_transaction_summary.get(target_checking_format).get('sources')
                         
                        unlock_reward_tier_index_list.append(tier_summary.get('tier_index'))
                        
                        if tier_no==total_tier_count:
                            #this is final tier
                            logger.debug('Unlocked the final tier')
                            is_cycle_completed = True
                    
                    else:
                        logger.debug('tier condition not match, tier no=%d', tier_no)
                        tier_summary['unlock_value']    = accumualated_checking_amount  
                        if accumualated_checking_amount>0:
                            tier_summary['unlock_source_details'] = accumulated_transaction_summary.get(target_checking_format).get('sources')
                        break
                    
                logger.debug('unlock_tier_count=%s', unlock_tier_count)
                        
        logger.debug('-----> customer_tier_summary_list=%s', customer_tier_summary_list)
        
        next_cycle_start_datetime = None
        if is_cycle_completed:
            allow_recycle = tier_reward_program.is_tier_recycle
            if allow_recycle:
                next_cycle_start_datetime = datetime(transact_datetime.year, transact_datetime.month, transact_datetime.day) + timedelta(days=1)
        
        CustomerEntitledTierRewardSummary.update(customer_tier_reward_summary, 
                                                 tier_summary_list      = { 'tiers': customer_tier_summary_list }, 
                                                 cycle_start_datetime   = next_cycle_start_datetime,
                                                 is_cycle_completed     = is_cycle_completed)
        logger.debug('Updated customer entitled tier reward summary')
    
    logger.debug('unlock_reward_tier_index_list=%s', unlock_reward_tier_index_list)
    
    return unlock_reward_tier_index_list   
