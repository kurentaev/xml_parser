import json
from rest_framework.response import Response
from rest_framework.views import APIView
from webapp.models import Individuals


class CheckUser(APIView):

    def get(self, request):
        parsed_data = json.loads(request.body.decode('utf-8'))
        pairs_count = sum(len(d.items()) for d in parsed_data)
        if pairs_count == 3:
            if 'first_name' in parsed_data[0] and 'second_name' in parsed_data[0] and 'third_name' in parsed_data[0]:
                users = Individuals.objects.filter(first_name__icontains=parsed_data[0]['first_name'],
                                                   second_name__icontains=parsed_data[0]['second_name'],
                                                   third_name__icontains=parsed_data[0]['third_name'])
                if len(users) > 0:
                    return Response({'answer': 'Положительный ответ'})
                else:
                    return Response({'answer': 'Отрицательный ответ'})
            else:
                return Response({'answer': 'Некорректные поля для поиска'})
        else:
            return Response({'answer': 'Недостаточно полей для поиска'})
