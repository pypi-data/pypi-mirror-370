import logging
import os
import re
import shutil

import fitz
import numpy as np
import requests
from scipy.spatial.distance import cosine

from jcweaver.api import lifecycle
from jcweaver.api.api import input_prepare, output_prepare
from jcweaver.core.model import DATASET, PLATFORM_MODELARTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 输入输出路径
# input_file_path = "./input_files"        # 输入目录
# output_dir = "saveChunk"                 # 文本块存放目录
# output_file_path = "./output_dataset/output.json"  # 最终数据集输出路径

input_file_path = input_prepare(DATASET, '')
output_dir = "saveChunk"  # 文本块存放目录
output_file_path = output_prepare(DATASET, 'output.json')  # 最终数据集输出路径

# 文本分块参数
chunk_max_length = 500  # 每个文本块最大字符数
start_chunk_threshold = 1000  # 超过这个长度开始分块
similarity_threshold = 0.7  # 语义相似度阈值

# 数据集生成参数
entries_per_file = 2

# Ollama 本地 API
ollama_url = "http://127.0.0.1:11434/api/generate"
ollama_model = "qwen3:4b"


# ------------------ 工具函数 ------------------
def clean_dir(directory):
    """清空并创建文件夹"""
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logger.info(f"删除文件夹 {directory}")
    os.makedirs(directory, exist_ok=True)
    logger.info(f"创建文件夹 {directory}")


def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def pdf_to_text(pdf_path, txt_path):
    """PDF 转 TXT"""
    pdf_document = fitz.open(pdf_path)
    with open(txt_path, "w", encoding="utf-8") as text_file:
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text_file.write(page.get_text())
    pdf_document.close()


def get_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext == ".txt":
        return "txt"
    elif ext == ".pdf":
        return "pdf"
    else:
        return "unknown"


def save_chunks_to_files(chunks, output_dir):
    """保存文本块到文件"""
    os.makedirs(output_dir, exist_ok=True)
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(output_dir, f"chunk_{i + 1}.txt")
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(chunk)
        logger.info(f"保存文本块 {i + 1} -> {chunk_file}")


def get_sentence_embedding(sentence):
    """获取句子向量表示，暂用简单字符向量，可替换为更精细方法"""
    vec = np.array([ord(c) for c in sentence])
    if len(vec) == 0:
        vec = np.zeros(1)
    return vec / (np.linalg.norm(vec) + 1e-8)


def split_text_by_semantic(text, chunk_max_length, similarity_threshold=0.7):
    """基于简单语义相似度分块"""
    sentences = re.split(r"(?<=[。！？；\n])", text)
    chunks = []
    if not sentences:
        return [text]
    current_chunk = sentences[0]
    current_embedding = get_sentence_embedding(current_chunk)
    for s in sentences[1:]:
        s = s.strip()
        if not s:
            continue
        emb = get_sentence_embedding(s)
        sim = 1 - cosine(current_embedding, emb)
        if sim > similarity_threshold and len(current_chunk + s) <= chunk_max_length:
            current_chunk += s
            current_embedding = (current_embedding + emb) / 2
        else:
            chunks.append(current_chunk)
            current_chunk = s
            current_embedding = emb
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def generate_single_entry_ollama(text):
    """调用本地 Ollama HTTP API 生成单条 JSON 指令"""
    payload = {
        "model": ollama_model,
        "prompt": f"""
            基于以下文本生成1条高质量JSON指令条目：
            {text}
            
            生成格式：
            {{
            "instruction": "...",
            "input": "...",
            "output": "..."
            }}
        """,
        "stream": False  # 👈 关键：禁用流式，直接一次性返回完整 JSON
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=120)
        if response.status_code != 200:
            logger.error(f"Ollama 返回错误 {response.status_code}: {response.text}")
            return None

        data = response.json()
        # Ollama 的非流式返回里 "response" 字段就是完整的生成文本
        return data.get("response", "").strip()

    except Exception as e:
        logger.error(f"调用 Ollama 生成条目失败: {e}")
        return None


def generate_dataset(folder_path, output_file_path, entries_per_file=2):
    """生成数据集"""
    result_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            text = read_text_file(file_path)
            logger.info(f"处理 {filename}")
            for j in range(entries_per_file):
                logger.info(f"  生成第 {j + 1}/{entries_per_file} 条")
                entry = generate_single_entry_ollama(text)
                if entry:
                    result_list.append(entry)
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("{\n" + ",\n".join(result_list) + "\n}")
    logger.info(f"数据集已保存到 {output_file_path}")


@lifecycle(platform=PLATFORM_MODELARTS)
def run():
    clean_dir(output_dir)

    for root, dirs, files in os.walk(input_file_path):
        for file in files:
            input_file = os.path.join(root, file)
            ftype = get_file_type(input_file)
            if ftype == "pdf":
                txt_file = input_file + ".txt"
                pdf_to_text(input_file, txt_file)
                input_file = txt_file
            elif ftype == "unknown":
                logger.warning(f"跳过不支持文件类型: {input_file}")
                continue
            text = read_text_file(input_file)
            chunks = [text]
            if len(text) > start_chunk_threshold:
                chunks = split_text_by_semantic(text, chunk_max_length, similarity_threshold)
            save_chunks_to_files(chunks, output_dir)

    logger.info("开始生成数据集...")
    generate_dataset(output_dir, output_file_path, entries_per_file)


if __name__ == "__main__":
    run()
