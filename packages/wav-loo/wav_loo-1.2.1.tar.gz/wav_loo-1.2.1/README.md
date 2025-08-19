# WAV Loo

版本：1.2.1

`wav-loo` 是一个为音频处理和云原生开发设计的集成工具箱，它提供了三大核心功能：

1.  **WAV 文件查找器**：在本地或远程URL中快速定位WAV音频文件。
2.  **命令行快捷别名**：集成了数十个常用的 `kubectl`、`atlasctl` 和其他开发运维命令，提升效率。
3.  **Loss 函数库 + 数据生成**：提供损失函数与车载多音区数据生成工具。

## 安装

```bash
pip install wav-loo
```

## 功能一：WAV 文件查找

你可以在Python代码中或通过命令行来查找WAV文件。

### 命令行用法

```bash
wav-loo find <路径或URL> [--output <文件>] [--verbose]
```
-   **示例**:
    -   `wav-loo find /path/to/audio`
    -   `wav-loo find https://example.com/audio-files/`

### Python API 用法

```python
from wav_loo import WavFinder
finder = WavFinder()
wavs = finder.find_wav_files('/path/to/audio')
print(wavs)
```

## 功能二：快捷命令

通过 `wav-loo` 执行常用的运维开发命令，无需配置复杂的alias。

### 命令行用法

只需将别名作为 `wav-loo` 的子命令即可。

-   **示例**:
    ```bash
    # 查看pods (等价于 kubectl get pods -o wide)
    wav-loo kg

    # 查看signal命名空间日志 (等价于 kubectl logs -n signal)
    wav-loo kln

    # 使用unimirror安装numpy (等价于 uv pip install -i ... numpy)
    wav-loo uv numpy
    ```

### 支持的快捷命令列表

| 子命令 | 等价 bash 命令                                    | 说明                                     |
|--------|---------------------------------------------------|------------------------------------------|
| `kd`   | `kubectl delete pods`                             | 删除所有pods                             |
| `kg`   | `kubectl get pods -o wide`                        | 查看pods（详细）                         |
| `kl`   | `kubectl logs`                                    | 查看日志                                 |
| `rs`   | `kubectl describe ResourceQuota -n ...`           | 查看资源配额（需补命名空间）             |
| `kdn`  | `kubectl delete pods -n signal`                   | 删除signal命名空间pods                   |
| `kgn`  | `kubectl get pods -o wide -n signal`              | 查看signal命名空间pods                   |
| `kln`  | `kubectl logs -n signal`                          | 查看signal命名空间日志                   |
| `at`   | `atlasctl top node`                               | atlas节点监控                            |
| `ad`   | `atlasctl delete job`                             | 删除atlas作业                            |
| `atd`  | `atlasctl delete`                                 | 删除atlas资源                            |
| `adp`  | `atlasctl delete job pytorchjob`                  | 删除pytorch作业                          |
| `adn`  | `atlasctl delete job -n signal`                   | 删除signal命名空间作业                   |
| `tb`   | `tensorboard --port=3027 --logdir=.`              | 启动tensorboard                          |
| `ca`   | `conda activate <env>`                            | 激活conda环境（需补环境名）              |
| `gp`   | `gpustat -i`                                      | 查看GPU状态                              |
| `kgg`  | `kubectl get po --all-namespaces -o wide [extra args]` | 全局查看pods（可附加kubectl过滤参数） |
| `uv`   | `uv pip install -i ...`                           | 使用unimirror安装PyPI包（需补包名）      |


## 功能三：Loss 函数库

`wav-loo` 提供了一系列在信号处理和深度学习中常用的损失函数。

### `multi_channel_separation_consistency_loss`

**功能**:

计算多通道（N>2）音频信号分离后的一致性损失。该损失旨在惩罚模型输出的多个通道之间的**幅度谱**差异与原始目标信号中对应通道之间的**幅度谱**差异不一致的情况。它通过计算所有通道对 (pair) 的预测幅度谱差异和目标幅度谱差异，然后最小化这两组差异之间的L1距离来实现。

**使用方法**:

