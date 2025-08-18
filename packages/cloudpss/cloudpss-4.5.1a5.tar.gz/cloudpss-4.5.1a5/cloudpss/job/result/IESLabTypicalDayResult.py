from .IESResult import IESResult
import re
import copy
class IESLabTypicalDayResult(IESResult):
    
    def __init__(self, *args, **kwargs):
        """
            初始化
        """
        IESResult.__init__(self, *args, **kwargs)
        self.__plotIndex = 0
        self.__typicalIndex = 0
        self.__type_list =['电负荷', '热负荷','冷负荷','总辐射','散射辐射', '直射辐射',  '天顶角', '环境温度', '土壤温度', '10m风速', '50m风速', '建筑物高度风速', '风机高度风速']
        self.result = {'TypicalMonth': [],'TypicalDay': []}
        for i in range(12):
            self.result['TypicalMonth'].append({'月份': int, '持续天数': [],'电负荷': [], '热负荷': [],'冷负荷':[],'总辐射': [],'直射辐射': [],'散射辐射': [],'天顶角': [],
                                                '环境温度': [], '土壤温度': [], '建筑物高度风速': [], '风机高度风速': [],'10m风速': [], '50m风速': [] })
    def __readPlotResult(self):
        length = self.getMessageLength()
        if (length > self.__plotIndex):
            for num in range(self.__plotIndex, length):# update TypicalMonth
                val = self.getMessage(num)
                if val['type'] == 'plot':
                    key_list = re.split('-month',val['key'])#分别为类型和月份
                    # print(key_list)
                    self.result['TypicalMonth'][int(key_list[1])-1]['月份'] = int(key_list[1])
                    if key_list[0] in ['总辐射','散射辐射']:#从第一类数据中分析每个月各个典型日的天数
                        typicalNum = len(val['data']['traces'])
                        for i in range(typicalNum):
                            self.result['TypicalMonth'][int(key_list[1])-1]['持续天数'].append(int(re.findall('\d+',val['data']['traces'][i]['name'])[1]))
                    # 每个月各类型数据的各个典型日的数据，由于部分月份可能没有电冷热负荷，某月的某个典型日可能缺少冷热负荷
                    for i in range(typicalNum):
                        self.result['TypicalMonth'][int(key_list[1])-1][key_list[0]].append([])
                    for i in range(len(val['data']['traces'])):
                        self.result['TypicalMonth'][int(key_list[1])-1][key_list[0]][int(re.findall('\d+',val['data']['traces'][i]['name'])[0])-1] = copy.deepcopy(val['data']['traces'][i]['y'])
            self.__plotIndex = length
            # update TypicalDay based on TypicalMonth
            for m in range(12):
                for i in range(len(self.result['TypicalMonth'][m]['持续天数'])):
                    self.result['TypicalDay'].append({'info':{'typicalDayID': int, 'name': str, 'duration': int, 'maxElectricalLoad': 0.0, 'maxHeatLoad': 0.0, 'maxCoolLoad': 0.0}, 
                                                      'data': {'电负荷': [], '热负荷': [],'冷负荷':[],'总辐射': [],'直射辐射': [],'散射辐射': [],'天顶角': [],
                                                               '环境温度': [], '土壤温度': [], '建筑物高度风速': [], '风机高度风速': [],'10m风速': [], '50m风速': []}})
                    self.result['TypicalDay'][-1]['info']['typicalDayID'] = self.__typicalIndex
                    self.result['TypicalDay'][-1]['info']['name'] = str(m+1) + '月典型日' + str(i+1)
                    self.result['TypicalDay'][-1]['info']['duration'] = self.result['TypicalMonth'][m]['持续天数'][i]
                    if self.result['TypicalMonth'][m]['电负荷']:
                        if self.result['TypicalMonth'][m]['电负荷'][i]:
                            self.result['TypicalDay'][-1]['info']['maxElectricalLoad'] = max(self.result['TypicalMonth'][m]['电负荷'][i])
                    if self.result['TypicalMonth'][m]['热负荷']:
                        if self.result['TypicalMonth'][m]['热负荷'][i]:
                            self.result['TypicalDay'][-1]['info']['maxHeatLoad'] = max(self.result['TypicalMonth'][m]['热负荷'][i])
                    if self.result['TypicalMonth'][m]['冷负荷']:
                        if self.result['TypicalMonth'][m]['冷负荷'][i]:
                            self.result['TypicalDay'][-1]['info']['maxCoolLoad'] = max(self.result['TypicalMonth'][m]['冷负荷'][i])
                    for type_i in self.__type_list:
                        if self.result['TypicalMonth'][m][type_i]:
                            self.result['TypicalDay'][-1]['data'][type_i] = self.result['TypicalMonth'][m][type_i][i]
                    self.__typicalIndex += 1
    def GetTypical(self):
        '''
            获取所有的 GetTypical 典型日数据

            >>> result.GetTypical()
            {...}
        '''
        self.__readPlotResult()
        return self.result['TypicalDay']
    def GetTypicalDayNum(self):
        '''
            获取当前result的典型日数量
            
            :return: int类型，代表典型日数量
        '''
        
        self.__readPlotResult()
        return self.__typicalIndex
    def GetTypicalDayInfo(self,dayID):
        '''
            获取dayID对应典型日的基础信息
            
            :params: dayID int类型，表示典型日的ID，数值位于 0~典型日数量 之间
            
            :return: dict类型，代表典型日的基础信息，包括典型日所代表的日期范围、典型日的名称等
        '''
        self.__readPlotResult()
        return self.result['TypicalDay'][dayID].get('info','没有该数据')
        
    def GetTypicalDayCurve(self,dayID, dataType):
        '''
            获取dayID对应典型日下dataType参数的时序曲线
            
            :params: dayID int类型，表示典型日的ID，数值位于 0~典型日数量 之间
            :params: dataType enum类型，标识辐照强度、环境温度、土壤温度、建筑物高度风速、风机高度风速、电负荷、热负荷、冷负荷的参数类型
            
            :return: list<float>类型，代表以1h为时间间隔的该参数的日内时序曲线
        '''
        self.__readPlotResult()
        return self.result['TypicalDay'][dayID]['data'].get(dataType,'没有该类型数据')
    
    def GetTypicalMonth(self):
        '''
            获取所有的 GetTypicalMonth 数据
            
            >>> result.GetTypicalMonth()
            
            :return: list<dict>类型，代表各月各类型的典型日数据
        '''
        self.__readPlotResult()
        return self.result['TypicalMonth']
    
    def GetTypicalMonthNum(self,monthID):
        '''
            获取第monthID月各类型的典型日数据

            >>> result.GetTypicalMonthNum()
            
            :params: monthID int类型，表示典型月的ID，数值位于 1-12 之间

            :return: dict类型，代表第monthID月各类型的典型日数据
            {...}
        '''
        self.__readPlotResult()
        return self.result['TypicalMonth'][monthID-1]
        
    
    def GetTypicalMonthCurve(self,monthID, dataType):
        '''
            获取dayID对应典型日下dataType参数的时序曲线
            
            :params: monthID int类型，表示典型月的ID，数值位于 1-12 之间
            :params: dataType enum类型，标识总辐射、环境温度、土壤温度、建筑物高度风速、风机高度风速、电负荷、热负荷、冷负荷的参数类型
            
            :return: list<list>类型，代表以1h为时间间隔的该参数的典型日内时序曲线
        '''
        self.__readPlotResult()
        return self.result['TypicalMonth'][monthID-1].get(dataType,'没有该类型数据')