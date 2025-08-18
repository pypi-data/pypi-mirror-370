import logging

from agent_tools._info import APP_NAME

log = logging.getLogger(APP_NAME)

# Add a handler if none exists
if not log.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
