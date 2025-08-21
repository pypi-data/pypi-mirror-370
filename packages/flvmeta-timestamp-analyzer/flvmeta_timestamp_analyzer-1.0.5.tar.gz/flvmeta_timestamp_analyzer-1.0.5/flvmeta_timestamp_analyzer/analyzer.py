#!/usr/bin/env python3
"""
FLV音视频时间戳分析工具
用法: 
  python3 flv_timestamp_analyzer.py <input.flv> [output.html]
示例:
  python3 flv_timestamp_analyzer.py test.flv
  python3 flv_timestamp_analyzer.py test.flv analysis.html
"""

import json
import os
import sys
import subprocess
import traceback
from pyecharts.charts import Line, Grid
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode  # 导入JsCode
from collections import defaultdict

# 检查依赖项
def check_dependencies():
    # 检查flvmeta是否安装
    try:
        version_info = subprocess.run(["flvmeta", "-V"], capture_output=True, text=True)
        if version_info.returncode != 0:
            raise Exception("flvmeta执行失败")
        print(f"检测到flvmeta版本: {version_info.stdout.strip()}")
    except Exception as e:
        print("错误: 需要安装flvmeta工具")
        print("安装方法: ")
        print("  macOS: brew install flvmeta")
        print("  Linux: sudo apt-get install flvmeta 或从源码编译")
        print("  Windows: 下载 https://github.com/noirotm/flvmeta/releases")
        print("  源码: https://github.com/noirotm/flvmeta")
        return False
    
    # 检查pyecharts是否安装
    try:
        import pyecharts
        print(f"检测到pyecharts版本: {pyecharts.__version__}")
    except ImportError:
        print("错误: 需要安装pyecharts库")
        print("安装方法: pip install pyecharts")
        return False
        
    return True
    
# 使用flvmeta解析FLV文件 - 增强错误处理
def parse_flv_with_flvmeta(flv_path):
    if not os.path.exists(flv_path):
        raise FileNotFoundError(f"文件不存在: {flv_path}")
    
    try:
        # 调用flvmeta解析FLV文件, 将JSON输出到stdout
        print(f"调用flvmeta解析: {flv_path}")
        cmd = ["flvmeta", "-F", "-j", flv_path]
        # 设置 text=True, subprocess 会使用系统默认编码解码
        # 如果遇到编码问题, 可能需要手动指定编码, e.g., encoding='utf-8'
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if not result.stdout:
            raise RuntimeError("flvmeta没有生成任何输出。")
    
        # 直接从stdout解析JSON
        return json.loads(result.stdout)
    
    except subprocess.CalledProcessError as e:
        error_msg = f"flvmeta执行错误 (退出码 {e.returncode}):\n{e.stderr}"
        if "not a FLV" in e.stderr:
            error_msg += "\n提示: 输入文件可能不是有效的FLV格式"
        raise RuntimeError(error_msg) from e
    
    except json.JSONDecodeError as e:
        # 打印前500个字符以帮助调试
        stdout_preview = result.stdout.strip()[:500]
        raise RuntimeError(f"JSON解析错误: {e}\n收到的输出 (前500字符):\n{stdout_preview}..." ) from e
    
