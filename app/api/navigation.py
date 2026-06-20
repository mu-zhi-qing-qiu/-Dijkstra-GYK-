from fastapi import APIRouter, HTTPException, status

from app.data.campus_data import build_campus_graph, list_places
from app.models.request import NavigationRequest
from app.models.response import NavigationResponse, PlaceInfo
from app.services.navigation_service import NavigationService

router = APIRouter(prefix="/api", tags=["navigation"])
_navigation_service = NavigationService(build_campus_graph())


@router.get("/places", response_model=list[PlaceInfo])
def get_places() -> list[PlaceInfo]:
    """返回全部校园地点，供前端选择起终点。"""
    return [PlaceInfo(**place) for place in list_places()]


@router.post("/navigation", response_model=NavigationResponse)
def navigate(request: NavigationRequest) -> NavigationResponse:
    try:
        return _navigation_service.navigate(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/navigation/floyd", response_model=NavigationResponse)
def navigate_by_floyd(request: NavigationRequest) -> NavigationResponse:
    try:
        return _navigation_service.navigate_by_floyd(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
