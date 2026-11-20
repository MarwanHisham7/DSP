import os
import math
import numpy as np


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


def generate_sinusoidal_signal(wave_type, amplitude, phase_shift_deg, analog_freq, sampling_freq, duration=1.0):
    """
    Generates discrete sinusoidal/cosinusoidal signal.
    x(n) = A * sin(2*pi*(f/fs)*n + theta) or A * cos(2*pi*(f/fs)*n + theta)
    """
    if sampling_freq <= 0:
        raise ValueError("Sampling frequency must be greater than zero.")

    # Convert phase shift from degrees to radians
    phase_rad = math.radians(phase_shift_deg)

    # Total samples N = duration * sampling_frequency
    N = int(sampling_freq * duration)
    indices = list(range(N))
    values = []

    for n in indices:
        angle = 2 * math.pi * (analog_freq / sampling_freq) * n + phase_rad
        if wave_type.lower() == 'sine':
            val = amplitude * math.sin(angle)
        else:
            val = amplitude * math.cos(angle)
        values.append(round(val, 6))

    return indices, values

def quantize_signal(indices, values, levels=None, bits=None):

    x = np.asarray(values, dtype=float)

    if x.size == 0:
        raise ValueError("The signal is empty.")

    if not np.all(np.isfinite(x)):
        raise ValueError("Signal values must be finite numbers.")

    # 1. Determine levels and bits
    if bits is not None:
        if not isinstance(bits, int) or not 1 <= bits <= 16:
            raise ValueError("Bits must be an integer from 1 to 16.")

        levels = 2 ** bits

    elif levels is not None:
        if not isinstance(levels, int) or not 2 <= levels <= 65536:
            raise ValueError("Levels must be an integer from 2 to 65536.")

        bits = math.ceil(math.log2(levels))

    else:
        raise ValueError("Specify either levels or bits.")

    # 2. Find minimum and maximum
    xmin = float(np.min(x))
    xmax = float(np.max(x))


    # 3. Calculate step size
    step = (xmax - xmin) / levels

    # 4. Create intervals
    level_ranges = []

    for i in range(levels):
        lower = xmin + i * step
        upper = xmin + (i + 1) * step
        midpoint = (lower + upper) / 2

        level_ranges.append({
            "lower": lower,
            "upper": upper,
            "midpoint": midpoint
        })

    # 5. Find the interval of each sample
    interval_indices = []
    quantized = []

    for sample in x:
        for i in range(levels):

            lower = level_ranges[i]["lower"]
            upper = level_ranges[i]["upper"]
            midpoint = level_ranges[i]["midpoint"]

            if lower <= sample < upper:
                interval_indices.append(i + 1)
                quantized.append(midpoint)
                break
            elif i == levels - 1 and np.isclose(sample, upper):
                interval_indices.append(i + 1)
                quantized.append(midpoint)
                break

    interval_indices = np.array(interval_indices)
    quantized = np.array(quantized)

    # 6. Calculate errors
    errors = quantized - x
    squared_errors = errors ** 2

    average_error_power = float(np.mean(squared_errors))

    # 7. Generate binary codes
    codes = [
        format(int(index) - 1, f"0{bits}b")
        for index in interval_indices
    ]

    # 8. Build output table
    table_rows = []

    for i in range(len(x)):
        table_rows.append((
            int(indices[i]),
            float(x[i]),
            int(interval_indices[i]),
            float(quantized[i]),
            float(errors[i]),
            float(squared_errors[i]),
            codes[i]
        ))

    # 9. Return results
    return (
        table_rows,
        quantized.tolist(),
        errors.tolist(),
        squared_errors.tolist(),
        codes,
        average_error_power
    )

def moving_average(indices, values, window_size):
    if not 1 <= window_size <= len(values):
        raise ValueError("Invalid window size")

    result_indices = []
    result_values = []

    for i in range(len(values) - window_size + 1):
        total = 0

        for j in range(window_size):
            total += values[i + j]

        average = total / window_size

        result_indices.append(indices[i])
        result_values.append(average)

    return result_indices, result_values


def first_derivative(indices, values):
    if len(values) < 2:
        raise ValueError("At least 2 samples required")

    result_indices = []
    result_values = []

    for i in range(len(values) - 1):
        result_indices.append(indices[i])
        result_values.append(values[i + 1] - values[i])

    return result_indices, result_values



def second_derivative(indices, values):
    if len(values) < 3:
        raise ValueError("At least 3 samples required")

    result_indices = []
    result_values = []

    for i in range(len(values) - 2):
        result_indices.append(indices[i])

        result_values.append(
            values[i + 2] - 2 * values[i + 1] + values[i]
        )

    return result_indices, result_values

def convolve_signals(indices1, values1, indices2, values2):
    if not values1 or not values2:
        raise ValueError("Signals cannot be empty")

    output_length = len(values1) + len(values2) - 1

    result_values = [0] * output_length

    for i in range(len(values1)):
        for j in range(len(values2)):
            result_values[i + j] += values1[i] * values2[j]

    start_index = indices1[0] + indices2[0]

    result_indices = list(
        range(start_index, start_index + output_length)
    )

    return result_indices, result_values


if __name__ == "__main__":
    print("--- Running Staff Verification Tests ---\n")

    from DSP_Task_TEST_functions import (
        AddSignalSamplesAreEqual,
        SubSignalSamplesAreEqual,
        MultiplySignalByConst,
        ShiftSignalByConst,
        Folding,
        CompareSignals
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


    # Moving Average Test 1: Window Size = 3
    indices, values = read_signal_file("MovingAvg_input.txt")

    result_indices, result_values = moving_average(
        indices, values, 3
    )

    print("\nMoving Average Test 1 (Window = 3)")

    CompareSignals(
        "MovingAvg_out1.txt",
        result_indices,
        result_values
    )

    # Moving Average Test 2: Window Size = 5
    result_indices, result_values = moving_average(
        indices, values, 5
    )

    print("\nMoving Average Test 2 (Window = 5)")

    CompareSignals(
        "MovingAvg_out2.txt",
        result_indices,
        result_values
    )

    # 3. First Derivative Test
    indices, values = read_signal_file("Derivative_input.txt")

    result_indices, result_values = first_derivative(
        indices, values
    )

    print("\nFirst Derivative Test")

    CompareSignals(
        "1st_derivative_out.txt",
        result_indices,
        result_values
    )


    # 4. Second Derivative Test
    result_indices, result_values = second_derivative(
        indices, values
    )

    print("\nSecond Derivative Test")

    CompareSignals(
        "2nd_derivative_out.txt",
        result_indices,
        result_values
    )


    # 5. Convolution Test
    indices1, values1 = read_signal_file("Conv1.txt")
    indices2, values2 = read_signal_file("Conv2.txt")

    result_indices, result_values = convolve_signals(
        indices1, values1,
        indices2, values2
    )

    print("\nConvolution Test")

    CompareSignals(
        "Conv_output.txt",
        result_indices,
        result_values
    )



    print("\n--- All Tests Completed ---")