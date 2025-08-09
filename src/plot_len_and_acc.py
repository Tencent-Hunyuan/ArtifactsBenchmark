import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import seaborn as sns

# Set style for publication quality
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# ========== 新增：拟合曲线开关 ==========
SHOW_FIT_CURVE = True  # 设置为 False 可以关闭拟合曲线

plt.rcParams.update({
    'font.size': 12,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
    'figure.titlesize': 18,
    'axes.linewidth': 1.2,
    'grid.alpha': 0.3
})

# Data from the table - simplified to closed/open classification
data = {
    "GPT-5": {"AVG": 72.55, "IFLEN": 0, "category": "closed"},
    "Claude Opus 4.1": {"AVG": 59.76, "IFLEN": 0, "category": "closed"},
    "Gemini-2.5-Pro": {"AVG": 57.74, "IFLEN": 0, "category": "closed"},
    "Claude Sonnet 4 (20250514)": {"AVG": 57.28, "IFLEN": 0, "category": "closed"},
    "GPT-OSS-120B": {"AVG": 57.69, "IFLEN": 16018.79, "category": "open"},
    "Qwen3-235B-A22B-Thinking-2507": {"AVG": 55.01, "IFLEN": 34357.84, "category": "open"},
    "o3-2025-04-16": {"AVG": 54.04, "IFLEN": 0, "category": "closed"},
    "GLM-4.5": {"AVG": 51.33, "IFLEN": 21854.10, "category": "open"},
    "GLM-4.5_Air": {"AVG": 48.90, "IFLEN": 20925.02, "category": "open"},
    "Claude 3.7 Sonnet (20250219)": {"AVG": 51.32, "IFLEN": 15480.06, "category": "open"},
    "Qwen3-235B-A22B-Instruct-2507": {"AVG": 50.62, "IFLEN": 20765.47, "category": "open"},
    "DeepSeek-R1-0528": {"AVG": 47.73, "IFLEN": 19215.71, "category": "open"},
    "Kimi K2 Instruct": {"AVG": 47.65, "IFLEN": 7116.99, "category": "open"},
    "Qwen3-Coder-480B-A35B-Instruct": {"AVG": 47.15, "IFLEN": 17581.53, "category": "open"},
    "GPT-4.1-2025-04-14": {"AVG": 45.95, "IFLEN": 7290.94, "category": "closed"},
    "DeepSeek-V3-0324": {"AVG": 43.50, "IFLEN": 11443.06, "category": "open"},
    "DeepSeek-R1": {"AVG": 41.41, "IFLEN": 10751.63, "category": "open"},
    "Qwen3-Coder-30B-A3B-Instruct": {"AVG": 41.16, "IFLEN": 18087.12, "category": "open"},
    "Qwen3-235B-A22B": {"AVG": 41.09, "IFLEN": 19314.92, "category": "open"},
    "hunyuan-A13B": {"AVG": 40.95, "IFLEN": 17924.89, "category": "open"},
    "Claude 3.5 Sonnet (20241022)": {"AVG": 39.85, "IFLEN": 6391.96, "category": "closed"},
    "KAT-V1-40B": {"AVG": 35.21, "IFLEN": 23262.57, "category": "open"},
    "GPT-4o": {"AVG": 33.54, "IFLEN": 4882.36, "category": "closed"},
}

# Simplified color scheme for closed vs open
colors = {
    "closed": "#2E86AB",      # Professional blue
    "open": "#A23B72",        # Deep magenta
}

# Compute unknown position
iflen_values = [v["IFLEN"] for v in data.values() if v["IFLEN"] > 0]
max_iflen = max(iflen_values)
unknown_x = max_iflen + 3000  # More spacing for better visual separation

# Create figure with screen-friendly size
fig, ax = plt.subplots(figsize=(12, 8), dpi=100)

# Plot points with enhanced styling
for model, vals in data.items():
    x = unknown_x if vals["IFLEN"] == 0 else vals["IFLEN"]
    y = vals["AVG"]
    category = vals["category"]
    
    # Enhanced scatter plot with larger points and edge
    ax.scatter(x, y, c=colors[category], s=120, alpha=0.8, 
              edgecolors='white', linewidth=1.5, zorder=5)

