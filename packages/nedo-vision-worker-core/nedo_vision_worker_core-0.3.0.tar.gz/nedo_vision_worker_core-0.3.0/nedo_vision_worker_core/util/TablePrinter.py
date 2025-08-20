from tabulate import tabulate

class TablePrinter:
    """Utility class for printing structured data in a tabular format."""

    @staticmethod
    def print_table(data, headers=None, title="Data Table", table_format="fancy_grid"):
        """
        Prints a list of dictionaries or lists in a formatted table.

        Args:
            data (list): A list of dictionaries or lists containing the data.
            headers (list, optional): Column headers (if None, inferred from dict keys).
            title (str, optional): Title for the table (default: "Data Table").
            table_format (str, optional): Tabulate format (default: "fancy_grid").
        """
        if not data:
            print(f"\n{title}: No data available.\n")
            return

        # If data is a list of dictionaries, extract headers automatically
        if isinstance(data[0], dict):
            if headers is None:
                headers = list(data[0].keys())
            data = [[row.get(header, "") for header in headers] for row in data]

        print(f"\n{title}")
        print(tabulate(data, headers=headers, tablefmt=table_format))
