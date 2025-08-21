try:
    # pydantic >1.10.18
    from pydantic.v1 import *  # noqa: F403
    from pydantic.v1 import ConstrainedStr, utils  # noqa: F401
except ImportError:
    # pydantic <=1.10.17
    from pydantic import *  # noqa: F403
    from pydantic import ConstrainedStr, utils  # noqa: F401


class NonEmptyStr(ConstrainedStr):
    min_length: int = 1
