# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/store/xhs/xhs_store_media.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# -*- coding: utf-8 -*-
# @Author  : helloteemo
# @Time    : 2024/7/11 22:35
# @Desc    : Xiaohongshu media storage
import pathlib
from typing import Dict

import aiofiles
from PIL import Image

from base.base_crawler import AbstractStoreImage, AbstractStoreVideo
from tools import utils
import config
import io
import re
import os
from datetime import datetime
def clean_title(title: str) -> str:
        # 仅去掉非法路径字符
    title = re.sub(r'[\\/:*?"<>|\n\r\t]', '', title)

    # 去掉emoji（可选）
    title = re.sub(r'[\U00010000-\U0010ffff]', '', title)

    return title[:30]   # 控制长度

def safe_name(name: str):
    if not name:
        return "unknown"
    name = re.sub(r'[\\/:"*?<>|\n\r]+', "_", name)
    return name.strip()

class XiaoHongShuImage(AbstractStoreImage):
    def __init__(self):
        if config.SAVE_DATA_PATH:
            self.base_store_path = f"{config.SAVE_DATA_PATH}/xhs"
        else:
            self.base_store_path = "data/xhs"

    async def store_image(self, item: Dict):
        await self.save_image(
            item["pic_content"],
            item["extension_file_name"],
            item["title"],
            item["time"],
            item["nickname"]
        )
    async def save_image(
            self,
            pic_content: bytes,
            extension_file_name: str,
            title: str,
            timestamp: int,
            nickname: str
    ):
        ts = timestamp / 1000

        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        safe_title = clean_title(title)
        idx = extension_file_name.split('.')[0]

        filename = f"{date_str}_{safe_title}_{idx}.jpg"
        safe_nickname = safe_name(nickname)

        user_dir = os.path.join(self.base_store_path, safe_nickname, "images")
        pathlib.Path(user_dir).mkdir(parents=True, exist_ok=True)
        save_path = os.path.join(user_dir, filename)
        if os.path.exists(save_path):
            utils.logger.info(f"[XHS] skip existing {save_path}")
            return
        try:
            img = Image.open(io.BytesIO(pic_content))
            img = img.convert("RGB")

            img.save(
                save_path,
                "JPEG",
                quality=95,
                subsampling=0,   # 保留细节
                optimize=True
            )
            os.utime(save_path, (ts, ts))
            utils.logger.info(f"[XHS] saved {save_path}")

        except Exception as e:
            utils.logger.error(f"[XHS] convert fail, fallback raw save: {e}")

            # ===== fallback 原始写盘 =====
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(pic_content)
            os.utime(save_path, (ts, ts))


class XiaoHongShuVideo(AbstractStoreVideo):
    def __init__(self):
        if config.SAVE_DATA_PATH:
            self.base_store_path = f"{config.SAVE_DATA_PATH}/xhs"
        else:
            self.base_store_path = "data/xhs"

    async def store_video(self, item: Dict):
        await self.save_video(
            item["video_content"],
            item["extension_file_name"],
            item["title"],
            item["time"],
            item["nickname"]
        )


    async def save_video(
        self,
        video_content: bytes,
        extension_file_name: str,
        title: str,
        timestamp: int,
        nickname: str
    ):

        # ========= 命名 =========
        ts = timestamp / 1000
        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        safe_title = clean_title(title)
        safe_nickname = safe_name(nickname)

        idx = extension_file_name.split('.')[0]
        ext = extension_file_name.split('.')[-1]

        filename = f"{date_str}_{safe_title}_{idx}.{ext}"

        user_dir = os.path.join(self.base_store_path, safe_nickname, "videos")
        pathlib.Path(user_dir).mkdir(parents=True, exist_ok=True)
        save_path = os.path.join(user_dir, filename)
        if os.path.exists(save_path):
            utils.logger.info(f"[XHS] skip existing {save_path}")
            return
        async with aiofiles.open(save_path, 'wb') as f:
            await f.write(video_content)
        os.utime(save_path, (ts, ts))
        utils.logger.info(f"[XHS] saved video {save_path}")