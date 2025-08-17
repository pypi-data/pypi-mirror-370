def show(on: bool = True) -> None:
    """
    В JupyterLab включает/выключает скрытие текста и курсора в АКТИВНОЙ ячейке.
    show(True)  -> скрыть (слепой набор)
    show(False) -> показать (удалить стиль)
    В средах вне Jupyter — тихо ничего не делает.
    """
    try:
        from IPython.display import HTML, Javascript, display  # type: ignore
    except Exception:
        return

    STYLE_ID = "blind-typing-hide-cursor"

    if on:
        css = f"""
        <style id="{STYLE_ID}">
        .jp-Notebook .cm-editor.cm-focused .cm-content,
        .jp-Notebook .cm-editor.cm-focused .cm-content * {{
          color: transparent !important;
        }}
        .jp-Notebook .cm-editor.cm-focused .cm-cursor {{
          display: none !important;
        }}
        </style>
        """
        display(HTML(css))
    else:
        js = f"var el = document.getElementById('{STYLE_ID}'); if (el) el.remove();"
        display(Javascript(js))
