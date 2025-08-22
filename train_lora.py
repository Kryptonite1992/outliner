#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小 LoRA 训练脚本示例。
依赖: pip install transformers peft datasets accelerate bitsandbytes (可选)
数据: data/train.jsonl  每行 {"text": "..."}
运行示例:
  python train_lora.py \
    --base_model gpt2 \
    --data_path data/train.jsonl \
    --output_dir lora-out \
    --epochs 2 --batch_size 2
"""
import os
import json
import argparse
from typing import List
from datasets import Dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM, Trainer,
                          TrainingArguments, DataCollatorForLanguageModeling)
from peft import LoraConfig, get_peft_model


def load_jsonl(path: str) -> Dataset:
    rows: List[str] = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            txt = obj.get('text')
            if txt:
                rows.append(txt)
    return Dataset.from_dict({'text': rows})


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base_model', required=True, help='基础模型名称或本地路径')
    ap.add_argument('--data_path', default='data/train.jsonl')
    ap.add_argument('--output_dir', default='lora-out')
    ap.add_argument('--batch_size', type=int, default=2)
    ap.add_argument('--epochs', type=int, default=2)
    ap.add_argument('--lr', type=float, default=2e-4)
    ap.add_argument('--max_length', type=int, default=256)
    ap.add_argument('--lora_r', type=int, default=8)
    ap.add_argument('--lora_alpha', type=int, default=16)
    ap.add_argument('--lora_dropout', type=float, default=0.05)
    ap.add_argument('--fp16', action='store_true')
    ap.add_argument('--bf16', action='store_true')
    return ap.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    print('== 加载分词器 ==')
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print('== 加载数据 ==')
    ds = load_jsonl(args.data_path)

    def tokenize(batch):
        return tokenizer(batch['text'], truncation=True, max_length=args.max_length,
                         padding='max_length')

    tokenized = ds.map(tokenize, batched=True, remove_columns=['text'])

    print('== 加载基础模型 ==')
    model = AutoModelForCausalLM.from_pretrained(args.base_model, device_map='auto', trust_remote_code=True)

    print('== 应用 LoRA ==')
    lora_cfg = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=['c_attn','q_proj','k_proj','v_proj','o_proj'],  # 兼容常见结构, 不存在的会忽略
        lora_dropout=args.lora_dropout,
        task_type='CAUSAL_LM'
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    print('== 配置训练参数 ==')
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=2,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        fp16=args.fp16,
        bf16=args.bf16,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        report_to='none'
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        data_collator=collator
    )

    print('== 开始训练 ==')
    trainer.train()

    print('== 保存 Adapter ==')
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print('完成: 保存到', args.output_dir)


if __name__ == '__main__':
    main()
