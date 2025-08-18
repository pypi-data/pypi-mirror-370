import nltk

# 下载英文词性标注器
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('averaged_perceptron_tagger')
# 同时确保分词和 WordNet 数据可用
nltk.download('punkt')
nltk.download('wordnet')
print("export HF_ENDPOINT='https://hf-mirror.com'")
