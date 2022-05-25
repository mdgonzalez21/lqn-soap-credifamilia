import os
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.getenv("APP_ENV", default="DEV")

if ENV == "PRD":
    WSDL = "lib/wsdl/credifamilia-prd.wsdl"
else:
    WSDL = "lib/wsdl/credifamilia-dev.wsdl"

UNDEFINED_ERROR = "Error indefinido."


sentry_sdk.init(
    dsn="https://82569d4f1ab94d708d8d51bb89b99618@o412045.ingest.sentry.io/5288222",
    integrations=[AwsLambdaIntegration()],
    traces_sample_rate=1.0,  # adjust the sample rate in production as needed
    environment=ENV,
)
