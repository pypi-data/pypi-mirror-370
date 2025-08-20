import os
import pathlib

from authorizenet.constants import constants

BASE_DIR = pathlib.Path(__file__).resolve().parent
DEBUG = True
SECRET_KEY = "xem*6no%8d9%^qzt2f3x3ar-uq4_+7h9myc$t0!+4%bj5us6f)"
USE_TZ = False
DEFAULT_FIELD_CLASS = "p-2 w-full bg-white dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300"
DEFAULT_TAX_RATE = "0.0825"

# Secrets
MERCHANT_AUTH_LOGIN_ID = os.getenv("MERCHANT_AUTH_LOGIN_ID")
MERCHANT_AUTH_TRANSACTION_KEY = os.getenv("MERCHANT_AUTH_TRANSACTION_KEY")
MERCHANT_AUTH_ENVIRONMENT = constants.SANDBOX
MERCHANT_AUTH_VALIDATION_MODE = "testMode"
WIALON_ADMIN_ID = os.getenv("WIALON_ADMIN_ID")
WIALON_TOKEN = os.getenv("WIALON_TOKEN")
