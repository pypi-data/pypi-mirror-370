from typing import Any, Callable, Protocol

ViewFn = Callable[..., Any]


class SupportsCreateOverlayDecorator(Protocol):
    def create_overlay_decorator(
        self, overlay_type: str, overlay_key: str
    ) -> Callable[[str, Any], Callable[[ViewFn], ViewFn]]: ...


def create_drawer_decorator(
    rl: SupportsCreateOverlayDecorator,
) -> Callable[[str, Any], Callable[[ViewFn], ViewFn]]:
    return rl.create_overlay_decorator("drawer", "drawer")
