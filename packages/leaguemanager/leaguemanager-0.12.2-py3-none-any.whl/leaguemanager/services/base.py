from typing import Any

import attrs
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService as _SQLAlchemyAsyncRepositoryService
from advanced_alchemy.service import SQLAlchemySyncRepositoryService as _SQLAlchemySyncRepositoryService
from advanced_alchemy.service import is_dict_with_field, is_dict_without_field

from ._typing import ModelT


class SQLAlchemySyncRepositoryService(_SQLAlchemySyncRepositoryService):
    """AdvancedAlchemy introduced attrs out-of-the-box support with v1.5

    This class used to provide a `to_model` method for compatability with attrs defined Models.
    This will be removed in a future version.
    """


class SQLAlchemyAsyncRepositoryService(_SQLAlchemyAsyncRepositoryService):
    """AdvancedAlchemy introduced attrs out-of-the-box support with v1.5

    This class used to provide a `to_model` method for compatability with attrs defined Models.
    This will be removed in a future version.
    """

    ...