# Enhanced vertical line for unknown category
ax.axvline(unknown_x, color='#666666', linestyle='--', linewidth=2, alpha=0.7, zorder=1)

# ========== 新增：绘制拟合曲线 ==========
if SHOW_FIT_CURVE:
    # 收集已知推理长度的数据点（排除IFLEN=0的模型）
    known_x = []
    known_y = []
    for model, vals in data.items():
        if vals["IFLEN"] > 0:  # 只使用已知推理长度的数据
            known_x.append(vals["IFLEN"])
            known_y.append(vals["AVG"])
    
    if len(known_x) >= 2:  # 至少需要2个点来拟合直线
        # 转换为numpy数组
        known_x = np.array(known_x)
        known_y = np.array(known_y)
        
        # 使用线性拟合（一次多项式）
        coefficients = np.polyfit(known_x, known_y, 1)  # 1表示一次多项式（直线）
        poly_func = np.poly1d(coefficients)
        
        # 生成平滑的x值用于绘制直线
        x_smooth = np.linspace(min(known_x), max(known_x), 200)
        y_smooth = poly_func(x_smooth)
        
        # 绘制拟合直线（虚线样式）
        ax.plot(x_smooth, y_smooth, color='#FF6B35', linewidth=2.5, 
                alpha=0.8, linestyle='--', zorder=3,  # 改为虚线
                label='Fitted Line')  # 改为英文
        
        # 计算相关系数
        correlation = np.corrcoef(known_x, known_y)[0, 1]
        
        print(f"拟合直线已添加 - 使用{len(known_x)}个已知推理长度的数据点")
        print(f"线性拟合方程: y = {coefficients[0]:.4f}x + {coefficients[1]:.2f}")
        print(f"相关系数: {correlation:.3f}")

# Set axis limits first - before label positioning
#ax.set_ylim(30, 75)
ax.set_ylim(33, 73)
ax.set_xlim(-2000, unknown_x + max_iflen * 0.15)

# Add shaded region for unknown inference length
unknown_width = max_iflen * 0.15
rect = Rectangle((unknown_x - unknown_width/2, ax.get_ylim()[0]), 
                unknown_width, ax.get_ylim()[1] - ax.get_ylim()[0],
                facecolor='lightgray', alpha=0.2, zorder=0)
ax.add_patch(rect)

# Advanced label positioning to minimize overlaps
used_positions = []  # Track used positions to avoid overlaps

def shorten_model_name(model_name):
    """Shorten long model names for better display"""
    # Handle specific long model names
    name_mapping = {
        "Qwen3-Coder-30B-A3B-Instruct": "Qwen3-Coder-30B",
        "Qwen3-235B-A22B": "Qwen3-235B",
        "hunyuan-A13B": "Hunyuan-A13B",
        "Qwen3-235B-A22B-Thinking-2507": "Qwen3-235B-Thinking",
        "Qwen3-235B-A22B-Instruct-2507": "Qwen3-235B-Instruct",
        "Qwen3-Coder-480B-A35B-Instruct": "Qwen3-Coder-480B",
        "Claude Sonnet 4 (20250514)": "Claude Sonnet 4",
        "Claude 3.7 Sonnet (20250219)": "Claude 3.7 Sonnet",
        "Claude 3.5 Sonnet (20241022)": "Claude 3.5 Sonnet",
    }
    
    return name_mapping.get(model_name, model_name)

def get_special_position_for_overlapping_models(model_name, x, y, used_positions, ax):
    """Handle special positioning for the three overlapping models"""
    # Define specific positions for the three overlapping models
    special_positions = {
        "Qwen3-Coder-30B-A3B-Instruct": (-12, 8, 'right', 'bottom'),   # Top-left, much closer
        "Qwen3-235B-A22B": (15, 0, 'left', 'center'),                  # Right, closer
        "hunyuan-A13B": (-12, -8, 'right', 'top'),                      # Bottom-left, much closer
    }
    
    if model_name in special_positions:
        offset_x, offset_y, ha, va = special_positions[model_name]
        
        # Calculate and store bounding box
        display_name = shorten_model_name(model_name)
        text_width, text_height = get_text_bbox_size(display_name, fontsize=8)
        x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
        y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
        text_width_data = text_width * x_range / 800
        text_height_data = text_height * y_range / 600
        
        label_x_data = x + offset_x * x_range / 800
        label_y_data = y + offset_y * y_range / 600
        
        if ha == 'left':
            label_left = label_x_data
            label_right = label_x_data + text_width_data
        elif ha == 'right':
            label_left = label_x_data - text_width_data
            label_right = label_x_data
        else:  # center
            label_left = label_x_data - text_width_data / 2
            label_right = label_x_data + text_width_data / 2
            
        if va == 'bottom':
            label_bottom = label_y_data
            label_top = label_y_data + text_height_data
        elif va == 'top':
            label_bottom = label_y_data - text_height_data
            label_top = label_y_data
        else:  # center
            label_bottom = label_y_data - text_height_data / 2
            label_top = label_y_data + text_height_data / 2
        
        used_positions.append((label_left, label_right, label_bottom, label_top))
        return offset_x, offset_y, ha, va
    
    return None

