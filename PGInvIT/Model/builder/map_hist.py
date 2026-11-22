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
        64: B('unit_capital'), 65: B('distribution_repayment_of_capital'), 66: B('oe_capital_reserve'), 67: B('oe_retained_earnings'), 70: B('non_controlling_interest'),
        72: B('long_term_borrowings'), 73: B('short_term_borrowings'), 74: B('current_maturities'),
        80: B('dtl_gross_depreciation_difference'), 81: neg(B('dta_mat_credit_entitlement')), 82: {k: -(B('dta_total')[k] - (B('dta_mat_credit_entitlement').get(k) or 0)) for k in B('dta_total')}, 84: B('other_non_current_liabilities'), 85: B('long_term_provisions'),
        90: B('gross_block'), 91: B('accumulated_depreciation'), 92: B('impairment'), 94: B('cwip'), 96: B('intangibles_gross'), 97: add(B('intangibles_accumulated_amortisation'), B('intangibles_impairment_provision')),
        99: B('goodwill'), 100: B('non_current_investments'), 101: B('nc_trade_receivables'), 102: B('nc_other_financial_assets'), 103: B('nca_advance_tax_net_of_provisions'), 104: {k: (B('nc_other_non_current_assets').get(k) or 0) - (B('nca_advance_tax_net_of_provisions').get(k) or 0) for k in B('nc_other_non_current_assets')},
        107: B('inventories'), 108: B('trade_receivables'), 109: B('current_investments'), 111: B('other_bank_balances'), 110: B('cash_and_cash_equivalents'),
        113: B('other_current_financial_assets'), 114: B('other_current_assets_reported'), 117: B('trade_payables'),
        118: B('ocfl_dues_for_capital_expenditure'), 119: {k: (B('other_current_financial_liabilities').get(k) or 0) - (B('ocfl_dues_for_capital_expenditure').get(k) or 0) for k in B('other_current_financial_liabilities')}, 120: B('other_current_liabilities'), 122: B('current_tax_liabilities_net'),
        121: B('short_term_provisions'),
        132: C('cfo_profit_before_tax'), 134: C('cfo_adj_depreciation_amortisation'), 136: C('cfo_adj_impairment_reversal'),
        142: C('cfo_adj_finance_cost'), 143: add(C('cfo_adj_interest_income'), C('cfo_adj_interest_income_on_loans_to_spvs')),
        146: add(C('cfo_adj_excess_provision_written_back'), C('cfo_adj_provision_for_bad_doubtful_debts'), C('cfo_adj_profit_loss_on_disposal_of_fixed_assets')),
        149: C('wc_inventories'), 150: C('wc_trade_receivables'), 153: C('wc_trade_payables'),
        152: add(*[C(k) for k in ['wc_other_current_financial_liabilities', 'wc_other_non_financial_liabilities', 'wc_other_current_liabilities',
                                  'wc_provisions', 'wc_other_non_current_liabilities', 'wc_non_current_financial_assets',
                                  'wc_other_current_financial_assets', 'wc_earmarked_bank_balances', 'wc_other_current_assets', 'wc_other_non_current_assets']]),
        158: add(C('cfo_direct_taxes_paid_net'), C('cfo_income_tax_refund_received')),
        161: add(C('cfi_ppe_and_cwip'), C('cfi_purchase_of_intangible_assets')), 165: C('cfi_acquisition_of_non_controlling_interest'),
        169: C('cfi_interest_income_received'), 173: C('cfi_investment_in_fixed_deposits_net'),
        176: C('cff_proceeds_from_issue_of_unit_capital'), 179: C('cff_proceeds_from_borrowings'), 180: C('cff_repayment_of_borrowings'),
        184: C('cff_dividend_paid_to_nci'), 185: C('cff_finance_cost_paid'), 187: C('cff_distribution_to_unitholders'),
        191: add(C('opening_cash'), C('cash_acquired_on_acquisition_date')),
        265: O('nav_per_unit_fair_value_rs'),
    }
    for r in list(H):
        H[r] = {k: v for k, v in H[r].items() if v is not None}
    return H, d
