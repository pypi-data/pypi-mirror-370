import torch
from torch.utils.data import Dataset
import pandas as pd
from transformers import (
    BertTokenizer, BertForSequenceClassification, pipeline
)
from transformers import ElectraTokenizer, ElectraForSequenceClassification
from transformers import AutoTokenizer, AutoModel
import nlpaug.augmenter.word as naw
import random
import numpy as np
import tqdm
from torch.utils.data import DataLoader

# ======================== 数据增强器（一次初始化，全局用） ========================
synonym_aug = naw.SynonymAug(aug_src='wordnet')
# synonym_aug = naw.SynonymAug(aug_src='baidu', lang='zh')
delete_aug = naw.RandomWordAug(action="delete")
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# ======================== Dataset ========================
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=64, aug_prob=0.3):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.aug_prob = aug_prob  # 每条数据增强的概率
    def __len__(self):
        return len(self.texts)
    def augment(self, text):
        """按随机策略增强文本"""
        p = random.random()
        if p < 0.5:  # 同义词替换
            return synonym_aug.augment(text)
        elif p < 1.0:  # 随机删除
            return delete_aug.augment(text)
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        # 随机增强
        if random.random() < self.aug_prob:
            text = self.augment(text)
            
        text2 = self.augment(text)
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )
        encoding_aug = self.tokenizer(
            text2,
            truncation=True,
            padding='max_length',
            max_length=self.max_len,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'input_ids_aug': encoding_aug['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long),
            'idx': idx
        }

# ======================== 其他代码不变 ========================
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def add_label_noise(labels, noise_rate=0.3, num_classes=None, seed=42):
    random.seed(seed)
    noisy_labels = labels.copy()
    n = len(labels)
    num_noisy = int(n * noise_rate)
    noisy_indices = random.sample(range(n), num_noisy)
    for idx in noisy_indices:
        old_label = noisy_labels[idx]
        possible_labels = list(range(num_classes))
        possible_labels.remove(old_label)
        noisy_labels[idx] = random.choice(possible_labels)
    return noisy_labels

# ======================== Main ========================
def main():
    set_seed(42)
    # 中文数据集
    train_df = pd.read_csv("train.csv")
    test_df = pd.read_csv("test.csv")
    train_texts = train_df['文本'].tolist()
    test_texts = test_df['文本'].tolist()
    labels = train_df['标签'].unique()
    label2id = {label: idx for idx, label in enumerate(labels)}
    train_labels = train_df['标签'].map(label2id)
    test_labels = test_df['标签'].map(label2id)

    # train_df = pd.read_csv("trec_train.csv")
    # test_df = pd.read_csv("trec_test.csv")
    # train_texts = train_df['text'].tolist()
    # test_texts = test_df['text'].tolist()
    # train_labels = train_df['fine_label']
    # test_labels = test_df['fine_label']
    num_labels = len(set(train_labels))
    #标签加噪
    train_labels = add_label_noise(train_labels, noise_rate=0.3, num_classes=num_labels)

    # tokenizer = ElectraTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
    # model = ElectraForSequenceClassification.from_pretrained("hfl/chinese-roberta-wwm-ext", num_labels=num_labels)  # num_labels 根据任务调整
    #英文模型
    # tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    # model1 = BertForSequenceClassification.from_pretrained("bert-large-uncased", num_labels=num_labels)
    # model1 = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=num_labels)

    #中文模型
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    model1 = BertForSequenceClassification.from_pretrained("bert-base-chinese", num_labels=num_labels)
    train_dataset = TextDataset(train_texts, train_labels, tokenizer, aug_prob=0.3)
    test_dataset = TextDataset(test_texts, test_labels, tokenizer, aug_prob=0.0)  # 测试集不增强
    # train(model1,train_dataset,test_dataset)
    test(model1,test_dataset,train_dataset)

def test(model,test_dataset,train_dataset):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.load_state_dict(torch.load("best_model.pth"))
    model.to(device)
    test_loader = DataLoader(test_dataset, batch_size=16)
    # 保存模型
    train_loader = DataLoader(train_dataset, batch_size=16,shuffle=False)
    train_preds  = []
    test_preds  = []
    for batch in tqdm.tqdm(train_loader, desc="Predict Train"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, return_dict=True)
        preds = outputs.logits.argmax(dim=1).cpu().tolist()
        train_preds.extend(preds)
    test_loader = DataLoader(test_dataset, batch_size=16,shuffle=False)
    for batch in tqdm.tqdm(test_loader, desc="Predict Test"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, return_dict=True)
        preds = outputs.logits.argmax(dim=1).cpu().tolist()
        test_preds.extend(preds)
    # 保存 CSV，保持原数据顺序
    train_df = pd.DataFrame({
        "label": [train_dataset[i]["labels"].item() for i in range(len(train_dataset))],
        "pred": train_preds
    })
    test_df = pd.DataFrame({
        "label": [test_dataset[i]["labels"].item() for i in range(len(test_dataset))],
        "pred": test_preds
    })
    train_df.to_csv("train_result.csv", index=False, encoding="utf-8-sig")
    test_df.to_csv("test_result.csv", index=False, encoding="utf-8-sig")
    print("CSVs saved successfully.")    

def train(model,train_dataset,test_dataset):
    #使用gsmc进行训练，推荐使用
    from trainer.gsmc_trainer import Trainer
    trainer = Trainer(
        model=model,
        max_acc=69.0,
        )
    trainer.train(train_dataset, 
                  test_dataset, 
                  epochs=40, 
                  batch_size=16,
                  loss_type='catoni',
                  alpha = 0.9,
                  T = 1.0
                  )
if __name__ == "__main__":
    main()
