"""
Testes de integração para o SearchableDropdown
"""

import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
# Import será feito após configuração do Django
from django.db import models
from django.http import JsonResponse
from recoveredperispirit.django.django_searchable_dropdown.forms import (
    SearchableDropdownField,
    SearchableDropdownMultipleField,
    SearchableDropdownWithInfoField
)
from recoveredperispirit.django.django_searchable_dropdown.utils import dropdown_config


from .test_models import TestModel


class TestIntegrationViews(TestCase):
    """Testes de integração para views"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        # Criar usuário de teste
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Criar instâncias de teste
        self.obj1 = TestModel.objects.create(
            name='Item 1',
            description='Descrição do item 1',
            active=True,
            category='tech'
        )
        self.obj2 = TestModel.objects.create(
            name='Item 2',
            description='Descrição do item 2',
            active=True,
            category='sports'
        )
        self.obj3 = TestModel.objects.create(
            name='Item 3',
            description='Descrição do item 3',
            active=False,
            category='tech'
        )
        
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_search_options_view(self):
        """Testa view de busca de opções"""
        # Simular view de busca
        def search_options(request, dropdown_type):
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
        
        # Teste com query válida
        request = self.factory.get('/search/test/?q=Item')
        response = search_options(request, 'test')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['options']), 2)  # Item 1 e Item 2
        
        # Teste com query muito curta
        request = self.factory.get('/search/test/?q=a')
        response = search_options(request, 'test')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['options']), 0)
    
    def test_get_option_info_view(self):
        """Testa view de informações da opção"""
        # Simular view de informações
        def get_option_info(request, dropdown_type, option_id):
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
        
        # Teste com item válido
        request = self.factory.get(f'/info/test/{self.obj1.id}/')
        response = get_option_info(request, 'test', self.obj1.id)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Item 1')
        self.assertEqual(data['category'], 'tech')
        
        # Teste com item inativo
        request = self.factory.get(f'/info/test/{self.obj3.id}/')
        response = get_option_info(request, 'test', self.obj3.id)
        
        self.assertEqual(response.status_code, 404)
    
    def test_form_submission_with_dropdown(self):
        """Testa submissão de formulário com dropdown"""
        from django import forms
        class TestForm(forms.Form):
            item = SearchableDropdownField(
                choices=[(obj.id, obj.name) for obj in TestModel.objects.filter(active=True)],
                required=True
            )
            description = forms.CharField(max_length=200)
        
        # Teste com dados válidos
        form_data = {
            'item': str(self.obj1.id),
            'description': 'Teste de descrição'
        }
        
        form = TestForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['item'], str(self.obj1.id))
        self.assertEqual(form.cleaned_data['description'], 'Teste de descrição')
        
        # Teste com dados inválidos
        form_data = {
            'item': '999',  # ID inexistente
            'description': 'Teste de descrição'
        }
        
        form = TestForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('item', form.errors)
    
    def test_multiple_selection_form(self):
        """Testa formulário com seleção múltipla"""
        from django import forms
        class MultipleForm(forms.Form):
            items = SearchableDropdownMultipleField(
                choices=[(obj.id, obj.name) for obj in TestModel.objects.filter(active=True)],
                max_selections=2
            )
        
        # Teste com seleção válida
        form_data = {
            'items': [str(self.obj1.id), str(self.obj2.id)]
        }
        
        form = MultipleForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data['items']), 2)
        
        # Teste excedendo limite
        form_data = {
            'items': [str(self.obj1.id), str(self.obj2.id), '999']
        }
        
        form = MultipleForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('items', form.errors)


class TestTemplateIntegration(TestCase):
    """Testes de integração com templates"""
    
    def setUp(self):
        self.client = Client()
        
        # Criar instâncias de teste
        self.obj1 = TestModel.objects.create(
            name='Item 1',
            description='Descrição 1',
            active=True
        )
        self.obj2 = TestModel.objects.create(
            name='Item 2',
            description='Descrição 2',
            active=True
        )
        
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_widget_template_rendering(self):
        """Testa renderização do template do widget"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        widget = SearchableDropdownWidget(
            choices=[(obj.id, obj.name) for obj in TestModel.objects.all()],
            dropdown_type='test',
            placeholder='Selecione um item'
        )
        
        html = widget.render('test_field', '')
        
        # Verifica elementos essenciais do template
        self.assertIn('searchable-dropdown', html)
        self.assertIn('dropdown-display', html)
        self.assertIn('dropdown-menu', html)
        self.assertIn('search-input', html)
        self.assertIn('options-container', html)
        self.assertIn('Selecione um item', html)
        self.assertIn('Item 1', html)
        self.assertIn('Item 2', html)
        
        # Verifica se os arquivos estáticos estão incluídos
        self.assertIn('searchable-dropdown.css', html)
        self.assertIn('searchable-dropdown.js', html)
        self.assertIn('searchable-dropdown-init.js', html)
    
    def test_multiple_widget_template_rendering(self):
        """Testa renderização do template do widget de múltipla seleção"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownMultipleWidget
        
        widget = SearchableDropdownMultipleWidget(
            choices=[(obj.id, obj.name) for obj in TestModel.objects.all()],
            max_selections=2
        )
        
        html = widget.render('test_field', [])
        
        # Verifica elementos específicos de múltipla seleção
        self.assertIn('searchable-dropdown-multiple', html)
        self.assertIn('selected-items', html)
        self.assertIn('option-checkbox', html)
        self.assertIn('multiple-actions', html)
        self.assertIn('select-all', html)
        self.assertIn('clear-all', html)
        self.assertIn('data-max-selections="2"', html)
    
    def test_info_widget_template_rendering(self):
        """Testa renderização do template do widget com informações"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWithInfoWidget
        
        widget = SearchableDropdownWithInfoWidget(
            choices=[(obj.id, obj.name) for obj in TestModel.objects.all()],
            info_url='/api/info/{id}/',
            info_container_id='info-container'
        )
        
        html = widget.render('test_field', '')
        
        # Verifica elementos específicos de informações
        self.assertIn('searchable-dropdown-with-info', html)
        self.assertIn('data-info-url="/api/info/{id}/"', html)
        self.assertIn('data-info-container="info-container"', html)
        self.assertIn('dropdown-info-container', html)
        self.assertIn('info-content', html)


