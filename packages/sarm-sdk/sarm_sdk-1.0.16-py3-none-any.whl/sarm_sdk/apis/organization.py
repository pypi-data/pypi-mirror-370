#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 组织架构 API

提供组织架构相关的API操作，包括创建、查询、更新、删除等功能。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.organization import OrganizeInsert, Organization, OrganizationTree, OrganizeUser
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class OrganizationAPI:
    """组织架构API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client

    def statistics(
            self,
            data: List[Dict[str, Any]],
            statistical_info: List[Dict[str, Any]],
            factory_id: str,
            data_count:int=0,
            data_type: str = "running"
    ):
        reqData = {
            "data": data,
            "statistical_info": statistical_info,
            "critical_data_count": data_count,
            "data_type": data_type,
            "factory_id": factory_id
        }
        # 发送请求
        response = self.client.post(
            '/api/insert/statistics',
            data=reqData,
        )
        return response
    def create_batch(
        self,
        organizations: List[OrganizeInsert],
        execute_release: bool = False
    ) -> BatchOperationResult:
        """
        批量创建组织
        
        Args:
            organizations: 组织数据列表
            execute_release: 是否直接发布，默认False进入预处理状态
            
        Returns:
            批量操作结果
            
        Raises:
            SARMValidationError: 数据验证失败
            SARMAPIError: API调用失败
        """
        if not organizations:
            raise SARMValidationError("组织列表不能为空")
        
        if len(organizations) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证数据
        org_data = []
        for org in organizations:
            if isinstance(org, OrganizeInsert):
                org_data.append(org.dict())
            else:
                org_data.append(org)
        
        # 发送请求
        response = self.client.post(
            '/api/organize/openapi/create',
            data=org_data,
            execute_release=execute_release
        )
        
        # 处理简单的成功响应
        if isinstance(response, dict) and 'code' in response:
            success = response.get('code') == 200
            # 创建批量操作结果
            from ..models.response import BatchOperationItem
            items = []
            for i, org in enumerate(organizations):
                # 正确获取组织信息
                if isinstance(org, dict):
                    unique_id = org.get('organize_unique_id', f"org_{i}")
                    name = org.get('organize_name', '')
                elif hasattr(org, 'organize_unique_id'):
                    unique_id = getattr(org, 'organize_unique_id', f"org_{i}")
                    name = getattr(org, 'organize_name', '')
                else:
                    unique_id = f"org_{i}"
                    name = ''
                
                items.append(BatchOperationItem(
                    unique_id=unique_id,
                    name=name,
                    success=success,
                    msg="创建成功" if success else "创建失败"
                ))
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def create(self, organization: OrganizeInsert, execute_release: bool = False) -> BatchOperationResult:
        """
        创建单个组织
        
        Args:
            organization: 组织数据
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        return self.create_batch([organization], execute_release=execute_release)
    
    def update_batch(
        self,
        organizations: List[OrganizeInsert],
        execute_release: bool = False
    ) -> BatchOperationResult:
        """
        批量更新组织
        
        Args:
            organizations: 组织数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not organizations:
            raise SARMValidationError("组织列表不能为空")
        
        # 验证数据
        org_data = []
        for org in organizations:
            if isinstance(org, OrganizeInsert):
                org_data.append(org.dict())
            else:
                org_data.append(org)
        
        # 发送请求
        response = self.client.post(
            '/api/organize/openapi/update',
            data=org_data,
            execute_release=execute_release
        )
        
        # 处理简单的成功响应
        if isinstance(response, dict) and 'code' in response:
            success = response.get('code') == 200
            # 创建批量操作结果
            from ..models.response import BatchOperationItem
            items = []
            for i, org in enumerate(organizations):
                # 正确获取组织信息
                if isinstance(org, dict):
                    unique_id = org.get('organize_unique_id', f"org_{i}")
                    name = org.get('organize_name', '')
                elif hasattr(org, 'organize_unique_id'):
                    unique_id = getattr(org, 'organize_unique_id', f"org_{i}")
                    name = getattr(org, 'organize_name', '')
                else:
                    unique_id = f"org_{i}"
                    name = ''
                
                items.append(BatchOperationItem(
                    unique_id=unique_id,
                    name=name,
                    success=success,
                    msg="更新成功" if success else "更新失败"
                ))
            
            return BatchOperationResult(
                data=items,
                code=response.get('code', 200)
            )
        
        return BatchOperationResult(**response)
    
    def update(self, organization: OrganizeInsert, execute_release: bool = False) -> BatchOperationResult:
        """
        更新单个组织
        
        Args:
            organization: 组织数据
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        return self.update_batch([organization], execute_release=execute_release)
    
    def delete_batch(self, unique_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除组织
        
        Args:
            unique_ids: 组织唯一ID列表
            
        Returns:
            删除结果
            
        Note:
            当层及下级存在关联数据时不允许删除
        """
        if not unique_ids:
            raise SARMValidationError("组织ID列表不能为空")
        
        response = self.client.post(
            '/api/organize/openapi/delete',
            data=unique_ids
        )
        
        return response
    
    def delete(self, unique_id: str) -> Dict[str, Any]:
        """
        删除单个组织
        
        Args:
            unique_id: 组织唯一ID
            
        Returns:
            删除结果
        """
        return self.delete_batch([unique_id])
    
    def get(
        self,
        organize_unique_id: Optional[str] = None,
        organize_name: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        查询组织列表
        
        Args:
            organize_unique_id: 组织唯一ID（精确匹配）
            organize_name: 组织名称（模糊匹配）
            page: 页码
            limit: 每页数量
            
        Returns:
            组织列表和分页信息
        """
        query_data = {
            "page": page,
            "limit": limit
        }
        
        if organize_unique_id:
            query_data["organize_unique_id"] = organize_unique_id
        if organize_name:
            query_data["organize_name"] = organize_name
        
        response = self.client.post('/api/organize/openapi/get', data=query_data)
        return response
    
    def refresh_cache(self) -> Dict[str, Any]:
        """
        刷新组织架构树缓存
        
        这是一个异步操作，用于在批量导入组织数据后刷新组织架构树缓存，
        确保组织层级关系的数据一致性。
        
        Returns:
            操作结果
            
        Note:
            - 这是异步操作，调用成功仅表示任务已提交
            - 建议在批量导入组织后调用此方法
            - 大量组织数据的缓存刷新可能需要一定时间
        """
        response = self.client.get('/api/organize/async_refresh_organize_tree_cache')
        return response
    
    def get_tree(self) -> List[OrganizationTree]:
        """
        获取组织架构树
        
        Returns:
            组织架构树列表
            
        Note:
            如果组织架构缓存未更新，建议先调用 refresh_cache() 方法
        """
        # 获取所有组织
        all_orgs = []
        page = 1
        limit = 100
        
        while True:
            response = self.get(page=page, limit=limit)
            data_list = response.get('data', {}).get('data_list', [])
            
            if not data_list:
                break
                
            all_orgs.extend(data_list)
            
            # 检查是否还有更多数据
            total = response.get('data', {}).get('total', 0)
            if len(all_orgs) >= total:
                break
                
            page += 1
        
        # 构建组织树
        return self._build_organization_tree(all_orgs)
    
    def _build_organization_tree(self, organizations: List[Dict[str, Any]]) -> List[OrganizationTree]:
        """
        构建组织架构树
        
        Args:
            organizations: 组织数据列表
            
        Returns:
            组织架构树列表
        """
        # 创建组织字典，便于查找
        org_dict = {org['organize_uuid']: org for org in organizations}
        
        # 查找根节点（父ID为'0'或None的组织）
        roots = []
        
        for org in organizations:
            parent_id = org.get('organize_puuid')
            if parent_id == '0' or parent_id is None:
                tree_node = OrganizationTree(
                    organize_unique_id=org['organize_uuid'],
                    organize_name=org['organize_name'],
                    level=0,
                    children=[]
                )
                self._build_children(tree_node, org_dict, 1)
                roots.append(tree_node)
        
        return roots
    
    def _build_children(
        self,
        parent_node: OrganizationTree,
        org_dict: Dict[str, Dict[str, Any]],
        level: int
    ):
        """
        递归构建子组织节点
        
        Args:
            parent_node: 父节点
            org_dict: 组织字典
            level: 当前层级
        """
        parent_id = parent_node.organize_unique_id
        
        for org_id, org in org_dict.items():
            if org.get('organize_puuid') == parent_id:
                child_node = OrganizationTree(
                    organize_unique_id=org['organize_uuid'],
                    organize_name=org['organize_name'],
                    level=level,
                    children=[]
                )
                self._build_children(child_node, org_dict, level + 1)
                parent_node.children.append(child_node)
    
    # 用户管理相关方法
    def create_users(
        self,
        organize_unique_id: str,
        users: List[OrganizeUser]
    ) -> Dict[str, Any]:
        """
        批量创建组织用户
        
        Args:
            organize_union_id: 组织唯一ID
            users: 用户数据列表
            
        Returns:
            创建结果
        """
        if not users:
            raise SARMValidationError("用户列表不能为空")
        
        user_data = []
        for user in users:
            if isinstance(user, OrganizeUser):
                user_data.append(user.dict())
            else:
                user_data.append(user)
        
        request_data = {
            "organize_unique_id": organize_unique_id,
            "user_list": user_data
        }
        
        response = self.client.post('/api/organize_user/create', data=request_data)
        return response
    
    def update_users(self, users: List[OrganizeUser]) -> Dict[str, Any]:
        """
        批量更新组织用户
        
        Args:
            users: 用户数据列表
            
        Returns:
            更新结果
        """
        if not users:
            raise SARMValidationError("用户列表不能为空")
        
        user_data = []
        for user in users:
            if isinstance(user, OrganizeUser):
                user_data.append(user.dict())
            else:
                user_data.append(user)
        
        response = self.client.post('/api/organize_user/update', data=user_data)
        return response
    
    def delete_users(self, user_unique_ids: List[str]) -> Dict[str, Any]:
        """
        批量删除组织用户
        
        Args:
            user_unique_ids: 用户唯一ID列表
            
        Returns:
            删除结果
        """
        if not user_unique_ids:
            raise SARMValidationError("用户ID列表不能为空")
        
        response = self.client.post('/api/organize_user/delete', data=user_unique_ids)
        return response

    def delete_parent_id(self, organize_id: List[str]) -> Dict[str, Any]:
        """
        删除组织的父级ID关联

        Args:
            organize_id: 组织ID

        Returns:
            操作结果
        """
        response = self.client.post('/api/organize/openapi/delete_pid', data=organize_id)
        return response

    def delete_leader(self, organize_id: List[str]) -> Dict[str, Any]:
        """
        删除组织的负责人关联

        Args:
            organize_id: 组织ID

        Returns:
            操作结果
        """
        response = self.client.post('/api/organize/openapi/delete_leader', data=organize_id)
        return response
    
    def get_users(
        self,
        organize_unique_id: str,
        user_unique_id: Optional[str] = None,
        user_name: Optional[str] = None,
        enterprise_email: Optional[str] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        查询组织用户列表
        
        Args:
            organize_union_id: 组织唯一ID
            user_unique_id: 用户唯一ID
            user_name: 用户名
            enterprise_email: 企业邮箱
            page: 页码
            limit: 每页数量
            
        Returns:
            用户列表和分页信息
        """
        user_info = {}
        if user_unique_id:
            user_info["organize_user_unique_id"] = user_unique_id
        if user_name:
            user_info["organize_user_name"] = user_name
        if enterprise_email:
            user_info["organize_user_enterprise_email"] = enterprise_email
        
        query_data = {
            "organize_unique_id": organize_unique_id,
            "user_info": user_info,
            "page": page,
            "limit": limit
        }
        
        response = self.client.post('/api/organize_user/list', data=query_data)
        return response 