DEFAULT_NUMBER_OF_ITEMS = 30
DEFAULT_PRINT_SIZE = 10
DEFAULT_MAX_SIZE = 100
INDEX_ORDERED = {"field": "index", "direction": "ASC"}
INDEX_ORDERED_DESC = {"field": "index", "direction": "DESC"}
PAGINATE_OUTPUT = """
            items {{
                {0}
            }}
            page {{
                index
                size
            }}
            total
"""


def get_page_input(index: int = 1, size: int = DEFAULT_NUMBER_OF_ITEMS) -> dict:
    return {"index": index, "size": size}
