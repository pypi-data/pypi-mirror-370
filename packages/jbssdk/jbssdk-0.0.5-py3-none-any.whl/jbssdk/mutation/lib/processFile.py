import hashlib
import json
import math
from datetime import datetime


def getfileListUploadPostJson(mergeData, nickName, userId):
    try:
        fileInfo = json.loads(mergeData['fileInfo'])
        file = {
            "searchValue": None,
            "id": "",
            "createBy": None,
            "createTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updateBy": {
                "nickName": nickName,
                "id": userId
            },
            "updateTime": None,
            "remark": None,
            "dataScope": None,
            "beginTime": None,
            "endTime": None,
            "advancedQuery": None,
            "searchId": None,
            "orgSchema": None,
            "pageNum": None,
            "pageSize": None,
            "orderByColumn": None,
            "isAsc": None,
            "params": {},
            "delFlag": "0",
            "isNewRecord": None,
            "numbering": None,
            "name": mergeData['fileName'],
            "realName": fileInfo['realName'],
            "dataId": None,
            "businessId": None,
            "dataType": "deal_base",
            "directoryId": "9702b56404494bb0973e9aa871eb3f7d",
            "directoryName": "商业计划书(BP)",
            "url": fileInfo['url'],
            "suffix": fileInfo['suffix'],
            "sizes": fileInfo['sizes'],
            "discussId": None,
            "remindUsers": None,
            "fileTag": None,
            "fileSort": 1,
            "rowSort": None,
            "hideStatus": None,
            "slotData": [],
            "nickName": None,
            "icon": None,
            "fileType": None,
            "isBuiltIn": None,
            "fileLibraryRole": None,
            "isCollection": None,
            "level": None,
            "sort": None,
            "fileList": None,
            "parentId": None,
            "belong": None,
            "businessName": None,
            "businessTye": None,
            "localhostPath": None,
            "onlineEditType": None,
            "directoryListId": [],
            "userId": None,
            "rolesId": None,
            "tempSource": None,
            "fileDataRoomPermission": None,
            "fileName": None,
            "fileId": None,
            "checkRequired": "false",
            "dataIdList": None,
            "dealIdList": None,
            "dealBatchId": None,
            "lpIdList": None,
            "dataRoomLpName": None,
            "dataRoomNotName": None,
            "relativePath": None,
            "folderBusinessId": None,
            "fileIdTemp": mergeData['fileId'],
            "path": "null/null",
            "md5": fileInfo['mD5'],
            "orderBySql": ""
        }
        return [file]
    except Exception as e:
        print(e)
        return None

def get_binary_md5(binary_data):
    """计算二进制数据的 MD5 值"""
    md5_hash = hashlib.md5()
    md5_hash.update(binary_data)
    return md5_hash.hexdigest()


async def calculate_filename_md5(filename):
    """
    计算文件名的 MD5 值
    Args:
        filename (str): 文件名字符串
    Returns:
        str: 文件名的 MD5 哈希值（32个字符的十六进制字符串）
    """
    md5_hash = hashlib.md5()
    md5_hash.update(filename.encode("utf-8"))  # 将文件名编码为 UTF-8 字节
    return md5_hash.hexdigest()


async def chunk_binary_file(binary_data, filename, chunk_size=2048000):
    """
    分块二进制文件数据，并生成相关信息 (异步实现)
    Args:
        binary_data: 文件的二进制数据
        filename: 文件名字
        chunk_size: 每一块的大小（默认：2048000 字节）

    Yields:
        分块信息的字典，包括块号、大小、文件名等
    """
    total_size = len(binary_data)  # 二进制文件的总大小
    file_md5 = get_binary_md5(binary_data)  # 整体文件的 MD5
    total_chunks = math.ceil(total_size / chunk_size)  # 总块数

    for chunk_number in range(total_chunks):
        # 获取当前分块的起始与结束
        start = chunk_number * chunk_size
        end = min(start + chunk_size, total_size)

        # 当前分块数据
        chunk_data = binary_data[start:end]
        current_chunk_size = len(chunk_data)
        filename_md5 = await calculate_filename_md5(filename)

        identifier = f"{file_md5}_{filename_md5}"  # 生成唯一标识符

        # 生成当前块信息
        chunk_info = {
            "chunkNumber": chunk_number + 1,
            "chunkSize": chunk_size,
            "currentChunkSize": current_chunk_size,
            "totalSize": total_size,
            "identifier": identifier,
            "filename": filename,
            "relativePath": filename,  # 默认文件名作为根路径
            "totalChunks": total_chunks,
            "file": chunk_data,  # 当前分块的二进制数据
        }

        yield chunk_info  # 异步生成当前分块信息


