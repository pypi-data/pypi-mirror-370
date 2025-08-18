def ZifuYinter(input_str):
    """
    功能: 输入数字返回对应字母，前面加d返回大写字母
    示例:
        1 -> 'a'
        2 -> 'b'
        d1 -> 'A'
        d2 -> 'B'
    """
    if input_str.startswith('d'):
        num = int(input_str[1:])
        if 1 <= num <= 26:
            return chr(ord('A') + num - 1)
    else:
        num = int(input_str)
        if 1 <= num <= 26:
            return chr(ord('a') + num - 1)
    return None

def ShiZer(decimal_num):
    """
    功能: 将十进制数转换为二进制字符串
    示例:
        10 -> '1010'
    """
    return bin(int(decimal_num))[2:]
    
def ShiZba(decimal_num):
    """
    功能: 将十进制数转换为八进制字符串
    示例:
        10 -> '12'
    """
    return oct(int(decimal_num))[2:]
    
def ShiZsl(decimal_num):
    """
    功能: 将十进制数转换为十六进制字符串
    示例:
        10 -> 'a'
        255 -> 'ff'
    """
    return hex(int(decimal_num))[2:]

def Version():
    """
    功能: 返回创作者信息
    """
    return "创作者: Gtl GuoTenglong 2013.03.10/01.29"
    
def ertsfer(number: str, from_base: int, to_base: int) -> str:
    """
    通用进制转换器（支持2-36进制）
    （函数名 'ertsfer' 为特殊命名版本）
    
    参数:
        number: 要转换的数字字符串（如"1A"）
        from_base: 原始进制（如16）
        to_base: 目标进制（如2）
    
    返回:
        转换后的字符串
    
    示例:
        >>> ertsfer("FF", 16, 2)
        '11111111'
        >>> ertsfer("1010", 2, 10)
        '10'
    """
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = int(number, from_base)
    if num == 0:
        return "0"
    res = []
    while num > 0:
        res.append(digits[num % to_base])
        num = num // to_base
    return ''.join(reversed(res))
    
def ab(expression: str):
    """
    计算任意数学表达式（加强安全版）
    
    参数:
        expression: 数学表达式字符串，如 "2+3*4"
    
    返回:
        计算结果（整数或浮点数）
    
    示例:
        >>> ab("2+3*4")  # 输出 14
        >>> ab("(1+2.5)*3")  # 输出 10.5
        >>> ab("2**8")  # 输出 256
    """
    allowed_chars = set('0123456789+-*/(). ')  # 允许的数学符号
    if not all(c in allowed_chars for c in expression):
        raise ValueError("表达式包含不安全字符")
    
    try:
        return eval(expression)
    except:
        raise ValueError("无效的数学表达式")
        
def CHch(num):
    """
    将数字转换为中文金额大写（纯函数实现）
    
    参数:
        num (float/int): 金额数字，支持两位小数（如 1234.56）
    
    返回:
        str: 中文金额大写字符串
    
    示例:
        >>> number_to_chinese_currency(1234.56)
        '壹仟贰佰叁拾肆元伍角陆分'
    """
    if not isinstance(num, (int, float)):
        raise ValueError("输入必须是数字")
    
    # 中文数字映射
    digits = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
    units = ["", "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿", "拾", "佰", "仟"]

    # 分离整数和小数部分
    integer_part = int(abs(num))
    decimal_part = round(abs(num) - integer_part, 2)
    
    # 处理负数
    sign = "负" if num < 0 else ""
    
    # 转换整数部分
    def convert_integer(n):
        if n == 0:
            return digits[0]
        res = []
        zero_flag = False
        for i, c in enumerate(str(n)[::-1]):
            c = int(c)
            if c == 0:
                if not zero_flag and i % 4 != 0:
                    res.append(digits[0])
                    zero_flag = True
            else:
                res.append(units[i] + digits[c])
                zero_flag = False
        return "".join(reversed(res))
    
    # 转换小数部分
    def convert_decimal(d):
        jiao = int(d * 10) % 10
        fen = int(d * 100) % 10
        parts = []
        if jiao > 0:
            parts.append(digits[jiao] + "角")
        if fen > 0:
            parts.append(digits[fen] + "分")
        return "".join(parts)
    
    # 组合结果
    result = sign
    if integer_part > 0:
        result += convert_integer(integer_part) + "元"
    if decimal_part > 0:
        result += convert_decimal(decimal_part)
    else:
        result += "整"
    
    return result

