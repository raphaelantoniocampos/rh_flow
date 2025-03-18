from config import Config
import time
import threading


class DownloadTask:
    def run(self):
        # TODO: add progress panels later
        downloaded_files = []

        fiorilli_thread = threading.Thread(target=self.fiorilli_downloads)
        ahgora_thread = threading.Thread(target=self.ahgora_downloads)

        fiorilli_thread.start()
        ahgora_thread.start()

        fiorilli_thread.join()
        ahgora_thread.join()

        self._wait_for_downloads_to_complete(downloaded_files)
        self._move_files_to_data_dir()

    def _wait_for_downloads_to_complete(self, downloaded_files):
        while len(downloaded_files) < 4:
            for file in self.downloads_dir_path.iterdir():
                if any(
                    keyword in file.name.lower()
                    for keyword in ["grid", "pontoferias", "pontoafast", "funcionarios"]
                ):
                    if file.name not in downloaded_files:
                        downloaded_files.append(file.name)
            time.sleep(30)

    def _move_files_to_data_dir(self):
        Config.move_files_from_downloads_dir(
            self.downloads_dir_path, self.data_dir_path
        )
