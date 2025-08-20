from aicard.evaluation.loaders import read_data, is_path, read_pd
from aicard.evaluation.experiments import convert_to_datasets, anns_to_datasets


def get_forced_sets():
    return {"label","class_name","ground_truth","emotion","cat"}


def _unknown_columns_handler(data, number_of_samples, length_of_sample):
    out = {}
    forced_sets = get_forced_sets()
    for column_name in data.column_names:
        my_set = set({str(row) for row in data[column_name]})  # for immutable values
        if len(my_set) <= 20:
            out[f"values of {column_name} and number of instances"] = [
                f"{s}: {len(data.filter(lambda x: str(x[column_name]) == s))}"
                for s in my_set
            ]
        elif any(item in column_name.lower() for item in forced_sets):  # force a set
            try:  # if items are iterable flatten them
                items = []
                for item in data[column_name]:
                    try:
                        items.extend(item)
                    except TypeError:
                        items.extend([item])
            except TypeError:
                items = data[column_name]
            my_set = set(items)
            out[f"values of {column_name} and number of instances"] = [
                f"{s}: {sum(1 for label in items if label == s)}" for s in my_set
            ]
        else:
            out[f"sample for the first {number_of_samples} rows of {column_name}"] = [
                f"{data[column_name][i]}"[:length_of_sample]
                for i in range(number_of_samples)
            ]
    return out


def _extract_data_info(
    data,
    anns=[None],
    out_in={},
    task=None,
    max_out_chars=3000,
    number_of_samples=5,
    length_of_sample=100,
):
    if is_path(data):
        data = read_data(data)
    data = convert_to_datasets(data)
    anns = anns_to_datasets(anns)

    out = out_in
    out["column_names"] = (
        data.column_names
        if len(anns.column_names) == 0
        else data.column_names + anns.column_names
    )
    out["length of data"] = len(data)

    if task is not None:
        out["task"] = task

    out = out | _unknown_columns_handler(data, number_of_samples, length_of_sample)

    if len(anns.column_names) != 0:
        out = out | _unknown_columns_handler(anns, number_of_samples, length_of_sample)

    if len(f"{out}") > max_out_chars:  # ensure the output is not too big
        if number_of_samples == 1:
            raise ValueError("Dataset is too big for the LLM to handle")
        out = _extract_data_info(
            data=data,
            anns=anns,
            out_in=out_in,
            task=task,
            max_out_chars=3000,
            number_of_samples=number_of_samples - 1,
            length_of_sample=length_of_sample - 20,
        )

    return out


def ydata_report(path, destination="ydata.html"):
    from ydata_profiling import ProfileReport

    df = read_data_pd(path)
    profile = ProfileReport(df, title="Dataset Report", explorative=True)
    profile.to_file(destination)
