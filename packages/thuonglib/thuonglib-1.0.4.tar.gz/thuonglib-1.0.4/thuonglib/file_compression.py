__all__ = ["encode_bytes", "decode_bytes", "compress_file_1", "decompress_file_1"]

import heapq
import struct
from collections import Counter
import math

class Node:
    __slots__ = ("symbol","weight","left","right")
    def __init__(self, symbol=None, weight=0, left=None, right=None):
        self.symbol = symbol  # None for internal nodes
        self.weight = weight
        self.left = left
        self.right = right
    def is_leaf(self):
        return self.symbol is not None

def build_frequency_table(data: bytes):
    freqs = [0]*256
    counter = Counter(data)
    for b, c in counter.items():
        freqs[b] = c
    return freqs

def build_huffman_tree(freqs):
    # freqs: list of 256 non-negative ints
    heap = []
    unique_id = 0
    for sym, f in enumerate(freqs):
        if f > 0:
            node = Node(symbol=sym, weight=f)
            heapq.heappush(heap, (f, unique_id, node))
            unique_id += 1
    # Edge case: empty input
    if not heap:
        return None
    # Edge case: only one symbol -> create a dummy sibling so we get a tree
    if len(heap) == 1:
        f, uid, only = heapq.heappop(heap)
        dummy = Node(symbol=None, weight=0)
        parent = Node(symbol=None, weight=f+0, left=only, right=dummy)
        return parent
    while len(heap) > 1:
        f1, _, n1 = heapq.heappop(heap)
        f2, _, n2 = heapq.heappop(heap)
        parent = Node(symbol=None, weight=f1+f2, left=n1, right=n2)
        heapq.heappush(heap, (parent.weight, unique_id, parent))
        unique_id += 1
    return heapq.heappop(heap)[2]

def build_codes_from_tree(root):
    codes = {}
    if root is None:
        return codes
    # If tree root is leaf (single-symbol case), assign code "0"
    if root.is_leaf():
        codes[root.symbol] = "0"
        return codes
    def dfs(node, path):
        if node.is_leaf():
            codes[node.symbol] = path or "0"  # safety: never empty
            return
        if node.left: dfs(node.left, path + "0")
        if node.right: dfs(node.right, path + "1")
    dfs(root, "")
    return codes

def encode_bytes(data: bytes) -> bytes:
    # Build freq table and header
    freqs = build_frequency_table(data)
    root = build_huffman_tree(freqs)
    if root is None:
        # empty input: header with zero valid bits, zero freqs, no payload
        header = b'HUF1' + bytes([0]) + struct.pack('>256Q', *([0]*256))
        return header

    codes = build_codes_from_tree(root)
    # Bit-pack codes into bytes
    out_bytes = bytearray()
    cur_byte = 0
    bits_filled = 0  # number of bits currently in cur_byte (0..7)
    for b in data:
        code = codes[b]
        for bit_char in code:
            bit = 1 if bit_char == '1' else 0
            cur_byte = (cur_byte << 1) | bit
            bits_filled += 1
            if bits_filled == 8:
                out_bytes.append(cur_byte)
                cur_byte = 0
                bits_filled = 0
    # handle remaining bits
    if bits_filled == 0:
        valid_bits = 8 if len(out_bytes) > 0 else 0  # if there is at least one output byte, it's full
    else:
        # pad right (least-significant side) with zeros by shifting left
        cur_byte = cur_byte << (8 - bits_filled)
        out_bytes.append(cur_byte)
        valid_bits = bits_filled

    # build header: magic + valid_bits + 256*Q frequencies
    header = b'HUF1' + bytes([valid_bits]) + struct.pack('>256Q', *freqs)
    return header + bytes(out_bytes)

