import uvicorn
from app.config.environment import get_settings
from app.app import init_app

# def _setup_logging(self):
#     self.logger = logging.getLogger(__name__)
#     self.logger.setLevel(logging.DEBUG)
#     if len(self.logger.handlers) == 0: # Prevent successive configuration for same logger instance
#         log_format = logging.Formatter('MAD <' + os.getenv('MAD_ENV','') + '> [%(levelname)s] - %(message)s')
#         handler = logging.handlers.SysLogHandler(address = '/dev/log', facility=logging.handlers.SysLogHandler.LOG_LOCAL0)
#         handler.setFormatter(log_format)
#         self.logger.addHandler(handler)

_SETTINGS = get_settings()


app = init_app(_SETTINGS)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)