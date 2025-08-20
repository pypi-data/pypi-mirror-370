from __future__ import annotations

from enum import IntEnum
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Dict, ClassVar
from datetime import date, datetime, timedelta, timezone
from uuid import UUID, uuid4


def _utc_now() -> datetime:
    """Return the current UTC time with timezone information."""
    return datetime.now(timezone.utc)


class Offset(IntEnum):
    """
    Position offset types for order execution.

    Specifies how an order affects existing positions, particularly
    important in futures trading where position management is explicit.
    """

    UNKNOWN = 0  # Unknown or undefined offset
    OPEN = 1  # Open a new position
    CLOSE = 2  # Close an existing position
    CLOSE_TODAY = 3  # Close a position opened today
    CLOSE_YESTERDAY = 4  # Close a position opened before today

    @classmethod
    def is_open(cls, offset: Offset) -> bool:
        """
        Check if the offset is an open type.

        Args:
            offset: The offset to check

        Returns:
            bool: True if the offset is OPEN, False otherwise
        """
        return offset == cls.OPEN

    @classmethod
    def is_close(cls, offset: Offset) -> bool:
        """
        Check if the offset is any close type (CLOSE, CLOSE_TODAY, CLOSE_YESTERDAY).

        Uses a range check for better performance since all close types have
        consecutive enum values from 2 to 4.

        Args:
            offset: The offset to check

        Returns:
            bool: True if the offset is any close type, False otherwise
        """
        return 2 <= offset <= 4


class OrderType(IntEnum):
    """
    Order types for trading operations.

    Values are grouped by main categories with distinct ranges:
    - Unknown: 0
    - Limit orders: 100-199
    - Market orders: 200-299
    """

    UNKNOWN = 0  # Unknown or undefined order type

    # === Limit Orders (限价单) ===
    LIMIT = 100  # Basic limit order (限价单)
    LIMIT_FAK = 110  # Fill and Kill limit order (限价FAK, 剩余即撤销)
    LIMIT_FOK = 111  # Fill or Kill limit order (限价FOK, 全部成交或撤销)

    # === Market Orders (市价单) ===
    MARKET = 200  # Basic market order (市价单)
    MARKET_BOC = 210  # Best of counterparty (对手方最优价)
    MARKET_BOP = 211  # Best of party (己方最优价)
    MARKET_FAK = 220  # Fill and Kill (市价FAK, 剩余即撤销)
    MARKET_FOK = 221  # Fill or Kill (市价FOK, 全部成交或撤销)
    MARKET_B5TC = 230  # Best 5 then cancel (最优五档剩余撤销)
    MARKET_B5TL = 231  # Best 5 then limit (最优五档剩余转限价)
    MARKET_FAL = 240  # Fill and Limit (市价转限价)
    MARKET_BOPC = 241  # Best price Fill and Kill (最优价格剩余撤销)
    MARKET_BOPL = 242  # Best price then Limit (最优价格剩余转限价)

    @classmethod
    def is_limit(cls, order_type: OrderType) -> bool:
        """
        Check if the order type is any limit order type.

        Uses a range check for optimal performance since all limit order types
        have values in the range 100-199.

        Args:
            order_type: The order type to check

        Returns:
            bool: True if the order type is any limit order type, False otherwise
        """
        return 100 <= order_type < 200

    @classmethod
    def is_market(cls, order_type: OrderType) -> bool:
        """
        Check if the order type is any market order type.

        Uses a range check for optimal performance since all market order types
        have values in the range 200-299.

        Args:
            order_type: The order type to check

        Returns:
            bool: True if the order type is any market order type, False otherwise
        """
        return 200 <= order_type < 300


class OrderSide(IntEnum):
    """
    Direction of an order (buy or sell).

    Specifies whether the order is to purchase or sell an asset.
    """

    UNKNOWN = 0  # Unknown or undefined order side
    BUY = 1  # Buy/long order
    SELL = 2  # Sell/short order


