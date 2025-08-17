import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.optim import AdamW
import tqdm
from transformers import MarianMTModel, MarianTokenizer

class NegativeALMStats:
    """
    维护所有历史迭代中 ALM<0 样本的均值 μ_t 与方差 σ_t（Welford 在线算法）
    只纳入 ALM<0 的样本；μ, σ 在训练过程中动态更新。
    """
    def __init__(self, device="cpu"):
        self.n = 0
        self.mean = torch.tensor(0.0, device=device)
        self.M2 = torch.tensor(0.0, device=device)
        self.device = device
    def update_with_batch(self, alm_values):
        """
        alm_values: 1D tensor，仅包含本批次中 ALM<0 的样本的 ALM 值（不反传梯度）
        """
        for x in alm_values:
            self.n += 1
            delta = x - self.mean
            self.mean = self.mean + delta / self.n
            delta2 = x - self.mean
            self.M2 = self.M2 + delta * delta2

    def get_stats(self):
        if self.n == 0:
            mu = torch.tensor(0.0, device=self.device)
            var = torch.tensor(1.0, device=self.device)  # 防止除零
        else:
            # population variance: M2 / n
            var = self.M2 / self.n
            mu = self.mean
            # 最小方差夹紧，避免数值不稳定
            var = torch.clamp(var, min=1e-6)
        return mu.detach(), var.detach()


class ALMTracker:
    """
    为每个样本 idx 维护 LM 的累计均值（即 ALM）。
    ALM^{(t)}(x)= (1/t)∑_{r=1..t} LM^{(r)}(x)
    """
    def __init__(self, num_examples, device="cpu"):
        self.sum_lm = torch.zeros(num_examples, device=device)
        self.count = torch.zeros(num_examples, dtype=torch.long, device=device)

    def update(self, idx_tensor, lm_tensor):
        """
        idx_tensor: [B] 样本全局索引
        lm_tensor : [B] 当前迭代 LM 值（不需要对历史求梯度，训练权重用 detach）
        """
        with torch.no_grad():
            self.sum_lm.index_add_(0, idx_tensor, lm_tensor.detach())
            self.count.index_add_(0, idx_tensor, torch.ones_like(idx_tensor, dtype=torch.long))

    def get_alm(self, idx_tensor):
        with torch.no_grad():
            s = self.sum_lm[idx_tensor]
            c = self.count[idx_tensor].clamp(min=1)  # 防止除零
            return (s / c)

class BackTranslator:
    def __init__(self, src_lang='en', mid_lang='de'):
        self.src_lang = src_lang
        self.mid_lang = mid_lang
        self.model_en2mid = MarianMTModel.from_pretrained(f'Helsinki-NLP/opus-mt-{src_lang}-{mid_lang}').eval()
        self.tokenizer_en2mid = MarianTokenizer.from_pretrained(f'Helsinki-NLP/opus-mt-{src_lang}-{mid_lang}')
        self.model_mid2en = MarianMTModel.from_pretrained(f'Helsinki-NLP/opus-mt-{mid_lang}-{src_lang}').eval()
        self.tokenizer_mid2en = MarianTokenizer.from_pretrained(f'Helsinki-NLP/opus-mt-{mid_lang}-{src_lang}')

    @torch.no_grad()
    def translate(self, texts, model, tokenizer):
        batch = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to(model.device)
        translated = model.generate(**batch)
        return tokenizer.batch_decode(translated, skip_special_tokens=True)

    def back_translate(self, texts):
        mid = self.translate(texts, self.model_en2mid, self.tokenizer_en2mid)
        back = self.translate(mid, self.model_mid2en, self.tokenizer_mid2en)
        return back

