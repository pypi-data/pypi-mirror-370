"""
PDF文本处理工具模块

该模块提供PDF文本字符分组、排序和过滤功能。
"""

import string
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.cluster import DBSCAN

from ..exceptions import PDFProcessingError

logger = logging.getLogger(__name__)


def divide_groups(chars: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    将PDF字符按照空间位置分组。
    
    根据字符的坐标位置使用聚类算法将字符分组，
    并对每组内的字符进行排序。
    
    Args:
        chars: PDF字符列表，每个字符包含位置和文本信息
        
    Returns:
        分组后的字符列表，每个组是一个字符列表
        
    Raises:
        PDFProcessingError: 当字符分组处理失败时抛出
    """
    if not chars:
        logger.warning("输入的字符列表为空")
        return []
        
    if not isinstance(chars, list):
        raise PDFProcessingError(f"字符参数必须是列表类型，但收到: {type(chars)}")
    
    try:
        logger.debug(f"开始处理 {len(chars)} 个字符的分组")
        
        words = {}  # 用于存储文字和坐标信息的字典
        points = []
        
        for char in chars:
            if not isinstance(char, dict):
                logger.warning(f"跳过无效的字符对象: {char}")
                continue
                
            # 验证字符对象必需的键
            required_keys = ['x0', 'y1', 'text']
            if not all(key in char for key in required_keys):
                logger.warning(f"字符对象缺少必需的键: {char}")
                continue
                
            point = (char['x0'], char['y1'])
            hash_value = hash(point)
            points.append(point)
            words[hash_value] = char
        
        if not points:
            logger.warning("没有有效的字符点可处理")
            return []
            
        points_groups = _divide_point(points)
        
        text_groups = []
        for group_points in points_groups.values():
            chars_in_group = []
            for point in group_points:
                key = hash(tuple(point))
                if key in words:
                    chars_in_group.append(words[key])
            
            if chars_in_group:
                sorted_chars = _sorted_chars(chars_in_group)
                text_groups.append(sorted_chars)
        
        logger.debug(f"成功分成 {len(text_groups)} 个字符组")
        return text_groups
        
    except Exception as e:
        logger.error(f"字符分组处理失败: {e}")
        raise PDFProcessingError(f"字符分组处理失败: {e}") from e


def _divide_point(points: List[Tuple[float, float]]) -> Dict[int, List[Tuple[float, float]]]:
    """
    使用DBSCAN算法对坐标点进行聚类。
    
    Args:
        points: 坐标点列表，每个点为(x, y)元组
        
    Returns:
        聚类结果字典，键为聚类标签，值为该聚类中的点列表
        
    Raises:
        PDFProcessingError: 当聚类失败时抛出
    """
    if not points:
        logger.warning("坐标点列表为空")
        return {}
        
    try:
        logger.debug(f"开始对 {len(points)} 个坐标点进行聚类")
        
        # 指定距离阈值
        threshold_distance = 40.0  # 可以根据需要修改这个值
        point_dict = {}
        
        # 将点列表转换为numpy数组供DBSCAN使用
        points_array = np.array(points)
        
        # 使用DBSCAN进行聚类
        dbscan = DBSCAN(eps=threshold_distance, min_samples=2)
        clusters = dbscan.fit(points_array)
        
        # 按聚类标签分组点
        for i, cluster_label in enumerate(clusters.labels_):
            if cluster_label not in point_dict:
                point_dict[cluster_label] = []
            point_dict[cluster_label].append(points[i])
        
        # 记录聚类结果
        non_noise_clusters = len([k for k in point_dict.keys() if k != -1])
        noise_points = len(point_dict.get(-1, []))
        logger.debug(f"聚类完成: {non_noise_clusters} 个聚类, {noise_points} 个噪声点")
        
        return point_dict
        
    except Exception as e:
        logger.error(f"坐标点聚类失败: {e}")
        raise PDFProcessingError(f"坐标点聚类失败: {e}") from e
        
def _sorted_chars(chars: List[Dict[str, Any]], tolerance: float = 1.0) -> List[Dict[str, Any]]:
    """
    对字符列表进行排序，先按行后按列。
    
    根据字符的Y坐标进行水平分组，然后在每组内按X坐标排序。
    对于垂直排列的单个字符，再按X坐标进行垂直分组。
    
    Args:
        chars: 字符列表，每个字符包含坐标信息
        tolerance: 位置容差值，用于判断字符是否在同一行或列
        
    Returns:
        排序后的字符列表
        
    Raises:
        PDFProcessingError: 当字符排序失败时抛出
    """
    if not chars:
        logger.debug("字符列表为空，返回空列表")
        return []
        
    if not isinstance(chars, list):
        raise PDFProcessingError(f"字符参数必须是列表类型，但收到: {type(chars)}")
        
    try:
        logger.debug(f"开始对 {len(chars)} 个字符进行排序")
        
        # 验证字符对象的必需字段
        required_keys = ['x0', 'x1', 'y0', 'y1', 'text']
        for i, char in enumerate(chars):
            if not isinstance(char, dict):
                raise PDFProcessingError(f"第 {i} 个字符不是字典类型: {char}")
            if not all(key in char for key in required_keys):
                raise PDFProcessingError(f"第 {i} 个字符缺少必需的键 {required_keys}: {char}")
        
        v_chars = []
        h_chars = sorted(chars, key=lambda x: x['y1'], reverse=True)
        horizontal_groups = []
        current_group = []
        
        if not h_chars:
            return []
            
        pre_top_y = h_chars[0]['y1']
        pre_bottom_y = h_chars[0]['y0']
        
        for char in h_chars:
            current_top_y = char['y1']
            current_bottom_y = char['y0']
            arrange = False
            
            # 检查标点符号的特殊处理
            if _is_punctuation(char['text']):
                over_top_y = min(current_top_y, pre_top_y)
                over_bottom_y = max(current_bottom_y, pre_bottom_y)
                
                if over_top_y >= over_bottom_y and (current_top_y - current_bottom_y) != 0:
                    overlay = (over_top_y - over_bottom_y) / (current_top_y - current_bottom_y)
                    arrange = overlay > 0.8

            if abs(current_top_y - pre_top_y) <= tolerance or arrange:
                current_group.append(char)
            else:
                # 如果不在容差范围内，则保存当前组并开始新的组
                if len(current_group) == 1:
                    v_chars.append(current_group[0])
                else:
                    current_group = sorted(current_group, key=lambda x: x['x0'], reverse=False)
                    horizontal_groups.append(current_group)
                current_group = [char]
                pre_top_y = current_top_y
                pre_bottom_y = current_bottom_y
        
        # 处理最后一组
        if len(current_group) == 1:
            v_chars.append(current_group[0])
        else:
            current_group = sorted(current_group, key=lambda x: x['x0'], reverse=False)
            horizontal_groups.append(current_group)
            
        # 如果没有垂直字符，直接返回水平分组的结果
        if not v_chars:
            chars_result = [char for group in horizontal_groups for char in group]
            return _filter_char_by_overlap(chars_result)
        
        # 处理垂直字符分组
        v_chars = sorted(v_chars, key=lambda x: x['x0'], reverse=False)
        vertical_groups = []
        current_group = []
        pre_mid_x = (v_chars[0]['x0'] + v_chars[0]['x1']) / 2.0
        
        for char in v_chars:
            current_mid_x = (char['x0'] + char['x1']) / 2.0
            if abs(current_mid_x - pre_mid_x) <= tolerance:
                current_group.append(char)
            else:
                # 如果不在容差范围内，则保存当前组并开始新的组
                current_group = sorted(current_group, key=lambda x: x['y1'], reverse=True)
                vertical_groups.append(current_group)
                current_group = [char]
                pre_mid_x = current_mid_x
        
        if current_group:
            current_group = sorted(current_group, key=lambda x: x['y1'], reverse=True)
            vertical_groups.append(current_group)
            
        # 合并水平和垂直分组的结果
        sorted_chars_result = [char for group in horizontal_groups for char in group]
        sorted_chars_result.extend([char for group in vertical_groups for char in group])
        
        filtered_chars = _filter_char_by_overlap(sorted_chars_result)
        logger.debug(f"字符排序完成，从 {len(chars)} 个字符过滤到 {len(filtered_chars)} 个字符")
        
        return filtered_chars
        
    except Exception as e:
        logger.error(f"字符排序失败: {e}")
        raise PDFProcessingError(f"字符排序失败: {e}") from e


def _filter_char_by_overlap(chars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    过滤重叠的字符。
    
    移除与前一个字符重叠度超过80%的重复字符。
    
    Args:
        chars: 字符列表
        
    Returns:
        过滤后的字符列表
        
    Raises:
        PDFProcessingError: 当字符过滤失败时抛出
    """
    if not chars:
        return []
        
    if not isinstance(chars, list):
        raise PDFProcessingError(f"字符参数必须是列表类型，但收到: {type(chars)}")
        
    try:
        logger.debug(f"开始过滤 {len(chars)} 个字符的重叠")
        
        # 创建字符列表的副本以避免修改原列表时出现问题
        filtered_chars = chars.copy()
        removed_count = 0
        
        for index in range(len(filtered_chars) - 1, 0, -1):
            current_char = filtered_chars[index]
            pre_char = filtered_chars[index - 1]
            
            # 验证字符对象的必需字段
            required_keys = ['x0', 'y0', 'x1', 'y1', 'text']
            if not all(key in current_char for key in required_keys):
                logger.warning(f"当前字符缺少必需的键: {current_char}")
                continue
            if not all(key in pre_char for key in required_keys):
                logger.warning(f"前一个字符缺少必需的键: {pre_char}")
                continue
                
            # 只处理相同文本的字符
            if current_char['text'] != pre_char['text']:
                continue
                
            overlap = _calculate_overlap(
                [current_char['x0'], current_char['y0'], current_char['x1'], current_char['y1']], 
                [pre_char['x0'], pre_char['y0'], pre_char['x1'], pre_char['y1']]
            )
            
            # 如果重叠度超过80%，删除当前字符
            if overlap > 0.8:
                del filtered_chars[index]
                removed_count += 1
        
        logger.debug(f"字符过滤完成，移除了 {removed_count} 个重叠字符")
        return filtered_chars
        
    except Exception as e:
        logger.error(f"字符过滤失败: {e}")
        raise PDFProcessingError(f"字符过滤失败: {e}") from e

def _calculate_overlap(rect1: List[float], rect2: List[float]) -> float:
    """
    计算两个矩形的重叠比例。
    
    Args:
        rect1: 第一个矩形的坐标 [x0, y0, x1, y1]
        rect2: 第二个矩形的坐标 [x0, y0, x1, y1]
        
    Returns:
        重叠比例 (0.0 到 1.0 之间)
        
    Raises:
        PDFProcessingError: 当矩形坐标无效时抛出
    """
    if not isinstance(rect1, (list, tuple)) or len(rect1) != 4:
        raise PDFProcessingError(f"rect1 必须是包含4个元素的列表或元组，但收到: {rect1}")
    if not isinstance(rect2, (list, tuple)) or len(rect2) != 4:
        raise PDFProcessingError(f"rect2 必须是包含4个元素的列表或元组，但收到: {rect2}")
        
    try:
        # 解析矩形坐标
        x1_rect1, y1_rect1, x2_rect1, y2_rect1 = rect1
        x1_rect2, y1_rect2, x2_rect2, y2_rect2 = rect2

        # 验证矩形坐标的有效性
        if x2_rect1 <= x1_rect1 or y2_rect1 <= y1_rect1:
            logger.warning(f"无效的矩形1坐标: {rect1}")
            return 0.0
        if x2_rect2 <= x1_rect2 or y2_rect2 <= y1_rect2:
            logger.warning(f"无效的矩形2坐标: {rect2}")
            return 0.0

        # 计算矩形面积
        area_rect1 = (x2_rect1 - x1_rect1) * (y2_rect1 - y1_rect1)
        area_rect2 = (x2_rect2 - x1_rect2) * (y2_rect2 - y1_rect2)

        # 计算重叠部分的坐标
        x1_overlap = max(x1_rect1, x1_rect2)
        y1_overlap = max(y1_rect1, y1_rect2)
        x2_overlap = min(x2_rect1, x2_rect2)
        y2_overlap = min(y2_rect1, y2_rect2)

        # 计算重叠部分的宽度和高度
        width_overlap = max(0, x2_overlap - x1_overlap)
        height_overlap = max(0, y2_overlap - y1_overlap)

        # 计算重叠部分的面积
        area_overlap = width_overlap * height_overlap

        # 计算重合程度 (相对于较小矩形的面积)
        min_area = min(area_rect1, area_rect2)
        if min_area == 0:
            logger.warning("矩形面积为0，返回重叠比例0")
            return 0.0
            
        overlap_ratio = area_overlap / min_area
        
        # 确保重叠比例在合理范围内
        overlap_ratio = max(0.0, min(1.0, overlap_ratio))
        
        return overlap_ratio
        
    except (TypeError, ValueError) as e:
        logger.error(f"计算矩形重叠比例时发生错误: {e}")
        raise PDFProcessingError(f"计算矩形重叠比例失败: {e}") from e

def _is_punctuation(char: str) -> bool:
    """
    判断字符是否为标点符号。
    
    包含中英文标点符号的判断。
    
    Args:
        char: 要判断的字符
        
    Returns:
        如果是标点符号返回True，否则返回False
    """
    if not isinstance(char, str):
        logger.warning(f"输入的字符不是字符串类型: {char}")
        return False
        
    # 包含中英文标点符号的集合
    punctuation_set = set(string.punctuation + '，。；：！？【】（）《》''""－／％')
    return char in punctuation_set