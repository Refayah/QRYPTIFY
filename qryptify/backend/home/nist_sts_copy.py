import pandas as pd
import numpy as np
import math
import scipy.special as ss
from scipy.stats import norm, entropy
import warnings
from .xgboost_model import *
import zlib
from scipy.stats import skew
from scipy.signal import welch
from scipy.fft import rfft, rfftfreq
import hashlib
import os
from numba import jit
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

warnings.filterwarnings('ignore')

class BinaryData:
    def __init__(self, bit_string):
        n = len(bit_string)
        padding = (8 - n % 8) % 8
        if padding > 0:
            bit_string += '0' * padding

        # pack bits to bytes efficiently
        n_bytes = len(bit_string) // 8
        packed_bytes = int(bit_string, 2).to_bytes(n_bytes, 'big')
        self.packed = np.frombuffer(packed_bytes, dtype=np.uint8)
        self.unpacked = np.unpackbits(self.packed)[:n]
        self.n = n

        # Cache commonly used values
        self._ones_count = None
        self._byte_counts = None

    @property
    def ones_count(self):
        if self._ones_count is None:
            self._ones_count = np.count_nonzero(self.unpacked)
        return self._ones_count

    @property
    def byte_counts(self):
        if self._byte_counts is None:
            self._byte_counts = np.bincount(self.packed, minlength=256)
        return self._byte_counts

def monobit_test(binary):
    if binary.n == 0:
        return [0.0, False]
    s = abs(2.0 * float(binary.ones_count) - float(binary.n))
    p = math.erfc(s / (math.sqrt(float(binary.n)) * math.sqrt(2.0)))
    return [p, p >= 0.01]

def frequency_within_block_test(binary, M=128):
    if binary.n < M:
        return [0.0, False]
    nBlocks = binary.n // M
    blocks = binary.unpacked[:nBlocks * M].reshape(nBlocks, M)
    proportions = np.sum(blocks, axis=1, dtype=np.float64) / float(M)
    chisq = float(np.sum(4.0 * M * ((proportions - 0.5) ** 2)))
    p = ss.gammaincc(nBlocks / 2.0, chisq / 2.0)
    return [p, p >= 0.01]

def runs_test(binary):
    if binary.n < 2:
        return [0.0, False]
    prop = float(binary.ones_count) / float(binary.n)
    tau = 2.0 / math.sqrt(binary.n)
    if abs(prop - 0.5) >= tau:
        return [0.0, False]
    vobs = 1.0 + float(np.sum(binary.unpacked[:-1] != binary.unpacked[1:]))
    if prop == 0 or prop == 1:
        return [0.0, False]
    expected = 2.0 * binary.n * prop * (1.0 - prop)
    variance = 2.0 * binary.n * prop * (1.0 - prop)
    if variance == 0:
        return [0.0, False]
    numerator = abs(vobs - expected)
    denominator = 2.0 * math.sqrt(variance)
    if denominator == 0:
        return [0.0, False]
    p = math.erfc(numerator / denominator)
    return [p, p >= 0.01]

def longest_run_within_block_test(binary):
    def longest_run_in_block(block_bits):
        if len(block_bits) == 0:
            return 0
        max_run = 0
        current_run = 0
        for bit in block_bits:
            if bit == 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0
        return max_run

    bits = binary.unpacked
    n = binary.n
    if n < 128:
        return [0.0, False]
    elif n <= 6272:
        K, M = 3, 8
        vclasses = [1, 2, 3, 4]
        vprobs = [0.2148, 0.3672, 0.2305, 0.1875]
    elif n <= 750000:
        K, M = 5, 128
        vclasses = [4, 5, 6, 7, 8, 9]
        vprobs = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    else:
        K, M = 6, 10000
        vclasses = [10, 11, 12, 13, 14, 15, 16]
        vprobs = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

    N = n // M
    numBlocks = n // M
    blocks = bits[:numBlocks * M].reshape(numBlocks, M)
    runs = np.array([longest_run_in_block(block) for block in blocks])
    freqs = np.histogram(runs, bins=[-1e10, *vclasses, 1e10])[0]
    vs = np.array(freqs, dtype=np.float64)
    chisq = 0.0
    for i in range(K):
        expected = N * vprobs[i]
        if expected > 0:
            chisq += ((vs[i] - expected) ** 2) / expected
    p = ss.gammaincc(K / 2.0, chisq / 2.0)
    return [p, p >= 0.01]

def binary_matrix_rank_test(binary):
    n = binary.n
    M, Q = 32, 32
    N = n // (M * Q)
    if N == 0:
        return [0.0, False]
    bits = binary.unpacked[:N * M * Q]
    matrices = bits.reshape(N, M, Q)

    ranks = np.array([np.linalg.matrix_rank(matrix) for matrix in matrices])
    fm = np.sum(ranks == M)
    fm1 = np.sum(ranks == M - 1)
    rest = N - fm - fm1

    chisq = ((fm - 0.2888 * N) ** 2) / (0.2888 * N)
    chisq += ((fm1 - 0.5776 * N) ** 2) / (0.5776 * N)
    chisq += ((rest - 0.1336 * N) ** 2) / (0.1336 * N)
    p = math.exp(-chisq / 2.0)
    return [p, p >= 0.01]

