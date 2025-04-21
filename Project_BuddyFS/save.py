import os
import struct
import argparse
import matplotlib.pyplot as plt
from natsort import natsorted  # 导入 natsort 库


def read_bin_files(input_dir):
    bin_files = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.bin'):
            file_path = os.path.join(input_dir, file_name)
            bin_files.append(file_path)
    return natsorted(bin_files)  # 对文件路径进行自然排序


def visualize_data_blocks(bin_files, output_dir='visualizations'):
    os.makedirs(output_dir, exist_ok=True)

    file_names = []
    non_empty_sizes = []
    empty_sizes = []
    
    # 用于饼图和折线图的数据
    for bin_file in bin_files:
        with open(bin_file, 'rb') as f:
            data = f.read()
            non_empty_size = len(data.strip(b'\x00'))
            empty_size = len(data) - non_empty_size

        file_names.append(os.path.basename(bin_file))
        non_empty_sizes.append(non_empty_size)
        empty_sizes.append(empty_size)

    # 柱状图：非空数据大小与空数据大小
    plt.figure(figsize=(10, 6))
    x = range(len(file_names))
    plt.bar(x, non_empty_sizes, width=0.4, label='Non-Empty Data Size (Bytes)', align='center', alpha=0.7)
    plt.bar(x, empty_sizes, width=0.4, label='Empty Size (Bytes)', align='edge', alpha=0.9)
    plt.xticks(x, file_names, rotation=45, ha='right')
    plt.ylabel("Size (Bytes)")
    plt.title("Data Size Comparison - Bar Chart")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "data_size_comparison_bar_chart.png"))
    plt.show()

    # 饼图：非空数据和空数据比例
    for i, bin_file in enumerate(bin_files):
        plt.figure(figsize=(6, 6))
        labels = ['Non-Empty Data', 'Empty Data']
        sizes = [non_empty_sizes[i], empty_sizes[i]]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#4CAF50', '#FFC107'])
        plt.title(f"Data vs Empty Size for {os.path.basename(bin_file)}")
        plt.savefig(os.path.join(output_dir, f"{os.path.basename(bin_file).replace('.bin', '')}_pie_chart.png"))
        plt.show()

    # 折线图：数据大小和空数据大小趋势
    plt.figure(figsize=(10, 6))
    plt.plot(file_names, non_empty_sizes, marker='o', label='Non-Empty Data Size', color='#4CAF50', linestyle='--')
    plt.plot(file_names, empty_sizes, marker='x', label='Empty Size', color='#FFC107', linestyle='-.')
    plt.xticks(rotation=45, ha='right')  # 调整x轴标签角度
    plt.ylabel("Bytes")
    plt.title("Data Size Trend Across Files")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "data_size_trend_line_chart.png"))
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Visualize data blocks from bin files.")
    parser.add_argument("input_dir", type=str, help="Directory containing the .bin files.")
    parser.add_argument("--output_dir", type=str, default="visualizations", help="Directory to save visualizations.")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    bin_files = read_bin_files(input_dir)
    if not bin_files:
        print("No .bin files found in the specified directory.")
    else:
        print(f"Found {len(bin_files)} binary files to visualize.")
        visualize_data_blocks(bin_files, output_dir)


if __name__ == "__main__":
    main()