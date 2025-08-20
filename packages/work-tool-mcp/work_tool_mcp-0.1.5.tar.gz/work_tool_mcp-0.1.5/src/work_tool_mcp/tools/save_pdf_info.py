"""
PDF信息提取工具模块

该模块提供从PDF文件中提取文本、字体、颜色等信息的功能。
"""

import os
import logging
import pdfplumber

from datetime import datetime
from typing import Any, Dict

from .pdf_handler import divide_groups  
from .excel_handler import ExcelHandler
from ..constants.fonts import FONT_MAP
from ..exceptions import PDFError, PDFParsingError, ValidationError

logger = logging.getLogger(__name__)

def save_pdf_info(pdf_filepath: str, output_folder: str) -> Dict[str, Any]:
    """
    获取PDF文件的详细信息。
    
    提取PDF文件中的文本、字体、颜色、字号等信息，
    并按页面组织这些信息。
    
    Args:
        pdf_filepath: PDF文件的完整路径
        output_folder: 输出文件夹路径（可选，当前版本未使用）
        
    Returns:
        包含PDF信息的字典，包含以下键：
        - filename: 文件路径
        - basename: 文件基础名称（不含扩展名）
        - fonts: 文件中使用的所有字体列表
        - colors: 文件中使用的所有颜色列表
        - size: 文件中使用的所有字号列表
        - pages: 按页面组织的详细信息
        
    Raises:
        ValidationError: 当文件路径无效时抛出
        PDFParsingError: 当PDF解析失败时抛出
        PDFError: 当PDF处理失败时抛出
    """
    # 验证输入参数
    if not pdf_filepath:
        raise ValidationError("PDF文件路径不能为空")
        
    if not isinstance(pdf_filepath, str):
        raise ValidationError(f"PDF文件路径必须是字符串类型，但收到: {type(pdf_filepath)}")
        
    if not os.path.exists(pdf_filepath):
        raise ValidationError(f"PDF文件不存在: {pdf_filepath}")
        
    if not pdf_filepath.lower().endswith('.pdf'):
        raise ValidationError(f"文件不是PDF格式: {pdf_filepath}")
        
    try:
        logger.info(f"开始提取PDF信息: {pdf_filepath}")
        
        # 初始化文件信息结构
        file_info: Dict[str, Any] = {
            "filename": pdf_filepath, 
            "basename": os.path.splitext(os.path.basename(pdf_filepath))[0],
            "fonts": set(),
            "colors": set(),
            "size": set(),
            "pages": {},
        }
        
        with pdfplumber.open(pdf_filepath) as pdf_data:
            if not pdf_data.pages:
                logger.warning(f"PDF文件没有页面: {pdf_filepath}")
                return _finalize_file_info(file_info)
                
            logger.debug(f"PDF包含 {len(pdf_data.pages)} 页")
            
            for page_index, page in enumerate(pdf_data.pages):
                try:
                    page_info = _process_page(page, page_index + 1)
                    
                    # 合并页面信息到文件信息
                    file_info["fonts"].update(page_info["fonts"])
                    file_info["colors"].update(page_info["colors"])
                    file_info["size"].update(page_info["size"])
                    file_info["pages"][f"页面 {page_index + 1}"] = page_info
                    
                except Exception as e:
                    logger.error(f"处理第 {page_index + 1} 页时发生错误: {e}")
                    # 继续处理其他页面，不中断整个流程
                    continue
        
        result = _finalize_file_info(file_info=file_info)
        logger.info(f"PDF信息提取完成: {len(result['pages'])} 页")

        formatted_timestamp = datetime.now().strftime("%Y%m%d")
        
        logger.info(f"开始保存PDF信息到Excel文件: {formatted_timestamp}")

        info_file = os.path.join(output_folder, f"PDF-Info({formatted_timestamp}).xlsx")
        if os.path.exists(info_file):
            # 如果目标目录存在，则删除目录及其内容
            os.remove(info_file)
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(info_file), exist_ok=True)
        ExcelHandler(info_file).save_pdf_info_to_excel(data=result, is_size=True)
        logger.info(f"字号识别文件已保存: {info_file}")
        ExcelHandler(info_file).save_pdf_info_to_excel(data=result, is_font=True)
        logger.info(f"字体识别文件已保存: {info_file}")
        ExcelHandler(info_file).save_pdf_info_to_excel(data=result, is_color=True)
        logger.info(f"颜色识别文件已保存: {info_file}")
        ExcelHandler(info_file).save_pdf_info_to_excel(data=result, is_space=True)
        logger.info(f"空格识别文件已保存: {info_file}")

        return result
    except PermissionError as e:
        logger.error(f"没有权限访问PDF文件: {e}")
        raise PDFError(f"没有权限访问PDF文件: {e}") from e
    except Exception as pdf_error:
        # 处理可能的PDF语法错误或其他pdfplumber异常
        if "PDFSyntaxError" in str(type(pdf_error)) or "syntax" in str(pdf_error).lower():
            logger.error(f"PDF文件格式错误: {pdf_error}")
            raise PDFParsingError(f"PDF文件格式错误: {pdf_error}") from pdf_error
        else:
            logger.error(f"提取PDF信息失败: {pdf_error}")
            raise PDFError(f"提取PDF信息失败: {pdf_error}") from pdf_error


