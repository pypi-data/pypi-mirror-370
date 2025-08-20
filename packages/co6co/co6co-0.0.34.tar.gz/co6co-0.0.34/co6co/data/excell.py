

from ..utils import log
from io import BytesIO
from typing import TypedDict
from abc import ABC, abstractmethod
from typing import Literal
try:
    import pandas as pd
    pandas_flag = True
except Exception as e:
    pandas_flag = False


class AbsImport(ABC):
    """
    导入excel
    """

    def __init__(self,   sheet_name=None, templateFileName='template.xlsx'):
        self.sheet_name = sheet_name
        self.templateFileName = templateFileName

    @abstractmethod
    def columns(self):
        columns = ["id", "name", "code", "createTime"]
        return columns

    @abstractmethod
    async def handler(self, *, rawData: list[list | dict], item: list[list | dict], **kwargs):
        """
        处理数据
        return: 1: 插入 2: 更新 -1: 错误,0:忽略
        """
        print(item)
        return -1

    @abstractmethod
    async def handlerFinshed(self, **kwargs):
        """
        处理完成
        """
        print("处理完成")
        pass

    @abstractmethod
    async def handlerBefore(self, item, **kwargs):
        """
        处理完成
        """
        # nan!=nan
        item = ['' if x != x else x for x in item]
        return item

    @abstractmethod
    async def handlerError(self, **kwargs):
        """
        处理错误
        """
        print("处理错误")
        pass

    def template(self):
        # 假设模板文件名为 template.xlsx，放在当前目录下
        columns = self. columns()
        df = pd.DataFrame(columns=columns)
        # 设置适应内容宽度
        pd.set_option('display.max_colwidth', None)
        output = BytesIO()
        # 将 DataFrame 写入二进制流，这里以 Excel 格式为例
        df.to_excel(output, index=False, sheet_name=self.sheet_name)
        # 移动到流的起始位置
        output.seek(0)
        # 获取二进制数据
        binary_data = output.read()
        return binary_data

    @property
    def template_length(self):
        """
        获取文件头信息 
        文件大小
        """
        binary_data = self.template()
        return len(binary_data)

    async def _handlerData(self, rawData: list[list | dict], data: list[list | dict], **kwargs):
        """
        导入数据
        """
        uploadNum = 0
        insertNum = 0
        errorNum = 0
        msg = ""
        if data:
            try:
                for item in data:
                    # nan!=nan
                    item = await self.handlerBefore(item=item, **kwargs)
                    result = await self.handler(rawData=rawData, item=item, **kwargs)
                    if result == 1:
                        insertNum += 1
                    elif result == 2:
                        uploadNum += 1
                    elif result == -1 or result == 0:
                        errorNum += 1
                await self.handlerFinshed(**kwargs)
            except Exception as e:
                msg = str(e)
                log.err(f"导入数据出现错误，{e}")
                await self.handlerError(**kwargs)
        return insertNum, uploadNum, errorNum, msg

    def fileCheck(self, file: str):
        """
        检查文件是否为 Excel 格式
        @param file "xxxx.xlsx[xls]
        """
        if not file.endswith(('.xlsx', '.xls')):
            return False
        return True

    async def importData(self, data: any, orient: Literal['dict', 'list', "series", 'index', 'records', 'split'] = 'dict', **kwargs):
        """
        @param data: 二进制流
        @param orient: 数据格式[dict,list,index,series,records,split]
        @return: 插入数量,上传数量,错误数量,错误信息
        """
        try:
            # 读取 Excel 文件
            df = pd.read_excel(data, sheet_name=self.sheet_name)
            # 这里可以对数据进行进一步处理
            result = df.to_dict(orient=orient)  # index,columns,data
            itemList = []
            if orient == "index" or orient == "list":
                itemList = [v for _, v in result.items()]
            elif orient == "dict":
                itemList = [v for _, v in result.items()]
            elif orient == "records":
                itemList = [v for v in result]
            elif orient == "split":
                itemList = [v for v in result.get("data")]

            elif orient == "series":
                itemList = [result[v] for v, in result]
            insertNum, updateNum, errorNUm, msg = await self._handlerData(rawData=result, data=itemList, **kwargs)
            return insertNum, updateNum, errorNUm, msg

        except Exception as e:
            raise e
