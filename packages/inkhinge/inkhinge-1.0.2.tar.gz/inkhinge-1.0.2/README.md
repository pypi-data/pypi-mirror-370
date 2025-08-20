# inkhinge

`inkhinge`是一个专为光谱分析设计的工具集，专注于光谱数据的处理、转换与拟合分析，支持Omnic SPA格式文件的转换及Kubelka-Munk（KM）值的多维度曲线拟合，为光谱数据分析提供从数据预处理到高级建模的完整流程支持。通过`pip install inkhinge`安装后，可便捷处理光谱数据转换、背景校正、批量处理及多维度拟合等任务，同时新增图像灰度值计算和图像格式转换功能，拓展了工具集在图像光谱分析领域的应用。


## 安装
```bash
pip install inkhinge
```


## 函数文档与使用方法

---

### `read_to_csv`
读取Omnic SPA格式光谱文件并转换为CSV格式，支持背景校正、批量处理及多文件合并，自动计算Kubelka-Munk值。

#### 参数:
- `input_path` (str): 输入路径（单个SPA文件或包含SPA文件的目录）。
- `output_path` (str, 可选): 输出路径（单个CSV文件或目录），默认与输入同目录并添加`_converted`后缀。
- `background_path` (str, 可选): 背景文件（如BG.spa）路径，用于背景校正（透射率/反射率数据适用）。
- `overwrite` (bool, 可选): 是否覆盖已有文件，默认`False`。
- `recursive` (bool, 可选): 处理目录时是否递归子目录，默认`False`。
- `precision` (int, 可选): 输出数据的小数位数（默认20位，确保定点表示，避免科学计数法）。
- `merge_output` (str, 可选): 合并后CSV的路径，默认`None`（不合并）。

#### 返回:
- 单个文件转换：返回输出CSV路径。
- 批量转换：返回成功转换的文件数（未合并时）或文件路径列表（合并时）。

#### 核心功能:
- 自动识别光谱类型（吸光度、透射率等）并标注单位。
- 对反射率数据自动计算Kubelka-Munk值。
- 支持背景校正（透射率数据减法校正，反射率数据除法校正）。
- 批量处理时按文件名排序，合并后列名自动编号（如`Kubelka-Munk_0`）。

#### 使用方法:
```python
from inkhinge.core import read_to_csv

# 单个SPA文件转换（带背景校正）
output_path = read_to_csv(
    input_path="sample.spa",
    output_path="output/sample.csv",
    background_path="background.BG.spa",  # 应用背景校正，若不需要，取消此行即可
    precision=15  # 保留15位小数
)
print(f"转换完成，输出路径：{output_path}")

# 批量转换目录中所有SPA文件（含子目录）,但不合并
success_count = read_to_csv(
    input_path="spectral_data/",
    output_path="converted_csv/",
    recursive=True,  # 递归处理子目录
    overwrite=True,  # 覆盖已有文件
    precision=10
)
print(f"批量转换完成，成功转换{success_count}个文件")

# 转换指定目录下的所有SPA文件，并将其合并为单个CSV文件
read_to_csv(
    input_path="spectral_data/",
    output_path="converted_csv/",
    merge_output="merged_spectra.csv"  # 合并所有CSV
)
print("转换与合并完成，结果已保存至merged_spectra.csv")
```

---

### `curvefit_km_t`
对指定行的KM值随时间变化进行指数曲线拟合（`y = a·x^b·exp(-c·x)`），输出拟合参数、R²值及可视化结果。

#### 参数:
- `file_path` (str): 输入CSV文件路径（每行对应一个波数，每列对应一个时间点）。
- `target_row` (int, 可选): 目标行号（从1开始），默认1。
- `txt_output_path` (str, 可选): 拟合结果文本路径，默认`curvefit_km_t.txt`。
- `png_output_path` (str, 可选): 拟合图像路径，默认`curvefit_km_t.png`。
- `show_plot` (bool, 可选): 是否显示图像，默认`True`。

