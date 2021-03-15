import os, re, time, json
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import admininfo as a_i
from .models import useritemsinfo as u_i_i
from .models import iteminfo as i_i
from .models import itemchangeinfo as i_c_i
from .models import itemstock as i_s


class getItemInfo:
    """
    回传资产列表信息
    
    """
    def __init__(self, **kwds):
        self.pageSep = kwds['pageSep']
        self.name = kwds['name']
        self.num = kwds['num']

    def getItemInfoData(self):
        try:            
            test = i_i.objects.all().exists()            
            if test:
                gII = i_i.objects.all().order_by( '-item_inbound_date' )
                paginator = Paginator(gII, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    print('num', self.num)
                    number = paginator.page(self.num)
                    print(number.object_list)                    
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                ItemInfoData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
            else:
                ItemInfoDataList = []
                paginator = Paginator(ItemInfoDataList, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                info = '暂时没有IT资产'
                ItemInfoData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
                ItemInfoData['userinfo']['info'] = info
        except:
            pass
        return ItemInfoData

class getSearchItemSn(getItemInfo):
    """
    回传搜索资产SN/名称的结果列表信息
    
    """
    def __init__(self, **kwds):
        getItemInfo.__init__(self,  pageSep = kwds['pageSep'], name = kwds['name'], num = kwds['num'])
        self.SearchSn = kwds['SearchSn']

    def getSearchItemSnData(self):
        try:
            testSnExists = i_i.objects.filter(Q(item_name__icontains=self.SearchSn)|Q(item_sn__icontains=self.SearchSn)|
                                              Q(item_now_user__icontains=self.SearchSn)|Q(item_now_user_workid__icontains=self.SearchSn)|
                                              Q(item_statu__icontains=self.SearchSn)|Q(item_location__icontains=self.SearchSn)|
                                              Q(item_kind__icontains=self.SearchSn)).exists()
            if testSnExists:
                snII = i_i.objects.filter(Q(item_name__icontains=self.SearchSn)|Q(item_sn__icontains=self.SearchSn)|
                                          Q(item_now_user__icontains=self.SearchSn)|Q(item_now_user_workid__icontains=self.SearchSn)|
                                          Q(item_statu__icontains=self.SearchSn)|Q(item_location__icontains=self.SearchSn)|
                                          Q(item_kind__icontains=self.SearchSn)).order_by( '-item_inbound_date' )
                paginator = Paginator(snII, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)                   
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                SearchItemSnData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
            else:
                SearchItemSnDataList = []
                paginator = Paginator(SearchItemSnDataList, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                info = '没有搜索到相关IT资产'
                SearchItemSnData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
                SearchItemSnData['userinfo']['info'] = info
        except:
            pass
        return SearchItemSnData


class DeleteItemInfo(getItemInfo):
    """
    删除资产信息

    """
    def __init__(self, **kwds):
        getItemInfo.__init__(self,  pageSep = kwds['pageSep'], name = kwds['name'], num = kwds['num'])
        self.item_sn = kwds['item_sn']
        self.item_now_user_workid = kwds['item_now_user_workid']

    def DeleteItemInfoData(self):
        try:
            oldItemLocation = i_i.objects.get( item_sn = self.item_sn ).item_location   # 资产原所在位置
            passUserItemRec = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = oldItemLocation )[0]    # 删除用户表里的设备信息
            editingPassUserItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
            if editingPassUserItemKind == '手机':
                old_user_phone_sn_list = passUserItemRec.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                old_user_phone_sn_list_new = old_user_phone_sn_list.split(',')
                old_user_phone_sn_list_new.remove(self.item_sn)
                try:
                    old_user_phone_sn_list_new.remove('')
                except:
                    pass
                passUserItemRec.user_phone_sn = old_user_phone_sn_list_new
            if editingPassUserItemKind == '手机号码':
                old_user_phone_num_list = passUserItemRec.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                old_user_phone_num_list_new = old_user_phone_num_list.split(',')
                old_user_phone_num_list_new.remove(self.item_sn)
                try:
                    old_user_phone_num_list_new.remove('')
                except:
                    pass
                passUserItemRec.user_phone_num = old_user_phone_num_list_new
            if editingPassUserItemKind == 'pad':
                old_user_pad_sn_list = passUserItemRec.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                old_user_pad_sn_list_new = old_user_pad_sn_list.split(',')
                old_user_pad_sn_list_new.remove(self.item_sn)
                try:
                    old_user_pad_sn_list_new.remove('')
                except:
                    pass
                passUserItemRec.user_pad_sn = old_user_pad_sn_list_new
            if editingPassUserItemKind == '微信号':
                old_user_wechat_name_list = passUserItemRec.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                old_user_wechat_name_list_new = old_user_wechat_name_list.split(',')
                old_user_wechat_name_list_new.remove(self.item_sn)
                try:
                    old_user_wechat_name_list_new.remove('')
                except:
                    pass
                passUserItemRec.user_wechat_name = old_user_wechat_name_list_new
            if editingPassUserItemKind == '千牛账号':
                old_user_qianniu_name_list = passUserItemRec.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                old_user_qianniu_name_list_new = old_user_qianniu_name_list.split(',')
                old_user_qianniu_name_list_new.remove(self.item_sn)
                try:
                    old_user_qianniu_name_list_new.remove('')
                except:
                    pass
                passUserItemRec.user_qianniu_name = old_user_qianniu_name_list_new
            if editingPassUserItemKind == '其他':
                old_user_otheritems_list = passUserItemRec.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                old_user_otheritems_list_new = old_user_otheritems_list.split(',')
                old_user_otheritems_list_new.remove(self.item_sn)
                try:
                    old_user_otheritems_list_new.remove('')
                except:
                    pass
                passUserItemRec.user_otheritems = old_user_otheritems_list_new
            if editingPassUserItemKind == '台式电脑':
                passUserItemRec.user_pc_sn = ''
            if editingPassUserItemKind == '笔记本电脑':
                passUserItemRec.user_notebook_sn = ''
            passUserItemRec.save()
            try:
                editingItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                item_location = i_i.objects.get( item_sn = self.item_sn ).item_location
                item_statu = i_i.objects.get( item_sn = self.item_sn ).item_statu
                q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = item_location )[0] # 更新该部门闲置物资库存
                if item_statu == '闲置':                    
                    item_stock_num_now = q_i_s.item_stock_num - 1
                    q_i_s.item_stock_num = item_stock_num_now
                    q_i_s.save()
            except:
                pass
            q_i_i = i_i.objects.get( item_sn = self.item_sn )
            q_i_i.delete()
            info = '{}已删除！'.format(self.item_sn)                              
            getDeleteItemInfoView = getItemInfo(pageSep = self.pageSep, name = self.name, num = self.num)
            getDeleteItemInfoData = getDeleteItemInfoView.getItemInfoData()
            getDeleteItemInfoData['userinfo']['info'] = info
            print(getDeleteItemInfoData)
            return getDeleteItemInfoData
        except:  # 删除原状态为报废的资产
            try:
                editingItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                item_location = i_i.objects.get( item_sn = self.item_sn ).item_location
                item_statu = i_i.objects.get( item_sn = self.item_sn ).item_statu
                q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = item_location )[0] # 更新该部门闲置物资库存   
                item_destory_num_now = q_i_s.item_destory_num - 1
                q_i_s.item_destory_num = item_destory_num_now
                q_i_s.save()
                q_i_i = i_i.objects.get( item_sn = self.item_sn )
                q_i_i.delete()
            except:
                pass
            info = '{}已删除！'.format(self.item_sn)                              
            getDeleteItemInfoView = getItemInfo(pageSep = self.pageSep, name = self.name, num = self.num)
            getDeleteItemInfoData = getDeleteItemInfoView.getItemInfoData()
            getDeleteItemInfoData['userinfo']['info'] = info
            print(getDeleteItemInfoData)
            return getDeleteItemInfoData



