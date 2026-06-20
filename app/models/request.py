from typing import Literal

from pydantic import BaseModel, Field

TravelMode = Literal["walk", "bike"]
TrafficPeriod = Literal["normal", "morning_peak", "lunch_peak", "evening_peak"]
PathStrategy = Literal["distance", "time"]


class NavigationRequest(BaseModel):
    start: int = Field(..., ge=0, description="起点编号")
    end: int = Field(..., ge=0, description="终点编号")
    mode: TravelMode = Field(..., description="出行方式: walk 或 bike")
    period: TrafficPeriod = Field(..., description="当前时段")
    strategy: PathStrategy = Field("distance", description="路径策略: distance 或 time（可选，默认 distance）")
