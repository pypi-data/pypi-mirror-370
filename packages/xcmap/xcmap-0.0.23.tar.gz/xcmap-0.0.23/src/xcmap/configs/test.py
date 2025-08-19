# import time
#
# from nacos_center import NacosConfig, NacosStore
# if __name__ == '__main__':
#     nacos_config = NacosConfig(
#         server_addresses="https://nacos-api.banyanph.com:6443",
#         data_id="storage.yaml",
#         group="STORAGE",
#         username="nacos",
#         password="8uhb(IJN0okm"
#     )
#     nacos_store = NacosStore(nacos_config)
#     while True:
#         config = nacos_store.get_config()
#         print(config)
#         time.sleep(5)