import re
import io
import sys


def shift_trailing_spaces_to_start(s):
    stripped = s.rstrip()
    num_spaces = len(s) - len(stripped)
    return " " * num_spaces + stripped


def print_aligned_table(rows):
    # headers
    headers = ["Layer (type)", "Output Shape", "Param #"]
    all_rows = [headers] + rows

    # max width
    col_widths = []
    for col_idx in range(3):
        max_width = max(len(row[col_idx]) for row in all_rows)
        col_widths.append(max_width)

    out = ""
    # Print headers
    out += (
        f"{'-' * col_widths[0]}----"
        f"{'-' * col_widths[1]}----"
        f"{'-' * col_widths[2]}"
    )
    out += (
        f"{headers[0]:>{col_widths[0]}}    "
        f"{headers[1]:>{col_widths[1]}}    "
        f"{headers[2]:>{col_widths[2]}}"
    )
    out += (
        f"{'=' * col_widths[0]}===="
        f"{'=' * col_widths[1]}===="
        f"{'=' * col_widths[2]}"
    )

    # Print row
    for row in rows:
        out += (
            f"{row[0]:>{col_widths[0]}}    "
            f"{row[1]:>{col_widths[1]}}    "
            f"{row[2]:>{col_widths[2]}}"
        )
    out += (
        f"{'=' * col_widths[0]}===="
        f"{'=' * col_widths[1]}===="
        f"{'=' * col_widths[2]}"
    )

    return out


def reform_tensorflow(summary_str):
    rows = []
    lines = summary_str.splitlines()

    for line in lines:
        # Only process data rows
        if "│" in line and all(x not in line for x in ["─", "━", "┏", "┡"]):
            cells = [cell.strip() for cell in line.split("│")[1:-1]]
            rows.append(cells)

    for i in range(len(rows)):
        # Extract text inside parentheses from the first column
        matches = re.findall(r"\((.*?)\)", rows[i][0])
        if matches:
            rows[i][0] = matches[0] + f"-{i + 1}"

    out = print_aligned_table(rows)

    for line in lines[-3:]:
        out += line

    return out


def model_summary(model: "Pytorch or Tensorflow", input_data=None):
    try:
        import torch.nn as nn

        if isinstance(model, nn.Module):
            from torchinfo import summary

            if input_data is None:
                raise ValueError("For PyTorch models, you must provide `input_data`.")
            model.eval()

            buffer = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = buffer
            summary(model, input_data=input_data)
            sys.stdout = original_stdout
            output = buffer.getvalue()

            return output
    except ImportError:
        pass  # torch not installed

    try:
        import tensorflow as tf

        if isinstance(model, tf.keras.Model):
            buffer = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = buffer
            model.summary(line_length=200)
            summary(model, input_data=input_data)
            sys.stdout = original_stdout
            output = buffer.getvalue()
            output = reform_tensorflow(output)
            return output
    except ImportError:
        pass  # tensorflow not installed

    raise TypeError(
        "Unknown model type or missing dependencies. Make sure it's a PyTorch or TensorFlow model."
    )