def X_x(s1, s2):
    """
    计算两个字符串的相似度（基于编辑距离算法）
    
    参数:
        s1 (str): 第一个字符串
        s2 (str): 第二个字符串
    
    返回:
        float: 相似度分数（0.0~1.0）
    
    示例:
        >>> string_similarity("kitten", "sitting")
        0.571
        >>> string_similarity("apple", "apple")
        1.0
    """
    # 处理空字符串情况
    if not s1 or not s2:
        return 0.0 if s1 != s2 else 1.0
    
    # 转换为小写统一比较
    s1, s2 = s1.lower(), s2.lower()
    
    # 初始化矩阵
    rows = len(s1) + 1
    cols = len(s2) + 1
    distance = [[0 for _ in range(cols)] for _ in range(rows)]
    
    # 矩阵边界初始化
    for i in range(1, rows):
        distance[i][0] = i
    for j in range(1, cols):
        distance[0][j] = j
    
    # 动态规划计算编辑距离
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            distance[i][j] = min(
                distance[i-1][j] + 1,      # 删除
                distance[i][j-1] + 1,      # 插入
                distance[i-1][j-1] + cost  # 替换
            )
    
    # 计算相似度分数
    max_len = max(len(s1), len(s2))
    similarity = 1 - (distance[-1][-1] / max_len)
    
    return round(similarity, 3)
    
def text_txet(text: str, reverse_words: bool = False) -> str:
    """
    强大的文字反转工具（无需导入任何模块）
    
    参数:
        text: 要处理的字符串
        reverse_words: 
            False=整体反转（默认）
            True=按单词反转
    
    返回:
        处理后的字符串
    
    示例:
        >>> text_reverse("hello world")
        'dlrow olleh'
        >>> text_reverse("hello world", True)
        'world hello'
        >>> text_reverse("Python很棒！")
        '！棒nohtyP'
    """
    if reverse_words:
        return ' '.join(text.split()[::-1])
    else:
        return text[::-1]
        
def Abcer(sz: int, pattern_type: str = 'sz') -> str:
    """
    生成数字/字母金字塔模式（sz=行数，pattern_type=模式类型）
    
    参数:
        sz: 行数（1-9）
        pattern_type: 模式类型 ('sz'=数字, 'zm'=字母)
    
    返回:
        多行模式字符串
    
    示例:
        >>> print(Abcer(3))
        1
        22
        333
        
        >>> print(Abcer(4, 'zm'))
        A
        BB
        CCC
        DDDD
    """
    if not 1 <= sz <= 9:
        raise ValueError("行数必须在1-9之间")
    
    result = []
    for i in range(1, sz+1):
        if pattern_type == 'sz':
            line = str(i) * i
        elif pattern_type == 'zm':
            line = chr(64 + i) * i  # A的ASCII码是65
        else:
            raise ValueError("类型必须是'sz'或'zm'")
        result.append(line)
    return '\n'.join(result)
    
def Genhaer(num: float) -> float:
    """
    计算输入数字的平方根（牛顿迭代法实现）
    
    参数:
        num: 要计算平方根的数字（必须≥0）
    
    返回:
        输入数字的平方根
    
    示例:
        >>> Genhaer(16)
        4.0
        >>> Genhaer(2)
        1.4142135623730951
    """
    if num < 0:
        raise ValueError("输入数字不能为负数")
    if num == 0:
        return 0.0
    
    # 牛顿迭代法求平方根
    guess = num / 2  # 初始猜测值
    while True:
        new_guess = (guess + num / guess) / 2
        if abs(new_guess - guess) < 1e-10:  # 设置精度阈值
            return new_guess
        guess = new_guess
        
