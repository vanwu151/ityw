# coding=utf-8
import os, re, time, json
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator , PageNotAnInteger, EmptyPage
from django.db.models import Sum, Q
from .models import admininfo as a_i
from .models import useritemsinfo as u_i_i
from .models import iteminfo as i_i
from .models import itemchangeinfo as i_c_i
from .models import itemstock as i_s
from .ITYWclass import *
# Create your views here.


def json_test(request):
    if request.method == "POST":
        a = request.body
        print(a, type(a))
        name = json.loads(a)
        print(name['description']['name'])
        print(name, type(name))
        jsontest = {"code": "200", "status": "success"}
        jsontest2 = {"ACT": "Hello", "User": name}
        data = [jsontest, jsontest2]
        return JsonResponse(data, safe=False)

def relogin(request):
    if request.method == "GET":
        return render(request, 'Kpi/Login.html')

def register(request):
    try:
        if request.method == "GET":
            return render(request, 'Kpi/register.html')
        elif request.method == "POST":
            user=request.POST.get('user')                                                              #获取前端login页面输入的用户名赋给变量v1
            try:                                                                    
                j = a_i.objects.get( admin_name = user ).user_name                                       #尝试通过前端login页面获取的用户名从数据库里查询有无记录
                info = user + ':该用户名已被注册！'                                                      #获取到记录则不会抛出异常，回传给前端Info信息，已查询到相同用户名的用户并提醒该用户名已被注册
                return render(request, 'Kpi/register.html', {'userinfo': {'info': info}})
            except:                                                                                  #如果程序抛出异常则代表前端login页面获取的用户名在已有数据库里未查询到记录                                                      #可继续往下进行用户注册操作
                v5 = request.POST.get('pwd')
                password = make_password(v5,None,'pbkdf2_sha256')
                info = '恭喜！ ' + user + ' 用户注册成功！'
                q = a_i(admin_name = user,  admin_password = password)
                q.save()
            return render(request, 'Kpi/Login.html', {'userinfo': {'info': info}})   #注册成功返回到登录页面
    except:
        info = '请填写注册信息！'
        return render(request, 'Kpi/register.html', {'userinfo': {'info': info}})
    
def login(request):
    if request.method == "GET":
        return render(request, 'Kpi/Login.html')

def logout(request):                #注销操作 
    request.session.clear()         #删除session里的全部内容
    return redirect('/login')       #重定向到/login前端页面
    

def logininfo(request):
    try:
        num = request.session['index']
    except:
        num = '1'
    try:
        pageSep = request.session['pageSep']
    except:
        pageSep = 10
    if request.method == "POST":
        try:
            UserName=request.POST.get('user')
            UserPass=request.POST.get('pwd')
            q = a_i.objects.get(admin_name=UserName)
            name = q.admin_name
            pwd  = q.admin_password
            if UserName == name and check_password(UserPass,pwd) is True:
                request.session['username'] = UserName    #定义session“username”字段并令session中username字段值为登录的用户名
                request.session['is_login'] = True        #定义session“is_login”字段并令该字段值为"True"表示会话已经创建
                getItemInfoView = getItemInfo(name = name, num = num, pageSep = pageSep)
                getItemInfoData = getItemInfoView.getItemInfoData()
                return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
            else:
                info = '用户名或密码错误！'
                return render(request, 'Kpi/Login.html', {'userinfo': {'info': info}})
        except:
            info = '登录信息不能为空！'
            return render(request, 'Kpi/Login.html', {'userinfo': {'info': info}})


