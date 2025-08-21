# 🚀 Puhu vs Pillow Performance Benchmark Report

## 📊 System Information

| Property | Value |
|----------|-------|
| Timestamp | 2025-08-20T22:36:27.807946 |
| Platform | macOS-15.6-x86_64-i386-64bit |
| Processor | i386 |
| Architecture | 64bit |
| Python Version | 3.12.8 |
| CPU Cores | 8 |
| Total Memory | 16.0 GB |
| Pillow Version | 11.3.0 |
| Puhu Version | 0.1.0 |
| Test Iterations | 3 |

## 📈 Performance Summary

| Operation | Puhu Time (ms) | Pillow Time (ms) | Speedup | Puhu Memory (MB) | Pillow Memory (MB) | Winner |
|-----------|----------------|------------------|---------|------------------|--------------------|---------|
| Load File 100X100 Rgb | 0.02 | 0.15 | 9.09x | 0.02 | 0.01 | **Puhu** |
| Load File 100X100 Rgba | 0.01 | 0.14 | 19.98x | 0.00 | 0.00 | **Puhu** |
| Load File 100X100 L | 0.01 | 0.11 | 12.82x | 0.00 | 0.00 | **Puhu** |
| Load File 500X500 Rgb | 0.01 | 0.13 | 18.02x | 0.00 | 0.00 | **Puhu** |
| Load File 500X500 Rgba | 0.01 | 0.10 | 17.40x | 0.00 | 0.00 | **Puhu** |
| Load File 500X500 L | 0.01 | 0.11 | 17.76x | 0.00 | 0.00 | **Puhu** |
| Load File 1000X1000 Rgb | 0.01 | 0.11 | 15.79x | 0.00 | 0.00 | **Puhu** |
| Load File 1000X1000 Rgba | 0.01 | 0.13 | 21.70x | 0.00 | 0.00 | **Puhu** |
| Load File 1000X1000 L | 0.01 | 0.10 | 16.50x | 0.00 | 0.00 | **Puhu** |
| Load File 2000X2000 Rgb | 0.01 | 0.11 | 17.26x | 0.00 | 0.00 | **Puhu** |
| Load File 2000X2000 Rgba | 0.01 | 0.11 | 14.85x | 0.00 | 0.00 | **Puhu** |
| Load File 2000X2000 L | 0.01 | 0.13 | 19.04x | 0.00 | 0.00 | **Puhu** |
| Resize 250X250 Nearest | 4.27 | 11.48 | 2.69x | 1.72 | 0.19 | **Puhu** |
| Resize 250X250 Bilinear | 3.97 | 13.72 | 3.46x | 0.10 | 1.64 | **Puhu** |
| Resize 250X250 Bicubic | 4.55 | 14.97 | 3.29x | 0.99 | 0.00 | **Puhu** |
| Resize 250X250 Lanczos | 5.23 | 16.65 | 3.18x | 0.06 | 0.00 | **Puhu** |
| Resize 500X500 Nearest | 4.43 | 11.35 | 2.56x | 1.30 | 0.00 | **Puhu** |
| Resize 500X500 Bilinear | 4.47 | 14.14 | 3.17x | 0.01 | 0.00 | **Puhu** |
| Resize 500X500 Bicubic | 5.38 | 29.41 | 5.47x | 0.02 | 3.24 | **Puhu** |
| Resize 500X500 Lanczos | 6.29 | 18.27 | 2.91x | 0.01 | 0.00 | **Puhu** |
| Resize 1500X1500 Nearest | 11.13 | 12.21 | ~1x | 5.27 | 0.00 | **Tie** |
| Resize 1500X1500 Bilinear | 11.24 | 21.57 | 1.92x | 0.03 | 1.91 | **Puhu** |
| Resize 1500X1500 Bicubic | 16.46 | 26.20 | 1.59x | 4.74 | 0.00 | **Puhu** |
| Resize 1500X1500 Lanczos | 15.75 | 33.68 | 2.14x | 0.00 | 1.91 | **Puhu** |
| Crop 200X200 | 2.27 | 11.61 | 5.13x | 0.01 | 0.00 | **Puhu** |
| Crop 400X400 | 2.32 | 11.44 | 4.93x | 0.00 | 0.00 | **Puhu** |
| Crop 700X700 | 2.88 | 11.32 | 3.93x | 0.00 | 0.00 | **Puhu** |
| Rotate 90 | 1.20 | 3.51 | 2.93x | 0.00 | 0.00 | **Puhu** |
| Rotate 180 | 1.25 | 3.37 | 2.69x | 0.00 | 0.00 | **Puhu** |
| Rotate 270 | 1.27 | 3.35 | 2.64x | 0.00 | 0.00 | **Puhu** |
| Transpose Flip Left Right | 1.30 | 3.34 | 2.57x | 0.00 | 0.00 | **Puhu** |
| Transpose Flip Top Bottom | 1.22 | 3.14 | 2.58x | 0.00 | 0.00 | **Puhu** |


## 📊 Summary Statistics

### Speed Comparison
- **Puhu faster**: 31 operations
- **Pillow faster**: 0 operations
- **Tied**: 1 operations

### Memory Efficiency
- **Puhu more efficient**: 5 operations
- **Pillow more efficient**: 12 operations
- **Tied**: 15 operations

### Overall Performance
- **Puhu average**: 3.34ms
- **Pillow average**: 6.51ms
- **Overall ratio**: 1.95x

## 💡 Key Findings

### Puhu Strengths
- ✅ **Lazy Loading**: Excellent performance for image loading operations
- ✅ **Memory Efficiency**: Generally uses less memory during loading phase
- ✅ **Fast File Access**: Minimal overhead for file path operations

### Pillow Strengths
- ✅ **Image Processing**: Significantly faster for resize, crop, and transformation operations
- ✅ **Mature Optimization**: Decades of optimization show in processing performance
- ✅ **Native Libraries**: Leverages highly optimized C libraries

### Recommendations

1. **Use Puhu when**:
   - Loading many images but processing few
   - Memory efficiency is critical
   - You need lazy loading benefits
   - Working with simple operations on small images

2. **Use Pillow when**:
   - Heavy image processing workloads
   - Performance-critical resize/crop operations
   - Complex image manipulation pipelines
   - Production systems requiring maximum speed

3. **Hybrid approach**:
   - Use Puhu for loading and simple operations
   - Convert to Pillow for intensive processing when needed
   - Leverage Puhu's batch operations to reduce Python-Rust boundary crossings

---

*Report generated on 2025-08-20T22:36:27.807946*
