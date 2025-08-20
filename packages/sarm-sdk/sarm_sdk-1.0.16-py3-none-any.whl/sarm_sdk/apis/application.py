#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 应用 API

提供应用相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..models.response import BatchOperationResult
from ..exceptions import SARMValidationError, SARMAPIError

if TYPE_CHECKING:
    from ..client import SARMClient


class ApplicationAPI:
    """应用API类"""
    
    def __init__(self, client: 'SARMClient'):
        self.client = client

    def statistics(
            self,
            data: List[Dict[str, Any]],
            statistical_info: List[Dict[str, Any]],
            factory_id: str,
            data_count: int = 0,
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
        applications: List[Dict[str, Any]],
        execute_release: bool = False
    ):
        """
        批量创建应用
        
        Args:
            applications: 应用数据列表
            execute_release: 是否直接发布
            
        Returns:
            批量操作结果
        """
        if not applications:
            raise SARMValidationError("应用列表不能为空")
        
        if len(applications) > 1000:
            raise SARMValidationError("单次批量操作不能超过1000条记录")
        
        # 验证必填字段
        for app in applications:
            if 'application' not in app:
                raise SARMValidationError("缺少 application 字段")
            
            application = app['application']
            if 'application_unique_id' not in application:
                raise SARMValidationError("缺少 application_unique_id 字段")
            if 'application_name' not in application:
                raise SARMValidationError("缺少 application_name 字段")

        # 发送请求
        response = self.client.post(
            '/api/application/create',
            data=applications,
            execute_release=execute_release
        )
        return response
        # # 处理批量操作结果
        # if isinstance(response, dict) and 'code' in response:
        #     from ..models.response import BatchOperationItem
        #
        #     # 应用API的响应格式比较简单，我们需要构造BatchOperationResult
        #     code = response.get('code')
        #     success = code == 200 or code == '200'
        #     items = [
        #         BatchOperationItem(
        #             unique_id=app['application'].get('application_unique_id', f"app_{i}"),
        #             name=app['application'].get('application_name', ''),
        #             success=success,
        #             msg=response.get('msg_zh', "创建成功" if success else "创建失败")
        #         )
        #         for i, app in enumerate(applications)
        #     ]
        #
        #     return BatchOperationResult(
        #         data=items,
        #         code=200 if success else 500
        #     )
        #
        # return BatchOperationResult(**response)
    
    def create(self, application_data: Dict[str, Any], execute_release: bool = False):
        """创建单个应用"""
        return self.create_batch([application_data], execute_release=execute_release)
    
    def delete_batch(self, app_ids: List[str]):
        """
        批量删除应用
        
        Args:
            app_ids: 应用ID列表
            
        Returns:
            批量操作结果
        """
        if not app_ids:
            raise SARMValidationError("应用ID列表不能为空")
        
        data = {"app_id_list": app_ids}
        response = self.client.delete('/api/application/delete', data=data)
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
        #                 unique_id=app_id,
        #                 name='',
        #                 success=success,
        #                 msg="删除成功" if success else "删除失败"
        #             )
        #             for app_id in app_ids
        #         ]
        #
        #     return BatchOperationResult(
        #         data=items,
        #         code=response.get('code', 200)
        #     )
        #
        # return BatchOperationResult(**response)
    
    def delete(self, app_id: str) -> BatchOperationResult:
        """删除单个应用"""
        return self.delete_batch([app_id])
    
    def get_list(
        self,
        page: int = 1,
        limit: int = 10,
        application_name: Optional[str] = None,
        application_status: Optional[str] = None,
        data_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取应用列表
        
        Args:
            page: 页码
            limit: 每页条数
            application_name: 应用名称
            application_status: 应用状态(active、inactive)
            data_status: 数据状态(imperfect,perfect,published)
            
        Returns:
            应用列表
        """
        data = {"page": page, "limit": limit}
        
        if application_name:
            data["application_name"] = application_name
        if application_status:
            data["application_status"] = application_status
        if data_status:
            data["data_status"] = data_status
        
        response = self.client.get('/api/application/list', data=data)
        return response
    
    def update(
        self,
        application_data: Dict[str, Any],
        execute_release: bool = False
    ) -> Dict[str, Any]:
        """
        更新应用
        
        Args:
            application_data: 应用数据
            execute_release: 是否直接发布
            
        Returns:
            操作结果
        """
        response = self.client.post(
            '/api/application/update',
            data=application_data,
            execute_release=execute_release
        )
        return response
    
    def delete_business_system(self, app_id: str, business_system_id: str) -> Dict[str, Any]:
        """删除应用的业务系统关联"""
        data = {
            "app_id": app_id,
            "business_system_id": business_system_id
        }
        response = self.client.delete('/api/application/delete_business_system', data=data)
        return response 