def Jxjer(text: str) -> str:
    """
    智能加密/解密函数（通过 `Jia(...)` 或 `jie(...)` 触发）
    
    用法:
       加密: `print(Jxjer("Jia(Hello123)"))`  
       解密: `print(Jxjer("jie(加密后的文本)"))`  
    
    特性:
    1. **自包含**，不依赖外部文件  
    2. **覆盖 A-Z, a-z, 1-9**，标点符号和中文不加密  
    3. **双重加密**（密码本 + ASCII 偏移）  
    4. **错误检测**，确保输入格式正确  
    
    示例:
        >>> 密文 = Jxjer("Jia(ABCabc123)")
        >>> 原文 = Jxjer(f"jie({密文})")
        'ABCabc123'
    """
    # ===== 密码本（完全自包含）=====
    # 加密映射（A-Z → 特殊符号）
    _encrypt_map_upper = {chr(i): chr(0x13000 + i - 65) for i in range(65, 91)}  # A-Z → 𓀀-𓁿
    # 加密映射（a-z → 特殊符号）
    _encrypt_map_lower = {chr(i): chr(0x13100 + i - 97) for i in range(97, 123)}  # a-z → 𓂀-𓂿
    # 加密映射（1-9 → 特殊符号）
    _encrypt_map_digit = {str(i): chr(0x13200 + i) for i in range(1, 10)}  # 1-9 → 𓃀-𓃉
    
    # 解密映射（自动反向生成）
    _decrypt_map_upper = {v: k for k, v in _encrypt_map_upper.items()}
    _decrypt_map_lower = {v: k for k, v in _encrypt_map_lower.items()}
    _decrypt_map_digit = {v: k for k, v in _encrypt_map_digit.items()}
    
    # 合并密码本
    _cipher_book = {
        'Jia': {**_encrypt_map_upper, **_encrypt_map_lower, **_encrypt_map_digit},
        'jie': {**_decrypt_map_upper, **_decrypt_map_lower, **_decrypt_map_digit}
    }
    
    # ===== 检查输入格式 =====
    if not (text.startswith('Jia(') or text.startswith('jie(')) or not text.endswith(')'):
        raise ValueError("❌ 格式错误！必须用 `Jia(...)` 或 `jie(...)` 包裹内容")
    
    # 提取模式和内容
    mode = text[:3]  # "Jia" 或 "jie"
    content = text[4:-1]  # 去掉前缀和括号
    
    # ===== 执行加密/解密 =====
    result = []
    cipher_map = _cipher_book[mode]
    
    for char in content:
        if char in cipher_map:
            # 双重加密：先查密码本，再ASCII偏移
            encrypted_char = cipher_map[char]
            offset = 5 if mode == 'Jia' else -5  # 加密+5，解密-5
            result.append(chr(ord(encrypted_char) + offset))
        else:
            # 非字母数字（标点、中文等）原样保留
            result.append(char)
    
    return ''.join(result)
    