```python
import torch
from wav_loo.loss import multi_channel_separation_consistency_loss

# 假设 pred_mag_specs 和 target_mag_specs 是你的模型输出和目标真值
# 形状: (B, N, F, T), 类型: torch.float32
# B: batch_size, N: 通道数, F: 频率bins, T: 时间帧
pred_mag_specs = torch.randn(8, 4, 257, 100, dtype=torch.float32)
target_mag_specs = torch.randn(8, 4, 257, 100, dtype=torch.float32)

loss = multi_channel_separation_consistency_loss(pred_mag_specs, target_mag_specs)
print(f"一致性损失: {loss.item()}")
```

## 功能四：多通道车载语音数据生成（已更新逻辑）

生成基于车载多位置 IR（房间脉冲响应）和干净语音的多音区数据集，用于语音分离等任务。

- **IR 目录结构**：`ir_root` 内部递归查找子目录名包含以下关键词的文件夹，并收集其中的 `.wav` IR：
  - `zhujia`, `fujia`, `zhujiahoupai`, `fujiahoupai`（不区分大小写，名称包含即可）
- **干净语音**：`clean_root` 内递归查找 `.wav` 文件（多通道 clean 会先混为单声道）。
- **音区设置**：
  - 4 音区（默认）：上述四个位置分别映射到输出通道 `[0,1,2,3]`。
  - 2 音区：`zone_a=[zhujia, zhujiahoupai]` → 通道 `0`；`zone_b=[fujia, fujiahoupai]` → 通道 `1`。
- **生成规则（核心更新）**：
  - 始终保留 IR 卷积后的多通道空间信息（不做单声道合并）。
  - 2 音区/单说话人：仅从可用物理位置中随机选择一个 IR 进行卷积。
  - 2 音区/多说话人：为每个说话人随机分配一个独立的物理位置（若人数多于位置数则循环分配），各自与对应 IR 卷积后按通道相加。
  - 4 音区：使用该区域下所有可用 IR；各子位置与 clean 卷积后按通道相加。
  - 当 IR 通道数与输出通道数不一致时，按输出通道数对齐（自动 pad/截断）。
  - `mixture (T, N)`：所有标签（区域）贡献沿“标签维”求和后得到。
  - `target (T, N)`：第 `i` 列仅保留标签 `i` 在通道 `i` 的自通道成分（便于监督）。
- **配置参数（关键）**：
  - `zones`：取值 `2` 或 `4`
  - `presence_prob`：每个区域有人说话的概率（默认 0.5）
  - `two_zone_multi_speaker_prob`：2 音区时，单个区域内出现多说话人的概率（默认 0.3）
  - `two_zone_max_speakers_per_zone`：2 音区时，单个区域内最多说话人数（默认 2）
  - `max_clean_seconds`：每条 clean 的最大时长（默认 30s）
  - `sample_rate`、`num_samples` 等

### 命令行用法

```bash
# 4 音区，默认 60000 条，16kHz，默认输出到 ./generated_car_data
wav-loo gen --ir-dir /path/to/ir_root --clean-dir /path/to/clean_root

# 2 音区，自定义输出与数量
wav-loo gen \
  --ir-dir /path/to/ir_root \
  --clean-dir /path/to/clean_root \
  --zones 2 \
  --num-samples 2000 \
  --sample-rate 16000 \
  --output /path/to/out_dir
```

### Python API 用法（推荐）

```python
from wav_loo.data_gen import CarDataGenerator, GenerationConfig

cfg = GenerationConfig(
    ir_root_dir="/path/to/ir_root",
    clean_root_dir="/path/to/clean_root",
    output_dir="/path/to/out_dir",
    sample_rate=16000,
    num_samples=60000,
    zones=2,  # 或 4
    random_seed=42,
    max_clean_seconds=30.0,
    presence_prob=0.5,
    two_zone_multi_speaker_prob=0.3,
    two_zone_max_speakers_per_zone=2,
)
CarDataGenerator(cfg).generate()
```

### 数据生成依赖
- 运行数据生成需要：`numpy`、`soundfile`（依赖系统库 `libsndfile`）、`scipy`、`tqdm`。

## 依赖
- Python 3.7+
- requests
- beautifulsoup4
- urllib3

## 许可证
MIT License 