class AddedItemInfo(getItemInfo):
    """
    增加资产信息

    """
    def __init__(self, **kwds):
        getItemInfo.__init__(self,  pageSep = kwds['pageSep'], name = kwds['name'], num = kwds['num'])
        self.item_inbound_date = kwds['item_inbound_date']
        self.item_name = kwds['item_name']
        self.item_kind = kwds['item_kind']
        self.item_sn = kwds['item_sn']
        self.item_now_user = kwds['item_now_user']
        self.item_now_user_workid = kwds['item_now_user_workid']
        self.item_statu = kwds['item_statu']
        self.item_location = kwds['item_location']
        self.item_info = kwds['item_info']

    def AddedItemInfoData(self):
        try:
            u_i_i.objects.filter(user_name = '').filter(user_location = self.item_location)[0]  # 判读资产所在位置是否有无空用户记录
        except:
            initialNoneUserItemRec = u_i_i( user_name = '', user_location = self.item_location)   # 初始化资产所在位置空用户记录
            initialNoneUserItemRec.save() 
        try:
            i_i.objects.get( item_sn = self.item_sn) # 判断资产信息表里有无该资产的唯一编码或号码
            info = '{} 资产编号/号码已存在'.format(self.item_sn)
            getItemInfoView = getItemInfo(pageSep = self.pageSep, name = self.name, num = self.num)
            getItemInfoData = getItemInfoView.getItemInfoData()
            getItemInfoData['userinfo']['info'] = info
            return getItemInfoData
        except:                        
            try:
                uii = u_i_i.objects.filter( user_workid = self.item_now_user_workid )[0]  # 利用工号判断用户资产表里有无该员工记录
                print('nowworkid', self.item_now_user_workid)
                if self.item_kind != '台式电脑' and self.item_kind != '笔记本电脑':   # 每名员工名下只能有一台台式电脑或笔记本，所以单独拎出来
                    try:
                        i_s.objects.filter( item_kind = self.item_kind )[0]  # 判断库存表里有无该类型资产               
                        test = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location ).exists()
                        item_stock_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_stock_num
                        item_destory_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_destory_num
                        if test:
                            qis = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0]
                            if self.item_statu == '闲置':
                                item_stock_num = item_stock_num + 1                        
                                qis.item_stock_num = item_stock_num
                            if self.item_statu == '报废':
                                item_destory_num = item_destory_num + 1
                                qis.item_destory_num = item_destory_num
                            qis.save()
                        else:
                            if self.item_statu == '在用':
                                Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                            if self.item_statu == '闲置':
                                item_stock_num = item_stock_num + 1
                                Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                            if self.item_statu == '报废':
                                item_destory_num = item_destory_num + 1
                                Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                            Saveitemstock.save()
                    except:            
                        if self.item_statu == '在用':
                            Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 0)
                        if self.item_statu == '闲置':
                            Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 1, item_destory_num = 0)
                        if self.item_statu == '报废':
                            Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 1)
                        Saveitemstock.save()
                    SaveItemInfo = i_i(item_inbound_date = self.item_inbound_date, item_name = self.item_name, item_kind = self.item_kind, item_sn = self.item_sn, 
                                item_now_user = self.item_now_user, item_now_user_workid = self.item_now_user_workid, item_statu = self.item_statu,
                                item_location = self.item_location, item_info = self.item_info)
                    SaveItemInfo.save()
                    if self.item_kind == '手机':
                        user_phone_sn_list = uii.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        user_phone_sn_list_new = user_phone_sn_list.split(',')
                        user_phone_sn_list_new.append(self.item_sn)
                        try:
                            user_phone_sn_list_new.remove('')
                        except:
                            pass
                        uii.user_phone_sn = user_phone_sn_list_new
                        info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                    if self.item_kind == '手机号码':
                        user_phone_num_list = uii.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        user_phone_num_list_new = user_phone_num_list.split(',')
                        user_phone_num_list_new.append(self.item_sn)
                        try:
                            user_phone_num_list_new.remove('')
                        except:
                            pass
                        uii.user_phone_num = user_phone_num_list_new
                        info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                    if self.item_kind == 'pad':
                        user_pad_sn_list = uii.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        user_pad_sn_list_new = user_pad_sn_list.split(',')
                        user_pad_sn_list_new.append(self.item_sn)
                        try:
                            user_pad_sn_list_new.remove('')
                        except:
                            pass
                        uii.user_pad_sn = user_pad_sn_list_new
                        info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                    if self.item_kind == '微信号':
                        user_wechat_name_list = uii.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        user_wechat_name_list_new = user_wechat_name_list.split(',')
                        user_wechat_name_list_new.append(self.item_sn)
                        try:
                            user_wechat_name_list_new.remove('')
                        except:
                            pass
                        uii.user_wechat_name = user_wechat_name_list_new
                        info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                    if self.item_kind == '千牛账号':
                        user_qianniu_name_list = uii.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        user_qianniu_name_list_new = user_qianniu_name_list.split(',')
                        user_qianniu_name_list_new.append(self.item_sn)
                        try:
                            user_qianniu_name_list_new.remove('')
                        except:
                            pass
                        uii.user_qianniu_name = user_qianniu_name_list_new
                        info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                    if self.item_kind == '其他':
                        user_otheritems_list = uii.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        user_otheritems_list_new = user_otheritems_list.split(',')
                        user_otheritems_list_new.append(self.item_sn)
                        try:
                            user_otheritems_list_new.remove('')
                        except:
                            pass
                        uii.user_otheritems = user_otheritems_list_new
                        info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                if self.item_kind == '台式电脑':
                    try:   # 判断该员工是否已经有台式电脑
                        pcTest = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_location )[0].user_pc_sn
                        if pcTest != '' and ( self.item_now_user != '' and self.item_now_user_workid != ''): # 空名可以挂多台电脑
                            info = '{}员工已经有台式电脑'.format(self.item_now_user_workid)                            
                        if (pcTest == '' or pcTest != '') and (self.item_now_user == '' or self.item_now_user_workid == ''):
                            uii = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_location )[0]
                            user_pc_list = uii.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            user_pc_list_new = user_pc_list.split(',')
                            user_pc_list_new.append(self.item_sn)
                            try:
                                user_pc_list_new.remove('')
                            except:
                                pass
                            uii.user_pc_sn = user_pc_list_new
                            info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                            SaveItemInfo = i_i(item_inbound_date = self.item_inbound_date, item_name = self.item_name, item_kind = self.item_kind, item_sn = self.item_sn, 
                                item_now_user = self.item_now_user, item_now_user_workid = self.item_now_user_workid, item_statu = self.item_statu,
                                item_location = self.item_location, item_info = self.item_info)
                            SaveItemInfo.save()
                            try:
                                i_s.objects.filter( item_kind = self.item_kind )[0]  # 判断库存表里有无该类型资产               
                                test = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location ).exists()
                                item_stock_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_stock_num
                                item_destory_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_destory_num
                                if test:
                                    qis = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0]
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1                        
                                        qis.item_stock_num = item_stock_num
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        qis.item_destory_num = item_destory_num
                                    qis.save()
                                else:
                                    if self.item_statu == '在用':
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    Saveitemstock.save()
                            except:            
                                if self.item_statu == '在用':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 0)
                                if self.item_statu == '闲置':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 1, item_destory_num = 0)
                                if self.item_statu == '报废':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 1)
                                Saveitemstock.save()
                        if pcTest == '' and ( self.item_now_user != '' and self.item_now_user_workid != ''):
                            uii.user_pc_sn = self.item_sn
                            info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                            SaveItemInfo = i_i(item_inbound_date = self.item_inbound_date, item_name = self.item_name, item_kind = self.item_kind, item_sn = self.item_sn, 
                                item_now_user = self.item_now_user, item_now_user_workid = self.item_now_user_workid, item_statu = self.item_statu,
                                item_location = self.item_location, item_info = self.item_info)
                            SaveItemInfo.save()
                            try:
                                i_s.objects.filter( item_kind = self.item_kind )[0]  # 判断库存表里有无该类型资产               
                                test = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location ).exists()
                                item_stock_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_stock_num
                                item_destory_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_destory_num
                                if test:
                                    qis = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0]
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1                        
                                        qis.item_stock_num = item_stock_num
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        qis.item_destory_num = item_destory_num
                                    qis.save()
                                else:
                                    if self.item_statu == '在用':
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    Saveitemstock.save()
                            except:            
                                if self.item_statu == '在用':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 0)
                                if self.item_statu == '闲置':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 1, item_destory_num = 0)
                                if self.item_statu == '报废':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 1)
                                Saveitemstock.save()
                    except:
                        pass
                if self.item_kind == '笔记本电脑':
                    try:   # 判断该员工是否已经有台式电脑
                        notebookTest = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_location )[0].user_notebook_sn
                        if notebookTest != '' and ( self.item_now_user != '' and self.item_now_user_workid != ''): # 空名可以挂多台电脑
                            info = '{}员工已经有笔记本电脑'.format(self.item_now_user_workid)
                        if (notebookTest == '' or notebookTest != '') and (self.item_now_user == '' or self.item_now_user_workid == ''):
                            uii = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_location )[0]
                            user_notebook_list = uii.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            user_notebook_list_new = user_notebook_list.split(',')
                            user_notebook_list_new.append(self.item_sn)
                            try:
                                user_notebook_list_new.remove('')
                            except:
                                pass
                            uii.user_notebook_sn = user_notebook_list_new
                            info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                            SaveItemInfo = i_i(item_inbound_date = self.item_inbound_date, item_name = self.item_name, item_kind = self.item_kind, item_sn = self.item_sn, 
                                item_now_user = self.item_now_user, item_now_user_workid = self.item_now_user_workid, item_statu = self.item_statu,
                                item_location = self.item_location, item_info = self.item_info)
                            SaveItemInfo.save()
                            try:
                                i_s.objects.filter( item_kind = self.item_kind )[0]  # 判断库存表里有无该类型资产               
                                test = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location ).exists()
                                item_stock_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_stock_num
                                item_destory_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_destory_num
                                if test:
                                    qis = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0]
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1                        
                                        qis.item_stock_num = item_stock_num
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        qis.item_destory_num = item_destory_num
                                    qis.save()
                                else:
                                    if self.item_statu == '在用':
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    Saveitemstock.save()
                            except:            
                                if self.item_statu == '在用':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 0)
                                if self.item_statu == '闲置':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 1, item_destory_num = 0)
                                if self.item_statu == '报废':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 1)
                                Saveitemstock.save()
                        if notebookTest == '' and ( self.item_now_user != '' and self.item_now_user_workid != ''):
                            uii.user_notebook_sn = self.item_sn
                            info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                            SaveItemInfo = i_i(item_inbound_date = self.item_inbound_date, item_name = self.item_name, item_kind = self.item_kind, item_sn = self.item_sn, 
                                item_now_user = self.item_now_user, item_now_user_workid = self.item_now_user_workid, item_statu = self.item_statu,
                                item_location = self.item_location, item_info = self.item_info)
                            SaveItemInfo.save()
                            try:
                                i_s.objects.filter( item_kind = self.item_kind )[0]  # 判断库存表里有无该类型资产               
                                test = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location ).exists()
                                item_stock_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_stock_num
                                item_destory_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_destory_num
                                if test:
                                    qis = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0]
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1                        
                                        qis.item_stock_num = item_stock_num
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        qis.item_destory_num = item_destory_num
                                    qis.save()
                                else:
                                    if self.item_statu == '在用':
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '闲置':
                                        item_stock_num = item_stock_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    if self.item_statu == '报废':
                                        item_destory_num = item_destory_num + 1
                                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                                    Saveitemstock.save()
                            except:            
                                if self.item_statu == '在用':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 0)
                                if self.item_statu == '闲置':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 1, item_destory_num = 0)
                                if self.item_statu == '报废':
                                    Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 1)
                                Saveitemstock.save()
                    except:
                        pass
                uii.save()
                
            except:
                SaveItemInfo = i_i(item_inbound_date = self.item_inbound_date, item_name = self.item_name, item_kind = self.item_kind, item_sn = self.item_sn, 
                            item_now_user = self.item_now_user, item_now_user_workid = self.item_now_user_workid, item_statu = self.item_statu,
                            item_location = self.item_location, item_info = self.item_info)
                SaveItemInfo.save()
                try:
                    i_s.objects.filter( item_kind = self.item_kind )[0]  # 判断库存表里有无该类型资产              
                    test = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location ).exists()
                    item_stock_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_stock_num
                    item_destory_num = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0].item_destory_num
                    if test:
                        qis = i_s.objects.filter( item_kind = self.item_kind ).filter( item_stock_location = self.item_location )[0]
                        if self.item_statu == '闲置':
                            item_stock_num = item_stock_num + 1                        
                            qis.item_stock_num = item_stock_num
                        if self.item_statu == '报废':
                            item_destory_num = item_destory_num + 1
                            qis.item_destory_num = item_destory_num
                        qis.save()
                    else:
                        if self.item_statu == '在用':
                            Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                        if self.item_statu == '闲置':
                            item_stock_num = item_stock_num + 1
                            Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                        if self.item_statu == '报废':
                            item_destory_num = item_destory_num + 1
                            Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = item_stock_num, item_destory_num = item_destory_num)
                        Saveitemstock.save()
                except:            
                    if self.item_statu == '在用':
                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 0)
                    if self.item_statu == '闲置':
                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 1, item_destory_num = 0)
                    if self.item_statu == '报废':
                        Saveitemstock = i_s(item_kind = self.item_kind, item_stock_location = self.item_location, item_stock_num = 0, item_destory_num = 1)
                    Saveitemstock.save()
                if self.item_kind == '手机':
                    phone_sn = self.item_sn
                    user_phone_sn = [phone_sn]
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_phone_sn = user_phone_sn )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                if self.item_kind == '手机号码':
                    phone_num = self.item_sn
                    user_phone_num = [phone_num]
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_phone_num = user_phone_num )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)                          
                if self.item_kind == 'pad':
                    pad_sn = self.item_sn
                    user_pad_sn = [pad_sn]
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_pad_sn = user_pad_sn )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)                          
                if self.item_kind == '微信号':
                    wechat_name = self.item_sn
                    user_wechat_name = [wechat_name]
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_wechat_name = user_wechat_name )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)                          
                if self.item_kind == '千牛账号':
                    qianniu_name = self.item_sn
                    user_qianniu_name = [qianniu_name]
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_qianniu_name = user_qianniu_name )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)                          
                if self.item_kind == '其他':
                    otheritems = self.item_sn
                    user_otheritems = [otheritems]
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_otheritems = user_otheritems )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)                          
                if self.item_kind == '台式电脑':
                    if self.item_now_user == '' or self.item_now_user_workid == '':
                        user_pc = self.item_sn
                        user_pc_sn = [user_pc]
                    else:
                        user_pc_sn = self.item_sn
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_pc_sn = user_pc_sn )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                if self.item_kind == '笔记本电脑':
                    if self.item_now_user == '' or self.item_now_user_workid == '':
                        user_notebook = self.item_sn
                        user_notebook_sn = [user_notebook]
                    else:
                        user_notebook_sn = self.item_sn
                    Saveuseritemsinfo = u_i_i(user_name = self.item_now_user, user_workid = self.item_now_user_workid, user_location = self.item_location,
                                                user_notebook_sn = user_notebook_sn )
                    info = '{} 资产，编号/号码 {} 已添加'.format(self.item_name, self.item_sn)
                Saveuseritemsinfo.save()                                     
        getItemInfoView = getItemInfo(pageSep = self.pageSep, name = self.name, num = self.num)
        getItemInfoData = getItemInfoView.getItemInfoData()
        getItemInfoData['userinfo']['info'] = info
        print(getItemInfoData)
        return getItemInfoData
        

