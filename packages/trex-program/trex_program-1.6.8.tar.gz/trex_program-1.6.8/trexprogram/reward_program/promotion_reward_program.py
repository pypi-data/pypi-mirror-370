from trexprogram.reward_program.reward_program_base import SchemeRewardProgram,\
    EntitledVoucherSummary, VoucherRewardProgramBase
from trexconf import program_conf
import logging
from trexlib.utils.string_util import is_not_empty
from trexprogram.utils.reward_program_helper import calculate_expiry_date
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexanalytics.bigquery_upstream_data_config import create_entitled_customer_voucher_upstream_for_merchant


logger = logging.getLogger('reward-program-lib')

class PromotionRewardProgram(SchemeRewardProgram, VoucherRewardProgramBase):
    
    def __init__(self, merchant_acct, program_configuration, ):
        super(PromotionRewardProgram, self).__init__(merchant_acct, program_configuration)
        
        self.reward_format              = program_configuration.get('reward_format')
        self.program_key                = program_configuration.get('program_key')
        self.promotion_codes_list       = program_configuration.get('program_settings').get('exclusivity').get('promotion_codes', [])
        
        logger.debug('PromotionRewardProgram: reward_format=%s', self.reward_format)
        
        if not self.reward_format in (program_conf.REWARD_FORMAT_POINT, 
                                      program_conf.REWARD_FORMAT_STAMP,
                                      program_conf.REWARD_FORMAT_PREPAID, 
                                      program_conf.REWARD_FORMAT_VOUCHER, 
                                      ):
            raise Exception('Invalid program configuration')
        
    def is_eligible(self, customer_acct, promotion_code):
        logger.debug('PromotionRewardProgram: promotion_codes_list=%s', self.promotion_codes_list)
        logger.debug('PromotionRewardProgram: promotion_code=%s', promotion_code)
        
        if is_not_empty(self.promotion_codes_list):
            if promotion_code in self.promotion_codes_list:
                
                super_is_eligible_based_on_exclusivity = self.is_eligible_based_on_exclusivity(customer_acct)
                
                logger.debug('PromotionRewardProgram: going to check super class is_eligible_based_on_exclusivity=%s', super_is_eligible_based_on_exclusivity) 
                return super_is_eligible_based_on_exclusivity
        else:
            return super.is_eligible_based_on_exclusivity(customer_acct)
        
        return False
    
    def get_giveaway_reward_sales_amount(self, transaction_details):
        
        transact_amount             = transaction_details.transact_amount
        tax_amount                  = transaction_details.tax_amount
        
        giveaway_reward_sales_amount = transact_amount - tax_amount
        
        return giveaway_reward_sales_amount
        
    def give(self, customer_acct, transaction_details, reward_set=1): 
        promotion_code                  = transaction_details.promotion_code
        
        if self.is_eligible(customer_acct, promotion_code):
            
            transact_datetime               = transaction_details.transact_datetime
            transaction_id                  = transaction_details.transaction_id
            invoice_id                      = transaction_details.invoice_id
            transact_by                     = transaction_details.transact_by_user
            transact_outlet                 = transaction_details.transact_outlet_details
            
            giveaway_reward_sales_amount    = self.get_giveaway_reward_sales_amount(transaction_details)
            reward_unit                     = self.calculate_reward_unit(giveaway_reward_sales_amount) * reward_set
            reward_amount                   = self.calculate_entitle_reward_amount(reward_unit=reward_unit)
            effective_date                  = transact_datetime.date()
            
            logger.debug('PromotionRewardProgram: giveaway_reward_sales_amount=%s', giveaway_reward_sales_amount)
            logger.debug('PromotionRewardProgram: reward_unit=%s', reward_unit)
            logger.debug('PromotionRewardProgram: reward_amount=%s', reward_amount)
            
            if self.reward_format == program_conf.REWARD_FORMAT_POINT:
                
                reward_unit                     = self.calculate_reward_unit(giveaway_reward_sales_amount) * reward_set
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
                            create_entitled_customer_voucher_upstream_for_merchant(customer_voucher)
                        
                        entiteld_voucher_brief.add(merchant_voucher, customer_voucher_list)
                            
                    else:
                        logger.warn('Voucher is not found for voucher_key=%s', voucher.get('voucher_key'))
                
                return entiteld_voucher_brief
            
        else:
            logger.debug('PromotionRewardProgram: not eligible to get reward')   
                
    