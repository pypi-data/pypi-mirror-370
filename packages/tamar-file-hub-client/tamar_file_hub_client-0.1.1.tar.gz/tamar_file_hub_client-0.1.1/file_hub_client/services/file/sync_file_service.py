"""
同步文件服务
"""
import grpc
from typing import Optional, Dict, List, Any

from .base_file_service import BaseFileService
from ...rpc.sync_client import SyncGrpcClient
from ...schemas import (
    File,
    FileListResponse,
    GetFileResponse,
)
from ...errors import FileNotFoundError


class SyncFileService(BaseFileService):
    """同步文件服务"""

    def __init__(self, client: SyncGrpcClient):
        """
        初始化文件服务
        
        Args:
            client: 同步gRPC客户端
        """
        self.client = client

    def generate_share_link(
            self,
            file_id: str,
            *,
            is_public: bool = True,
            access_scope: str = "view",
            expire_seconds: int = 86400,
            max_access: Optional[int] = None,
            share_password: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> str:
        """
        生成分享链接
        
        Args:
            file_id: 文件ID
            is_public: 是否公开
            access_scope: 访问范围
            expire_seconds: 过期时间（秒）
            max_access: 最大访问次数
            share_password: 访问密码
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
            
        Returns:
            分享ID
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.ShareLinkRequest(
            file_id=file_id,
            is_public=is_public,
            access_scope=access_scope,
            expire_seconds=expire_seconds
        )

        if max_access is not None:
            request.max_access = max_access
        if share_password:
            request.share_password = share_password

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.GenerateShareLink(request, metadata=grpc_metadata)

        return response.file_share_id

    def visit_file(
            self,
            file_share_id: str,
            access_type: str = "view",
            access_duration: int = 0,
            metadata: Optional[Dict[str, Any]] = None,
            request_id: Optional[str] = None,
            **extra_metadata
    ) -> None:
        """
        访问文件（通过分享链接）
        
        Args:
            file_share_id: 分享ID
            access_type: 访问类型
            access_duration: 访问时长
            metadata: 元数据
            **extra_metadata: 额外的元数据（如 x-org-id, x-user-id 等）
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        from google.protobuf import struct_pb2

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        # 转换metadata为Struct
        struct_metadata = struct_pb2.Struct()
        if metadata:
            for key, value in metadata.items():
                struct_metadata[key] = value

        request = file_service_pb2.FileVisitRequest(
            file_share_id=file_share_id,
            access_type=access_type,
            access_duration=access_duration,
            metadata=struct_metadata
        )

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **extra_metadata)

        stub.VisitFile(request, metadata=grpc_metadata)

    def get_file(self, file_id: str, request_id: Optional[str] = None,
                 **metadata) -> GetFileResponse:
        """
        获取文件信息
        
        Args:
            file_id: 文件ID
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
            
        Returns:
            文件信息响应，包含文件信息和上传文件信息
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        from ...schemas.file import GetFileResponse

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.GetFileRequest(file_id=file_id)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        try:
            response = stub.GetFile(request, metadata=grpc_metadata)
            
            # 转换文件信息
            file_info = self._convert_file_info(response.file)
            
            # 转换上传文件信息（如果存在）
            upload_file_info = None
            if response.HasField('upload_file'):
                upload_file_info = self._convert_upload_file_info(response.upload_file)
            
            return GetFileResponse(file=file_info, upload_file=upload_file_info)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise FileNotFoundError(file_id)
            raise

    def rename_file(self, file_id: str, new_name: str, request_id: Optional[str] = None,
                    **metadata) -> File:
        """
        重命名文件
        
        Args:
            file_id: 文件ID
            new_name: 新文件名
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
            
        Returns:
            更新后的文件信息
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.RenameFileRequest(
            file_id=file_id,
            new_name=new_name
        )

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        try:
            response = stub.RenameFile(request, metadata=grpc_metadata)
            return self._convert_file_info(response)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise FileNotFoundError(file_id)
            raise

    def delete_file(self, file_id: str, request_id: Optional[str] = None,
                    **metadata) -> None:
        """
        删除文件
        
        Args:
            file_id: 文件ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.DeleteFileRequest(file_id=file_id)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        try:
            stub.DeleteFile(request, metadata=grpc_metadata)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise FileNotFoundError(file_id)
            raise

    def list_files(
            self,
            folder_id: Optional[str] = None,
            file_name: Optional[str] = None,
            file_type: Optional[List[str]] = None,
            created_by_role: Optional[str] = None,
            created_by: Optional[str] = None,
            page_size: int = 20,
            page: int = 1,
            request_id: Optional[str] = None,
            **metadata
    ) -> FileListResponse:
        """
        列出文件
        
        Args:
            folder_id: 文件夹ID
            file_name: 文件名过滤
            file_type: 文件类型过滤
            created_by_role: 创建者角色过滤
            created_by: 创建者过滤
            page_size: 每页大小
            page: 页码
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
            
        Returns:
            文件列表响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.ListFilesRequest(
            folder_id=folder_id,
            page_size=page_size,
            page=page
        )

        if file_name:
            request.file_name = file_name
        if file_type:
            request.file_type.extend(file_type)
        if created_by_role:
            request.created_by_role = created_by_role
        if created_by:
            request.created_by = created_by

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.ListFiles(request, metadata=grpc_metadata)

        files = [self._convert_file_info(f) for f in response.files]

        return FileListResponse(files=files)
