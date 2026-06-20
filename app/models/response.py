from pydantic import BaseModel, Field


class NavigationResponse(BaseModel):
    path: list[int] = Field(..., description="推荐路径编号")
    path_names: list[str] = Field(..., description="推荐路径地点名称")
    distance: float = Field(..., description="总距离，单位米")
    time: float = Field(..., description="预计耗时，单位秒")


class PlaceInfo(BaseModel):
    id: int = Field(..., description="地点编号")
    name: str = Field(..., description="地点名称")
    code: str = Field(..., description="地点代码")
