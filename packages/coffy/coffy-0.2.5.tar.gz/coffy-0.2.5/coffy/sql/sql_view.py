import webbrowser
import tempfile
from pathlib import Path
from html import escape


def _show_sqldict_in_browser(sql_data, title="SQLDict Viewer"):
    """
    Render an SQLDict object in the browser as an HTML table.
    """
    if not len(sql_data):
        raise ValueError("SQLDict is empty.")

    # Extract data
    data = sql_data.as_list()
    columns = list(data[0].keys())

    # Build table header
    header_html = "".join(f"<th>{escape(col)}</th>" for col in columns)

    # Build table rows
    rows_html = ""
    for row in data:
        row_html = "".join(f"<td>{escape(str(row[col]))}</td>" for col in columns)
        rows_html += f"<tr>{row_html}</tr>\n"

    # Full HTML template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{escape(title)}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 20px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background: #f4f4f4;
            }}
            tr:nth-child(even) {{
                background: #fafafa;
            }}
        </style>
    </head>
    <body>
        <h1>{escape(title)}</h1>
        <table>
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """

    # Write HTML to temp file
    temp_file = Path(tempfile.gettempdir()) / "sqldict_viewer.html"
    temp_file.write_text(html, encoding="utf-8")

    # Open in default browser
    webbrowser.open(temp_file.as_uri())
