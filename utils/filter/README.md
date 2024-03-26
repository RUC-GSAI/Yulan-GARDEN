# Filter

Filter (`./utils/workers/filter.py`) is a module to filter the useless or sensitive texts, including 11 different rules:

1. `fil_short_texts`: short texts (hyperparamter: minimum length of the texts, default: 170).

2. `fil_non_ch`: non-Chinese texts (hyperparamter: biggest ratio of non-Chinese characters , default: 0.4).

3. `fil_copyright`: 'Copyright' texts.

4. `fil_short_lines`: texts with too many short lines (hyperparamter: biggest ratio of short lines, short lines means the length of the line is less than 3, default: 0.25).

5. `fil_dirty_words`: texts with dirty words.

6. `fil_langs`: texts not in the accepted language list (hyperparamter: an accepted language list).

7. `fil_lang_score`: texts with language score lower than reject threshold (hyperparamter: reject threshold).

8. `fil_ppl`: texts with perplexity larger than avg. + n * std. (hyperparamter: n)

9. `fil_alphanum`: non-English texts (hyperparamter: lower bound and upper bound ratio of non-English characters).

10. `fil_my_rules`: other custom rules. To make Yulan-GARDEN more flexible, you can set your custom rules in `./utils/utils/my_rules.py` as functions and add the names of the functions into the setting files.

All the hyperparamters are changable in the light of `Debugger`.