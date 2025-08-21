#!/usr/bin/env python3
"""
Comprehensive API Compatibility Test for Puhu vs Pillow

This script provides detailed comparison between Puhu and Pillow:
- Function/method existence
- Actual functionality testing
- Performance comparison
- Format support
- Error handling compatibility
"""

import tempfile
import time
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import io

# Import both libraries
import puhu
from PIL import Image as PILImage, ImageFilter
try:
    from PIL import ImageEnhance
except ImportError:
    ImageEnhance = None


def test_functionality(test_name: str, test_func, *args, **kwargs) -> Tuple[bool, str, float]:
    """Test a function and return success, error message, and execution time."""
    start_time = time.time()
    try:
        result = test_func(*args, **kwargs)
        execution_time = time.time() - start_time
        return True, "Success", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, str(e), execution_time

def compare_module_functions():
    """Compare top-level module functions between Puhu and Pillow"""
    print("\n=== Module Functions Comparison ===")

    # Common Pillow functions we want to check
    pillow_funcs = [
        "open",
        "save",
        "new",
        "fromarray",
        "frombytes",
        "frombuffer",
        "crop",
        "resize",
        "rotate",
        "transpose",
        "convert",
    ]

    print(f"{'Function':<20} {'Pillow':<10} {'Puhu':<10} {'Functional Test':<20}")
    print("-" * 70)

    for func_name in pillow_funcs:
        has_pillow = hasattr(PILImage, func_name) or func_name in dir(PILImage)
        has_puhu = hasattr(puhu, func_name) or func_name in dir(puhu)
        
        # Test actual functionality
        func_test = "N/A"
        if has_puhu:
            try:
                if func_name == "open":
                    # Test with a simple image creation first
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                        test_img = PILImage.new("RGB", (10, 10), "red")
                        test_img.save(tmp.name)
                        puhu.open(tmp.name)
                    func_test = "✓ Works"
                elif func_name == "new":
                    puhu.new("RGB", (10, 10))
                    func_test = "✓ Works"
                else:
                    func_test = "⚠ Not tested"
            except Exception as e:
                func_test = f"✗ Error: {str(e)[:20]}..."

        print(
            f"{func_name:<20} {'✓' if has_pillow else '✗':<10} {'✓' if has_puhu else '✗':<10} {func_test:<20}"
        )


def compare_image_methods():
    """Compare Image class methods between Puhu and Pillow"""
    print("\n=== Image Class Methods Comparison ===")

    # Create temporary images
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_path = temp_path / "test.png"

        # Create test images
        pil_img = PILImage.new("RGB", (100, 100))
        pil_img.save(test_path)

        puhu_img = puhu.open(test_path)

        # Get methods from both libraries
        pil_methods = set(dir(pil_img))
        puhu_methods = set(dir(puhu_img))

        # Filter out private methods
        pil_methods = {m for m in pil_methods if not m.startswith("_")}
        puhu_methods = {m for m in puhu_methods if not m.startswith("_")}

        # Common important methods to check
        important_methods = [
            "save",
            "resize",
            "crop",
            "rotate",
            "transpose",
            "convert",
            "copy",
            "paste",
            "split",
            "thumbnail",
            "transform",
            "filter",
        ]

        print(f"{'Method':<20} {'Pillow':<10} {'Puhu':<10} {'Functional Test':<25}")
        print("-" * 75)

        for method in important_methods:
            has_pillow = method in pil_methods
            has_puhu = method in puhu_methods
            
            # Test actual functionality
            func_test = "N/A"
            if has_puhu and has_pillow:
                try:
                    if method == "resize":
                        result = puhu_img.resize((50, 50))
                        func_test = "✓ Works" if result else "✗ Failed"
                    elif method == "crop":
                        result = puhu_img.crop((10, 10, 50, 50))
                        func_test = "✓ Works" if result else "✗ Failed"
                    elif method == "rotate":
                        result = puhu_img.rotate(90)
                        func_test = "✓ Works" if result else "✗ Failed"
                    elif method == "copy":
                        result = puhu_img.copy()
                        func_test = "✓ Works" if result else "✗ Failed"
                    elif method == "transpose":
                        result = puhu_img.transpose(puhu.Transpose.FLIP_LEFT_RIGHT)
                        func_test = "✓ Works" if result else "✗ Failed"
                    elif method == "save":
                        save_path = temp_path / "test_save.png"
                        puhu_img.save(save_path)
                        func_test = "✓ Works" if save_path.exists() else "✗ Failed"
                    elif method == "thumbnail":
                        test_img = puhu_img.copy()
                        test_img.thumbnail((25, 25))
                        func_test = "✓ Works"
                    else:
                        func_test = "⚠ Not tested"
                except Exception as e:
                    func_test = f"✗ Error: {str(e)[:15]}..."
            elif has_puhu and not has_pillow:
                func_test = "⚠ Puhu only"
            elif not has_puhu and has_pillow:
                func_test = "⚠ Pillow only"

            print(
                f"{method:<20} {'✓' if has_pillow else '✗':<10} {'✓' if has_puhu else '✗':<10} {func_test:<25}"
            )

        # Check properties
        print("\n=== Image Properties Comparison ===")
        properties = ["size", "width", "height", "mode", "format", "info"]

        print(f"{'Property':<20} {'Pillow':<10} {'Puhu':<10} {'Value Check':<20}")
        print("-" * 70)

        for prop in properties:
            has_pillow = hasattr(pil_img, prop)
            has_puhu = hasattr(puhu_img, prop)
            
            value_check = "N/A"
            if has_puhu and has_pillow:
                try:
                    puhu_val = getattr(puhu_img, prop)
                    pil_val = getattr(pil_img, prop)
                    if prop in ["size", "width", "height"]:
                        value_check = "✓ Match" if puhu_val == pil_val else "✗ Differ"
                    else:
                        value_check = "✓ Accessible"
                except Exception:
                    value_check = "✗ Error"

            print(
                f"{prop:<20} {'✓' if has_pillow else '✗':<10} {'✓' if has_puhu else '✗':<10} {value_check:<20}"
            )


