from transformers import LongformerTokenizer, LongformerModel

# 下载模型和分词器
tokenizer = LongformerTokenizer.from_pretrained('allenai/longformer-base-4096')
model = LongformerModel.from_pretrained('allenai/longformer-base-4096')

# 保存到本地目录 
tokenizer.save_pretrained('../config_file/longformer/')
model.save_pretrained('../config_file/longformer/')