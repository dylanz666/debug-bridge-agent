from fastapi import APIRouter

router = APIRouter(
    prefix='/product',
    tags=['router for product']
)


@router.get("/info")
def get_product_info():
    return {
        "name": "product 1",
        "stock": 100
    }