class OrderStatus(IntEnum):
    """
    Status of an order in its lifecycle.

    Tracks the progression of an order from creation to completion.
    """

    UNKNOWN = 0  # Unknown or undefined status
    PENDING_NEW = 1  # Order created but not yet sent to exchange
    NEW = 2  # Order accepted by exchange but not yet executed
    PARTIALLY_FILLED = 3  # Order partially executed
    FILLED = 4  # Order fully executed
    PENDING_CANCEL = 5  # Cancellation requested but not confirmed
    CANCELLED = 6  # Order successfully cancelled
    REJECTED = 7  # Order rejected by exchange
    EXPIRED = 8  # Order expired without execution


class PositionSide(IntEnum):
    """
    Direction of a position (long or short).

    Indicates whether a position benefits from price increases (long)
    or decreases (short).
    """

    UNKNOWN = 0  # Unknown or undefined position side
    LONG = 1  # Long position (profits when price rises)
    SHORT = 2  # Short position (profits when price falls)


@dataclass(slots=True)
class Order:
    """
    Represents a trading order with complete lifecycle information.

    Required fields when creating an order:
    - symbol: Instrument to trade
    - offset: Open or close position
    - side: Buy or sell
    - size: Order quantity
    - price: Order price
    - order_type: Market, limit, etc.

    Other fields are either auto-generated or filled during processing.

    Note: This class is designed to be compatible with Polars DataFrames while
    maintaining data integrity through explicit recalculation of derived fields.
    """

    # Order identification
    client_order_id: str  # Client-assigned order identifier
    order_id: str  # System-assigned order identifier
    account_id: str  # Account identifier

    # Order parameters
    symbol: str  # Instrument to trade
    side: OrderSide  # Buy or sell
    position_side: PositionSide  # Long or short position effect
    size: float  # Order quantity
    price: float  # Order price
    order_type: OrderType  # Market, limit, etc.
    offset: Offset  # Open or close position
    status: OrderStatus  # Current order status

    # Timestamps
    created_at: datetime  # When order was created
    updated_at: datetime  # When order was last updated
    time_in_force: timedelta  # Duration for which the order is valid
    tdate: date = field(init=False)  # Trading date (derived from created_at)

    # Execution details with default values
    filled_size: float = 0.0  # Quantity filled
    filled_vwap: float = 0.0  # Volume-weighted average price of fills
    fee: float = 0.0  # Total fees for this order

    # Fields with default values
    rejection_reason: str = ""  # Reason if order was rejected

    # Class variables for default values
    DEFAULT_TIME_IN_FORCE: ClassVar[timedelta] = timedelta(days=1)

    # Derived fields
    is_filled: bool = field(init=True, default=False)  # Whether order is fully filled
    remaining_size: float = field(init=True, default=0.0)  # Remaining size to be filled
    expire_at: datetime = field(init=False)  # Calculated expiration time

    def __post_init__(self) -> None:
        """Validate order parameters and calculate derived fields after initialization."""
        if self.size <= 0:
            raise ValueError("Order size must be greater than 0")

        # Calculate expire_at from time_in_force
        self.expire_at = self.created_at + self.time_in_force

        # Simple tdate calculation from created_at
        self.tdate = self.created_at.date()

        # Initialize derived fields
        self.update_derived_fields()

    def update_derived_fields(self) -> None:
        """
        Recalculate all derived fields based on current values.

        Call this method after modifying filled_size or other fields that affect derived values.
        """
        self.remaining_size = self.size - self.filled_size
        self.is_filled = self.filled_size >= self.size

        # Update status based on fill state if not already terminal
        if self.status not in (
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        ):
            if self.is_filled:
                self.status = OrderStatus.FILLED
            elif self.filled_size > 0:
                self.status = OrderStatus.PARTIALLY_FILLED

    def update_with_execution(
        self, exec_size: float, exec_price: float, exec_fee: float = 0.0
    ) -> None:
        """
        Update order with execution details.

        Args:
            exec_size: Size executed in this fill
            exec_price: Price of this execution
            exec_fee: Fee for this execution
        """
        if exec_size <= 0:
            raise ValueError("Execution size must be positive")

        # Calculate new VWAP
        total_value_before = self.filled_size * self.filled_vwap
        total_value_after = total_value_before + (exec_size * exec_price)
        new_filled_size = self.filled_size + exec_size

        # Update fields
        self.fee += exec_fee
        self.filled_size = new_filled_size
        self.filled_vwap = (
            total_value_after / new_filled_size if new_filled_size > 0 else 0
        )
        self.updated_at = datetime.now()

        # Recalculate derived fields
        self.update_derived_fields()

    @classmethod
    def new(
        cls,
        symbol: str,
        offset: Offset,
        side: OrderSide,
        size: float,
        price: float,
        order_type: OrderType,
        time_in_force: Optional[timedelta] = None,
        client_order_id: Optional[str] = None,
        account_id: str = "",
        created_at: Optional[datetime] = None,
    ) -> "Order":
        """
        Create a new order with the required fields.

        This factory method handles the creation of a properly initialized order
        with all required fields and sensible defaults for optional fields.

        Args:
            symbol: Instrument to trade
            offset: Open or close position
            side: Buy or sell
            size: Order quantity
            price: Order price
            order_type: Market, limit, etc.
            time_in_force: Duration for which the order is valid (default: 1 day)
            client_order_id: Client-assigned order ID (default: auto-generated)
            account_id: Account identifier (default: empty string)
            created_at: Creation timestamp (default: current time)

        Returns:
            Order: A fully initialized order object
        """
        if created_at is None:
            created_at = datetime.now(timezone.utc)

        # Auto-determine position_side based on side and offset
        position_side = PositionSide.LONG
        if offset == Offset.OPEN:
            position_side = (
                PositionSide.LONG if side == OrderSide.BUY else PositionSide.SHORT
            )
        else:  # CLOSE
            position_side = (
                PositionSide.SHORT if side == OrderSide.BUY else PositionSide.LONG
            )

        # Generate client_order_id if not provided
        if client_order_id is None:
            prefix = "MKT" if order_type == OrderType.MARKET else "LMT"
            client_order_id = f"{prefix}_{uuid4().hex[:12]}"

        # Set default time_in_force
        if time_in_force is None:
            time_in_force = cls.DEFAULT_TIME_IN_FORCE

        return cls(
            client_order_id=client_order_id,
            order_id=client_order_id,  # Will be assigned by the system
            account_id=account_id,
            symbol=symbol,
            side=side,
            position_side=position_side,
            size=size,
            price=price,
            order_type=order_type,
            offset=offset,
            status=OrderStatus.PENDING_NEW,
            created_at=created_at,
            updated_at=created_at,
            time_in_force=time_in_force,
        )