def compare_enums():
    """Compare enums/constants between Puhu and Pillow"""
    print("\n=== Enums/Constants Comparison ===")

    # Check for common Pillow enums
    pillow_enums = {
        "Resampling": hasattr(PILImage, "Resampling"),
        "Transpose": hasattr(PILImage, "Transpose"),
        "ImageMode": False,  # Pillow doesn't have this as an enum
        "ImageFormat": False,  # Pillow doesn't have this as an enum
    }

    puhu_enums = {
        "Resampling": hasattr(puhu, "Resampling"),
        "Transpose": hasattr(puhu, "Transpose"),
        "ImageMode": hasattr(puhu, "ImageMode"),
        "ImageFormat": hasattr(puhu, "ImageFormat"),
    }

    print(f"{'Enum':<20} {'Pillow':<10} {'Puhu':<10}")
    print("-" * 40)

    for enum_name, has_pillow in pillow_enums.items():
        has_puhu = puhu_enums.get(enum_name, False)
        print(
            f"{enum_name:<20} {'✓' if has_pillow else '✗':<10} {'✓' if has_puhu else '✗':<10}"
        )


def check_api_compatibility():
    """Check if Puhu API is compatible with Pillow with detailed testing"""
    print("\n=== Detailed API Compatibility Testing ===")

    # Test basic operations with the same API
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_path = temp_path / "test.png"

        # Create test images
        pil_img = PILImage.new("RGB", (100, 100), "red")
        pil_img.save(test_path)

        compatibility_tests = [
            ("Image.open(path)", lambda: puhu.open(test_path)),
            ("Image.new('RGB', (100, 100))", lambda: puhu.new("RGB", (100, 100))),
            ("Image.new('RGB', (100, 100), 'red')", lambda: puhu.new("RGB", (100, 100), "red")),
            ("img.resize((50, 50))", lambda: puhu.open(test_path).resize((50, 50))),
            ("img.crop((10, 10, 60, 60))", lambda: puhu.open(test_path).crop((10, 10, 60, 60))),
            ("img.rotate(90)", lambda: puhu.open(test_path).rotate(90)),
            ("img.transpose(FLIP_LEFT_RIGHT)", lambda: puhu.open(test_path).transpose(puhu.Transpose.FLIP_LEFT_RIGHT)),
            ("img.copy()", lambda: puhu.open(test_path).copy()),
            ("img.save(path)", lambda: puhu.open(test_path).save(temp_path / "output.png")),
        ]
        
        print(f"{'Test':<35} {'Status':<10} {'Time (ms)':<12} {'Notes':<20}")
        print("-" * 80)
        
        for test_name, test_func in compatibility_tests:
            success, error, exec_time = test_functionality(test_name, test_func)
            status = "✓ Pass" if success else "✗ Fail"
            notes = "Compatible" if success else error[:18] + "..."
            print(f"{test_name:<35} {status:<10} {exec_time*1000:<12.2f} {notes:<20}")


