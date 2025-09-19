from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, Field, computed_field, ConfigDict


class RewardRate(BaseModel):
    asset_address: str
    rewards_daily_rate: float


class Rewards(BaseModel):
    # Accept None, a single dict, or a list of dicts
    rates: Optional[Union[RewardRate, List[RewardRate]]] = None
    min_size: float = Field(0, alias="min_size")
    max_spread: float = Field(0, alias="max_spread")


class TokenQuote(BaseModel):
    token_id: str
    outcome: str
    price: Optional[float] = None  # some markets can have null price
    winner: Optional[bool] = None


class SimpleMarket(BaseModel):
    # Core identifiers/state
    condition_id: str
    active: bool
    closed: bool
    archived: bool
    accepting_orders: bool

    # Payload frequently present in “simplified” responses (all optional)
    enable_order_book: Optional[bool] = None
    accepting_order_timestamp: Optional[str] = None
    question_id: Optional[str] = None
    question: Optional[str] = None
    description: Optional[str] = None
    market_slug: Optional[str] = None
    end_date_iso: Optional[str] = None
    game_start_time: Optional[str] = None
    seconds_delay: Optional[int] = None
    fpmm: Optional[str] = None
    maker_base_fee: Optional[float] = None
    taker_base_fee: Optional[float] = None
    notifications_enabled: Optional[bool] = None
    neg_risk: Optional[bool] = None
    neg_risk_market_id: Optional[str] = None
    neg_risk_request_id: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    is_50_50_outcome: Optional[bool] = None
    tags: Optional[List[str]] = None
    minimum_order_size: Optional[float] = None
    minimum_tick_size: Optional[float] = None
    liquidity: Optional[float] = 10000.0

    rewards: Rewards
    tokens: List[TokenQuote]

    # Pydantic config: ignore unknown keys, allow aliases
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    # ---- Convenience computed fields to keep old call sites happy ----
    @computed_field
    @property
    def outcomes(self) -> List[str]:
        return [t.outcome for t in self.tokens]

    @computed_field
    @property
    def outcome_prices(self) -> List[float]:
        # Coerce None to 0.0 for stability
        return [float(t.price) if t.price is not None else 0.0 for t in self.tokens]

    @computed_field
    @property
    def clob_token_ids(self) -> List[str]:
        return [t.token_id for t in self.tokens]

    @computed_field
    @property
    def rewardsMinSize(self) -> float:
        return self.rewards.min_size

    @computed_field
    @property
    def rewardsMaxSpread(self) -> float:
        return self.rewards.max_spread

    @computed_field
    @property
    def id(self) -> str:
        return self.condition_id


class ClobReward(BaseModel):
    id: str  # returned as string in api but really an int?
    conditionId: str
    assetAddress: str
    rewardsAmount: float  # only seen 0 but could be float?
    rewardsDailyRate: int  # only seen ints but could be float?
    startDate: str  # yyyy-mm-dd formatted date string
    endDate: str  # yyyy-mm-dd formatted date string


class Tag(BaseModel):
    id: str
    label: Optional[str] = None
    slug: Optional[str] = None
    forceShow: Optional[bool] = None  # missing from current events data
    createdAt: Optional[str] = None  # missing from events data
    updatedAt: Optional[str] = None  # missing from current events data
    _sync: Optional[bool] = None


class PolymarketEvent(BaseModel):
    id: str  # "11421"
    ticker: Optional[str] = None
    slug: Optional[str] = None
    title: Optional[str] = None
    startDate: Optional[str] = None
    creationDate: Optional[str] = (
        None  # fine in market event but missing from events response
    )
    endDate: Optional[str] = None
    image: Optional[str] = None
    icon: Optional[str] = None
    active: Optional[bool] = None
    closed: Optional[bool] = None
    archived: Optional[bool] = None
    new: Optional[bool] = None
    featured: Optional[bool] = None
    restricted: Optional[bool] = None
    liquidity: Optional[float] = None
    volume: Optional[float] = None
    reviewStatus: Optional[str] = None
    createdAt: Optional[str] = None  # 2024-07-08T01:06:23.982796Z,
    updatedAt: Optional[str] = None  # 2024-07-15T17:12:48.601056Z,
    competitive: Optional[float] = None
    volume24hr: Optional[float] = None
    enableOrderBook: Optional[bool] = None
    liquidityClob: Optional[float] = None
    _sync: Optional[bool] = None
    commentCount: Optional[int] = None
    # markets: list[str, 'Market'] # forward reference Market defined below - TODO: double check this works as intended
    markets: Optional[list[Market]] = None
    tags: Optional[list[Tag]] = None
    cyom: Optional[bool] = None
    showAllOutcomes: Optional[bool] = None
    showMarketImages: Optional[bool] = None


