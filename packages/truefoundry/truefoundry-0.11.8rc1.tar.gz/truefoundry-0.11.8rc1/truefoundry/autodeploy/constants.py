import os

DEBUG = os.getenv("AUTODEPLOY_DEBUG", "")

AUTODEPLOY_TFY_BASE_URL = os.getenv(
    "AUTODEPLOY_TFY_BASE_URL", "https://app.truefoundry.com"
).strip("/")
AUTODEPLOY_OPENAI_BASE_URL = os.environ.get("AUTODEPLOY_OPENAI_BASE_URL")
AUTODEPLOY_OPENAI_API_KEY = os.environ.get("AUTODEPLOY_OPENAI_API_KEY")
AUTODEPLOY_MODEL_NAME = os.environ.get(
    "AUTODEPLOY_MODEL_NAME", "auto-deploy-openai/gpt-4-turbo-2024-04-09"
)
ABOUT_AUTODEPLOY = """We'll use AI to build and deploy your project automatically.
Our AI Agent analyzes your codebase, checks for a Dockerfile, creates one if missing, builds a Docker image, fixes any issues, and runs the application to ensure we have built it correctly.
If you don't want to use our AI Agent to deploy automatically, create a [green]truefoundry.yaml[/] file in your project's root.
"""
# The maximum file size to read is set to 10KB.
# This limit is determined by the token limit of the LLM used, which is 128,000 tokens.
# Given that one token is approximately equivalent to 4 English characters,
# a 10KB file size limit (or ~10,000 characters |  ~2500 tokens) ensures that the file content,
# along with any additional context and instructions for the LLM, fits within the model's token limit.
MAX_FILE_SIZE_READ = 10 * 1024