def Additem(request):
    if request.session.get('is_login',None):
        try:
            num = request.session['index']
        except:
            num = '1'
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10
        if request.method == "POST":
            name = request.session['username']
            try:
                action = request.POST.get('action')
                if action == "新增":
                    item_inbound_date = request.POST.get('item_inbound_date')
                    item_name = request.POST.get('item_name')
                    item_kind = request.POST.get('item_kind')
                    item_sn = request.POST.get('item_sn')
                    item_now_user = request.POST.get('item_now_user')
                    item_now_user_workid = request.POST.get('item_now_user_workid')
                    item_statu = request.POST.get('item_statu')
                    item_location = request.POST.get('item_location')
                    item_info = request.POST.get('item_info')
                    if (item_now_user == '' or item_now_user_workid == '') and item_statu == '在用':
                        info = '新增资产状态为“在用”时，资产所属用户不得为空'
                        getItemInfoView = getItemInfo(name = name, num = num, pageSep = pageSep)
                        getItemInfoData = getItemInfoView.getItemInfoData()
                        getItemInfoData['userinfo']['info'] = info
                        return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
                    if (item_now_user != '' or item_now_user_workid != '') and item_statu == '报废':
                        info = '新增资产状态为“报废”时，资产所属用户必须为空'
                        getItemInfoView = getItemInfo(name = name, num = num, pageSep = pageSep)
                        getItemInfoData = getItemInfoView.getItemInfoData()
                        getItemInfoData['userinfo']['info'] = info
                        return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
                    else:
                        AddedItemInfoView = AddedItemInfo(name = name, num = num, pageSep = pageSep, item_inbound_date = item_inbound_date,
                                                    item_name = item_name, item_kind = item_kind, item_sn = item_sn, item_now_user = item_now_user,
                                                    item_now_user_workid = item_now_user_workid, item_statu = item_statu, item_location = item_location,
                                                    item_info = item_info)
                        AddedItemInfoData = AddedItemInfoView.AddedItemInfoData()
                        return render(request, 'Kpi/showmanageiteminfo.html', AddedItemInfoData)
            except:
                pass

def EditItemlogin(request):
    if request.method == "POST":
        item_sn = request.POST.get('item_sn')
        item_now_user_workid = request.POST.get('item_now_user_workid')
        request.session['item_sn'] = item_sn
        request.session['item_pass_user_workid'] = item_now_user_workid
        return render(request, 'Kpi/EditItemLogin.html')


def EditItemloginInfo(request):
    try:
        # try:
        #     num = request.session['index']
        # except:
        #     num = '1'
        # try:
        #     pageSep = request.session['pageSep']
        # except:
        #     pageSep = 10
        if request.method == "POST":
            try:
                UserName=request.POST.get('user')
                UserPass=request.POST.get('pwd')
                q = a_i.objects.get(admin_name=UserName)
                name = q.admin_name
                pwd  = q.admin_password
                if UserName == name and check_password(UserPass,pwd) is True:
                    request.session['username'] = UserName    #定义session“username”字段并令session中username字段值为登录的用户名
                    request.session['is_login'] = True        #定义session“is_login”字段并令该字段值为"True"表示会话已经创建           
                    item_sn = request.session['item_sn']
                    item_now_user_workid = request.session['item_pass_user_workid']
                    ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn)
                    ItemDetailData = ItemDetailDataView.getItemDetailData()
                    return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)
                    #return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
                else:
                    info = '用户名或密码错误！'
                    return render(request, 'Kpi/EditItemLogin.html', {'userinfo': {'info': info}})
            except:
                info = '登录信息不能为空！'
                return render(request, 'Kpi/EditItemLogin.html', {'userinfo': {'info': info}})
    except Exception as e:
        print(e)

def EditItem(request):
    if request.session.get('is_login', None):
        try:
            num = request.session['index']
        except:
            num = '1'
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10
        if request.method == "POST":
            name = request.session['username']
            try:
                action = request.POST.get('action')
                if action == "编辑":
                    item_sn = request.POST.get('item_sn')
                    item_now_user_workid = request.POST.get('item_now_user_workid')
                    request.session['item_sn'] = item_sn
                    request.session['item_pass_user_workid'] = item_now_user_workid
                    ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn)
                    ItemDetailData = ItemDetailDataView.getItemDetailData()
                    return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)
                if action == "删除":
                    item_sn = request.POST.get('item_sn')
                    item_now_user_workid = request.POST.get('item_now_user_workid')
                    DeleteItemInfoView = DeleteItemInfo( name = name, item_sn = item_sn, num = num, pageSep = pageSep, item_now_user_workid = item_now_user_workid )
                    DeleteItemInfoData = DeleteItemInfoView.DeleteItemInfoData()
                    return render(request, 'Kpi/showmanageiteminfo.html', DeleteItemInfoData)
            except:
                pass

