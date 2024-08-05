from fastapi import APIRouter, Depends

router = APIRouter(
    prefix='/user',
    tags=['router for user']
)


async def after_request():
    pass


@router.get("/info")
def get_product_info(request: dict = Depends(after_request)):
    return {
        "name": "dylan zhang",
        "age": 18
    }
