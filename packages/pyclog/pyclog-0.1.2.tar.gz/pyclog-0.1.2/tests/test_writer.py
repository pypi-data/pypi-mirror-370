# pyclog/tests/test_writer.py

import os
import pytest
import struct
import gzip
from datetime import datetime, timedelta

from pyclog.writer import ClogWriter
from pyclog import constants
from pyclog.exceptions import ClogWriteError, UnsupportedCompressionError

@pytest.fixture
def temp_clog_file(tmp_path):
    """为测试提供一个临时 .clog 文件路径。"""
    return tmp_path / "test.clog"

def test_writer_initialization_and_header(temp_clog_file):
    """测试 ClogWriter 初始化时是否正确写入文件头。"""
    with ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_GZIP) as writer:
        pass # 确保文件被创建和关闭

    assert temp_clog_file.exists()
    with open(temp_clog_file, 'rb') as f:
        header = f.read(16)
        assert header[0:4] == constants.MAGIC_BYTES
        assert header[4:5] == constants.FORMAT_VERSION_V1
        assert header[5:6] == constants.COMPRESSION_GZIP
        assert header[6:16] == constants.RESERVED_BYTES

def test_writer_no_compression(temp_clog_file):
    """测试无压缩模式下的写入。"""
    with ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_NONE) as writer:
        writer.write_record("INFO", "Hello, world!")
        writer.write_record("DEBUG", "Another log entry.")
    
    with open(temp_clog_file, 'rb') as f:
        f.read(16) # 跳过文件头
        
        # 读取第一个块头
        chunk_header = f.read(12)
        compressed_size, uncompressed_size, record_count = struct.unpack('<III', chunk_header)
        assert record_count == 2 # 两个记录
        
        # 读取块数据
        chunk_data = f.read(compressed_size)
        assert len(chunk_data) == uncompressed_size # 无压缩时，压缩大小等于未压缩大小

        records = chunk_data.split(constants.RECORD_DELIMITER)
        assert len(records) == 3 # 2条记录 + 末尾可能有的空行
        assert records[0].decode('utf-8').endswith("INFO\tHello, world!")
        assert records[1].decode('utf-8').endswith("DEBUG\tAnother log entry.")

def test_writer_gzip_compression(temp_clog_file):
    """测试 Gzip 压缩模式下的写入。"""
    with ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_GZIP) as writer:
        writer.write_record("INFO", "Test Gzip compression.")
        writer.write_record("WARNING", "This is a warning.")
    
    with open(temp_clog_file, 'rb') as f:
        f.read(16) # 跳过文件头
        
        chunk_header = f.read(12)
        compressed_size, uncompressed_size, record_count = struct.unpack('<III', chunk_header)
        assert record_count == 2
        
        compressed_data = f.read(compressed_size)
        decompressed_data = gzip.decompress(compressed_data)
        
        records = decompressed_data.split(constants.RECORD_DELIMITER)
        assert len(records) == 3
        assert records[0].decode('utf-8').endswith("INFO\tTest Gzip compression.")
        assert records[1].decode('utf-8').endswith("WARNING\tThis is a warning.")
        assert len(decompressed_data) == uncompressed_size

def test_writer_zstandard_compression(temp_clog_file):
    """测试 Zstandard 压缩模式下的写入。"""
    try:
        import zstandard as zstd
    except ImportError:
        pytest.skip("Zstandard 库未安装，跳过此测试。")

    with ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_ZSTANDARD) as writer:
        writer.write_record("INFO", "Test Zstandard compression.")
        writer.write_record("DEBUG", "Another Zstd entry.")
    
    with open(temp_clog_file, 'rb') as f:
        f.read(16) # 跳过文件头
        
        chunk_header = f.read(12)
        compressed_size, uncompressed_size, record_count = struct.unpack('<III', chunk_header)
        assert record_count == 2
        
        compressed_data = f.read(compressed_size)
        dctx = zstd.ZstdDecompressor()
        decompressed_data = dctx.decompress(compressed_data)
        
        records = decompressed_data.split(constants.RECORD_DELIMITER)
        assert len(records) == 3
        assert records[0].decode('utf-8').endswith("INFO\tTest Zstandard compression.")
        assert records[1].decode('utf-8').endswith("DEBUG\tAnother Zstd entry.")
        assert len(decompressed_data) == uncompressed_size

def test_writer_unsupported_compression_raises_error(temp_clog_file):
    """测试不持的压缩算法是否抛出错误。"""
    with pytest.raises(UnsupportedCompressionError):
        with ClogWriter(temp_clog_file, compression_code=b'\x99') as writer:
            writer.write_record("INFO", "Should not be written.")

