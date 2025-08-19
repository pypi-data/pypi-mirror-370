"""
pip install nacos-sdk-python==0.1.14
@Author: kang.yang
@Date: 2024/5/7 16:50
"""
import nacos
import yaml


class NacosConfig:
    """
    nacos服务器配置
    """
    SERVER_ADDRESS = "http://nacos-idc-lan.qizhidao.net:8848"  # 服务器地址
    NAMESPACE = "f2afa4d4-6707-4170-a90c-f3f963075e15"  # 命名空间id
    USER_NAME = "qc_conf_user_dev"  # 账号
    PASSWORD = "2DYH1XfbS79FeM3y"  # 密码


class NacosApi:
    """
    nacos配置读写操作
    """

    def __init__(self,
                 host=NacosConfig.SERVER_ADDRESS,
                 namespace=NacosConfig.NAMESPACE,
                 user=NacosConfig.USER_NAME,
                 password=NacosConfig.PASSWORD):
        self.client = nacos.NacosClient(host,
                                        namespace=namespace,
                                        username=user,
                                        password=password)

    def get_by_data_id(self, data_id: str, key: str = None, group: str = 'DEFAULT_GROUP'):
        if not data_id:
            raise KeyError('data_id不能为空')

        nacos_config = self.client.get_config(data_id, group)
        dict_nacos_config = yaml.load(nacos_config, Loader=yaml.FullLoader)

        if key is not None:
            key_data = dict_nacos_config.get(key)
            print(key_data)
            return key_data
        else:
            print(dict_nacos_config)
            return dict_nacos_config


if __name__ == '__main__':
    pass


