from typing import Optional

from wbcore.contrib.color.enums import WBColor
from wbcore.metadata.configs import display as dp
from wbcore.metadata.configs.display.instance_display import Inline, Layout, Page
from wbcore.metadata.configs.display.instance_display.operators import default
from wbcore.metadata.configs.display.instance_display.shortcuts import Display
from wbcore.metadata.configs.display.view_config import DisplayViewConfig

from wbportfolio.models import OrderProposal


class OrderProposalDisplayConfig(DisplayViewConfig):
    def get_list_display(self) -> Optional[dp.ListDisplay]:
        return dp.ListDisplay(
            fields=[
                dp.Field(key="trade_date", label="Order Date"),
                dp.Field(key="rebalancing_model", label="Rebalancing Model"),
                dp.Field(key="comment", label="Comment"),
            ],
            legends=[
                dp.Legend(
                    key="status",
                    items=[
                        dp.LegendItem(
                            icon=WBColor.BLUE_LIGHT.value,
                            label=OrderProposal.Status.DRAFT.label,
                            value=OrderProposal.Status.DRAFT.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.YELLOW_LIGHT.value,
                            label=OrderProposal.Status.SUBMIT.label,
                            value=OrderProposal.Status.SUBMIT.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.GREEN_LIGHT.value,
                            label=OrderProposal.Status.APPROVED.label,
                            value=OrderProposal.Status.APPROVED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_LIGHT.value,
                            label=OrderProposal.Status.DENIED.label,
                            value=OrderProposal.Status.DENIED.value,
                        ),
                        dp.LegendItem(
                            icon=WBColor.RED_DARK.value,
                            label=OrderProposal.Status.FAILED.label,
                            value=OrderProposal.Status.FAILED.value,
                        ),
                    ],
                ),
            ],
            formatting=[
                dp.Formatting(
                    column="status",
                    formatting_rules=[
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.BLUE_LIGHT.value},
                            condition=("==", OrderProposal.Status.DRAFT.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.YELLOW_LIGHT.value},
                            condition=("==", OrderProposal.Status.SUBMIT.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.GREEN_LIGHT.value},
                            condition=("==", OrderProposal.Status.APPROVED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_LIGHT.value},
                            condition=("==", OrderProposal.Status.DENIED.value),
                        ),
                        dp.FormattingRule(
                            style={"backgroundColor": WBColor.RED_DARK.value},
                            condition=("==", OrderProposal.Status.FAILED.value),
                        ),
                    ],
                )
            ],
        )

    def get_instance_display(self) -> Display:
        return Display(
            pages=[
                Page(
                    title="Main Information",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[
                                ["status", "status", "status"],
                                ["trade_date", "total_cash_weight", "min_order_value"],
                                ["rebalancing_model", "target_portfolio", "target_portfolio"]
                                if self.view.new_mode
                                else ["rebalancing_model", "rebalancing_model", "rebalancing_model"],
                                ["comment", "comment", "comment"],
                            ],
                        ),
                    },
                ),
                Page(
                    title="Orders",
                    layouts={
                        default(): Layout(
                            grid_template_areas=[["orders"]],
                            grid_template_rows=["1fr"],
                            inlines=[Inline(key="orders", endpoint="orders")],
                        ),
                    },
                ),
            ]
        )
