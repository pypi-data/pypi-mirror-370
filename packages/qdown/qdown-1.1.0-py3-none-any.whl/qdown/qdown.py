"""
qdown - Client for QualitegDrive

使用方法:
  qdown ID [オプション]

オプション:
  -O FILENAME     出力ファイル名を指定
  -o DIR          出力ディレクトリを指定
  -s SERVER       サーバーURLを指定 (デフォルト: https://drive.qualiteg.com)
  -q, --quiet     進捗表示を非表示
  --use-head      HEADリクエストを使用（従来動作）
  --skip-check    存在確認をスキップ（最速ダウンロード）
  -h, --help      ヘルプを表示

 v1.1.0- の特徴:
  - デフォルトでHEADリクエストをスキップ（大容量ファイル対応）
  - /file/{id} での存在確認（より確実）
  - 存在確認のスキップオプション（最速ダウンロード）
"""

import httpx
import os
import sys
import re
import argparse
import asyncio
import urllib.parse
from pathlib import Path
from tqdm import tqdm


class QDown:
    """
    ID認証付きファイルサーバー用のPythonクライアント（改良版）
    """

    def __init__(self, server_url="https://drive.qualiteg.com", quiet=False,
                 skip_head=True, skip_exists_check=False):
        """
        クライアントの初期化

        Args:
            server_url (str): ファイルサーバーのベースURL
            quiet (bool): 進捗表示を非表示にするかどうか
            skip_head (bool): HEADリクエストをスキップするかどうか（デフォルト: True）
            skip_exists_check (bool): 存在確認をスキップするかどうか（デフォルト: False）
        """
        self.server_url = server_url.rstrip('/')
        self.quiet = quiet
        self.skip_head = skip_head
        self.skip_exists_check = skip_exists_check
        self.timeout = httpx.Timeout(30.0, connect=60.0, read=60.0)

    def check_file_exists_via_page(self, file_id):
        """
        /file/{id} ページで存在確認と基本情報取得

        Args:
            file_id (str): ファイルID

        Returns:
            dict: ファイル情報（存在しない場合はNone）
        """
        url = f"{self.server_url}/file/{file_id}"

        try:
            with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
                response = client.get(url)

                if response.status_code == 404:
                    return None

                if response.status_code == 200:
                    # ファイル名を抽出（オプション）
                    filename_match = re.search(r'<h3 class="mb-0">(.*?)</h3>', response.text)
                    filename = filename_match.group(1) if filename_match else None

                    # ファイルサイズを抽出（オプション）
                    size_match = re.search(r'<i class="fas fa-weight-hanging.*?</i>\s*([\d.]+ [KMGT]?B)', response.text)
                    file_size = size_match.group(1) if size_match else None

                    return {
                        'exists': True,
                        'filename': filename,
                        'file_size_display': file_size
                    }

                # その他のステータスコード
                return {'exists': False, 'status': response.status_code}

        except Exception as e:
            if not self.quiet:
                print(f"警告: 存在確認中にエラーが発生しました: {e}", file=sys.stderr)
            return None

    async def check_file_exists_via_page_async(self, file_id):
        """
        /file/{id} ページで存在確認と基本情報取得（非同期版）
        """
        url = f"{self.server_url}/file/{file_id}"

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.get(url)

                if response.status_code == 404:
                    return None

                if response.status_code == 200:
                    filename_match = re.search(r'<h3 class="mb-0">(.*?)</h3>', response.text)
                    filename = filename_match.group(1) if filename_match else None

                    size_match = re.search(r'<i class="fas fa-weight-hanging.*?</i>\s*([\d.]+ [KMGT]?B)', response.text)
                    file_size = size_match.group(1) if size_match else None

                    return {
                        'exists': True,
                        'filename': filename,
                        'file_size_display': file_size
                    }

                return {'exists': False, 'status': response.status_code}

        except Exception as e:
            if not self.quiet:
                print(f"警告: 存在確認中にエラーが発生しました: {e}", file=sys.stderr)
            return None

    async def download_by_file_id(self, file_id, output=None, output_dir=None):
        """
        ファイルIDを指定してファイルをダウンロード（非同期版）

        Args:
            file_id (str): ダウンロードするファイルのID (qd_id)
            output (str, optional): 出力ファイル名
            output_dir (str, optional): 出力ディレクトリ

        Returns:
            str: ダウンロードしたファイルのパス
        """
        url = f"{self.server_url}/download/{file_id}"
        suggested_filename = None

        # 出力ディレクトリの設定
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = "."

        # 存在確認（スキップ可能）
        if not self.skip_exists_check:
            if not self.quiet:
                print(f"[qdown] ファイル存在確認中: {file_id}")

            file_info = await self.check_file_exists_via_page_async(file_id)

            if file_info is None or not file_info.get('exists', False):
                print(f"エラー: ID '{file_id}' のファイルが見つかりませんでした", file=sys.stderr)
                return None

            suggested_filename = file_info.get('filename')
            if not self.quiet and suggested_filename:
                print(f"[qdown] ファイル検出: {suggested_filename}")
                if file_info.get('file_size_display'):
                    print(f"[qdown] サイズ: {file_info['file_size_display']}")

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # HEADリクエスト（オプション）
                if not self.skip_head:
                    try:
                        head_response = await client.head(url)

                        if head_response.status_code == 404:
                            print(f"エラー: ID '{file_id}' のファイルが見つかりませんでした", file=sys.stderr)
                            return None

                        if head_response.status_code != 200:
                            print(f"エラー: ステータスコード {head_response.status_code}", file=sys.stderr)
                            return None

                        # Content-Dispositionヘッダーからファイル名を取得
                        if "content-disposition" in head_response.headers and not suggested_filename:
                            cd = head_response.headers["content-disposition"]
                            suggested_filename = self._extract_filename_from_header(cd)

                    except httpx.TimeoutException:
                        if not self.quiet:
                            print(f"警告: HEADリクエストがタイムアウトしました。ダウンロードを続行します。", file=sys.stderr)

                # 保存用のファイル名を決定
                if output:
                    output_filename = output
                elif suggested_filename:
                    output_filename = os.path.basename(suggested_filename)
                else:
                    output_filename = f"download_{file_id}"

                file_path = os.path.join(output_dir, output_filename)

                # ストリーミングダウンロード
                async with client.stream("GET", url) as response:
                    if response.status_code == 404:
                        print(f"エラー: ID '{file_id}' のファイルが見つかりませんでした", file=sys.stderr)
                        return None

                    if response.status_code != 200:
                        print(f"エラー: ダウンロード中にエラーが発生しました。ステータスコード: {response.status_code}", file=sys.stderr)
                        return None

                    # Content-Dispositionヘッダーから最終的なファイル名を取得
                    if "content-disposition" in response.headers and not output:
                        cd = response.headers["content-disposition"]
                        extracted_name = self._extract_filename_from_header(cd)
                        if extracted_name:
                            output_filename = os.path.basename(extracted_name)
                            file_path = os.path.join(output_dir, output_filename)

                    # ファイルサイズを取得
                    total_size = int(response.headers.get("content-length", 0))

                    with open(file_path, "wb") as f:
                        if not self.quiet and total_size > 0:
                            progress_bar = tqdm(
                                total=total_size,
                                unit="B",
                                unit_scale=True,
                                desc=f"ダウンロード中: {output_filename}"
                            )

                        downloaded = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            f.write(chunk)
                            if not self.quiet and total_size > 0:
                                downloaded += len(chunk)
                                progress_bar.update(len(chunk))

                        if not self.quiet and total_size > 0:
                            progress_bar.close()

                if not self.quiet:
                    print(f"[qdown] ファイルを保存しました: {file_path}")
                return file_path

            except httpx.RequestError as e:
                print(f"エラー: リクエストに失敗しました - {e}", file=sys.stderr)
                return None
            except Exception as e:
                print(f"エラー: {e}", file=sys.stderr)
                return None

    def download_by_file_id_sync(self, file_id, output=None, output_dir=None):
        """
        ファイルIDを指定してファイルをダウンロード（同期版）

        Args:
            file_id (str): ダウンロードするファイルのID (qd_id)
            output (str, optional): 出力ファイル名
            output_dir (str, optional): 出力ディレクトリ

        Returns:
            str: ダウンロードしたファイルのパス
        """
        url = f"{self.server_url}/download/{file_id}"
        suggested_filename = None

        # 出力ディレクトリの設定
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        else:
            output_dir = "."

        # 存在確認（スキップ可能）
        if not self.skip_exists_check:
            if not self.quiet:
                print(f"[qdown] ファイル存在確認中: {file_id}")

            file_info = self.check_file_exists_via_page(file_id)

            if file_info is None or not file_info.get('exists', False):
                print(f"エラー: ID '{file_id}' のファイルが見つかりませんでした", file=sys.stderr)
                return None

            suggested_filename = file_info.get('filename')
            if not self.quiet and suggested_filename:
                print(f"[qdown] ファイル検出: {suggested_filename}")
                if file_info.get('file_size_display'):
                    print(f"[qdown] サイズ: {file_info['file_size_display']}")

        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            try:
                # HEADリクエスト（オプション）
                if not self.skip_head:
                    try:
                        head_response = client.head(url)

                        if head_response.status_code == 404:
                            print(f"エラー: ID '{file_id}' のファイルが見つかりませんでした", file=sys.stderr)
                            return None

                        if head_response.status_code != 200:
                            print(f"エラー: ステータスコード {head_response.status_code}", file=sys.stderr)
                            return None

                        # Content-Dispositionヘッダーからファイル名を取得
                        if "content-disposition" in head_response.headers and not suggested_filename:
                            cd = head_response.headers["content-disposition"]
                            suggested_filename = self._extract_filename_from_header(cd)

                    except httpx.TimeoutException:
                        if not self.quiet:
                            print(f"警告: HEADリクエストがタイムアウトしました。ダウンロードを続行します。", file=sys.stderr)

                # 保存用のファイル名を決定
                if output:
                    output_filename = output
                elif suggested_filename:
                    output_filename = os.path.basename(suggested_filename)
                else:
                    output_filename = f"download_{file_id}"

                file_path = os.path.join(output_dir, output_filename)

                # ストリーミングダウンロード
                with client.stream("GET", url) as response:
                    if response.status_code == 404:
                        print(f"エラー: ID '{file_id}' のファイルが見つかりませんでした", file=sys.stderr)
                        return None

                    if response.status_code != 200:
                        print(f"エラー: ダウンロード中にエラーが発生しました。ステータスコード: {response.status_code}", file=sys.stderr)
                        return None

                    # Content-Dispositionヘッダーから最終的なファイル名を取得
                    if "content-disposition" in response.headers and not output:
                        cd = response.headers["content-disposition"]
                        extracted_name = self._extract_filename_from_header(cd)
                        if extracted_name:
                            output_filename = os.path.basename(extracted_name)
                            file_path = os.path.join(output_dir, output_filename)

                    # ファイルサイズを取得
                    total_size = int(response.headers.get("content-length", 0))

                    with open(file_path, "wb") as f:
                        if not self.quiet and total_size > 0:
                            progress_bar = tqdm(
                                total=total_size,
                                unit="B",
                                unit_scale=True,
                                desc=f"ダウンロード中: {output_filename}"
                            )

                        downloaded = 0
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
                            if not self.quiet and total_size > 0:
                                downloaded += len(chunk)
                                progress_bar.update(len(chunk))

                        if not self.quiet and total_size > 0:
                            progress_bar.close()

                if not self.quiet:
                    print(f"[qdown] ファイルを保存しました: {file_path}")
                return file_path

            except httpx.RequestError as e:
                print(f"エラー: リクエストに失敗しました - {e}", file=sys.stderr)
                if "Name or service not known" in str(e):
                    print("WSLで実行しているとき、このDNSエラーに遭遇した場合は以下をお試しください")
                    print("If you are running this in WSL, please try setting up DNS as follows:", file=sys.stderr)
                    print("STEP 1: Disable the automatic DNS configuration in WSL2", file=sys.stderr)
                    print("In WSL bash, run the following to prevent automatic generation of resolv.conf:", file=sys.stderr)
                    print('sudo sh -c \'cat > /etc/wsl.conf << EOF', file=sys.stderr)
                    print('[user]', file=sys.stderr)
                    print('default=mlu', file=sys.stderr)
                    print('[network]', file=sys.stderr)
                    print('generateResolvConf = false', file=sys.stderr)
                    print('EOF\'', file=sys.stderr)
                    print("STEP 2: Restart WSL from Windows", file=sys.stderr)
                    print('wsl --shutdown', file=sys.stderr)
                    print("STEP 3: After restarting WSL, run the following in the shell:", file=sys.stderr)
                    print('sudo sh -c \'cat > /etc/resolv.conf << EOF', file=sys.stderr)
                    print('nameserver 8.8.8.8', file=sys.stderr)
                    print('nameserver 8.8.4.4', file=sys.stderr)
                    print('EOF\'', file=sys.stderr)
                return None
            except Exception as e:
                print(f"エラー: {e}", file=sys.stderr)
                return None

    def _extract_filename_from_header(self, content_disposition):
        """
        Content-Dispositionヘッダーからファイル名を抽出

        Args:
            content_disposition (str): Content-Dispositionヘッダーの値

        Returns:
            str: 抽出されたファイル名（抽出できない場合はNone）
        """
        if not content_disposition or "filename=" not in content_disposition:
            return None

        try:
            # filename*=UTF-8''形式のエンコードがある場合
            if "filename*=UTF-8''" in content_disposition:
                encoded_part = content_disposition.split("filename*=UTF-8''")[1]
                # セミコロンやダブルクォートがあれば処理
                if '"' in encoded_part:
                    encoded_part = encoded_part.split('"')[0]
                if ';' in encoded_part:
                    encoded_part = encoded_part.split(';')[0]
                # URLデコードして正しいファイル名を取得
                return urllib.parse.unquote(encoded_part)
            else:
                # 通常のファイル名
                filename_part = content_disposition.split("filename=")[1].strip('"')
                return filename_part.replace('"', '').split(';')[0]
        except Exception:
            return None