# 分离音视频时间戳并分析
def analyze_timestamps(json_data, flv_path):
    # 分离音频和视频标签
    audio_timestamps = []
    video_timestamps = []
    
    # 确保tags字段存在
    if "tags" not in json_data:
        metadata = json_data.get("metadata", {})
        raise ValueError(f"JSON数据中缺少'tags'字段。flvmeta可能未正确解析文件。\n元数据: {metadata}")
    
    for i, tag in enumerate(json_data['tags']):
        if 'type' not in tag:
            continue
            
        if tag['type'] == 'audio':
            audio_timestamps.append({
                "index": i,
                "timestamp": tag.get('timestamp', 0),
                "dataSize": tag.get('dataSize', 0)
            })
        elif tag['type'] == 'video':
            video_timestamps.append({
                "index": i,
                "timestamp": tag.get('timestamp', 0),
                "dataSize": tag.get('dataSize', 0)
            })
    
    # 计算差值函数
    def calculate_diffs(timestamps):
        if len(timestamps) < 2:
            return [], [], []
        
        # 按时间戳排序
        timestamps_sorted = sorted(timestamps, key=lambda x: x['timestamp'])
        timestamps_values = [t['timestamp'] for t in timestamps_sorted]
        diffs = [timestamps_values[i] - timestamps_values[i-1] for i in range(1, len(timestamps_values))]
        
        # 获取每个差值对应的位置（结束时间戳）
        positions = [t['timestamp'] for t in timestamps_sorted[1:]]
        
        return timestamps_sorted, positions, diffs
    
    # 处理音频时间戳
    audio_sorted, audio_positions, audio_diffs = calculate_diffs(audio_timestamps)
    # 处理视频时间戳
    video_sorted, video_positions, video_diffs = calculate_diffs(video_timestamps)
    
    # 计算统计信息
    def calculate_stats(diffs, label):
        if not diffs:
            return {}
        
        avg = sum(diffs) / len(diffs)
        max_val = max(diffs)
        min_val = min(diffs)
        
        # 检测异常点
        anomalies = []
        for i, diff in enumerate(diffs):
            # 检测时间回退
            if diff < 0:
                anomalies.append({
                    "type": "time_reversal",
                    "position": audio_positions[i] if label == "audio" else video_positions[i],
                    "value": diff,
                    "index": audio_sorted[i+1]['index'] if label == "audio" else video_sorted[i+1]['index'],
                    "start_time": audio_sorted[i]['timestamp'] if label == "audio" else video_sorted[i]['timestamp'],
                    "end_time": audio_sorted[i+1]['timestamp'] if label == "audio" else video_sorted[i+1]['timestamp']
                })
            # 检测大跳跃 (超过平均值的5倍)
            elif diff > avg * 5:
                anomalies.append({
                    "type": "large_jump",
                    "position": audio_positions[i] if label == "audio" else video_positions[i],
                    "value": diff,
                    "index": audio_sorted[i+1]['index'] if label == "audio" else video_sorted[i+1]['index'],
                    "start_time": audio_sorted[i]['timestamp'] if label == "audio" else video_sorted[i]['timestamp'],
                    "end_time": audio_sorted[i+1]['timestamp'] if label == "audio" else video_sorted[i+1]['timestamp']
                })
        # 检测缺失帧 (超过平均值的10倍)
            elif diff > avg * 10:
                anomalies.append({
                    "type": "missing_frame",
                    "position": audio_positions[i] if label == "audio" else video_positions[i],
                    "value": diff,
                    "index": audio_sorted[i+1]['index'] if label == "audio" else video_sorted[i+1]['index'],
                    "start_time": audio_sorted[i]['timestamp'] if label == "audio" else video_sorted[i]['timestamp'],
                    "end_time": audio_sorted[i+1]['timestamp'] if label == "audio" else video_sorted[i+1]['timestamp']
                })
        
        return {
            "avg": avg,
            "max": max_val,
            "min": min_val,
            "anomalies": anomalies
        }
    
    audio_stats = calculate_stats(audio_diffs, "audio") if audio_diffs else {}
    video_stats = calculate_stats(video_diffs, "video") if video_diffs else {}
    
    # 文件基本信息
    filename = os.path.basename(flv_path)
    
    # 尝试获取元数据
    metadata = {}
    for tag in json_data['tags']:
        if tag.get('type') == 'scriptData' and tag.get('scriptDataObject', {}).get('name') == 'onMetaData':
            metadata = tag['scriptDataObject'].get('metadata', {})
            break
    
    return {
        "filename": filename,
        "metadata": metadata,
        "audio": {
            "timestamps": audio_timestamps,
            "sorted": audio_sorted,
            "positions": audio_positions,
            "diffs": audio_diffs,
            "stats": audio_stats
        },
        "video": {
            "timestamps": video_timestamps,
            "sorted": video_sorted,
            "positions": video_positions,
            "diffs": video_diffs,
            "stats": video_stats
        },
        "total_tags": len(json_data['tags'])
    }

