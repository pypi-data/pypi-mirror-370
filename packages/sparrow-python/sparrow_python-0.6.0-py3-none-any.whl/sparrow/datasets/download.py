from datasets import load_dataset
from flaxkv import FlaxKV

db = FlaxKV("infinity")

# 应用自定义解码逻辑

# 流式加载
# ['stage1', 'stage2', 'stage3', 'stage4']
dataset = load_dataset("BAAI/Infinity-MM", "stage2", split="train", streaming=True)

print(dataset)

for sample in dataset:
    for key, value in sample.items():
        if key not in db:
            db[key] = []
        db[key].append(value)
    print(db)
