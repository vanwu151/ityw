from django.db import models
import django.utils.timezone as timezone
import datetime
# Create your models here.

class admininfo(models.Model):
	admin_name = models.CharField(max_length=20)
	admin_password = models.CharField(max_length=128, default="")
	
	def __str__(self):
		return self.admin_name

class useritemsinfo(models.Model):
	user_name = models.CharField(max_length=50) # = item_now_user
	user_workid = models.CharField(max_length=20, default="")
	user_location = models.CharField(max_length=50, default="")  # 用户资产现在所在位置 = item_location
	user_pc_sn = models.CharField(max_length=2000)
	user_notebook_sn = models.CharField(max_length=4000)
	user_phone_sn = models.CharField(max_length=1500)
	user_pad_sn = models.CharField(max_length=1500)
	user_monitor_sn = models.CharField(max_length=2000)
	user_phone_num = models.CharField(max_length=1500)
	user_wechat_name = models.CharField(max_length=1000)
	user_qianniu_name = models.CharField(max_length=1000)
	user_otheritems = models.CharField(max_length=5000)

	def __str__(self):
		return self.user_name


class iteminfo(models.Model):
	item_inbound_date = models.DateTimeField('更新时间', default=timezone.now)   # 资产记录入库时间
	item_name = models.CharField(max_length=20)
	item_kind = models.CharField(max_length=20)   #资产种类（pc\notebook\phone\pad\phonenum\wechat\qianniu\other）
	item_statu = models.CharField(max_length=2, default="")  #资产状态是否闲置
	item_sn = models.CharField(max_length=50)    #SN号\手机号\微信号...
	item_now_user = models.CharField(max_length=50)   # 资产现在所属用户
	item_now_user_workid = models.CharField(max_length=20, default="")
	item_location = models.CharField(max_length=50, default="")  # 资产现在所在位置  =  item_change_location
	item_info = models.CharField(max_length=1000) 

class itemchangeinfo(models.Model):
	item_change_date = models.DateTimeField('更新时间', default=timezone.now)
	item_name = models.CharField(max_length=50)
	item_statu = models.CharField(max_length=2, default="")  #资产状态是否闲置
	item_sn = models.CharField(max_length=50)   #SN号\手机号\微信号...
	item_change_location = models.CharField(max_length=50, default="")   
	item_pass_user = models.CharField(max_length=20)
	item_now_user = models.CharField(max_length=20)   # = item_now_user
	item_now_user_workid = models.CharField(max_length=20, default="")
	item_change_info = models.CharField(max_length=500)
	item_pass_info = models.CharField(max_length=1000)
	change_info_user = models.CharField(max_length=20)
	add_item_info = models.CharField(max_length=50, default="")
	del_item_info = models.CharField(max_length=50, default="")

	def __str__(self):
		return self.item_name

class itemstock(models.Model):
	item_kind = models.CharField(max_length=20)
	item_stock_location = models.CharField(max_length=50, default="")  #对应IT资产库存位置 = item_location AND item_statu = '闲置'
	item_stock_num = models.IntegerField(blank=True, null=True)
	item_destory_num = models.IntegerField(blank=True, null=True)
#upload.objects.exlude(user_name='admin')