# 生成ECharts图表（音视频分开）
def create_charts(data, output_path):
    """创建时间戳增量分析图表"""
    
    def _create_stream_chart(stream_data, stream_name, color):
        if not stream_data['diffs']:
            return None
            
        # 准备数据
        timestamps = stream_data['sorted']
        diffs = stream_data['diffs']
        positions = stream_data['positions']
        stats = stream_data['stats']
        
        # 创建数据点列表：[(时间戳, 增量)]
        data_points = []
        for i in range(len(diffs)):
            # 使用后一个时间戳作为x轴值，增量作为y轴值
            timestamp = timestamps[i+1]['timestamp']
            diff = diffs[i]
            data_points.append([timestamp, diff])
        
        # 创建标记点数据（异常点）
        mark_points_data = []
        if stats.get('anomalies'):
            for anom in stats['anomalies']:
                # 找到异常点在数据点列表中的位置
                for i, (timestamp, diff) in enumerate(data_points):
                    if timestamp == anom['end_time']:
                        mark_points_data.append(
                            opts.MarkPointItem(
                                name=anom['type'],
                                coord=[timestamp, diff],
                                value=diff,
                                itemstyle_opts=opts.ItemStyleOpts(color="red")
                            )
                        )
                        break
        
        # 创建折线图
        chart = Line(init_opts=opts.InitOpts(width="100%", height="500px"))
        chart.add_xaxis([point[0] for point in data_points])
        chart.add_yaxis(
            series_name=f"{stream_name}增量(ms)",
            y_axis=[point[1] for point in data_points],
            is_smooth=False,
            is_symbol_show=True,
            symbol="circle",
            symbol_size=4,
            linestyle_opts=opts.LineStyleOpts(width=1, color=color),
            itemstyle_opts=opts.ItemStyleOpts(border_width=1, border_color=color, color=color),
            markpoint_opts=opts.MarkPointOpts(
                data=mark_points_data,
                symbol_size=50
            ) if mark_points_data else None,
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(y=stats.get('avg', 0), name="平均值")
                ],
                linestyle_opts=opts.LineStyleOpts(type_="dashed", width=1)
            ),
        )
        
        # 设置全局选项
        chart.set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{stream_name}时间戳增量分析",
                pos_left="center",
                pos_top="10px",
                title_textstyle_opts=opts.TextStyleOpts(font_size=16, font_weight="bold")
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                trigger="axis",
                trigger_on="mousemove|click",
                axis_pointer_type="cross",
                background_color="rgba(255,255,255,0.9)",
                border_color="#ccc",
                border_width=1,
                textstyle_opts=opts.TextStyleOpts(color="#000"),
                formatter=JsCode("function(params){"
                "if(params.length>0){"
                "var param=params[0];"
                "var time=param.axisValue;"
                "var value=param.data[1];"
                "return param.seriesName+'<br/>'+"
                "'时间戳: '+time+'ms<br/>'+"
                "'增量: '+value+'ms';"
                "}"
                "return '';"
                "}")
            ),
            xaxis_opts=opts.AxisOpts(
                name="时间戳(ms)",
                name_location="middle",
                name_gap=30,
                name_textstyle_opts=opts.TextStyleOpts(font_size=12),
                type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.2)),
                axisline_opts=opts.AxisLineOpts(is_show=True),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(rotate=0, font_size=10)
            ),
            yaxis_opts=opts.AxisOpts(
                name="增量(ms)",
                name_location="middle",
                name_gap=50,
                name_textstyle_opts=opts.TextStyleOpts(font_size=12),
                type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.2)),
                axisline_opts=opts.AxisLineOpts(is_show=True),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(font_size=10)
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    is_show=True,
                    type_="inside",
                    range_start=0,
                    range_end=100,
                    orient="horizontal"
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    type_="slider",
                    range_start=0,
                    range_end=100,
                    orient="horizontal",
                    pos_bottom="10px"
                )
            ],
            legend_opts=opts.LegendOpts(
                is_show=True,
                pos_top="30px",
                pos_right="20px"
            )
        )
        
        return chart
    
    # 创建音频和视频图表
    audio_chart = None
    if data['audio']['diffs']:
        audio_chart = _create_stream_chart(data['audio'], "音频", "#5470c6")
    
    video_chart = None
    if data['video']['diffs']:
        video_chart = _create_stream_chart(data['video'], "视频", "#91cc75")
    
    # 处理没有数据的情况
    if not audio_chart and not video_chart:
        print("没有足够的数据生成图表。")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>没有足够的数据生成图表 (No data to generate chart).</h1></body></html>")
        return output_path
    
    # 为每个图表创建独立的页面，实现独立控制
    from pyecharts.charts import Page
    
    # 创建独立页面布局
    page = Page(
        layout=Page.SimplePageLayout,
        page_title=f"{data['filename']} 分析报告"
    )
    
    # 添加图表到页面
    if audio_chart:
        page.add(audio_chart)
    if video_chart:
        page.add(video_chart)
    
    # 渲染图表
    page.render(output_path)
    return output_path

