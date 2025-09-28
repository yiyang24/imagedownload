import requests
from PIL import Image
import io
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_image(url, headers=None):
    """下载单个图片，处理404错误"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://digicol.dpm.org.cn/'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # 检查是否为404错误
        if response.status_code == 404:
            print(f"图片不存在: {url}")
            return None
            
        response.raise_for_status()
        
        # 验证是否为图片
        if not response.headers.get('content-type', '').startswith('image/'):
            print(f"URL返回的不是图片: {response.headers.get('content-type')}")
            return None
        
        return Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return None

def generate_urls(base_url, matrix_size):
    """根据基URL和矩阵大小生成所有URL"""
    cols, rows = matrix_size  # 列数, 行数
    urls = []
    
    # 从基URL中提取路径部分
    base_path = base_url.rsplit('/', 1)[0]  # 去掉文件名部分
    
    # 正确的行列顺序：列优先，然后行
    for col in range(cols):  # 列循环
        for row in range(rows):  # 行循环
            # 生成新的URL，格式为 col_row.png
            url = f"{base_path}/{col}_{row}.png"
            urls.append(url)
    
    return urls

def download_all_images(urls, max_workers=5):
    """并发下载所有图片"""
    images_dict = {}  # 用字典存储图片，键为(col, row)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有下载任务
        future_to_url = {executor.submit(download_image, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                img = future.result()
                if img is not None:
                    # 从URL中解析出行列坐标
                    filename = url.split('/')[-1]
                    col_str, row_str = filename.replace('.png', '').split('_')
                    col, row = int(col_str), int(row_str)
                    
                    images_dict[(col, row)] = img
                    print(f"成功下载: {url} -> 位置({col}, {row})")
            except Exception as e:
                print(f"处理 {url} 时出错: {e}")
    
    return images_dict

def stitch_images(images_dict, matrix_size):
    """拼接所有图片瓦片，保持原始尺寸"""
    if not images_dict:
        raise ValueError("没有可用的图片进行拼接")
    
    cols, rows = matrix_size
    
    # 获取所有存在的列和行
    existing_cols = sorted(set(col for col, row in images_dict.keys()))
    existing_rows = sorted(set(row for col, row in images_dict.keys()))
    
    print(f"存在的列: {existing_cols}")
    print(f"存在的行: {existing_rows}")
    
    # 计算每列的最大宽度和每行的最大高度
    col_widths = []
    for col in existing_cols:
        widths = [img.size[0] for (c, r), img in images_dict.items() if c == col]
        if widths:
            col_widths.append(max(widths))
        else:
            col_widths.append(0)
    
    row_heights = []
    for row in existing_rows:
        heights = [img.size[1] for (c, r), img in images_dict.items() if r == row]
        if heights:
            row_heights.append(max(heights))
        else:
            row_heights.append(0)
    
    # 计算最终大图的尺寸
    final_width = sum(col_widths)
    final_height = sum(row_heights)
    
    print(f"最终图片尺寸: {final_width} × {final_height}")
    
    # 获取图片模式（假设所有图片模式相同）
    sample_img = next(iter(images_dict.values()))
    
    # 创建空白的大图
    final_image = Image.new(sample_img.mode, (final_width, final_height))
    
    # 按行列顺序粘贴所有瓦片，保持原始尺寸
    for (col, row), img in sorted(images_dict.items()):
        # 计算列和行在现有序列中的索引
        col_idx = existing_cols.index(col)
        row_idx = existing_rows.index(row)
        
        # 计算粘贴位置
        x = sum(col_widths[:col_idx])  # 前面所有列的宽度之和
        y = sum(row_heights[:row_idx])  # 前面所有行的高度之和
        
        # 粘贴到对应位置，不改变原始尺寸
        final_image.paste(img, (x, y))
        print(f"已拼接: 位置({col}, {row}) -> 坐标({x}, {y})，尺寸{img.size}")
    
    return final_image

def main():
    # 输入基URL和矩阵大小
    base_url = "https://shuziwenwu-1259446244.cos.ap-beijing.myqcloud.com/relic/bdd178efd491494f854c52cf2cd001b6/image-bundle/12/0_0.png"
    matrix_size = (2, 5)  # (列数, 行数)
    
    print(f"基URL: {base_url}")
    print(f"矩阵大小: {matrix_size[0]}列 × {matrix_size[1]}行")
    
    # 生成所有URL
    urls = generate_urls(base_url, matrix_size)
    print(f"生成的URL数量: {len(urls)}")
    print("URL列表:")
    for url in urls:
        print(f"  {url}")
    
    print("开始下载图片瓦片...")
    images_dict = download_all_images(urls)
    
    if not images_dict:
        print("没有成功下载任何图片，程序退出")
        return
    
    print(f"\n成功下载 {len(images_dict)} 张图片瓦片")
    print("开始拼接图片...")
    
    try:
        final_image = stitch_images(images_dict, matrix_size)
        
        # 保存最终图片（不进行压缩）
        output_path = "stitched_image.png"
        # 使用最高质量保存，无压缩
        final_image.save(output_path, format='PNG', compress_level=0)
        
        print(f"\n图片拼接完成！")
        print(f"保存路径: {os.path.abspath(output_path)}")
        print(f"最终尺寸: {final_image.size[0]} × {final_image.size[1]} 像素")
        
    except Exception as e:
        print(f"拼接过程中出错: {e}")

if __name__ == "__main__":
    main()