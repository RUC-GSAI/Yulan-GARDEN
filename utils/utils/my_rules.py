import re

def too_many_chapters(text: str) -> bool:
    chapters = re.findall(r'第.*章', text)
    return len(chapters) >= 10

def my_words(text: str) -> bool:
    words = [r'售楼地址：', r'重要参数', r'基本参数']
    for word in words:
        if len(re.findall(word, text)) > 0:
            return True
    return False