try:
    from enum import StrEnum  # type: ignore
except ImportError:
    from strenum import StrEnum

from clickpy.exception import ClickStrategyNotFound
from clickpy.strategy.strategy import (
    BasicClickStrategy,
    ClickStrategy,
    NaturalClickStrategy,
)


class StrategyEnum(StrEnum):  # type: ignore
    DEFAULT = "basic"
    NATURAL = "natural"


CLICK_STRAEGIES = {
    StrategyEnum.DEFAULT: BasicClickStrategy,
    StrategyEnum.NATURAL: NaturalClickStrategy,
}


def generate_click_strategy(click_type: str | None, **kwargs) -> ClickStrategy:
    if not click_type:
        raise TypeError(
            f"{type(generate_click_strategy).__name__}() is missing"
            " 1 requirement argument: click_type"
        )

    try:
        strat = CLICK_STRAEGIES[click_type]
        return strat(**kwargs)
    except KeyError:
        raise ClickStrategyNotFound()
