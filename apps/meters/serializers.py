import this

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from meters.models import House, Flat, WaterMeter, MeterValues, Tariff, Calculations
from meters.tasks import house_calc_task


class FlatNewViewSerializer(ModelSerializer):

    class Meta:
        model = Flat
        fields = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['Статус'] = self.status
        representation['Сообщение'] = self.message
        if instance:
            representation['id'] = instance.id
            representation['Номер квартиры'] = instance.flat_number
            representation['Площадь квартиры'] = instance.flat_area
            representation['Дом'] = instance.flat_house.house_address
        return representation


class WaterMeterSerializer(ModelSerializer):
    value = SerializerMethodField()

    def get_value(self, inst):
        month = int(self.context.get('month'))

        # Текущее показание
        value = MeterValues.objects.filter(mv_month=month, mv_meter=inst.id)
        if len(value) < 1:
            return 'Нет текущего показания!'
        current_value = int(value[0].mv_value)

        # Предыдущее показание
        value = MeterValues.objects.filter(mv_month=month - 1, mv_meter=inst.id)
        if len(value) < 1:
            return 'Нет предыдущего показания!'
        prev_value = int(value[0].mv_value)

        delta = current_value - prev_value
        if delta < 0:
            return f'Текущее показание({current_value}) меньше предыдущего({prev_value})!'

        return delta

    current_month = SerializerMethodField()

    def get_current_month(self, inst):
        return self.context.get('month')

    class Meta:
        model = WaterMeter
        fields = ['current_month', 'wm_inv', 'value']


class FlatSerializer(ModelSerializer):
    current_month = SerializerMethodField()

    def get_current_month(self, instance):
        return self.context.get('month')

    flat_meters = SerializerMethodField()

    def get_flat_meters(self, instance):
        meters = WaterMeter.objects.filter(wm_flat=instance.id)
        return WaterMeterSerializer(meters, many=True, context={'month': self.context.get('month')}).data

    class Meta:
        model = Flat
        fields = ['current_month', 'id', 'flat_number', 'flat_area', 'flat_meters']


class HouseSerializer(ModelSerializer):
    current_month_s = SerializerMethodField()

    def get_current_month_s(self, instance):
        return self.month

    house_flats_s = SerializerMethodField()

    def get_house_flats_s(self, inst):
        flats = Flat.objects.filter(flat_house=inst.id)  # Фильтр квартир по id дома
        return FlatSerializer(flats, many=True, context={'month': self.month}).data

    house_flat_numbers_s = SerializerMethodField()

    def get_house_flat_numbers_s(self, instance):
        flats = Flat.objects.filter(flat_house=instance.id)
        flats_str = f'Номера квартир: ['
        for flat in flats:
            flats_str += f'{flat.flat_number}, '
        return f'{flats_str}]'

    house_calculations_s = SerializerMethodField()

    def get_house_calculations_s(self, instance):
        month = self.month
        calc = Calculations.objects.filter(calc_house=instance.id, calc_month=month)
        calcs = {}
        if len(calc) < 1:
            calcs['Статус'] = f'Расчет за месяц - {month},  еще не проводился.'
            calcs['Общедомовые нужды'] = 0
            calcs['Индивидуальное потребление'] = 0
            calcs['Начало расчета'] = ''
            calcs['Окончание расчета'] = ''
        else:
            calcs['Статус'] = calc[0].calc_status
            calcs['Общедомовые нужды'] = calc[0].calc_odn_value
            calcs['Индивидуальное потребление'] = calc[0].calc_ind_value
            calcs['Начало расчета'] = calc[0].calc_start
            calcs['Окончание расчета'] = calc[0].calc_end
        return calcs

    class Meta:
        model = House
        fields = [
            'current_month_s',
            'house_address',
            'house_flat_numbers_s',
            'house_calculations_s',
            'house_flats_s',
        ]


class HouseCalcSerializer(ModelSerializer):
    current_month = SerializerMethodField()

    def get_current_month(self, instance):
        return self.month

    start_calculation = SerializerMethodField()

    def get_start_calculation(self, instance):
        house_calc_task.delay(instance.id, self.month)
        return 'Расчет запущен'

    class Meta:
        model = House
        fields = [
            'current_month',
            'house_address',
            'start_calculation',
        ]
