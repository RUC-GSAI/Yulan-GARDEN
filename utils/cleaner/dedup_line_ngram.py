import string
import re
from nltk.util import ngrams
from utils.cleaner.cleaner_base import CleanerBase

# class CleanerDedupLineByNgram():
class CleanerDedupLineByNgram(CleanerBase):
    def __init__(self):
        self.line_delimiter = list("\n")
        chinese_punctuation = "，。！？：；“”‘’（）《》【】、|—"
        self.gram_delimiter = list(string.punctuation) + list(chinese_punctuation) + [' ']
        super().__init__()
    
    def clean_single_text(self, text: str, n: int = 5, thre_sim: float = 0.95) -> str:
        lines = [each for each in re.split('|'.join(map(re.escape, self.line_delimiter)), text) if each != '']
        cnt, lineinfo = 0, list()
        for idx, line in enumerate(lines):
            grams = [each for each in re.split('|'.join(map(re.escape, self.gram_delimiter)), line) if each != '']
            computed_ngrams = list(ngrams(grams, min(len(grams), n)))
            lineinfo.append({
                "lineno": idx,
                "text": line,
                "n": min(len(grams), n),
                "ngrams": computed_ngrams,
                "keep": 0
            })
            cnt += 1
        
        last = {}
        for idx, each in enumerate(lineinfo):
            # print(each)
            if last == {}:
                each["keep"] = 1
                last = each
            else:
                ngrams_last = set(last["ngrams"])
                ngrams_cur = set(each["ngrams"])
                ngrams_intersection = len(ngrams_last.intersection(ngrams_cur))
                ngrams_union = len(ngrams_last.union(ngrams_cur))
                jaccard_sim = ngrams_intersection / ngrams_union if ngrams_union != 0 else 0
                # print(jaccard_sim, ngrams_last, ngrams_cur)
                if jaccard_sim < thre_sim:
                    each["keep"] = 1
                    last = each

        line_delimiter = self.line_delimiter[0]
        text = line_delimiter.join([each["text"] for each in lineinfo if each["keep"] == 1])        

        return text
    
if __name__ == '__main__':
    text = "Hello World\nHello Hello World\nHello World\nHello World\nHello World\n"
    # text = "我 是 一 个 木 头 人\n我 是 一 个 木 头\n我 是 一 个 木 头\n我 是 一 个 人\n"
    cleaner = CleanerDedupLineByNgram()
    text = cleaner.clean_single_text(text, 5, 0.95)
    print(text)