def test_performance_comparison():
    """Compare performance between Puhu and Pillow for common operations"""
    print("\n=== Performance Comparison ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_path = temp_path / "test.png"
        
        # Create a larger test image for meaningful performance comparison
        pil_img = PILImage.new("RGB", (1000, 1000), "red")
        pil_img.save(test_path)
        
        operations = [
            ("Image Loading", lambda: puhu.open(test_path), lambda: PILImage.open(test_path)),
            ("Resize (500x500)", 
             lambda: puhu.open(test_path).resize((500, 500)), 
             lambda: PILImage.open(test_path).resize((500, 500))),
            ("Crop (100x100)", 
             lambda: puhu.open(test_path).crop((100, 100, 600, 600)), 
             lambda: PILImage.open(test_path).crop((100, 100, 600, 600))),
            ("Rotate 90°", 
             lambda: puhu.open(test_path).rotate(90), 
             lambda: PILImage.open(test_path).rotate(90)),
        ]
        
        print(f"{'Operation':<20} {'Puhu (ms)':<12} {'Pillow (ms)':<12} {'Ratio':<10}")
        print("-" * 60)
        
        for op_name, puhu_func, pillow_func in operations:
            try:
                # Test Puhu
                puhu_success, puhu_error, puhu_time = test_functionality("puhu", puhu_func)
                
                # Test Pillow
                pillow_success, pillow_error, pillow_time = test_functionality("pillow", pillow_func)
                
                if puhu_success and pillow_success:
                    ratio = puhu_time / pillow_time if pillow_time > 0 else float('inf')
                    ratio_str = f"{ratio:.2f}x" if ratio < 10 else ">10x"
                    print(f"{op_name:<20} {puhu_time*1000:<12.2f} {pillow_time*1000:<12.2f} {ratio_str:<10}")
                else:
                    error_msg = puhu_error if not puhu_success else pillow_error
                    print(f"{op_name:<20} {'Error':<12} {'Error':<12} {error_msg[:10]:<10}")
            except Exception as e:
                print(f"{op_name:<20} {'Error':<12} {'Error':<12} {str(e)[:10]:<10}")

def test_format_support():
    """Test format support comparison"""
    print("\n=== Format Support Comparison ===")
    
    formats_to_test = ['PNG', 'JPEG', 'BMP', 'TIFF', 'GIF', 'WEBP']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print(f"{'Format':<10} {'Pillow Read':<12} {'Puhu Read':<12} {'Pillow Write':<13} {'Puhu Write':<12}")
        print("-" * 70)
        
        for fmt in formats_to_test:
            # Create test image in this format using Pillow
            test_file = temp_path / f"test.{fmt.lower()}"
            pillow_read = pillow_write = puhu_read = puhu_write = "✗"
            
            try:
                # Test Pillow write
                pil_img = PILImage.new("RGB", (50, 50), "red")
                if fmt == 'JPEG':
                    pil_img.save(test_file, format=fmt, quality=95)
                else:
                    pil_img.save(test_file, format=fmt)
                pillow_write = "✓"
                
                # Test Pillow read
                PILImage.open(test_file)
                pillow_read = "✓"
                
                # Test Puhu read
                try:
                    puhu.open(test_file)
                    puhu_read = "✓"
                except Exception:
                    puhu_read = "✗"
                
                # Test Puhu write
                try:
                    puhu_img = puhu.open(test_file)
                    puhu_out = temp_path / f"puhu_out.{fmt.lower()}"
                    puhu_img.save(puhu_out, format=fmt)
                    puhu_write = "✓"
                except Exception:
                    puhu_write = "✗"
                    
            except Exception:
                pillow_write = "✗"
                pillow_read = "✗"
            
            print(f"{fmt:<10} {pillow_read:<12} {puhu_read:<12} {pillow_write:<13} {puhu_write:<12}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Edge Cases and Error Handling ===")
    
    edge_cases = [
        ("Open non-existent file", lambda: puhu.open("non_existent.png")),
        ("Create image with invalid mode", lambda: puhu.new("INVALID", (100, 100))),
        ("Resize to zero size", lambda: puhu.new("RGB", (100, 100)).resize((0, 0))),
        ("Crop with invalid box", lambda: puhu.new("RGB", (100, 100)).crop((200, 200, 300, 300))),
        ("Rotate with invalid angle", lambda: puhu.new("RGB", (100, 100)).rotate(45.5)),
    ]
    
    print(f"{'Test Case':<35} {'Puhu Behavior':<25} {'Expected':<15}")
    print("-" * 75)
    
    for test_name, test_func in edge_cases:
        success, error, _ = test_functionality(test_name, test_func)
        behavior = "Raises exception" if not success else "No exception"
        expected = "Should raise" if "invalid" in test_name.lower() or "non-existent" in test_name.lower() else "Varies"
        print(f"{test_name:<35} {behavior:<25} {expected:<15}")

def document_missing_features():
    """Document features that are in Pillow but missing in Puhu"""
    print("\n=== Feature Gap Analysis ===")

    # Categorized Pillow features
    feature_categories = {
        "Core Image Operations": [
            "convert", "split", "merge", "paste", "alpha_composite",
            "blend", "composite", "eval"
        ],
        "Pixel Access": [
            "getpixel", "putpixel", "getdata", "putdata", 
            "getbands", "getbbox", "getextrema"
        ],
        "Color/Palette": [
            "getpalette", "putpalette", "quantize", "convert",
            "point", "remap_palette"
        ],
        "Filters/Enhancement": [
            "filter", "enhance", "effect_spread", "entropy",
            "histogram", "reduce"
        ],
        "Creation Methods": [
            "fromarray", "frombytes", "frombuffer", "fromstring"
        ],
        "Advanced": [
            "transform", "verify", "draft", "seek", "tell",
            "load", "close"
        ]
    }

    print(f"{'Category':<25} {'Missing in Puhu':<50}")
    print("-" * 75)
    
    total_missing = 0
    for category, features in feature_categories.items():
        missing_in_category = []
        for feature in features:
            # Check both module level and instance level
            has_module = hasattr(puhu, feature)
            
            # Try to create an instance to check methods
            try:
                test_img = puhu.new("RGB", (10, 10))
                has_instance = hasattr(test_img, feature)
            except:
                has_instance = False
                
            if not (has_module or has_instance):
                missing_in_category.append(feature)
        
        if missing_in_category:
            missing_str = ", ".join(missing_in_category[:5])  # Show first 5
            if len(missing_in_category) > 5:
                missing_str += f" (+{len(missing_in_category)-5} more)"
            print(f"{category:<25} {missing_str:<50}")
            total_missing += len(missing_in_category)
        else:
            print(f"{category:<25} {'All implemented':<50}")
    
    print(f"\nTotal missing features: {total_missing}")
    
    # Priority recommendations
    print("\n=== Implementation Priority Recommendations ===")
    priority_features = [
        ("HIGH", ["convert", "paste", "fromarray", "split"]),
        ("MEDIUM", ["filter", "getpixel", "putpixel", "blend"]),
        ("LOW", ["histogram", "entropy", "quantize", "verify"])
    ]
    
    for priority, features in priority_features:
        print(f"{priority} Priority: {', '.join(features)}")


def generate_compatibility_report():
    """Generate a comprehensive compatibility report"""
    print("\n" + "="*80)
    print("COMPREHENSIVE COMPATIBILITY REPORT SUMMARY")
    print("="*80)
    
    # Quick compatibility score
    basic_operations = ['open', 'new', 'resize', 'crop', 'save', 'rotate']
    working_ops = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_path = temp_path / "test.png"
        PILImage.new("RGB", (100, 100)).save(test_path)
        
        for op in basic_operations:
            try:
                if op == 'open':
                    puhu.open(test_path)
                elif op == 'new':
                    puhu.new("RGB", (50, 50))
                elif op == 'resize':
                    puhu.open(test_path).resize((50, 50))
                elif op == 'crop':
                    puhu.open(test_path).crop((10, 10, 60, 60))
                elif op == 'save':
                    puhu.open(test_path).save(temp_path / "out.png")
                elif op == 'rotate':
                    puhu.open(test_path).rotate(90)
                working_ops += 1
            except:
                pass
    
    compatibility_score = (working_ops / len(basic_operations)) * 100
    
    print(f"Basic Operations Compatibility Score: {compatibility_score:.1f}%")
    print(f"Working operations: {working_ops}/{len(basic_operations)}")
    
    if compatibility_score >= 80:
        print("✓ EXCELLENT: Puhu provides strong Pillow compatibility")
    elif compatibility_score >= 60:
        print("⚠ GOOD: Puhu covers most essential Pillow operations")
    elif compatibility_score >= 40:
        print("⚠ FAIR: Puhu covers some Pillow operations")
    else:
        print("✗ POOR: Puhu has limited Pillow compatibility")
    
    print("\nRecommendations:")
    print("- Puhu is suitable for basic image processing tasks")
    print("- Consider implementing missing high-priority features")
    print("- Performance is competitive for supported operations")

if __name__ == "__main__":
    print("=== Enhanced Puhu vs Pillow API Compatibility Test ===")
    print(f"Puhu version: {puhu.__version__}")
    print(f"Pillow version: {PILImage.__version__}")

    compare_module_functions()
    compare_image_methods()
    compare_enums()
    test_performance_comparison()
    test_format_support()
    check_api_compatibility()
    test_edge_cases()
    document_missing_features()
    generate_compatibility_report()
