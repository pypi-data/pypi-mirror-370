#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zipfile
import json
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from aiohttp import ClientSession, ClientTimeout, FormData, ClientConnectorError, ClientError
from tqdm import tqdm

from .logger import logger


SDP = 'driver.py'
SDX = 'driver.xml'


class DriverUpdater():
    def __init__(self, path: str, host: str, username: str, password: str, ignore: list = []):
        self.host     = host
        self.url      = f'http://{host}/interface/db/selector'
        self.username = username
        self.password = password
        self.ignore   = ignore

        self.token              = None
        self.encoding           = 'utf-8'
        self.work_path          = Path(path)
        self.temp_path          = self.work_path / '.temp'
        self.record_file        = self.temp_path / '.record'
        self.record             = {host: {}}
        self.tq                 = None
        self.suc_list           = []
        self.fail_list          = []
        self.fail_msg_list      = []

    def __repr__(self):
        return f"DriverUpdater({self.host})"

    def __get_hash(self, path: Path) -> int:
        return hashlib.md5(path.read_bytes().strip()).hexdigest()

    def load_record(self):
        if not self.temp_path.exists():
            self.temp_path.mkdir()

        try:
            self.record = json.loads(self.record_file.read_text(encoding=self.encoding))
        except:
            self.record = {}
            logger.warning(f'更新记录读取失败, 使用默认值。')

    def dump_record(self):
        self.record_file.write_text(
            json.dumps(self.record, ensure_ascii=False),
            encoding=self.encoding,
        )

    def get_update_list(self) -> list[tuple[Path, dict]]:
        last_host = self.record.get('last_host')
        list = []

        for item in self.work_path.iterdir():
            if item.name in self.ignore:
                logger.debug(f'路径 "{item}" 在忽略列表中, 已忽略')
                continue

            if not item.is_dir():
                logger.debug(f'路径 "{item}" 不是目录, 已忽略')
                continue

            if not (driver_py := item / SDP).exists():
                logger.debug(f'路径 "{item}" 中没有 "driver.py" 文件, 已忽略')
                continue

            if not (driver_xml := item / SDX).exists():
                logger.debug(f'路径 "{item}" 中没有 "driver.xml" 文件, 已忽略')
                continue

            hash = self.record.get(self.host, {}).get(item.name, {})
            driver_py_hash = self.__get_hash(driver_py)
            driver_xml_hash = self.__get_hash(driver_xml)

            if hash.get(SDP) == driver_py_hash and hash.get(SDX) == driver_xml_hash:
                logger.debug(f'路径 "{item}" 未更改, 已忽略')
                continue

            upload_only = False

            # 若没有更新记录，仅上传
            if not hash:
                upload_only = True

            # 更换主机，且 hash 与原主机 hash 一致，仅上传
            if last_host != self.host:
                last_hash = self.record.get(last_host, {}).get(item.name, {})

                if last_hash.get(SDP) == driver_py_hash and last_hash.get(SDX) == driver_xml_hash:
                    upload_only = True

            list.append((item, {
                'upload_only': upload_only,
                SDP: driver_py_hash,
                SDX: driver_xml_hash,
            }))

        return list

    async def login(self):
        async with ClientSession(timeout=ClientTimeout(total=3)) as session:
            async with session.post(self.url, json={
                "project": "items",
                "type": "im-function",
                "id": "login",
                "param": {
                    "data": {
                        "username": self.username,
                        "password": self.password,
                    },
                },
            }) as response:
                if response.status == 200:
                    self.token = (await response.json()).get('data', {}).get('token')
                else:
                    logger.error(f'登录失败，状态码：{response.status}')

    async def _upload_file(self, path: Path, new_hash: dict) -> bool:
        zip_file = self.temp_path / f'{path.name}.gms'

        if not new_hash.get('upload_only'):
            # 增加驱动版本
            try:
                xml = (path / SDX).read_text(encoding=self.encoding)
                dom = minidom.parseString(xml)
                version_dom = dom.getElementsByTagName('version')[0].firstChild
                version = int(version_dom.data) + 1
                version_dom.data = version

                properties = dom.getElementsByTagName('property')
                for p in properties:
                    name = p.getElementsByTagName('name')[0].firstChild.data
                    if isinstance(name, str):
                        name = name.lower()
                    if name == '驱动版本' or name == 'version':
                        p.getElementsByTagName('default')[0].firstChild.data = version
                        break
                dom = dom.toxml().replace('<?xml version="1.0" ?>', '')
            except (ExpatError, IndexError) as e:
                self.fail_list.append(path.name)
                self.fail_msg_list.append((path.name, f'更新驱动程序版本失败，请检查 \'{path.name}/driver.xml\' 文件格式是否正确, 错误信息：\'{e}\''))
                return False
            except FileNotFoundError:
                self.fail_list.append(path.name)
                self.fail_msg_list.append((path.name, f'更新驱动程序版本失败，请检查 \'{path.name}/driver.xml\' 文件是否存在'))
                return False

        # 构建 zip 文件
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(str(path / SDP), SDP)
            if not new_hash.get('upload_only'):
                zf.writestr(SDX, dom)
            else:
                zf.write(str(path / SDX), SDX)

        # 上传 zip 文件
        with open(zip_file, 'rb') as f:
            data = FormData(quote_fields=False, charset=self.encoding)
            data.add_field('param', '{"project":"items","type":"im-function","id":"upload_driver","param":{}}', content_type='application/json')
            data.add_field('file', f, filename=f'{path.name}.gms', content_type='application/zip')

            headers = {'Authorization': f'Basic {self.token}',}

            async with ClientSession() as session:
                async with session.post(self.url, data=data, headers=headers, timeout=None) as response:
                    result = await response.json()

                    if result.get('code') == 200:
                        self.suc_list.append(path.name)
                        if not new_hash.get('upload_only'):
                            # 写入新版本号
                            with open(path / SDX, 'w', encoding=self.encoding) as f:
                                f.write(dom)
                            # 更新记录
                            new_hash[SDX] = self.__get_hash(path / SDX)
                        return True
                    else:
                        self.fail_list.append(path.name)
                        self.fail_msg_list.append((path.name, result.get('message', '')))
                        return False

    async def upload_file(self, path: Path, new_hash: dict):
        if await self._upload_file(path, new_hash):
            new_hash.pop('upload_only', None)
            self.record.setdefault(self.host, {})[path.name] = new_hash
        self.tq.update(1)

    async def update_async(self):
        self.load_record()

        list = self.get_update_list()
        if not list:
            logger.info('没有需要更新的驱动程序')
            return

        await self.login()
        if not self.token:
            return

        tasks = [asyncio.ensure_future(self.upload_file(*item)) for item in list]

        self.tq = tqdm(total=len(tasks), desc=f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]}] 上传进度')
        await asyncio.gather(*tasks)
        self.tq.close()

        logger.info(f'更新完成, 成功：{len(self.suc_list)}, 失败：{len(self.fail_list)}, 忽略: {len(self.ignore or [])}')
        for name, message in self.fail_msg_list:
            self.record.setdefault(self.host, {}).pop(name, None)
            logger.warning(f'更新 "{name}" 失败, 原因: "{message}"')

        self.record['last_host'] = self.host

        self.dump_record()

    def update(self):
        try:
            asyncio.get_event_loop().run_until_complete(self.update_async())
        except asyncio.TimeoutError:
            logger.error(f'连接 {self.host} 超时')
        except ClientConnectorError:
            logger.error(f'连接 {self.host} 失败')
        except ClientError as e:
            logger.error(f'请求失败，错误信息：{e}')
