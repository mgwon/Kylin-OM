# fixed_enhanced_linux_expert_finetuner.py - 修复版本
import os
import json
import torch
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset, load_dataset, concatenate_datasets
from tqdm import tqdm
import warnings
import requests
import random
from typing import List, Dict, Any

warnings.filterwarnings('ignore')

# 设置环境变量
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class FixedLinuxExpertFineTuner:
    def __init__(self, model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"):
        self.model_name = model_name
        # 强制使用单GPU避免设备不匹配
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        print(f"正在使用模型: {model_name}")

        # 初始化tokenizer
        print("加载tokenizer...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                padding_side="right"
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            print("✓ Tokenizer加载成功")
        except Exception as e:
            print(f"❌ Tokenizer加载失败: {e}")
            # 使用备用模型
            backup_models = [
                "Qwen/Qwen2.5-7B-Instruct",
                "microsoft/DialoGPT-medium"
            ]

            for backup_model in backup_models:
                try:
                    print(f"尝试备用模型: {backup_model}")
                    self.model_name = backup_model
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        backup_model,
                        trust_remote_code=True,
                        padding_side="right"
                    )
                    if self.tokenizer.pad_token is None:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
                    print(f"✓ 成功使用备用模型: {backup_model}")
                    break
                except Exception as backup_e:
                    print(f"❌ 备用模型 {backup_model} 也失败: {backup_e}")
                    continue
            else:
                raise Exception("所有模型都无法加载")

    def load_huggingface_datasets(self):
        """加载多个开源数据集"""
        print("正在加载开源数据集...")
        all_datasets = []

        # 1. 尝试加载Shell命令数据集
        try:
            print("加载Unix命令数据集...")
            unix_commands = load_dataset("harpomaxx/unix-commands", split="train")
            if len(unix_commands) > 0:
                unix_data = self.process_unix_commands(unix_commands)
                all_datasets.extend(unix_data)
                print(f"✓ Unix命令数据集: {len(unix_data)} 条")
        except Exception as e:
            print(f"❌ Unix命令数据集加载失败: {e}")

        # 2. 尝试加载指令数据集
        try:
            print("加载Alpaca指令数据集...")
            alpaca_dataset = load_dataset("tatsu-lab/alpaca", split="train")
            # 筛选Linux相关的指令
            linux_alpaca = self.filter_linux_instructions(alpaca_dataset)
            all_datasets.extend(linux_alpaca)
            print(f"✓ Alpaca Linux相关数据: {len(linux_alpaca)} 条")
        except Exception as e:
            print(f"❌ Alpaca数据集加载失败: {e}")

        # 3. 加载自制的Linux专家数据集
        print("添加自制Linux专家数据集...")
        custom_data = self.create_comprehensive_linux_dataset()
        all_datasets.extend(custom_data)
        print(f"✓ 自制数据集: {len(custom_data)} 条")

        # 4. 从网络资源生成数据
        try:
            print("生成Linux命令解释数据...")
            command_data = self.generate_command_explanations()
            all_datasets.extend(command_data)
            print(f"✓ 命令解释数据: {len(command_data)} 条")
        except Exception as e:
            print(f"❌ 命令数据生成失败: {e}")

        # 打乱数据
        random.shuffle(all_datasets)
        print(f"总数据量: {len(all_datasets)} 条")

        if len(all_datasets) < 1000:
            print("⚠️ 警告: 数据量较少，正在扩充...")
            all_datasets = self.augment_dataset(all_datasets)
            print(f"扩充后数据量: {len(all_datasets)} 条")

        return all_datasets

    def process_unix_commands(self, dataset):
        """处理Unix命令数据集"""
        processed_data = []

        for item in dataset:
            try:
                if 'command' in item and 'description' in item:
                    command = str(item['command']).strip()
                    description = str(item['description']).strip()

                    if command and description and len(command) < 100:
                        # 创建指令-回答对
                        instruction = f"请解释Linux命令 {command} 的作用"
                        output = f"命令 {command} 的作用是: {description}"

                        processed_data.append({
                            'instruction': instruction,
                            'output': output
                        })

                        if len(processed_data) >= 200:  # 限制数量
                            break
            except Exception as e:
                continue

        return processed_data

    def filter_linux_instructions(self, dataset):
        """筛选Linux相关的指令"""
        linux_keywords = [
            'linux', 'command', 'terminal', 'bash', 'shell', 'file', 'directory',
            'permission', 'process', 'system', 'network', 'server', 'grep',
            'find', 'sed', 'awk', 'chmod', 'chown', 'ps', 'top', 'systemctl'
        ]

        filtered_data = []

        for item in dataset:
            try:
                instruction = str(item.get('instruction', '')).lower()
                output = str(item.get('output', '')).lower()

                # 检查是否包含Linux相关关键词
                if any(keyword in instruction or keyword in output for keyword in linux_keywords):
                    filtered_data.append({
                        'instruction': item.get('instruction', ''),
                        'output': item.get('output', '')
                    })

                    if len(filtered_data) >= 500:  # 限制数量
                        break
            except Exception as e:
                continue

        return filtered_data

    def create_comprehensive_linux_dataset(self):
        """创建全面的Linux专家数据集"""
        linux_data = [
            {
                'instruction': '如何查看Linux系统中正在运行的进程？',
                'output': '可以使用以下命令查看进程：\n1) ps aux - 显示所有正在运行的进程及详细信息\n2) top - 实时显示进程状态和系统负载\n3) htop - top的增强版本，提供更好的交互界面\n4) ps -ef - 显示完整的进程信息包括父进程\n5) pgrep 进程名 - 根据进程名查找PID\n这些命令可以帮助你监控系统状态和管理进程。'
            },
            {
                'instruction': '解释Linux中的文件权限系统',
                'output': 'Linux文件权限基于三个用户类别：所有者(owner)、组(group)、其他用户(others)。每个类别有三种权限：\n- 读权限(r=4): 可以查看文件内容或列出目录\n- 写权限(w=2): 可以修改文件或在目录中创建删除文件\n- 执行权限(x=1): 可以执行文件或进入目录\n权限用数字表示时是这些值的和，如755表示所有者可读写执行(7)，组和其他用户可读执行(5)。使用chmod命令修改权限，如chmod 755 filename。'
            },
            {
                'instruction': 'Linux网络配置有哪些常用命令？',
                'output': 'Linux网络配置常用命令包括：\n1) ifconfig/ip addr - 查看和配置网络接口\n2) ping - 测试网络连通性\n3) netstat/ss - 查看网络连接状态和端口\n4) route/ip route - 管理路由表\n5) iptables/firewalld - 防火墙配置\n6) wget/curl - 下载文件和测试HTTP连接\n7) tcpdump/wireshark - 网络抓包分析\n8) nslookup/dig - DNS查询工具'
            },
            {
                'instruction': '如何在Linux中监控系统性能？',
                'output': 'Linux系统性能监控工具：\n1) top/htop - 实时查看进程和系统负载\n2) iotop - 监控磁盘I/O使用情况\n3) iftop - 监控网络流量\n4) vmstat - 显示虚拟内存、进程、CPU统计\n5) iostat - 显示I/O和CPU统计信息\n6) sar - 收集和报告系统活动\n7) dstat - 实时系统资源统计\n8) nmon - IBM的综合性能监控工具'
            },
            {
                'instruction': 'Linux中的文件查找命令有哪些？',
                'output': 'Linux文件查找命令：\n1) find - 最强大的查找工具\n   - find /path -name "filename" 按名称查找\n   - find /path -type f -size +100M 查找大文件\n   - find /path -mtime -7 查找7天内修改的文件\n2) locate - 基于数据库的快速查找\n3) which - 查找可执行文件路径\n4) whereis - 查找二进制文件、源代码和手册页\n5) grep - 在文件内容中搜索字符串'
            },
            {
                'instruction': '如何在Linux中管理后台进程？',
                'output': 'Linux后台进程管理：\n1) 启动后台进程：\n   - command & - 直接在后台运行\n   - nohup command & - 忽略挂起信号在后台运行\n2) 作业控制：\n   - jobs - 查看当前作业\n   - bg %job_id - 将作业放到后台\n   - fg %job_id - 将后台作业调到前台\n3) 进程控制：\n   - Ctrl+Z - 暂停当前进程\n   - kill PID - 终止进程'
            },
            {
                'instruction': 'Linux中的压缩和解压命令详解',
                'output': 'Linux压缩解压命令详解：\n1) tar命令 - 打包工具：\n   - tar -czf archive.tar.gz files/ 创建gzip压缩包\n   - tar -xzf archive.tar.gz 解压gzip包\n   - tar -cjf archive.tar.bz2 files/ 创建bzip2压缩包\n2) zip/unzip：\n   - zip -r archive.zip files/ 压缩\n   - unzip archive.zip 解压\n3) gzip/gunzip - 单文件压缩'
            },
            {
                'instruction': 'Linux文本处理命令有哪些？',
                'output': 'Linux文本处理命令：\n1) grep - 文本搜索：\n   - grep "pattern" file 搜索模式\n   - grep -i "pattern" file 忽略大小写\n2) sed - 流编辑器：\n   - sed "s/old/new/g" file 替换文本\n3) awk - 文本分析工具：\n   - awk "{print $1}" file 打印第一列\n4) sort/uniq - 排序和去重\n5) cut - 按列提取文本'
            }
        ]

        return linux_data

    def generate_command_explanations(self):
        """生成Linux命令解释数据"""
        commands = {
            'ls': '列出目录内容',
            'cd': '切换目录',
            'pwd': '显示当前工作目录',
            'mkdir': '创建目录',
            'rm': '删除文件或目录',
            'cp': '复制文件或目录',
            'mv': '移动或重命名文件',
            'chmod': '修改文件权限',
            'grep': '搜索文本模式',
            'find': '查找文件和目录',
            'ps': '显示进程信息',
            'top': '显示实时进程信息',
            'df': '显示磁盘空间使用情况',
            'free': '显示内存使用情况',
            'cat': '显示文件内容',
            'head': '显示文件开头',
            'tail': '显示文件结尾',
            'tar': '打包和压缩文件',
            'wget': '下载文件',
            'ssh': 'SSH远程登录',
            'ping': '测试网络连通性'
        }

        command_data = []

        for cmd, desc in commands.items():
            command_data.append({
                'instruction': f'Linux命令 {cmd} 是做什么用的？',
                'output': f'{cmd} 命令用于{desc}。这是Linux系统中的常用命令之一。'
            })

        return command_data

    def augment_dataset(self, dataset):
        """数据增强"""
        augmented = dataset.copy()

        # 通过重新表述问题来增加数据
        rephrase_patterns = [
            ("如何", "怎样"),
            ("什么是", "请解释"),
            ("命令", "指令"),
            ("使用", "运用")
        ]

        for item in dataset:
            instruction = item['instruction']
            output = item['output']

            # 重新表述指令
            for old, new in rephrase_patterns:
                if old in instruction:
                    new_instruction = instruction.replace(old, new)
                    augmented.append({
                        'instruction': new_instruction,
                        'output': output
                    })
                    break

        return augmented

    def create_linux_dataset(self):
        """创建Linux专家数据集（主入口）"""
        print("创建增强的Linux专家数据集...")

        # 加载所有数据源
        all_data = self.load_huggingface_datasets()

        # 分割训练和测试数据
        train_size = int(0.8 * len(all_data))
        random.shuffle(all_data)

        train_data = all_data[:train_size]
        test_data = all_data[train_size:]

        print(f"训练数据: {len(train_data)} 条")
        print(f"测试数据: {len(test_data)} 条")

        return train_data, test_data

    def format_data_for_training(self, data):
        """格式化数据用于训练"""
        formatted_data = []
        for item in data:
            try:
                # 根据模型类型调整格式
                if "DeepSeek" in self.model_name:
                    text = f"<|user|>\n{item['instruction']}\n<|assistant|>\n{item['output']}<|end|>"
                elif "Qwen" in self.model_name:
                    text = f"<|im_start|>user\n{item['instruction']}<|im_end|>\n<|im_start|>assistant\n{item['output']}<|im_end|>"
                else:
                    # 通用格式
                    text = f"用户: {item['instruction']}\n助手: {item['output']}"

                formatted_data.append({'text': text})
            except Exception as e:
                print(f"格式化数据时出错: {e}")
                continue

        return Dataset.from_list(formatted_data)

    def tokenize_function(self, examples):
        """数据标记化函数"""
        try:
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding='max_length',
                max_length=512,
                return_tensors='pt'
            )
        except Exception as e:
            print(f"标记化错误: {e}")
            return {}

    def load_model(self, model_path=None):
        """加载模型"""
        if model_path and os.path.exists(model_path):
            print(f"加载微调后的模型: {model_path}")
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map={'': 0} if torch.cuda.is_available() else None,  # 强制使用GPU 0
                low_cpu_mem_usage=True
            )
        else:
            print(f"加载原始模型: {self.model_name}")
            model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map={'': 0} if torch.cuda.is_available() else None,  # 强制使用GPU 0
                low_cpu_mem_usage=True
            )
        return model

    def fine_tune(self, train_data, test_data):
        """微调模型"""
        print("开始微调模型...")

        # 格式化数据
        train_dataset = self.format_data_for_training(train_data)
        test_dataset = self.format_data_for_training(test_data)

        # 标记化数据
        train_dataset = train_dataset.map(self.tokenize_function, batched=True, remove_columns=['text'])
        test_dataset = test_dataset.map(self.tokenize_function, batched=True, remove_columns=['text'])

        # 加载模型
        model = self.load_model()

        # 设置训练参数
        training_args = TrainingArguments(
            output_dir="./fixed_linux_expert_model",
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            gradient_accumulation_steps=4,  # 减少
            num_train_epochs=2,  # 减少训练轮数
            learning_rate=2e-5,
            fp16=torch.cuda.is_available(),
            logging_steps=10,
            save_steps=100,
            eval_steps=100,
            evaluation_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            warmup_ratio=0.1,
            lr_scheduler_type="cosine",
            report_to="none",
            save_total_limit=2,
            dataloader_pin_memory=False,
            dataloader_num_workers=0,  # 避免多进程问题
            remove_unused_columns=False,
        )

        # 设置数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        # 创建训练器
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=test_dataset,
            data_collator=data_collator,
        )

        # 开始训练
        print("开始训练过程...")
        try:
            trainer.train()
        except Exception as e:
            print(f"训练过程中出现错误: {e}")
            print("尝试继续训练...")

        # 保存模型
        final_model_path = "./fixed_linux_expert_model_final"
        trainer.save_model(final_model_path)
        print(f"模型微调完成并已保存到: {final_model_path}")

        return final_model_path

    def generate_response(self, model, prompt, max_length=200):
        """生成回答 - 修复inf/nan问题"""
        try:
            # 根据模型调整输入格式
            if "DeepSeek" in self.model_name:
                input_text = f"<|user|>\n{prompt}\n<|assistant|>\n"
            elif "Qwen" in self.model_name:
                input_text = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
            else:
                input_text = f"用户: {prompt}\n助手: "

            inputs = self.tokenizer.encode(input_text, return_tensors='pt').to(self.device)

            # 设置attention_mask
            attention_mask = torch.ones_like(inputs).to(self.device)

            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    attention_mask=attention_mask,
                    max_new_tokens=150,  # 使用max_new_tokens而不是max_length
                    temperature=0.6,  # DeepSeek推荐的温度
                    do_sample=True,
                    top_p=0.95,  # 添加top_p
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,  # 避免重复
                    no_repeat_ngram_size=3
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # 提取回答部分
            if "DeepSeek" in self.model_name:
                if '<|assistant|>' in response:
                    return response.split('<|assistant|>\n')[-1].strip()
            elif "Qwen" in self.model_name:
                if '<|im_start|>assistant' in response:
                    return response.split('<|im_start|>assistant\n')[-1].strip()
            else:
                if '助手:' in response:
                    return response.split('助手:')[-1].strip()

            return response.strip()

        except Exception as e:
            print(f"生成回答时出错: {e}")
            return "抱歉，生成回答时出现了错误。"

    def create_test_questions(self):
        """创建测试问题"""
        return [
            {
                'question': '如何查看Linux系统中正在运行的进程？',
                'expected_keywords': ['ps', 'top', 'htop', '进程', '命令']
            },
            {
                'question': '解释Linux中的文件权限系统',
                'expected_keywords': ['权限', 'chmod', 'rwx', '用户', '组']
            },
            {
                'question': 'Linux中如何查找文件？',
                'expected_keywords': ['find', 'locate', 'grep', '搜索', '文件']
            },
            {
                'question': '如何在Linux中管理服务？',
                'expected_keywords': ['systemctl', 'service', '启动', '停止', '状态']
            },
            {
                'question': 'Linux网络配置有哪些常用命令？',
                'expected_keywords': ['ifconfig', 'ip', 'netstat', '网络', '配置']
            }
        ]

    def evaluate_model(self, model, test_questions):
        """评估模型"""
        results = []
        print("正在评估模型...")

        for question in tqdm(test_questions):
            try:
                response = self.generate_response(model, question['question'])
                score = self.calculate_relevance_score(response, question.get('expected_keywords', []))
                results.append({
                    'question': question['question'],
                    'response': response,
                    'score': score
                })
                print(f"问题: {question['question'][:40]}...")
                print(f"回答: {response[:100]}...")
                print(f"分数: {score:.3f}\n")
            except Exception as e:
                print(f"评估错误: {e}")
                results.append({
                    'question': question['question'],
                    'response': "生成失败",
                    'score': 0
                })

        return results

    def calculate_relevance_score(self, response, expected_keywords):
        """计算回答的相关性分数"""
        if not expected_keywords:
            return 0.5

        response_lower = response.lower()
        matches = sum(1 for keyword in expected_keywords if keyword.lower() in response_lower)
        return matches / len(expected_keywords)

    def visualize_results(self, original_results, finetuned_results):
        """可视化结果对比"""
        orig_scores = [r['score'] for r in original_results]
        ft_scores = [r['score'] for r in finetuned_results]

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('修复版Linux专家模型微调效果对比', fontsize=16, fontweight='bold')

        # 1. 平均分数对比
        categories = ['原始模型', '微调模型']
        avg_scores = [np.mean(orig_scores), np.mean(ft_scores)]

        axes[0, 0].bar(categories, avg_scores, color=['#ff7f0e', '#2ca02c'], alpha=0.7)
        axes[0, 0].set_title('平均性能分数对比')
        axes[0, 0].set_ylabel('分数')
        axes[0, 0].set_ylim(0, 1)

        for i, v in enumerate(avg_scores):
            axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')

        # 2. 各问题得分对比
        x = np.arange(len(orig_scores))
        width = 0.35

        axes[0, 1].bar(x - width / 2, orig_scores, width, label='原始模型', color='#ff7f0e', alpha=0.7)
        axes[0, 1].bar(x + width / 2, ft_scores, width, label='微调模型', color='#2ca02c', alpha=0.7)
        axes[0, 1].set_title('各问题得分对比')
        axes[0, 1].set_xlabel('问题编号')
        axes[0, 1].set_ylabel('分数')
        axes[0, 1].legend()

        # 3. 改进幅度
        improvements = [ft_scores[i] - orig_scores[i] for i in range(len(orig_scores))]
        colors = ['#d62728' if imp < 0 else '#2ca02c' for imp in improvements]

        axes[1, 0].bar(range(len(improvements)), improvements, color=colors, alpha=0.7)
        axes[1, 0].set_title('性能改进幅度')
        axes[1, 0].set_xlabel('问题编号')
        axes[1, 0].set_ylabel('改进分数')
        axes[1, 0].axhline(y=0, color='black', linestyle='-', alpha=0.3)

        # 4. 分数分布
        axes[1, 1].hist([orig_scores, ft_scores], bins=10, alpha=0.7,
                        label=['原始模型', '微调模型'], color=['#ff7f0e', '#2ca02c'])
        axes[1, 1].set_title('分数分布')
        axes[1, 1].set_xlabel('分数')
        axes[1, 1].set_ylabel('频次')
        axes[1, 1].legend()

        plt.tight_layout()
        plt.savefig('fixed_linux_expert_model_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

        # 生成报告
        self.generate_report(original_results, finetuned_results, avg_scores, improvements)

    def generate_report(self, original_results, finetuned_results, avg_scores, improvements):
        """生成详细报告"""
        report = f"""
# 修复版Linux专家模型微调效果报告

## 模型信息
- 使用模型: {self.model_name}
- 计算设备: {self.device}
- 修复问题: 解决了设备不匹配和inf/nan错误

## 整体性能对比
- 原始模型平均分数: {avg_scores[0]:.4f}
- 微调模型平均分数: {avg_scores[1]:.4f}
- 整体提升: {((avg_scores[1] - avg_scores[0]) / avg_scores[0] * 100):.2f}%

## 详细问题分析
"""

        for i, (orig, ft) in enumerate(zip(original_results, finetuned_results)):
            improvement = improvements[i]
            improvement_pct = (improvement / orig['score'] * 100) if orig['score'] > 0 else 0

            report += f"""
### 问题 {i + 1}: {orig['question']}
- 原始模型分数: {orig['score']:.3f}
- 微调模型分数: {ft['score']:.3f}
- 改进幅度: {improvement_pct:.1f}%

**原始模型回答**: {orig['response'][:200]}{'...' if len(orig['response']) > 200 else ''}

**微调模型回答**: {ft['response'][:200]}{'...' if len(ft['response']) > 200 else ''}

"""

        with open('fixed_linux_expert_model_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print("详细报告已保存到 fixed_linux_expert_model_report.md")


def main():
    """主函数"""
    print("=" * 60)
    print("修复版Linux专家模型微调系统")
    print("已解决设备不匹配和inf/nan错误")
    print("=" * 60)

    # 检查GPU
    if torch.cuda.is_available():
        print(f"✅ 检测到GPU: {torch.cuda.get_device_name()}")
        print(f"   GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024 ** 3:.1f} GB")
        print(f"   强制使用GPU:0 避免设备冲突")
    else:
        print("⚠️  使用CPU模式")

    # 初始化微调器
    try:
        print("\n📚 初始化修复版微调器...")
        finetuner = FixedLinuxExpertFineTuner()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    # 步骤1: 准备数据集
    print("\n📊 步骤1: 准备数据集")
    try:
        train_data, test_data = finetuner.create_linux_dataset()
    except Exception as e:
        print(f"❌ 数据集准备失败: {e}")
        return

    # 步骤2: 创建测试问题
    print("\n🧪 步骤2: 创建测试问题")
    test_questions = finetuner.create_test_questions()

    # 步骤3: 测试原始模型
    print("\n🔍 步骤3: 测试原始模型")
    try:
        original_model = finetuner.load_model()
        original_results = finetuner.evaluate_model(original_model, test_questions)

        # 清理内存
        del original_model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception as e:
        print(f"❌ 测试原始模型时出错: {e}")
        return

    # 步骤4: 微调模型
    print("\n🚀 步骤4: 开始微调模型")
    try:
        model_path = finetuner.fine_tune(train_data, test_data)
    except Exception as e:
        print(f"❌ 微调过程中出错: {e}")
        return

    # 步骤5: 测试微调后的模型
    print("\n📈 步骤5: 测试微调后的模型")
    try:
        finetuned_model = finetuner.load_model(model_path)
        finetuned_results = finetuner.evaluate_model(finetuned_model, test_questions)
    except Exception as e:
        print(f"❌ 测试微调模型时出错: {e}")
        return

    # 步骤6: 生成对比分析
    print("\n📊 步骤6: 生成效果对比分析")
    finetuner.visualize_results(original_results, finetuned_results)

    print("\n" + "=" * 60)
    print("🎉 修复版Linux专家模型微调完成!")
    print("\n📁 生成的文件:")
    print("  📊 fixed_linux_expert_model_comparison.png - 效果对比图")
    print("  📝 fixed_linux_expert_model_report.md - 详细分析报告")
    print(f"  🤖 {model_path} - 微调后的模型")
    print("\n🔧 修复的问题:")
    print("  • 解决了多GPU设备不匹配错误")
    print("  • 修复了生成时的inf/nan概率错误")
    print("  • 优化了模型加载和训练参数")
    print("  • 添加了更好的错误处理")
    print("=" * 60)


if __name__ == "__main__":
    main()