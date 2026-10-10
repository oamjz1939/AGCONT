---
name: end-to-blender
description: "将《明日方舟：终末地》等游戏衍生 MMD 模型（.pmx）自动转换并配置为适合绘画参考与姿态调节的 Blender 工程文件（.blend）。包含骨骼分层、棍状显示、IK 保留、材质贴图修复与自包含打包功能。当用户提到 end-to-blender、终末地模型转 blender、pmx 转 blend 摆姿态等需求时使用。"
---

# End to Blender 转换规范与工具

本 Skill 用于将《明日方舟：终末地》及同类游戏的衍生 MMD 角色模型（`.pmx`），自动化转换为适合作为绘画人体参考、姿态摆放与透视辅助的 Blender 工程文件（`.blend`）。

## 核心设计目标

1. **开箱即用**：双击 `.blend` 文件打开后，默认处于“姿态模式”（Pose Mode）和“材质预览”视图。
2. **骨骼清爽**：骨骼采用“棍状”（Stick）纤细显示，开启“在前显示”。默认隐藏物理碰撞和次级杂乱骨骼，不遮挡人体轮廓。
3. **分层管理**：身体、四肢、手指、头发、衣物分入清晰的骨骼集合（Bone Collections），便于单独显示或隐藏。
4. **色彩纯净**：自动剥离原 MMD 缺失的阴影贴图引用，保留纯净的基础颜色贴图，避免出现洋红色缺失块。
5. **完全自包含**：自动将所有贴图打包（Pack）进 `.blend` 文件，移动工程文件不丢贴图。

## 目录结构

- `scripts/convert_pmx_to_blend.py`：核心 Blender Python 转换脚本。
- `scripts/run.sh`：便捷 Shell 启动包装器。

## 执行方式

### 1. 单模型转换

使用 Shell 脚本转换单个 `.pmx` 文件：

```bash
~/.gemini/config/skills/end-to-blender/scripts/run.sh -i "/path/to/角色.pmx"
```

指定自定义输出路径：

```bash
~/.gemini/config/skills/end-to-blender/scripts/run.sh -i "/path/to/角色.pmx" -o "/path/to/输出.blend"
```

直接通过 Blender 执行：

```bash
/Applications/Blender.app/Contents/MacOS/Blender -b -P ~/.gemini/config/skills/end-to-blender/scripts/convert_pmx_to_blend.py -- -i "/path/to/角色.pmx"
```

### 2. 批量处理示例

如需转换某一目录下的全部角色文件夹：

```bash
for pmx in /path/to/new/*/*.pmx; do
    ~/.gemini/config/skills/end-to-blender/scripts/run.sh -i "$pmx"
done
```

## 转换逻辑细节

### 1. 骨骼集合分类对照
- **Root / 根节点**：全局位移与旋转。
- **センター / 重心中心**：骨盆重心调节。
- **ＩＫ**：双腿与双脚地面反向动力学控制器。
- **体(上) / 体(下)**：脊椎、胸腔、腰部核心躯干。
- **腕 / 足**：手臂与腿部主要关节。
- **指**：双手各关节细分骨骼。
- **头发与耳朵与尾巴**：包含 `hair_`、`ear_`、`tail_` 命名前缀骨骼。
- **衣物与饰品**：包含 `clothes_`、`spike_`、`strap_`、`shawl_`、`ornament_` 等部件骨骼。
- **次级与物理骨骼(已隐藏)**：包含 `QB_`、`HB_`、`spring_`、`錘`、`Bip`、`捩`、`_dummy_`、`_shadow_` 等骨骼。

### 2. 贴图与材质清理
MMD 模型经常在 PMX 材质槽中引用内置的 `toon01.bmp` 等贴图。在未附带该文件的环境下，Blender 会因贴图丢失显示洋红色块。脚本会自动检测并移除对缺失文件的引用，将着色器中的阴影贴图影响因子重置为 0，仅保留基础漫反射贴图。

### 3. 环境与依赖
- 要求 Blender 4.2 LTS 或 5.x 版本。
- 依赖 `mmd_tools` 扩展或插件。已在 Blender 脚本目录正确安装支持 modern Blender 的版本。