def Moditem(request):
    if request.session.get('is_login', None):
        if request.method == "POST":
            action = request.POST.get('action')
            item_sn = request.session['item_sn']
            name = request.session['username']
            item_pass_user_workid = request.session['item_pass_user_workid']
            item_change_date = request.POST.get('item_change_date')
            item_statu = request.POST.get('item_statu')
            item_change_location = request.POST.get('item_change_location')
            item_now_user = request.POST.get('item_now_user')
            item_now_user_workid = request.POST.get('item_now_user_workid')
            item_change_info = request.POST.get('item_change_info')
            item_pass_info = i_i.objects.get( item_sn = item_sn ).item_info
            change_info_user = request.session['username']
            if action == "修改":                
                if item_statu == '在用':
                    try:
                        if ( item_now_user != '' and item_now_user_workid != '' ):
                            u_i_i.objects.filter( user_name = item_now_user )[0]  # 判断现用户是否存在，以及是否为空
                            testItemStatu = i_i.objects.get( item_sn = item_sn ).item_statu
                            if testItemStatu != '报废':
                                getModedItemInfoView = getModedItemInfo( name = name, item_sn = item_sn , item_change_date = item_change_date,
                                                                        item_statu = item_statu, item_change_location = item_change_location, 
                                                                        item_now_user = item_now_user, item_now_user_workid = item_now_user_workid,
                                                                        item_change_info = item_change_info, item_pass_user_workid = item_pass_user_workid, item_pass_info = item_pass_info, change_info_user = change_info_user)                    
                                getModedItemInfoData = getModedItemInfoView.getModedItemsData()
                                return render(request, 'Kpi/showedititeminfo.html', getModedItemInfoData)
                            else:
                                info = '{}资产信息未变更，已报废！'.format(item_now_user)   # 避免闲置库存多加
                                ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
                                ItemDetailData = ItemDetailDataView.getItemDetailData()
                                ItemDetailData['userinfo']['info'] = info
                                return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)
                        else:
                            info = '资产状态为在用时，资产所属用户不得为空'
                            ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
                            ItemDetailData = ItemDetailDataView.getItemDetailData()
                            ItemDetailData['userinfo']['info'] = info
                            return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)
                    except:
                        info = '用户：{}不存在！资产信息未变更，请填写用户IT资产表里存在的用户！'.format(item_now_user)
                        ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
                        ItemDetailData = ItemDetailDataView.getItemDetailData()
                        ItemDetailData['userinfo']['info'] = info
                        return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)

                if item_statu == '闲置':
                    try:
                        testNowUserExists = u_i_i.objects.filter( user_name = item_now_user )[0]  # 判断现用户是否存在，以及是否为空
                        testItemStatu = i_i.objects.get( item_sn = item_sn ).item_statu
                        print(testNowUserExists)
                        if (testNowUserExists or (item_now_user == '' and item_now_user_workid == '')) and testItemStatu != '闲置' and testItemStatu != '报废':    # 资产状态设置为闲置，现用户可以为空或者存在于现有用户资产列表里的用户但原状态不可为闲置状态
                            getModedItemInfoView = getModedItemInfo( name = name, item_sn = item_sn , item_change_date = item_change_date,
                                                                item_statu = item_statu, item_change_location = item_change_location, 
                                                                item_now_user = item_now_user,  item_now_user_workid = item_now_user_workid,
                                                                item_change_info = item_change_info, item_pass_user_workid = item_pass_user_workid, item_pass_info = item_pass_info, change_info_user = change_info_user)
                            getModedItemInfoData = getModedItemInfoView.getModedItemsData()
                            # info = '{}资产信息已变更！'.format(item_sn)
                            # getModedItemInfoData['userinfo']['info'] = info
                            print(getModedItemInfoData)
                            return render(request, 'Kpi/showedititeminfo.html', getModedItemInfoData)
                        else:
                            info = '{}资产信息未变更状态已经为闲置或已报废！'.format(item_now_user)   # 避免闲置库存多加
                            ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
                            ItemDetailData = ItemDetailDataView.getItemDetailData()
                            ItemDetailData['userinfo']['info'] = info
                            return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)
                    except:
                        info = '用户：{}不存在！资产信息未变更，请填写用户IT资产表里存在的用户！'.format(item_now_user)
                        ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
                        ItemDetailData = ItemDetailDataView.getItemDetailData()
                        ItemDetailData['userinfo']['info'] = info
                        return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)

                if item_statu == '报废':
                    try:
                        testItemStatu = i_i.objects.get( item_sn = item_sn ).item_statu
                        if item_now_user == '' and item_now_user_workid == '' and testItemStatu != '报废':    # 资产状态设置为报废，现用户需要设置为空，直接计入部门的该资产报废数量
                            getModedItemInfoView = getModedItemInfo( name = name, item_sn = item_sn , item_change_date = item_change_date,
                                                                    item_statu = item_statu, item_change_location = item_change_location, 
                                                                    item_now_user = item_now_user, item_now_user_workid = item_now_user_workid,
                                                                    item_change_info = item_change_info, item_pass_user_workid = item_pass_user_workid, item_pass_info = item_pass_info, change_info_user = change_info_user)
                            getModedItemInfoData = getModedItemInfoView.getModedItemsData()
                            info = '{}资产信息已变更！'.format(item_sn)
                            getModedItemInfoData['userinfo']['info'] = info
                            return render(request, 'Kpi/showedititeminfo.html', getModedItemInfoData)
                        else:
                            info = '资产状态设置为报废，无需填写新用户，资产信息未变更！'
                            ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
                            ItemDetailData = ItemDetailDataView.getItemDetailData()
                            ItemDetailData['userinfo']['info'] = info
                            return render(request, 'Kpi/showedititeminfo.html', ItemDetailData)
                    except:
                        pass


