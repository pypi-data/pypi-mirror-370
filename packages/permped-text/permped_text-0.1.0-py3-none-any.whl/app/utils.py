import re
import requests


def minimize_text(content):
    content = re.sub(r'[^\w\s]', '', content)
    content = content.replace("\n", " ")
    return " ".join(content.split())


def clean_and_filter_text(text):
    stopwords = set(
        requests.get(
            "https://gist.githubusercontent.com/rg089/35e00abf8941d72d419224cfd5b5925d/raw/12d899b70156fd0041fa9778d657330b024b959c/stopwords.txt"
        ).text.splitlines()
    )
    filtered_words = [w for w in text.split() if w.lower() not in stopwords]
    return " ".join(filtered_words)
