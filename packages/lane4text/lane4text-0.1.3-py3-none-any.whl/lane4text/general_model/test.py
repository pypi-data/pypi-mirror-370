from general_model import QwenFinetuneTool
import pandas as pd

if __name__ == "__main__":
    # 1. 构造训练数据（字段名为“产品名称”“保险条款”“用户问题”“答案”）
    train_df = pd.DataFrame([
        {
            "产品名称": "健康险A",  # 字段名：产品名称
            "保险条款": "投保年龄18-60岁，保障期1年",  # 字段名：保险条款
            "用户问题": "该产品投保年龄限制？",  # 字段名：用户问题
            "答案": "18-60岁"  # 字段名：答案
        }
    ])

    # 2. 构造测试数据（同字段名）
    test_df = pd.DataFrame([
        {
            "产品名称": "健康险A",
            "保险条款": "投保年龄18-60岁，保障期1年",
            "用户问题": "保障期是多久？"
        }
    ])

    # 3. 配置模板：占位符与数据字段名完全一致
    config = {
        "train_data": train_df,
        "test_data": test_df,
        "model_path": "/root/autodl-tmp/qwen3-8b/Qwen/Qwen3-8B",
        "lora_save_path": "/root/autodl-tmp/insurance-lora",
        "result_save_path": "/root/autodl-tmp/insurance_result.csv",
        # 模板占位符直接用数据字段名（产品名称/保险条款/用户问题/答案）
        "instruction_template": "请根据给定的保险产品和条款，简洁回答问题",
        "input_template": "产品：{产品名称}，条款：{保险条款}，问题：{用户问题}",
        "output_template": "### 输出：{答案}",
        "test_output_prefix": "### 输出："
    }

    # 4. 训练+推理（无需任何字段映射配置）
    tool = QwenFinetuneTool(**config)
    tool.train(train_args_dict={"per_device_train_batch_size": 2})
    tool.inference()