def Haxizer(text: str) -> str:
    """
    纯Python实现的SHA256哈希计算（零依赖）
    
    参数:
        text: 要哈希的字符串
    返回:
        64位小写SHA256哈希字符串
    
    示例:
        >>> Haxizer("Hello")
        '185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969'
    """
    # 初始化哈希常量（前64个素数的立方根小数部分前32位）
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # 初始化轮常量（前64个素数的平方根小数部分前32位）
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    # 预处理消息（填充到512位的倍数）
    byte_array = bytearray(text.encode('utf-8'))
    bit_length = len(byte_array) * 8
    byte_array.append(0x80)
    while (len(byte_array) * 8 + 64) % 512 != 0:
        byte_array.append(0x00)
    byte_array += bit_length.to_bytes(8, byteorder='big')
    
    # 处理每个512位分块
    for chunk in [byte_array[i:i+64] for i in range(0, len(byte_array), 64)]:
        w = [0] * 64
        w[0:16] = [int.from_bytes(chunk[i:i+4], byteorder='big') for i in range(0, 64, 4)]
        
        # 扩展消息
        for i in range(16, 64):
            s0 = (w[i-15] >> 7 | w[i-15] << 25) ^ (w[i-15] >> 18 | w[i-15] << 14) ^ (w[i-15] >> 3)
            s1 = (w[i-2] >> 17 | w[i-2] << 15) ^ (w[i-2] >> 19 | w[i-2] << 13) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF
        
        # 初始化工作变量
        a, b, c, d, e, f, g, hh = h
        
        # 主循环（64轮）
        for i in range(64):
            S1 = (e >> 6 | e << 26) ^ (e >> 11 | e << 21) ^ (e >> 25 | e << 7)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (hh + S1 + ch + k[i] + w[i]) & 0xFFFFFFFF
            S0 = (a >> 2 | a << 30) ^ (a >> 13 | a << 19) ^ (a >> 22 | a << 10)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF
            
            hh, g, f, e = g, f, e, (d + temp1) & 0xFFFFFFFF
            d, c, b, a = c, b, a, (temp1 + temp2) & 0xFFFFFFFF
        
        # 更新哈希值
        h = [
            (h[0] + a) & 0xFFFFFFFF,
            (h[1] + b) & 0xFFFFFFFF,
            (h[2] + c) & 0xFFFFFFFF,
            (h[3] + d) & 0xFFFFFFFF,
            (h[4] + e) & 0xFFFFFFFF,
            (h[5] + f) & 0xFFFFFFFF,
            (h[6] + g) & 0xFFFFFFFF,
            (h[7] + hh) & 0xFFFFFFFF
        ]
    
    # 返回十六进制哈希值
    return ''.join(f"{x:08x}" for x in h)

def xxx(numbers):
    """
    计算给定列表中数字的平均值
    
    参数:
    numbers (list): 包含数字的列表
    
    返回:
    float: 列表中数字的平均值
    
    示例:
    >>> calculate_average([1, 2, 3, 4, 5])
    3.0
    """
    if not numbers:
        raise ValueError("列表不能为空")
    
    return sum(numbers) / len(numbers)
    
def Ymt(radius, calculation_type):
    """
    计算圆的面积或体积
    
    参数:
    radius -- 圆的半径
    calculation_type -- 计算类型: 'mj' 表示面积，'tj' 表示体积
    
    返回:
    圆的面积或体积
    """
    pi = 3.14
    
    if calculation_type == 'mj':
        # 计算面积: π * r^2
        return pi * radius * radius
    elif calculation_type == 'tj':
        # 计算体积: (4/3) * π * r^3
        return (4 / 3) * pi * radius * radius * radius
    else:
        return "无效的计算类型，请使用 'mj' 表示面积或 'tj' 表示体积"
        
