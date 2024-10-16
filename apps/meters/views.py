from functools import wraps

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from meters.models import House, Flat
from meters.serializers import HouseSerializer, HouseCalcSerializer, FlatNewViewSerializer


class FlatNewView(ModelViewSet):
    queryset = Flat.objects.all()
    serializer_class = FlatNewViewSerializer

    def get_queryset(self):
        house_id = self.request.GET.get("house_id", None)
        house = House.objects.get(id=house_id)

        flat_number = self.request.GET.get("flat_number", None)
        flat_area = self.request.GET.get("flat_area", None)

        try:
            flat = Flat.objects.create(
                flat_number=flat_number,
                flat_area=flat_area,
                flat_house=house
            )

            self.serializer_class.status = 'Successfully'
            self.serializer_class.message = 'Квартира успешно создана'
            return Flat.objects.filter(id=flat.id)

        except Exception as ex:
            msg = f'Произошла ошибка при создании квартиры в доме - {house}. {ex}'
            self.serializer_class.status = 'Error'
            self.serializer_class.message = msg
            print(f'**FlatNewView: {msg}')
            return {'', ''}


class HouseView(ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id']

    def get_queryset(self):
        house_id = self.request.GET.get("id", None)
        if house_id is None:
            raise Exception('Не указан ID дома')

        month = self.request.GET.get("month", None)
        if month is not None:
            self.serializer_class.month = month
            return self.queryset
        else:
            raise Exception('Не указан расчётный месяц')



class HouseCalcView(ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseCalcSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id']

    def get_queryset(self):
        self.serializer_class.month = self.request.GET.get("month", None)
        return self.queryset

