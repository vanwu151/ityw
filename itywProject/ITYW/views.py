# coding=utf-8
import os, re, time, json
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator , PageNotAnInteger, EmptyPage
from django.db.models import Sum
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
                    ItemDetailDataView = getItemDetail( name = name, item_sn = item_sn )
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
                                                                        item_change_info = item_change_info, item_pass_user_workid = item_pass_user_workid)                    
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
                                                                item_change_info = item_change_info, item_pass_user_workid = item_pass_user_workid)
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
                                                                    item_change_info = item_change_info, item_pass_user_workid = item_pass_user_workid)
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
            getItemInfoView = getItemInfo(name = name, num = num, pageSep = pageSep)
            getItemInfoData = getItemInfoView.getItemInfoData()
            try:
                return render(request, 'Kpi/showmanageiteminfo.html', getItemInfoData)
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
            getUserItemsInfoView = getUserItemsInfo(name = name, num = num, pageSep = pageSep)
            getUserItemsInfoData = getUserItemsInfoView.getUserItemsData()
            try:
                return render(request, 'Kpi/showuseriteminfo.html', getUserItemsInfoData)
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
            getItemStockInfoView = getItemStockInfo(name = name, num = num, pageSep = pageSep)
            getItemStockInfoData = getItemStockInfoView.getItemStockData()
            try:
                return render(request, 'Kpi/showitemstockinfo.html', getItemStockInfoData)
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



def Manage(request):
    if request.session.get('is_login',None):
        if request.method == "POST" or request.method == "GET":
            try:
                # info = '用户管理列表'
                m = request.session['username']
                userdic = ui.objects.exclude(user_name = m).exclude(user_name = "admin")
                userlist = []
                rolelist = []
                for i in userdic:
                    userlist.append(i)
                print(userlist)
                for k in userlist:
                    q = ui.objects.get(user_name = k)
                    role = q.user_role
                    rolelist.append(role)
                print(rolelist)
                userroleinfolist=zip(userlist,rolelist)                    #将userlist与rolelist打包成userroleinfolist
                return render(request, 'Kpi/Manage.html', {'userinfo': {'name': m, 'userroleinfolist': userroleinfolist}})
            except:
                pass

def Edit(request):
    if request.session.get('is_login',None):
        if request.method == "POST":
            EditUserName = request.POST.get('username')
            request.session['EditUserName'] = EditUserName                              #定义session“EditUserName”字段并令session中EditUserName字段值为需要编辑的用户名
            print(EditUserName)
            action = request.POST.get('action')
            try:
                try:
                    if action == "编辑":
                        q = ui.objects.get(user_name = EditUserName)
                        phone = q.user_phone
                        department = q.user_department
                        userrole = q.user_role
                        return render(request, 'Kpi/Edituserinfo.html', {'userinfo': {'name': request.session['username'], 'editusername': EditUserName,'phone': phone,'department': department, 'userrole':userrole}})
                except:
                    info = '请勾选需要编辑的用户'            # 未勾选用户名点编辑后的报错提醒
                    m = request.session['username']
                    try:
                        userdic = ui.objects.exclude(user_name = m).exclude(user_name = "admin")
                        userlist = []
                        rolelist = []
                        for i in userdic:
                            userlist.append(i)
                        print(userlist)
                        for k in userlist:
                            q = ui.objects.get(user_name = k)
                            role = q.user_role
                            rolelist.append(role)
                        print(rolelist)
                        userroleinfolist=zip(userlist,rolelist)
                    except:
                        pass
                    return render(request, 'Kpi/Manage.html', {'userinfo': {'info': info, 'name':m, 'userroleinfolist': userroleinfolist}})
                try:
                    if action == "删除":
                        q = ui.objects.get(user_name = EditUserName)
                        q.delete()
                        return redirect('/Manage')
                except:
                    info = '请勾选需要删除的用户'            # 未勾选用户名点编辑后的报错提醒
                    m = request.session['username']
                    try:
                        userdic = ui.objects.exclude(user_name = m).exclude(user_name = "admin")
                        userlist = []
                        rolelist = []
                        for i in userdic:
                            userlist.append(i)
                        print(userlist)
                        for k in userlist:
                            q = ui.objects.get(user_name = k)
                            role = q.user_role
                            rolelist.append(role)
                        print(rolelist)
                        userroleinfolist=zip(userlist,rolelist)
                    except:
                        pass
                    return render(request, 'Kpi/Manage.html', {'userinfo': {'info': info, 'name':m, 'userroleinfolist': userroleinfolist}})
            except:
                pass

