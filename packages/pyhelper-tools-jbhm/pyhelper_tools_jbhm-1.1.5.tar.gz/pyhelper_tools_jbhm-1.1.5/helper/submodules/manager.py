from ..core import np, show_gui_popup


def normalize(data: np.ndarray):
    range_val = data.max() - data.min()
    return np.zeros_like(data) if range_val == 0 else (data - data.min()) / range_val


def conditional(df, conditions, results, column_name):
    try:
        if len(conditions) != len(results):
            raise ValueError("La cantidad de condiciones y resultados debe ser igual.")

        condlist = []
        for cond in conditions:
            if callable(cond):
                cond = cond(df)
            cond = np.asarray(cond, dtype=bool)
            condlist.append(cond)

        df[column_name] = np.select(condlist, results, default=False)
        return df

    except Exception as e:
        show_gui_popup(title="Error", content=str(e))