class TestJavaScriptIntegration(TestCase):
    """Testes de integração com JavaScript"""
    
    def setUp(self):
        self.client = Client()
        
        # Criar instâncias de teste
        self.obj1 = TestModel.objects.create(
            name='Item 1',
            description='Descrição 1',
            active=True
        )
        
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_widget_data_attributes(self):
        """Testa atributos de dados do widget para JavaScript"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        widget = SearchableDropdownWidget(
            dropdown_type='test',
            placeholder='Selecione',
            search_placeholder='Buscar...',
            no_results_text='Nada encontrado',
            min_search_length=2,
            max_results=20,
            ajax_url='/api/search/',
            allow_clear=True,
            allow_create=False
        )
        
        html = widget.render('test_field', '')
        
        # Verifica atributos de dados
        self.assertIn('data-type="test"', html)
        self.assertIn('data-search-placeholder="Buscar..."', html)
        self.assertIn('data-search-placeholder="Buscar..."', html)
        self.assertIn('data-no-results-text="Nada encontrado"', html)
        self.assertIn('data-min-search-length="2"', html)
        self.assertIn('data-max-results="20"', html)
        self.assertIn('data-ajax-url="/api/search/"', html)
        self.assertIn('data-allow-clear="true"', html)
        self.assertIn('data-allow-create="false"', html)
    
    def test_multiple_widget_data_attributes(self):
        """Testa atributos de dados do widget de múltipla seleção"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownMultipleWidget
        
        widget = SearchableDropdownMultipleWidget(
            max_selections=3
        )
        
        html = widget.render('test_field', [])
        
        self.assertIn('data-max-selections="3"', html)
    
    def test_ajax_widget_data_attributes(self):
        """Testa atributos de dados do widget AJAX"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownAjaxWidget
        
        widget = SearchableDropdownAjaxWidget(
            delay=500
        )
        
        html = widget.render('test_field', '')
        
        self.assertIn('data-delay="500"', html)


class TestConfigurationIntegration(TestCase):
    """Testes de integração com configurações"""
    
    def setUp(self):
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_config_registration_and_usage(self):
        """Testa registro e uso de configurações"""
        # Registrar configuração
        config = {
            'placeholder': 'Config Placeholder',
            'search_placeholder': 'Config Search',
            'no_results_text': 'Config No Results',
            'min_search_length': 3,
            'max_results': 15
        }
        
        dropdown_config.register_type('test_type', config)
        
        # Verificar se foi registrada
        self.assertIn('test_type', dropdown_config.configs)
        self.assertEqual(dropdown_config.get_config('test_type'), config)
        
        # Usar em widget
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        widget = SearchableDropdownWidget(dropdown_type='test_type')
        
        self.assertEqual(widget.placeholder, 'Config Placeholder')
        self.assertEqual(widget.search_placeholder, 'Config Search')
        self.assertEqual(widget.no_results_text, 'Config No Results')
        self.assertEqual(widget.min_search_length, 3)
        self.assertEqual(widget.max_results, 15)
    
    def test_config_override(self):
        """Testa sobrescrita de configurações"""
        # Registrar configuração
        dropdown_config.register_type('test_type', {
            'placeholder': 'Default Placeholder',
            'search_placeholder': 'Default Search'
        })
        
        # Criar widget com sobrescrita
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        widget = SearchableDropdownWidget(
            dropdown_type='test_type',
            placeholder='Custom Placeholder'
        )
        
        # Placeholder deve ser sobrescrito, search_placeholder deve manter o padrão
        self.assertEqual(widget.placeholder, 'Custom Placeholder')
        self.assertEqual(widget.search_placeholder, 'Default Search')
    
    def test_config_update(self):
        """Testa atualização de configurações"""
        # Registrar configuração inicial
        dropdown_config.register_type('test_type', {
            'placeholder': 'Initial',
            'search_placeholder': 'Initial Search'
        })
        
        # Atualizar configuração
        dropdown_config.update_config('test_type', {
            'placeholder': 'Updated',
            'no_results_text': 'Updated No Results'
        })
        
        # Verificar atualização
        config = dropdown_config.get_config('test_type')
        self.assertEqual(config['placeholder'], 'Updated')
        self.assertEqual(config['search_placeholder'], 'Initial Search')
        self.assertEqual(config['no_results_text'], 'Updated No Results')


class TestErrorHandlingIntegration(TestCase):
    """Testes de integração para tratamento de erros"""
    
    def setUp(self):
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_widget_with_invalid_choices(self):
        """Testa widget com choices inválidas"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        # Widget deve funcionar com choices vazias
        widget = SearchableDropdownWidget(choices=[])
        html = widget.render('test_field', '')
        
        self.assertIn('searchable-dropdown', html)
        self.assertIn('options-container', html)
    
    def test_widget_with_special_characters(self):
        """Testa widget com caracteres especiais"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        choices = [
            ('1', 'Opção com "aspas"'),
            ('2', 'Opção com & símbolos'),
            ('3', 'Opção com <tags>'),
            ('4', 'Opção com quebra\nde linha')
        ]
        
        widget = SearchableDropdownWidget(choices=choices)
        html = widget.render('test_field', '1')
        
        # Verifica se caracteres especiais foram tratados corretamente
        self.assertIn('Opção com &quot;aspas&quot;', html)
        self.assertIn('Opção com &amp; símbolos', html)
        self.assertIn('Opção com &lt;tags&gt;', html)
    
    def test_form_validation_errors(self):
        """Testa erros de validação de formulário"""
        from django import forms
        class TestForm(forms.Form):
            field = SearchableDropdownField(
                choices=[('1', 'Opção 1')],
                required=True
            )
        
        # Teste com dados vazios
        form = TestForm({})
        self.assertFalse(form.is_valid())
        self.assertIn('field', form.errors)
        
        # Teste com valor inválido
        form = TestForm({'field': '2'})
        self.assertFalse(form.is_valid())
        self.assertIn('field', form.errors)
    
    def test_multiple_selection_validation_errors(self):
        """Testa erros de validação de seleção múltipla"""
        from django import forms
        class MultipleForm(forms.Form):
            field = SearchableDropdownMultipleField(
                choices=[('1', 'Opção 1'), ('2', 'Opção 2')],
                max_selections=1
            )
        
        # Teste excedendo limite
        form = MultipleForm({'field': ['1', '2']})
        self.assertFalse(form.is_valid())
        self.assertIn('field', form.errors)


class TestPerformanceIntegration(TestCase):
    """Testes de integração para performance"""
    
    def setUp(self):
        # Criar muitos objetos para teste de performance
        for i in range(100):
            TestModel.objects.create(
                name=f'Item {i}',
                description=f'Descrição do item {i}',
                active=True
            )
        
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_widget_with_large_choices(self):
        """Testa widget com muitas opções"""
        from recoveredperispirit.django.django_searchable_dropdown.widgets import SearchableDropdownWidget
        
        choices = [(obj.id, obj.name) for obj in TestModel.objects.all()]
        
        widget = SearchableDropdownWidget(choices=choices)
        html = widget.render('test_field', '')
        
        # Verifica se renderiza sem erros
        self.assertIn('searchable-dropdown', html)
        self.assertIn('options-container', html)
        
        # Verifica se todas as opções estão presentes
        for obj in TestModel.objects.all()[:10]:  # Verifica apenas os primeiros 10
            self.assertIn(obj.name, html)
    
    def test_form_with_large_queryset(self):
        """Testa formulário com queryset grande"""
        from django import forms
        class LargeForm(forms.Form):
            field = SearchableDropdownField(
                queryset=TestModel.objects.all()
            )
        
        form = LargeForm()
        html = form.as_p()
        
        # Verifica se renderiza sem erros
        self.assertIn('searchable-dropdown', html)
        self.assertIn('options-container', html)
