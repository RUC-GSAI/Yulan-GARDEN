import re

def for_bdbk(text: str) -> str:
    '''
    delete the content from '目录' to '编辑'
    '''
    lines = text.split('\n')
    keywords = ['目录', '编辑']
    length = len(lines)
    i = 0
    for i in range(length):
        if lines[i] == keywords[0]:
            break
    if i >= length or lines[i] != keywords[0]:
        return text
    j = i + 1
    for j in range(i + 1, length):
        if lines[j] == keywords[1]:
            break
    if j >= length or lines[j] != keywords[1]:
        return text
    del lines[i: j - 1]
    text = '\n'.join(lines)
    return text

def RemoveLineBreaks(text: str) -> str:
    '''
    delete redundant line breaks
    '''
    paras = text.split('\n\n')
    paras = [para.replace('\n', ' ') for para in paras]
    text = '\n'.join(paras)
    return text
