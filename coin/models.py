from django.db import models
from django.db.models import Model

# Create your models here.
from django.utils import timezone

coin_type_choice = (
    (1, 'USDT'),
)
price_type_choice = (
    (1, '买入'),
    (2, '卖出'),
)


class User(Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    username = models.CharField(db_column="user_name", max_length=64, null=False)
    password = models.CharField(max_length=64, null=False)
    realName = models.CharField(db_column="real_name", max_length=64, null=False)
    email = models.CharField(max_length=32, null=True)
    phone = models.CharField(max_length=32, null=True)
    createTime = models.DateTimeField(db_column="create_time", null=False, default=timezone.now)
    lastModifyTime = models.DateTimeField(db_column="last_modify_time", null=False, default=timezone.now)

    class Meta:
        db_table = "coin_user"  # 更改表名


class SendConfig(Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="user_id", db_constraint=False,
                             db_index=False)
    sendEmail = models.BooleanField(db_column="send_email", default=True)
    sendSms = models.BooleanField(db_column="send_sms", default=True)
    coinType = models.IntegerField(db_column="coin_type", choices=coin_type_choice, default=1)
    buyPrice = models.DecimalField(db_column="buy_price", max_digits=18, decimal_places=2)
    salePrice = models.DecimalField(db_column="sale_price", max_digits=18, decimal_places=2)
    createTime = models.DateTimeField(db_column="create_time", null=False, default=timezone.now)
    lastModifyTime = models.DateTimeField(db_column="last_modify_time", null=False, default=timezone.now)

    class Meta:
        db_table = "coin_send_config"  # 更改表名


class PriceData(Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="主键")
    merchantName = models.CharField(max_length=64, db_column="merchant_name", null=False, verbose_name="商户名称")
    price = models.DecimalField(max_digits=18, decimal_places=3, db_column="price", verbose_name="价格")
    rate = models.DecimalField(max_digits=18, decimal_places=3, db_column="rate", verbose_name="汇率", default=0)
    recordTime = models.DateTimeField(db_column="record_time", null=False, default=timezone.now, verbose_name="爬取时间")
    coinType = models.IntegerField(db_column="coin_type", choices=coin_type_choice, default=1)
    priceType = models.IntegerField(db_column="price_type", choices=price_type_choice, default=1)

    class Meta:
        db_table = "coin_price_data"


class SystemConfig(Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="主键")
    module_choice = (
        (1, u'邮件'),
        (2, u'短信'),
    )
    module = models.IntegerField(choices=module_choice)
    paramCode = models.CharField(max_length=64, null=False, db_column="param_code")
    paramValue = models.CharField(max_length=64, null=False, db_column="param_value")
    paramDesc = models.CharField(max_length=128, null=False, db_column="param_desc")
    createTime = models.DateTimeField(db_column="create_time", null=False, default=timezone.now)
    lastModifyTime = models.DateTimeField(db_column="last_modify_time", null=False, default=timezone.now)

    class Meta:
        db_table = "coin_system_config"
