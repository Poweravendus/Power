"""Map the annual history JSON (Rs cr) into Consolidated rows."""
import json

def g(d, sec, key):
    return {int('20' + k[2:]): v for k, v in d[sec].get(key, {}).items()}

def add(*series):
    out = {}
    for s in series:
        for k, v in s.items():
            if v is not None:
                out[k] = out.get(k, 0) + v
    return out

def neg(s):
    return {k: (-v if v is not None else None) for k, v in s.items()}

def build_H(path):
    d = json.load(open(path))
    P, B, C, N, O = (lambda k: g(d, 'pnl', k)), (lambda k: g(d, 'bs', k)), (lambda k: g(d, 'cf', k)), (lambda k: g(d, 'ndcf', k)), (lambda k: g(d, 'other', k))
    H = {
        6: P('revenue_from_operations'), 9: P('investment_manager_fees'), 10: P('project_manager_fees'),
        11: P('om_infrastructure_maintenance_charges'), 12: P('employee_benefits'), 13: P('insurance'), 14: P('other_expenses'),
        22: P('other_income'), 23: P('depreciation_amortisation'), 28: P('finance_costs'), 29: P('impairment_net'),
        37: P('current_tax'), 38: P('deferred_tax'), 39: P('earlier_years_tax'), 45: P('other_comprehensive_income'),
        49: P('minority_interest_share'),
        56: {k: v / 1e7 for k, v in O('units_outstanding_year_end_number').items()}, 58: O('dpu_declared_for_year_rs'),
        64: B('unit_capital'), 65: add(B('other_equity'), B('distribution_repayment_of_capital')), 68: B('non_controlling_interest'),
        70: B('long_term_borrowings'), 71: B('short_term_borrowings'), 72: B('current_maturities'),
        78: B('deferred_tax_liability_net'), 79: B('other_non_current_liabilities'), 80: B('long_term_provisions'),
        85: B('gross_block'), 86: add(B('accumulated_depreciation'), B('impairment')), 88: B('cwip'), 91: B('intangibles'),
        92: B('goodwill'), 93: B('non_current_investments'), 95: B('other_non_current_assets_incl_financial'),
        98: B('inventories'), 99: B('trade_receivables'), 100: B('other_bank_balances'), 101: B('cash_and_cash_equivalents'),
        104: B('other_current_assets'), 107: B('trade_payables'),
        108: add(B('other_current_financial_liabilities'), B('other_current_liabilities'), B('current_tax_liabilities_net')),
        109: B('short_term_provisions'),
        119: C('cfo_profit_before_tax'), 121: C('cfo_adj_depreciation_amortisation'), 123: C('cfo_adj_impairment_reversal'),
        129: C('cfo_adj_finance_cost'), 130: add(C('cfo_adj_interest_income'), C('cfo_adj_interest_income_on_loans_to_spvs')),
        133: add(C('cfo_adj_excess_provision_written_back'), C('cfo_adj_provision_for_bad_doubtful_debts'), C('cfo_adj_profit_loss_on_disposal_of_fixed_assets')),
        136: C('wc_inventories'), 137: C('wc_trade_receivables'), 140: C('wc_trade_payables'),
        139: add(*[C(k) for k in ['wc_other_current_financial_liabilities', 'wc_other_non_financial_liabilities', 'wc_other_current_liabilities',
                                  'wc_provisions', 'wc_other_non_current_liabilities', 'wc_non_current_financial_assets',
                                  'wc_other_current_financial_assets', 'wc_earmarked_bank_balances', 'wc_other_current_assets', 'wc_other_non_current_assets']]),
        145: add(C('cfo_direct_taxes_paid_net'), C('cfo_income_tax_refund_received')),
        148: add(C('cfi_ppe_and_cwip'), C('cfi_purchase_of_intangible_assets')), 152: C('cfi_acquisition_of_non_controlling_interest'),
        156: C('cfi_interest_income_received'), 160: C('cfi_investment_in_fixed_deposits_net'),
        163: C('cff_proceeds_from_issue_of_unit_capital'), 166: C('cff_proceeds_from_borrowings'), 167: C('cff_repayment_of_borrowings'),
        171: C('cff_dividend_paid_to_nci'), 172: C('cff_finance_cost_paid'), 174: C('cff_distribution_to_unitholders'),
        178: add(C('opening_cash'), C('cash_acquired_on_acquisition_date')),
        218: N('ndcf_spv_level_sum_of_5_spvs'), 226: N('ndcf_trust_level'), 244: O('nav_per_unit_fair_value_rs'),
    }
    # NDCF bridge from SPV-level NDCF to Trust NDCF (old framework FY22-24, revised FY25-26)
    H[219] = add(N('trust_old_fees_interest_expenses_at_trust'), N('trust_new_cfo_of_trust'), N('trust_new_treasury_income'))
    H[220] = N('trust_new_finance_cost_on_borrowings')
    H[222] = N('trust_old_dsra_set_aside')
    H[224] = N('trust_old_income_tax_statutory_dues')
    H[225] = add(N('trust_old_repayment_of_external_debt'), N('trust_new_debt_repayment'))
    H[223] = {fy: H[226][fy] - H[218][fy] - sum(H[r].get(fy) or 0 for r in (219, 220, 222, 224, 225)) for fy in H[226]}
    for r in list(H):
        H[r] = {k: v for k, v in H[r].items() if v is not None}
    return H, d
