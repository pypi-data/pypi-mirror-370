import difflib
import string
import re
from pypinyin import pinyin, Style

class TextHandler:
    
    @staticmethod
    def get_pinyin(input_string: str):
        # 判断 input_string 是否为汉字
        if TextHandler.is_chinese(input_string):
            # 将汉字转换为拼音
            pinyin_list = pinyin(input_string, style=Style.TONE)
            pinyin_string = ""
            for pinyin_word in pinyin_list:
                pinyin_string += " ".join(pinyin_word) + " "
            return pinyin_string.strip()
        else:
            return input_string
    
    @staticmethod
    def is_pinyin(input_string):
        pinyin_chars = set("ɑɡɪʊ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZāēīōūǖĀĒĪŌŪǕáéíóúǘÁÉÍÓÚǗàèìòùǜÀÈÌÒÙǛǎěǐǒǔǚǍĚǏǑǓǙüÜ\xa0\n")
        return all(char in pinyin_chars for char in input_string)
    
    @staticmethod
    def similarity_ratio(a, b, remove_punctuation=True, use_contains=False):
        if remove_punctuation:
            a = TextHandler.remove_punctuation(a)
            b = TextHandler.remove_punctuation(b)
            
        ratio = difflib.SequenceMatcher(None, a, b).ratio()
        if use_contains and ratio < 0.1 and TextHandler.contains_four_consecutive(a, b):
            return 0.1
        # 检查两个字符串中是否包含连续的四个字符
        else:
            return ratio

    @staticmethod
    def contains_four_consecutive(a, b):
        """
        检查两个字符串是否包含连续四个相连字符。
        """
        for i in range(len(a) - 3):  # -3 是因为要至少有4个连续字符
            sub_a = a[i:i+4]
            if sub_a in b:
                return True
        return False
    
    @staticmethod
    def remove_punctuation(text):
        # 定义中文标点符号
        chinese_punctuation = " 。？！，、；：“”‘’（）《》【】——…"
        # 合并英文和中文标点符号
        all_punctuation = string.punctuation + chinese_punctuation
        # 创建转换表
        translator = str.maketrans('', '', all_punctuation)
        return text.translate(translator)
    
    @staticmethod
    def diff_list(a, b):
        # 使用 difflib 获取两个字符串之间的差异
        s = difflib.SequenceMatcher(None, a, b)
        diffs = []
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            diffs.append((tag, i1, i2, j1, j2))
        return diffs

    @staticmethod
    def unchanged_indices(a, b):
        diffs = TextHandler.diff_list(a, b)
        unchanged_a = []
        unchanged_b = []

        # 遍历差异，找到相等的部分
        for diff in diffs:
            tag, i1, i2, j1, j2 = diff
            if tag == 'equal':
                unchanged_a.extend(range(i1, i2))
                unchanged_b.extend(range(j1, j2))
        
        return unchanged_a, unchanged_b
    
    @staticmethod
    def filter_indices(a, unchanged_a, b, unchanged_b):
        a_is_pinyin = TextHandler.is_pinyin(a)
        b_is_pinyin = TextHandler.is_pinyin(b)
        min_length = 3
        is_span = True
        if (a_is_pinyin):
            min_length = min([len(t) for t in a.replace("\xa0", " ").replace("\n", " ").split(" ")])
        elif (b_is_pinyin):
            min_length = min([len(t) for t in b.replace("\xa0", " ").replace("\n", " ").split(" ")])
        
        filtered_indices_a = TextHandler.filter_consecutive(unchanged_a, min_length=min_length, is_span=is_span)
        filtered_indices_b = TextHandler.filter_consecutive(unchanged_b, min_length=min_length, is_span=is_span)
        
        filtered_pairs = []
        for index in range(len(unchanged_a)):
            if index in filtered_indices_a and index in filtered_indices_b:
                filtered_pairs.append((unchanged_a[index], unchanged_b[index]))
        
        return filtered_pairs
    
    @staticmethod
    def get_same_rate(str1, str2, limit=0):
        try:
            m = len(str1)
            n = len(str2)

            # 创建一个二维表格来保存最长公共子串的长度
            # dp[i][j] 表示以 str1[i-1] 和 str2[j-1] 结尾的公共子串的长度
            dp = [[0] * (n + 1) for _ in range(m + 1)]

            # 用于记录最长公共子串的长度和结束位置
            max_len = 0
            end_index = 0

            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if str1[i - 1] == str2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                        if dp[i][j] > max_len:
                            max_len = dp[i][j]
                            end_index = i

            # 从 end_index 和 max_len 得到最长公共子串
            longest_len = len(str1[end_index - max_len:end_index])
            if limit > longest_len:
                return 0.0
            same1_rate = longest_len / len(str1)
            same2_rate = longest_len / len(str2)
            if same1_rate > same2_rate:
                return same1_rate * 0.9 + same2_rate * 0.1
            else:
                return same2_rate * 0.9 + same1_rate * 0.1
        except:
            return 0.0
    
    @staticmethod
    def filter_consecutive(indices, min_length=2, is_span=False):
        # 存放结果的列表
        result_indices = []
        current_sequence = []

        for i, index in enumerate(indices):
            # 如果当前序列为空，开始一个新的序列
            if not current_sequence:
                current_sequence.append(i)
            else:
                # 检查当前索引是否连续
                if index == indices[current_sequence[-1]] + 1 or (is_span and index == indices[current_sequence[-1]] + 2):
                    current_sequence.append(i)
                else:
                    # 检查是否符合最小长度要求，符合则加入结果
                    if len(current_sequence) >= min_length:
                        result_indices.extend(current_sequence)
                    # 开始一个新的序列
                    current_sequence = [i]

        # 最后一组序列
        if len(current_sequence) >= min_length:
            result_indices.extend(current_sequence)

        return result_indices
    
    @staticmethod
    def is_chinese(word):
        # 使用正则表达式判断字符串是否包含汉字
        return bool(re.search(r'[\u4e00-\u9fff]', word))

    @staticmethod
    def get_pinyin_first_letter(word):
        # 获取汉字的拼音首字母
        if TextHandler.is_chinese(word):
            pinyin_str = pinyin(word, style=Style.FIRST_LETTER)
            return pinyin_str[0][0] if pinyin_str else word
        else:
            # 如果是英文则直接返回首字母
            return word[0]
    
    @staticmethod
    def scale_and_round(cmyk_string):
        try:
            cmyk_color = [float(val) for val in cmyk_string.strip('()').split(',')]
            scaled_values = [round(value * 100) for value in cmyk_color]
            return ", ".join([str(item) for item in scaled_values])
        except:
            return "未知"
    
    @staticmethod
    def cmyk_str_to_rgb(cmyk_string):
        try:
            cmyk_values = [float(val) for val in cmyk_string.strip('()').split(',')]
            return TextHandler.cmyk_to_rgb(*cmyk_values)
        except:
            return "ffffff"
    
    @staticmethod
    def cmyk_to_rgb(c, m, y, k):
        """
        Convert CMYK color to RGB color.
        :param c: Cyan component (0.0 - 1.0)
        :param m: Magenta component (0.0 - 1.0)
        :param y: Yellow component (0.0 - 1.0)
        :param k: Black component (0.0 - 1.0)
        :return: Tuple representing RGB color in the range (0, 255)
        """
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        hex_color = '{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))
        return hex_color