def discrete_fourier_transform_test(binary):
    n = binary.n
    if n < 1000:
        return [0.0, False]
    bits = 2 * binary.unpacked.astype(np.float64) - 1
    s = np.fft.fft(bits)
    modulus = np.abs(s[:n // 2])
    tau = math.sqrt(math.log(1.0 / 0.05) * n)
    n0 = 0.95 * n / 2.0
    n1 = np.sum(modulus < tau)
    d = (n1 - n0) / math.sqrt(n * 0.95 * 0.05 / 4.0)
    p = math.erfc(abs(d) / math.sqrt(2.0))
    return [p, p >= 0.01]

def maurers_universal_test(binary):
    n = binary.n
    L = 5
    if n >= 387840: L = 6
    if n >= 904960: L = 7
    if n >= 2068480: L = 8
    if n >= 4654080: L = 9
    if n >= 10342400: L = 10
    if n >= 22753280: L = 11
    if n >= 49643520: L = 12
    if n >= 107560960: L = 13
    if n >= 231669760: L = 14
    if n >= 496435200: L = 15
    if n >= 1059061760: L = 16
    if L < 6:
        return [0.0, False]

    _var = [2.954, 3.125, 3.238, 3.311, 3.356, 3.384, 3.401, 3.410, 3.416, 3.419, 3.421]
    _EV = [5.2177052, 6.1962507, 7.1836656, 8.1764248, 9.1723243, 10.170032, 11.168765,
           12.168070, 13.167693, 14.167488, 15.167379]
    var = _var[L - 6]
    EV = _EV[L - 6]

    Q = 10 * (2 ** L)
    K = (n // L) - Q
    if K <= 0:
        return [0.0, False]

    bits = binary.unpacked[:(Q + K) * L]
    blocks = bits.reshape(-1, L)
    powers = 2 ** np.arange(L - 1, -1, -1, dtype=np.uint32)
    repacked = np.dot(blocks, powers)
    initSeg = repacked[:Q]
    testSeg = repacked[Q:]

    last_occurrence = np.zeros(2 ** L, dtype=np.int64)
    for i, val in enumerate(initSeg):
        last_occurrence[val] = i + 1

    distances = []
    for i, val in enumerate(testSeg):
        if last_occurrence[val] > 0:
            distances.append(i + Q + 1 - last_occurrence[val])
        last_occurrence[val] = i + Q + 1

    if len(distances) == 0:
        return [0.0, False]

    log_sum = np.sum(np.log2(distances, dtype=np.float64))
    fn = log_sum / len(distances)
    c = 0.7 - 0.8 / L + (4 + 32 / L) * pow(K, -3 / L) / 15
    sigma = c * math.sqrt(var / K)
    if sigma == 0:
        return [0.0, False]
    stat = abs(fn - EV) / (math.sqrt(2) * sigma)
    p = math.erfc(stat)
    return [p, p >= 0.01]

def cumulative_sums_test(binary, mode=0):
    if binary.n < 100:
        return [0.0, False]
    bits = 2 * binary.unpacked.astype(np.int8) - 1
    css = np.cumsum(bits, dtype=np.int32)
    z = float(np.max(np.abs(css)))
    if z == 0:
        return [1.0, True]
    n = float(binary.n)
    start1 = int(((-n / z) + 1) / 4)
    end1 = int(((n / z) - 1) / 4)
    start2 = int(((-n / z) - 3) / 4)
    end2 = int(((n / z) - 1) / 4)

    def compute_term(k, i1, i2):
        t1 = ((4 * k + i1) * z) / math.sqrt(n)
        t2 = ((4 * k + i2) * z) / math.sqrt(n)
        return norm.cdf(t1) - norm.cdf(t2)

    s1 = sum(compute_term(k, 1, -1) for k in range(start1, end1 + 1))
    s2 = sum(compute_term(k, 3, 1) for k in range(start2, end2 + 1))
    p = 1.0 - s1 + s2
    p = max(0.0, min(1.0, p))
    return [p, p >= 0.01]

def random_excursion_test(binary):
    bits = 2 * binary.unpacked.astype(np.int8) - 1
    s = np.cumsum(bits, dtype=np.int32)
    s = np.concatenate(([0], s, [0]))
    zcrosses = np.where(s == 0)[0]
    if len(zcrosses) < 2:
        return [(0.0, False)] * 9
    J = len(zcrosses) - 1
    if J < 500:
        return [(0.0, False)] * 9

    def get_probability(x, k):
        x = abs(x - 4)
        if x == 0:
            return 0.0
        if k == 0:
            pi = 1.0 - 1.0 / (2.0 * x)
        elif k >= 5:
            pi = (1.0 / (2.0 * x)) * ((1.0 - 1.0 / (2.0 * x)) ** 4)
        else:
            pi = (1.0 / (4.0 * x * x)) * ((1.0 - 1.0 / (2.0 * x)) ** (k - 1))
        return pi

    states = np.zeros((9, 6), dtype=np.int32)
    for i in range(len(zcrosses) - 1):
        cycle = s[zcrosses[i]:zcrosses[i + 1] + 1]
        for state in range(-4, 5):
            count = np.sum(cycle == state)
            count = min(count, 5)
            states[state + 4, count] += 1

    results = []
    for x in range(9):
        if x == 4:
            results.append((0.0, False))
            continue
        chisq = 0.0
        for k in range(6):
            prob = get_probability(x, k)
            expected = J * prob
            if expected >= 5:
                chisq += ((float(states[x, k]) - expected) ** 2) / expected
        p = ss.gammaincc(2.5, chisq / 2.0)
        results.append((p, p >= 0.01))

    return results

def random_excursion_variant_test(binary):
    bits = 2 * binary.unpacked.astype(np.int8) - 1
    s = np.cumsum(bits, dtype=np.int32)
    J = float(np.sum(s == 0) + 1)
    if J < 500:
        return [(0.0, False)] * 18

    s_filtered = s[(s >= -9) & (s <= 9)]
    if len(s_filtered) == 0:
        return [(0.0, False)] * 18

    results = []
    for state in range(-9, 10):
        if state == 0:
            continue
        count = np.sum(s_filtered == state)
        denominator = 2.0 * J * (4.0 * abs(float(state)) - 2.0)
        if denominator <= 0:
            results.append((0.0, False))
            continue
        numerator = abs(float(count) - J)
        p = math.erfc(numerator / math.sqrt(denominator))
        results.append((p, p >= 0.01))

    while len(results) < 18:
        results.append((0.0, False))

    return results[:18]

def shannon_entropy_bits(binary):
    if binary.n == 0:
        return 0.0
    p1 = binary.ones_count / binary.n
    p0 = 1.0 - p1
    eps = 1e-12
    H = 0.0
    if p0 > eps:
        H -= p0 * np.log2(p0)
    if p1 > eps:
        H -= p1 * np.log2(p1)
    return H

def byte_entropy(binary):
    if len(binary.packed) == 0:
        return 0.0
    counts = binary.byte_counts[binary.byte_counts > 0]
    probs = counts / counts.sum()
    return entropy(probs, base=2)

def byte_histogram_features(binary):
    if len(binary.packed) == 0:
        return 0.0, 0.0, 0.0, 0.0
    counts = binary.byte_counts.astype(np.float64)
    probs = counts / counts.sum()
    expected = counts.sum() / 256.0
    chi2 = np.sum((counts - expected) ** 2 / (expected + 1e-12))
    max_p = probs.max()
    std_p = probs.std()
    mean_p = probs.mean()
    cv = std_p / (mean_p + 1e-12)
    return chi2, max_p, std_p, cv

def run_length_features(binary):
    bits = binary.unpacked
    if len(bits) == 0:
        return 0.0, 0.0, 0.0, 0.0
    runs = []
    current = bits[0]
    length = 1
    for b in bits[1:]:
        if b == current:
            length += 1
        else:
            runs.append(length)
            current = b
            length = 1
    runs.append(length)
    runs = np.array(runs, dtype=np.float64)
    run_mean = runs.mean()
    run_std = runs.std()
    run_max = runs.max()
    run_cv = run_std / (run_mean + 1e-12)
    return run_mean, run_std, run_max, run_cv

def autocorrelation_features(binary):
    bits = binary.unpacked.astype(np.int8)
    if len(bits) < 10:
        return 0.0, 0.0, 0.0, 0.0
    x = 2 * bits - 1
    lags = [1, 2, 4, 8]
    acf_values = []
    for lag in lags:
        if len(x) <= lag:
            acf_values.append(0.0)
        else:
            acf = np.dot(x[:-lag], x[lag:]) / (len(x) - lag)
            acf_values.append(float(acf))
    return tuple(acf_values)

def complexity_features(binary):
    bits = binary.unpacked
    if len(bits) == 0:
        return 0.0, 0.0
    n = len(bits)
    complexity = 0
    i = 0
    prefix_dict = set()
    while i < n:
        for j in range(i + 1, min(i + 100, n + 1)):
            substring = tuple(bits[i:j])
            if substring not in prefix_dict:
                prefix_dict.add(substring)
                complexity += 1
                i = j
                break
        else:
            i += 1
    lz_complexity = complexity / (n / np.log2(n + 1) + 1e-12)
    if n >= 8:
        patterns = set()
        for i in range(n - 7):
            pattern = tuple(bits[i:i+8])
            patterns.add(pattern)
        compression_ratio = len(patterns) / (n - 7)
    else:
        compression_ratio = 1.0
    return lz_complexity, compression_ratio

def bit_transition_features(binary):
    bits = binary.unpacked
    if len(bits) < 2:
        return 0.0, 0.0, 0.0
    transitions = np.diff(bits.astype(np.int8))
    zero_to_one = np.sum(transitions == 1)
    one_to_zero = np.sum(transitions == -1)
    total_trans = zero_to_one + one_to_zero
    transition_rate = total_trans / (len(bits) - 1)
    transition_balance = abs(zero_to_one - one_to_zero) / (total_trans + 1e-12)
    p = binary.ones_count / binary.n
    expected_transitions = 2 * p * (1 - p) * (binary.n - 1)
    transition_deviation = abs(total_trans - expected_transitions) / (expected_transitions + 1e-12)
    return transition_rate, transition_balance, transition_deviation

def spectral_features(binary):
    bits = binary.unpacked
    if len(bits) < 100:
        return 0.0, 0.0, 0.0
    x = 2 * bits.astype(np.float64) - 1
    fft_vals = np.fft.fft(x)
    power_spectrum = np.abs(fft_vals[:len(fft_vals)//2])**2
    ps_norm = power_spectrum / (power_spectrum.sum() + 1e-12)
    spectral_entropy = entropy(ps_norm + 1e-12, base=2)
    max_power = power_spectrum.max()
    mean_power = power_spectrum.mean()
    dominant_freq_ratio = max_power / (mean_power + 1e-12)
    geometric_mean = np.exp(np.mean(np.log(power_spectrum + 1e-12)))
    arithmetic_mean = np.mean(power_spectrum)
    spectral_flatness = geometric_mean / (arithmetic_mean + 1e-12)
    return spectral_entropy, dominant_freq_ratio, spectral_flatness

def local_randomness_features(binary):
    bits = binary.unpacked
    n = len(bits)
    if n < 1000:
        return 0.0, 0.0
    block_size = min(500, n // 10)
    n_blocks = n // block_size
    block_entropies = []
    block_ones_ratios = []
    for i in range(n_blocks):
        block = bits[i*block_size:(i+1)*block_size]
        ones = np.sum(block)
        p1 = ones / len(block)
        p0 = 1 - p1
        if 0 < p0 < 1:
            H = -(p0 * np.log2(p0) + p1 * np.log2(p1))
        else:
            H = 0.0
        block_entropies.append(H)
        block_ones_ratios.append(p1)
    entropy_variance = np.var(block_entropies)
    ones_ratio_variance = np.var(block_ones_ratios)
    return entropy_variance, ones_ratio_variance

WINDOW_SIZE = 1024
WINDOW_STEP = 512
DIFF_BLOCK_SIZE = 128

@jit(nopython=True, cache=True)
def fast_entropy(window):
    """Vectorized entropy calculation"""
    p1 = np.mean(window)
    if p1 <= 0 or p1 >= 1:
        return 0.0
    p0 = 1 - p1
    return -(p0 * np.log2(p0) + p1 * np.log2(p1))

@jit(nopython=True, cache=True)
def fast_run_lengths(bitstream):
    """Optimized run length calculation"""
    if len(bitstream) < 2:
        return 0.0, 0.0
    
    diffs = np.diff(bitstream.astype(np.int8))
    transitions = np.where(diffs != 0)[0]
    
    if len(transitions) < 2:
        return 0.0, 0.0
    
    runs = np.diff(transitions).astype(np.float64)
    return np.mean(runs), np.var(runs)

# @jit(nopython=True, cache=True)
# def sliding_window_features_fast(bitstream):
#     """Optimized sliding window with numba"""
#     n_windows = (len(bitstream) - WINDOW_SIZE) // WINDOW_STEP + 1
#     entropies = np.zeros(n_windows)
    
#     for i in range(n_windows):
#         start = i * WINDOW_STEP
#         window = bitstream[start:start + WINDOW_SIZE]
#         entropies[i] = fast_entropy(window)
    
#     run_mean, run_var = fast_run_lengths(bitstream)
    
#     return (
#         np.mean(entropies),
#         np.var(entropies),
#         0.0 if len(entropies) < 3 else skew(entropies),  # skew computed outside numba
#         run_mean,
#         run_var
#     )

@jit(nopython=True, cache=True)
def markov_features_fast(bitstream):
    """Optimized Markov transition matrix"""
    transitions = np.zeros((2, 2), dtype=np.float64)
    
    for i in range(len(bitstream) - 1):
        transitions[bitstream[i], bitstream[i + 1]] += 1
    
    # Row normalization
    row_sums = transitions.sum(axis=1)
    for i in range(2):
        if row_sums[i] > 0:
            transitions[i] = transitions[i] / row_sums[i]
    
    # Flatten and calculate entropy
    probs = transitions.flatten()
    ent = 0.0
    for p in probs:
        if p > 1e-12:
            ent -= p * np.log2(p)
    
    return transitions[0, 0], transitions[0, 1], transitions[1, 0], transitions[1, 1], ent

def spectral_features_fast(bitstream):
    """Optimized spectral features using FFT"""
    # Downsample if too large
    if len(bitstream) > 100000:
        step = len(bitstream) // 50000
        signal = (bitstream[::step] * 2 - 1).astype(np.float32)
    else:
        signal = (bitstream * 2 - 1).astype(np.float32)
    
    # Use FFT instead of welch for speed
    fft_vals = np.abs(rfft(signal))
    freqs = rfftfreq(len(signal), d=1.0)
    
    psd = fft_vals ** 2
    psd_sum = np.sum(psd)
    
    if psd_sum < 1e-12:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    
    psd_norm = psd / psd_sum
    
    # Spectral features
    centroid = np.sum(freqs * psd_norm)
    flatness = np.exp(np.mean(np.log(psd + 1e-12))) / (np.mean(psd) + 1e-12)
    energy = psd_sum
    
    low_mask = freqs < 0.1
    high_mask = freqs > 0.4
    
    low_energy = np.sum(psd[low_mask]) if np.any(low_mask) else 0.0
    high_energy = np.sum(psd[high_mask]) if np.any(high_mask) else 0.0
    
    return centroid, flatness, energy, low_energy, high_energy

def compression_features_fast(bitstream):
    """Optimized compression - sample for large streams"""
    # Sample if too large (compression is slow)
    if len(bitstream) > 100000:
        step = len(bitstream) // 50000
        sample = bitstream[::step]
    else:
        sample = bitstream
    
    byte_data = np.packbits(sample).tobytes()
    compressed = zlib.compress(byte_data, level=1)  # Fast compression level
    
    return len(compressed) / len(byte_data)

@jit(nopython=True, cache=True)
def differential_features_fast(bitstream):
    """Optimized differential Hamming distance"""
    n_blocks = (len(bitstream) - 2 * DIFF_BLOCK_SIZE) // DIFF_BLOCK_SIZE
    
    if n_blocks < 1:
        return 0.0, 0.0
    
    hamming = np.zeros(n_blocks)
    
    for i in range(n_blocks):
        start = i * DIFF_BLOCK_SIZE
        b1 = bitstream[start:start + DIFF_BLOCK_SIZE]
        b2 = bitstream[start + DIFF_BLOCK_SIZE:start + 2 * DIFF_BLOCK_SIZE]
        hamming[i] = np.mean(b1 ^ b2)
    
    return np.mean(hamming), np.var(hamming)

def flatten_test_results(row):
    flattened = {}
    
    # Simple NIST tests - these match your column names
    simple_tests = [
        'bits_testing', 
        'frequency_within_block', 
        'runs',
        'longest_run_within_block', 
        'binary_matrix_rank',
        'discrete_fourier_transform', 
        'maurers_universal_statistical',
        'cumulative_sums'
    ]
    
    for test in simple_tests:
        if test in row:
            result = row[test]
            flattened[f'{test}_pvalue'] = float(result[0])
            flattened[f'{test}_pass'] = int(result[1])
    
    # Random excursions - your CSV has states from -4 to 4
    if 'random_excursions' in row:
        results = row['random_excursions']
        # Your CSV shows states -4 through 4
        for i, (p_val, success) in enumerate(results[:9]):  # 9 states from -4 to 4
            state = i - 4  # This gives -4, -3, -2, -1, 0, 1, 2, 3, 4
            flattened[f'random_excursions_state{state}_pvalue'] = float(p_val)
            flattened[f'random_excursions_state{state}_pass'] = int(success)

    # Random excursions variant - your CSV has states -9 through 9 (excluding 0)
    if 'random_excursions_variant' in row:
        results = row['random_excursions_variant']
        states = list(range(-9, 0)) + list(range(1, 10))  # -9 to -1, 1 to 9
        for i, (p_val, success) in enumerate(results[:18]):  # 18 states
            state = states[i]
            flattened[f'random_excursions_variant_state{state}_pvalue'] = float(p_val)
            flattened[f'random_excursions_variant_state{state}_pass'] = int(success)
    
    # Feature mapping - make sure these match your CSV columns exactly
    feature_mapping = {
        'entropy_bits': 'entropy_bits',
        'entropy_bytes': 'entropy_bytes',
        'chi2_bytes': 'chi2_bytes',
        'max_p_byte': 'max_p_byte',
        'std_p_byte': 'std_p_byte',
        'cv_byte': 'cv_byte',
        'run_mean': 'run_mean',
        'run_std': 'run_std',
        'run_max': 'run_max',
        'run_cv': 'run_cv',
        'acf_lag1': 'acf_lag1',
        'acf_lag2': 'acf_lag2',
        'acf_lag4': 'acf_lag4',
        'acf_lag8': 'acf_lag8',
        'lz_complexity': 'lz_complexity',
        'compression_ratio_x': 'compression_ratio_x',  # Note: your CSV has _x
        'transition_rate': 'transition_rate',
        'transition_balance': 'transition_balance',
        'transition_deviation': 'transition_deviation',
        'spectral_entropy': 'spectral_entropy',
        'dominant_freq_ratio': 'dominant_freq_ratio',
        'spectral_flatness_x': 'spectral_flatness_x',  # Note: your CSV has _x
        'entropy_variance': 'entropy_variance',
        'ones_ratio_variance': 'ones_ratio_variance',
        'block_uniqueness_ratio': 'block_uniqueness_ratio',
        'potential_padding_value': 'potential_padding_value',
        'padding_consistency': 'padding_consistency',
        'mean_block_correlation': 'mean_block_correlation',
        'std_block_correlation': 'std_block_correlation',
        'length_mod_blocksize': 'length_mod_blocksize',
        'last_block_entropy': 'last_block_entropy',
        'first_block_entropy': 'first_block_entropy',
        'prefix_bias_score': 'prefix_bias_score',
        'prefix_std': 'prefix_std',
        'first_byte_is_zero': 'first_byte_is_zero',
        'byte_255_value': 'byte_255_value',
        'chunk64_entropy_mean': 'chunk64_entropy_mean',
        'chunk64_entropy_std': 'chunk64_entropy_std',
        'max_byte_freq': 'max_byte_freq',
        'min_byte_freq': 'min_byte_freq',
        'byte_freq_range': 'byte_freq_range',
        'unusual_byte_count': 'unusual_byte_count',
        'high_bit_ratio': 'high_bit_ratio',
        'low_bit_ratio': 'low_bit_ratio',
        'long_run_count': 'long_run_count',
        'ciphertext_length': 'ciphertext_length',
        'length_category': 'length_category',
        'length_bucket': 'length_bucket',
        'entropy_split_256_first': 'entropy_split_256_first',
        'entropy_split_256_second': 'entropy_split_256_second',
        'entropy_split_256_ratio': 'entropy_split_256_ratio',
        'entropy_split_512_first': 'entropy_split_512_first',
        'entropy_split_512_second': 'entropy_split_512_second',
        'entropy_split_512_ratio': 'entropy_split_512_ratio',
        'entropy_split_768_first': 'entropy_split_768_first',
        'entropy_split_768_second': 'entropy_split_768_second',
        'entropy_split_768_ratio': 'entropy_split_768_ratio',
        'entropy_split_1024_first': 'entropy_split_1024_first',
        'entropy_split_1024_second': 'entropy_split_1024_second',
        'entropy_split_1024_ratio': 'entropy_split_1024_ratio',
        'entropy_split_2048_first': 'entropy_split_2048_first',
        'entropy_split_2048_second': 'entropy_split_2048_second',
        'entropy_split_2048_ratio': 'entropy_split_2048_ratio',
        'kl_divergence_first_second': 'kl_divergence_first_second',
        'chi_square_first_second': 'chi_square_first_second',
        'first_16_zero_count': 'first_16_zero_count',
        'has_asn1_marker': 'has_asn1_marker',
        'first_16_entropy': 'first_16_entropy',
        'divisible_by_small_primes': 'divisible_by_small_primes',
        'first_chunk_bit_density': 'first_chunk_bit_density',
        'length_mod_16': 'length_mod_16',
        'length_mod_32': 'length_mod_32',
        'length_mod_64': 'length_mod_64',
        'sample_id': 'sample_id',
        'win_entropy_mean': 'win_entropy_mean',
        'win_entropy_var': 'win_entropy_var',
        'win_entropy_skew': 'win_entropy_skew',
        'run_length_mean': 'run_length_mean',
        'run_length_var': 'run_length_var',
        'p00': 'p00',
        'p01': 'p01',
        'p10': 'p10',
        'p11': 'p11',
        'transition_entropy': 'transition_entropy',
        'spectral_centroid': 'spectral_centroid',
        'spectral_flatness_y': 'spectral_flatness_y',
        'spectral_energy': 'spectral_energy',
        'low_freq_energy': 'low_freq_energy',
        'high_freq_energy': 'high_freq_energy',
        'compression_ratio_y': 'compression_ratio_y',
        'hamming_mean': 'hamming_mean',
        'hamming_var': 'hamming_var'
    }

    for key, col_name in feature_mapping.items():
        if key in row:
            flattened[col_name] = float(row[key]) if isinstance(row[key], (int, float)) else row[key]
    
    return flattened

@jit(nopython=True, cache=True)
def sliding_window_features_fast(bitstream):
    """Optimized sliding window with numba - returns entropies for skew calculation"""
    n_windows = (len(bitstream) - WINDOW_SIZE) // WINDOW_STEP + 1
    entropies = np.zeros(n_windows)
    
    for i in range(n_windows):
        start = i * WINDOW_STEP
        window = bitstream[start:start + WINDOW_SIZE]
        entropies[i] = fast_entropy(window)
    
    run_mean, run_var = fast_run_lengths(bitstream)
    
    return (
        np.mean(entropies),
        np.var(entropies),
        entropies,  # Return the entropies array
        run_mean,
        run_var
    )

def process_bitstream(bit_stream):
    try:
        # Get the unpacked bits array for Numba functions
        bits = bit_stream.unpacked
        
        nist_results = {
            "bits_testing": monobit_test(bit_stream),
            "frequency_within_block": frequency_within_block_test(bit_stream),
            "runs": runs_test(bit_stream),
            "longest_run_within_block": longest_run_within_block_test(bit_stream),
            "binary_matrix_rank": binary_matrix_rank_test(bit_stream),
            "discrete_fourier_transform": discrete_fourier_transform_test(bit_stream),
            "maurers_universal_statistical": maurers_universal_test(bit_stream),
            "cumulative_sums": cumulative_sums_test(bit_stream),
            "random_excursions": random_excursion_test(bit_stream),
            "random_excursions_variant": random_excursion_variant_test(bit_stream),
        }
        
        H_bits = shannon_entropy_bits(bit_stream)
        H_bytes = byte_entropy(bit_stream)
        chi2_bytes, max_p_byte, std_p_byte, cv_byte = byte_histogram_features(bit_stream)
        run_mean, run_std, run_max, run_cv = run_length_features(bit_stream)
        acf1, acf2, acf4, acf8 = autocorrelation_features(bit_stream)
        lz_complexity, compression_ratio = complexity_features(bit_stream)
        trans_rate, trans_balance, trans_dev = bit_transition_features(bit_stream)
        spec_entropy, dom_freq_ratio, spec_flatness = spectral_features(bit_stream)
        ent_var, ones_var = local_randomness_features(bit_stream)
        
        features = {}
        
        # Sliding window features - using bits (NumPy array)
        win_ent_mean, win_ent_var, entropies, run_len_mean, run_len_var = sliding_window_features_fast(bits)
        
        # Compute skew outside the numba function
        from scipy.stats import skew
        win_ent_skew = skew(entropies) if len(entropies) >= 3 else 0.0
        
        features["win_entropy_mean"] = win_ent_mean
        features["win_entropy_var"] = win_ent_var
        features["win_entropy_skew"] = win_ent_skew
        features["run_length_mean"] = run_len_mean
        features["run_length_var"] = run_len_var
        
        # Markov features - using bits
        p00, p01, p10, p11, trans_ent = markov_features_fast(bits)
        features["p00"] = p00
        features["p01"] = p01
        features["p10"] = p10
        features["p11"] = p11
        features["transition_entropy"] = trans_ent
        
        # Spectral features - using bits
        spec_cent, spec_flat, spec_energy, low_freq, high_freq = spectral_features_fast(bits)
        features["spectral_centroid"] = spec_cent
        features["spectral_flatness_y"] = spec_flat
        features["spectral_energy"] = spec_energy
        features["low_freq_energy"] = low_freq
        features["high_freq_energy"] = high_freq
        
        # Compression features - using bits
        features["compression_ratio_y"] = compression_features_fast(bits)
        
        # Differential features - using bits
        hamming_mean, hamming_var = differential_features_fast(bits)
        features["hamming_mean"] = hamming_mean
        features["hamming_var"] = hamming_var

        result = {
            **nist_results,
            "entropy_bits": H_bits,
            "entropy_bytes": H_bytes,
            "chi2_bytes": chi2_bytes,
            "max_p_byte": max_p_byte,
            "std_p_byte": std_p_byte,
            "cv_byte": cv_byte,
            "run_mean": run_mean,
            "run_std": run_std,
            "run_max": run_max,
            "run_cv": run_cv,
            "acf_lag1": acf1,
            "acf_lag2": acf2,
            "acf_lag4": acf4,
            "acf_lag8": acf8,
            "lz_complexity": lz_complexity,
            "compression_ratio_x": compression_ratio,
            "transition_rate": trans_rate,
            "transition_balance": trans_balance,
            "transition_deviation": trans_dev,
            "spectral_entropy": spec_entropy,
            "dominant_freq_ratio": dom_freq_ratio,
            "spectral_flatness_x": spec_flatness,
            "entropy_variance": ent_var,
            "ones_ratio_variance": ones_var,
            **features
        }

        return flatten_test_results(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
        }


# def process_bitstream(bit_stream):
#     try:
#         # Get the unpacked bits array for Numba functions
#         bits = bit_stream.unpacked
        
#         nist_results = {
#             "bits_testing": monobit_test(bit_stream),
#             "frequency_within_block": frequency_within_block_test(bit_stream),
#             "runs": runs_test(bit_stream),
#             "longest_run_within_block": longest_run_within_block_test(bit_stream),
#             "binary_matrix_rank": binary_matrix_rank_test(bit_stream),
#             "discrete_fourier_transform": discrete_fourier_transform_test(bit_stream),
#             "maurers_universal_statistical": maurers_universal_test(bit_stream),
#             "cumulative_sums": cumulative_sums_test(bit_stream),
#             "random_excursions": random_excursion_test(bit_stream),
#             "random_excursions_variant": random_excursion_variant_test(bit_stream),
#         }
        
#         H_bits = shannon_entropy_bits(bit_stream)
#         H_bytes = byte_entropy(bit_stream)
#         chi2_bytes, max_p_byte, std_p_byte, cv_byte = byte_histogram_features(bit_stream)
#         run_mean, run_std, run_max, run_cv = run_length_features(bit_stream)
#         acf1, acf2, acf4, acf8 = autocorrelation_features(bit_stream)
#         lz_complexity, compression_ratio = complexity_features(bit_stream)
#         trans_rate, trans_balance, trans_dev = bit_transition_features(bit_stream)
#         spec_entropy, dom_freq_ratio, spec_flatness = spectral_features(bit_stream)
#         ent_var, ones_var = local_randomness_features(bit_stream)
        
#         features = {}
        
#         # Sliding window features - using bits (NumPy array)
#         win_ent_mean, win_ent_var, win_ent_skew, run_len_mean, run_len_var = sliding_window_features_fast(bits)
#         features["win_entropy_mean"] = win_ent_mean
#         features["win_entropy_var"] = win_ent_var
#         features["win_entropy_skew"] = win_ent_skew
#         features["run_length_mean"] = run_len_mean
#         features["run_length_var"] = run_len_var
        
#         # Markov features - using bits
#         p00, p01, p10, p11, trans_ent = markov_features_fast(bits)
#         features["p00"] = p00
#         features["p01"] = p01
#         features["p10"] = p10
#         features["p11"] = p11
#         features["transition_entropy"] = trans_ent
        
#         # Spectral features - using bits
#         spec_cent, spec_flat, spec_energy, low_freq, high_freq = spectral_features_fast(bits)
#         features["spectral_centroid"] = spec_cent
#         features["spectral_flatness_y"] = spec_flat
#         features["spectral_energy"] = spec_energy
#         features["low_freq_energy"] = low_freq
#         features["high_freq_energy"] = high_freq
        
#         # Compression features - using bits
#         features["compression_ratio_y"] = compression_features_fast(bits)
        
#         # Differential features - using bits
#         hamming_mean, hamming_var = differential_features_fast(bits)
#         features["hamming_mean"] = hamming_mean
#         features["hamming_var"] = hamming_var

#         result = {
#             **nist_results,
#             "entropy_bits": H_bits,
#             "entropy_bytes": H_bytes,
#             "chi2_bytes": chi2_bytes,
#             "max_p_byte": max_p_byte,
#             "std_p_byte": std_p_byte,
#             "cv_byte": cv_byte,
#             "run_mean": run_mean,
#             "run_std": run_std,
#             "run_max": run_max,
#             "run_cv": run_cv,
#             "acf_lag1": acf1,
#             "acf_lag2": acf2,
#             "acf_lag4": acf4,
#             "acf_lag8": acf8,
#             "lz_complexity": lz_complexity,
#             "compression_ratio_x": compression_ratio,
#             "transition_rate": trans_rate,
#             "transition_balance": trans_balance,
#             "transition_deviation": trans_dev,
#             "spectral_entropy": spec_entropy,
#             "dominant_freq_ratio": dom_freq_ratio,
#             "spectral_flatness_x": spec_flatness,
#             "entropy_variance": ent_var,
#             "ones_ratio_variance": ones_var,
#             **features
#         }

#         return flatten_test_results(result)

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return {
#             "error": str(e),
#         }

def nist_statistical_test(bit_data: str):
    bit_stream = BinaryData(bit_data)   
    nist_dict = process_bitstream(bit_stream)

    if "error" in nist_dict:
        raise RuntimeError(f"Error processing bitstream: {nist_dict['error']}")

    # QUICK ANALYSIS
    print(f"\n✅ nist_dict has {len(nist_dict)} columns")
    print(f"Column names sample (first 10): {list(nist_dict.keys())}")
    
    # Check if it has 185 columns (what your model expects)
    expected_columns = 185
    if len(nist_dict) == expected_columns:
        print(f"✓ Correct number of columns: {len(nist_dict)}")
    else:
        print(f"⚠ WARNING: Expected {expected_columns} columns but got {len(nist_dict)}")
        print(f"Difference: {len(nist_dict) - expected_columns} extra/missing columns")
    
    nist_test_df = pd.DataFrame([nist_dict])
    return feed_nist_data(nist_test_df)