def get_text_bbox_size(text, fontsize=8):
    """Estimate text bounding box size"""
    # Rough estimation: each character is about 0.6 * fontsize wide, height is fontsize
    width = len(text) * fontsize * 0.6
    height = fontsize * 1.2  # Add some padding
    return width, height

def find_non_overlapping_position(x, y, model_name, used_positions, ax):
    """Find a position that doesn't overlap with existing labels"""
    text_width, text_height = get_text_bbox_size(model_name, fontsize=8)
    
    # Convert text dimensions to data coordinates
    # Get axis dimensions for scaling
    x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    
    # Convert pixel-based text size to data coordinates (rough approximation)
    text_width_data = text_width * x_range / 800  # Assuming 800px figure width
    text_height_data = text_height * y_range / 600  # Assuming 600px figure height
    
    # Extended list of candidate positions with varying distances
    base_positions = [
        # Close positions
        (15, 0, 'left', 'center'),     # Right
        (-15, 0, 'right', 'center'),   # Left  
        (0, 15, 'center', 'bottom'),   # Top
        (0, -15, 'center', 'top'),     # Bottom
        (12, 12, 'left', 'bottom'),    # Top-right
        (-12, 12, 'right', 'bottom'),  # Top-left
        (12, -12, 'left', 'top'),      # Bottom-right
        (-12, -12, 'right', 'top'),    # Bottom-left
        
        # Medium distance positions
        (25, 0, 'left', 'center'),     
        (-25, 0, 'right', 'center'),   
        (0, 25, 'center', 'bottom'),   
        (0, -25, 'center', 'top'),     
        (20, 20, 'left', 'bottom'),    
        (-20, 20, 'right', 'bottom'),  
        (20, -20, 'left', 'top'),      
        (-20, -20, 'right', 'top'),    
        
        # Far positions for difficult cases
        (35, 0, 'left', 'center'),     
        (-35, 0, 'right', 'center'),   
        (0, 35, 'center', 'bottom'),   
        (0, -35, 'center', 'top'),     
        (30, 15, 'left', 'bottom'),    
        (-30, 15, 'right', 'bottom'),  
        (30, -15, 'left', 'top'),      
        (-30, -15, 'right', 'top'),
        
        # Additional diagonal positions
        (15, 25, 'left', 'bottom'),
        (-15, 25, 'right', 'bottom'),
        (15, -25, 'left', 'top'),
        (-15, -25, 'right', 'top'),
        (25, 35, 'left', 'bottom'),
        (-25, 35, 'right', 'bottom'),
        (25, -35, 'left', 'top'),
        (-25, -35, 'right', 'top'),
    ]
    
    for offset_x, offset_y, ha, va in base_positions:
        # Convert offset from points to data coordinates
        label_x_data = x + offset_x * x_range / 800
        label_y_data = y + offset_y * y_range / 600
        
        # Calculate label bounding box in data coordinates
        if ha == 'left':
            label_left = label_x_data
            label_right = label_x_data + text_width_data
        elif ha == 'right':
            label_left = label_x_data - text_width_data
            label_right = label_x_data
        else:  # center
            label_left = label_x_data - text_width_data / 2
            label_right = label_x_data + text_width_data / 2
            
        if va == 'bottom':
            label_bottom = label_y_data
            label_top = label_y_data + text_height_data
        elif va == 'top':
            label_bottom = label_y_data - text_height_data
            label_top = label_y_data
        else:  # center
            label_bottom = label_y_data - text_height_data / 2
            label_top = label_y_data + text_height_data / 2
        
        # Check if this position conflicts with existing labels
        conflict = False
        for used_bbox in used_positions:
            used_left, used_right, used_bottom, used_top = used_bbox
            
            # Check for bounding box overlap
            if not (label_right < used_left or label_left > used_right or 
                    label_top < used_bottom or label_bottom > used_top):
                conflict = True
                break
        
        if not conflict:
            # Store the bounding box for future conflict checking
            used_positions.append((label_left, label_right, label_bottom, label_top))
            return offset_x, offset_y, ha, va
    
    # If all positions conflict, use a far position and hope for the best
    offset_x, offset_y = 45, 0
    ha, va = 'left', 'center'
    label_x_data = x + offset_x * x_range / 800
    label_y_data = y + offset_y * y_range / 600
    
    label_left = label_x_data
    label_right = label_x_data + text_width_data
    label_bottom = label_y_data - text_height_data / 2
    label_top = label_y_data + text_height_data / 2
    
    used_positions.append((label_left, label_right, label_bottom, label_top))
    return offset_x, offset_y, ha, va

