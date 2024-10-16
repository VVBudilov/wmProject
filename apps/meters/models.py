from django.db import models


class House (models.Model):
    house_address = models.CharField(max_length=255)

    def __str__(self):
        return f'Дом: {self.house_address} [{self.id}]'


class Flat (models.Model):
    flat_number = models.CharField(max_length=10)
    flat_area = models.IntegerField()
    flat_house = models.ForeignKey(House, related_name='flats', on_delete=models.PROTECT, null=True)

    class Meta:
        unique_together = ['flat_number', 'flat_house']

    def __str__(self):
        return f'Квартира №{self.flat_number}[{self.id}]; площадью: {self.flat_area} кв.м; в доме: {self.flat_house.house_address}'


class WaterMeter (models.Model):
    wm_inv = models.CharField(max_length=50)
    wm_flat = models.ForeignKey(Flat, related_name='meters', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return (f'Счетчик №{self.wm_inv}[{self.id}]; '
                f'установлен в квартире: {self.wm_flat.flat_house.house_address}, '
                f'{self.wm_flat.flat_number}')


class MeterValues (models.Model):
    mv_value = models.IntegerField()
    mv_month = models.IntegerField()
    mv_meter = models.ForeignKey(WaterMeter, related_name='values', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return (f'Показания за {self.mv_month} месяц - {self.mv_value}; '
                f'по счетчику №{self.mv_meter.wm_inv}[{self.id}]; '
                f'установленному в квартире: {self.mv_meter.wm_flat.flat_house.house_address}, '
                f'{self.mv_meter.wm_flat.flat_number}')


class Tariff (models.Model):
    tariff_value = models.DecimalField(max_digits=6, decimal_places=2)
    tariff_desc = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.tariff_desc} [{self.id}] - {self.tariff_value} рублей'


class Calculations (models.Model):
    calc_month = models.IntegerField()
    calc_status = models.CharField(max_length=10)
    calc_odn_value = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    calc_ind_value = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    calc_start = models.CharField(max_length=50)
    calc_end = models.CharField(max_length=50)
    calc_errors = models.TextField(default='')
    calc_warnings = models.TextField(default='')
    calc_house = models.ForeignKey(House, related_name='calculations', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f'Месяц: {self.calc_month}; {self.calc_house} [{self.id}] '

