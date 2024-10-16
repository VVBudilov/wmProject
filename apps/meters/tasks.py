import datetime

from celery import shared_task

from meters.common import house_total_calculation
from meters.models import House, Calculations


status_done = 'done'


@shared_task
def house_calc_task(house_id, month):
    print(f'**house_calc_task: started for house={house_id}, month={month}')
    house = House.objects.get(id=house_id)
    calcs = Calculations.objects.filter(calc_house=house_id, calc_month=month)
    if len(calcs) == 0:
        calc = Calculations.objects.create(
            calc_month=month,
            calc_house=house
        )
    else:
        calc = calcs[0]
        if calc.calc_status != status_done:
            print(f'**house_calc_task: Расчет по дому: {house_id}, за месяц: {month} уже запущен!')
            return

    calc.calc_status = f'in-progress'
    calc.calc_start = f'{datetime.datetime.now()}'
    calc.calc_end = ''
    calc.calc_odn_value = 0
    calc.calc_ind_value = 0
    calc.calc_errors = ''
    calc.calc_warnings = ''
    calc.save()

    # Расчет...
    calc.calc_ind_value, calc.calc_odn_value = house_total_calculation(house, month, calc)
    calc.calc_status = status_done
    calc.calc_end = f'{datetime.datetime.now()}'
    calc.save()

    print(f'**house_calc_task: finished')


