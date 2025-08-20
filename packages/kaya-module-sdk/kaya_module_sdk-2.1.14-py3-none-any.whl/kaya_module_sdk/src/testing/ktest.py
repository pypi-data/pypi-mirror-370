from logging import Logger, getLogger

log: Logger = getLogger(__name__)


def setup_kit_framework(legacy: bool = False) -> type:
    if legacy:
        log.info("Initiating KIT(H) - legacy mode...")
        from kaya_module_sdk.src.testing.kit_harness import KIT
    else:
        log.info("Initiating KIT(C)...")
        from kaya_module_sdk.src.testing.kit_code import KIT  # type: ignore
    return KIT
