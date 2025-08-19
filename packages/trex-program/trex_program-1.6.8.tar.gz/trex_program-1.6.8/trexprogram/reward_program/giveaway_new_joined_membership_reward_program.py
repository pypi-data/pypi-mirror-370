'''
Created on 13 Mar 2023

@author: jacklok
'''
from trexprogram.utils.reward_program_helper import calculate_expiry_date

'''
Created on 19 May 2021

@author: jacklok
'''

from trexprogram.reward_program.reward_program_base import SchemeRewardProgram, VoucherRewardProgramBase,\
    EntitledVoucherSummary
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher
from trexconf import program_conf
import logging
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward

logger = logging.getLogger('reward-program-lib')

class GiveawayNewJoinedMembershipRewardProgram(SchemeRewardProgram, VoucherRewardProgramBase):
    
    def __init__(self, program_configuration, currency=None):
        super(GiveawayNewJoinedMembershipRewardProgram, self).__init__(program_configuration, currency=currency)
        
        self.reward_format              = program_configuration.get('reward_format')
        self.giveaway_method            = program_configuration.get('giveaway_method')
        self.giveaway_system_condition  = program_configuration.get('giveaway_system_condition')
        
        logger.debug('GiveawayRewardProgram: reward_format=%s', self.reward_format)
        logger.debug('GiveawayRewardProgram: giveaway_system_condition=%s', self.giveaway_system_condition)
        
        if not self.reward_format in (program_conf.REWARD_FORMAT_POINT, 
                                      program_conf.REWARD_FORMAT_STAMP,
                                      program_conf.REWARD_FORMAT_PREPAID, 
                                      program_conf.REWARD_FORMAT_VOUCHER, 
                                      ):
            raise Exception('Invalid program configuration')    
    
    def give(self, customer_acct, transaction_details, reward_set=1): 
        if self.is_eligible_based_on_exclusivity(customer_acct):
            
            logger.debug('GiveawayRewardProgram: Going to give reward')
            logger.debug('GiveawayRewardProgram: reward_format=%s', self.reward_format)
            logger.debug('GiveawayRewardProgram: reward_set=%s', reward_set)
            
            logger.debug('program_configuration=%s', self.program_configuration)
            
            transact_datetime               = transaction_details.transact_datetime
            
            transaction_id                  = transaction_details.transaction_id
            invoice_id                      = transaction_details.invoice_id
            
            transact_by                     = transaction_details.transact_by_user
            
            transact_outlet                 = transaction_details.transact_outlet_details
            
            reward_unit                     = reward_set
            
            is_membership_purchase          = transaction_details.is_membership_purchase
            
            if is_membership_purchase:
                pass
                
            
            reward_amount                   = self.calculate_entitle_reward_amount(reward_unit=reward_unit)
            
            effective_date                  = transact_datetime.date()
            
            logger.debug('GiveawayRewardProgram: reward_unit=%s', reward_unit)
            
            if self.reward_format == program_conf.REWARD_FORMAT_POINT:
                
                expiry_date                     = calculate_expiry_date(self.expiration_type, self.expiration_value, start_date=effective_date)
                
                point_reward = CustomerPointReward.create( 
                                                customer_acct       = customer_acct, 
                                                reward_amount       = reward_amount,
                                                transact_outlet     = transact_outlet, 
                                                effective_date      = effective_date,
                                                expiry_date         = expiry_date, 
                                                transaction_id      = transaction_id, 
                                                invoice_id          = invoice_id, 
                                                rewarded_by         = transact_by,
                                                program_key         = self.program_key,
                                                rewarded_datetime   = transact_datetime,
                                                )
                
                return point_reward
            
            elif self.reward_format == program_conf.REWARD_FORMAT_PREPAID:
                
                prepaid_topup_reward = CustomerPrepaidReward.topup(customer_acct, reward_amount, None, 
                                                                   topup_outlet=transact_outlet, 
                                                                   topup_by=transact_by, 
                                                                   invoice_id=invoice_id,
                                                                   transaction_id=transaction_id,
                                                                   )

                
                return prepaid_topup_reward
            
            
            elif self.reward_format == program_conf.REWARD_FORMAT_STAMP:
                
                expiry_date                     = calculate_expiry_date(self.expiration_type, self.expiration_value, start_date=effective_date)
                
                stamp_reward    = CustomerStampReward.create( 
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
                                            )
            
                return stamp_reward
            
            elif self.reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                entiteld_voucher_brief  = EntitledVoucherSummary(transaction_id=transaction_id)
                vouchers_list           = self.construct_giveaway_voucher_details_list(transaction_details)
                customer_voucher_list   = []
                for voucher in vouchers_list:
                    merchant_voucher = MerchantVoucher.fetch(voucher.get('voucher_key'))
                    if merchant_voucher:
                        
                        effective_date          = voucher.get('effective_date')
                        expiry_date             = voucher.get('expiry_date')
                        voucher_amount          = voucher.get('voucher_amount') * reward_unit
                        
                        logger.debug('Giveaway Voucher: expiry_date=%s', expiry_date)
                        
                        for v in range(voucher_amount):
                            customer_voucher = CustomerEntitledVoucher.create(
                                                                        merchant_voucher,
                                                                        customer_acct, 
                                                                        transact_outlet     = transact_outlet,
                                                                        transaction_id      = transaction_id,
                                                                        invoice_id          = invoice_id,
                                                                        rewarded_by         = transact_by,
                                                                        rewarded_datetime   = transact_datetime,
                                                                        effective_date      = effective_date,
                                                                        expiry_date         = expiry_date,
                                                                        program_key         = self.program_key,    
                                                                        )
                            customer_voucher_list.append(customer_voucher)
                        
                        entiteld_voucher_brief.add(merchant_voucher, customer_voucher_list)
                            
                    else:
                        logger.warn('Voucher is not found for voucher_key=%s', voucher.get('voucher_key'))
                
                return entiteld_voucher_brief
            
        else:
            logger.debug('Not eligible to get reward')
    
    
    