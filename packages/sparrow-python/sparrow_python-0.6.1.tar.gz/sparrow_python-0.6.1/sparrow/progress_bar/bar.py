from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table


class Bar:
    def __init__(self, total, title='Progress'):
        """
        bar = Bar(100, title='Processing').start()
        for i in range(100):
            bar(f"Processing item {i}")
        bar.stop()

        # Using with context manager
        with Bar(100, title='Processing') as bar:
            for i in range(100):
                bar(f"Processing item {i}")
        """
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        )
        self.task = self.progress.add_task(title, total=total)

    def __call__(self, description, advance=1):
        self.progress.update(self.task, advance=advance, description=description)

    def start(self):
        self.progress.start()
        return self

    def stop(self):
        self.progress.stop()

    def __enter__(self):
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()


class probar:
    def __init__(self, iterable, total_steps=None, title=None):
        """
        """
        self.iterable = iterable
        if total_steps is None:
            try:
                total_steps = len(iterable)
                if not total_steps:
                    total_steps = None
            except:
                total_steps = None
        self.total_steps = total_steps
        self.title = title

    def __iter__(self):
        with Progress() as progress:
            task = progress.add_task(self.title, total=self.total_steps)
            for idx, item in enumerate(self.iterable):
                yield item
                progress.update(task, advance=1)


class MultiProbar:
    def __init__(self):
        self._progress = Progress()
        self._overall_progress = Progress()
        self.live_progress = None

    def add_task(self, description, total):
        self._progress.add_task(description=description,
                                total=total)

    def start(self):
        # self._progress.start()
        total = sum(task.total for task in self._progress.tasks)
        overall_task = self._overall_progress.add_task("All Jobs", total=int(total))

        progress_table = Table.grid()
        progress_table.add_row(
            Panel.fit(
                self._overall_progress, title="Overall Progress", border_style="green", padding=(2, 2)
            ),
            Panel.fit(self._progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
        )

        self.progress_table = progress_table
        self.live_progress = Live(progress_table, refresh_per_second=10)
        self.live_progress.start()

        # with Live(progress_table, refresh_per_second=10):
        #     while not self._overall_progress.finished:
        #         # progress
        #         time.sleep(0.1)
        #         for job in self._progress.tasks:
        #             if not job.finished:
        #                 self._progress.advance(job.id)
        #
        #         completed = sum(task.completed for task in self._progress.tasks)
        #         self._overall_progress.update(overall_task, completed=completed)

    def update(self, advance=1):
        if not self._overall_progress.finished:
            time.sleep(0.1)
            for job in self._progress.tasks:
                if not job.finished:
                    self._progress.advance(job.id, advance=advance)

            completed = sum(task.completed for task in self._progress.tasks)
            self._overall_progress.update(self.progress_table, completed=completed)

    def stop(self):
        self._progress.stop()


if __name__ == "__main__":
    import time
    import threading


    # for i in probar(range(100), title="emmm"):
    #     time.sleep(0.1)

    def test1():
        def show(progress, task, total: int):
            for i in range(total):
                progress.update(task, advance=1)
                time.sleep(.005)

        progress = Progress()
        progress.start()
        task1 = progress.add_task(description=str(1000), total=1000)
        task2 = progress.add_task(description=str(2000), total=2000)
        t1 = threading.Thread(target=show, name='t1', args=(progress, task1, 1000))
        t2 = threading.Thread(target=show, name='t2', args=(progress, task2, 2000))
        t1.start()
        t2.start()
        [i.join() for i in [t1, t2]]
        progress.stop()
        print("test1 complete")


    def test2():
        with Progress() as progress:
            task1 = progress.add_task("[red]Downloading...", total=1000)
            task2 = progress.add_task("[green]Processing...", total=100)
            task3 = progress.add_task("[cyan]Cooking...", total=1000)

            while not progress.finished:
                progress.update(task1, advance=0.5)
                progress.update(task2, advance=0.3)
                progress.update(task3, advance=0.9)
                time.sleep(0.02)


    def test3():
        from time import sleep

        job_progress = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        job1 = job_progress.add_task("[green]Cooking")
        job2 = job_progress.add_task("[magenta]Baking", total=200)
        job3 = job_progress.add_task("[cyan]Mixing", total=400)

        total = sum(task.total for task in job_progress.tasks)
        overall_progress = Progress()
        overall_task = overall_progress.add_task("All Jobs", total=int(total))

        progress_table = Table.grid()
        progress_table.add_row(
            Panel.fit(
                overall_progress, title="Overall Progress", border_style="green", padding=(2, 2)
            ),
            Panel.fit(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
        )

        with Live(progress_table, refresh_per_second=10):
            while not overall_progress.finished:
                sleep(0.1)
                for job in job_progress.tasks:
                    if not job.finished:
                        job_progress.advance(job.id)

                completed = sum(task.completed for task in job_progress.tasks)
                overall_progress.update(overall_task, completed=completed)


    # test1()
    # test2()
    # test3()
    # test4()
    with Bar(100, title='Bar') as bar:
        for i in range(100):
            bar(f"Processing item {i}")
            time.sleep(0.01)

    for i in probar(range(100), title="probar"):
        time.sleep(0.01)
