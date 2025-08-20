# import usb.core
# import usb.util


# import time


# import platform
#
# # find our device
# dev = usb.core.find(idVendor=0x03EB, idProduct=0x2421)  # 设备管理器中确认这两个参数值
#
# # was it found?
# if dev is None:
#     raise ValueError('Device not found')
#
# if platform.system().lower() == 'linux':
#     if dev.is_kernel_driver_active(0):
#         dev.detach_kernel_driver(0)  # ＃分离内核驱动程序并通过libusb声明
#
# # set the active configuration. With no arguments, the first
# # configuration will be the active one
# dev.set_configuration()
#
# # get an endpoint instance
# configuration = dev.get_active_configuration()
# # configuration = dev[0]
#
# cfg_ = configuration[(0, 0)]
# # alt = usb.util.find_descriptor(cfg_, find_all=True, bInterfaceNumber=1)
# # print(alt)
#
# # 0x2 写入节点
# outPoint = usb.util.find_descriptor(
#     cfg_,
#     # match the first OUT endpoint
#     custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
#
# # 0x81 读取节点
# inPoint = usb.util.find_descriptor(
#     cfg_,
#     # match the first IN endpoint
#     custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
#
# # assert outPoint, inPoint is not None
#
# msg = [90, 0, 1, 2, 255, 0, 0, 136, 90]  # bytes
# temp0 = [0 for i in range(64 - len(msg))]  # 缺少的字节
#
# msg.extend(temp0)  # 合并后64个字节[1, 2, 3, 4, 5, 6,0,0,0,0,......]
#
# outPoint.write(msg)  # 写入 注意必须满足64个字节
# # dev.write(0x2, msg, 0)  # 效果同上写入
#
# read = inPoint.read(64)  # 读取64个字节
# print(read)
# # read = dev.read(0x81, 64, 0)  # 效果同上读取

# def getUsbHidDeviceList():
#     """
#     获取usb-hid列表
#     :return: usb-hid list
#     """
#     dev = usb.core.find(find_all=True, idVendor=0x03EB, idProduct=0x2421)
#     return [item for item in dev]


# def getUsbHidDeviceDict():
#     """
#     获取usb-hid字典
#     :return: usb-hid dict
#     """
#     dev = usb.core.find(find_all=True, idVendor=0x03EB, idProduct=0x2421)
#     hidDic = {}
#     for item in dev:
#         hidDic[str(item.address)] = item
#     return hidDic

# start = time.time()
# hid_list = getUsbHidDict()
# print(hid_list)
# print(time.time() - start)

# python -c "import usb; print(f'Using PyUSB {usb.__version__}')"
# python -m timeit -s "import usb; list(usb.core.find(find_all=True))"