# 打印分析结果
def print_analysis_report(data):
    print("\n" + "="*60)
    print(f"FLV音视频时间戳分析报告: {data['filename']}")
    print("="*60)
    
    if data['metadata']:
        print(f"元数据: {json.dumps(data['metadata'], indent=2, ensure_ascii=False)}")
    
    print(f"\n总标签数: {data['total_tags']}")
    
    # 音频统计
    if data['audio']['timestamps']:
        audio_duration = max(t['timestamp'] for t in data['audio']['timestamps']) - min(t['timestamp'] for t in data['audio']['timestamps'])
        print(f"\n[音频统计]")
        print(f"音频帧数: {len(data['audio']['timestamps'])}")
        print(f"音频时长: {audio_duration}ms")
        if data['audio']['diffs']:
            stats = data['audio']['stats']
            print(f"平均间隔: {stats['avg']:.2f}ms | 最大间隔: {stats['max']}ms | 最小间隔: {stats['min']}ms")
            if stats.get('anomalies'):
                print("音频异常点:")
                for anom in stats['anomalies']:
                    anomaly_type = "时间回退" if anom['type'] == "time_reversal" else ("大跳跃" if anom['type'] == "large_jump" else "缺失帧")
                    print(f" - 位置 {anom['position']}ms: {anomaly_type} ({anom['value']}ms) [标签#{anom['index']}]")
            else:
                print("未检测到音频异常点")
    else:
        print("\n[音频] 无音频数据")
    
    # 视频统计
    if data['video']['timestamps']:
        video_duration = max(t['timestamp'] for t in data['video']['timestamps']) - min(t['timestamp'] for t in data['video']['timestamps'])
        print(f"\n[视频统计]")
        print(f"视频帧数: {len(data['video']['timestamps'])}")
        print(f"视频时长: {video_duration}ms")
        if data['video']['diffs']:
            stats = data['video']['stats']
            print(f"平均间隔: {stats['avg']:.2f}ms | 最大间隔: {stats['max']}ms | 最小间隔: {stats['min']}ms")
            if stats.get('anomalies'):
                print("视频异常点:")
                for anom in stats['anomalies']:
                    anomaly_type = "时间回退" if anom['type'] == "time_reversal" else ("大跳跃" if anom['type'] == "large_jump" else "缺失帧")
                    print(f" - 位置 {anom['position']}ms: {anomaly_type} ({anom['value']}ms) [标签#{anom['index']}]")
            else:
                print("未检测到视频异常点")
    else:
        print("\n[视频] 无视频数据")
    
    print("="*60)

def main(flv_path, output_path=None):
    try:
        # 使用flvmeta解析FLV文件
        print(f"调用flvmeta解析FLV文件: {flv_path}")
        json_data = parse_flv_with_flvmeta(flv_path)
        
        # 分析时间戳变化
        print("分析时间戳变化...")
        analysis_data = analyze_timestamps(json_data, flv_path)
        
        # 打印文本报告
        print_analysis_report(analysis_data)
        
        # 确定输出路径
        if not output_path:
            base_name = os.path.splitext(os.path.basename(flv_path))[0]
            output_path = f"{base_name}_timestamp_analysis.html"
        
        # 生成可视化图表
        print(f"生成可视化图表: {output_path}")
        actual_output_path = create_charts(analysis_data, output_path)
        
        print("\n分析完成!")
        print(f"图表已保存至: {os.path.abspath(output_path)}")
        return True
    
    except Exception as e:
        print("\n错误: 分析失败")
        print(f"错误信息: {str(e)}")
        print(f"详细错误: {traceback.format_exc()}")
        return False

def cli_main():
    """命令行入口点函数，供setuptools使用"""
    # 检查参数
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        sys.exit(0)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 获取输入文件路径
    flv_path = sys.argv[1]
    
    # 获取输出文件路径（可选）
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 执行分析
    success = main(flv_path, output_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    cli_main()
