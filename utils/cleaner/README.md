# Cleaner

Cleaner (`./utils/workers/cleaner.py`) is a submodule of the Processing Module to refine the raw datasets, including operators as follows:

1. `extractor`: extract content from format files, including HTML, mobi, epub and pdf.

2. `rm_crawlerchars`: remove the unused patterns in the text (e.g. '&nbsp').

3. `sub_newline`: remove consecutive newlines in the text.

4. `rm_re_rules`: remove regular expressions.

5. `sub_re_rules`: substitute regular expressions.

6. `rm_str_rules`: remove raw strings.

7. `rm_re_lines`: remove **a line** if any text fragments in this line matching any of **regular expressions** in `re_list`.

8. `rm_str_lines`: remove **a line** if any text fragments in this line matching any of **string** in `str_list`".

9. `rm_str_seg`: remove **a segment** after matching any of **string** in `str_list` if any text fragments in this text are matched.

10. `rm_re_seg`: remove **a segment** after matching any of **string** in `re_list` if any text fragments in this text are matched.

11. `rm_pii`: remove **personally identifiable information** including emails, idcards, ips, phones and urls

12. `tra2sim`: convert Traditional Chinese to Simplified Chinese.

13. `my_funcs`: other custom rules. You can set your custom rules in `./utils/utils/my_funcs.py` as functions and add the names of the functions into the setting files. 