"""
    #  @ModuleName: VasBuild
    #  @Function: 
    #  @Author: Ljx
    #  @Time: 2020/12/7 11:41
"""

"""
    #  @ModuleName: IasBuild
    #  @Function: 
    #  @Author: Ljx
    #  @Time: 2020/12/4 14:32
"""
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from ..serializers.serializers import VasPackageSerializers
from ..common.sdk_function import docker_build
from ..common.sdk_function import docker_run_vas
from ..common.argsCmd import vas_3_name, vas_3_url, vas_4_name, vas_4_url, dockerfile_vas
import os
import logging
from ..common.sdk_requests import get_sdk_opencv_version

logger = logging.getLogger(__name__)



class VasPackage(APIView):
    """
    用于封装Vas
    """
    def post(self, requests, *args, **kwargs):
        data = requests.data
        obj = VasPackageSerializers(data=data)
        if not obj.is_valid():
            logging.exception(obj)
            return Response({"87": "参数错误"})
        image_name = obj.data.get("image_name")
        port = obj.data.get("port")
        image = image_name + "_test_vas"

        try:
            opencv_version = get_sdk_opencv_version(image_name)
        except Exception as e:
            logging.exception(e)
            return Response({"code": "90", "msg": "获取镜像版本失败"})
        if not opencv_version:
            logging.exception(opencv_version)
            return Response({"code": "90", "msg": "算法启动失败, 获取算法OpenCV失败"})
        # 封装镜像
        if opencv_version.startswith("3."):
            status = docker_build(image, dockerfile_vas, image_name, vas_3_name, vas_3_url)
            if not status:
                return Response({"code": "90", "msg": "dockerfile生成失败"})
        else:
            status = docker_build(image, dockerfile_vas, image_name, vas_4_name, vas_4_url)
            if not status:
                return Response({"code": "90", "msg": "dockerfile生成失败"})
        # 运行镜像
        status, res = docker_run_vas(image, port)
        if not status:
            if "port is already" in res:
                logging.exception(res)
                return Response({"code": "90", "msg": "算法启动失败, 端口被占用"})
            else:
                logging.exception(res)
                return Response({"code": "90", "msg": "算法启动失败, 请确保镜像存在或者镜像名称正确"})
        return Response({"code": "100", "msg": "封装VAS成功,可以直接调用VAS", "container_id": res})
