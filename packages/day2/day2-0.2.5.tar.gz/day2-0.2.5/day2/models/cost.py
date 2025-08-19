import re
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Utility function to convert camelCase or PascalCase to snake_case
def to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class GetCostByChargeTypeOutput(BaseModel):
    """Details of cost breakdown by charge type.

    This model provides a comprehensive breakdown of costs by various charge types.
    It supports dynamic fields, automatically converting any additional charge types
    from the API response to snake_case attributes.

    Attributes:
        total_cost: Total cost for the period
        usage: Standard usage charges
        bundled_discount: Bundled discount amount
        credit: Credits applied
        discount: General discounts applied
        discounted_usage: Usage charges after discounts
        fee: General fees
        refund: Refund amounts
        ri_fee: Reserved Instance fees
        tax: Tax charges
        savings_plan_upfront_fee: Upfront fee for Savings Plans
        savings_plan_recurring_fee: Recurring fee for Savings Plans
        savings_plan_covered_usage: Usage covered by Savings Plans
        savings_plan_negation: Savings Plan negation amounts
        spp_discount: SPP (Service Provider Program) discounts
        distributor_discount: Distributor discounts

    Note:
        Additional charge types returned by the API are automatically added as
        attributes with their names converted to snake_case format.
    """

    total_cost: Optional[float] = Field(None, alias="TotalCost")
    usage: Optional[float] = Field(None, alias="Usage")
    bundled_discount: Optional[float] = Field(None, alias="BundledDiscount")
    credit: Optional[float] = Field(None, alias="Credit")
    discount: Optional[float] = Field(None, alias="Discount")
    discounted_usage: Optional[float] = Field(None, alias="DiscountedUsage")
    fee: Optional[float] = Field(None, alias="Fee")
    refund: Optional[float] = Field(None, alias="Refund")
    ri_fee: Optional[float] = Field(None, alias="RIFee")
    tax: Optional[float] = Field(None, alias="Tax")
    savings_plan_upfront_fee: Optional[float] = Field(
        None, alias="SavingsPlanUpfrontFee"
    )
    savings_plan_recurring_fee: Optional[float] = Field(
        None, alias="SavingsPlanRecurringFee"
    )
    savings_plan_covered_usage: Optional[float] = Field(
        None, alias="SavingsPlanCoveredUsage"
    )
    savings_plan_negation: Optional[float] = Field(None, alias="SavingsPlanNegation")
    spp_discount: Optional[float] = Field(None, alias="SPPDiscount")
    distributor_discount: Optional[float] = Field(None, alias="DistributorDiscount")

    # Allow extra fields
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def handle_dynamic_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dynamic extra fields by converting them to snake_case."""
        known_fields = {
            field.alias or field_name for field_name, field in cls.model_fields.items()
        }
        # Dynamically handle all extra fields
        for key in list(values.keys()):
            if key not in known_fields:
                # Convert the extra field to snake_case and map it
                snake_case_key = to_snake_case(key)
                values[snake_case_key] = values.pop(key)
        return values
