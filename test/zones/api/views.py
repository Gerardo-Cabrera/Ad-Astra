from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from zones.models import Distribution
from zones.models import Zone


@api_view(['POST'])
def edit(request):
    zone_id = request.data.get('id')
    name = request.data.get('name')
    distributions = request.data.get('distributions')

    zone = Zone.objects.filter(pk=zone_id).first()
    
    if not zone:
        return Response('', status=status.HTTP_400_BAD_REQUEST)
    
    for distribution_data in distributions:
        distribution_id = distribution_data.get('id')
        distribution_percentage = distribution_data.get('percentage')

        if distribution_id:
            distribution = Distribution.objects.filter(pk=distribution_id).first()
            if not distribution:
                return Response('', status=status.HTTP_400_BAD_REQUEST)

            distribution.percentage = distribution_percentage
            distribution.save()
        else:
            distribution = Distribution.objects.create(percentage=distribution_percentage, zone=zone)

    zone.name = name
    zone.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete(request, id):
    try:
        distribution = Distribution.objects.get(pk=id)
        distribution.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Distribution.DoesNotExist:
        return Response({'error': 'Distribution not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
