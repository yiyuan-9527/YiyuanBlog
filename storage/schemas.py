from typing import Literal

from ninja import Schema


class UpgradePlanIn(Schema):
    """
    升級方案
    """

    # 限制方案名稱只能是這三個
    new_plan: Literal['BASIC', 'STANDARD', 'PREMIUM']