@dataclass(slots=True)
class Execution:
    """
    Represents a single execution of an order.

    This class contains all details of a trade execution, including execution parameters,
    pricing information, and timestamps.
    """

    # Execution identification
    exec_id: str  # System-assigned execution identifier
    order_id: str  # Parent order identifier

    # Execution parameters
    symbol: str  # Instrument that was traded
    offset: Offset  # Open or close position
    side: OrderSide  # Buy or sell
    position_side: PositionSide  # Long or short position effect
    size: float  # Quantity executed
    price: float  # Execution price
    fee: float  # Fees for this execution

    # Timestamp
    ttime: datetime  # When execution occurred (renamed from created_at)
    tdate: date = field(init=False)  # Trading date (derived from ttime)

    # Fields with default values
    account_id: str = ""  # Account identifier

    def __post_init__(self) -> None:
        """Calculate tdate from ttime."""
        self.tdate = self.ttime.date()

    @classmethod
    def new_from_order(
        cls, filled_size: float, filled_price: float, order: Order
    ) -> Execution:
        """Create an execution from an order."""
        return cls(
            exec_id=str(uuid4()),
            order_id=order.order_id,
            symbol=order.symbol,
            offset=order.offset,
            side=order.side,
            position_side=order.position_side,
            size=filled_size,
            price=filled_price,
            fee=0.0,
            ttime=datetime.now(timezone.utc),
            account_id=order.account_id,
        )


