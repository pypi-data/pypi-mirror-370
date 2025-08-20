import os
from dotenv import load_dotenv

load_dotenv()

# The MoMo API environment (sandbox or live)
ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")
BASE_API_URL = os.getenv("BASE_API_URL", "https://sandbox.momodeveloper.mtn.com/")
CALLBACK_HOST = os.getenv("CALLBACK_HOST")


PRODUCT_SUBSCRIPTION_KEY = os.getenv("PRODUCT_SUBSCRIPTION_KEY")
PRODUCT_API_USER_ID = os.getenv("PRODUCT_API_USER_ID")
PRODUCT_API_SECRET = os.getenv("PRODUCT_API_SECRET")


from .base import Base
from .collections.collection import Collection
from .remittances.remittance import Remittance
from .disbursements.disbursement import Disbursement
from .widgets.widget import Widget
from .sandbox.sandbox import Sandbox

__all__ = ['Base', 'Collection', 'Remittance', 'Disbursement', 'Widget', 'Sandbox']
