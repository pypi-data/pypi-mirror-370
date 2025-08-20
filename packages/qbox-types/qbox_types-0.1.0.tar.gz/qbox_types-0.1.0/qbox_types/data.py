from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import IntEnum
from typing import List, Optional, TYPE_CHECKING, Union


class Exchange(IntEnum):
    """
    Trading exchanges and venues.

    Represents the major exchanges where financial instruments are traded,
    including stock exchanges and futures/commodities exchanges in China.
    """

    # Stock exchanges
    SHSE = 1  # Shanghai Stock Exchange (上海证券交易所)
    SZSE = 2  # Shenzhen Stock Exchange (深圳证券交易所)

    # Futures and derivatives exchanges
    CFFEX = 11  # China Financial Futures Exchange (中国金融期货交易所/中金所)
    SHFE = 12  # Shanghai Futures Exchange (上海期货交易所/上期所)
    DCE = 13  # Dalian Commodity Exchange (大连商品交易所/大商所)
    CZCE = 14  # Zhengzhou Commodity Exchange (郑州商品交易所/郑商所)
    INE = 15  # Shanghai International Energy Exchange (上海国际能源交易中心)
    GFEX = 16  # Guangzhou Futures Exchange (广州期货交易所/广期所)

    # Other exchanges
    HKEX = 21  # Hong Kong Exchanges and Clearing (香港交易所)
    SGX = 31  # Singapore Exchange (新加坡交易所)

    @classmethod
    def is_stock_exchange(cls, exchange: Exchange) -> bool:
        """Check if the exchange is a stock exchange."""
        return exchange in (cls.SHSE, cls.SZSE, cls.HKEX)

    @classmethod
    def is_futures_exchange(cls, exchange: Exchange) -> bool:
        """Check if the exchange is a futures exchange."""
        return exchange in (cls.CFFEX, cls.SHFE, cls.DCE, cls.CZCE, cls.INE, cls.GFEX)

    @classmethod
    def is_china_exchange(cls, exchange: Exchange) -> bool:
        """Check if the exchange is located in mainland China."""
        return exchange in (
            cls.SHSE,
            cls.SZSE,
            cls.CFFEX,
            cls.SHFE,
            cls.DCE,
            cls.CZCE,
            cls.INE,
            cls.GFEX,
        )

    @classmethod
    def get_exchange_code(cls, exchange: Exchange) -> str:
        """
        Get the standard code for an exchange.

        Returns:
            str: The standard exchange code (e.g., 'SHSE', 'SZSE')
        """
        return exchange.name

    @classmethod
    def from_code(cls, code: str) -> Exchange:
        """
        Get an exchange enum value from its code.

        Args:
            code: The exchange code (e.g., 'SHSE', 'SZSE')

        Returns:
            The corresponding Exchange enum value

        Raises:
            ValueError: If the code doesn't match any exchange
        """
        try:
            return cls[code.upper()]
        except KeyError:
            raise ValueError(f"Unknown exchange code: {code}")


