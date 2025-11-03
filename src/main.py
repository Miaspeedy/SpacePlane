from loguru import logger

if __name__ == '__main__':
    logger.trace("this is a trace message")
    logger.debug("this is a debug message")
    logger.info("this is an info message")
    logger.success("this is a success message") 
    logger.warning("this is a warning message")
    logger.error("this is an error message")
    logger.critical("this is a critical message")