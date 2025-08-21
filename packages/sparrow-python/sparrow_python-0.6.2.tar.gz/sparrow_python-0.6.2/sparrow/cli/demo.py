from rich import print
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
table = Table(title="", box=None)
table.add_column("server", justify="left", style="cyan", no_wrap=True)
table.add_column("in-net", justify="left", style="#df412f")
table.add_column("out-net", justify="left", style="green")
table.add_column("out-net", justify="left", style="#f5bb00")

table.add_row("tft", "http://localhost:8800", "http://localhost:58800", "./TFT-project/tft.log")
table.add_row("streamlit", "http://localhost:8501", "http://localhost:34501", "./streamlit.log")
table.add_row("callback", "http://localhost:33221", "http://localhost:33221", "./callback.log")

print(Panel(table, title="🤗MVTF is ready to serve!", expand=False, ))

text = Text("Hello\n asdf\nasldfj\nasdf", justify="center")


def _init_table(n_cols=3):
    table = Table(
        title="", box=None, highlight=True, show_header=False, min_width=50
    )
    table.add_column('', justify='left')
    for _ in range(n_cols-1):
        table.add_column('', justify='right')
    return table


ttable = _init_table(n_cols=2)



# print(Panel(table, title="🤗MVTF is ready to serve!", expand=False))
