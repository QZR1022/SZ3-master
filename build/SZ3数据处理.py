"""
SZ3 通用压缩脚本
使用方法: 修改下面 CONFIG 中的配置项
"""

import numpy as np
import pysz
from pysz import szConfig, szErrorBoundMode
import os
import time

# ============================================
# 用户配置区 - 只需要改这里
# ============================================

CONFIG = {
    # 1. 输入文件路径 (.raw 格式)
    "input_raw": r"D:/xwechat_files/.../volRendering_H2_3d.raw",

    # 2. 数据维度
    "shape": (512, 512, 144),

    # 3. 数据类型: "float32" 或 "float64"
    "dtype": "float32",

    # 4. 输出文件名前缀（可选，留空则自动用输入文件名）
    "output_prefix": "",  # 例如 "H2" 或留空

    # 5. 压缩参数: 目标 PSNR 值 (越大质量越高，压缩率越低)
    "psnr": 40,  # 可以改成 30, 40, 50 等

    # 6. 输出目录
    "output_dir": "sz3_results",
}


# ============================================
# 以下代码不需要修改
# ============================================

def main():
    # 读取配置
    input_file = CONFIG["input_raw"]
    shape = CONFIG["shape"]
    dtype = np.float32 if CONFIG["dtype"] == "float32" else np.float64
    psnr_target = CONFIG["psnr"]
    output_dir = CONFIG["output_dir"]

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 确定输出文件名前缀
    if CONFIG["output_prefix"]:
        prefix = CONFIG["output_prefix"]
    else:
        prefix = os.path.splitext(os.path.basename(input_file))[0]

    print(f"\n{'=' * 60}")
    print(f"SZ3 压缩")
    print(f"{'=' * 60}")
    print(f"输入文件: {os.path.basename(input_file)}")
    print(f"数据维度: {shape}")
    print(f"数据类型: {CONFIG['dtype']}")
    print(f"目标 PSNR: {psnr_target} dB")
    print(f"{'=' * 60}\n")

    # 加载数据
    print("1. 加载数据...")
    data = np.fromfile(input_file, dtype=dtype)
    data = data.reshape(shape)
    original_size = data.nbytes
    print(f"   形状: {shape}")
    print(f"   大小: {original_size / 1024 / 1024:.2f} MB")
    print(f"   范围: [{data.min():.4f}, {data.max():.4f}]")

    # 配置
    config = szConfig()
    config.errorBoundMode = szErrorBoundMode.PSNR
    config.psnrErrorBound = psnr_target

    # 压缩
    print("\n2. 压缩中...")
    start = time.time()
    compressed, ratio = pysz.sz.compress(data, config)
    compress_time = time.time() - start

    # 解压
    print("3. 解压中...")
    start = time.time()
    decompressed, _ = pysz.sz.decompress(compressed, dtype, shape)
    decompress_time = time.time() - start

    # 验证
    max_err, psnr_actual, nrmse = pysz.sz.verify(data, decompressed)

    # 保存文件
    compressed_file = os.path.join(output_dir, f"{prefix}_psnr{psnr_target}.sz3")
    reconstructed_file = os.path.join(output_dir, f"{prefix}_psnr{psnr_target}_reconstructed.raw")

    with open(compressed_file, "wb") as f:
        f.write(compressed.tobytes())

    decompressed.tofile(reconstructed_file)

    # 输出结果
    print(f"\n{'=' * 60}")
    print(f"✅ 压缩完成!")
    print(f"{'=' * 60}")
    print(f"压缩文件: {compressed_file} ({len(compressed) / 1024 / 1024:.2f} MB)")
    print(f"重建文件: {reconstructed_file}")
    print(f"压缩比: {ratio:.2f}x")
    print(f"压缩时间: {compress_time:.2f} 秒")
    print(f"解压时间: {decompress_time:.2f} 秒")
    print(f"实际 PSNR: {psnr_actual:.2f} dB (目标: {psnr_target})")
    print(f"最大误差: {max_err:.6e}")
    print(f"NRMSE: {nrmse:.6e}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()