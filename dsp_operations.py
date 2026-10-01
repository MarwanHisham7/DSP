import os


def read_signal_file(file_path):
    indices = []
    values = []

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    n = int(parts[0])
                    x = float(parts[1])
                    indices.append(n)
                    values.append(x)
                except ValueError:
                    continue

    if not indices:
        raise ValueError(f"No valid sample data found in {file_path}")

    return indices, values


def multiply_signal(indices, values, factor):
    scaled_values = [x * factor for x in values]
    return indices, scaled_values


def shift_signal(indices, values, k):
    shifted_indices = [n - k for n in indices]
    return shifted_indices, values


def fold_signal(indices, values):
    folded_indices = [-n for n in reversed(indices)]
    folded_values = list(reversed(values))
    return folded_indices, folded_values


def add_signals(signals_dict):
    sample_map = {}
    for sig in signals_dict.values():
        for n, x in zip(sig['indices'], sig['values']):
            sample_map[n] = sample_map.get(n, 0.0) + x

    res_indices = sorted(sample_map.keys())
    res_values = [sample_map[n] for n in res_indices]
    return res_indices, res_values


def subtract_signals(sig1, sig2):
    sample_map = {}
    for n, x in zip(sig1['indices'], sig1['values']):
        sample_map[n] = x

    for n, x in zip(sig2['indices'], sig2['values']):
        sample_map[n] = sample_map.get(n, 0.0) - x

    res_indices = sorted(sample_map.keys())
    res_values = [sample_map[n] for n in res_indices]
    return res_indices, res_values


if __name__ == "__main__":
    print("--- Running Staff Verification Tests ---\n")

    from DSP_Task_TEST_functions import (
        AddSignalSamplesAreEqual,
        SubSignalSamplesAreEqual,
        MultiplySignalByConst,
        ShiftSignalByConst,
        Folding
    )

    # Load test signals
    n1, x1 = read_signal_file("Signal1.txt")
    n2, x2 = read_signal_file("Signal2.txt")

    # 1. Addition Test
    add_n, add_x = add_signals({
        "Signal1.txt": {"indices": n1, "values": x1},
        "Signal2.txt": {"indices": n2, "values": x2}
    })
    AddSignalSamplesAreEqual("Signal1.txt", "Signal2.txt", add_n, add_x)

    # 2. Subtraction Test
    sub_n, sub_x = subtract_signals(
        {"indices": n1, "values": x1},
        {"indices": n2, "values": x2}
    )
    SubSignalSamplesAreEqual("Signal1.txt", "Signal2.txt", sub_n, sub_x)

    # 3. Multiply by 5 Test
    mul_n, mul_x = multiply_signal(n1, x1, 5)
    MultiplySignalByConst(5, mul_n, mul_x)

    # 4. Advance (+3) Test
    adv_n, adv_x = shift_signal(n1, x1, 3)
    ShiftSignalByConst(3, adv_n, adv_x)

    # 5. Delay (-3) Test
    delay_n, delay_x = shift_signal(n1, x1, -3)
    ShiftSignalByConst(-3, delay_n, delay_x)

    # 6. Folding Test
    fold_n, fold_x = fold_signal(n1, x1)
    Folding(fold_n, fold_x)

    print("\n--- All Tests Completed ---")