def searchitem(request):
    itemSearchSn = request.GET.get('item_sn')
    print(itemSearchSn)
    if request.method == "GET":
        getSearchItemInfoView = getSearchItemInfo( itemSearchSn = itemSearchSn )
        getSearchItemInfoData = getSearchItemInfoView.getSearchItemData()
        try:
            return render(request, 'Kpi/showitemsearchinfo.html', getSearchItemInfoData)
        except:
            pass

def searchitemsn(request):
    if request.session.get('is_login',None):
        num = request.GET.get('index','1')
        request.session['index'] = num
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10 
        name = request.session['username']
        if request.method == "POST":
            SearchSn = request.POST.get('searchitemsn')
            request.session['SearchSn'] = SearchSn
            getSearchItemSnView = getSearchItemSn( num = num, pageSep = pageSep, name = name, SearchSn = SearchSn )
            getSearchItemSnData = getSearchItemSnView.getSearchItemSnData()
            try:
                return render(request, 'Kpi/showmanageiteminfo.html', getSearchItemSnData)
            except:
                pass


def searchitemstock(request):
    if request.session.get('is_login',None):
        num = request.GET.get('index','1')
        request.session['index'] = num
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10 
        name = request.session['username']
        if request.method == "POST":
            searchitemstockinfo = request.POST.get('searchitemstockinfo')
            request.session['searchitemstockinfo'] = searchitemstockinfo
            getSearchItemStockInfoView = getSearchItemStockInfo( num = num, pageSep = pageSep, name = name, searchitemstockinfo = searchitemstockinfo )
            getSearchItemStockInfoData = getSearchItemStockInfoView.getSearchItemStockInfoData()
            try:
                return render(request, 'Kpi/showitemstockinfo.html', getSearchItemStockInfoData)
            except:
                pass

def searchuserinfo(request):
    if request.session.get('is_login',None):
        num = request.GET.get('index','1')
        request.session['index'] = num
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10 
        name = request.session['username']
        if request.method == "POST":
            action = request.POST.get('go')
            if action == '搜索':
                searchuser = request.POST.get('searchuser')
                request.session['searchuser'] = searchuser
                getSearchUserItemsView = getSearchUserItems( num = num, pageSep = pageSep, name = name, searchuser = searchuser )
                getSearchUserItemsData = getSearchUserItemsView.getSearchUserItemsData()
            if action == 'ALL':
                getSearchUserItemsView = getItemInfo(name = name, num = num, pageSep = pageSep)
                getSearchUserItemsData = getSearchUserItemsView.getItemInfoData()
            try:
                return render(request, 'Kpi/showuseriteminfo.html', getSearchUserItemsData)
            except:
                pass

