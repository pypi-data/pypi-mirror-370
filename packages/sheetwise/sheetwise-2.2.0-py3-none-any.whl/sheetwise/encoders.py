"""Encoding utilities for spreadsheet data."""

import pandas as pd


class VanillaEncoder:
    """Vanilla spreadsheet encoding with cell addresses and formats"""

    def encode_to_markdown(self, df: pd.DataFrame, include_format: bool = False) -> str:
        """
        Encode spreadsheet to Markdown-like format

        Args:
            df: Input DataFrame
            include_format: Whether to include format information

        Returns:
            Markdown-style string representation
        """
        lines = []

        for i, row in df.iterrows():
            row_parts = []
            for j, col in enumerate(df.columns):
                cell_value = row[col]
                cell_addr = self._to_excel_address(i, j)

                if pd.isna(cell_value) or cell_value == "":
                    cell_repr = f"{cell_addr}, "
                else:
                    cell_repr = f"{cell_addr},{cell_value}"

                row_parts.append(cell_repr)

            lines.append("|".join(row_parts))

        return "\n".join(lines)

    def _to_excel_address(self, row: int, col: int) -> str:
        """Convert row, column indices to Excel address"""
        col_letter = ""
        col_num = col + 1
        while col_num > 0:
            col_num -= 1
            col_letter = chr(col_num % 26 + ord("A")) + col_letter
            col_num //= 26
        return f"{col_letter}{row + 1}"
