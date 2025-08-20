import hid


def getUsbHidPathList():
    e = hid.enumerate(0x03eb, 0x2421)
    result = []
    for item in e:  # type:dict
        path = str(item.get("path"))
        if path.find("kbd") == -1 and path.find("KBD") == -1:
            result.append(item.get("path"))
    return result


def getUsbHidPathDict():
    """
    获取usb-hid字典
    :return: usb-hid dict
    """
    result = {}
    e = hid.enumerate(0x03eb, 0x2421)
    for index, item in enumerate(e):  # type:dict
        path = str(item.get("path"))
        if path.find("kbd") == -1 and path.find("KBD") == -1:
            result["USB-HID-" + str(index)] = item.get("path")
    return result


#
#
# print(getUsbHidPathList())
# # print(getUsbHidPathDict())