@dataclass(slots=True)
class CancelOrder:
    """
    Represents a cancellation request for an existing order.

    This class tracks cancellation requests for risk management and operational purposes.
    It maintains a record of all cancellation attempts, which is essential for:

    1. Exchange compliance: Many exchanges impose higher fees or penalties when
       cancellation frequency exceeds certain thresholds.
    2. Risk management: Monitoring cancellation patterns to identify potential
       issues with trading algorithms or market conditions.
    3. Performance analysis: Evaluating order lifecycle efficiency and execution quality.

    The data in this class needs to be persisted and restorable at least for intraday
    trading sessions to maintain accurate cancellation counts and ensure proper
    application of exchange-specific cancellation rules.

    Attributes:
        client_order_id: Client-side identifier for the order being cancelled
        order_id: System-assigned identifier for the order being cancelled
        created_at: Timestamp when the cancellation request was initiated
    """

    # Order identifiers
    client_order_id: str  # Client-side order identifier
    order_id: str  # System-assigned order identifier

    # Timestamp
    created_at: datetime  # When cancellation request occurred


@dataclass(slots=True)
class CancelReject:
    """
    Represents a rejected cancellation request.

    Records details when an attempt to cancel an order is rejected.
    """

    # Order identifiers
    client_order_id: str  # Client-side order identifier
    order_id: str  # System-assigned order identifier

    # Rejection details
    symbol: str  # Instrument being traded
    reject_reason: str  # Explanation for the rejection
    original_order_status: (
        OrderStatus  # Status of order when cancellation was attempted
    )

    # Timestamp
    created_at: datetime  # When rejection occurred

    # Fields with default values (must come after non-default fields)
    reject_code: str = ""  # Error code for the rejection


