import numpy as np


def downcast(df, show_reduction=False):
    original_mem_usage = sum(df.memory_usage() / 10**6)
    for c in df.select_dtypes(int).columns:
        # Positive integers
        if df[c].min() > 0:
            if df[c].max() < 255:
                df[c] = df[c].astype(np.uint8)
            elif df[c].max() < 65535:
                df[c] = df[c].astype(np.uint16)
            elif df[c].max() < 4294967295:
                df[c] = df[c].astype(np.uint32)
            else:
                df[c] = df[c].astype(np.uint64)
        # Negative integers
        else:
            if df[c].max() < 127 and df[c].min() > -127:
                df[c] = df[c].astype(np.int8)
            elif df[c].max() < 32767 and df[c].min() > -32767:
                df[c] = df[c].astype(np.int16)
            elif df[c].max() < 2147483648 and df[c].min() > -2147483648:
                df[c] = df[c].astype(np.int32)
            else:
                df[c] = df[c].astype(np.int64)

        # Downcast all floats to 32 bits (unlikely to need more precision than that)
        for c in df.select_dtypes(float).columns:
            df[c] = df[c].astype(np.float32)

    if show_reduction:
        reduced_mem_usage = sum(df.memory_usage() / 10**6)
        reduced_mem_usage_pct = 100 * (1 - reduced_mem_usage / original_mem_usage)
        print(f'{original_mem_usage:.2f}MB -> {reduced_mem_usage:.2f}MB ({reduced_mem_usage_pct:.2f}% reduction)')
    return df