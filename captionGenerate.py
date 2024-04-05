import torch
from transformers import BertTokenizer
from PIL import Image
from datasets import coco, utils
from configuration import Config
import os
import time

from models import caption


class CaptionGenerator:
    def __init__(self, checkpoint_paths):
        self.config = Config()
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.start_token = self.tokenizer.convert_tokens_to_ids(self.tokenizer.cls_token)
        self.end_token = self.tokenizer.convert_tokens_to_ids(self.tokenizer.sep_token)
        self.models = []

        for checkpoint_path in checkpoint_paths:
            # 检查模型的版本和检查点
            print(f"加载checkpoint模型: {checkpoint_path}")
            if not os.path.exists(checkpoint_path):
                raise NotImplementedError(f'checkpoint路径无效: {checkpoint_path}')
            print("找到checkpoint模型")
            model, _ = caption.build_model(self.config)
            print("加载checkpoint模型中...")
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            model.load_state_dict(checkpoint['model'])
            self.models.append(model)

    def generate_caption(self,image):
        # 读取图像
        # image_path = 'Temp/tempImage.jpg'
        # image = Image.open(image_path)
        image = coco.val_transform(image)
        image = image.unsqueeze(0)

        def create_caption_and_mask(start_token, max_length):
            caption_template = torch.zeros((1, max_length), dtype=torch.long)
            mask_template = torch.ones((1, max_length), dtype=torch.bool)

            caption_template[:, 0] = start_token
            mask_template[:, 0] = False

            return caption_template, mask_template

        captions = []
        for model in self.models:
            caption, cap_mask = create_caption_and_mask(self.start_token, self.config.max_position_embeddings)

            @torch.no_grad()
            def evaluate():
                model.eval()
                for i in range(self.config.max_position_embeddings - 1):
                    predictions = model(image, caption, cap_mask)
                    predictions = predictions[:, i, :]
                    predicted_id = torch.argmax(predictions, axis=-1)

                    if predicted_id[0] == 102:  # 102 对应于 [SEP] token
                        return caption

                    caption[:, i + 1] = predicted_id[0]
                    cap_mask[:, i + 1] = False

                return caption

            T1 = time.time()
            output = evaluate()
            T2 = time.time()
            result = self.tokenizer.decode(output[0].tolist(), skip_special_tokens=True)
            print(f"生成字幕结果: {result.capitalize()}, 生成消耗时间: {T2 - T1} 秒")
            captions.append(result.capitalize())

        return captions