def decode_bytes(blob: bytes) -> bytes:
    if len(blob) < 5 + 256*8:
        # Could be empty input header or invalid
        if blob.startswith(b'HUF1') and len(blob) == 4 + 1 + 256*8:
            valid_bits = blob[4]
            if valid_bits == 0:
                return b''
        raise ValueError("Invalid or corrupted blob (too short)")
    magic = blob[:4]
    if magic != b'HUF1':
        raise ValueError("Not a Huffman blob (bad magic)")
    valid_bits = blob[4]
    freqs = list(struct.unpack('>256Q', blob[5:5+256*8]))
    payload = blob[5+256*8:]
    # empty input case
    if valid_bits == 0 and len(payload) == 0:
        return b''
    root = build_huffman_tree(freqs)
    if root is None:
        return b''
    if len(payload) == 0:
        return b''
    # iterate bits left-to-right in each byte (most significant bit first)
    out = bytearray()
    node = root
    bits_processed = 0
    for i, byte in enumerate(payload):
        # determine how many valid bits in this byte
        if i == len(payload) - 1:
            if valid_bits == 0:
                bits_in_this_byte = 0
            else:
                bits_in_this_byte = valid_bits
        else:
            bits_in_this_byte = 8
        for bit_index in range(bits_in_this_byte):
            # take bit from MSB to LSB
            shift = 7 - bit_index
            bit = (byte >> shift) & 1
            node = node.right if bit == 1 else node.left
            if node is None:
                raise ValueError("Decoding error: walked to None")
            if node.is_leaf():
                out.append(node.symbol)
                node = root
            bits_processed += 1
    return bytes(out)

def entropy_from_freqs(freqs: list) -> float:
    """
    Tính entropy H = -sum p_i log2 p_i (bits per symbol).
    freqs: list 256 tần suất (ints).
    """
    total = sum(freqs)
    if total == 0:
        return 0.0
    H = 0.0
    for f in freqs:
        if f > 0:
            p = f / total
            H -= p * math.log2(p)
    return H

def bits_per_symbol(freqs: list, codes: dict) -> float:
    """
    Tính chiều dài mã trung bình (bits/symbol) theo bảng code hiện có.
    codes: dict mapping symbol(int) -> code string of '0'/'1'.
    """
    total = sum(freqs)
    if total == 0:
        return 0.0
    s = 0
    for sym, f in enumerate(freqs):
        if f > 0:
            code = codes.get(sym)
            if code is None:
                raise ValueError(f"No code for symbol {sym}")
            s += f * len(code)
    s += 16_424
    return s / total

def rated(average_bits: float, entropy: float, Original_size: int, Compressed_size: int) -> tuple:
    ratio_bits = average_bits / entropy
    ratio_compressed = Compressed_size / Original_size
    return average_bits, entropy, ratio_bits, ratio_compressed

def compress_file_1(input_file: str):
    with open(input_file, "rb") as f:
        data = f.read()
    compressed = encode_bytes(data)
    if decode_bytes(compressed) == data:
        print("\nCompression successful: decoded matches original data.")
        average_bits = bits_per_symbol(build_frequency_table(data), build_codes_from_tree(build_huffman_tree(build_frequency_table(data))))
        entropy = entropy_from_freqs(build_frequency_table(data))
        Original_size = len(data)
        Compressed_size = len(compressed)
        average_bits, entropy, ratio_bits, ratio_compressed = rated(average_bits, entropy, Original_size, Compressed_size)
        del data  # free memory
        print(f"\nAverage bits per symbol: {average_bits:.3f}")
        print(f"\nEntropy: {entropy:.3f} bits/symbol")
        print(f"\nCompression ratio (bits/symbol): {ratio_bits:.3f}")
        print(f"\nCompression ratio (compressed/original): {ratio_compressed:.3f}")
    output_file = input_file + ".huf"
    with open(output_file, "wb") as f:
        f.write(compressed)

def decompress_file_1(input_file: str):
    with open(input_file, "rb") as f:
        compressed = f.read()
    decompressed = decode_bytes(compressed)
    if decompressed:
        print("\nDecompression successful.")
        output_file = input_file[:-4]
        with open(output_file, "wb") as f:
            f.write(decompressed)
        print(f"\nDecompressed file saved as: {output_file}")
    else:
        print("\nDecompression failed.")