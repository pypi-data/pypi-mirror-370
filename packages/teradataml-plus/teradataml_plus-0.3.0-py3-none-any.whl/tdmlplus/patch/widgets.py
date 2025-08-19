from IPython.display import display, HTML
import uuid  # To generate unique IDs
from .. import tdml
from typing import List

def _display_content_in_tabs(content_dict, tab_index_open=0):
    """
    Displays multiple pieces of HTML content in a tabbed interface within a Jupyter Notebook.

    Args:
        content_dict (dict): A dictionary where keys are tab titles (str) and values are HTML content (str).
        tab_index_open (int): Index of the tab to be opened by default. Negative values count from the end.

    Example:
        content_dict = {
            "Tab 1": "<p>This is content for Tab 1</p>",
            "Tab 2": "<p>This is content for Tab 2</p>"
        }
        display_content_in_tabs(content_dict, tab_index_open=-1)
    """
    unique_id = str(uuid.uuid4()).replace("-", "")  # Unique identifier for this tab instance

    num_tabs = len(content_dict)
    tab_index_open = (tab_index_open % num_tabs) if num_tabs > 0 else 0  # Handle negative indices

    html_code = f"""
    <style>
        .tab-container-{unique_id} {{
            border-bottom: 2px solid #ddd;
            display: flex;
        }}
        .tab-label-{unique_id} {{
            padding: 10px 15px;
            cursor: pointer;
            border: 1px solid #ddd;
            border-bottom: none;
            background: #f1f1f1;
            margin-right: 5px;
        }}
        .tab-label-{unique_id}.active {{
            background: white;
            border-top: 2px solid #007bff;
            font-weight: bold;
        }}
        .tab-content-{unique_id} {{
            display: none;
            padding: 15px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .tab-content-{unique_id}.active {{
            display: block;
        }}
    </style>

    <div class="tab-container-{unique_id}">
    """

    tab_ids = []  # To store the tab ids for each content
    for i, (tab_title, _) in enumerate(content_dict.items()):
        tab_id = str(uuid.uuid4()).replace("-", "")  # Unique ID for each tab
        tab_ids.append(tab_id)
        active_class = "active" if i == tab_index_open else ""
        html_code += f'<div class="tab-label-{unique_id} {active_class}" data-tab="{tab_id}">{tab_title}</div>'

    html_code += "</div>"

    # Add the content for each tab
    for i, (tab_title, content) in enumerate(content_dict.items()):
        tab_id = tab_ids[i]
        display_style = "active" if i == tab_index_open else ""
        html_code += f'<div class="tab-content-{unique_id} {display_style}" id="tab-{tab_id}">{content}</div>'

    # JavaScript to handle tab switching
    html_code += f"""
    <script>
        (function() {{
            let tabs = document.querySelectorAll(".tab-label-{unique_id}");
            let contents = document.querySelectorAll(".tab-content-{unique_id}");

            tabs.forEach((tab) => {{
                tab.addEventListener("click", function() {{
                    tabs.forEach(t => t.classList.remove("active"));
                    contents.forEach(c => c.classList.remove("active"));

                    let tabId = this.getAttribute("data-tab");
                    document.getElementById("tab-" + tabId).classList.add("active");
                    this.classList.add("active");
                }});
            }});
        }})();
    </script>
    """

    display(HTML(html_code))




def tab_dfs(
    DFs: List['tdml.DataFrame'] = [],
    table_names: List[str] = [],
    tab_index_open: int = 0
) -> None:
    """
    Display multiple Teradata DataFrames and table/view names in a tabbed UI
    in a Jupyter Notebook.

    Args:
        DFs (List[tdml.DataFrame], optional): DataFrames to render directly.
        table_names (List[str], optional): Table or view names to load as DataFrames.
        tab_index_open (int, optional): Index of the tab to open by default.
                                        Negative values count from the end.

    Returns:
        None
    """
    assert (len(DFs) > 0) or (len(table_names) > 0), "Provide at least one DataFrame or table name."

    DFs_table_names_dict = {}
    for DF in DFs:
        DF._DataFrame__execute_node_and_set_table_name(DF._nodeid, DF._metaexpr)
        DFs_table_names_dict[DF._table_name] = DF._repr_html_()

    tables_table_names_dict = {
        t: tdml.DataFrame(t)._repr_html_() for t in table_names
    }

    _display_content_in_tabs(
        DFs_table_names_dict | tables_table_names_dict,
        tab_index_open=tab_index_open
    )