# Add direct labels on scatter points with advanced anti-overlap positioning
unknown_models = [(model, vals) for model, vals in data.items() if vals["IFLEN"] == 0]
known_models = [(model, vals) for model, vals in data.items() if vals["IFLEN"] > 0]

# Handle unknown inference length models with vertical distribution
for i, (model, vals) in enumerate(unknown_models):
    x = unknown_x
    y = vals["AVG"]
    
    display_name = shorten_model_name(model)
    
    # Alternate left and right positioning for unknown models
    if i % 2 == 0:  # Even index - put on the left
        offset_x = -15
        ha = 'right'
    else:  # Odd index - put on the right
        offset_x = 15
        ha = 'left'
    
    # Calculate vertical offset to spread models vertically
    total_unknown = len(unknown_models)
    if total_unknown > 1:
        # Calculate spacing to distribute evenly across available vertical space
        y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
        base_spacing = min(12, y_range / total_unknown * 0.5)  # Reduced spacing further
        # Group left and right models separately for vertical distribution
        group_index = i // 2  # Group index (0, 0, 1, 1, 2, 2, ...)
        groups_in_side = (total_unknown + 1) // 2  # How many groups on each side
        if groups_in_side > 1:
            offset_y = (group_index - (groups_in_side - 1) / 2) * base_spacing
        else:
            offset_y = 0
    else:
        offset_y = 0
    
    va = 'center'
    
    # Store bounding box for conflict checking with known models
    text_width, text_height = get_text_bbox_size(display_name, fontsize=8)
    x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    text_width_data = text_width * x_range / 800
    text_height_data = text_height * y_range / 600
    
    label_x_data = x + offset_x * x_range / 800
    label_y_data = y + offset_y * y_range / 600
    
    if ha == 'right':
        label_left = label_x_data - text_width_data
        label_right = label_x_data
    else:  # 'left'
        label_left = label_x_data
        label_right = label_x_data + text_width_data
    
    label_bottom = label_y_data - text_height_data / 2
    label_top = label_y_data + text_height_data / 2
    
    used_positions.append((label_left, label_right, label_bottom, label_top))
    
    ax.annotate(display_name, (x, y), xytext=(offset_x, offset_y), 
               textcoords='offset points', fontsize=8, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        alpha=0.95, edgecolor=colors[vals["category"]], linewidth=1),
               ha=ha, va=va, zorder=10)

# Handle known inference length models with smart positioning
for model, vals in known_models:
    x = vals["IFLEN"]
    y = vals["AVG"]
    
    display_name = shorten_model_name(model)
    
    # Check if this is one of the special overlapping models
    special_pos = get_special_position_for_overlapping_models(model, x, y, used_positions, ax)
    
    if special_pos:
        offset_x, offset_y, ha, va = special_pos
    else:
        # Use advanced positioning for other known inference length models
        offset_x, offset_y, ha, va = find_non_overlapping_position(x, y, display_name, used_positions, ax)
    
    ax.annotate(display_name, (x, y), xytext=(offset_x, offset_y), 
               textcoords='offset points', fontsize=8, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        alpha=0.95, edgecolor=colors[vals["category"]], linewidth=1),
               ha=ha, va=va, zorder=10)