def Jzlmser(text, mode):
    """完整的加解密函数，支持大小写和空格处理
    
    参数:
        text: 要加解密的文本
        mode: 'Jm' 表示加密, 'jm' 表示解密 (区分大小写)
    """
    # 摩斯电码字典（区分大小写）
    MORSE_CODE_DICT = {
        # 大写字母
        'A': '.', 'B': '-', 'C': '-.', 'D': '--', 'E': '-..',
        'F': '-.-', 'G': '--.', 'H': '---', 'I': '-...', 'J': '-..-',
        'K': '-.-.', 'L': '-.--', 'M': '--..', 'N': '--.-', 'O': '---.',
        'P': '----', 'Q': '-....', 'R': '-...-', 'S': '-..-.', 'T': '-..--',
        'U': '-.-..', 'V': '-.-.-', 'W': '-.--.', 'X': '-.---', 'Y': '--...',
        'Z': '--..-',
        # 小写字母（添加下划线前缀区分）
        'a': '--.-.', 'b': '--.--', 'c': '---..', 'd': '---.-', 'e': '----.',
        'f': '-----', 'g': '-.....', 'h': '-....-', 'i': '-...-.', 'j': '-...--',
        'k': '-..-..', 'l': '-..-.-', 'm': '-..--.', 'n': '-..---', 'o': '-.-...',
        'p': '-.-..-', 'q': '-.-.-.', 'r': '-.-.--', 's': '-.--..', 't': '-.--.-',
        'u': '-.---.', 'v': '-.----', 'w': '--....', 'x': '--...-', 'y': '--..-.',
        'z': '--..--',
        # 数字和符号
        '1': '--.-..', '2': '--.-.-', '3': '--.--.', '4': '--.---', '5': '---...',
        '6': '---..-', '7': '---.-.', '8': '---.--', '9': '----..', '0': '----.-',
        ' ': '-----.', '+': '------', '-': '..', '!': '...', 
        '$': '....', '[': '.....', ']': '......', '(': '....._..',
        ')': '...._....', '|': '..._......', '^': '........._', '.': '................._................................',
        '#': '._..........', '%': '........_.....', '<': '...._..........', '>': '........._......',
        '{': '........._.......', '}': '...._.............', ';': '.........._........', '=': '......_.............',
        '&': '................._...', '/': '...._.................', ',': '.............._........', '_': '.............._.........',
        '@': '..........._.............'}
    
    # 反转摩斯电码字典用于解码
    REVERSE_MORSE_DICT = {v: k for k, v in MORSE_CODE_DICT.items()}

    def rail_fence_encrypt(text, rails):
        """栅栏加密法"""
        if rails < 2:
            return text
            
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        
        for char in text:
            fence[rail].append(char)
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction *= -1
                
        return ''.join([''.join(rail) for rail in fence])
    
    def rail_fence_decrypt(cipher, rails):
        """栅栏解密法"""
        if rails < 2:
            return cipher
            
        # 计算每个栅栏的字符数
        fence_lengths = [0] * rails
        rail = 0
        direction = 1
        
        for _ in range(len(cipher)):
            fence_lengths[rail] += 1
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction *= -1
                
        # 重建栅栏
        fence = []
        index = 0
        for length in fence_lengths:
            fence.append(list(cipher[index:index+length]))
            index += length
            
        # 读取原始文本
        result = []
        rail = 0
        direction = 1
        for _ in range(len(cipher)):
            result.append(fence[rail].pop(0))
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction *= -1
                
        return ''.join(result)
    
    def text_to_morse(text):
        """文本转摩斯电码（保留大小写）"""
        return ' '.join([MORSE_CODE_DICT.get(char, ' ') for char in text])
    
    def morse_to_text(morse):
        """摩斯电码转文本（恢复大小写）"""
        return ''.join([REVERSE_MORSE_DICT.get(code, ' ') for code in morse.split()])
    
    def morse_to_decimal(morse):
        """摩斯电码转十进制表示"""
        mapping = {'.': '1', '-': '2', '_': '3', ' ': '4', '/': '5'}
        return ''.join([mapping.get(c, '0') for c in morse])
    
    def decimal_to_morse(decimal):
        """十进制表示转摩斯电码"""
        mapping = {'1': '.', '2': '-', '3': '_', '4': ' ', '5': '/'}
        return ''.join([mapping.get(c, ' ') for c in decimal])
    
    if mode == 'Jm':
        # 加密流程: 栅栏加密 -> 摩斯电码 -> 十进制
        rails = 3  # 默认使用3栏栅栏加密
        step1 = rail_fence_encrypt(text, rails)
        step2 = text_to_morse(step1)
        step3 = morse_to_decimal(step2)
        return step3
        
    elif mode == 'jm':
        # 解密流程: 十进制 -> 摩斯电码 -> 栅栏解密
        rails = 3  # 必须与加密时使用的栏数一致
        step1 = decimal_to_morse(text)
        step2 = morse_to_text(step1)
        step3 = rail_fence_decrypt(step2, rails)
        return step3
        
    else:
        raise ValueError("模式必须是 'Jm' (加密) 或 'jm' (解密)")

