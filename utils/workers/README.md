# Workers

The core code of Workers can be found in this directory, including Reformatter, Cleaner, Filter, Debugger and Deduplicator.

## Reformatter

We reformat the raw datasets into jsonlines, where each row is a JSON dictionary including a ``text'' field and other meta information, aligning with the format of Huggingface datasets.

## Filter

Filter fixes the datasets by discarding contentless texts (e.g.,~crawled thin content webpage), non-target language texts, ambiguous texts, and toxic texts. [The details of each operator](../filter/README.md) are in Filter Module.

## Cleaner

Cleaner eliminates useless content with weak semantics or with personal privacy, such as HTML tags in crawled web data or reporter names in news data. [The details of each operator](../cleaner/README.md) are in Cleaner Module.

## Deduplicator

[Deduplicator](./deduplicator.py) utilizes the MinHash Locality Sensitive Hashing (MinHashLSH) algorithm to remove duplicate texts from datasets. Our implementation follows the depository ``text-dedup`` from [text-dedup](https://github.com/ChenghaoMou/text-dedup).

## Evaluator

Evaluator employs a visualization approach to present the data distribution (perplexity, language, etc.) in a user-friendly manner. [The details](../evaluator/README.md) are in Evaluator Module.

## Retriever

Retriever integrates a simple search engine implemented by ElasticSearch to retrieve entity-level or topic-level texts, which can help users determine whether the dataset contains texts related to the field. [The details](../retriever/README.md) are in Retriever Module.

## Debugger

[Debugger](./debugger.py) is a module to give a report (default path: `./debug_report.json`) for `Filter` hyperparameters and `Cleaner` details sample from the raw data. You can set `if_debug` in `settings.json` as `true` to make it work.

In `Filter` report, Debugger lists some values of hyperparameters and corresponding filter ratio for users to choose the appropriate values of hyperparameters according to a certain filter ratio. Make sure value of `use` of the filter rules (`debug_paras` in `settings.json`) are `true`.

In `Cleaner` report, for each rule in Cleaner, Debugger includes the match ratio, which is number of successful matches divided by the total texts traversed by Debugger, the average execution time and some match cases. All of the information helps users judge whether the rule works in Cleaner. Make sure value of `use` of the cleaner rules (`clean_paras` in `settings.json`) are `true`.

Besides, `debug_find_cases` helps developers find the texts which contain certain key words using the form of regular expressions. The report of `debug_find_cases` is in `Cleaner` report.