#### 返回:
- 字典，包含拟合参数（`a`, `b`, `c`）、R²值、原始数据及拟合表达式等。

#### 使用方法:
```python
from inkhinge.core import curvefit_km_t

# 对CSV中第3行的KM值进行时间序列拟合
result = curvefit_km_t(
    file_path="merged_spectra.csv",
    target_row=3,  # 目标行号（从1开始）
    txt_output_path="time_fit_result.txt",
    png_output_path="time_fit_plot.png"
)
print(f"拟合函数表达式：{result['fit_expression']}")
print(f"拟合优度R²：{result['r_squared']:.4f}")
```

---

### `curvefit_km_wavenumber`
对指定时间点的KM值与波数进行多峰高斯-洛伦兹混合函数拟合，适用于分析特定时间下的光谱峰特征。

#### 参数:
- `file_path` (str): 输入CSV文件路径（每行对应一个波数，每列对应一个时间点）。
- `time_column_index` (int, 可选): 目标时间列索引（从0开始），默认1。
- `txt_output_path` (str, 可选): 拟合结果文本路径，默认`curvefit_km_wavenumber.txt`。
- `png_output_path` (str, 可选): 拟合图像路径，默认`curvefit_km_wavenumber.png`。

#### 返回:
- 字典，包含拟合参数、R²值、拟合表达式及原始数据。

#### 拟合模型:
多峰高斯-洛伦兹混合函数，每个峰的表达式为：  
`η·(a/(1+((w-x₀)/σ)²)) + (1-η)·(a·exp(-(w-x₀)²/(2σ²)))`  
（`η`为混合系数，`a`为振幅，`x₀`为峰位，`σ`为半宽）

#### 使用方法:
```python
from inkhinge.core import curvefit_km_wavenumber

# 对第2列（时间点）的KM值与波数进行拟合
result = curvefit_km_wavenumber(
    file_path="merged_spectra.csv",
    time_column_index=2,  # 目标时间列索引（从0开始）
    txt_output_path="wavenumber_fit_result.txt",
    png_output_path="wavenumber_fit_plot.png"
)
print(f"拟合优度R²：{result['r2']:.4f}")
```

---

### `curvefit_km_t_wavenumber`
对时间-波数-KM值三维数据进行拟合，先通过时间序列拟合获取常数`k`，再对`a(w)`和`c(w)`进行多峰高斯-洛伦兹拟合，最终构建三维模型`KM(t,w) = a(w)·t^k·exp(-c(w)·t)`,k为常数。

#### 参数:
- `file_path` (str): 输入CSV文件路径。
- `wavenumber_min` (float, 可选): 波数下限，默认1300 cm⁻¹。
- `wavenumber_max` (float, 可选): 波数上限，默认1320 cm⁻¹。
- `output_txt_path` (str, 可选): 结果文本路径，默认`curvefit.txt`。
- `output_img_path` (str, 可选): 三维拟合图像路径，默认`curvefit.png`。
- `peak_num` (int, 可选): 拟合时需要用的峰的个数，默认为3。

#### 返回:
- 字典，包含常数`k`、`a(w)`和`c(w)`的拟合参数、整体R²值及数据范围等。

#### 核心功能:
- 自动修正波数非单调问题（排序确保1300→1320 cm⁻¹）。
- 分两步拟合：先求`k`（所有波数的`b`值均值），再固定`k`拟合`a(w)`和`c(w)`。
- 输出原始数据与拟合曲面的三维对比图，标注整体及分项R²值。

#### 使用方法:
```python
from inkhinge.core import curvefit_km_t_wavenumber

# 对1300-1320 cm⁻¹范围内的三维数据进行拟合
result = curvefit_km_t_wavenumber(
    file_path="merged_spectra.csv",
    wavenumber_min=1300,
    wavenumber_max=1320,
    output_txt_path="3d_fit_result.txt",
    output_img_path="3d_fit_plot.png",
    peak_num=3,  # 默认为3
)
print(f"整体拟合优度R²：{result['r2_overall']:.4f}")
print(f"常数k值：{result['k']:.6f}")
```