class getItemDetail:
    """
    回传IT资产详细信息

    """
    def __init__(self, **kwds):
        self.name = kwds['name']
        self.item_sn = kwds['item_sn']

    def getItemDetailData(self):
        try:
            iDD = i_i.objects.get( item_sn = self.item_sn )
            item_name = iDD.item_name
            item_pass_user = iDD.item_now_user
            item_info = iDD.item_info
            item_statu = iDD.item_statu
            item_location = iDD.item_location
            item_pass_user_workid = iDD.item_now_user_workid
            ItemDetaiData = {'userinfo': {'name': self.name,
                                 'item_sn': self.item_sn,
                                 'item_name': item_name,
                                 'item_pass_user': item_pass_user, 
                                 'item_info': item_info,
                                 'item_statu': item_statu,
                                 'item_location': item_location,
                                 'item_pass_user_workid': item_pass_user_workid}}
        except:
            pass
        return ItemDetaiData

class getModedItemInfo(getItemDetail):
    """
    回传修改后的IT资产详细信息

    """
    def __init__(self, **kwds):
        getItemDetail.__init__(self, name = kwds['name'], item_sn = kwds['item_sn'])
        self.item_change_date = kwds['item_change_date']
        self.item_statu = kwds['item_statu']
        self.item_change_location = kwds['item_change_location']
        self.item_now_user = kwds['item_now_user']
        self.item_now_user_workid = kwds['item_now_user_workid']
        self.item_pass_user_workid = kwds['item_pass_user_workid']
        self.item_change_info = kwds['item_change_info']

    def getModedItemsData(self):
        try:
            OldItemDetailView = getItemDetail(name = self.name, item_sn = self.item_sn)
            OldItemDetailData = OldItemDetailView.getItemDetailData()
            q_i_i = i_i.objects.get( item_sn = self.item_sn )
            oldItemLocation = q_i_i.item_location
            try:
                passUserItemRec = u_i_i.objects.get( user_workid = self.item_pass_user_workid )
            except:
                try:
                    passUserItemRec = u_i_i.objects.filter( user_workid = self.item_pass_user_workid ).filter( user_location = oldItemLocation )[0]
                except:
                    pass
            try: 
                nowUserItemRec = u_i_i.objects.get( user_workid = self.item_now_user_workid )
            except:
                try:
                    nowUserItemRec  = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_change_location )[0]
                except:
                    pass
            if self.item_statu == '在用':
                editingItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind                
                if editingItemKind != '台式电脑' and editingItemKind != '笔记本电脑':
                    s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                    item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                    item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                    s.save()  # 更新资产变更表
                    q_i_i = i_i.objects.get( item_sn = self.item_sn )
                    item_old_location = q_i_i.item_location
                    q_i_i.item_statu = self.item_statu
                    q_i_i.item_location = self.item_change_location
                    q_i_i.item_now_user = self.item_now_user
                    q_i_i.item_now_user_workid = self.item_now_user_workid
                    q_i_i.item_info = self.item_change_info
                    q_i_i.save()
                    if OldItemDetailData['userinfo']['item_statu'] == '闲置':
                        old_i_s =  i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = item_old_location )[0]                   
                        item_stock_num_now = old_i_s.item_stock_num - 1
                        old_i_s.item_stock_num = item_stock_num_now
                        old_i_s.save()
                    try:                    
                        q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存                        
                    except:  # 无库存则生成库存记录
                        Saveitemstock = i_s(item_kind = editingItemKind, item_stock_location = self.item_change_location, item_stock_num = 0, item_destory_num = 0)
                        Saveitemstock.save()
                    if self.item_now_user == OldItemDetailData['userinfo']['item_pass_user']:  # 如果用户未变
                        if self.item_change_location == OldItemDetailData['userinfo']['item_location']:  # 如果资产所在位置未变
                            info = '{}已变更！'.format(self.item_sn)                        
                        if self.item_change_location != OldItemDetailData['userinfo']['item_location']:
                            info = '{}已变更！'.format(self.item_sn)                    
                    if self.item_now_user != OldItemDetailData['userinfo']['item_pass_user']:   # 如果用户改变
                        if self.item_change_location == OldItemDetailData['userinfo']['item_location']:  # 如果资产所在位置未变
                            info = '{}已变更！'.format(self.item_sn)
                        if self.item_change_location != OldItemDetailData['userinfo']['item_location']:  # 如果资产所在位置改未变
                            info = '{}已变更！'.format(self.item_sn)                        
                        editingPassUserItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                        if editingPassUserItemKind == '手机':
                            old_user_phone_sn_list = passUserItemRec.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_phone_sn_list_new = old_user_phone_sn_list.split(',')
                            old_user_phone_sn_list_new.remove(self.item_sn)
                            try:
                                old_user_phone_sn_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_phone_sn = old_user_phone_sn_list_new
                            now_user_phone_sn_list = nowUserItemRec.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_phone_sn_list_new = now_user_phone_sn_list.split(',')
                            now_user_phone_sn_list_new.append(self.item_sn)
                            try:
                                now_user_phone_sn_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_phone_sn = now_user_phone_sn_list_new
                        if editingPassUserItemKind == '手机号码':
                            old_user_phone_num_list = passUserItemRec.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_phone_num_list_new = old_user_phone_num_list.split(',')
                            old_user_phone_num_list_new.remove(self.item_sn)
                            try:
                                old_user_phone_num_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_phone_num = old_user_phone_num_list_new
                            now_user_phone_num_list = nowUserItemRec.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_phone_num_list_new = now_user_phone_num_list.split(',')
                            now_user_phone_num_list_new.append(self.item_sn)
                            try:
                                now_user_phone_num_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_phone_num = now_user_phone_num_list_new
                        if editingPassUserItemKind == 'pad':
                            old_user_pad_sn_list = passUserItemRec.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_pad_sn_list_new = old_user_pad_sn_list.split(',')
                            old_user_pad_sn_list_new.remove(self.item_sn)
                            try:
                                old_user_pad_sn_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_pad_sn = old_user_pad_sn_list_new
                            now_user_pad_sn_list = nowUserItemRec.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_pad_sn_list_new = now_user_pad_sn_list.split(',')
                            now_user_pad_sn_list_new.append(self.item_sn)
                            try:
                                now_user_pad_sn_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_pad_sn = now_user_pad_sn_list_new
                        if editingPassUserItemKind == '微信号':
                            old_user_wechat_name_list = passUserItemRec.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_wechat_name_list_new = old_user_wechat_name_list.split(',')
                            old_user_wechat_name_list_new.remove(self.item_sn)
                            try:
                                old_user_wechat_name_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_wechat_name = old_user_wechat_name_list_new
                            now_user_wechat_name_list = nowUserItemRec.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_wechat_name_list_new = now_user_wechat_name_list.split(',')
                            now_user_wechat_name_list_new.append(self.item_sn)
                            try:
                                now_user_wechat_name_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_wechat_name = now_user_wechat_name_list_new
                        if editingPassUserItemKind == '千牛账号':
                            old_user_qianniu_name_list = passUserItemRec.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_qianniu_name_list_new = old_user_qianniu_name_list.split(',')
                            old_user_qianniu_name_list_new.remove(self.item_sn)
                            try:
                                old_user_qianniu_name_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_qianniu_name = old_user_qianniu_name_list_new
                            now_user_qianniu_name_list = nowUserItemRec.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_qianniu_name_list_new = now_user_qianniu_name_list.split(',')
                            now_user_qianniu_name_list_new.append(self.item_sn)
                            try:
                                now_user_qianniu_name_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_qianniu_name = now_user_qianniu_name_list_new
                        if editingPassUserItemKind == '其他':
                            old_user_otheritems_list = passUserItemRec.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_otheritems_list_new = old_user_otheritems_list.split(',')
                            old_user_otheritems_list_new.remove(self.item_sn)
                            try:
                                old_user_otheritems_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_otheritems = old_user_otheritems_list_new
                            now_user_otheritems_list = nowUserItemRec.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_otheritems_list_new = now_user_otheritems_list.split(',')
                            now_user_otheritems_list_new.append(self.item_sn)
                            try:
                                now_user_otheritems_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_otheritems = now_user_otheritems_list_new
                if editingItemKind == '台式电脑':
                    try:                    
                        testPc = u_i_i.objects.get( user_workid = self.item_now_user_workid ).user_pc_sn
                    except:
                        try:
                            testPc = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_change_location )[0].user_pc_sn
                        except:
                            pass
                    try:   # 如果现用户底下有资产
                        testPcStatu = i_i.objects.get( item_sn = testPc ).item_statu
                        if testPc != '' and testPc != self.item_sn and testPcStatu != '闲置':  # 变更现用户原资产信息                          
                            oldItemInfoRc = i_i.objects.get( item_sn = testPc )
                            oldItemInfoRc.item_statu = '闲置'
                            oldItemInfoRc.item_now_user = ''
                            oldItemInfoRc.item_now_user_workid = ''
                            oldItemInfoRc.save()
                            oldItemStandByRc = u_i_i.objects.filter( user_workid = '' ).filter( user_location = self.item_change_location )[0]
                            oldItemStandByRcList = oldItemStandByRc.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            oldItemStandByRcListNew = oldItemStandByRcList.split(',')
                            oldItemStandByRcListNew.append(testPc)
                            try:
                                oldItemStandByRcListNews.remove('')
                            except:
                                pass
                            oldItemStandByRc.user_pc_sn = oldItemStandByRcListNew
                            oldItemStandByRc.save()
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num + 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                                    item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                                    item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                        s.save()  # 更新资产变更表
                        q_i_i = i_i.objects.get( item_sn = self.item_sn )    
                        if q_i_i.item_statu == '闲置' and (self.item_pass_user_workid != self.item_now_user_workid):
                            oldItemInfoRc = i_i.objects.get( item_sn = testPc )
                            oldItemInfoRc.item_statu = '闲置'
                            oldItemInfoRc.item_now_user = ''
                            oldItemInfoRc.item_now_user_workid = ''
                            oldItemInfoRc.save()
                            oldItemStandByRc = u_i_i.objects.filter( user_workid = '' ).filter( user_location = self.item_change_location )[0]
                            oldItemStandByRcList = oldItemStandByRc.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            oldItemStandByRcListNew = oldItemStandByRcList.split(',')
                            oldItemStandByRcListNew.append(testPc)
                            try:
                                oldItemStandByRcListNew.remove('')
                            except:
                                pass
                            oldItemStandByRc.user_pc_sn = oldItemStandByRcListNew
                            oldItemStandByRc.save()
                            oldItemLocation = q_i_i.item_location
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = oldItemLocation )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num - 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        elif q_i_i.item_statu == '闲置':
                            oldItemLocation = q_i_i.item_location
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = oldItemLocation )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num - 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        q_i_i.item_statu = self.item_statu
                        q_i_i.item_location = self.item_change_location
                        q_i_i.item_now_user = self.item_now_user
                        q_i_i.item_now_user_workid = self.item_now_user_workid
                        q_i_i.item_info = self.item_change_info
                        q_i_i.save()
                        if self.item_pass_user_workid == '':
                            old_user_pc_list = passUserItemRec.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_pc_list_new = old_user_pc_list.split(',')
                            old_user_pc_list_new.remove(self.item_sn)
                            try:
                                old_user_pc_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_pc_sn = old_user_pc_list_new
                        else:
                            passUserItemRec.user_pc_sn = ''
                        nowUserItemRec.user_pc_sn = self.item_sn
                    except:   # 现用户底下无资产
                        try:
                            s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                                        item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                                        item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                            s.save()  # 更新资产变更表
                            q_i_i = i_i.objects.get( item_sn = self.item_sn )
                            if q_i_i.item_statu == '闲置':
                                oldItemLocation = q_i_i.item_location
                                q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = oldItemLocation )[0] # 更新该部门闲置物资库存
                                item_stock_num_now = q_i_s.item_stock_num - 1
                                q_i_s.item_stock_num = item_stock_num_now
                                q_i_s.save()
                            q_i_i.item_statu = self.item_statu
                            q_i_i.item_location = self.item_change_location
                            q_i_i.item_now_user = self.item_now_user
                            q_i_i.item_now_user_workid = self.item_now_user_workid
                            q_i_i.item_info = self.item_change_info
                            q_i_i.save()
                            if self.item_pass_user_workid == '':
                                old_user_pc_list = passUserItemRec.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                                old_user_pc_list_new = old_user_pc_list.split(',')
                                old_user_pc_list_new.remove(self.item_sn)
                                try:
                                    old_user_pc_list_new.remove('')
                                except:
                                    pass
                                passUserItemRec.user_pc_sn = old_user_pc_list_new
                            else:
                                passUserItemRec.user_pc_sn = ''
                            nowUserItemRec.user_pc_sn = self.item_sn
                        except:
                            pass
                    info = '{}资产变更成功！'.format(self.item_sn)
                if editingItemKind == '笔记本电脑':
                    try:                    
                        testNotebook = u_i_i.objects.get( user_workid = self.item_now_user_workid ).user_notebook_sn
                    except:
                        try:
                            testNotebook = u_i_i.objects.filter( user_workid = self.item_now_user_workid ).filter( user_location = self.item_change_location )[0].user_notebook_sn
                        except:
                            pass
                    try:   # 如果现用户底下有该类型资产
                        testNotebookStatu = i_i.objects.get( item_sn = testNotebook ).item_statu
                        if testNotebook != '' and testNotebook != self.item_sn and testNotebookStatu != '闲置':                            
                            oldItemInfoRc = i_i.objects.get( item_sn = testNotebook )
                            oldItemInfoRc.item_statu = '闲置'
                            oldItemInfoRc.item_now_user = ''
                            oldItemInfoRc.item_now_user_workid = ''
                            oldItemInfoRc.save()
                            oldItemStandByRc = u_i_i.objects.filter( user_workid = '' ).filter( user_location = self.item_change_location )[0]
                            oldItemStandByRcList = oldItemStandByRc.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            oldItemStandByRcListNew = oldItemStandByRcList.split(',')
                            oldItemStandByRcListNew.append(testNotebook)
                            try:
                                oldItemStandByRcListNews.remove('')
                            except:
                                pass
                            oldItemStandByRc.user_notebook_sn = oldItemStandByRcListNew
                            oldItemStandByRc.save()
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num + 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                                    item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                                    item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                        s.save()  # 更新资产变更表
                        q_i_i = i_i.objects.get( item_sn = self.item_sn )
                        if q_i_i.item_statu == '闲置' and (self.item_pass_user_workid != self.item_now_user_workid):
                            oldItemInfoRc = i_i.objects.get( item_sn = testNotebook )
                            oldItemInfoRc.item_statu = '闲置'
                            oldItemInfoRc.item_now_user = ''
                            oldItemInfoRc.item_now_user_workid = ''
                            oldItemInfoRc.save()                            
                            oldItemStandByRc = u_i_i.objects.filter( user_workid = '' ).filter( user_location = self.item_change_location )[0]
                            oldItemStandByRcList = oldItemStandByRc.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            oldItemStandByRcListNew = oldItemStandByRcList.split(',')
                            oldItemStandByRcListNew.append(testNotebook)
                            try:
                                oldItemStandByRcListNew.remove('')
                            except:
                                pass
                            oldItemStandByRc.user_notebook_sn = oldItemStandByRcListNew
                            oldItemStandByRc.save()
                            oldItemLocation = q_i_i.item_location
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = oldItemLocation )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num - 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        elif q_i_i.item_statu == '闲置':
                            oldItemLocation = q_i_i.item_location
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = oldItemLocation )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num - 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        q_i_i.item_statu = self.item_statu
                        q_i_i.item_location = self.item_change_location
                        q_i_i.item_now_user = self.item_now_user
                        q_i_i.item_now_user_workid = self.item_now_user_workid
                        q_i_i.item_info = self.item_change_info
                        q_i_i.save()
                        if self.item_pass_user_workid == '':
                            print(passUserItemRec.user_notebook_sn)
                            old_user_notebook_list = passUserItemRec.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_notebook_list_new = old_user_notebook_list.split(',')
                            old_user_notebook_list_new.remove(self.item_sn)
                            try:
                                old_user_notebook_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_notebook_sn = old_user_notebook_list_new
                        if self.item_pass_user_workid != '':
                            print(passUserItemRec.user_notebook_sn)
                            passUserItemRec.user_notebook_sn = ''                            
                        nowUserItemRec.user_notebook_sn = self.item_sn
                    except:   # 现用户底下无该类型资产
                        try:
                            s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                                        item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                                        item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                            s.save()  # 更新资产变更表
                            q_i_i = i_i.objects.get( item_sn = self.item_sn )
                            if q_i_i.item_statu == '闲置':
                                oldItemLocation = q_i_i.item_location
                                q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = oldItemLocation )[0] # 更新该部门闲置物资库存
                                item_stock_num_now = q_i_s.item_stock_num - 1
                                q_i_s.item_stock_num = item_stock_num_now
                                q_i_s.save()
                            q_i_i.item_statu = self.item_statu
                            q_i_i.item_location = self.item_change_location
                            q_i_i.item_now_user = self.item_now_user
                            q_i_i.item_now_user_workid = self.item_now_user_workid
                            q_i_i.item_info = self.item_change_info
                            q_i_i.save()
                            if self.item_pass_user_workid == '':
                                old_user_notebook_list = passUserItemRec.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                                old_user_notebook_list_new = old_user_notebook_list.split(',')
                                old_user_notebook_list_new.remove(self.item_sn)
                                try:
                                    old_user_notebook_list_new.remove('')
                                except:
                                    pass
                                print(old_user_notebook_list_new)
                                passUserItemRec.user_notebook_sn = old_user_notebook_list_new
                            else:
                                passUserItemRec.user_notebook_sn = ''
                            print(passUserItemRec)
                            nowUserItemRec.user_notebook_sn = self.item_sn
                        except:
                            pass

                    info = '{}资产变更成功！'.format(self.item_sn)
                passUserItemRec.save()
                nowUserItemRec.save()
            if self.item_statu == '闲置':
                s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                                item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                                item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                s.save()  # 更新资产变更表
                editingItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                if editingItemKind != '台式电脑' and editingItemKind != '笔记本电脑':
                    try:   # 查看该类资产在现处位置有无库存
                        q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                        item_stock_num_now = q_i_s.item_stock_num + 1
                        q_i_s.item_stock_num = item_stock_num_now
                        q_i_s.save()
                    except:  # 无库存则生成库存记录
                        Saveitemstock = i_s(item_kind = editingItemKind, item_stock_location = self.item_change_location, item_stock_num = 1, item_destory_num = 0)
                        Saveitemstock.save()
                    q_i_i = i_i.objects.get( item_sn = self.item_sn )
                    q_i_i.item_statu = self.item_statu
                    q_i_i.item_location = self.item_change_location
                    q_i_i.item_now_user = self.item_now_user
                    q_i_i.item_now_user_workid = self.item_now_user_workid
                    q_i_i.item_info = self.item_change_info
                    q_i_i.save()               
                    if self.item_now_user == OldItemDetailData['userinfo']['item_pass_user']:  # 如果用户未变
                        if self.item_change_location == OldItemDetailData['userinfo']['item_location']:  # 如果资产所在位置未变                        
                            info = '{}已变更！'.format(self.item_sn)                        
                        if self.item_change_location != OldItemDetailData['userinfo']['item_location']:
                            info = '{}已变更！'.format(self.item_sn)                    
                    if self.item_now_user != OldItemDetailData['userinfo']['item_pass_user']:   # 如果用户改变
                        if self.item_change_location == OldItemDetailData['userinfo']['item_location']:  # 如果资产所在位置未变
                            info = '{}已变更！'.format(self.item_sn)
                        if self.item_change_location != OldItemDetailData['userinfo']['item_location']:  # 如果资产所在位置改未变
                            info = '{}已变更！'.format(self.item_sn)        
                        editingPassUserItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                        if editingPassUserItemKind == '手机':
                            old_user_phone_sn_list = passUserItemRec.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_phone_sn_list_new = old_user_phone_sn_list.split(',')
                            old_user_phone_sn_list_new.remove(self.item_sn)
                            try:
                                old_user_phone_sn_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_phone_sn = old_user_phone_sn_list_new
                            now_user_phone_sn_list = nowUserItemRec.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_phone_sn_list_new = now_user_phone_sn_list.split(',')
                            now_user_phone_sn_list_new.append(self.item_sn)
                            try:
                                now_user_phone_sn_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_phone_sn = now_user_phone_sn_list_new
                        if editingPassUserItemKind == '手机号码':
                            old_user_phone_num_list = passUserItemRec.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_phone_num_list_new = old_user_phone_num_list.split(',')
                            old_user_phone_num_list_new.remove(self.item_sn)
                            try:
                                old_user_phone_num_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_phone_num = old_user_phone_num_list_new
                            now_user_phone_num_list = nowUserItemRec.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_phone_num_list_new = now_user_phone_num_list.split(',')
                            now_user_phone_num_list_new.append(self.item_sn)
                            try:
                                now_user_phone_num_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_phone_num = now_user_phone_num_list_new
                        if editingPassUserItemKind == 'pad':
                            old_user_pad_sn_list = passUserItemRec.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_pad_sn_list_new = old_user_pad_sn_list.split(',')
                            old_user_pad_sn_list_new.remove(self.item_sn)
                            try:
                                old_user_pad_sn_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_pad_sn = old_user_pad_sn_list_new
                            now_user_pad_sn_list = nowUserItemRec.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_pad_sn_list_new = now_user_pad_sn_list.split(',')
                            now_user_pad_sn_list_new.append(self.item_sn)
                            try:
                                now_user_pad_sn_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_pad_sn = now_user_pad_sn_list_new
                        if editingPassUserItemKind == '微信号':
                            old_user_wechat_name_list = passUserItemRec.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_wechat_name_list_new = old_user_wechat_name_list.split(',')
                            old_user_wechat_name_list_new.remove(self.item_sn)
                            try:
                                old_user_wechat_name_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_wechat_name = old_user_wechat_name_list_new
                            now_user_wechat_name_list = nowUserItemRec.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_wechat_name_list_new = now_user_wechat_name_list.split(',')
                            now_user_wechat_name_list_new.append(self.item_sn)
                            try:
                                now_user_wechat_name_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_wechat_name = now_user_wechat_name_list_new
                        if editingPassUserItemKind == '千牛账号':
                            old_user_qianniu_name_list = passUserItemRec.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_qianniu_name_list_new = old_user_qianniu_name_list.split(',')
                            old_user_qianniu_name_list_new.remove(self.item_sn)
                            try:
                                old_user_qianniu_name_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_qianniu_name = old_user_qianniu_name_list_new
                            now_user_qianniu_name_list = nowUserItemRec.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_qianniu_name_list_new = now_user_qianniu_name_list.split(',')
                            now_user_qianniu_name_list_new.append(self.item_sn)
                            try:
                                now_user_qianniu_name_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_qianniu_name = now_user_qianniu_name_list_new
                        if editingPassUserItemKind == '其他':
                            old_user_otheritems_list = passUserItemRec.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_otheritems_list_new = old_user_otheritems_list.split(',')
                            old_user_otheritems_list_new.remove(self.item_sn)
                            try:
                                old_user_otheritems_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_otheritems = old_user_otheritems_list_new
                            now_user_otheritems_list = nowUserItemRec.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            now_user_otheritems_list_new = now_user_otheritems_list.split(',')
                            now_user_otheritems_list_new.append(self.item_sn)
                            try:
                                now_user_otheritems_list_new.remove('')
                            except:
                                pass
                            nowUserItemRec.user_otheritems = now_user_otheritems_list_new
                if editingItemKind == '台式电脑':
                    if self.item_now_user_workid == '':
                        try:   # 查看该类资产在现处位置有无库存
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num + 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        except:  # 无库存则生成库存记录
                            Saveitemstock = i_s(item_kind = editingItemKind, item_stock_location = self.item_change_location, item_stock_num = 1, item_destory_num = 0)
                            Saveitemstock.save()
                        if self.item_pass_user_workid == '':
                            old_user_pc_list = passUserItemRec.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_pc_list_new = old_user_pc_list.split(',')
                            old_user_pc_list_new.remove(self.item_sn)
                            try:
                                old_user_pc_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_pc_sn = old_user_pc_list_new
                        else:
                            passUserItemRec.user_pc_sn = ''
                        nowItemInfoRc = i_i.objects.get( item_sn = self.item_sn )
                        nowItemInfoRc.item_statu = '闲置'
                        nowItemInfoRc.item_location = self.item_change_location
                        nowItemInfoRc.item_now_user = self.item_now_user
                        nowItemInfoRc.item_now_user_workid = self.item_now_user_workid
                        nowItemInfoRc.item_info = self.item_change_info
                        nowItemInfoRc.save()
                        now_user_pc_list = nowUserItemRec.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        now_user_pc_list_new = now_user_pc_list.split(',')
                        now_user_pc_list_new.append(self.item_sn)
                        try:
                            now_user_pc_list_new.remove('')
                        except:
                            pass
                        nowUserItemRec.user_pc_sn = now_user_pc_list_new
                        # nowItemInfoRc.item_statu = '闲置'
                        # nowItemInfoRc.item_now_user = self.item_now_user
                        # nowItemInfoRc.item_now_user_workid = self.item_now_user_workid
                        # nowItemInfoRc.save()
                    if self.item_now_user_workid != '':  # 闲置资产转移至非空用户，判断原用户是否有电脑若有则将原电脑设置为闲置状态且无关联用户及用户工号
                        testPc = u_i_i.objects.get( user_workid = self.item_now_user_workid ).user_pc_sn
                        if testPc != '':                            
                            oldItemInfoRc = i_i.objects.get( item_sn = testPc )
                            oldItemInfoRc.item_statu = '闲置'
                            oldItemInfoRc.item_now_user = ''
                            oldItemInfoRc.item_now_user_workid = ''
                            oldItemInfoRc.save()
                        nowItemInfoRc = i_i.objects.get( item_sn = self.item_sn )
                        nowItemInfoRc.item_location = self.item_change_location
                        nowItemInfoRc.item_info = self.item_change_info
                        nowItemInfoRc.item_statu = '闲置'
                        nowItemInfoRc.item_now_user = self.item_now_user
                        nowItemInfoRc.item_now_user_workid = self.item_now_user_workid
                        nowItemInfoRc.save()
                        q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                        item_stock_num_now = q_i_s.item_stock_num + 1
                        q_i_s.item_stock_num = item_stock_num_now
                        q_i_s.save()
                        if self.item_pass_user_workid == '':
                            old_user_pc_list = passUserItemRec.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_pc_list_new = old_user_pc_list.split(',')
                            old_user_pc_list_new.remove(self.item_sn)
                            try:
                                old_user_pc_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_pc_sn = old_user_pc_list_new
                        else:
                            passUserItemRec.user_pc_sn = ''
                        nowUserItemRec.user_pc_sn = self.item_sn
                    info = '{}资产变更成功！'.format(self.item_sn)
                if editingItemKind == '笔记本电脑':
                    if self.item_now_user_workid == '':
                        try:   # 查看该类资产在现处位置有无库存
                            q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                            item_stock_num_now = q_i_s.item_stock_num + 1
                            q_i_s.item_stock_num = item_stock_num_now
                            q_i_s.save()
                        except:  # 无库存则生成库存记录
                            Saveitemstock = i_s(item_kind = editingItemKind, item_stock_location = self.item_change_location, item_stock_num = 1, item_destory_num = 0)
                            Saveitemstock.save()
                        if self.item_pass_user_workid == '':
                            old_user_notebook_list = passUserItemRec.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_notebook_list_new = old_user_notebook_list.split(',')
                            old_user_notebook_list_new.remove(self.item_sn)
                            try:
                                old_user_notebook_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_notebook_sn = old_user_notebook_list_new
                        else:
                            passUserItemRec.user_notebook_sn = ''
                        now_user_notebook_list = nowUserItemRec.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        now_user_notebook_list_new = now_user_notebook_list.split(',')
                        now_user_notebook_list_new.append(self.item_sn)
                        try:
                            now_user_notebook_list_new.remove('')
                        except:
                            pass
                        nowUserItemRec.user_notebook_sn = now_user_notebook_list_new
                        nowItemInfoRc = i_i.objects.get( item_sn = self.item_sn )
                        nowItemInfoRc.item_location = self.item_change_location
                        nowItemInfoRc.item_info = self.item_change_info
                        nowItemInfoRc.item_statu = '闲置'
                        nowItemInfoRc.item_now_user = self.item_now_user
                        nowItemInfoRc.item_now_user_workid = self.item_now_user_workid
                        nowItemInfoRc.save()
                    if self.item_now_user_workid != '':  # 闲置资产转移至非空用户，判断原用户是否有电脑若有则将原电脑设置为闲置状态且无关联用户及用户工号
                        testNotebook = u_i_i.objects.get( user_workid = self.item_now_user_workid ).user_notebook_sn
                        if testNotebook != '':                            
                            oldItemInfoRc = i_i.objects.get( item_sn = testNotebook )
                            oldItemInfoRc.item_statu = '闲置'
                            oldItemInfoRc.item_now_user = ''
                            oldItemInfoRc.item_now_user_workid = ''
                            oldItemInfoRc.save()
                        nowItemInfoRc = i_i.objects.get( item_sn = self.item_sn )
                        nowItemInfoRc.item_statu = '闲置'
                        nowItemInfoRc.item_location = self.item_change_location
                        nowItemInfoRc.item_info = self.item_change_info
                        nowItemInfoRc.item_now_user = self.item_now_user
                        nowItemInfoRc.item_now_user_workid = self.item_now_user_workid
                        nowItemInfoRc.save()
                        q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存
                        item_stock_num_now = q_i_s.item_stock_num + 1
                        q_i_s.item_stock_num = item_stock_num_now
                        q_i_s.save()
                        if self.item_pass_user_workid == '':
                            old_user_notebook_list = passUserItemRec.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                            old_user_notebook_list_new = old_user_notebook_list.split(',')
                            old_user_notebook_list_new.remove(self.item_sn)
                            try:
                                old_user_notebook_list_new.remove('')
                            except:
                                pass
                            passUserItemRec.user_notebook_sn = old_user_notebook_list_new
                        else:
                            passUserItemRec.user_notebook_sn = ''
                        nowUserItemRec.user_notebook_sn = self.item_sn
                    info = '{}资产变更成功！'.format(self.item_sn)
                passUserItemRec.save()
                nowUserItemRec.save()                        
            if self.item_statu == '报废':
                s = i_c_i( item_change_date = self.item_change_date, item_name = OldItemDetailData['userinfo']['item_name'], item_change_location = self.item_change_location,
                                item_statu = self.item_statu, item_sn = self.item_sn, item_pass_user = OldItemDetailData['userinfo']['item_pass_user'] ,item_now_user = self.item_now_user,
                                item_now_user_workid = self.item_now_user_workid, item_change_info = self.item_change_info)
                s.save()  # 更新资产变更表
                editingItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                q_i_i = i_i.objects.get( item_sn = self.item_sn )
                item_old_location = q_i_i.item_location
                if OldItemDetailData['userinfo']['item_statu'] == '闲置':                    
                    old_i_s =  i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = item_old_location )[0]                   
                    item_stock_num_now = old_i_s.item_stock_num - 1
                    old_i_s.item_stock_num = item_stock_num_now
                    old_i_s.save()
                try:
                    q_i_s = i_s.objects.filter( item_kind = editingItemKind ).filter( item_stock_location = self.item_change_location )[0] # 更新该部门闲置物资库存                    
                    item_destory_num_now = q_i_s.item_destory_num + 1
                    q_i_s.item_destory_num = item_destory_num_now
                    q_i_s.save()
                except:
                    Saveitemstock = i_s(item_kind = editingItemKind, item_stock_location = self.item_change_location, item_stock_num = 0, item_destory_num = 1)
                    Saveitemstock.save()
                try:
                    passUserItemRec = u_i_i.objects.get( user_workid = self.item_pass_user_workid )
                except:
                    try:
                        q_i_i = i_i.objects.get( item_sn = self.item_sn )
                        oldItemLocation = q_i_i.item_location
                        passUserItemRec = u_i_i.objects.filter( user_workid = self.item_pass_user_workid ).filter( user_location = oldItemLocation )[0]
                    except:
                        pass
                editingPassUserItemKind = i_i.objects.get( item_sn = self.item_sn ).item_kind
                if editingPassUserItemKind == '手机':
                    old_user_phone_sn_list = passUserItemRec.user_phone_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                    old_user_phone_sn_list_new = old_user_phone_sn_list.split(',')
                    old_user_phone_sn_list_new.remove(self.item_sn)
                    try:
                        old_user_phone_sn_list_new.remove('')
                    except:
                        pass
                    passUserItemRec.user_phone_sn = old_user_phone_sn_list_new
                if editingPassUserItemKind == '手机号码':
                    old_user_phone_num_list = passUserItemRec.user_phone_num.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                    old_user_phone_num_list_new = old_user_phone_num_list.split(',')
                    old_user_phone_num_list_new.remove(self.item_sn)
                    try:
                        old_user_phone_num_list_new.remove('')
                    except:
                        pass
                    passUserItemRec.user_phone_num = old_user_phone_num_list_new
                if editingPassUserItemKind == 'pad':
                    old_user_pad_sn_list = passUserItemRec.user_pad_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                    old_user_pad_sn_list_new = old_user_pad_sn_list.split(',')
                    old_user_pad_sn_list_new.remove(self.item_sn)
                    try:
                        old_user_pad_sn_list_new.remove('')
                    except:
                        pass
                    passUserItemRec.user_pad_sn = old_user_pad_sn_list_new
                if editingPassUserItemKind == '微信号':
                    old_user_wechat_name_list = passUserItemRec.user_wechat_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                    old_user_wechat_name_list_new = old_user_wechat_name_list.split(',')
                    old_user_wechat_name_list_new.remove(self.item_sn)
                    try:
                        old_user_wechat_name_list_new.remove('')
                    except:
                        pass
                    passUserItemRec.user_wechat_name = old_user_wechat_name_list_new
                if editingPassUserItemKind == '千牛账号':
                    old_user_qianniu_name_list = passUserItemRec.user_qianniu_name.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                    old_user_qianniu_name_list_new = old_user_qianniu_name_list.split(',')
                    old_user_qianniu_name_list_new.remove(self.item_sn)
                    try:
                        old_user_qianniu_name_list_new.remove('')
                    except:
                        pass
                    passUserItemRec.user_qianniu_name = old_user_qianniu_name_list_new
                if editingPassUserItemKind == '其他':
                    old_user_otheritems_list = passUserItemRec.user_otheritems.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                    old_user_otheritems_list_new = old_user_otheritems_list.split(',')
                    old_user_otheritems_list_new.remove(self.item_sn)
                    try:
                        old_user_otheritems_list_new.remove('')
                    except:
                        pass
                    passUserItemRec.user_otheritems = old_user_otheritems_list_new
                if editingPassUserItemKind == '台式电脑':
                    if self.item_pass_user_workid == '':
                        old_user_pc_list = passUserItemRec.user_pc_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        old_user_pc_list_new = old_user_pc_list.split(',')
                        old_user_pc_list_new.remove(self.item_sn)
                        try:
                            old_user_pc_list_new.remove('')
                        except:
                            pass
                        passUserItemRec.user_pc_sn = old_user_pc_list_new
                    else:
                        passUserItemRec.user_pc_sn = ''
                if editingPassUserItemKind == '笔记本电脑':
                    if self.item_pass_user_workid == '':
                        old_user_notebook_list = passUserItemRec.user_notebook_sn.replace('[', '').replace(']', '').replace("'","").replace(' ','')
                        old_user_notebook_list_new = old_user_notebook_list.split(',')
                        old_user_notebook_list_new.remove(self.item_sn)
                        try:
                            old_user_notebook_list_new.remove('')
                        except:
                            pass
                        passUserItemRec.user_notebook_sn = old_user_notebook_list_new
                    else:
                        passUserItemRec.user_notebook_sn = ''
                passUserItemRec.save()
                nowItemInfoRc = i_i.objects.get( item_sn = self.item_sn )
                nowItemInfoRc.item_now_user = self.item_now_user
                nowItemInfoRc.item_now_user_workid = self.item_now_user_workid
                nowItemInfoRc.item_statu = self.item_statu
                nowItemInfoRc.item_location = self.item_change_location
                nowItemInfoRc.item_info = self.item_change_info
                nowItemInfoRc.save()
                info = '{}已报废！'.format(self.item_sn)                                
            NowItemDetailDataView = getItemDetail( name = self.name, item_sn = self.item_sn )
            NowItemDetailData = NowItemDetailDataView.getItemDetailData()
            NowItemDetailData['userinfo']['info'] = info
            return NowItemDetailData            
        except:
            pass
                    

