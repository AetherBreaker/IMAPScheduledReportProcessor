if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from asyncio.queues import Queue
from datetime import date
from logging import getLogger
from ssl import create_default_context

from environment_init_vars import FATAL_EVENT, SETTINGS
from err_handling import handle_fatal_exc_sync
from imap_tools import A, MailBox, MailMessage, MailMessageFlags

logger = getLogger(__name__)


STATIC_DATE_FILTER = date(2026, 4, 8)  # Only process emails from this date onward to avoid old backlog


@handle_fatal_exc_sync
def start_imap_email_monitoring(queue: Queue[MailMessage]) -> None:
  """Start the IMAP email monitoring. Runs in a separate thread"""
  # waiting for updates 60 sec, print unseen immediately if any update
  ssl_context = create_default_context()
  with MailBox(
    host=SETTINGS.watch_imap_server,
    port=SETTINGS.watch_imap_port,
    ssl_context=ssl_context,
  ).login(SETTINGS.watch_email, SETTINGS.watch_email_pwd, "INBOX") as mailbox:
    with mailbox.idle as idle:
      while True:
        responses = idle.poll(SETTINGS.watch_polling_timeout_sec)
        if FATAL_EVENT.is_set():
          break
        if responses:
          for msg in mailbox.fetch(
            A(
              seen=False,
              from_="emails@mailing.goftx.com",
              date_gte=STATIC_DATE_FILTER,
              # new=True,
            )
          ):
            if msg.uid is not None:
              mailbox.flag(msg.uid, MailMessageFlags.SEEN, True)
            queue.put_nowait(msg)
        else:
          logger.info(f"no updates in {SETTINGS.watch_polling_timeout_sec} sec")
