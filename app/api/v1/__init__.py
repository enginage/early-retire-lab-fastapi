from fastapi import APIRouter
from app.api.v1 import financial_institutions, expenses, income_targets, early_retirement_initial_setting, isa_accounts, isa_account_details, isa_account_sales, isa_account_dividends, pension_fund_accounts, pension_fund_account_details, irp_accounts, irp_account_details, common_code_masters, common_code_details, domestic_etfs, usa_etfs, experience_lab_stocks

api_router = APIRouter()
api_router.include_router(financial_institutions.router, prefix="/financial-institutions", tags=["financial-institutions"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(income_targets.router, prefix="/income-targets", tags=["income-targets"])
api_router.include_router(early_retirement_initial_setting.router, prefix="/early-retirement-initial-setting", tags=["early-retirement-initial-setting"])
api_router.include_router(isa_accounts.router, prefix="/isa-accounts", tags=["isa-accounts"])
api_router.include_router(isa_account_details.router, prefix="/isa-account-details", tags=["isa-account-details"])
api_router.include_router(isa_account_sales.router, prefix="/isa-account-sales", tags=["isa-account-sales"])
api_router.include_router(isa_account_dividends.router, prefix="/isa-account-dividends", tags=["isa-account-dividends"])
api_router.include_router(pension_fund_accounts.router, prefix="/pension-fund-accounts", tags=["pension-fund-accounts"])
api_router.include_router(pension_fund_account_details.router, prefix="/pension-fund-account-details", tags=["pension-fund-account-details"])
api_router.include_router(irp_accounts.router, prefix="/irp-accounts", tags=["irp-accounts"])
api_router.include_router(irp_account_details.router, prefix="/irp-account-details", tags=["irp-account-details"])
api_router.include_router(common_code_masters.router, prefix="/common-code-masters", tags=["common-code-masters"])
api_router.include_router(common_code_details.router, prefix="/common-code-details", tags=["common-code-details"])
api_router.include_router(domestic_etfs.router, prefix="/domestic-etfs", tags=["domestic-etfs"])
api_router.include_router(usa_etfs.router, prefix="/usa-etfs", tags=["usa-etfs"])
api_router.include_router(experience_lab_stocks.router, prefix="/experience-lab-stocks", tags=["experience-lab-stocks"])

