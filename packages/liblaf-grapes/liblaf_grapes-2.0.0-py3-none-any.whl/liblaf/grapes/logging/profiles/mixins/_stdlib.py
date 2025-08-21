import logging


class MixinStdlib:
    def clear_stdlib_handlers(self) -> None:
        for logger in logging.root.manager.loggerDict.values():
            if isinstance(logger, logging.PlaceHolder):
                continue
            logger.handlers.clear()
            logger.propagate = True
