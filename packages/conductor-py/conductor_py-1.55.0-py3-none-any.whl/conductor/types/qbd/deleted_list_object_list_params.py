# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DeletedListObjectListParams"]


class DeletedListObjectListParams(TypedDict, total=False):
    object_types: Required[
        Annotated[
            List[
                Literal[
                    "account",
                    "billing_rate",
                    "class",
                    "currency",
                    "customer",
                    "customer_message",
                    "customer_type",
                    "date_driven_terms",
                    "employee",
                    "inventory_site",
                    "item_discount",
                    "item_fixed_asset",
                    "item_group",
                    "item_inventory",
                    "item_inventory_assembly",
                    "item_non_inventory",
                    "item_other_charge",
                    "item_payment",
                    "item_sales_tax",
                    "item_sales_tax_group",
                    "item_service",
                    "item_subtotal",
                    "job_type",
                    "other_name",
                    "payment_method",
                    "payroll_item_non_wage",
                    "payroll_item_wage",
                    "price_level",
                    "sales_representative",
                    "sales_tax_code",
                    "ship_method",
                    "standard_terms",
                    "to_do",
                    "unit_of_measure_set",
                    "vehicle",
                    "vendor",
                    "vendor_type",
                    "workers_comp_code",
                ]
            ],
            PropertyInfo(alias="objectTypes"),
        ]
    ]
    """Filter for deleted list-objects by their list-object type(s)."""

    conductor_end_user_id: Required[Annotated[str, PropertyInfo(alias="Conductor-End-User-Id")]]
    """
    The ID of the EndUser to receive this request (e.g.,
    `"Conductor-End-User-Id: {{END_USER_ID}}"`).
    """

    deleted_after: Annotated[str, PropertyInfo(alias="deletedAfter")]
    """
    Filter for deleted list-objects deleted on or after this date and time, within
    the last 90 days (QuickBooks limit), in ISO 8601 format (YYYY-MM-DDTHH:mm:ss).
    If you only provide a date (YYYY-MM-DD), the time is assumed to be 00:00:00 of
    that day.
    """

    deleted_before: Annotated[str, PropertyInfo(alias="deletedBefore")]
    """
    Filter for deleted list-objects deleted on or before this date and time, within
    the last 90 days (QuickBooks limit), in ISO 8601 format (YYYY-MM-DDTHH:mm:ss).
    If you only provide a date (YYYY-MM-DD), the time is assumed to be 23:59:59 of
    that day.
    """
