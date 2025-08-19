import logging
import math
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, TypeVar

from celery import shared_task
from django.core.exceptions import ValidationError
from django.db import DatabaseError, models
from django.db.models import (
    F,
    OuterRef,
    Subquery,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce, Round
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from pandas._libs.tslibs.offsets import BDay
from wbcompliance.models.risk_management.mixins import RiskCheckMixin
from wbcore.contrib.authentication.models import User
from wbcore.contrib.icons import WBIcon
from wbcore.contrib.notifications.dispatch import send_notification
from wbcore.enums import RequestType
from wbcore.metadata.configs.buttons import ActionButton
from wbcore.models import WBModel
from wbcore.utils.models import CloneMixin
from wbfdm.models import InstrumentPrice
from wbfdm.models.instruments.instruments import Cash, Instrument

from wbportfolio.models.asset import AssetPosition
from wbportfolio.models.roles import PortfolioRole
from wbportfolio.pms.trading import TradingService
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import Position as PositionDTO

from .orders import Order

logger = logging.getLogger("pms")

SelfOrderProposal = TypeVar("SelfOrderProposal", bound="OrderProposal")


class OrderProposal(CloneMixin, RiskCheckMixin, WBModel):
    trade_date = models.DateField(verbose_name="Trading Date")

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMIT = "SUBMIT", "Pending"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"
        FAILED = "FAILED", "Failed"

    comment = models.TextField(default="", verbose_name="Order Comment", blank=True)
    status = FSMField(default=Status.DRAFT, choices=Status.choices, verbose_name="Status")
    rebalancing_model = models.ForeignKey(
        "wbportfolio.RebalancingModel",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="order_proposals",
        verbose_name="Rebalancing Model",
        help_text="Rebalancing Model that generates the target portfolio",
    )
    portfolio = models.ForeignKey(
        "wbportfolio.Portfolio", related_name="order_proposals", on_delete=models.PROTECT, verbose_name="Portfolio"
    )
    creator = models.ForeignKey(
        "directory.Person",
        blank=True,
        null=True,
        related_name="order_proposals",
        on_delete=models.PROTECT,
        verbose_name="Owner",
    )
    min_order_value = models.IntegerField(
        default=0, verbose_name="Minimum Order Value", help_text="Minimum Order Value in the Portfolio currency"
    )
    total_cash_weight = models.DecimalField(
        default=Decimal("0"),
        decimal_places=4,
        max_digits=5,
        verbose_name="Total Cash Weight",
        help_text="The desired percentage for the cash component. The remaining percentage (100% minus this value) will be allocated to total target weighting. Default is 0%.",
    )

    class Meta:
        verbose_name = "Order Proposal"
        verbose_name_plural = "Order Proposals"
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "trade_date"],
                name="unique_order_proposal",
            ),
        ]

    def save(self, *args, **kwargs):
        # if a order proposal is created before the existing earliest order proposal, we automatically shift the linked instruments inception date to allow automatic NAV computation since the new inception date
        if not self.portfolio.order_proposals.filter(trade_date__lt=self.trade_date).exists():
            # we need to set the inception date as the first order proposal trade date (and thus, the first position date). We expect a NAV at 100 then
            self.portfolio.instruments.filter(inception_date__gt=self.trade_date).update(
                inception_date=self.trade_date
            )
        super().save(*args, **kwargs)

    @property
    def check_evaluation_date(self):
        return self.trade_date

    @property
    def checked_object(self) -> Any:
        return self.portfolio

    @cached_property
    def portfolio_total_asset_value(self) -> Decimal:
        return self.portfolio.get_total_asset_value(self.last_effective_date)

    @cached_property
    def validated_trading_service(self) -> TradingService:
        """
        This property holds the validated trading services and cache it.This property expect to be set only if is_valid return True
        """
        target_portfolio = self.convert_to_portfolio()

        return TradingService(
            self.trade_date,
            effective_portfolio=self._get_default_effective_portfolio(),
            target_portfolio=target_portfolio,
            total_target_weight=target_portfolio.total_weight,
        )

    @cached_property
    def last_effective_date(self) -> date:
        try:
            return self.portfolio.assets.filter(date__lt=self.trade_date).latest("date").date
        except AssetPosition.DoesNotExist:
            return self.value_date

    @cached_property
    def value_date(self) -> date:
        return (self.trade_date - BDay(1)).date()

    @property
    def previous_order_proposal(self) -> SelfOrderProposal | None:
        future_proposals = OrderProposal.objects.filter(portfolio=self.portfolio).filter(
            trade_date__lt=self.trade_date, status=OrderProposal.Status.APPROVED
        )
        if future_proposals.exists():
            return future_proposals.latest("trade_date")
        return None

    @property
    def next_order_proposal(self) -> SelfOrderProposal | None:
        future_proposals = OrderProposal.objects.filter(portfolio=self.portfolio).filter(
            trade_date__gt=self.trade_date, status=OrderProposal.Status.APPROVED
        )
        if future_proposals.exists():
            return future_proposals.earliest("trade_date")
        return None

    @property
    def cash_component(self) -> Cash:
        return Cash.objects.get_or_create(
            currency=self.portfolio.currency, defaults={"is_cash": True, "name": self.portfolio.currency.title}
        )[0]

    @property
    def total_expected_target_weight(self) -> Decimal:
        return Decimal("1") - self.total_cash_weight

    def get_orders(self):
        base_qs = self.orders.all().annotate(
            last_effective_date=Subquery(
                AssetPosition.unannotated_objects.filter(
                    date__lt=OuterRef("value_date"),
                    portfolio=OuterRef("portfolio"),
                )
                .order_by("-date")
                .values("date")[:1]
            ),
            previous_weight=Coalesce(
                Subquery(
                    AssetPosition.unannotated_objects.filter(
                        underlying_quote=OuterRef("underlying_instrument"),
                        date=OuterRef("last_effective_date"),
                        portfolio=OuterRef("portfolio"),
                    )
                    .values("portfolio")
                    .annotate(s=Sum("weighting"))
                    .values("s")[:1]
                ),
                Decimal(0),
            ),
            contribution=F("previous_weight") * (F("daily_return") + Value(Decimal("1"))),
        )
        portfolio_contribution = base_qs.aggregate(s=Sum("contribution"))["s"] or Decimal("1")
        orders = base_qs.annotate(
            effective_weight=Round(
                F("contribution") / Value(portfolio_contribution), precision=Order.ORDER_WEIGHTING_PRECISION
            ),
            tmp_effective_weight=F("contribution") / Value(portfolio_contribution),
            target_weight=Round(F("effective_weight") + F("weighting"), precision=Order.ORDER_WEIGHTING_PRECISION),
            effective_shares=Coalesce(
                Subquery(
                    AssetPosition.objects.filter(
                        underlying_quote=OuterRef("underlying_instrument"),
                        date=OuterRef("last_effective_date"),
                        portfolio=OuterRef("portfolio"),
                    )
                    .values("portfolio")
                    .annotate(s=Sum("shares"))
                    .values("s")[:1]
                ),
                Decimal(0),
            ),
            target_shares=F("effective_shares") + F("shares"),
        )
        total_effective_weight = orders.aggregate(s=models.Sum("effective_weight"))["s"] or Decimal("1")
        with suppress(Order.DoesNotExist):
            largest_order = orders.latest("effective_weight")
            if quant_error := Decimal("1") - total_effective_weight:
                orders = orders.annotate(
                    effective_weight=models.Case(
                        models.When(
                            id=largest_order.id, then=models.F("effective_weight") + models.Value(Decimal(quant_error))
                        ),
                        default=models.F("effective_weight"),
                    ),
                    target_weight=models.Case(
                        models.When(
                            id=largest_order.id, then=models.F("target_weight") + models.Value(Decimal(quant_error))
                        ),
                        default=models.F("target_weight"),
                    ),
                )
        return orders.annotate(
            has_warnings=models.Case(
                models.When(models.Q(price=0) | models.Q(target_weight__lt=0), then=Value(True)), default=Value(False)
            ),
        )

    def __str__(self) -> str:
        return f"{self.portfolio.name}: {self.trade_date} ({self.status})"

    def convert_to_portfolio(
        self, use_effective: bool = False, with_cash: bool = True, use_desired_target_weight: bool = False
    ) -> PortfolioDTO:
        """
        Data Transfer Object
        Returns:
            DTO order object
        """
        portfolio = {}
        for asset in self.portfolio.assets.filter(date=self.last_effective_date):
            portfolio[asset.underlying_quote] = dict(
                shares=asset._shares,
                weighting=asset.weighting,
                delta_weight=Decimal("0"),
                price=asset._price,
                currency_fx_rate=asset._currency_fx_rate,
            )
        for order in self.get_orders():
            previous_weight = order._previous_weight
            if use_desired_target_weight and order.desired_target_weight is not None:
                delta_weight = order.desired_target_weight - previous_weight
            else:
                delta_weight = order.weighting
            portfolio[order.underlying_instrument] = dict(
                weighting=previous_weight,
                delta_weight=delta_weight,
                shares=order._target_shares if not use_effective else order._effective_shares,
                price=order.price,
                currency_fx_rate=order.currency_fx_rate,
            )
        previous_weights = dict(map(lambda r: (r[0].id, float(r[1]["weighting"])), portfolio.items()))
        try:
            last_returns, portfolio_contribution = self.portfolio.get_analytic_portfolio(
                self.value_date, weights=previous_weights, use_dl=True
            ).get_contributions()
            last_returns = last_returns.to_dict()
        except ValueError:
            last_returns, portfolio_contribution = {}, 1
        positions = []
        total_weighting = Decimal("0")
        for instrument, row in portfolio.items():
            weighting = row["weighting"]
            daily_return = Decimal(last_returns.get(instrument.id, 0))

            if not use_effective:
                drifted_weight = (
                    round(
                        weighting * (daily_return + Decimal("1")) / Decimal(portfolio_contribution),
                        Order.ORDER_WEIGHTING_PRECISION,
                    )
                    if portfolio_contribution
                    else weighting
                )
                weighting = drifted_weight + row["delta_weight"]
            positions.append(
                PositionDTO(
                    underlying_instrument=instrument.id,
                    instrument_type=instrument.instrument_type.id,
                    weighting=weighting,
                    daily_return=daily_return if use_effective else Decimal("0"),
                    shares=row["shares"],
                    currency=instrument.currency.id,
                    date=self.last_effective_date if use_effective else self.trade_date,
                    is_cash=instrument.is_cash or instrument.is_cash_equivalent,
                    price=row["price"],
                    currency_fx_rate=row["currency_fx_rate"],
                )
            )
            total_weighting += weighting
        if portfolio and with_cash and total_weighting and (cash_weight := Decimal("1") - total_weighting):
            cash_position = self.get_estimated_target_cash(target_cash_weight=cash_weight)
            positions.append(cash_position._build_dto())
        return PortfolioDTO(positions)

    # Start tools methods
    def _clone(self, **kwargs) -> SelfOrderProposal:
        """
        Method to clone self as a new order proposal. It will automatically shift the order date if a proposal already exists
        Args:
            **kwargs: The keyword arguments
        Returns:
            The cloned order proposal
        """
        trade_date = kwargs.get("clone_date", self.trade_date)

        # Find the next valid order date
        while OrderProposal.objects.filter(portfolio=self.portfolio, trade_date=trade_date).exists():
            trade_date += timedelta(days=1)

        order_proposal_clone = OrderProposal.objects.create(
            trade_date=trade_date,
            comment=kwargs.get("clone_comment", self.comment),
            status=OrderProposal.Status.DRAFT,
            rebalancing_model=self.rebalancing_model,
            portfolio=self.portfolio,
            creator=self.creator,
        )
        for order in self.orders.all():
            order.id = None
            order.order_proposal = order_proposal_clone
            order.save()

        return order_proposal_clone

    def normalize_orders(self):
        """
        Call the trading service with the existing orders and normalize them in order to obtain a total sum target weight of 100%
        The existing order will be modified directly with the given normalization factor
        """
        service = TradingService(
            self.trade_date,
            effective_portfolio=self._get_default_effective_portfolio(),
            target_portfolio=self.convert_to_portfolio(use_effective=False, with_cash=False),
            total_target_weight=self.total_expected_target_weight,
        )
        leftovers_orders = self.orders.all()
        for underlying_instrument_id, order_dto in service.trades_batch.trades_map.items():
            with suppress(Order.DoesNotExist):
                order = self.orders.get(underlying_instrument_id=underlying_instrument_id)
                order.weighting = round(order_dto.delta_weight, Order.ORDER_WEIGHTING_PRECISION)
                order.save()
                leftovers_orders = leftovers_orders.exclude(id=order.id)
        leftovers_orders.delete()
        self.fix_quantization()

    def fix_quantization(self):
        if self.orders.exists():
            t_weight = self.get_orders().aggregate(models.Sum("target_weight"))["target_weight__sum"] or Decimal("0.0")
            # we handle quantization error due to the decimal max digits. In that case, we take the biggest order (highest weight) and we remove the quantization error
            if quantize_error := (t_weight - self.total_expected_target_weight):
                biggest_order = self.orders.latest("weighting")
                biggest_order.weighting -= quantize_error
                biggest_order.save()

    def _get_default_target_portfolio(self, use_desired_target_weight: bool = False, **kwargs) -> PortfolioDTO:
        if self.rebalancing_model:
            params = {}
            if rebalancer := getattr(self.portfolio, "automatic_rebalancer", None):
                params.update(rebalancer.parameters)
            params.update(kwargs)
            return self.rebalancing_model.get_target_portfolio(
                self.portfolio, self.trade_date, self.value_date, **params
            )
        return self.convert_to_portfolio(use_effective=False, use_desired_target_weight=use_desired_target_weight)

    def _get_default_effective_portfolio(self):
        return self.convert_to_portfolio(use_effective=True)

    def reset_orders(
        self,
        target_portfolio: PortfolioDTO | None = None,
        effective_portfolio: PortfolioRole | None = None,
        validate_order: bool = True,
        use_desired_target_weight: bool = False,
    ):
        """
        Will delete all existing orders and recreate them from the method `create_or_update_trades`
        """
        if self.rebalancing_model:
            self.orders.all().delete()
        # delete all existing orders
        # Get effective and target portfolio
        if not target_portfolio:
            target_portfolio = self._get_default_target_portfolio(use_desired_target_weight=use_desired_target_weight)
        if not effective_portfolio:
            effective_portfolio = self._get_default_effective_portfolio()
        if target_portfolio:
            service = TradingService(
                self.trade_date,
                effective_portfolio=effective_portfolio,
                target_portfolio=target_portfolio,
                total_target_weight=self.total_expected_target_weight,
            )
            if validate_order:
                service.is_valid()
                orders = service.validated_trades
            else:
                orders = service.trades_batch.trades_map.values()

            for order_dto in orders:
                instrument = Instrument.objects.get(id=order_dto.underlying_instrument)
                currency_fx_rate = instrument.currency.convert(
                    self.value_date, self.portfolio.currency, exact_lookup=True
                )
                # we cannot do a bulk-create because Order is a multi table inheritance
                weighting = round(order_dto.delta_weight, Order.ORDER_WEIGHTING_PRECISION)
                daily_return = order_dto.daily_return
                try:
                    order = self.orders.get(underlying_instrument=instrument)
                    order.weighting = weighting
                    order.currency_fx_rate = currency_fx_rate
                    order.daily_return = daily_return
                except Order.DoesNotExist:
                    order = Order(
                        underlying_instrument=instrument,
                        order_proposal=self,
                        value_date=self.trade_date,
                        weighting=weighting,
                        daily_return=daily_return,
                        currency_fx_rate=currency_fx_rate,
                    )
                order.price = order.get_price()
                # if we cannot automatically find a price, we consider the stock is invalid and we sell it
                if not order.price:
                    order.price = Decimal("0.0")
                    order.weighting = -order_dto.effective_weight

                order.save()
        # final sanity check to make sure invalid order with effective and target weight of 0 are automatically removed:
        self.get_orders().filter(target_weight=0, effective_weight=0).delete()

        self.fix_quantization()

        for order in self.get_orders():
            order.order_type = Order.get_type(weighting, order_dto.previous_weight, order_dto.target_weight)
            order.save()

    def approve_workflow(
        self,
        approve_automatically: bool = True,
        silent_exception: bool = False,
        force_reset_order: bool = False,
        **reset_order_kwargs,
    ):
        if self.status == OrderProposal.Status.APPROVED:
            logger.info("Reverting order proposal ...")
            self.revert()
        if self.status == OrderProposal.Status.DRAFT:
            if (
                self.rebalancing_model or force_reset_order
            ):  # if there is no position (for any reason) or we the order proposal has a rebalancer model attached (orders are computed based on an aglo), we reapply this order proposal
                logger.info("Resetting orders ...")
                try:  # we silent any validation error while setting proposal, because if this happens, we assume the current order proposal state if valid and we continue to batch compute
                    self.reset_orders(**reset_order_kwargs)
                except (ValidationError, DatabaseError) as e:
                    self.status = OrderProposal.Status.FAILED
                    if not silent_exception:
                        raise ValidationError(e)
                    return
            logger.info("Submitting order proposal ...")
            self.submit()
        if self.status == OrderProposal.Status.SUBMIT:
            logger.info("Approving order proposal ...")
            if approve_automatically and self.portfolio.can_be_rebalanced:
                self.approve(replay=False)

    def replay(self, broadcast_changes_at_date: bool = True, reapply_order_proposal: bool = False):
        last_order_proposal = self
        last_order_proposal_created = False
        self.portfolio.load_builder_returns(self.trade_date, date.today())
        while last_order_proposal and last_order_proposal.status == OrderProposal.Status.APPROVED:
            last_order_proposal.portfolio = self.portfolio  # we set the same ptf reference
            if not last_order_proposal_created:
                if reapply_order_proposal:
                    logger.info(f"Replaying order proposal {last_order_proposal}")
                    last_order_proposal.approve_workflow(silent_exception=True, force_reset_order=True)
                    last_order_proposal.save()
                else:
                    logger.info(f"Resetting order proposal {last_order_proposal}")
                    last_order_proposal.reset_orders()
                if last_order_proposal.status != OrderProposal.Status.APPROVED:
                    break
            next_order_proposal = last_order_proposal.next_order_proposal
            if next_order_proposal:
                next_trade_date = next_order_proposal.trade_date - timedelta(days=1)
            elif next_expected_rebalancing_date := self.portfolio.get_next_rebalancing_date(
                last_order_proposal.trade_date
            ):
                next_trade_date = (
                    next_expected_rebalancing_date + timedelta(days=7)
                )  # we don't know yet if rebalancing is valid and can be executed on `next_expected_rebalancing_date`, so we add safety window of 7 days
            else:
                next_trade_date = date.today()
            next_trade_date = min(next_trade_date, date.today())
            gen = self.portfolio.drift_weights(
                last_order_proposal.trade_date, next_trade_date, stop_at_rebalancing=True
            )
            try:
                while True:
                    self.portfolio.builder.add(next(gen))
            except StopIteration as e:
                overriding_order_proposal = e.value

            self.portfolio.builder.bulk_create_positions(
                delete_leftovers=True,
            )
            for draft_tp in OrderProposal.objects.filter(
                portfolio=self.portfolio,
                trade_date__gt=last_order_proposal.trade_date,
                trade_date__lte=next_trade_date,
                status=OrderProposal.Status.DRAFT,
            ):
                draft_tp.reset_orders()
            if overriding_order_proposal:
                last_order_proposal_created = True
                last_order_proposal = overriding_order_proposal
            else:
                last_order_proposal_created = False
                last_order_proposal = next_order_proposal
        if broadcast_changes_at_date:
            self.portfolio.builder.schedule_change_at_dates(synchronous=False, evaluate_rebalancer=False)

    def invalidate_future_order_proposal(self):
        # Delete all future automatic order proposals and set the manual one into a draft state
        self.portfolio.order_proposals.filter(
            trade_date__gt=self.trade_date, rebalancing_model__isnull=False, comment="Automatic rebalancing"
        ).delete()
        for future_order_proposal in self.portfolio.order_proposals.filter(
            trade_date__gt=self.trade_date, status=OrderProposal.Status.APPROVED
        ):
            future_order_proposal.revert()
            future_order_proposal.save()

    def get_estimated_shares(
        self, weight: Decimal, underlying_quote: Instrument, quote_price: Decimal
    ) -> Decimal | None:
        """
        Estimates the number of shares for a order based on the given weight and underlying quote.

        This method calculates the estimated shares by dividing the order's total value in the portfolio's currency by the price of the underlying quote in the same currency. It handles currency conversion and suppresses any ValueError that might occur during the price retrieval.

        Args:
            weight (Decimal): The weight of the order.
            underlying_quote (Instrument): The underlying instrument for the order.

        Returns:
            Decimal | None: The estimated number of shares or None if the calculation fails.
        """
        # Retrieve the price of the underlying quote on the order date TODO: this is very slow and probably due to the to_date argument to the dl which slowdown drastically the query

        # Calculate the order's total value in the portfolio's currency
        trade_total_value_fx_portfolio = self.portfolio_total_asset_value * weight

        # Convert the quote price to the portfolio's currency
        price_fx_portfolio = quote_price * underlying_quote.currency.convert(
            self.trade_date, self.portfolio.currency, exact_lookup=False
        )

        # If the price is valid, calculate and return the estimated shares
        if price_fx_portfolio:
            return trade_total_value_fx_portfolio / price_fx_portfolio

    def get_round_lot_size(self, shares: Decimal, underlying_quote: Instrument) -> Decimal:
        if (round_lot_size := underlying_quote.round_lot_size) != 1 and (
            not underlying_quote.exchange or underlying_quote.exchange.apply_round_lot_size
        ):
            if shares > 0:
                shares = math.ceil(shares / round_lot_size) * round_lot_size
            elif abs(shares) > round_lot_size:
                shares = math.floor(shares / round_lot_size) * round_lot_size
        return shares

    def get_estimated_target_cash(self, target_cash_weight: Decimal | None = None) -> AssetPosition:
        """
        Estimates the target cash weight and shares for a order proposal.

        This method calculates the target cash weight by summing the weights of cash orders and adding any leftover weight from non-cash orders. It then estimates the target shares for this cash component if the portfolio is not only weighting-based.

        Args:
            target_cash_weight (Decimal): the expected target cash weight (Optional). If not provided, we estimate from the existing orders

        Returns:
            tuple[Decimal, Decimal]: A tuple containing the target cash weight and the estimated target shares.
        """
        # Retrieve orders with base information
        orders = self.get_orders()
        # Calculate the total target weight of all orders
        total_target_weight = orders.exclude(underlying_instrument__is_cash=True).aggregate(
            s=models.Sum("target_weight")
        )["s"] or Decimal(0)
        if target_cash_weight is None:
            target_cash_weight = Decimal("1") - total_target_weight

        # Initialize target shares to zero
        total_target_shares = Decimal(0)

        # Get or create a cash component for the portfolio's currency
        cash_component = self.cash_component
        # If the portfolio is not only weighting-based, estimate the target shares for the cash component
        if not self.portfolio.only_weighting:
            # Estimate the target shares for the cash component
            with suppress(ValueError):
                total_target_shares = self.get_estimated_shares(target_cash_weight, cash_component, Decimal("1.0"))

        # otherwise, we create a new position
        underlying_quote_price = InstrumentPrice.objects.get_or_create(
            instrument=cash_component,
            date=self.trade_date,
            calculated=False,
            defaults={"net_value": Decimal(1)},
        )[0]
        return AssetPosition(
            underlying_quote=cash_component,
            portfolio_created=None,
            portfolio=self.portfolio,
            date=self.trade_date,
            weighting=target_cash_weight,
            initial_price=underlying_quote_price.net_value,
            initial_shares=total_target_shares,
            asset_valuation_date=self.trade_date,
            underlying_quote_price=underlying_quote_price,
            currency=cash_component.currency,
            is_estimated=False,
        )

    # Start FSM logics

    @transition(
        field=status,
        source=Status.DRAFT,
        target=Status.SUBMIT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        ),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.SEND.icon,
                key="submit",
                label="Submit",
                action_label="Submit",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def submit(self, by=None, description=None, **kwargs):
        orders = []
        orders_validation_warnings = []
        qs = self.get_orders()
        total_target_weight = Decimal("0")
        for order in qs:
            order_warnings = order.submit(
                by=by, description=description, portfolio_total_asset_value=self.portfolio_total_asset_value, **kwargs
            )
            if order_warnings:
                orders_validation_warnings.extend(order_warnings)
            orders.append(order)
            total_target_weight += order._target_weight

        Order.objects.bulk_update(orders, ["shares", "weighting", "desired_target_weight"])

        # If we estimate cash on this order proposal, we make sure to create the corresponding cash component
        estimated_cash_position = self.get_estimated_target_cash()
        target_portfolio = self.validated_trading_service.trades_batch.convert_to_portfolio(
            estimated_cash_position._build_dto()
        )
        self.evaluate_active_rules(self.trade_date, target_portfolio, asynchronously=True)
        self.total_cash_weight = Decimal("1") - total_target_weight
        return orders_validation_warnings

    def can_submit(self):
        errors = dict()
        errors_list = []
        service = self.validated_trading_service
        try:
            service.is_valid(ignore_error=True)
            # if service.trades_batch.total_abs_delta_weight == 0:
            #     errors_list.append(
            #         "There is no change detected in this order proposal. Please submit at last one valid order"
            #     )
            if len(service.validated_trades) == 0:
                errors_list.append(_("There is no valid order on this proposal"))
            if service.errors:
                errors_list.extend(service.errors)
            if errors_list:
                errors["non_field_errors"] = errors_list
        except ValidationError:
            errors["non_field_errors"] = service.errors
            with suppress(KeyError):
                del self.__dict__["validated_trading_service"]
        return errors

    @property
    def can_be_approved_or_denied(self):
        return not self.has_non_successful_checks and self.portfolio.is_manageable

    @transition(
        field=status,
        source=Status.SUBMIT,
        target=Status.APPROVED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.can_be_approved_or_denied,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.APPROVE.icon,
                key="approve",
                label="Approve",
                action_label="Approve",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def approve(self, by=None, description=None, replay: bool = True, **kwargs):
        # We validate order which will create or update the initial asset positions
        if not self.portfolio.can_be_rebalanced:
            raise ValueError("Non-Rebalanceable portfolio cannot be traded manually.")
        warnings = []
        # We do not want to create the estimated cash position if there is not orders in the order proposal (shouldn't be possible anyway)
        estimated_cash_position = self.get_estimated_target_cash()
        assets = {}
        for order in self.get_orders():
            with suppress(ValueError):
                # we add the corresponding asset only if it is not the cache position (already included in estimated_cash_position)
                if order.underlying_instrument != estimated_cash_position.underlying_quote:
                    assets[order.underlying_instrument.id] = order._target_weight

        # if there is cash leftover, we create an extra asset position to hold the cash component
        if estimated_cash_position.weighting and len(assets) > 0:
            warnings.append(
                f"We created automatically a cash position of weight {estimated_cash_position.weighting:.2%}"
            )
            assets[estimated_cash_position.underlying_quote.id] = estimated_cash_position.weighting

        self.portfolio.builder.add((self.trade_date, assets)).bulk_create_positions(
            force_save=True, is_estimated=False
        )
        if replay and self.portfolio.is_manageable:
            replay_as_task.delay(self.id, user_id=by.id if by else None, broadcast_changes_at_date=False)
        return warnings

    def can_approve(self):
        errors = dict()
        orders = self.get_orders()
        if not self.portfolio.can_be_rebalanced:
            errors["non_field_errors"] = [_("The portfolio does not allow manual rebalanced")]
        if not orders.exists():
            errors["non_field_errors"] = [
                _("At least one order needs to be submitted to be able to approve this proposal")
            ]
        if not self.portfolio.can_be_rebalanced:
            errors["portfolio"] = [
                [_("The portfolio needs to be a model portfolio in order to approve this order proposal manually")]
            ]
        if self.has_non_successful_checks:
            errors["non_field_errors"] = [_("The pre orders rules did not passed successfully")]
        if orders.filter(has_warnings=True).exclude(underlying_instrument__is_cash=True):
            errors["non_field_errors"] = [
                _("There is warning that needs to be addresses on the orders before approval.")
            ]
        return errors

    @transition(
        field=status,
        source=Status.SUBMIT,
        target=Status.DENIED,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.can_be_approved_or_denied,
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.DENY.icon,
                key="deny",
                label="Deny",
                action_label="Deny",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def deny(self, by=None, description=None, **kwargs):
        self.orders.all().delete()
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]

    def can_deny(self):
        errors = dict()
        if not self.orders.all().exists():
            errors["non_field_errors"] = [
                _("At least one order needs to be submitted to be able to deny this proposal")
            ]
        return errors

    @transition(
        field=status,
        source=Status.SUBMIT,
        target=Status.DRAFT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        )
        and instance.has_all_check_completed
        or not instance.checks.exists(),  # we wait for all checks to succeed before proposing the back to draft transition
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.UNDO.icon,
                key="backtodraft",
                label="Back to Draft",
                action_label="backtodraft",
                # description_fields="<p>Start: {{start}}</p><p>End: {{end}}</p><p>Title: {{title}}</p>",
            )
        },
    )
    def backtodraft(self, **kwargs):
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]
        self.checks.delete()

    def can_backtodraft(self):
        pass

    @transition(
        field=status,
        source=Status.APPROVED,
        target=Status.DRAFT,
        permission=lambda instance, user: PortfolioRole.is_portfolio_manager(
            user.profile, portfolio=instance.portfolio
        ),
        custom={
            "_transition_button": ActionButton(
                method=RequestType.PATCH,
                identifiers=("wbportfolio:orderproposal",),
                icon=WBIcon.REGENERATE.icon,
                key="revert",
                label="Revert",
                action_label="revert",
                description_fields="<p>Unapply orders and move everything back to draft (i.e. The underlying asset positions will change like the orders were never applied)</p>",
            )
        },
    )
    def revert(self, **kwargs):
        with suppress(KeyError):
            del self.__dict__["validated_trading_service"]
        self.portfolio.assets.filter(date=self.trade_date, is_estimated=False).update(
            is_estimated=True
        )  # we delete the existing portfolio as it has been reverted

    def can_revert(self):
        errors = dict()
        if not self.portfolio.can_be_rebalanced:
            errors["portfolio"] = [
                _("The portfolio needs to be a model portfolio in order to revert this order proposal manually")
            ]
        return errors

    # End FSM logics

    @classmethod
    def get_endpoint_basename(cls) -> str:
        return "wbportfolio:orderproposal"

    @classmethod
    def get_representation_endpoint(cls) -> str:
        return "wbportfolio:orderproposalrepresentation-list"

    @classmethod
    def get_representation_value_key(cls) -> str:
        return "id"

    @classmethod
    def get_representation_label_key(cls) -> str:
        return "{{_portfolio.name}} ({{trade_date}})"


@receiver(post_save, sender="wbportfolio.OrderProposal")
def post_fail_order_proposal(sender, instance: OrderProposal, created, raw, **kwargs):
    # if we have a order proposal in a fail state, we ensure that all future existing order proposal are either deleted (automatic one) or set back to draft
    if not raw and instance.status == OrderProposal.Status.FAILED:
        # we delete all order proposal that have a rebalancing model and are marked as "automatic" (quite hardcoded yet)
        instance.invalidate_future_order_proposal()
        instance.invalidate_future_order_proposal()


@shared_task(queue="portfolio")
def replay_as_task(order_proposal_id, user_id: int | None = None, **kwargs):
    order_proposal = OrderProposal.objects.get(id=order_proposal_id)
    order_proposal.replay(**kwargs)
    if user_id:
        user = User.objects.get(id=user_id)
        send_notification(
            code="wbportfolio.portfolio.replay_done",
            title="Order Proposal Replay Completed",
            body=f'We’ve successfully replayed your order proposal for "{order_proposal.portfolio}" from {order_proposal.trade_date:%Y-%m-%d}. You can now review its updated composition.',
            user=user,
            reverse_name="wbportfolio:portfolio-detail",
            reverse_args=[order_proposal.portfolio.id],
        )