class getSearchItemInfo:
    """
    回传IT资产搜索信息
    
    """
    def __init__(self, **kwds):
        self.itemSearchSn = kwds['itemSearchSn']

    def getSearchItemData(self):
        try:
            q_i_i = i_i.objects.get( item_sn = self.itemSearchSn )
            item_inbound_date = q_i_i.item_inbound_date
            item_name = q_i_i.item_name
            item_statu = q_i_i.item_statu
            item_sn = q_i_i.item_sn
            item_location = q_i_i.item_location
            item_now_user = q_i_i.item_now_user
            item_now_user_workid = q_i_i.item_now_user_workid
            item_info = q_i_i.item_info
            q_ici = i_c_i.objects.filter( item_sn = self.itemSearchSn )
            item_change_datelist = []
            item_pass_userlist = []
            item_now_userlist = []
            item_statulist = []
            item_now_user_workidlist = []
            item_change_infolist = []
            print( q_ici )
            for m in q_ici:
                item_change_datelist.append( m.item_change_date )
                item_pass_userlist.append( m.item_pass_user )
                item_now_userlist.append( m.item_now_user )
                item_now_user_workidlist.append( m.item_now_user_workid )
                item_statulist.append( m.item_statu )
                item_change_infolist.append( m.item_change_info )
            ItemChangeInfoList = zip( item_change_datelist, item_pass_userlist, item_now_userlist, item_now_user_workidlist, item_statulist, item_change_infolist )
            SearchItemData = {'userinfo': {'item_inbound_date': item_inbound_date,
                                'item_name': item_name,
                                'item_statu':item_statu, 
                                'item_sn': item_sn,
                                'item_location': item_location,
                                'item_now_user': item_now_user,
                                'item_now_user_workid': item_now_user_workid,
                                'item_info': item_info,
                                'ItemChangeInfoList': ItemChangeInfoList}}
            print(SearchItemData)
            return SearchItemData
        except:
            info = '未查询到“{}”的资产信息，请联系管理员！'.format(self.itemSearchSn)
            NoResaultInfo = {'userinfo': {'info': info,
                                'item_sn': self.itemSearchSn}}
            return NoResaultInfo