@dataclass(slots=True)
class Cash:
    """
    Comprehensive cash balance information for a trading account.

    Tracks all aspects of an account's cash position including previous balance,
    deposits/withdrawals, realized/unrealized P&L, fees, and margin requirements.
    This provides a complete picture of the account's financial status.

    The key metrics include:
    - Previous balance (上日结存): Balance from previous trading day
    - Current balance components (deposits, withdrawals, P&L, fees)
    - Equity (当日权益): Total account value including unrealized P&L
    - Available funds (可用资金): Equity minus margin requirements
    - Risk ratio (风险度): Percentage of equity used as margin

    Note: This class is designed to be compatible with Polars DataFrames while
    maintaining data integrity through explicit recalculation of derived fields.
    """

    # Required field - must come before fields with defaults
    tdate: date  # Trading date for this cash snapshot

    # Timestamp of when this snapshot was created/updated
    ttime: datetime = field(default_factory=_utc_now)  # Snapshot timestamp

    # Trading date derived from ttime
    tdate: date = field(init=False)  # Trading date derived from ttime

    # Previous day balance
    previous_balance: float = 0.0  # Previous day's closing balance (上日结存)

    # Current day cash flows
    deposits: float = 0.0  # Cash deposits for current day (当日入金)
    withdrawals: float = 0.0  # Cash withdrawals for current day (当日出金)
    realized_pnl: float = 0.0  # Realized profit/loss from closed positions (平仓盈亏)
    unrealized_pnl: float = (
        0.0  # Unrealized profit/loss from open positions (持仓盯市盈亏)
    )
    fee: float = 0.0  # Trading commissions and fees (手续费)

    # Margin information
    margin_occupied: float = 0.0  # Margin required for current positions (保证金占用)
    frozen: float = 0.0  # Size that is frozen/locked (e.g., for pending orders)

    # Account details
    currency: str = "CNY"  # Currency of the cash balance
    account_id: str = ""  # Account identifier

    # Derived fields (calculated in __post_init__ and update_derived_fields)
    balance: float = field(
        init=False, default=0.0
    )  # Basic cash balance without unrealized P&L
    equity: float = field(
        init=False, default=0.0
    )  # Total account value including unrealized P&L (当日权益)
    available: float = field(
        init=False, default=0.0
    )  # Amount available for new positions (可用资金)
    risk_ratio: float = field(
        init=False, default=0.0
    )  # Risk ratio as percentage (风险度)

    def __post_init__(self) -> None:
        """Calculate derived fields after initialization."""
        # Derive tdate from ttime
        self.tdate = self.ttime.date()

        # Calculate financial derived fields
        self.update_derived_fields()

    def update_derived_fields(self) -> None:
        """
        Recalculate all derived fields based on current values.

        Call this method after modifying any field that affects derived values.
        """
        # Basic cash balance (without unrealized P&L)
        self.balance = (
            self.previous_balance
            + self.deposits
            - self.withdrawals
            + self.realized_pnl
            - self.fee
        )

        # Total equity including unrealized P&L
        self.equity = self.balance + self.unrealized_pnl

        # Available funds (equity minus margin requirements)
        self.available = self.equity - self.margin_occupied - self.frozen

        # Risk ratio (margin as percentage of equity)
        self.risk_ratio = (
            (self.margin_occupied / self.equity * 100) if self.equity > 0 else 0.0
        )

    @property
    def total_pnl(self) -> float:
        """
        Calculate total P&L (realized + unrealized).

        Returns:
            float: Sum of realized and standard unrealized P&L
        """
        return self.realized_pnl + self.unrealized_pnl

    # Helper methods for bulk updates
    def update_pnl(self, realized: float, unrealized: float) -> None:
        """
        Update both realized and unrealized P&L at once.

        Args:
            realized: New realized P&L value
            unrealized: New unrealized P&L value
        """
        self.realized_pnl = realized
        self.unrealized_pnl = unrealized
        self.update_derived_fields()

    def update_margin_info(self, margin_occupied: float, frozen: float) -> None:
        """
        Update margin and frozen amounts at once.

        Args:
            margin_occupied: New margin occupied value
            frozen: New frozen amount value
        """
        self.margin_occupied = margin_occupied
        self.frozen = frozen
        self.update_derived_fields()


