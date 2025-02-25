# IMPORTATION STANDARD
from copy import deepcopy
from threading import Thread
from queue import SimpleQueue
from pathlib import Path

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.log.collection.s3_sender import send_to_s3
from gamestonk_terminal.log.generation.settings import AppSettings

# DO NOT USE THE FILE LOGGER IN THIS MODULE


class QueueItem:
    @property
    def path(self) -> Path:
        return self.__path

    @property
    def last(self) -> bool:
        return self.__last

    def __init__(self, path: Path, last: bool = False):
        self.__path = path
        self.__last = last

    def __str__(self):
        return "{" + f'"last": {self.last}, "path": {self.path}' + "}"


class LogSender(Thread):
    @property
    def queue(self) -> SimpleQueue:
        return self.__queue

    @property
    def app_settings(self) -> AppSettings:
        return deepcopy(self.__app_settings)

    # OVERRIDE
    def run(self):
        queue = self.__queue
        app_settings = self.__app_settings

        app_name = app_settings.name
        identifier = app_settings.identifier

        while True:
            item: QueueItem = queue.get()
            file = item.path
            last = item.last

            # print(f"LogSender, processing : {file}")

            if gtff.LOG_COLLECTION:
                archives_file = file.parent / "archives" / f"{file.stem}.log"
                object_key = f"{app_name}-app/logs/{identifier}/{file.stem}.log"
                tmp_file = file.parent / "tmp" / f"{file.stem}.log"

                # print(f"Sending to S3, file : {file}")
                # print(f"Sending to S3, archives_file : {archives_file}")
                # print(f"Sending to S3, object_key : {object_key}")
                # print(f"Sending to S3, tmp_file : {tmp_file}")

                try:
                    send_to_s3(
                        archives_file=archives_file,
                        file=file,
                        object_key=object_key,
                        tmp_file=tmp_file,
                    )
                except Exception:
                    pass
                    # print(f"Sending to S3 failed : {e}")
                finally:
                    pass

            if last:
                break

    # OVERRIDE
    def __init__(
        self,
        app_settings: AppSettings,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.__app_settings = app_settings

        self.__queue: SimpleQueue = SimpleQueue()

    def send_path(self, path: Path, last: bool = False):
        """What ever path we send it need to the closed !"""

        queue = self.__queue
        queue.put(QueueItem(path=path, last=last))
