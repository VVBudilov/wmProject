import time

from meters.models import Flat, WaterMeter, MeterValues, Tariff


def house_total_calculation(house, month, calc=None):
    month = int(month)
    errors = []
    warnings = []

    house_meters_total = 0  # Показания всех счетчиков в квартире
    house_area_total = 0  # Общая площадь всех квартир в доме

    flat_desc = house.house_address
    flats = Flat.objects.filter(flat_house=house.id)  # Все квартиры в доме
    if len(flats) == 0:
        warnings.append(f'В доме {flat_desc} - нет квартир!')

    i = 1
    for flat in flats:
        # Состояние расчета
        if calc is not None:
            print(f'**house_total_calculation: {i} из {len(flats)}')
            calc.calc_status = f'{i} из {len(flats)}'
            calc.calc_errors = list2text(errors)
            calc.calc_warnings = list2text(warnings)
            calc.save()
            i += 1
            time.sleep(20)

        flat_desc = f'Квартира: {flat.flat_number}'
        # Общая площадь
        house_area_total += int(flat.flat_area)

        # Подсчет суммарного индивидуального потребления
        flat_meters = WaterMeter.objects.filter(wm_flat=flat.id)  # Все счетчики в квартере
        if len(flat_meters) == 0:
            warnings.append(f'{flat_desc} - счетчики не зарегистрированы!')
        for meter in flat_meters:
            # Текущее показание
            value = MeterValues.objects.filter(mv_month=month, mv_meter=meter.id)
            meter_desc = f'{flat_desc}, Счетчик: {meter.wm_inv}'
            if len(value) < 1:
                current_value = 0
                errors.append(f'{meter_desc} - нет текущего показания!')
            else:
                current_value = int(value[0].mv_value)

            # Предыдущее показание
            value = MeterValues.objects.filter(mv_month=month - 1, mv_meter=meter.id)
            if len(value) < 1:
                prev_value = 0
                errors.append(f'{meter_desc} - нет предыдущего показания!')
            else:
                prev_value = int(value[0].mv_value)

            if current_value == 0 or prev_value == 0:  # Не учитывается в расчете
                delta = 0
            else:
                delta = current_value - prev_value
                if delta < 0:  # Не учитывается в расчете
                    delta = 0
                    errors.append(
                        f'{meter_desc} - текущее показание({current_value}) меньше предыдущего({prev_value})!')

            house_meters_total += delta

    # Тарифы
    ind_tariff = float(Tariff.objects.filter(tariff_desc='За кубический метр')[0].tariff_value)
    odn_tariff = float(Tariff.objects.filter(tariff_desc='За квадратный метр')[0].tariff_value)

    ind_summ = round(house_meters_total * ind_tariff, 2)
    odn_summ = round(house_area_total * odn_tariff, 2)

    calc.calc_errors = list2text(errors)
    calc.calc_warnings = list2text(warnings)

    return ind_summ, odn_summ


def list2text(messages):
    text = ''
    for m in messages:
        text += m + '\n'
    return text