def ModRole(request):
    if request.session.get('is_login',None):
        if request.method == "POST":
            try:
                Moduser = request.session['EditUserName']
                print(Moduser)
                q = ui.objects.get(user_name = Moduser)
                Moddepartment = request.POST.get('department')
                Modrole = request.POST.get('role')
                if Moddepartment is not None:
                    q.user_department = Moddepartment
                    q.save()
                else:
                    pass
                if Modrole is not None:    
                    q.user_role = Modrole
                    q.save()
                else:
                    pass
                ModNewPass = request.POST.get('newpass') 
                if ModNewPass != '':
                    NewUserPass = make_password(ModNewPass, None, 'pbkdf2_sha256')
                    q.user_password = NewUserPass
                    q.save()
                    info = Moduser + '密码已更改!'
                else:
                    info = Moduser + '密码未更改!'    
                    pass
                if Modrole is None and ModNewPass == '':
                    info = Moduser + '信息未更改!'    
                name = q.user_name
                phone = q.user_phone
                department = q.user_department
                userrole = q.user_role
                return render(request, 'Kpi/Edituserinfo.html', {'userinfo': {'info': info, 'name': request.session['username'], 'editusername': name,'phone': phone,'department': department, 'userrole':userrole}})
            except:
                pass

def Modinfo(request):
    if request.session.get('is_login',None):
        if request.method == "GET":
            name = request.session['username']
            try:
                department = ui.objects.get( user_name = name).user_department
                phone = ui.objects.get( user_name = name ).user_phone
            except:
                pass
            return render(request, 'Kpi/Modinfo.html', {'userinfo': {'name': name, 'phone': phone, 'department': department}})


def InfoModed(request):
    if request.session.get('is_login',None):
        if request.method == "POST":        
            try:
                m = request.session['username']     #从session中获取用户姓名
                p = request.POST.get('passwd')      #获取前端输入的密码赋给变量p
                q = ui.objects.get(user_name=m)     #以查询条件q：字段user_name值为cookie重保存的用户信息为条件
                department = q.user_department
                phone = q.user_phone
                p2 = q.user_password                #通过查询条件q将用户的密码赋给变量p2
                if check_password(p,p2) is True:                               #当输入的密码p和查询出的密码p2比较后为真       
                    info = m + '信息更改成功！'
                    name = q.user_name                                         #将回传给前端的name字段赋值为通过查询条件q查到的用户名
                    ModPwd = request.POST.get('userinfo_passwd')
                    if ModPwd != '':
                        NewPwd = make_password(ModPwd ,None, 'pbkdf2_sha256')
                        q.user_password = NewPwd
                        q.save()
                        info = m + '密码已更改！'
                    else:
                        pass
                    ModPhone = request.POST.get('phone')
                    if ModPhone != '':                                      #如果获取到的新昵称值不是空的
                        q.user_nickname = ModPhone                          #则将变量ModPhon新号码，更新到数据库user_phone字段
                        q.save()                                               #保存更新
                        phone = q.user_phone                             #将回传给前端的user_phone字段赋值为通过查询条件q查到的昵称
                    else:                                                      #如果获取到的新昵称是空的
                        phone = q.phone                             #则不去更新数据库
                    return render(request, 'Kpi/Modinfo.html', {'userinfo': {'info': info, 'name': name, 'phone': phone, 'department': department}})
                elif check_password(p,p2) is False:
                    info = '密码错误！信息更改失败！'
                    name = q.user_name
                    return render(request, 'Kpi/Modinfo.html', {'userinfo': {'info': info, 'name': name, 'phone': phone, 'department': department}})
                else:
                    info = '用户信息错误！信息更改失败！'
                    name = q.user_name
                    return render(request, 'Kpi/Modinfo.html', {'userinfo': {'info': info, 'name': name, 'phone': phone, 'department': department}})
            except:
                info = '请填入正确的修改信息！'
                name = q.user_name
                return render(request, 'Kpi/Modinfo.html', {'userinfo': {'info': info, 'name': name, 'phone': phone, 'department': department}})





