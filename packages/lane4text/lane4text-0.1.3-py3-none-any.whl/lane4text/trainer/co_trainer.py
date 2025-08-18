import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.optim import AdamW,Adam
from torch.optim.lr_scheduler import LambdaLR
import tqdm
from copy import deepcopy


class Trainer:
    """
    Co-Teaching Trainer
    - 使用两个模型互相选择小损失样本
    - 每个 batch 保留一定比例小损失样本更新对方
    - 每 10 个 epoch 学习率衰减 0.1
    """
    def __init__(
        self,
        model1,                       # e.g., transformers.BertForSequenceClassification
        model2,
        device=None,
        lr=2e-5,
        forget_rate=0.3               # 忘记比例，越大越多噪声样本被丢弃
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model1 = model1.to(self.device)
        self.model2 = model2.to(self.device)
        self.optimizer1 = AdamW(self.model1.parameters(), lr=lr)
        self.optimizer2 = AdamW(self.model2.parameters(), lr=lr)
        self.ce = nn.CrossEntropyLoss(reduction="none")
        self.forget_rate = forget_rate

    def compute_forget_rate(self,epoch,total_epochs):
        return epoch/total_epochs*self.forget_rate


    def train(self, train_dataset, test_dataset=None,forget_rate=0.3,epochs=30, batch_size=16):
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size) if test_dataset else None

        for epoch in range(epochs):
            self.model1.train()
            self.model2.train()
            total_loss1, total_loss2 = 0.0, 0.0
            for batch in tqdm.tqdm(train_loader, desc=f"Epoch {epoch+1}"):
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                # 前向
                logits1 = self.model1(input_ids=input_ids, attention_mask=attention_mask, return_dict=True).logits
                logits2 = self.model2(input_ids=input_ids, attention_mask=attention_mask, return_dict=True).logits
                # 计算每个样本的损失
                loss1_per_sample = self.ce(logits1, labels)
                loss2_per_sample = self.ce(logits2, labels)
                forget_rate = self.compute_forget_rate(epoch,epochs)
                # 按小损失排序，取前 (1-forget_rate) 的样本
                keep_num = int((1 - forget_rate) * len(labels))
                idx1_sorted = torch.argsort(loss1_per_sample)[:keep_num]
                idx2_sorted = torch.argsort(loss2_per_sample)[:keep_num]
                # Co-Teaching: 用 model1 筛选的样本更新 model2, 反之亦然
                loss1 = self.ce(logits1[idx2_sorted], labels[idx2_sorted]).mean()
                loss2 = self.ce(logits2[idx1_sorted], labels[idx1_sorted]).mean()
                # 反向传播
                self.optimizer1.zero_grad()
                loss1.backward()
                self.optimizer1.step()
                self.optimizer2.zero_grad()
                loss2.backward()
                self.optimizer2.step()
                total_loss1 += loss1.item()
                total_loss2 += loss2.item()

            avg_loss1 = total_loss1 / max(1, len(train_loader))
            avg_loss2 = total_loss2 / max(1, len(train_loader))
            print(f"[Epoch {epoch+1}] Loss1: {avg_loss1:.4f}  Loss2: {avg_loss2:.4f}  LR: {self.optimizer1.param_groups[0]['lr']:.2e}")

            if test_loader is not None:
                acc1 = self.evaluate(self.model1, test_loader)
                acc2 = self.evaluate(self.model2, test_loader)
                print(f"               Test Acc1: {acc1:.2f}%  Test Acc2: {acc2:.2f}%")

    @torch.no_grad()
    def evaluate(self, model, data_loader):
        model.eval()
        correct, total = 0, 0
        for batch in tqdm.tqdm(data_loader, desc="Eval"):
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)
            logits = model(input_ids=input_ids, attention_mask=attention_mask, return_dict=True).logits
            preds = logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
        return 100.0 * correct / max(1, total)
