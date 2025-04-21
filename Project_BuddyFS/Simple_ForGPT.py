import os
import struct
import hashlib
import argparse
import matplotlib.pyplot as plt
from natsort import natsorted 


def read_partition_table(image_path):
    """
    Reads the GPT partition table from the disk image.
    """
    with open(image_path, 'rb') as f:
        # Read GPT header at LBA 1
        f.seek(512)  # GPT header starts at LBA 1 (sector 1, offset 512 bytes)
        gpt_header = f.read(92)

        # Verify GPT signature
        signature = gpt_header[0:8].decode('utf-8')
        if signature != "EFI PART":
            raise ValueError("Invalid GPT header. Make sure the disk uses GPT partitioning.")

        # Parse GPT header
        partition_entry_lba = struct.unpack("<Q", gpt_header[72:80])[0]  # LBA where partition entries start
        num_partition_entries = struct.unpack("<L", gpt_header[80:84])[0]  # Number of partition entries
        partition_entry_size = struct.unpack("<L", gpt_header[84:88])[0]  # Size of each partition entry

        # Read partition entries
        partitions = []
        f.seek(partition_entry_lba * 512)  # Move to the partition entries
        for i in range(num_partition_entries):
            entry = f.read(partition_entry_size)
            # Each entry is 128 bytes, with GUID, starting LBA, and ending LBA
            start_lba = struct.unpack("<Q", entry[32:40])[0]
            end_lba = struct.unpack("<Q", entry[40:48])[0]
            if start_lba != 0 and end_lba != 0:  # Valid partition
                total_sectors = end_lba - start_lba + 1
                partitions.append({
                    "start_sector": start_lba,
                    "total_sectors": total_sectors
                })
        return partitions


def read_blocks(image_path, start_sector, num_sectors, block_size=512):
    """
    Reads blocks from a specified partition in the disk image.
    """
    blocks = []
    with open(image_path, 'rb') as f:
        f.seek(start_sector * block_size)
        for _ in range(num_sectors):
            block = f.read(block_size)
            if not block:
                break
            blocks.append(block)
    return blocks


def compute_sha256(block):
    """
    Computes the SHA-256 hash of a block.
    """
    hash_obj = hashlib.sha256()
    hash_obj.update(block)
    return hash_obj.hexdigest()


def extract_data_blocks(blocks):
    """
    Separates data blocks and empty blocks, and computes hashes for data blocks.
    """
    data_blocks = []
    empty_blocks = 0
    hashes = []

    for block in blocks:
        if block.strip(b'\x00'):  # Non-empty block
            data_blocks.append(block)
            hashes.append(compute_sha256(block))
        else:
            empty_blocks += 1
    
    return data_blocks, empty_blocks, hashes


def save_blocks(data_blocks, output_dir):
    """
    Saves extracted data blocks to individual files.
    """
    os.makedirs(output_dir, exist_ok=True)
    for i, block in enumerate(data_blocks):
        file_path = os.path.join(output_dir, f'block_{i}.bin')
        with open(file_path, 'wb') as f:
            f.write(block)
        print(f"Block {i} saved to {file_path}")


def visualize_partition_data(partition_data, output_hashes, output_dir="visualizations"):
    """
    Visualizes partition data using matplotlib.
    """
    os.makedirs(output_dir, exist_ok=True)

    partition_ids = [f"Partition {i + 1}" for i in range(len(partition_data))]
    data_block_counts = [p["data_blocks"] for p in partition_data]
    empty_block_counts = [p["empty_blocks"] for p in partition_data]
    total_sizes = [p["total_sectors"] * 512 for p in partition_data]
    used_sizes = [p["data_blocks"] * 512 for p in partition_data]

    for partition_id, hash_list in output_hashes.items():
        print(f"Hashes for {partition_id}:")
        for i, file_hash in enumerate(hash_list):
            print(f"  Block {i}: {file_hash}")

    plt.figure(figsize=(10, 6))
    x = range(len(partition_ids))
    plt.bar(x, total_sizes, width=0.4, label='Total Size (Bytes)', align='center', alpha=0.7)
    plt.bar(x, used_sizes, width=0.4, label='Used Size (Bytes)', align='edge', alpha=0.9)
    plt.xticks(x, partition_ids, rotation=45, ha='right')
    plt.ylabel("Size (Bytes)")
    plt.title("Partition Total and Used Size")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "partition_size_bar_chart.png"))
    plt.show()

    for i, p in enumerate(partition_data):
        plt.figure(figsize=(6, 6))
        labels = ['Data Blocks', 'Empty Blocks']
        sizes = [p["data_blocks"], p["empty_blocks"]]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#4CAF50', '#FFC107'])
        plt.title(f"Partition {i + 1} Block Distribution")
        plt.savefig(os.path.join(output_dir, f"partition_{i + 1}_pie_chart.png"))
        plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(partition_ids, data_block_counts, marker='o', label='Data Blocks', color='#4CAF50', linestyle='--')
    plt.plot(partition_ids, empty_block_counts, marker='x', label='Empty Blocks', color='#FFC107', linestyle='-.')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Number of Blocks")
    plt.title("Data and Empty Block Trend Across Partitions")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "block_trend_line_chart.png"))
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Process GPT disk image and visualize partition data.")
    parser.add_argument("image_path", type=str, help="Path to the GPT disk image file.")
    parser.add_argument("--block_size", type=int, default=512, help="Block size in bytes (default: 512).")
    parser.add_argument("--output_dir", type=str, default="visualizations", help="Directory to save visualizations.")
    args = parser.parse_args()

    image_path = args.image_path
    block_size = args.block_size
    output_dir = args.output_dir

    partitions = read_partition_table(image_path)
    print("Partitions found:")
    partition_data = []
    output_hashes = {}

    for idx, partition in enumerate(partitions):
        print(f"Partition {idx + 1}: Start Sector={partition['start_sector']}, Total Sectors={partition['total_sectors']}")
        start_sector = partition["start_sector"]
        num_sectors = partition["total_sectors"]

        blocks = read_blocks(image_path, start_sector, num_sectors, block_size)
        data_blocks, empty_blocks, hashes = extract_data_blocks(blocks)
        print(f"Partition {idx + 1}: {len(data_blocks)} data blocks, {empty_blocks} empty blocks.")

        partition_data.append({
            "partition_id": idx + 1,
            "start_sector": start_sector,
            "total_sectors": num_sectors,
            "data_blocks": len(data_blocks),
            "empty_blocks": empty_blocks
        })

        output_hashes[f"Partition {idx + 1}"] = hashes

        save_blocks(data_blocks, output_dir=f"{output_dir}/partition_{idx + 1}_blocks")

    visualize_partition_data(partition_data, output_hashes, output_dir=output_dir)


if __name__ == "__main__":
    main()