---

### `GrayValueCalculation`类
提供图像灰度值计算功能，支持单张图片和批量图片处理，可根据指定的RGB范围筛选区域并计算平均灰度值，适用于图像光谱特征分析。

#### 静态方法`process_single_image`
处理单张图片，根据指定的RGB范围筛选符合条件的区域，计算并输出区域的平均灰度值及相关信息。

##### 参数:
- `image_path` (str): 图片文件路径。
- `red_range` (tuple): 红色通道范围，格式为(最小值, 最大值)。
- `green_range` (tuple): 绿色通道范围，格式为(最小值, 最大值)。
- `blue_range` (tuple): 蓝色通道范围，格式为(最小值, 最大值)。
- `max_valid_width` (int): 最大有效区域宽度。
- `max_valid_height` (int): 最大有效区域高度。
- `region_size` (int): 基础区域大小（如9表示9x9区域）。
- `output_dir` (str, 可选): 结果文件保存目录，默认"results"。

##### 返回:
- 字典，包含图片路径（`image_path`）、所有有效区域的平均灰度值平均值（`overall_average`）及结果文件路径（`result_file`）；若处理失败则返回`None`。


#### 静态方法`process_images`
处理图片，自动识别输入是单个文件还是目录，支持批量处理并生成汇总报告。

##### 参数:
- `input_path` (str): 单个图片文件路径或包含图片的目录路径。
- `red_range` (tuple): 红色通道范围，格式为(最小值, 最大值)。
- `green_range` (tuple): 绿色通道范围，格式为(最小值, 最大值)。
- `blue_range` (tuple): 蓝色通道范围，格式为(最小值, 最大值)。
- `max_valid_width` (int): 最大有效区域宽度。
- `max_valid_height` (int): 最大有效区域高度。
- `region_size` (int): 基础区域大小（如9表示9x9区域）。
- `output_dir` (str, 可选): 结果文件保存目录，默认"results"。

##### 返回:
- 列表，包含每张图片的处理结果字典；若输入路径不存在或处理失败则返回空列表。

##### 支持的图片格式:
- `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`

#### 使用方法:
```python
from inkhinge.core import GrayValueCalculation

# 处理单张图片
single_result = GrayValueCalculation.process_single_image(
    image_path="tifdemo/an.tif",
    red_range=(0, 15),
    green_range=(0, 15),
    blue_range=(0, 15),
    max_valid_width=10,
    max_valid_height=10,
    region_size=9,
    output_dir="analysis_results"
)
print(f"单张图片平均灰度值：{single_result['overall_average']:.2f}")

# 批量处理目录中的图片
batch_results = GrayValueCalculation.process_images(
    input_path="image_directory/",  # 图片目录路径
    red_range=(0, 15),
    green_range=(0, 15),
    blue_range=(0, 15),
    max_valid_width=10,
    max_valid_height=10,
    region_size=9,
    output_dir="batch_analysis_results"
)
print(f"批量处理完成，成功处理{len(batch_results)}张图片")
```

---

### `TifToPng`类
TIF格式到PNG格式的转换工具类，支持单文件转换和批量转换，方便图像数据的处理与兼容。

#### 静态方法`convert_single`
将单个TIF文件转换为PNG格式。

##### 参数:
- `input_path` (str): TIF文件的路径。
- `output_path` (str, 可选): 输出PNG文件的路径，若为`None`则在原目录生成同名PNG文件。

##### 返回:
- 转换成功返回`True`，否则返回`False`。


#### 静态方法`batch`
批量转换目录中的所有TIF文件为PNG格式。

##### 参数:
- `input_dir` (str): 包含TIF文件的目录。
- `output_dir` (str, 可选): 输出PNG文件的目录，若为`None`则使用输入目录。