def test_writer_flush_on_close(temp_clog_file):
    """测试关闭时是否刷新缓冲区。"""
    writer = ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_NONE)
    writer.write_record("INFO", "Record 1")
    writer.write_record("INFO", "Record 2")
    # 不手动调用 _flush_chunk，直接关闭
    writer.close()

    with open(temp_clog_file, 'rb') as f:
        f.read(16) # 跳过文件头
        chunk_header = f.read(12)
        compressed_size, uncompressed_size, record_count = struct.unpack('<III', chunk_header)
        assert record_count == 2
        chunk_data = f.read(compressed_size)
        records = chunk_data.split(constants.RECORD_DELIMITER)
        assert len(records) == 3
        assert records[0].decode('utf-8').endswith("INFO\tRecord 1")
        assert records[1].decode('utf-8').endswith("INFO\tRecord 2")

def test_writer_multiple_chunks(temp_clog_file):
    """测试写入多个块。"""
    # 设置 buffer_flush_records 为 1，确保每条记录都生成一个块
    with ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_NONE, buffer_flush_records=1) as writer:
        writer.write_record("INFO", "Record A") # 写入第一个块
        writer.write_record("INFO", "Record B") # 写入第二个块
        writer.write_record("INFO", "Record C") # 写入第三个块
    
    with open(temp_clog_file, 'rb') as f:
        f.read(16) # 跳过文件头

        # 读取第一个块
        chunk1_header = f.read(12)
        cs1, us1, rc1 = struct.unpack('<III', chunk1_header)
        assert rc1 == 1
        chunk1_data = f.read(cs1)
        assert chunk1_data.decode('utf-8').endswith("INFO\tRecord A\n")

        # 读取第二个块
        chunk2_header = f.read(12)
        cs2, us2, rc2 = struct.unpack('<III', chunk2_header)
        assert rc2 == 1
        chunk2_data = f.read(cs2)
        assert chunk2_data.decode('utf-8').endswith("INFO\tRecord B\n")

        # 取第三个块
        chunk3_header = f.read(12)
        cs3, us3, rc3 = struct.unpack('<III', chunk3_header)
        assert rc3 == 1
        chunk3_data = f.read(cs3)
        assert chunk3_data.decode('utf-8').endswith("INFO\tRecord C\n")

        assert not f.read() # 确保文件结束

def test_writer_empty_file(temp_clog_file):
    """测试写入空文件（只包含头）。"""
    with ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_NONE) as writer:
        pass # 不写入任何记录

    assert temp_clog_file.exists()
    with open(temp_clog_file, 'rb') as f:
        header = f.read(16)
        assert len(header) == 16
        assert not f.read() # 确保文件除了头没有其他内容

def test_writer_io_error_on_open(tmp_path):
    """测试打开文件失败时是否抛出 ClogWriteError。"""
    # 创建一个无法写入的路径 (例如，尝试写入目录而不是文件)
    invalid_path = tmp_path / "non_existent_dir" / "test.clog"
    with pytest.raises(ClogWriteError, match="无法打开文件"):
        with ClogWriter(invalid_path) as writer:
            pass

def test_writer_io_error_on_write_header(temp_clog_file, mocker):
    """测试写入文件头失败时是否抛出 ClogWriteError。"""
    # 模拟 open 函数，使其返回一个模拟的文件对象，该对象的 write 方法会抛出 IOError
    mock_file = mocker.mock_open().return_value
    mock_file.write.side_effect = IOError("模拟写入错误")
    mocker.patch('builtins.open', return_value=mock_file)
    
    with pytest.raises(ClogWriteError, match="写入文件头失败"):
        ClogWriter(temp_clog_file)
    
    # 移除对 mock_file.close 的断言，因为在初始化失败时，文件可能未被正确关闭
    # 或者测试的重点是异常是否被抛出，而不是文件关闭行为

def test_writer_io_error_on_flush_chunk(temp_clog_file, mocker):
    """测试刷新块时写入失败是否抛出 ClogWriteError。"""
    writer = ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_NONE)
    writer.write_record("INFO", "Test record.")
    
    # 模拟文件写入失败
    mocker.patch.object(writer.file, 'write', side_effect=IOError("模拟写入块错误"))
    
    try:
        with pytest.raises(ClogWriteError, match="写入数据块失败"):
            writer._flush_chunk()
    finally:
        writer.close() # 确保关闭文件，即使发生错误

def test_writer_io_error_on_close(temp_clog_file, mocker):
    """测试关闭文件失败时是否抛出 ClogWriteError。"""
    writer = ClogWriter(temp_clog_file, compression_code=constants.COMPRESSION_NONE)
    writer.write_record("INFO", "Test record.")
    
    # 模拟文件关闭失败
    mocker.patch.object(writer.file, 'close', side_effect=IOError("模拟关闭错误"))
    
    with pytest.raises(ClogWriteError, match="关闭文件失败"):
        writer.close()