@dataclass(slots=True)
class Position:
    """
    Represents a trading position with comprehensive price and P&L tracking.

    This class tracks position details including size, prices at different calculation
    bases (VWAP variants), and corresponding P&L metrics.

    Note: This class is designed to be compatible with Polars DataFrames while
    maintaining data integrity through explicit recalculation of derived fields.
    """

    # Core position identifiers
    symbol: str  # Instrument symbol

    # Position direction and size
    side: PositionSide  # Long or short direction
    size: float  # Total position size
    frozen: float  # Size that is frozen/locked (e.g., for pending orders)

    # Timestamp of when this snapshot was created/updated
    ttime: datetime = field(default_factory=_utc_now)  # Snapshot timestamp

    # Trading date derived from ttime
    tdate: date = field(init=False)  # Trading date derived from ttime

    # Fields with default values (must come after non-default fields)
    account_id: str = ""  # Account identifier

    # Price fields
    last_price: float = 0.0  # Most recent market price

    # VWAP fields (different calculation bases)
    vwap: float = 0.0  # Standard VWAP - Exchange standard position average price
    vwap_diluted: float = 0.0  # Diluted VWAP - Average price including fees/adjustments
    vwap_open: float = 0.0  # Open-based VWAP - Based on open prices only

    # P&L fields
    realized_pnl: float = 0.0  # Cumulative realized profit/loss from closed portions

    # Unrealized P&L fields (calculated from different VWAP bases)
    unrealized_pnl: float = 0.0  # P&L based on standard VWAP
    unrealized_pnl_diluted: float = 0.0  # P&L based on diluted VWAP
    unrealized_pnl_open: float = 0.0  # P&L based on open-price VWAP

    # Derived fields
    available: float = field(
        init=False, default=0.0
    )  # Size available for trading (size - frozen)

    def __post_init__(self) -> None:
        """Calculate derived fields after initialization."""
        # Derive tdate from ttime
        self.tdate = self.ttime.date()

        # Calculate position derived fields
        self.update_derived_fields()
        self.update_unrealized_pnl()

    def update_derived_fields(self) -> None:
        """
        Recalculate all derived fields based on current values.

        Call this method after modifying size or frozen values.
        """
        self.available = self.size - self.frozen

    def update_unrealized_pnl(self, multiplier: float = 1.0) -> None:
        """
        Update unrealized P&L values based on current prices and position.

        This recalculates all unrealized P&L metrics using the current last_price
        and the various VWAP values.

        Args:
            multiplier: Contract multiplier for calculating P&L (default: 1.0)
        """
        if self.size == 0 or self.last_price == 0:
            self.unrealized_pnl = 0.0
            self.unrealized_pnl_diluted = 0.0
            self.unrealized_pnl_open = 0.0
            return

        # Calculate P&L based on position direction
        if self.side == PositionSide.LONG:
            # For long positions: (current_price - avg_price) * size * multiplier
            self.unrealized_pnl = (self.last_price - self.vwap) * self.size * multiplier
            self.unrealized_pnl_diluted = (
                (self.last_price - self.vwap_diluted) * self.size * multiplier
            )
            self.unrealized_pnl_open = (
                (self.last_price - self.vwap_open) * self.size * multiplier
            )
        else:
            # For short positions: (avg_price - current_price) * size * multiplier
            self.unrealized_pnl = (self.vwap - self.last_price) * self.size * multiplier
            self.unrealized_pnl_diluted = (
                (self.vwap_diluted - self.last_price) * self.size * multiplier
            )
            self.unrealized_pnl_open = (
                (self.vwap_open - self.last_price) * self.size * multiplier
            )

    @property
    def total_pnl(self) -> float:
        """
        Calculate total P&L (realized + unrealized).

        Returns:
            float: Sum of realized and standard unrealized P&L
        """
        return self.realized_pnl + self.unrealized_pnl

    # Helper methods for bulk updates
    def update_size_info(self, size: float, frozen: float = 0.0) -> None:
        """
        Update size and frozen values at once.

        Args:
            size: New position size
            frozen: New frozen size (default: 0.0)
        """
        self.size = size
        self.frozen = frozen
        self.update_derived_fields()
        self.update_unrealized_pnl()

    def update_price_info(
        self, last_price: float, vwap: Optional[float] = None
    ) -> None:
        """
        Update price information and recalculate P&L.

        Args:
            last_price: New market price
            vwap: New VWAP (if None, keeps current value)
        """
        self.last_price = last_price
        if vwap is not None:
            self.vwap = vwap
        self.update_unrealized_pnl()


class SignalType(IntEnum):
    """
    Types of trading signals generated by strategies.

    Classifies signals based on their intended effect on positions.
    """

    UNKNOWN = 0  # Unknown or undefined signal type
    ENTRY = 1  # New position signal
    EXIT = 2  # Close position signal
    MODIFY = 3  # Adjust existing position signal


class SignalDirection(IntEnum):
    """
    Direction of trading signals.

    Specifies the market direction a signal is predicting or acting upon.
    """

    LONG = 1  # Long/bullish direction
    SHORT = 2  # Short/bearish direction
    FLAT = 3  # No direction/close all positions