def main():
    parser = argparse.ArgumentParser(
        description="qdown - IDベースファイルダウンロードツール",
        add_help=False
    )

    parser.add_argument("id", nargs="?", help="ダウンロードするファイルのID")
    parser.add_argument("-O", dest="output", help="出力ファイル名")
    parser.add_argument("-o", dest="output_dir", help="出力ディレクトリ")
    parser.add_argument("-s", dest="server", default="https://drive.qualiteg.com", help="サーバーURL")
    parser.add_argument("-q", "--quiet", action="store_true", help="進捗表示を非表示")
    parser.add_argument("--use-head", action="store_true", help="HEADリクエストを使用（従来動作）")
    parser.add_argument("--skip-check", action="store_true", help="存在確認をスキップ（最速ダウンロード）")
    parser.add_argument("-h", "--help", action="store_true", help="ヘルプを表示")

    args = parser.parse_args()

    if args.help or not args.id:
        print(__doc__)
        sys.exit(0)

    # skip_headのデフォルトはTrue（HEADリクエストをスキップ）
    # --use-headが指定された場合のみFalse（HEADリクエストを使用）
    skip_head = not args.use_head

    client = QDown(
        server_url=args.server,
        quiet=args.quiet,
        skip_head=skip_head,
        skip_exists_check=args.skip_check
    )

    result = asyncio.run(client.download_by_file_id(
        file_id=args.id,
        output=args.output,
        output_dir=args.output_dir
    ))

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()