class getUserItemsInfo:
    """
    回传用户IT资产列表信息
    
    """
    def __init__(self, **kwds):
        self.pageSep = kwds['pageSep']
        self.name = kwds['name']
        self.num = kwds['num']

    def getUserItemsData(self):
        try:            
            test = u_i_i.objects.all().exists()            
            if test:
                uII = u_i_i.objects.exclude( user_workid = '' ).exclude( user_name = '' ).order_by( 'id' )
                paginator = Paginator(uII, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    print('num', self.num)
                    number = paginator.page(self.num)
                    print(number.object_list)                    
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                UserItemsInfoData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
            else:
                UserItemsInfoDataList = []
                paginator = Paginator(UserItemsInfoDataList, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                info = '暂时没有员工资产信息'
                UserItemsInfoData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
                UserItemsInfoData['userinfo']['info'] = info
        except:
            pass
        return UserItemsInfoData

class getSearchUserItems(getUserItemsInfo):
    """
    回传搜索用户结果列表信息
    
    """
    def __init__(self, **kwds):
        getUserItemsInfo.__init__(self,  pageSep = kwds['pageSep'], name = kwds['name'], num = kwds['num'])
        self.searchuser = kwds['searchuser']

    def getSearchUserItemsData(self):
        try:
            testUserItemsExists = u_i_i.objects.filter(Q(user_name__icontains=self.searchuser)|Q(user_workid__icontains=self.searchuser)).exists()
            if testUserItemsExists:
                usII = u_i_i.objects.filter(Q(user_name__icontains=self.searchuser)|Q(user_workid__icontains=self.searchuser)).order_by( 'id' )
                paginator = Paginator(usII, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)                   
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                SearchUserItemsData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
            else:
                SearchUserItemsDataList = []
                paginator = Paginator(SearchUserItemsDataList, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                info = '没有搜索到相关用户资产信息'
                SearchUserItemsData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
                SearchUserItemsData['userinfo']['info'] = info
        except:
            pass
        return SearchUserItemsData


class getItemStockInfo:
    """
    回传用户IT资产列表信息
    
    """
    def __init__(self, **kwds):
        self.pageSep = kwds['pageSep']
        self.name = kwds['name']
        self.num = kwds['num']

    def getItemStockData(self):
        try:            
            test = i_s.objects.all().exists()            
            if test:
                isII = i_s.objects.all().order_by( 'id' )
                paginator = Paginator(isII, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    print('num', self.num)
                    number = paginator.page(self.num)
                    print(number.object_list)                    
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                ItemStockData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
            else:
                ItemStockDataList = []
                paginator = Paginator(ItemStockDataList, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                info = '暂时没有IT资产库存信息'
                ItemStockData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
                ItemStockData['userinfo']['info'] = info
        except:
            pass
        return ItemStockData

class getSearchItemStockInfo(getItemStockInfo):
    """
    回传搜索用户结果列表信息
    
    """
    def __init__(self, **kwds):
        getItemStockInfo.__init__(self,  pageSep = kwds['pageSep'], name = kwds['name'], num = kwds['num'])
        self.searchitemstockinfo = kwds['searchitemstockinfo']

    def getSearchItemStockInfoData(self):
        try:
            testItemStockInfoExists = i_s.objects.filter(Q(item_kind__icontains=self.searchitemstockinfo)|Q(item_stock_location__icontains=self.searchitemstockinfo)).exists()
            if testItemStockInfoExists:
                sIS = i_s.objects.filter(Q(item_kind__icontains=self.searchitemstockinfo)|Q(item_stock_location__icontains=self.searchitemstockinfo)).order_by( 'id' )
                paginator = Paginator(sIS, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)                   
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                SearchItemStockInfoData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
            else:
                SearchItemStockInfoDataList = []
                paginator = Paginator(SearchItemStockInfoDataList, self.pageSep, 3)
                # 值1：所有的数据
                # 值2：每一页的数据
                # 值3：当最后一页数据少于n条，将数据并入上一页
                try:
                    # 获取第几页
                    number = paginator.page(self.num)
                except PageNotAnInteger:
                    # 如果输入的页码数不是整数，那么显示第一页数据
                    number = paginator.page(1)
                except EmptyPage:
                    number = paginator.page(paginator.num_pages)
                info = '没有搜索到相关库存信息'
                SearchItemStockInfoData = {'userinfo': {'name': self.name,
                                 'page': number,
                                 'paginator':paginator, 
                                 'pageSep': self.pageSep}}
                SearchItemStockInfoData['userinfo']['info'] = info
        except:
            pass
        return SearchItemStockInfoData        




    