def itemstockinfo(request):
    if request.session.get('is_login',None):
        num = request.GET.get('index','1')
        request.session['index'] = num
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10
        if request.method == "GET":
            name = request.session['username']
            try:
                searchitemstockinfo = request.session['searchitemstockinfo']
                getSearchItemStockInfoView = getSearchItemStockInfo( num = num, pageSep = pageSep, name = name, searchitemstockinfo = searchitemstockinfo )
                getItemStockInfoData = getSearchItemStockInfoView.getSearchItemStockInfoData()
            except:
                getItemStockInfoView = getItemStockInfo(name = name, num = num, pageSep = pageSep)
                getItemStockInfoData = getItemStockInfoView.getItemStockData()
            try:
                return render(request, 'Kpi/showitemstockinfo.html', getItemStockInfoData)
            except:
                pass

def useriteminfo(request):
    if request.session.get('is_login',None):
        num = request.GET.get('index','1')
        request.session['index'] = num
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10 
        if request.method == "GET":
            name = request.session['username']
            try:
                searchuser = request.session['searchuser']
                getSearchUserItemsView = getSearchUserItems( num = num, pageSep = pageSep, name = name, searchuser = searchuser )
                getUserItemsInfoData = getSearchUserItemsView.getSearchUserItemsData()
            except:
                getUserItemsInfoView = getUserItemsInfo(name = name, num = num, pageSep = pageSep)
                getUserItemsInfoData = getUserItemsInfoView.getUserItemsData()
            try:
                return render(request, 'Kpi/showuseriteminfo.html', getUserItemsInfoData)
            except:
                pass

def manageiteminfo(request):
    if request.session.get('is_login',None):
        num = request.GET.get('index','1')
        request.session['index'] = num
        try:
            pageSep = request.session['pageSep']
        except:
            pageSep = 10 
        if request.method == "GET":
            name = request.session['username']
            try:
                SearchSn = request.session['SearchSn']
                getItemInfoView = getSearchItemSn( num = num, pageSep = pageSep, name = name, SearchSn = SearchSn )
                getItemInfoData = getItemInfoView.getSearchItemSnData()
            except:
                getItemInfoView = getItemInfo(name = name, num = num, pageSep = pageSep)
                getItemInfoData = getItemInfoView.getItemInfoData()
            try:
                return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
            except:
                pass

def PageItemInfo(request):
    if request.session.get('is_login',None):
        try:
            num = request.session['index']
        except:
            num = '1'
        if request.method == "POST":
            pageSep = int(request.POST.get('PageLength'))
            request.session['pageSep'] = pageSep    # 将一页展示多少行数存入session
            name = request.session['username']
            try:
                SearchSn = request.session['SearchSn']
                getItemInfoView = getSearchItemSn( num = num, pageSep = pageSep, name = name, SearchSn = SearchSn )
                getItemInfoData = getItemInfoView.getSearchItemSnData()
            except:
                getItemInfoView = getItemInfo(name = name, num = num, pageSep = pageSep)
                getItemInfoData = getItemInfoView.getItemInfoData()
            try:
                return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
            except:
                pass

def PageUserItem(request):
    if request.session.get('is_login',None):
        try:
            num = request.session['index']
        except:
            num = '1'
        if request.method == "POST":
            pageSep = int(request.POST.get('PageLength'))
            request.session['pageSep'] = pageSep    # 将一页展示多少行数存入session
            name = request.session['username']
            getUserItemsInfoView = getUserItemsInfo(name = name, num = num, pageSep = pageSep)
            getUserItemsInfoData = getUserItemsInfoView.getUserItemsData()
            try:
                return render(request, 'Kpi/showuseriteminfo.html', getUserItemsInfoData)
            except:
                pass 

def PageItemStock(request):
    if request.session.get('is_login',None):
        try:
            num = request.session['index']
        except:
            num = '1'
        if request.method == "POST":
            pageSep = int(request.POST.get('PageLength'))
            request.session['pageSep'] = pageSep    # 将一页展示多少行数存入session
            name = request.session['username']
            getItemStockInfoView = getItemStockInfo(name = name, num = num, pageSep = pageSep)
            getItemStockInfoData = getItemStockInfoView.getItemStockData()
            try:
                return render(request, 'Kpi/showitemstockinfo.html', getItemStockInfoData)
            except:
                pass    







