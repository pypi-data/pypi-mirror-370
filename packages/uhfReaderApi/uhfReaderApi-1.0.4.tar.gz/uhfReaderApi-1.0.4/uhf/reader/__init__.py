# from time import *
from uhf.reader.protocol import *
from uhf.reader.communication import *
from uhf.reader.utils import *
# from json import *
#
# tidMap = {}
#
#
# def receiveEpc(epcInfo: LogBaseEpcInfo):
#     if epcInfo.result == 0:
#         print((epcInfo.epc, epcInfo.tid, epcInfo.userData, epcInfo.reserved))
#         if epcInfo.tid not in tidMap:
#             epcInfo.result = 1
#             tidMap[epcInfo.tid] = epcInfo
#         else:
#             tid_ = tidMap[epcInfo.tid]
#             tid_.result += 1
#             tidMap[epcInfo.tid] = tid_
#
#
# def callEpcOver():
#     print("---------------------")
#     sum = 0
#     for k, v in tidMap.items():
#         print(k, v.result)
#         sum += v.result
#     print(len(tidMap), "======", sum)
#
#
# def callTcpDisconnect(readName: ()):
#     print("断开连接", readName)
#     client.close()
#
#
# def MsgBaseStopTest():
#     stop = MsgBaseStop()
#     client.sendSynMsg(stop)
#     print(stop.rtMsg)
#
#
# def MsgAppGetReaderInfoTest():
#     # info = MsgAppGetReaderInfo()
#     # client.sendSynMsg(info)
#     # print(info)
#     client.sendSynBytes(hexToBytes("5A0001021000080000000101020006ED08"))
#
#
# def MsgAppSetSerialParamTest():
#     param = MsgAppSetSerialParam(2)
#     client.sendSynMsg(param)
#     print(param.rtMsg)
#
#
# def MsgAppGetSerialParamTest():
#     serialParam = MsgAppGetSerialParam()
#     print(client.sendSynMsg(serialParam))
#     print(serialParam)
#
#
# def MsgAppSetGpoTest():
#     gpo = MsgAppSetGpo(gpo1=1)
#     print(client.sendSynMsg(gpo))
#
#
# def MsgAppGetGpiStateTest():
#     state = MsgAppGetGpiState()
#     client.sendSynMsg(state)
#     print(state)
#
#
# def MsgAppSetEthernetIPTest():
#     ip = MsgAppSetEthernetIP(1, ip="192.168.1.168", mask="255.255.255.0", gateway="192.168.1.1")
#     print(client.sendSynMsg(ip))
#
#
# def MsgAppGetEthernetIPTest():
#     ip = MsgAppGetEthernetIP()
#     print(client.sendSynMsg(ip))
#     print(ip)
#
#
# def MsgAppGetReaderMacTest():
#     mac = MsgAppGetReaderMac()
#     print(client.sendSynMsg(mac))
#     print(mac)
#
#
# def MsgAppGetTcpModeTest():
#     tcpMode = MsgAppGetTcpMode()
#     print(client.sendSynMsg(tcpMode))
#     print(tcpMode)
#
#
# def MsgAppSetTcpModeTest():
#     setTcpMode = MsgAppSetTcpMode(0, serverPort=8160, clientIp="192.168.11.21", clientPort=8160)
#     print(client.sendSynMsg(setTcpMode))
#
#
# def MsgAppGetGpiTriggerTest():
#     getTrigger = MsgAppGetGpiTrigger(0)
#     print(client.sendSynMsg(getTrigger))
#     print(getTrigger)
#
#
# def MsgAppSetGpiTriggerTest():
#     setTrigger = MsgAppSetGpiTrigger(0, 2, "", 1, overDelayTime=10, levelUploadSwitch=1)
#     print(client.sendSynMsg(setTrigger))
#
#
# def MsgAppSetWiegandTest():
#     setWiegand = MsgAppSetWiegand(0, 0, 1)
#     print(client.sendSynMsg(setWiegand))
#     print(setWiegand)
#
#
# def MsgAppGetWiegandTest():
#     getWiegand = MsgAppGetWiegand()
#     print(client.sendSynMsg(getWiegand))
#     print(getWiegand)
#
#
# def MsgAppResetTest():
#     reset = MsgAppReset()
#     print(client.sendSynMsg(reset))
#     print(reset)
#
#
# def MsgAppSetReaderTimeTest():
#     setTime = MsgAppSetReaderTime(nowTimeSecond())
#     print(client.sendSynMsg(setTime))
#     print(setTime)
#
#
# def MsgAppGetReaderTimeTest():
#     getTime = MsgAppGetReaderTime()
#     print(client.sendSynMsg(getTime))
#     print(getTime.seconds)
#     print(secondFormat(getTime.seconds))
#
#
# def MsgAppRestoreDefaultTest():
#     restoreDefault = MsgAppRestoreDefault()
#     print(client.senUnSynMsg(restoreDefault))
#
#
# def MsgAppSetRs485Test():
#     setRs485 = MsgAppSetRs485(2)
#     print(client.sendSynMsg(setRs485))
#
#
# def MsgAppGetRs485Test():
#     getRs485 = MsgAppGetRs485()
#     print(client.sendSynMsg(getRs485))
#     print(getRs485)
#
#
# def MsgAppSetBreakpointResumeTest():
#     setBreakpointResume = MsgAppSetBreakpointResume(0)
#     print(client.sendSynMsg(setBreakpointResume))
#     print(setBreakpointResume)
#
#
# def MsgAppGetBreakpointResumeTest():
#     getBreakpointResume = MsgAppGetBreakpointResume()
#     print(client.sendSynMsg(getBreakpointResume))
#     print(getBreakpointResume)
#
#
# def MsgAppGetCacheTagDataTest():
#     getCacheTagData = MsgAppGetCacheTagData()
#     print(client.sendSynMsg(getCacheTagData))
#
#
# def MsgAppClearCacheDataTest():
#     clearCacheData = MsgAppClearCacheData()
#     print(client.sendSynMsg(clearCacheData))
#
#
# def MsgAppTagDataReplyTest():
#     tagDataReply = MsgAppTagDataReply(1)
#     print(client.sendSynMsg(tagDataReply))
#
#
# def MsgAppSetBeepOnOffTest():
#     setBeepOnOff = MsgAppSetBeepOnOff(0)
#     print(client.sendSynMsg(setBeepOnOff))
#
#
# def MsgAppSetBeepTest():
#     setBeep = MsgAppSetBeep(1, 0)
#     print(client.sendSynMsg(setBeep))
#
#
# def MsgAppGetWhiteListTest():
#     getWhiteList = MsgAppGetWhiteList(0)
#     print(client.sendSynMsg(getWhiteList))
#     print(getWhiteList)
#
#
# def MsgAppImportWhiteListTest():
#     importWhiteList = MsgAppImportWhiteList(0)
#     importWhiteList.packetContent = []
#     print(client.sendSynMsg(importWhiteList))
#
#
# def MsgAppDelWhiteListTest():
#     delWhiteList = MsgAppDelWhiteList()
#     print(client.sendSynMsg(delWhiteList))
#
#
# def MsgAppSetWhiteListActionTest():
#     setWhiteListAction = MsgAppSetWhiteListAction(1, 1)
#     print(client.sendSynMsg(setWhiteListAction))
#
#
# def MsgAppGetWhiteListActionTest():
#     getWhiteListAction = MsgAppGetWhiteListAction()
#     print(client.sendSynMsg(getWhiteListAction))
#     print(getWhiteListAction)
#
#
# def MsgAppGetWhiteListSwitchTest():
#     getWhiteListSwitch = MsgAppGetWhiteListSwitch()
#     print(client.sendSynMsg(getWhiteListSwitch))
#     print(getWhiteListSwitch)
#
#
# def MsgAppSetWhiteListSwitchTest():
#     setWhiteListSwitch = MsgAppSetWhiteListSwitch(0, 1)
#     print(client.sendSynMsg(setWhiteListSwitch))
#     print(setWhiteListSwitch)
#
#
# def MsgAppGetUdpParamTest():
#     getUdpParam = MsgAppGetUdpParam()
#     print(client.sendSynMsg(getUdpParam))
#     print(getUdpParam)
#
#
# def MsgAppSetUdpParamTest():
#     setUdpParam = MsgAppSetUdpParam(0, ip="192.168.1.100", port=8168, period=100)
#     print(client.sendSynMsg(setUdpParam))
#
#
# def MsgAppGetHttpParamTest():
#     getHttpParam = MsgAppGetHttpParam()
#     print(client.sendSynMsg(getHttpParam))
#     print(getHttpParam)
#
#
# def MsgAppSetHttpParamTest():
#     setHttpParam = MsgAppSetHttpParam(1, period=5, timeout=5, reportAddress="http://192.168.1.168:1090/Report")
#     print(client.sendSynMsg(setHttpParam))
#
#
# # 5A00010129002A 01 0005 00 0005 00 01 0020 687474703A2F2F3139322E3136382E312E3136383A383039302F5265706F7274DB22
#
# # 转化成字符串(序列化)
# # name_dumps = json.dumps(name)
# # 转化成json格式(反序列化)
# # name01_loads = json.loads(name01)
# # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False：
# def MsgAppGetWifiHotspotSearchTest():
#     count = 0
#     while 1:
#         search = MsgAppGetWifiHotspotSearch(count)
#         if client.sendSynMsg(search)[0] == 0:
#             count += 1
#             if search.packetContent:
#                 # print(type(listToAscii(search.packetContent)))  # str
#                 result = loads(listToAscii(search.packetContent))  # type:dict
#                 print(result.items())
#             else:
#                 break
#
#
# def MsgAppSetWifiHotspotTest():
#     setWifiHotspot = MsgAppSetWifiHotspot("GX_5G", password="GX201909")
#     print(client.sendSynMsg(setWifiHotspot))
#
#
# def MsgAppGetWifiConnectStatusTest():
#     getWifiConnectStatus = MsgAppGetWifiConnectStatus()
#     print(client.sendSynMsg(getWifiConnectStatus))
#     print(getWifiConnectStatus)
#
#
# def MsgAppSetWifiIpTest():
#     setWifi = MsgAppSetWifiIp(1, ip="192.168.11.111", mask="255.255.255.0", gateway="192.168.11.1", dns1="192.168.11.1",
#                               dns2="0.0.0.0")
#     print(client.sendSynMsg(setWifi))
#
#
# def MsgAppGetWifiIpTest():
#     getWifi = MsgAppGetWifiIp(hotId=0)
#     print(client.sendSynMsg(getWifi))
#     print(getWifi)
#
#
# def MsgAppGetWifiSwitchTest():
#     getWifiSwitch = MsgAppGetWifiSwitch()
#     print(client.sendSynMsg(getWifiSwitch))
#     print(getWifiSwitch)
#
#
# def MsgAppSetWifiSwitchTest():
#     setWifiSwitch = MsgAppSetWifiSwitch(1)
#     print(client.sendSynMsg(setWifiSwitch))
#
#
# def MsgAppGetEasAlarmTest():
#     getEasAlarm = MsgAppGetEasAlarm()
#     print(client.sendSynMsg(getEasAlarm))
#     print(getEasAlarm)
#
#
# def MsgAppSetEasAlarmTest():
#     setEasAlarm = MsgAppSetEasAlarm(0, 0, 0, "1234", "FFFF", actionSuccess=ActionParamSuccess(1, gpo1=1),
#                                     actionFail=ActionParamFail(1, gpo2=0))
#     print(client.sendSynMsg(setEasAlarm))
#
#
# def MsgBaseGetCapabilitiesTest():
#     getCapabilities = MsgBaseGetCapabilities()
#     print(client.sendSynMsg(getCapabilities))
#     print(getCapabilities)
#
#
# def MsgBaseSetPowerTest():
#     dicPower = {"1": 20, "2": 20, "3": 21, "4": 23}
#     setPower = MsgBaseSetPower(**dicPower)
#     print(client.sendSynMsg(setPower))
#
#
# def MsgBaseGetPowerTest():
#     getPower = MsgBaseGetPower()
#     print(client.sendSynMsg(getPower))
#     print(getPower)
#
#
# def MsgBaseSetFreqRangeTest():
#     setFreqRange = MsgBaseSetFreqRange(3)
#     print(client.sendSynMsg(setFreqRange))
#
#
# def MsgBaseGetFreqRangeTest():
#     getFreqRange = MsgBaseGetFreqRange()
#     print(client.sendSynMsg(getFreqRange))
#     print(getFreqRange)
#
#
# def MsgBaseSetFrequencyTest():
#     fres = [0, 1, 2, 3, 4]
#     setFrequency = MsgBaseSetFrequency(0, *fres)
#     print(client.sendSynMsg(setFrequency))
#
#
# def MsgBaseGetFrequencyTest():
#     getFrequency = MsgBaseGetFrequency()
#     print(client.sendSynMsg(getFrequency))
#     print(getFrequency)
#
#
# def MsgBaseSetTagLogTest():
#     setTagLog = MsgBaseSetTagLog(repeatedTime=100)
#     print(client.sendSynMsg(setTagLog))
#
#
# def MsgBaseGetTagLogTest():
#     getTagLog = MsgBaseGetTagLog()
#     print(client.sendSynMsg(getTagLog))
#     print(getTagLog)
#
#
# def MsgBaseSetBasebandTest():
#     setBaseband = MsgBaseSetBaseband(baseSpeed=1, qValue=3, session=3, inventoryFlag=1)
#     print(client.sendSynMsg(setBaseband))
#
#
# def MsgBaseGetBasebandTest():
#     getBaseband = MsgBaseGetBaseband()
#     print(client.sendSynMsg(getBaseband))
#     print(getBaseband)
#
#
# def MsgBaseSetAutoDormancyTest():
#     setAutoDormancy = MsgBaseSetAutoDormancy(0, freeTime=10)
#     print(client.sendSynMsg(setAutoDormancy))
#
#
# def MsgBaseGetAutoDormancyTest():
#     getAutoDormancy = MsgBaseGetAutoDormancy()
#     print(client.sendSynMsg(getAutoDormancy))
#     print(getAutoDormancy)
#
#
# def MsgBaseInventoryEpcTest():
#     # epc_filter = ParamEpcFilter(0, 32, "1234")
#     inventoryEpc = MsgBaseInventoryEpc(1, 1, readTid=ParamEpcReadTid(0, 6), readUserData=ParamEpcReadUserData(0, 2),
#                                        readReserved=ParamEpcReadReserved(0, 2), hexPassword=None)
#     print(client.sendSynMsg(inventoryEpc))
#
#
# def MsgBaseWriteEpcTest():
#     temp = "2222"
#     hexData = getPcValue(temp) + temp
#     writeEpc = MsgBaseWriteEpc(1, 0, 2, hexData, hexPassword=None)
#     print(client.sendSynMsg(writeEpc))
#
#
# def MsgBaseLockEpcTest():
#     lockEpc = MsgBaseLockEpc(1, 1, 0, hexPassword="08002222")
#     print(client.sendSynMsg(lockEpc))
#
#
# def MsgBaseInventory6bEpcTest():
#     inventory6b = MsgBaseInventory6b(1, 1, 0, readUserData=Param6bReadUserData(0, 2))
#     print(client.sendSynMsg(inventory6b))
#
#
# def received6b(bInfo: LogBase6bInfo):
#     if bInfo.result == 0:
#         print(bInfo.tid)
#
#
# def call6bOver(bOver: LogBase6bOver):
#     print(bOver.rtMsg)
#
#
# def MsgBaseWrite6bTest():
#     write6b = MsgBaseWrite6b(1, "E004000030BCE808", 8, "ffff")
#     print(client.sendSynMsg(write6b))
#
#
# def MsgBaseLock6bGetTest():
#     lock6bGet = MsgBaseLock6bGet(1, "E004000030BCE808", 8)
#     print(client.sendSynMsg(lock6bGet))
#     print(lock6bGet.lockState)
#
#
# def MsgBaseInventoryGbTest():
#     inventoryGb = MsgBaseInventoryGb(1, 1)
#     print(client.sendSynMsg(inventoryGb))
#
#
# def receivedGb(gbInfo: LogBaseGbInfo):
#     if gbInfo.result == 0:
#         print(gbInfo.epc)
#
#
# def callGbOver(gbOver: LogBaseGbOver):
#     print(gbOver.rtMsg)
#
#
# def MsgBaseWriteGbTest():
#     temp = "2222"
#     hexData = getGbPcValue(temp) + temp
#     writeEpc = MsgBaseWriteGb(1, 0x10, 1, hexData, hexPassword=None)
#     print(client.sendSynMsg(writeEpc))
#
#
# if __name__ == '__main__':
#     try:
#         client = GClient()
#         client.callEpcInfo = receiveEpc
#         client.callEpcOver = callEpcOver
#         client.call6bInfo = received6b
#         client.call6bOver = call6bOver
#         client.callGbInfo = receivedGb
#         client.callGbOver = callGbOver
#         client.callDisconnected = callTcpDisconnect
#         stop = MsgBaseStop()
#         # if client.openTcp(("192.168.1.168", 8160)):
#         # if client.openSerial485(("COM7", 115200, 1), timeout=0):
#         # print(localtime())
#         # print(datetime.now())
#         # print(localtime())
#         # print(int(mktime(strptime(strftime("%Y-%m-%d %H:%M:%S", localtime()), "%Y-%m-%d %H:%M:%S"))))
#         if client.openSerial(("COM7", 115200), timeout=0):
#             print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
#             print("========================输入指定数字执行操作========================")
#             events = {0: MsgBaseStopTest, 1: MsgAppGetReaderInfoTest, 2: MsgAppSetSerialParamTest,
#                       3: MsgAppGetSerialParamTest, 4: MsgAppSetGpoTest, 5: MsgAppGetGpiStateTest,
#                       6: MsgAppSetEthernetIPTest, 7: MsgAppGetEthernetIPTest, 8: MsgAppGetReaderMacTest,
#                       9: MsgAppSetTcpModeTest, 10: MsgAppGetTcpModeTest, 11: MsgAppSetGpiTriggerTest,
#                       12: MsgAppGetGpiTriggerTest, 13: MsgAppSetWiegandTest, 14: MsgAppGetWiegandTest,
#                       15: MsgAppResetTest, 16: MsgAppSetReaderTimeTest, 17: MsgAppGetReaderTimeTest,
#                       18: MsgAppRestoreDefaultTest, 19: MsgAppSetRs485Test, 20: MsgAppGetRs485Test,
#                       21: MsgAppSetBreakpointResumeTest, 22: MsgAppGetBreakpointResumeTest,
#                       23: MsgAppGetCacheTagDataTest, 24: MsgAppClearCacheDataTest, 25: MsgAppTagDataReplyTest,
#                       26: MsgAppSetBeepOnOffTest, 27: MsgAppSetBeepTest, 28: MsgAppGetWhiteListTest,
#                       29: MsgAppDelWhiteListTest, 30: MsgAppSetWhiteListActionTest, 31: MsgAppGetWhiteListActionTest,
#                       32: MsgAppGetWhiteListSwitchTest, 33: MsgAppSetWhiteListSwitchTest, 34: MsgAppSetUdpParamTest,
#                       35: MsgAppGetUdpParamTest, 36: MsgAppGetHttpParamTest, 37: MsgAppSetHttpParamTest,
#                       38: MsgAppGetWifiHotspotSearchTest, 39: MsgAppSetWifiHotspotTest,
#                       40: MsgAppGetWifiConnectStatusTest, 41: MsgAppSetWifiIpTest, 42: MsgAppGetWifiIpTest,
#                       43: MsgAppGetWifiSwitchTest, 44: MsgAppSetWifiSwitchTest, 45: MsgAppGetEasAlarmTest,
#                       46: MsgAppSetEasAlarmTest, 47: MsgBaseGetCapabilitiesTest, 48: MsgBaseSetPowerTest,
#                       49: MsgBaseGetPowerTest, 50: MsgBaseSetFreqRangeTest, 51: MsgBaseGetFreqRangeTest,
#                       52: MsgBaseSetFrequencyTest, 53: MsgBaseGetFrequencyTest, 54: MsgBaseSetTagLogTest,
#                       55: MsgBaseGetTagLogTest, 56: MsgBaseSetBasebandTest, 57: MsgBaseGetBasebandTest,
#                       58: MsgBaseSetAutoDormancyTest, 59: MsgBaseGetAutoDormancyTest, 60: MsgBaseInventoryEpcTest,
#                       61: MsgBaseWriteEpcTest, 62: MsgBaseLockEpcTest, 63: MsgBaseInventory6bEpcTest,
#                       64: MsgBaseWrite6bTest, 65: MsgBaseLock6bGetTest, 66: MsgBaseInventoryGbTest}
#             for key, value in events.items():
#                 print(key, "-", value.__name__, end="\t\t")
#                 if key % 5 == 0 and key != 0:
#                     print()
#             while True:
#                 s = input()
#                 if s.isdigit():
#                     if int(s) in events:
#                         events[int(s)].__call__()
#
#             # print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
#
#
#
#     except Exception as ex:
#         raise ex
#         # print(ex.args)
#
#         # raise ex