def _process_page(page: Any, page_number: int) -> Dict[str, Any]:
    """
    处理单个PDF页面。
    
    Args:
        page: pdfplumber页面对象
        page_number: 页面编号
        
    Returns:
        页面信息字典
        
    Raises:
        PDFParsingError: 当页面处理失败时抛出
    """
    logger.debug(f"开始处理第 {page_number} 页")
    
    page_info: Dict[str, Any] = {
        "fonts": set(),
        "font_map": {},
        "colors": set(),
        "color_map": {},
        "size": set(),
        "size_map": {},
        "texts": []
    }
    
    try:
        # 获取页面字符
        chars = page.chars
        if not chars:
            logger.debug(f"第 {page_number} 页没有文字内容")
            return _finalize_page_info(page_info)
            
        logger.debug(f"第 {page_number} 页包含 {len(chars)} 个字符")
        
        # 使用分组算法处理字符
        groups = divide_groups(chars)
        
        for group in groups:
            if not group:
                continue
                
            page_text = ""
            for char in group:
                if not isinstance(char, dict):
                    logger.warning(f"跳过无效的字符对象: {char}")
                    continue
                    
                char_text = char.get("text", "")
                page_text += char_text
                
                # 处理字号信息
                _process_size_info(char, page_info)
                
                # 处理字体信息
                _process_font_info(char, page_info)
                
                # 处理颜色信息
                _process_color_info(char, page_info)
            
            # 将空格替换为可见标记
            if page_text:
                page_info["texts"].append(page_text.replace(" ", "[空格]"))
        
        # 为每个映射添加换行符
        _add_newlines_to_maps(page_info)
        
        logger.debug(f"第 {page_number} 页处理完成，生成 {len(page_info['texts'])} 个文本组")
        return _finalize_page_info(page_info)
        
    except Exception as e:
        logger.error(f"处理第 {page_number} 页失败: {e}")
        raise PDFParsingError(f"处理第 {page_number} 页失败: {e}") from e


def _process_size_info(char: Dict[str, Any], page_info: Dict[str, Any]) -> None:
    """处理字符的字号信息。"""
    size = char.get('size')
    if size is not None:
        sizename = str(size)
        page_info["size"].add(sizename)
        if sizename not in page_info["size_map"]:
            page_info["size_map"][sizename] = []
        page_info["size_map"][sizename].append(char.get('text', ''))


def _process_font_info(char: Dict[str, Any], page_info: Dict[str, Any]) -> None:
    """处理字符的字体信息。"""
    fontname_raw = char.get('fontname', '')
    if fontname_raw:
        fontname = get_fontname(fontname_raw)
        page_info["fonts"].add(fontname)
        if fontname not in page_info["font_map"]:
            page_info["font_map"][fontname] = []
        page_info["font_map"][fontname].append(char.get('text', ''))


def _process_color_info(char: Dict[str, Any], page_info: Dict[str, Any]) -> None:
    """处理字符的颜色信息。"""
    non_stroking_color = char.get('non_stroking_color')
    stroking_color = char.get('stroking_color')
    color = non_stroking_color if non_stroking_color else stroking_color
    
    if not color:
        color = "Unknown"

    page_info["colors"].add(color)
    color_str = str(color)
    if color_str not in page_info["color_map"]:
        page_info["color_map"][color_str] = []
    page_info["color_map"][color_str].append(char.get('text', ''))


def _add_newlines_to_maps(page_info: Dict[str, Any]) -> None:
    """为页面信息的映射添加换行符。"""
    for map_name in ["size_map", "font_map", "color_map"]:
        for key, value in page_info[map_name].items():
            if value and value[-1] != "\n":
                page_info[map_name][key].append("\n")


def _finalize_page_info(page_info: Dict[str, Any]) -> Dict[str, Any]:
    """完成页面信息的处理，将集合转换为列表。"""
    page_info["size"] = list(page_info["size"])
    page_info["fonts"] = list(page_info["fonts"])
    page_info["colors"] = list(page_info["colors"])
    return page_info


def _finalize_file_info(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """完成文件信息的处理，将集合转换为列表。"""
    file_info["size"] = list(file_info["size"])
    file_info["fonts"] = list(file_info["fonts"])
    file_info["colors"] = list(file_info["colors"])
    return file_info

def get_fontname(font: str) -> str:
    """
    根据字体名称映射获取中文字体名称。
    
    根据预定义的字体映射表，将技术字体名称转换为
    用户友好的中文字体名称。
    
    Args:
        font: 原始字体名称
        
    Returns:
        映射后的字体名称，如果没有找到映射则返回原名称
    """
    if not font:
        logger.warning("字体名称为空")
        return "Unknown"
        
    if not isinstance(font, str):
        logger.warning(f"字体名称不是字符串类型: {font}")
        return str(font)
    
    try:
        font_map = FONT_MAP
        for key, value in font_map.items():
            if key in font:
                logger.debug(f"字体映射: {font} -> {value}")
                return value
        
        logger.debug(f"未找到字体映射，使用原名称: {font}")
        return font
        
    except Exception as e:
        logger.error(f"字体名称映射失败: {e}")
        return font