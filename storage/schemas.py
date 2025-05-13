from ninja import Field, Schema


class UpgradePlanIn(Schema):
    """
    升級方案
    """

    new_plan: str = Field(examples=['BASIC', 'STANDARD', 'PREMIUM'])
