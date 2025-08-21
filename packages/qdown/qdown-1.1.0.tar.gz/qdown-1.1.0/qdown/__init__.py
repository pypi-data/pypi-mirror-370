"""

Copyright (c) 2023 Qualiteg Inc. all rights reserved.

This program is dual-licensed under the terms of the:
1) GNU Affero General Public License, version 3, or any later version.
2) A commercial license agreement provided by Qualiteg Inc.

If you choose to use or redistribute this program under the terms of AGPLv3:
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

If you wish to use or redistribute this program under a commercial license:
Please contact Qualiteg Inc.(https://qualiteg.com/contact) directly to obtain the terms and pricing.

"""

import asyncio
import re
from .qdown import QDown


def extract_file_id(url):
    """
    URLからファイルIDを抽出する

    Args:
        url (str): ファイルURL
            例1: https://drive.qualiteg.com/file/3kMM-X9S6-bMioFU0Fn8nHjAgQgWmG
            例2: https://drive.qualiteg.com/download/1Lki-o8QO-DCUmg60JRxGdXfif

    Returns:
        str: ファイルID
    """
    # /file/XXX 形式のURL
    file_pattern = r'https://drive\.qualiteg\.com/file/([a-zA-Z0-9_-]+)'
    file_match = re.search(file_pattern, url)
    if file_match:
        return file_match.group(1)

    # /download/XXX 形式のURL
    download_pattern = r'https://drive\.qualiteg\.com/download/([a-zA-Z0-9_-]+)'
    download_match = re.search(download_pattern, url)
    if download_match:
        return download_match.group(1)

    return url  # IDと思われる場合はそのまま返す


def download(download_url, output_path=None, output_dir=None, server_url="https://drive.qualiteg.com", quiet=False):
    """
    URLを指定してファイルをダウンロード

    Args:
        download_url (str): ダウンロードURL or ファイルID
        output_path (str, optional): 出力ファイルパス
        output_dir (str, optional): 出力ディレクトリ
        server_url (str, optional): サーバーURL
        quiet (bool, optional): 進捗表示を非表示にするかどうか

    Returns:
        str: ダウンロードしたファイルのパス
    """
    # URLからファイルIDを抽出
    file_id = extract_file_id(download_url)

    # QDownクライアントの初期化
    client = QDown(server_url=server_url, quiet=quiet)

    # 同期版メソッドを呼び出す
    return client.download_by_file_id_sync(
        file_id=file_id,
        output=output_path,
        output_dir=output_dir
    )