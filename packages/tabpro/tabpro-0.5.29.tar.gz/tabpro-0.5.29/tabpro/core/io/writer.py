'''
Base class for writing data to a file.
'''

from typing import (
    IO,
)

import pandas as pd
from rich.console import Console

from ..classes.row import Row

from ..progress import (
    Progress,
    TaskID,
)

from tqdm.auto import tqdm

class BaseWriter:
    def __init__(
        self,
        target: str,
        streaming: bool = True,
        quiet: bool = False,
        encoding: str = 'utf-8',
        skip_header: bool = False,
        progress: Progress | None = None,
    ):
        self.target = target
        self.streaming = streaming
        self.quiet = quiet
        self.encoding = encoding
        self.skip_header = skip_header
        self.rows: list[Row] | None = None
        self.fobj: IO | None = None
        self.finished: bool = False
        self.progress: Progress | None = progress
        self.task_id: TaskID | None = None
        if not self.support_streaming():
            self.streaming = False
        if self.streaming:
            self._open()

    def _open(self):
        if self.fobj:
            return
        self.fobj = open(self.target, 'w', encoding=self.encoding)
        if self.streaming:
            if self.progress:
                if self.task_id is None:
                    console = self._get_console()
                    console.log('Writing into: ', self.target)
                    self.task_id = self.progress.add_task(
                        f'Writing rows...',
                    )

    def support_streaming(self):
        return False

    def push_row(self, row: Row | pd.Series):
        if self.rows is None:
            self.rows = []
        if isinstance(row, pd.Series):
            new_row = Row()
            for key in row.keys():
                new_row[key] = row[key]
            row = new_row
        self.rows.append(row)
        if self.streaming:
            self._write_row(row)
            if self.progress and self.task_id is not None:
                self.progress.update(self.task_id, advance=1)

    def push_rows(self, rows: list[Row] | pd.DataFrame):
        if isinstance(rows, pd.DataFrame):
            for _, row in rows.iterrows():
                self.push_row(row)
        else:
            for row in rows:
                self.push_row(row)

    def _get_console(self):
        if self.progress:
            return self.progress.console
        else:
            return Console()

    def _write_row(self, row: Row):
        raise NotImplementedError
    
    def _write_all_rows(self):
        raise NotImplementedError
    
    def close(self):
        if self.finished: return
        if self.rows:
            if not self.streaming:
                if not self.quiet:
                    console = self._get_console()
                    console.log(f'writing {len(self.rows)} rows into: ', self.target)
                self._write_all_rows()
            self.finished = True
        if self.fobj:
            self.fobj.close()
            self.fobj = None
        return
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
    
    def __del__(self):
        self.close()
        return