class Market(BaseModel):
    id: int
    question: Optional[str] = None
    conditionId: Optional[str] = None
    slug: Optional[str] = None
    resolutionSource: Optional[str] = None
    endDate: Optional[str] = None
    liquidity: Optional[float] = None
    startDate: Optional[str] = None
    image: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    outcome: Optional[list] = None
    outcomePrices: Optional[list] = None
    volume: Optional[float] = None
    active: Optional[bool] = None
    closed: Optional[bool] = None
    marketMakerAddress: Optional[str] = None
    createdAt: Optional[str] = None  # date type worth enforcing for dates?
    updatedAt: Optional[str] = None
    new: Optional[bool] = None
    featured: Optional[bool] = None
    submitted_by: Optional[str] = None
    archived: Optional[bool] = None
    resolvedBy: Optional[str] = None
    restricted: Optional[bool] = None
    groupItemTitle: Optional[str] = None
    groupItemThreshold: Optional[int] = None
    questionID: Optional[str] = None
    enableOrderBook: Optional[bool] = None
    orderPriceMinTickSize: Optional[float] = None
    orderMinSize: Optional[int] = None
    volumeNum: Optional[float] = None
    liquidityNum: Optional[float] = None
    endDateIso: Optional[str] = None  # iso format date = None
    startDateIso: Optional[str] = None
    hasReviewedDates: Optional[bool] = None
    volume24hr: Optional[float] = None
    clobTokenIds: Optional[list] = None
    umaBond: Optional[int] = None  # returned as string from api?
    umaReward: Optional[int] = None  # returned as string from api?
    volume24hrClob: Optional[float] = None
    volumeClob: Optional[float] = None
    liquidityClob: Optional[float] = None
    acceptingOrders: Optional[bool] = None
    negRisk: Optional[bool] = None
    commentCount: Optional[int] = None
    _sync: Optional[bool] = None
    events: Optional[list[PolymarketEvent]] = None
    ready: Optional[bool] = None
    deployed: Optional[bool] = None
    funded: Optional[bool] = None
    deployedTimestamp: Optional[str] = None  # utc z datetime string
    acceptingOrdersTimestamp: Optional[str] = None  # utc z datetime string,
    cyom: Optional[bool] = None
    competitive: Optional[float] = None
    pagerDutyNotificationEnabled: Optional[bool] = None
    reviewStatus: Optional[str] = None  # deployed, draft, etc.
    approved: Optional[bool] = None
    clobRewards: Optional[list[ClobReward]] = None
    rewardsMinSize: Optional[int] = (
        None  # would make sense to allow float but we'll see
    )
    rewardsMaxSpread: Optional[float] = None
    spread: Optional[float] = None


class ComplexMarket(BaseModel):
    id: int
    condition_id: str
    question_id: str
    tokens: Union[str, str]
    rewards: str
    minimum_order_size: str
    minimum_tick_size: str
    description: str
    category: str
    end_date_iso: str
    game_start_time: str
    question: str
    market_slug: str
    min_incentive_size: str
    max_incentive_spread: str
    active: bool
    closed: bool
    seconds_delay: int
    icon: str
    fpmm: str
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


class SimpleEvent(BaseModel):
    id: int
    ticker: str
    slug: str
    title: str
    description: str
    end: str
    active: bool
    closed: bool
    archived: bool
    restricted: bool
    new: bool
    featured: bool
    restricted: bool
    markets: str


class Source(BaseModel):
    id: Optional[str]
    name: Optional[str]


class Article(BaseModel):
    source: Optional[Source]
    author: Optional[str]
    title: Optional[str]
    description: Optional[str]
    url: Optional[str]
    urlToImage: Optional[str]
    publishedAt: Optional[str]
    content: Optional[str]


class MarketRagHit(BaseModel):
    condition_id: str
    question: Optional[str] = None
    end: Optional[str] = None
    active: Optional[bool] = None
    closed: Optional[bool] = None
    archived: Optional[bool] = None
    clob_token_ids: Optional[List[str]] = None
    score: float  # NOTE: in Chroma, lower distance is more similar
