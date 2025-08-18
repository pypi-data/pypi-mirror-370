import json
import tempfile
import webbrowser


def _view_nosql_collection(data, col_name):
    """
    View a NoSQL collection in a user-friendly HTML format.

    data -- List of dictionaries representing the collection documents.
    col_name -- Name of the collection to display in the title.
    """
    # HTML template
    html_template = (
        """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>
        """
        + f"""
        {col_name}
        """
        + """
        </title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
                margin-top: 20px;
            }
            .card {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.15);
                width: 280px;
                padding: 15px;
                transition: transform 0.2s;
                word-wrap: break-word;
            }
            .card:hover {
                transform: scale(1.03);
            }
            .card-header {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 10px;
                color: #444;
            }
            .field {
                margin: 5px 0;
                font-size: 14px;
                color: #555;
            }
            .field strong {
                color: #333;
            }
            .collapsible {
                background-color: #007BFF;
                color: white;
                cursor: pointer;
                padding: 8px;
                border: none;
                text-align: left;
                outline: none;
                font-size: 14px;
                border-radius: 4px;
                margin-top: 10px;
            }
            .active, .collapsible:hover {
                background-color: #0056b3;
            }
            .content {
                padding: 0 10px;
                display: none;
                overflow: hidden;
                background-color: #f9f9f9;
                border-radius: 4px;
                margin-top: 5px;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
    """
        + f"""
    <h1>Collection: {col_name}</h1>
    <div class="container">
    """
    )

    # Generate cards dynamically
    for idx, doc in enumerate(data, start=1):
        # Pick a title: name/title or first key or fallback to Document #n
        if "name" in doc:
            title = doc["name"]
        elif "title" in doc:
            title = doc["title"]
        else:
            title = (
                f"{list(doc.keys())[0]}: {list(doc.values())[0]}"
                if doc
                else f"Document {idx}"
            )

        html_template += f'<div class="card"><div class="card-header">{title}</div>'

        for k, v in doc.items():
            if isinstance(v, (dict, list)):
                json_str = json.dumps(v, indent=2)
                html_template += f"""
                <button class="collapsible">{k}</button>
                <div class="content"><pre>{json_str}</pre></div>
                """
            else:
                html_template += f'<div class="field"><strong>{k}:</strong> {v}</div>'

        html_template += "</div>"

    html_template += """
    </div>
    <script>
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                content.style.display = (content.style.display === "block") ? "none" : "block";
            });
        }
    </script>
    </body>
    </html>
    """

    # Write to temporary file and open in browser
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
        f.write(html_template)
        webbrowser.open("file://" + f.name)