@dataclass(slots=True)
class Signal:
    """
    Trading signal representation for strategy decisions.

    A Signal represents a trading decision with type, direction, and confidence metrics.
    Each signal must have a type (ENTRY/EXIT/MODIFY), direction (LONG/SHORT/FLAT),
    and scoring metrics (strength and confidence).

    Signal Types:
        1. ENTRY Signals - Open new positions
            * ENTRY+LONG: Open long position
            * ENTRY+SHORT: Open short position
            Example:
                ENTRY+LONG+score(strength=0.9, confidence=0.8)  # Strong buy signal
                ENTRY+SHORT+score(strength=0.5, confidence=0.7)  # Moderate sell signal

        2. EXIT Signals - Close existing positions
            * EXIT+LONG: Close long position
            * EXIT+SHORT: Close short position
            * EXIT+FLAT: Close all positions
            Example:
                EXIT+LONG+score(strength=0.9, confidence=0.8)   # Strong signal to exit long
                EXIT+SHORT+score(strength=0.5, confidence=0.7)  # Moderate signal to exit short
                EXIT+FLAT+score(strength=0.9, confidence=0.9)   # Strong signal to close all positions

        3. MODIFY Signals - Adjust existing positions
            * MODIFY+LONG: Increase/decrease long position
            * MODIFY+SHORT: Increase/decrease short position
            Example:
                MODIFY+LONG+score(strength=0.9, confidence=0.8)   # Increase long position
                MODIFY+SHORT+score(strength=-0.5, confidence=0.7) # Decrease short position

    Scoring Metrics:
        - strength: [0 to 1.0] Indicates signal strength
            * Magnitude indicates the strength of the signal
        - confidence: [0.0 to 1.0] Indicates confidence in the signal
            * 1.0 = Highest confidence
            * 0.0 = Lowest confidence

    Invalid Combinations:
        - ENTRY + FLAT: Invalid (cannot enter a flat position)
        - MODIFY + FLAT: Invalid (use EXIT + FLAT to close all positions)
    """

    # Core signal identifiers
    signal_id: UUID  # Unique identifier for this signal
    strategy_id: str  # Identifier for the strategy that generated the signal
    symbol: str  # Instrument the signal applies to

    # Signal classification
    type: SignalType  # Entry, exit, or modify
    direction: SignalDirection  # Long, short, or flat

    # Signal strength metrics
    strength: float  # Signal strength (0.0 to 1.0)
    confidence: float  # Confidence level (0.0 to 1.0)

    # Signal timing
    created_at: datetime  # When the signal was generated
    expire_at: Optional[datetime] = None  # When the signal expires

    # Price levels
    entry_price: Optional[Decimal] = None  # Suggested entry price
    target_price: Optional[Decimal] = None  # Target price for take profit
    stop_price: Optional[Decimal] = None  # Stop loss price

    # Position sizing
    size_pct: Optional[float] = None  # Position size as percentage of portfolio

    # Additional metadata
    metrics: Dict[str, float] | None = None  # Quantitative metrics for the signal
    tags: Dict[str, str] | None = None  # Qualitative tags for categorization

    def __post_init__(self) -> None:
        """Validate signal parameters after initialization."""
        if not (0 <= self.strength <= 1.0):
            raise ValueError("Strength must be between 0 and 1.0")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.type == SignalType.ENTRY and self.direction == SignalDirection.FLAT:
            raise ValueError("Cannot ENTRY with FLAT direction")
        if self.type == SignalType.MODIFY and self.direction == SignalDirection.FLAT:
            raise ValueError("Cannot MODIFY with FLAT direction")
        if self.size_pct is not None and not (0 <= self.size_pct <= 1.0):
            raise ValueError("Size percentage must be between 0 and 1.0")

    @property
    def score(self) -> float:
        """
        Combined score considering both strength and confidence.

        Returns:
            float: Product of strength and confidence (0.0 to 1.0)
        """
        return self.strength * self.confidence
