from clickpy.exception import ClickStrategyNotFound
from clickpy.strategy._strategy import (
    BasicClickStrategy,
    ClickStrategy,
    NaturalClickStrategy,
)

DEFAULT_STRATEGY = "basic"
CLICK_STRAEGIES = {
    DEFAULT_STRATEGY: BasicClickStrategy,
    "natural": NaturalClickStrategy,
}


def generate_click_strategy(click_type: str, **kwargs) -> ClickStrategy:
    if click_type is None:
        raise TypeError(
            f"{type(generate_click_strategy).__name__}() is missing"
            " 1 requirement argument: click_type"
        )

    try:
        strat = CLICK_STRAEGIES[click_type]
        return strat(**kwargs)
    except KeyError:
        raise ClickStrategyNotFound()
