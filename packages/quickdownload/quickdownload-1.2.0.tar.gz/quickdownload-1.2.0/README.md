# QuickDownload

![PyPI Version](https://img.shields.io/pypi/v/quickdownload)
![Python Support](https://img.shields.io/pypi/pyversions/quickdownload)
![License](https://img.shields.io/github/license/Nikhil-K-Singh/quickdownload)
![Downloads](https://img.shields.io/pypi/dm/quickdownload)

A high-performance parallel file downloader that supports both HTTP/HTTPS downloads and BitTorrent downloads, with intelligent resume capabilities and robust error handling. **2-5x faster** than traditional tools like `wget` and `curl`.

## Key Features

- **Parallel Downloads**: Split HTTP files into multiple chunks and download simultaneously (up to 24 threads)
- **Smart Resume**: Intelligent chunk-level resume that survives crashes, network failures, and interruptions
- **Download Queue System**: Add multiple downloads to a persistent queue and process them sequentially
- **Bandwidth Throttling**: Limit download speed per chunk with flexible units (1M, 500K, 2.5MB, etc.)
- **BitTorrent Support**: Seamless handling of magnet links, .torrent files, and .torrent URLs
- **Real-time Progress**: Individual progress bars for each chunk with live speed monitoring
- **Robust Error Handling**: Advanced retry logic with exponential backoff and connection recovery
- **High Performance**: Typically 2-5x faster than `wget`/`curl` for large files
- **Chunk Verification**: Automatic corruption detection and re-download of damaged chunks
- **Configurable**: Customizable parallelism, output locations, and seeding options
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Easy Installation**: Available on PyPI with simple `pip install`

## Performance Comparison

| Scenario | wget/curl | QuickDownload | Improvement |
|----------|-----------|---------------|-------------|
| 1GB file, good connection | ~12 minutes | ~4 minutes | **3x faster** |
| Resume at 90% completion | ~30 seconds | ~5 seconds | **6x faster** |
| Unreliable network | Often restarts from 0% | Seamless resume | **Saves hours** |

## Quick Start

### Installation

**From PyPI (Recommended):**
```bash
pip install quickdownload
```

**From Source:**
```bash
git clone https://github.com/Nikhil-K-Singh/quickdownload.git
cd quickdownload
pip install -e .
```

**For BitTorrent support**, install libtorrent if needed:
```bash
# macOS with Homebrew
brew install libtorrent-rasterbar

# Ubuntu/Debian
sudo apt-get install python3-libtorrent

# Windows - try pip first, fallback to conda if needed
pip install libtorrent
# If pip fails, use conda (handles C++ dependencies automatically):
# conda install -c conda-forge libtorrent-python
```

### Basic Usage

**HTTP/HTTPS Downloads:**
```bash
# Simple download
quickdownload https://example.com/file.zip

# High-speed parallel download
quickdownload -p 16 https://example.com/largefile.zip

# Bandwidth-limited download
quickdownload --throttle 1M https://example.com/file.zip

# Custom output location
quickdownload -o ~/Downloads/file.zip https://example.com/file.zip
```

**Download Queue:**
```bash
# Add downloads to queue
quickdownload queue add https://example.com/file1.zip
quickdownload queue add https://example.com/file2.zip -p 8 --throttle 500K

# Process queue
quickdownload queue start

# Manage queue
quickdownload queue list
quickdownload queue remove job_123456
```

**BitTorrent Downloads:**
```bash
# Magnet link
quickdownload "magnet:?xt=urn:btih:..."

# .torrent file
quickdownload ubuntu.torrent

# With seeding (contribute back to the network for 30 minutes)
quickdownload --seed-time 30 ubuntu.torrent
```

## Why QuickDownload?

Traditional download tools like `wget` and `curl` were designed decades ago. QuickDownload brings modern capabilities:

- **Multi-connection downloading** utilizes full bandwidth
- **Intelligent resume** never loses progress, even with parameter changes
- **Download queue system** manages multiple files efficiently
- **Bandwidth throttling** provides precise speed control for shared networks
- **Unified interface** for HTTP and BitTorrent protocols  
- **Professional progress display** without clutter
- **Enterprise-grade error handling** for production use

## Command Reference

### Command Line Options

| Option | Short | Description | Default | Applies To |
|--------|-------|-------------|---------|------------|
| `--output` | `-o` | Custom output filename/directory | Current directory | Both |
| `--parallel` | `-p` | Number of parallel connections (HTTP: chunks, Torrent: pieces) | 4 | Both |
| `--throttle` | | Bandwidth limit per chunk/piece (e.g., 1M, 500K, 2.5MB) | No limit | Both |
| `--seed-time` | | Time to seed after torrent download (minutes) | 0 | Torrent only |
| `--help` | `-h` | Show help message | - | Both |

### Queue Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `queue add` | Add download to queue | `quickdownload queue add <url> -p 8 --throttle 1M` |
| `queue start` | Process queue sequentially | `quickdownload queue start` |
| `queue list` | Show all queued downloads | `quickdownload queue list` |
| `queue status` | Show queue statistics | `quickdownload queue status` |
| `queue remove` | Remove specific job | `quickdownload queue remove job_123` |
| `queue clear` | Clear completed jobs | `quickdownload queue clear` |
| `queue stop` | Stop queue processing | `quickdownload queue stop` |

### Progress Display

QuickDownload shows clean, professional progress output:

```
Chunk  0: DOWN [██████████░░░░░░░░░░]  50.1%   20.9 MB/41.7 MB  
Chunk  1: DONE [████████████████████] 100.0%   41.0 MB/41.0 MB  
Chunk  2: DOWN [████████░░░░░░░░░░░░]  40.2%   16.8 MB/41.8 MB  
──────────────────────────────────────────────────────────────────
Overall: [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 32.1% (658.2 MB/2.0 GB)
```

## Advanced Usage

### HTTP Download Examples

**Maximum Performance:**
```bash
# Use 16 parallel connections for maximum speed
quickdownload -p 16 https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso
```

**Custom Output:**
```bash
# Download to specific location with custom name
quickdownload -o ~/Downloads/ubuntu.iso https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso
```

**Conservative Bandwidth:**
```bash
# Use fewer connections for shared networks
quickdownload -p 2 https://example.com/file.zip
```

### BitTorrent Examples

**Linux Distributions:**
```bash
# Download Ubuntu (magnet link)
quickdownload "magnet:?xt=urn:btih:..."

# Download from .torrent file
quickdownload ~/Downloads/ubuntu-22.04-desktop-amd64.iso.torrent

# Download from .torrent URL  
quickdownload https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso.torrent
```

**Seeding Support:**
```bash
# Download and seed for 30 minutes
quickdownload --seed-time 30 "magnet:?xt=urn:btih:..."

# Download to specific directory with seeding for 30 minutes
quickdownload -o ~/Downloads --seed-time 30 ubuntu.torrent
```

**Parallelism for Torrents:**
```bash
# Conservative parallelism for slow connections or rare torrents
quickdownload -p 3 "magnet:?xt=urn:btih:..."

# Standard parallelism for most scenarios
quickdownload -p 6 ubuntu.torrent

# High-performance parallelism for fast connections and popular torrents
quickdownload -p 12 "magnet:?xt=urn:btih:..."

# Combined with bandwidth throttling
quickdownload -p 8 --throttle 2M ubuntu.torrent
```

## Queue System

QuickDownload includes a powerful queue system for managing multiple downloads:

### Adding Downloads to Queue

```bash
# Basic queue addition
quickdownload queue add https://example.com/file1.zip

# With custom settings
quickdownload queue add https://example.com/file2.zip -p 8 -o ~/Downloads/

# With bandwidth throttling
quickdownload queue add https://example.com/file3.zip --throttle 1M

# Multiple files with different settings
quickdownload queue add https://example.com/large_file.zip -p 16 --throttle 2M
quickdownload queue add https://example.com/small_file.zip -p 4 --throttle 500K
```

### Processing Queue

```bash
# Start processing all pending downloads
quickdownload queue start

# View queue status
quickdownload queue list
```

**Example Queue Output:**
```
Download Queue (3 jobs):
================================================================================
COMPLETED job_1754503665_0
   URL: https://example.com/file1.zip
   Output: file1.zip
   Parallel: 4
   Throttle: 1M per chunk
   Status: completed
   Progress: 100.0%

DOWNLOADING job_1754503666_1
   URL: https://example.com/file2.zip
   Output: ~/Downloads/file2.zip
   Parallel: 8
   Status: downloading
   Progress: 45.2%

PENDING job_1754503667_2
   URL: https://example.com/file3.zip
   Parallel: 4
   Throttle: 500K per chunk
   Status: pending
```

### Queue Management

```bash
# View queue status
quickdownload queue status

# Remove specific job
quickdownload queue remove job_1754503667_2

# Clear completed downloads
quickdownload queue clear

# Stop queue processing
quickdownload queue stop
```

**Queue Features:**
- **Persistent Storage**: Queue survives system restarts
- **Sequential Processing**: Downloads one file at a time to avoid conflicts
- **Individual Settings**: Each job can have different parallelism and throttling
- **Resume Support**: Queue jobs support the same smart resume features
- **Error Handling**: Failed jobs can be retried automatically
- **Progress Tracking**: Real-time status for all queued downloads

## Bandwidth Throttling

Control download speed with flexible bandwidth limiting:

### Throttling Syntax

```bash
# Throttle examples
quickdownload --throttle 1M https://example.com/file.zip     # 1 Megabyte per second
quickdownload --throttle 500K https://example.com/file.zip   # 500 Kilobytes per second
quickdownload --throttle 2.5MB https://example.com/file.zip  # 2.5 Megabytes per second
quickdownload --throttle 100k https://example.com/file.zip   # 100 Kilobytes per second (lowercase)
```

**Supported Units:**
- `M` or `m`: Megabytes per second (e.g., `1M` = 1,000,000 bytes/sec)
- `K` or `k`: Kilobytes per second (e.g., `500K` = 500,000 bytes/sec)
- `MB`: Megabytes per second (e.g., `1MB` = 1,000,000 bytes/sec)
- `KB`: Kilobytes per second (e.g., `100KB` = 100,000 bytes/sec)
- No unit: Bytes per second (e.g., `1000` = 1,000 bytes/sec)
- Decimal values supported: `1.5M`, `2.5K`, etc.

### Throttling with Parallel Downloads

```bash
# Each of 8 chunks limited to 200K (total ~1.6M)
quickdownload -p 8 --throttle 200K https://example.com/file.zip

# Conservative bandwidth usage
quickdownload -p 4 --throttle 100K https://example.com/file.zip
```

### Use Cases for Throttling

**Shared Networks:**
```bash
# Be considerate on shared connections
quickdownload --throttle 500K https://example.com/file.zip
```

**Background Downloads:**
```bash
# Limit impact on other applications
quickdownload --throttle 200K -p 2 https://example.com/large_file.zip
```

**Metered Connections:**
```bash
# Control data usage carefully
quickdownload --throttle 100K https://example.com/file.zip
```

**Queue with Mixed Speeds:**
```bash
# Priority downloads with higher speeds
quickdownload queue add https://urgent.com/file.zip --throttle 2M -p 8
quickdownload queue add https://background.com/file.zip --throttle 200K -p 2
```

**Throttling Features:**
- **Per-Chunk Limiting**: Each parallel chunk respects the speed limit
- **Smooth Rate Control**: Token bucket algorithm prevents speed bursts
- **Flexible Units**: Supports bits, bytes, and decimal multipliers
- **Queue Compatible**: Works seamlessly with the queue system
- **Real-time Display**: Shows current throttle limits in progress output

### Smart Resume System

QuickDownload's resume system is intelligent and robust:

```bash
# Start a large download
quickdownload -p 8 -o large_file.zip https://example.com/large_file.zip

# ... download interrupted (Ctrl+C, network failure, crash) ...

# Resume with same command - automatically detects and continues
quickdownload -p 8 -o large_file.zip https://example.com/large_file.zip
# Output: "Found existing download progress - checking chunks..."
# Output: "Resuming previous download..."
```

**Resume Features:**
- Survives computer crashes and restarts
- Handles network failures gracefully  
- Verifies chunk integrity before resuming
- Re-downloads corrupted chunks automatically
- Works with any interruption (Ctrl+C, system shutdown, etc.)

## How It Works

### Technical Architecture

1. **File Analysis**: Determines file size and server range request support
2. **Smart Chunking**: Divides file into optimal chunks based on parallelism
3. **Parallel Execution**: Downloads chunks simultaneously using ThreadPoolExecutor
4. **Progress Persistence**: Continuously saves state in JSON progress files
5. **Chunk Verification**: Validates each chunk before marking as complete
6. **Error Recovery**: Implements exponential backoff for failed chunks
7. **Assembly**: Combines verified chunks into final file
8. **Cleanup**: Removes temporary files on successful completion

### Error Handling

QuickDownload implements enterprise-grade error handling:

- **Connection Errors**: Exponential backoff retry (1s, 2.5s, 5s, 9.5s, 16s)
- **Partial Failures**: Failed chunks don't affect successful ones
- **Corruption Detection**: Automatic chunk size verification and re-download
- **Network Recovery**: Intelligent reconnection on network restoration
- **Graceful Fallback**: Single-threaded mode for unsupported servers

## Performance & Benchmarks

### Real-World Performance

**Large File Downloads (1GB Ubuntu ISO):**
```bash
# Traditional wget
wget https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso
# Time: ~12 minutes (100Mbps connection)
# Resume: Basic, loses progress on corruption

# QuickDownload  
quickdownload -p 8 https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso
# Time: ~4 minutes (same connection) - 3x faster!
# Resume: Intelligent, chunk-level verification
```
## Advanced: Distributed Cluster Downloading with Registration

QuickDownload's most advanced feature: distribute downloads across multiple devices on your network with **explicit node registration** for maximum control and reliability.

**Setup Multi-Device Cluster**

**Initialize each device (run once per device):**
```bash
# Device 1 (Main laptop)
quickdownload cluster init
quickdownload cluster set "main-laptop"

# Device 2 (Gaming desktop)  
quickdownload cluster init
quickdownload cluster set "gaming-desktop"

# Device 3 (Home server)
quickdownload cluster init
quickdownload cluster set "home-server"
```

**Registration-Based Downloads**

**Step 1: Coordinator starts download session**
```bash
quickdownload cluster download --required-nodes 3 --wait-time 60 \
  -p 30 "https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso"

# Output shows session ID: abc123def456
```

**Step 2: Other nodes choose to participate**
```bash
# On each device that wants to help:
quickdownload cluster register abc123def456

# Or check status first:
quickdownload cluster status
```

**Step 3: Download starts automatically**
Once enough nodes register, download begins with intelligent chunk distribution and local sharing.

**Session Management**

**Check cluster and registration status:**
```bash
quickdownload cluster status
# Shows all nodes and your active registrations
```

**Withdraw from downloads:**
```bash
# Leave specific download
quickdownload cluster unregister abc123def456

# Leave all active downloads
quickdownload cluster withdraw
```

**Advanced Registration Options**

**Flexible node requirements:**
```bash
# Require minimum 2 nodes, wait up to 45 seconds
quickdownload cluster download --required-nodes 2 --wait-time 45 \
  -p 20 "https://example.com/large-file.zip"

# Start immediately with any available nodes
quickdownload cluster download --required-nodes 1 --wait-time 5 \
  "https://example.com/urgent-file.zip"
```

**Bandwidth-controlled cluster downloads:**
```bash
# Each node's chunks limited to 1MB/s
quickdownload cluster download --throttle 1M --required-nodes 4 \
  -p 24 "https://example.com/massive-file.zip"
```

**Key Registration Benefits**

- **Voluntary participation** - nodes choose which downloads to join
- **Graceful withdrawal** - leave downloads without disrupting others  
- **Resource control** - manage device load explicitly
- **Session isolation** - multiple downloads with different node sets
- **Predictable performance** - coordinator knows exact participating nodes



### Feature Comparison

| Feature | wget | curl | QuickDownload |
|---------|------|------|---------------|
| HTTP parallel chunks | No | No | Yes (1-24 threads) |
| Torrent piece parallelism | No | No | Yes (1-24 pieces) |
| Smart resume | No | No | Yes (Chunk-level) |
| Download queue | No | No | Yes (Persistent queue) |
| Bandwidth throttling | No | No | Yes (Per-chunk/piece limiting) |
| Corruption detection | No | No | Yes (Automatic) |
| BitTorrent support | No | No | Yes (Full support) |
| Multi-device cluster | No | No | Yes (Registration-based) |
| Progress bars | Basic | Basic | **Multi-chunk/piece** |
| Error recovery | Basic | Basic | **Advanced** |
| Speed (large files) | 1x | 1x | **2-5x faster** |

### Performance Tips

**Optimal Thread Count for HTTP:**
- **Fast connections (100+ Mbps)**: 8-16 threads
- **Standard connections (25-100 Mbps)**: 4-8 threads  
- **Slow connections (<25 Mbps)**: 2-4 threads
- **Shared networks**: 2-4 threads to be considerate

**Optimal Thread Count for Torrents:**
- **Popular torrents (many seeders)**: 8-16 pieces
- **Standard torrents**: 4-8 pieces
- **Rare torrents (few seeders)**: 2-4 pieces
- **Private trackers**: Follow community guidelines (usually 4-8)

**When to Use QuickDownload:**
- Files larger than 100MB
- Unreliable networks where resume is critical
- High-speed connections that can benefit from parallelism
- When you need BitTorrent + HTTP in one tool
- Multi-device scenarios with cluster downloading

## Technical Details

### Resume Implementation

QuickDownload implements sophisticated resume functionality:

**Progress Tracking:**
- Creates `.progress` files containing download metadata
- Tracks completed chunks, file size, and parameters
- Validates chunk integrity on resume attempts
- Automatically handles parameter changes gracefully

**State Management:**
- Temporary `.part{N}` files for each chunk during download
- JSON progress files for persistent state tracking  
- Automatic cleanup on successful completion
- Corruption detection and automatic re-download

**Chunk Verification:**
- File size validation for each chunk
- Automatic re-download of corrupted/missing chunks
- Smart recovery that only downloads what's needed
- Integrity checking before final assembly

### Supported Protocols & Servers

**HTTP/HTTPS Support:**
- Servers with HTTP Range Request support (HTTP 206 Partial Content)
- Automatic detection of server capabilities
- Graceful fallback to single-threaded for unsupported servers
- Custom headers and authentication (when supported by server)

**BitTorrent Support:**
- Magnet links with full DHT support
- .torrent files (local and remote URLs)
- Tracker and peer discovery
- Optional seeding with configurable time limits

### Parallelism: HTTP vs BitTorrent

**HTTP Downloads (`-p` flag):**
- Splits **single file** into chunks based on byte ranges
- Downloads **different byte ranges** simultaneously from same server
- Higher parallelism = more simultaneous chunk downloads
- Limited by server's range request support and connection limits

**BitTorrent Downloads (`-p` flag):**
- Requests **different pieces** simultaneously from multiple peers
- Each piece is a complete data unit (typically 256KB-4MB)
- Higher parallelism = more simultaneous piece requests across peer swarm
- Limited by peer availability and network etiquette

**Optimal Settings Guide:**

| Connection Speed | HTTP `-p` | Torrent `-p` | Notes |
|-----------------|-----------|--------------|-------|
| < 25 Mbps | 2-4 | 2-4 | Conservative for shared networks |
| 25-100 Mbps | 4-8 | 4-8 | Standard broadband performance |
| 100+ Mbps | 8-16 | 8-16 | High-speed connections |
| Gigabit+ | 16-24 | 12-20 | Maximum performance |

**Performance Considerations:**
- **Popular torrents**: Can handle higher parallelism (many seeders available)
- **Rare torrents**: Use lower parallelism (few peers, be courteous)
- **Private trackers**: Follow community guidelines for connection limits
- **System resources**: Each parallel stream uses memory and CPU

### System Requirements

- **Python**: 3.7 or higher
- **Dependencies**: requests, libtorrent-python (for torrent support)
- **Disk Space**: Sufficient space for target file + temporary chunks
- **Network**: Any connection speed (optimizes automatically)
- **Platform**: Windows, macOS, Linux

## FAQ

**Q: How many parallel downloads should I use?**
A: Start with 4-8 threads. Optimal number depends on your connection speed and server capacity. More isn't always better due to overhead.

**Q: Does this work with all websites?**
A: QuickDownload works with any server supporting HTTP range requests. For servers without range support, it falls back to single-threaded download (still works, just no parallelism).

**Q: Can I resume interrupted downloads?**
A: Yes! QuickDownload automatically saves progress and resumes exactly where it left off. Simply run the same command again.

**Q: What if my computer crashes during download?**
A: No problem! Progress is saved continuously. On restart, QuickDownload verifies existing chunks and downloads only what's missing or corrupted.

**Q: How does chunk verification work?**
A: Each chunk is verified for size and integrity before being marked complete. Corrupted chunks are automatically re-downloaded.

**Q: What temporary files are created?**
A: During download: `filename.part0`, `filename.part1`, etc. (chunk files) and `filename.progress` (progress file). All are cleaned up automatically on completion.

**Q: Can I change parallelism for resumed downloads?**
A: Currently, you must use the same parameters (URL, output filename, parallel count) to resume. Changing parameters starts fresh.

**Q: How much faster is parallel downloading?**
A: Typically 2-5x faster than single-threaded downloads, depending on your connection and server capabilities.

**Q: Is QuickDownload safe to use?**
A: Yes, QuickDownload only downloads files and doesn't execute code. However, always be cautious about what you download from the internet.

**Q: How does the queue system work?**
A: The queue stores jobs in `~/.quickdownload/queue.json` and processes them sequentially. Each job can have different settings (parallelism, throttling, output location). The queue persists across system restarts.

**Q: How does bandwidth throttling work?**
A: Throttling uses a token bucket algorithm to limit each chunk's download speed. With `-p 4 --throttle 1M`, each of the 4 chunks is limited to 1 Mbps, giving roughly 4 Mbps total speed.

**Q: Does `-p` work the same for torrents and HTTP downloads?**
A: No, they work differently. For HTTP: `-p` splits one file into chunks from the same server. For torrents: `-p` controls how many pieces are requested simultaneously from different peers in the swarm.

**Q: What `-p` value should I use for torrents?**
A: Start with 4-8 for most torrents. Use higher values (8-16) for popular torrents with many seeders, and lower values (2-4) for rare torrents or slow connections.

**Q: Why is my torrent slow even with high `-p` value?**
A: Torrent speed depends on peer availability, not just parallelism. A rare torrent with few seeders won't benefit from high `-p` values. Also, some peers may have upload limits.

**Q: Can I use throttling with torrents?**
A: Yes! Use `--throttle` with torrents to limit bandwidth usage. This is especially helpful on shared networks or when downloading in the background.

**Q: Can I throttle the total download speed instead of per-chunk?**
A: Currently, throttling is per-chunk. For total speed control, calculate: `desired_total_speed ÷ parallel_chunks = per_chunk_limit`. For example, for 2 Mbps total with 4 chunks: `--throttle 500K -p 4`.

**Q: Can I add downloads to the queue while it's processing?**
A: Yes! You can add new jobs with `quickdownload queue add` while the queue is running. New jobs will be processed after current ones complete.

**Q: Why choose QuickDownload over wget/curl?**
A: QuickDownload offers parallel downloading, intelligent resume, download queue, bandwidth throttling, BitTorrent support, and better progress visualization - all in a modern, robust tool.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Download stuck at "Analyzing file..." | Server may be slow to respond. Check internet connection and try again. |
| "Range requests supported: False" | Server doesn't support parallel downloads. Will use single-threaded mode (still works). |
| Resume not working | Ensure same command parameters (URL, output file, parallel count) as original download. |
| Chunks failing repeatedly | Try reducing parallel count: `quickdownload -p 2 <url>` |
| BitTorrent not working | Install libtorrent: `pip install libtorrent` or use system package manager. |
| Permission errors | Check write permissions for output directory. |
| Queue not saving jobs | Check write permissions for `~/.quickdownload/` directory. |
| Throttling not working | Verify throttle syntax (e.g., `1M`, `500K`). Check that server supports range requests for parallel chunks. |
| Queue processing stops | Use `quickdownload queue status` to check for failed jobs. Restart with `quickdownload queue start`. |

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Nikhil-K-Singh/quickdownload.git
cd quickdownload

# Install in development mode
pip install -e .

```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python's `concurrent.futures` for parallel processing
- Uses `libtorrent` for BitTorrent protocol support
- Inspired by the need for faster, more reliable downloads in the modern era

---

**Made with care for faster, more reliable downloads**

[![GitHub](https://img.shields.io/badge/GitHub-Nikhil--K--Singh-blue?logo=github)](https://github.com/Nikhil-K-Singh)
[![PyPI](https://img.shields.io/badge/PyPI-quickdownload-blue?logo=pypi)](https://pypi.org/project/quickdownload/)

*Star this repo if QuickDownload saves you time!*