class AssetType(IntEnum):
    """
    Comprehensive classification of financial instrument types.

    Provides a unified taxonomy of tradable assets with hierarchical organization:
    - Major categories: 1000-level codes (e.g., 1010 for stocks)
    - Specific subtypes: 6-digit codes (e.g., 101001 for A-shares)
    - Detailed subtypes: 8-digit codes (e.g., 10100101 for main board A-shares)

    This enum provides a complete hierarchical classification system for all
    tradable financial instruments.
    """

    # === STOCKS (1010) ===
    STOCK = 1010  # General stock category
    STOCK_A = 101001  # A-shares (A股)
    STOCK_A_MAIN = 10100101  # Main board A-shares (主板A股)
    STOCK_A_GEM = 10100102  # Growth Enterprise Market (创业板)
    STOCK_A_STAR = 10100103  # Science and Technology Innovation Board (科创版)
    STOCK_A_BSE = 10100104  # Beijing Stock Exchange (北交所股票)
    STOCK_B = 101002  # B-shares (B股)
    STOCK_DR = 101003  # Depositary receipts (存托凭证)

    # === FUNDS (1020) ===
    FUND = 1020  # General fund category
    FUND_ETF = 102001  # Exchange Traded Funds (ETF)
    FUND_ETF_STOCK = 10200101  # Stock ETF (股票ETF)
    FUND_ETF_BOND = 10200102  # Bond ETF (债券ETF)
    FUND_ETF_COMMODITY = 10200103  # Commodity ETF (商品ETF)
    FUND_ETF_CROSS_BORDER = 10200104  # Cross-border ETF (跨境ETF)
    FUND_ETF_MONEY_MARKET = 10200105  # Money market ETF (货币ETF)
    FUND_LOF = 102002  # Listed Open-Ended Funds (LOF)
    FUND_FOF = 102005  # Fund of Funds (FOF)

    # === BONDS (1030) ===
    BOND = 1030  # General bond category
    BOND_CONVERTIBLE = 103001  # Convertible bonds (可转债)
    BOND_CONVERTIBLE_ORDINARY = 10300101  # Ordinary convertible bonds (普通可转债)
    BOND_CONVERTIBLE_EXCHANGEABLE = 10300102  # Exchangeable bonds (可交换债券)
    BOND_CONVERTIBLE_DETACHABLE = (
        10300103  # Detachable convertible bonds (可分离式债券)
    )
    BOND_CONVERTIBLE_PRIVATE = (
        10300104  # Private placement convertible bonds (定向可转债)
    )
    BOND_TREASURY = 103003  # Government bonds (国债)
    BOND_CORPORATE = 103006  # Corporate bonds (企业债)
    BOND_REPO = 103008  # Repurchase agreements (回购)

    # === FUTURES (1040) ===
    FUTURES = 1040  # General futures category
    FUTURES_INDEX = 104001  # Index futures (股指期货)
    FUTURES_COMMODITY = 104003  # Commodity futures (商品期货)
    FUTURES_BOND = 104006  # Bond futures (国债期货)

    # === OPTIONS (1050) ===
    OPTION = 1050  # General option category
    OPTION_STOCK = 105001  # Stock options (股票期权)
    OPTION_INDEX = 105002  # Index options (指数期权)
    OPTION_COMMODITY = 105003  # Commodity options (商品期权)

    # === INDICES (1060) ===
    INDEX = 1060  # General index category
    INDEX_STOCK = 106001  # Stock indices (股票指数)
    INDEX_FUND = 106002  # Fund indices (基金指数)
    INDEX_BOND = 106003  # Bond indices (债券指数)
    INDEX_FUTURES = 106004  # Futures indices (期货指数)

    # === SECTORS (1070) ===
    SECTOR = 1070  # General sector category
    SECTOR_CONCEPT = 107001  # Concept sectors (概念板块)

    # === OTHER CATEGORIES ===
    FOREX = 1080  # Foreign exchange
    CRYPTO = 1090  # Cryptocurrencies

    @classmethod
    def is_stock(cls, asset_type: AssetType) -> bool:
        """
        Check if the asset type is a stock or stock subtype.
        """
        return (
            asset_type == cls.STOCK
            or 101001 <= asset_type.value <= 101999
            or 10100101 <= asset_type.value <= 10199999
        )

    @classmethod
    def is_fund(cls, asset_type: AssetType) -> bool:
        """
        Check if the asset type is a fund or fund subtype.
        """
        return (
            asset_type == cls.FUND
            or 102001 <= asset_type.value <= 102999
            or 10200101 <= asset_type.value <= 10299999
        )

    @classmethod
    def is_bond(cls, asset_type: AssetType) -> bool:
        """Check if the asset type is a bond or bond subtype."""
        return (
            asset_type == cls.BOND
            or 103001 <= asset_type.value <= 103999
            or 10300101 <= asset_type.value <= 10399999
        )

    @classmethod
    def is_futures(cls, asset_type: AssetType) -> bool:
        """Check if the asset type is a futures contract or futures subtype."""
        return (
            asset_type == cls.FUTURES
            or 104001 <= asset_type.value <= 104999
            or 10400101 <= asset_type.value <= 10499999
        )

    @classmethod
    def is_option(cls, asset_type: AssetType) -> bool:
        """Check if the asset type is an option or option subtype."""
        return (
            asset_type == cls.OPTION
            or 105001 <= asset_type.value <= 105999
            or 10500101 <= asset_type.value <= 10599999
        )

    @classmethod
    def is_index(cls, asset_type: AssetType) -> bool:
        """Check if the asset type is an index or index subtype."""
        return (
            asset_type == cls.INDEX
            or 106001 <= asset_type.value <= 106999
            or 10600101 <= asset_type.value <= 10699999
        )

    @classmethod
    def is_sector(cls, asset_type: AssetType) -> bool:
        """Check if the asset type is a sector or sector subtype."""
        return (
            asset_type == cls.SECTOR
            or 107001 <= asset_type.value <= 107999
            or 10700101 <= asset_type.value <= 10799999
        )

    @classmethod
    def get_major_type(cls, asset_type: AssetType) -> AssetType:
        """
        Get the major category for a specific asset subtype.

        Args:
            asset_type: The specific asset type

        Returns:
            The corresponding major category

        Example:
            AssetType.get_major_type(AssetType.STOCK_A) -> AssetType.STOCK
            AssetType.get_major_type(AssetType.STOCK_A_MAIN) -> AssetType.STOCK
        """
        if asset_type.value < 100000:  # Already a major type
            return asset_type

        if asset_type.value < 10000000:  # 6-digit code (specific subtype)
            # Extract the major type code (first 4 digits)
            major_code = (asset_type.value // 100) * 10
        else:  # 8-digit code (detailed subtype)
            # Extract the major type code (first 4 digits)
            major_code = (asset_type.value // 10000) * 10

        try:
            return cls(major_code)
        except ValueError:
            raise ValueError(f"Could not determine major type for {asset_type}")

    @classmethod
    def get_specific_type(cls, asset_type: AssetType) -> AssetType:
        """
        Get the specific subtype for a detailed asset type.

        For 8-digit codes, returns the corresponding 6-digit parent category.
        For 6-digit codes or major types, returns the asset_type unchanged.

        Args:
            asset_type: The detailed asset type

        Returns:
            The corresponding specific subtype or the same type if already specific

        Example:
            AssetType.get_specific_type(AssetType.STOCK_A_MAIN) -> AssetType.STOCK_A
        """
        if asset_type.value < 10000000:  # Already a major or specific type
            return asset_type

        # Extract the specific type code (first 6 digits)
        specific_code = asset_type.value // 100 * 100 + asset_type.value % 100

        try:
            return cls(specific_code)
        except ValueError:
            # If the specific code doesn't exist, return the major type
            return cls.get_major_type(asset_type)


@dataclass(slots=True)
class Bar:
    """
    Bar data for financial instruments.

    Represents OHLCV (Open, High, Low, Close, Volume) data and additional metrics
    for a specific instrument at one-minute intervals. Contains price, volume, and
    turnover information for a single time period in the market.
    """

    symbol: str  # Instrument symbol
    tdate: date  # Trading date
    ttime: datetime  # Bar timestamp (includes date and time)
    open: float  # Opening price
    high: float  # Highest price
    low: float  # Lowest price
    close: float  # Closing price
    volume: int  # Trading volume
    turnover: float  # Trading turnover (total value traded)
    open_interest: int = 0  # Open interest (for derivatives)


@dataclass(slots=True)
class Tick:
    """
    Market tick data for financial instruments.

    Represents the most granular market data including price, volume,
    and order book information at each tick (individual market update).
    Provides a complete snapshot of market conditions at a specific moment,
    including both trade data and the current state of the order book.
    """

    symbol: str  # Instrument symbol
    tdate: date  # Trading date
    ttime: datetime  # Tick timestamp

    # Price data
    open: float  # Opening price
    high: float  # Highest price
    low: float  # Lowest price

    # Volume and Turnover data
    volume: int  # Trading volume
    turnover: float  # Trading turnover (total value traded)

    # --- Fields with default values --- #

    # Last trade specific data
    last_price: float = 0  # Last traded price
    last_volume: int = 0  # Volume of the last trade
    last_turnover: float = 0.0  # Turnover of the last trade

    # Other specific data
    # Trade type (futures)
    # 1: Both Open, 2: Both Close, 3: Long Open, 4: Short Open,
    # 5: Short Close, 6: Long Close, 7: Long Change, 8: Short Change
    trade_type: int = 0
    open_interest: int = 0  # Open interest (for derivatives)
    iopv: float = 0.0  # Indicative Optimized Portfolio Value (基金份额参考净值)

    # Order book data
    ask_p: List[float] = field(default_factory=list)  # Ask prices (array)
    ask_v: List[int] = field(default_factory=list)  # Ask volumes (array)
    bid_p: List[float] = field(default_factory=list)  # Bid prices (array)
    bid_v: List[int] = field(default_factory=list)  # Bid volumes (array)


@dataclass(slots=True)
class Trade:
    """
    Individual trade data for financial instruments.

    Represents each executed trade with price and volume information.
    Captures the details of a single transaction in the market, including
    the exact time, price, and size of the trade.
    """

    symbol: str  # Instrument symbol
    tdate: date  # Trading date
    ttime: datetime  # Trade timestamp
    price: float  # Trade price
    volume: int  # Trade volume
    turnover: float  # Trading turnover (total value traded)


@dataclass(slots=True)
class StkInstrumentExt:
    """
    Stock exchange instrument information for securities exchanges (SHSE, SZSE).

    Covers stocks, bonds, funds, ETFs and other securities traded on
    stock exchanges. Maps directly to STK_EXCH_CN business domain.
    """

    # === CORE IDENTIFIERS ===
    symbol: str  # Instrument symbol
    tdate: date  # Trading date
    asset_type: AssetType  # Asset type classification
    exchange: Exchange  # Exchange where traded (SHSE, SZSE)

    # === REFERENCE DATA ===
    asset_id: str  # Asset identifier
    asset_name: str  # Human-readable name

    # === TRADING PARAMETERS ===
    price_tick: float  # Minimum price movement
    upper_limit: float  # Daily upper price limit
    lower_limit: float  # Daily lower price limit
    trade_n: int  # Settlement period (T+0, T+1, etc.)
    is_st: bool  # Special treatment status (ST/ST*)
    is_suspended: bool  # Trading suspension status
    adj_factor: float  # Adjustment factor for corporate actions

    # === DAILY STATISTICS ===
    open: float  # Opening price
    high: float  # Highest price
    low: float  # Lowest price
    close: float  # Closing price
    volume: int  # Trading volume
    turnover: float  # Trading turnover value
    turnrate: float  # Turnover rate
    circ_mv: float  # Circulating market value
    prev_close: float  # Previous day closing price

    # === FUND-SPECIFIC DATA ===
    iopv: float = 0.0  # Indicative Optimized Portfolio Value (for ETFs/funds)

    # === LIFECYCLE INFORMATION ===
    listed_date: Optional[datetime] = None  # Initial listing date
    delisted_date: Optional[datetime] = None  # Delisting date (if applicable)


@dataclass(slots=True)
class FutInstrumentExt:
    """
    Futures exchange instrument information for futures exchanges (CFFEX, SHFE, DCE, CZCE, INE, GFEX).

    Covers futures contracts and options on futures. Maps directly to FUT_EXCH_CN business domain.
    """

    # === CORE IDENTIFIERS ===
    symbol: str  # Instrument symbol
    tdate: date  # Trading date
    asset_type: AssetType  # Asset type classification
    exchange: Exchange  # Exchange where traded (futures exchanges)

    # === REFERENCE DATA ===
    product_id: str  # Product identifier
    asset_id: str  # Asset identifier
    asset_name: str  # Human-readable name

    # === CONTRACT SPECIFICATIONS ===
    price_tick: float  # Minimum price movement
    multiplier: int  # Contract size multiplier
    margin_ratio: float  # Initial margin ratio when opening positions
    maint_margin_ratio: float  # Maintenance margin ratio during holding (usually lower)
    upper_limit: float  # Daily upper price limit
    lower_limit: float  # Daily lower price limit
    is_suspended: bool  # Trading suspension status

    # === DAILY STATISTICS ===
    open: float  # Opening price
    high: float  # Highest price
    low: float  # Lowest price
    close: float  # Closing price
    volume: int  # Trading volume
    turnover: float  # Trading turnover value
    prev_close: float  # Previous day closing price
    settle_price: float  # Daily settlement price
    prev_settle: float  # Previous settlement price
    open_interest: int  # Total open interest

    # === MARKET RANKING ===
    rank_volume: int  # Volume ranking among contracts
    rank_open_interest: int  # Open interest ranking
    rank_active: int  # Activity/liquidity ranking

    # === PRODUCT STATISTICS ===
    prd_volume: int  # Total product family volume
    prd_open_interest: int  # Total product family open interest

    # === LIFECYCLE INFORMATION ===
    listed_date: Optional[datetime] = None  # Initial listing date
    delisted_date: Optional[datetime] = None  # Delisting date (if applicable)


@dataclass(slots=True)
class OptInstrumentExt:
    """
    Options instrument information for both stock and futures exchanges.

    Covers stock options (SHSE, SZSE), index options, and commodity options (futures exchanges).
    Options have unique characteristics regardless of which exchange they trade on.
    """

    # === CORE IDENTIFIERS ===
    symbol: str  # Option symbol
    tdate: date  # Trading date
    asset_type: AssetType  # Asset type classification (OPTION_STOCK, OPTION_INDEX, OPTION_COMMODITY)
    exchange: Exchange  # Exchange where traded (can be stock or futures exchange)

    # === REFERENCE DATA ===
    asset_id: str  # Asset identifier
    asset_name: str  # Human-readable name
    underlying_symbol: str  # Underlying asset symbol (always required for options)

    # === OPTION SPECIFICATIONS ===
    strike_price: float  # Option strike/exercise price
    expiry_date: date  # Option expiration date
    option_type: str  # Call ("C") or Put ("P")
    multiplier: int  # Contract size (e.g., 10000 for stock options)
    exercise_style: str  # "European" or "American"

    # === TRADING PARAMETERS ===
    price_tick: float  # Minimum price movement
    upper_limit: float  # Daily upper price limit
    lower_limit: float  # Daily lower price limit
    is_suspended: bool  # Trading suspension status
    margin_ratio: float  # Initial margin ratio (applies to sellers, buyers usually pay premium only)
    maint_margin_ratio: float  # Maintenance margin ratio (usually lower than initial)

    # === DAILY STATISTICS ===
    open: float  # Opening price
    high: float  # Highest price
    low: float  # Lowest price
    close: float  # Closing price
    volume: int  # Trading volume
    turnover: float  # Trading turnover value
    prev_close: float  # Previous day closing price
    open_interest: int  # Total open interest (options have this like futures)

    # === OPTION-SPECIFIC METRICS ===
    intrinsic_value: (
        float  # Intrinsic value (max(0, S-K) for calls, max(0, K-S) for puts)
    )
    time_value: float  # Time value (option price - intrinsic value)

    # === OPTIONAL GREEKS (may not always be available) ===
    delta: float = 0.0  # Price sensitivity to underlying
    gamma: float = 0.0  # Delta sensitivity to underlying
    theta: float = 0.0  # Time decay
    vega: float = 0.0  # Volatility sensitivity
    rho: float = 0.0  # Interest rate sensitivity

    # === LIFECYCLE INFORMATION ===
    listed_date: Optional[datetime] = None  # Initial listing date
    delisted_date: Optional[datetime] = None  # Delisting date (if applicable)


# Legacy alias for backward compatibility - will point to StkInstrumentExt for now
# TODO: Remove after migration is complete
InstrumentExt = StkInstrumentExt


@dataclass(slots=True)
class MarketDividend:
    """
    Represents a dividend distribution event at the market/company level.

    This class describes the dividend policy of a security, such as cash dividend per share
    and stock dividend ratio. It is a "global" event, independent of any specific account.

    Note: This is different from ledger.Dividend, which represents the actual dividend
    transaction received by a specific account.
    """

    # Core dividend information
    symbol: str  # Security that issued the dividend
    cash_ratio: float  # Cash dividend per share/unit
    share_ratio: float  # Share dividend ratio (e.g., 0.1 for 1:10 stock dividend)

    # Dates
    ex_date: date  # Ex-dividend date
    payment_date: date  # Payment date when dividend was actually received
