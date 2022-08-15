from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    OpenApiExample,
    inline_serializer,
)
from rest_framework.serializers import IntegerField


class CategoryApiDoc:
    @staticmethod
    def category_get_schema():
        params = [
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                required=False,
                description='카테고리 데이터를 10개씩 끊어서 가져올 때 페이지 번호입니다.',
            ),
        ]

        responses_200 = OpenApiResponse(
            description='page 파라미터가 없으면 모든 데이터를 가져오고, page 파라미터로 페이지를 지정하면 10개 단위로 끊어서 가져옵니다.',
            response=inline_serializer(
                name='test',
                fields={
                    'test': IntegerField()
                }
            )
        )

        return extend_schema(
            description='카테고리 데이터를 가져옵니다.',
            parameters=params,
            # responses={
            #     200: {
            #         'Test': OpenApiTypes.INT
            #     }
            # }
        )