#### 使用方法:
```python
from inkhinge.core import TifToPng

# 转换单个TIF文件为PNG
# 不指定输出路径（默认在原目录生成同名PNG）
TifToPng.convert_single("input.tif")

# 指定输出路径
TifToPng.convert_single("tifdemo/an.tif", "tifdemo/an.png")

# 批量转换目录中的TIF文件
# 不指定输出目录（默认使用输入目录）
TifToPng.batch("input_dir")

# 指定输出目录
TifToPng.batch("input_dir", "output_dir")
```

---

### `insert_crystals`
将晶体结构插入到主体结构中，支持分子、离子或原子类型的晶体结构插入，考虑周期性边界条件并避免原子间过度重叠。

#### 参数:
- `host_path` (str): 主体结构文件路径。
- `insert_path` (str): 要插入的结构文件路径。
- `center` (tuple): 插入区域中心坐标 (x, y, z)。
- `radius` (float): 插入区域半径。
- `num` (int): 要插入的数量。
- `tolerance` (float, 可选): 碰撞容忍度 (0.0-1.0)，默认0.9。
- `max_attempts` (int, 可选): 最大尝试次数，默认1000。
- `output_path` (str, 可选): 输出文件路径，若为`None`则不保存，默认`None`。
- `view_crystals` (bool,可选): 是否可视化生成的晶体结构（默认为True）。

#### 返回:
- 插入后的结构对象（ASE的Atoms对象）。

#### 核心功能:
- 自动识别插入结构类型（分子、离子或原子），采用对应插入策略。
- 考虑周期性边界条件计算原子间最小距离，避免过度重叠。
- 基于晶体半径判断原子碰撞，支持自定义半径字典。
- 在指定球内随机生成插入位置，确保插入区域可控。

#### 使用方法:
```python
from inkhinge.core import insert_crystals
# 示例：插入5个分子到主体结构中
insert_crystals(
    host_path="6_mil-101_pbesol-ot_optcell.cif",  # 主体结构文件
    insert_path="NaCl_insert.cif",  # 要插入的结构文件
    center=[10.0, 10.0, 10.0],  # 插入中心坐标
    radius=5.0,  # 插入区域半径
    num=5,  # 插入数量
    tolerance=0.9,  # 碰撞容忍度
    max_attempts=1000,  # 最大尝试次数
    output_path="result.cif"  # 输出文件路径
)
```

---

## 功能特点
1. **高精度数据处理**：  
   - 光谱转换保留高小数精度（默认20位），避免科学计数法损失精度。
   - 拟合过程采用物理约束（如振幅非负、峰位在波数范围内），确保参数合理性。
   - 图像灰度值计算精确到像素级，支持自定义区域大小与RGB筛选范围。

2. **自动化与鲁棒性**：  
   - 自动识别光谱类型、处理波数排序问题、缺失值标记为`nan`。
   - 拟合失败时启用备用初始值策略，提高复杂数据的拟合成功率。
   - 图像处理自动创建输出目录，支持文件存在性检查与错误信息记录。

3. **全面的可视化支持**：  
   - 曲线拟合结果自动生成散点图（原始数据）与线图（拟合曲线）。
   - 三维拟合提供原始数据与拟合曲面的对比图，支持视角同步。

4. **灵活的批量处理**：  
   - 支持递归遍历子目录的SPA文件，合并后的数据结构适配深度学习输入格式。
   - 图片批量处理自动筛选支持的格式，生成汇总报告记录每张图片的灰度值结果。
   - 支持TIF到PNG的批量格式转换，自动处理目录结构和文件命名。


## 贡献
如果你想为`inkhinge`工具集做出贡献，请遵循以下步骤：
1. Fork本仓库
2. 创建特性分支（`git checkout -b feature/SpectralFeature`）
3. 提交更改（`git commit -m 'Add spectral preprocessing feature'`）
4. 推送分支（`git push origin feature/SpectralFeature`）
5. 打开Pull Request


## 许可证
本项目采用MIT许可证 - 详情请见[LICENSE](LICENSE)文件。