# Customize x-axis with better tick positioning
known_ticks = np.linspace(0, max_iflen, 6)
all_ticks = list(known_ticks) + [unknown_x]
tick_labels = [f"{int(t/1000)}K" if t < unknown_x else "Unknown" for t in all_ticks]
ax.set_xticks(all_ticks)
ax.set_xticklabels(tick_labels, rotation=0)

# Enhanced labels and title
ax.set_xlabel('Model Inference Output Length (Tokens)', fontweight='bold', fontsize=14)
ax.set_ylabel('ArtifactsBench Average Score', fontweight='bold', fontsize=14)
ax.set_title('ArtifactsBench Performance vs. Model Inference Length', 
             fontweight='bold', fontsize=16, pad=30)
             #fontweight='bold', fontsize=16, pad=24)

# Add legend for model categories with moderate sizing
legend_elements = [plt.scatter([], [], c=color, s=100, alpha=0.8, 
                              edgecolors='white', linewidth=1.2, label=cat.title()) 
                  for cat, color in colors.items()]

# ========== 新增：如果显示拟合曲线，添加到图例中 ==========
if SHOW_FIT_CURVE and 'known_x' in locals() and len(known_x) >= 2:
    # 添加拟合曲线到图例
    fit_curve_line = plt.Line2D([0], [0], color='#FF6B35', linewidth=2.5, 
                               alpha=0.8, linestyle='--', label='Fitted Line')  # 改为英文
    legend_elements.append(fit_curve_line)

ax.legend(handles=legend_elements, loc='lower right', frameon=True, 
         fancybox=True, shadow=True, fontsize=11, title='Model Category',
         title_fontsize=12)

# Enhanced grid
ax.grid(True, linestyle='-', alpha=0.3, linewidth=0.8)
ax.set_axisbelow(True)

# Add performance zones with subtle background colors
ax.axhspan(60, 75, alpha=0.1, color='green', zorder=0)  # High performance: 60-75
ax.axhspan(45, 60, alpha=0.1, color='yellow', zorder=0)  # Medium performance: 45-60
ax.axhspan(30, 45, alpha=0.1, color='orange', zorder=0)  # Lower performance: 30-45

# Add text annotations for performance zones - positioned to avoid label conflicts
ax.text(max_iflen * 0.15, 67.5, 'High Performance', fontsize=11, 
        alpha=0.7, style='italic', ha='center', fontweight='bold')
ax.text(max_iflen * 0.15, 52.5, 'Medium Performance', fontsize=11, 
        alpha=0.7, style='italic', ha='center', fontweight='bold')
ax.text(max_iflen * 0.15, 37.5, 'Lower Performance', fontsize=11, 
        alpha=0.7, style='italic', ha='center', fontweight='bold')

# Adjust layout for publication quality
plt.tight_layout()

# Add subtle border around the entire plot
for spine in ax.spines.values():
    spine.set_linewidth(1.5)
    spine.set_color('#333333')

plt.show()

print("图表已生成！标签重叠问题已修复：")
print("- Qwen3-Coder-30B-A3B-Instruct -> Qwen3-Coder-30B (左上角，位置已调整)")
print("- Qwen3-235B-A22B -> Qwen3-235B (右边)")  
print("- hunyuan-A13B -> Hunyuan-A13B (左下角，位置已调整)")

# ========== 新增：拟合曲线状态说明 ==========
print(f"\n拟合直线功能: {'已启用' if SHOW_FIT_CURVE else '已关闭'}")
print("提示：可以通过修改代码中的 SHOW_FIT_CURVE 变量来控制是否显示拟合直线")
if SHOW_FIT_CURVE:
    print("- 拟合直线使用已知推理长度的数据点进行线性拟合")
    print("- 直线为橙色虚线，帮助可视化数据趋势")

# Optional: Save in publication formats (uncomment when needed)
# plt.savefig('src/artifactsbench_analysis.pdf', dpi=300, bbox_inches='tight')
# plt.savefig('src/artifactsbench_analysis.png', dpi=300, bbox_inches='tight')