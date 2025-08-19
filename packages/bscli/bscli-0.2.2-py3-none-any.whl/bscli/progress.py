class ProgressReporter:
    def start(self, current: int, total: int, name: str):
        pass

    def finish(self, total: int):
        pass


class Report(ProgressReporter):
    def __init__(self, step: str):
        self.step = step

    def start(self, current: int, total: int, name: str):
        print("\x1b[2K", end="")  # clear line as next line printed may be shorter
        print(
            f'Starting "{self.step}" for {name} [{current}/{total}]',
            end="\r",
            flush=True,
        )

    def finish(self, total: len):
        print("\x1b[2K", end="")  # clear line as next line printed may be shorter
        print(f'Completed "{self.step}" [{total}/{total}]')
