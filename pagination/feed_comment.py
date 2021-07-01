from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FeedCommentPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "results": data,
                "num_pages": self.page.paginator.num_pages,
            }
        )
