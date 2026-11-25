import logging
logging.basicConfig(level=logging.INFO, filename="app.log", encoding="utf-8", format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",)
logger = logging.getLogger(__name__)