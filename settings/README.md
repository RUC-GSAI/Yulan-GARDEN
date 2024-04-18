## Predefined Templates
We provide some predefined configuration files as examples to reproduce existing widely used open-source datasets including Openwebtext2, Wikipedia-en, HackerNews, and CommonCrawl. 

### Openwebtext2
Openwebtext2 is an enhanced version of the Webtext dataset, which is the training corpus of GPT-2. 
It includes all Reddit submissions from 2005 to April 2020.
We filter the texts with short length, large perplexity and dirty words. 
We remove some meaningless signals, social media shares, and privacy information.

### Wikipedia-en
Wikipedia serves as a benchmark for obtaining high-quality text for language modeling. 
We utilize the English slice of Wikipedia up until Nov. 1st, 2023 as our Wikipedia-en dataset. 
We filter texts with short length and large perplexity. 
We remove the references and next-page links.

### HackerNews
HackerNews is an online platform dedicated to curating and sharing news articles, with a particular emphasis on computer science and entrepreneurship. 
We filter texts with large perplexity and remove some HTML tags and meaningless signals.

### CommonCrawl
CommonCrawl curates an accessible repository of web crawl data. 
We filter texts with short length, large perplexity, few sentences, few paragraphs, too many short lines, low language scores, and dirty words. 
We also filter the lines with few characters. 
We retain texts in 23 main languages, such as English and Chinese.

