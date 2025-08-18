"""
URLs de teste para os testes de integração
"""

from django.urls import path
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from test_app.models import TestModel


@require_http_methods(["GET"])
def search_options(request, dropdown_type):
    """View de teste para busca de opções"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'options': []})
    
    queryset = TestModel.objects.filter(
        name__icontains=query,
        active=True
    )[:10]
    
    options = []
    for obj in queryset:
        options.append({
            'value': obj.id,
            'text': obj.name
        })
    
    return JsonResponse({'options': options})


@require_http_methods(["GET"])
def get_option_info(request, dropdown_type, option_id):
    """View de teste para informações da opção"""
    try:
        obj = TestModel.objects.get(id=option_id, active=True)
        data = {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'category': obj.category
        }
        return JsonResponse(data)
    except TestModel.DoesNotExist:
        return JsonResponse({'error': 'Item não encontrado'}, status=404)


urlpatterns = [
    path('search/<str:dropdown_type>/', search_options, name='search_options'),
    path('info/<str:dropdown_type>/<int:option_id>/', get_option_info, name='get_option_info'),
]
