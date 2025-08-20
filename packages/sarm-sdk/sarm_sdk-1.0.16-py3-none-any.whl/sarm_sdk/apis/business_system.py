#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 业务系统 API

提供业务系统相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class BusinessSystemAPI:
    """业务系统API类"""
    
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
        business_systems: List[Dict[str, Any]],
        execute_release: bool = False
    ):
        """
        批量创建业务系统
        
        Args:
            business_systems: 业务系统数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not business_systems:
            raise SARMValidationError("业务系统列表不能为空")
        
        if len(business_systems) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证必填字段
        for bs in business_systems:
            if 'business_system' not in bs:
                raise SARMValidationError("缺少 business_system 字段")
            
            business_system = bs['business_system']
            if 'business_system_name' not in business_system:
                raise SARMValidationError("缺少 business_system_name 字段")
            if 'business_system_uuid' not in business_system:
                raise SARMValidationError("缺少 business_system_uuid 字段")
        
        # 发送请求
        response = self.client.post(
            '/api/business_system/create',
            data=business_systems,
            execute_release=execute_release
        )

        
        return response
    
    def create(self, business_system_data: Dict[str, Any], execute_release: bool = False):
        """创建单个业务系统"""
        return self.create_batch([business_system_data], execute_release=execute_release)
    
    def delete_batch(self, business_system_ids: List[str]):
        """
        批量删除业务系统
        注意：业务系统存在关联数据时无法删除
        
        Args:
            business_system_ids: 业务系统ID列表
            
        Returns:
            批量操作结果
        """
        if not business_system_ids:
            raise SARMValidationError("业务系统ID列表不能为空")
        
        data = {"business_system_id_list": business_system_ids}
        response = self.client.delete('/api/business_system/delete', data=data)
        return response
        # # 处理批量操作结果
        # if isinstance(response, dict) and 'code' in response and 'data' in response:
        #     from ..models.response import BatchOperationItem
        #
        #     if isinstance(response.get('data'), list):
        #         items = [
        #             BatchOperationItem(
        #                 unique_id=item.get('unique_id', ''),
        #                 name=item.get('name', ''),
        #                 success=item.get('success', False),
        #                 msg=item.get('msg', '')
        #             )
        #             for item in response['data']
        #         ]
        #     else:
        #         # 简单成功响应
        #         success = response.get('code') == 200
        #         items = [
        #             BatchOperationItem(
        #                 unique_id=bs_id,
        #                 name='',
        #                 success=success,
        #                 msg="删除成功" if success else "删除失败"
        #             )
        #             for bs_id in business_system_ids
        #         ]
        #
        #     return BatchOperationResult(
        #         data=items,
        #         code=response.get('code', 200),
        #         summary=response.get('summary', '')
        #     )
        #
        # return BatchOperationResult(**response)
    
    def delete(self, business_system_id: str) -> BatchOperationResult:
        """删除单个业务系统"""
        return self.delete_batch([business_system_id])
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 10,
        business_system_name: Optional[str] = None,
        business_system_status: Optional[str] = None,
        data_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取业务系统列表
        
        Args:
            page: 页码
            limit: 每页条数
            business_system_name: 业务系统名称
            business_system_status: 业务系统状态(active、maintenance、retired)
            data_status: 数据状态(imperfect,perfect,published)
            
        Returns:
            业务系统列表
        """
        data: Dict[str, Any] = {"page": page, "limit": limit}
        
        if business_system_name:
            data["business_system_name"] = business_system_name
        if business_system_status:
            data["business_system_status"] = business_system_status
        if data_status:
            data["data_status"] = data_status
        
        response = self.client.get('/api/business_system/list', data=data)
        return response
    
    def update(
        self,
        business_system_data: Dict[str, Any],
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        更新业务系统
        
        Args:
            business_system_data: 业务系统数据
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        response = self.client.post(
            '/api/business_system/update',
            data=business_system_data,
            execute_release=execute_release
        )
        return response
    
    def delete_organize(self, organize_id: str) -> Dict[str, Any]:
        """删除业务系统的组织关联"""
        data = {"organize_id": organize_id}
        response = self.client.delete('/api/business_system/delete_organize', data=data)
        return response 