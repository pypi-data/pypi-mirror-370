import numpy as np
from enum import Enum
from typing import Optional, List, Union, Tuple
from pathlib import Path

def call_service(master_ip:str, service_name:str, action_name:str, *args, **kwargs) -> dict:
    """
    调用算力板上的服务

    Args:
        master_ip (str): 算力板 ip 地址, 如: 192.168.99.2
        service_name (str): 服务名称
        action_name (str): 服务支持的 action 名称

    Returns:
        dict: {"success": True, "ret": ret}
    """

class Sensor:
    class OutputType(Enum):
        Rectify = 1
        Difference = 2  
        Depth = 3
        Marker2D = 4
        Marker3D = 5
        Marker3DFlow = 6
        Marker3DInit = 7
        MarkerUnorder = 8
        Force = 9
        ForceResultant = 16
        ForceNorm = 10
        Mesh3D = 11
        Mesh3DFlow = 12
        Mesh3DInit = 13
        Marker2DInit = 14
        Marker2DFlip = 15
        TimeStamp = 17

    @classmethod
    def createSolver(cls, runtime_path: Union[str, Path])-> "SensorSolver":
        """
        工厂方法（类方法），用于从给定的 runtime 配置路径创建一个 SensorSolver 实例。

        Args:
            runtime_path (str | Path):
                - 指向 runtime 配置文件的路径
                - 可以是字符串或 pathlib.Path 对象

        Returns:
            SensorSolver | bool:
                - 成功时返回初始化好的 SensorSolver 实例
                - 失败时返回 False（并打印错误信息）

        注意:
            - 若 runtime 配置文件损坏或解密失败，会抛异常并被捕获
        """

    @classmethod
    def create(
        cls,
        cam_id: Union[int, str] = 0,
        use_gpu: bool = True,
        config_path: Optional[Union[str, Path]] = None,
        api: Optional[object] = None,  # 若有具体 Enum 类型,建议替换 object
        infer_size: Tuple[int, int] = (144, 240),
        check_serial: bool = True,
        rectify_size: Optional[Tuple[int, int]] = None,
        ip_address: Optional[str] = None,
        video_path: Optional[str] = None
    ) -> "Sensor":
        """
        创建 Sensor 实例。

        Args:
            cam_id (int | str, optional): 相机 ID、序列号或视频路径。默认值为 0。
            use_gpu (bool, optional): 是否使用 GPU 进行推理。默认值为 True。
            config_path (str | Path, optional): 配置文件路径。默认 None。
            api (Enum, optional): 相机 API 类型（如 OpenCV 后端）。默认 None。
            check_serial (bool, optional): 是否检查相机序列号。默认 True。
                - 若设置环境变量 `XENSE_AUTO_SERIAL=1`,所有相机设备将使用 PID+camid 作为序列号（仅用于调试）。
            rectify_size (tuple[int, int], optional): 矫正后图像尺寸,用于图像重映射。默认 None。
            ip_address (str, optional): 相机的网络地址（用于远程连接）。默认 None。
            video_path (str, optional): 视频文件路径（用于离线模拟）。默认 None。

        Returns:
            Sensor: 创建的传感器实例。
        """

    def getRectifyImage(self) -> np.ndarray:
        """
        获取传感器图像,并对原始图像进行重映射。

        Returns:
            np.ndarray: 图像数据,形状为 (700, 400, 3),类型为 uint8
        """

    def resetReferenceImage(self) -> None:
        """
        重置传感器的参考图像。
        """
        ...

    def startSaveSensorInfo(self, path: str, data_to_save: Optional[List[Sensor.OutputType]] = None) -> None:
        """
        开始保存传感器信息。

        Args:
            path (str): 保存数据的路径。
            data_to_save (Optional[List[Sensor.OutputType]]): 指定要保存的数据类型列表, None则为所有可保存数据。
        """
        ...

    def stopSaveSensorInfo(self) -> None:
        """
        停止保存传感器信息。
        """
        ...

    def getCameraID(self) -> int:
        """
        获取相机 ID。

        Returns:
            int: 相机的唯一标识符。
        """
        ...

    def release(self) -> None:
        """
        安全退出传感器,释放资源。
        """

    def selectSensorInfo(self, *args: Sensor.OutputType):
        """
        选择需要输出的传感器数据类型。

        Args:
            一个或多个 `Sensor.OutputType` 枚举实例,用于指定所需的传感器输出数据类型。

            可选的 OutputType 枚举值及其说明如下：
                - Rectify: 校正图像,BGR 格式,shape = (h, w, 3)
                - Difference: 差分图像,BGR 格式,shape = (h, w, 3)
                - Depth: 深度图像,单位为毫米,shape = (h, w)
                - Force: 三维力分布,shape = (35, 20, 3)
                - ForceNorm: 法向力分量,shape = (35, 20, 3)
                - ForceResultant: 六维合力向量,shape = (6,)
                - Marker2D: 切向位移,shape = (35, 20, 2)
                - Mesh3D: 当前帧的三维网格,shape = (35, 20, 3)
                - Mesh3DInit: 初始三维网格,shape = (35, 20, 3)
                - Mesh3DFlow: 网格形变向量,shape = (35, 20, 3)

        Returns:
            返回的数据为 `Optional[np.ndarray]`,当对应传感器数据缺失时返回 None。

        示例:
            select_outputs(OutputType.Depth, OutputType.ForceNorm, OutputType.Mesh3D)
        """
    
    def calibrateSensor(self):
        """
        重新校准传感器(在无物理接触时调用)
        """

    def drawMarkerMove(self, img):
        """
        绘制描述marker位置变化的向量图像

        Parameters:
            img: image in [700,400,3] (h,w,c) uint8
        Returns:
            img: image in [700,400,3] (h,w,c) uint8
        """
    
    def scanSerialNumber() -> dict:
        """
        查找当前设备所有已经连接的传感器

        Returns:
            dict: {serial_number: camera_id}
        """

    
    def drawMarker(self, img, marker, color=(3, 253, 253), radius=2, thickness=2):
                """
        在原图上标注出已检测出的marker位置

        Parameters:
            img: image in [700,400,3] (h,w,c) uint8
            marker: np.array 
        Returns:
            img: image in [700,400,3] (h,w,c) uint8
        """

    def exportRuntimeConfig(self, save_dir="."):
        """
        将当前传感器的运行时配置导出到指定目录。

        Args:
            save_dir (str | Path, 可选):
                - 保存配置文件的目标目录
                - 默认为当前工作目录

        Returns:
            None

        功能:
            - 将当前 Sensor 内部的配置导出为可持久化文件，便于后续加载或调试。
            - 导出的文件可以作为 runtime 配置文件再次被 `createSolver` 使用。
        """
                
class SensorSolver(Sensor):
    """
    继承自 Sensor 的一个特殊实现 —— 用于 Solver 模式的传感器封装。
    主要功能：
      - 提供 selectSensorInfo 接口
    """
    def selectSensorInfo(self, *args, rectify_image=None):
        """
        从 图片或 numpy.array 获取传感器信息。

        Args:
            *args: 透传给 Sensor.selectSensorInfo 的位置参数
            rectify_image (np.ndarray): 矫正后的图像，必须提供

        Returns:
            selectSensorInfo 的输出结果

        注意:
            由于 Solver 模式必须传入矫正图像，因此 rectify_image 为必选参数，
            如果未提供，将抛出 ValueError。
        """

class ExampleView:
    def create2d(self, *args) -> View2d:
        """
        
        """
    def setDepth(self, depth):
        """
        
        """

    def setForceFlow(self, force, res_force, mesh_init):
        """
        
        """

    def setCallback(self, function):
        """
        
        """

    def show(self):
        """
        
        """

    def setMarkerUnorder(self, marker_unordered):
        """
        
        """

    class View2d():
        def setData(self, name, img):
            """
            
            """
