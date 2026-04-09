if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from asyncio import create_task, sleep
from asyncio.queues import Queue
from asyncio.tasks import Task
from ftplib import FTP
from logging import getLogger
from typing import NoReturn, Protocol, Self

from environment_init_vars import CWD
from err_handling import handle_fatal_exc_async
from imap_tools import MailMessage

logger = getLogger(__name__)


ATTACHMENT_DEPOT = CWD / "attachments_dl"
ATTACHMENT_DEPOT.mkdir(exist_ok=True)


class FTPProtocol(Protocol):
  def __init__(self, creds: dict) -> None: ...
  def __enter__(self) -> Self: ...
  def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...


class SFTFTPClient(FTP, FTPProtocol):
  def __init__(self, creds: dict) -> None:
    self.creds = creds
    super().__init__()

  def __enter__(self) -> Self:
    self.connect(host=self.creds["HOST"], port=self.creds["PORT"])
    self.login(user=self.creds["USER"], passwd=self.creds["PWD"])
    return self


@handle_fatal_exc_async
async def direct_email_processing(queue: Queue[MailMessage], processing_tasks: list[Task]) -> NoReturn:
  """Continuously check for new emails and process them."""
  while True:
    email_data = await queue.get()
    # try:
    tmp = create_task(process_email(email_data))
    await process_email(email_data)


async def process_email(email_data: MailMessage) -> None:
  """Process a single email message."""
  # Placeholder for actual email processing logic
  logger.info(f"Processing email with subject: {email_data.subject}")
  # Simulate processing time
  await sleep(1)
