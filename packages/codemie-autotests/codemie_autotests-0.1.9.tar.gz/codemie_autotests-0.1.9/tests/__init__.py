import os
import random
import string
from pathlib import Path

from dotenv import load_dotenv

from tests.utils.aws_parameters_store import AwsParameterStore

load_dotenv()

if os.getenv("AWS_ACCESS_KEY") and os.getenv("AWS_SECRET_KEY"):
    aws_parameters_store = AwsParameterStore.get_instance(
        access_key=os.getenv("AWS_ACCESS_KEY"),
        secret_key=os.getenv("AWS_SECRET_KEY"),
        session_token=os.getenv("AWS_SESSION_TOKEN", ""),
    )

    dotenv = aws_parameters_store.get_parameter(
        f"/codemie/autotests/dotenv/{os.getenv('ENV')}"
    )

    with open(Path(__file__).parent.parent / ".env", "w") as file:
        file.write(dotenv)

    load_dotenv()

LANGFUSE_TRACES_ENABLED = (
    os.getenv("LANGFUSE_TRACES_ENABLED", "false").lower() == "true"
)

PROJECT = os.getenv("PROJECT_NAME", "codemie")
TEST_USER = os.getenv("TEST_USER_FULL_NAME", "Test User")

autotest_entity_prefix = (
    f"{''.join(random.choice(string.ascii_lowercase) for _ in range(3))}_"
)