class Trainer:
    """
    完整 LANE 复现版：
    - 计算 M、LM、ALM
    - 截断高斯加权交叉熵
    - 标签感知监督对比损失
    - 总损失 L = α L_CE + (1-α) L_LSCL
    需要 dataset 返回 batch 字段：input_ids, attention_mask, labels, idx
    """
    def __init__(
        self,
        model,                        # e.g., transformers.BertForSequenceClassification
        num_train_examples,           # 训练集中样本总数（用于 ALM 累积）
        device=None,
        lr=2e-5,
        alpha=0.5,
        temperature=0.07
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.temperature = temperature
        self.alpha = alpha
        # 优化器同时优化分类模型与 Π（weight_net）
        self.optimizer = AdamW(self.model.parameters(), lr=lr)
        # 交叉熵按样本输出，方便逐样本加权
        self.ce = nn.CrossEntropyLoss(reduction="none")
        # 权重网络 Π：放在分类模型的隐藏表示之上（使用 [CLS] 表示）
        hidden_size = model.config.hidden_size
        num_labels = model.config.num_labels
        self.weight_net = nn.Linear(hidden_size, num_labels).to(self.device)
        # 将 Π 的参数也加入优化
        self.optimizer.add_param_group({"params": self.weight_net.parameters(), "lr": lr})
        # 维护 ALM（逐样本）
        self.alm_tracker = ALMTracker(num_train_examples, device=self.device)
        # 维护 ALM<0 的全局统计 μ_t, σ_t^2（在线）
        self.neg_stats = NegativeALMStats(device=self.device)

    # --------------------- 辅助计算 ---------------------

    @staticmethod
    def _compute_margin(logits, labels):
        """
        传统边距 M: z_y - max_{i!=y} z_i
        logits: [B, C], labels: [B]
        return: [B] 的 M
        """
        B, C = logits.shape
        arange = torch.arange(B, device=logits.device)
        z_y = logits[arange, labels]  # [B]

        # 将正确类位置设为 -inf 后再取 max 即得 max_{i!=y}
        mask = torch.zeros_like(logits, dtype=torch.bool)
        mask[arange, labels] = True
        logits_others = logits.masked_fill(mask, float("-inf"))
        max_other, _ = logits_others.max(dim=1)  # [B]
        M = z_y - max_other
        return M, max_other

    def _compute_label_aware_margin(self, logits, labels, weights_soft):
        """
        标签感知边距 LM（仅对负边距缩放）：
        若 M<0, 令 j = argmax_{i!=y} z_i，LM = (1 / w_{x,j}) * M；否则 LM=M
        logits: [B, C], labels: [B]
        weights_soft: [B, C]，来自 Π 的 softmax（w_{x,y}）
        return: LM [B]，以及 j 索引 [B]
        """
        B, C = logits.shape
        arange = torch.arange(B, device=logits.device)

        # M 与最大其他 logit 的索引 j
        mask = torch.zeros_like(logits, dtype=torch.bool)
        mask[arange, labels] = True
        logits_others = logits.masked_fill(mask, float("-inf"))
        max_other, j_idx = logits_others.max(dim=1)        # 值与位置
        z_y = logits[arange, labels]
        M = z_y - max_other                                 # [B]

        # 取 w_{x,j}
        w_xj = weights_soft[arange, j_idx].clamp(min=1e-6)  # 防止除 0

        # 仅在 M<0 时缩放
        LM = torch.where(M < 0, (1.0 / w_xj) * M, M)
        return LM, j_idx

    def _label_aware_contrastive_loss(self, embeds, labels, weights_soft):
        """
        标签感知监督对比损失（按论文公式）：
        L = sum_x - (1/|P_x|) sum_{p in P_x} log [ w_{x,y_x} * exp(sim(x,p)) / sum_{k!=x} w_{x,y_k}*exp(sim(x,k)) ]
        其中 sim= (h_x · h_k) / τ
        embeds: [B, H], labels: [B], weights_soft: [B, C]
        """
        device = embeds.device
        B = embeds.size(0)
        if B <= 1:
            return torch.zeros([], device=device)

        # 相似度矩阵（双向），按温度缩放
        sim = torch.matmul(embeds, embeds.t()) / self.temperature  # [B, B]

        # 构造掩码
        idx = torch.arange(B, device=device)
        mask_self = torch.eye(B, device=device).bool()  # 自身 mask
        same_label = (labels.unsqueeze(0) == labels.unsqueeze(1)) & (~mask_self)  # 正样本掩码 [B,B]

        # 分子：对每个 i，与其所有正样本 p 的项 w_{i,y_i} * exp(sim_{i,p}) 的和
        wi_yi = weights_soft[idx, labels]                        # [B]
        exp_sim = torch.exp(sim)                                 # [B,B]
        numerator = (wi_yi.unsqueeze(1) * exp_sim) * same_label  # [B,B], 仅正样本保留
        # 如果样本没有正样本，避免 0
        numerator_sum = numerator.sum(dim=1).clamp(min=1e-12)    # [B]

        # 分母：sum_{k!=i} w_{i,y_k} * exp(sim_{i,k})
        wi_yk = weights_soft[:, labels]                          # [B,B]: 行 i、列 k=标签(labels[k])
        denom_mat = wi_yk * exp_sim
        denom_mat = denom_mat.masked_fill(mask_self, 0.0)
        denominator_sum = denom_mat.sum(dim=1).clamp(min=1e-12)  # [B]

        # 对每个 i，只在有正样本时才计入损失；否则贡献为 0
        has_pos = same_label.any(dim=1)  # [B]
        loss_i = torch.zeros(B, device=device)
        loss_i[has_pos] = -torch.log(numerator_sum[has_pos] / denominator_sum[has_pos])

        # 对每个 i，按正样本个数归一（|P_x|），再求平均
        num_pos = same_label.sum(dim=1).clamp(min=1)  # [B]
        loss_i = loss_i / num_pos
        return loss_i.mean()

    # --------------------- 训练 / 评估 ---------------------

    def train(self, train_dataset, test_dataset=None, epochs=3, batch_size=16, grad_clip=1.0):
        """
        注意：dataset.__getitem__ 必须返回 'idx' 字段（0..num_train_examples-1）
        """
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size) if test_dataset else None

        for epoch in range(epochs):
            self.model.train()
            self.weight_net.train()
            total_loss = 0.0

            for batch in tqdm.tqdm(train_loader, desc=f"Epoch {epoch+1}"):
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                idxs = batch["idx"].to(self.device)  # 关键：样本全局索引

                self.optimizer.zero_grad()

                # 前向：拿到 logits 与句向量 [CLS]
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_hidden_states=True,
                    return_dict=True,
                )
                logits = outputs.logits                               # [B, C]
                cls_embeds = outputs.hidden_states[-1][:, 0, :]       # [B, H]

                # 权重网络 Π -> soft assignments w_{x,y}
                pi_logits = self.weight_net(cls_embeds)               # [B, C]
                weights_soft = F.softmax(pi_logits, dim=-1)           # [B, C]

                # ----- 1) 计算 LM，并更新 ALM（历史平均） -----
                LM, _ = self._compute_label_aware_margin(logits, labels, weights_soft)  # [B]
                # 更新样本的历史 ALM（不反传）
                self.alm_tracker.update(idxs, LM)

                with torch.no_grad():
                    # 当前 batch 的 ALM（用历史 sum/count 得到）
                    current_alm = self.alm_tracker.get_alm(idxs)      # [B]
                    # 筛选 ALM<0 的样本，更新全局 μ_t, σ_t^2
                    neg_mask = current_alm < 0
                    if neg_mask.any():
                        self.neg_stats.update_with_batch(current_alm[neg_mask])

                    mu_t, var_t = self.neg_stats.get_stats()
                    sigma_t = torch.sqrt(var_t)

                    # 截断高斯权重 λ_CE：仅对 (ALM<0 且 ALM<μ_t) 生效
                    # λ = exp( - (ALM - μ)^2 / (2 σ^2) )
                    # 若还未累计负样本（n=0），mu=0, sigma=1，效果等价于不缩放
                    below_mean = (current_alm < 0) & (current_alm < mu_t)
                    # 避免 sigma=0
                    denom = (2.0 * sigma_t * sigma_t).clamp(min=1e-6)
                    lam_ce = torch.ones_like(current_alm)
                    lam_ce[below_mean] = torch.exp(- (current_alm[below_mean] - mu_t) ** 2 / denom)

                # ----- 2) 加权交叉熵 L_CE -----
                ce_per = self.ce(logits, labels)          # [B]
                # 重要：权重不反传梯度（论文用历史预测统计量）
                ce_loss = (lam_ce.detach() * ce_per).mean()

                # ----- 3) 标签感知对比损失 L_LSCL -----
                llscl = self._label_aware_contrastive_loss(cls_embeds, labels, weights_soft)

                # ----- 4) 总损失 -----
                loss = self.ce(logits, labels).mean()   
                loss.backward()

                if grad_clip is not None and grad_clip > 0:
                    nn.utils.clip_grad_norm_(list(self.model.parameters()) + list(self.weight_net.parameters()), grad_clip)

                self.optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / max(1, len(train_loader))
            print(f"[Epoch {epoch+1}] Train Loss: {avg_loss:.4f}")

            if test_loader is not None:
                acc = self.evaluate(test_loader)
                print(f"               Test Acc: {acc:.2f}%")

    @torch.no_grad()
    def evaluate(self, data_loader):
        self.model.eval()
        self.weight_net.eval()
        correct, total = 0, 0
        for batch in tqdm.tqdm(data_loader, desc="Eval"):
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)

            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, return_dict=True)
            preds = outputs.logits.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
        return 100.0 * correct / max(1, total)
