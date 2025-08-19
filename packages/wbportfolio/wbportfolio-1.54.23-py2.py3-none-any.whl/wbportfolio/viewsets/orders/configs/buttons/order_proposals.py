from wbcore import serializers as wb_serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display import create_simple_display


class NormalizeSerializer(wb_serializers.Serializer):
    total_cash_weight = wb_serializers.FloatField(default=0, precision=4, percent=True)


class ResetSerializer(wb_serializers.Serializer):
    use_desired_target_weight = wb_serializers.BooleanField(
        default=False,
        label="Use initial target weight",
        help_text="If True, the target weight used will be the value at the time the order proposal was submitted (as it may have changed due to previous modifications). If False, the delta weight will be set to 0 instead.",
    )


class OrderProposalButtonConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.DropDownButton(
                label="Tools",
                buttons=(
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:orderproposal",),
                        key="replay",
                        icon=WBIcon.SYNCHRONIZE.icon,
                        label="Replay Orders",
                        description_fields="""
                        <p>Replay Orders. It will recompute all assets positions until next order proposal day (or today otherwise) </p>
                        """,
                        action_label="Replay Order",
                        title="Replay Order",
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:orderproposal",),
                        key="reset",
                        icon=WBIcon.REGENERATE.icon,
                        label="Reset Orders",
                        description_fields="""
                            <p><strong>Warning:</strong>This action will reset the order delta weight to either 0 or the difference between the previous weight and the locked target weight, depending on the user’s choice.</p>
                            <p><strong>Note:</strong>This operation will change the current delta weights and cannot be undone</p>
                            """,
                        action_label="Reset Orders",
                        title="Reset Orders",
                        serializer=ResetSerializer,
                        instance_display=create_simple_display([["use_desired_target_weight"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:orderproposal",),
                        key="normalize",
                        icon=WBIcon.EDIT.icon,
                        label="Normalize Orders",
                        description_fields="""
                            <p>Make sure all orders normalize to a total target weight of (100 - {{total_cash_weight}})%</p>
                            """,
                        action_label="Normalize Orders",
                        title="Normalize Orders",
                        serializer=NormalizeSerializer,
                        instance_display=create_simple_display([["total_cash_weight"]]),
                    ),
                    bt.ActionButton(
                        method=RequestType.PATCH,
                        identifiers=("wbportfolio:orderproposal",),
                        key="deleteall",
                        icon=WBIcon.DELETE.icon,
                        label="Delete All Orders",
                        description_fields="""
                    <p>Delete all orders from this order proposal?</p>
                    """,
                        action_label="Delete All Orders",
                        title="Delete All Orders",
                    ),
                ),
            ),
        }

    def get_custom_instance_buttons(self):
        return self.get_custom_list_instance_buttons()
