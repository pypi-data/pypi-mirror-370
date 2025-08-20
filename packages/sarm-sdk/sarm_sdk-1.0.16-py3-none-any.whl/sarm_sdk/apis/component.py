#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 软件成分 API

提供软件成分相关的API操作。
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..exceptions import SARMValidationError

if TYPE_CHECKING:
    from ..client import SARMClient


class ComponentAPI:
    """
    软件成分API类
    
    注意：软件成分创建可以通过以下两种方式实现：
    1. CarrierDataImportAPI.import_carrier_data() 方法进行批量创建
    2. ComponentAPI.add_to_carrier() 方法添加到特定载体
    
    本API主要提供更新、查询和关联管理功能。
    """
    
    def __init__(self, client: 'SARMClient'):
        self.client = client
    
    def update(self, component_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新软件成分信息
        
        Args:
            component_data: 软件成分数据
            
        Returns:
            操作结果
        """
        if 'component_unique_id' not in component_data:
            raise SARMValidationError("更新软件成分时必须提供 component_unique_id")
        
        response = self.client.post('/api/component/update', data=component_data)
        return response
    
    def add_to_carrier(
        self, 
        carrier_unique_id: str,
        component_data: Dict[str, Any],
        security_capability_unique_id: str
    ) -> Dict[str, Any]:
        """
        增加应用载体下软件成分
        
        注意：此方法可用于创建新的软件成分并关联到特定载体。
        
        Args:
            carrier_unique_id: 载体唯一ID
            component_data: 软件成分数据
            security_capability_unique_id: 安全能力唯一ID
            
        Returns:
            操作结果
        """
        if 'component_unique_id' not in component_data:
            raise SARMValidationError("必须提供 component_unique_id")
        
        params = {"security_capability_unique_id": security_capability_unique_id}
        response = self.client.post(
            f'/api/carrier/add_components/{carrier_unique_id}',
            data=component_data,
            params=params
        )
        return response
    
    def delete_from_carrier(
        self, 
        carrier_unique_id: str, 
        component_ids: List[str]
    ) -> Dict[str, Any]:
        """
        删除应用载体下软件成分
        注意：删除软件成分的同时会同步删除对应漏洞
        
        Args:
            carrier_unique_id: 载体唯一ID
            component_ids: 要删除的成分ID列表
            
        Returns:
            操作结果
        """
        if not component_ids:
            raise SARMValidationError("成分ID列表不能为空")
        
        response = self.client.delete(
            f'/api/carrier/components/{carrier_unique_id}',
            data=component_ids
        )
        return response
    
    def get_carrier_components(
        self, 
        carrier_unique_id: str,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取载体下的软件成分列表
        
        Args:
            carrier_unique_id: 载体唯一ID
            page: 页码
            limit: 每页条数
            
        Returns:
            成分列表
        """
        data = {
            "carrier_unique_id": carrier_unique_id,
            "page": page,
            "limit": limit
        }
        response = self.client.post('/api/carrier/components', data=data)
        return response 