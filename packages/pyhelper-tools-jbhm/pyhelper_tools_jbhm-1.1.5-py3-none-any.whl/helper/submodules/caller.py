from ..core import time, Path, os, json, ET, csv, show_gui_popup, t, pd


def call(
    name: str,
    type: str = None,
    path: str = None,
    timeout: int = 5,
    strict: bool = True,
    verbose: bool = False,
):
    start_time = time.time()
    path = Path(path) if path else Path.cwd()
    name = Path(name).stem

    def search_files(directory):
        found = {}
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if file_path.stem == name:
                    ext = file_path.suffix[1:].lower()
                    if ext in ["csv", "json", "xml"]:
                        found[ext] = file_path
            if time.time() - start_time > timeout:
                break
        return found

    found = search_files(path)

    if verbose:
        show_gui_popup(
            title=t("file_search_title"),
            text=f"{t('searching_from')}: {path}\n{t('files_found')}: {list(found.keys())}",
        )

    if type:
        type = type.lower()
        if type not in found:
            raise FileNotFoundError(
                t("file_not_found_explicit").format(name=name, ext=type, path=path)
            )
        return read(found[type], type)
    else:
        if not found:
            raise FileNotFoundError(
                t("file_not_found_any").format(name=name, path=path)
            )
        if len(found) == 1:
            ext, ruta = list(found.items())[0]
            return read(ruta, ext)
        if strict:
            raise ValueError(
                t("file_ambiguous").format(name=name, types=list(found.keys()))
            )
        else:
            return {ext: read(ruta, ext) for ext, ruta in found.items()}


def read(file_path: Path, ext: str):
    if ext == "json":
        return pd.read_json(file_path)
    elif ext == "csv":
        return pd.read_csv(file_path)
    elif ext == "xml":
        return pd.read_xml(file_path)
    elif ext == "html":
        return pd.read_html(file_path)
    else:
        raise ValueError(t("unsupported_file_type").format(ext=ext))
