"""
Testes unitários para os widgets do SearchableDropdown
"""

from django.test import TestCase, RequestFactory
from django import forms
from django.template.loader import render_to_string
from recoveredperispirit.django.django_searchable_dropdown.widgets import (
    SearchableDropdownWidget,
    SearchableDropdownMultipleWidget,
    SearchableDropdownAjaxWidget,
    SearchableDropdownWithInfoWidget
)
from recoveredperispirit.django.django_searchable_dropdown.utils import dropdown_config


class TestSearchableDropdownWidget(TestCase):
    """Testes para o widget SearchableDropdownWidget"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.widget = SearchableDropdownWidget()
        
        # Limpar configurações
        dropdown_config.configs.clear()
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão"""
        widget = SearchableDropdownWidget()
        
        self.assertEqual(widget.dropdown_type, 'default')
        self.assertEqual(widget.placeholder, 'Selecione uma opção')
        self.assertEqual(widget.search_placeholder, 'Digite para buscar...')
        self.assertEqual(widget.no_results_text, 'Nenhum resultado encontrado')
        self.assertEqual(widget.min_search_length, 1)
        self.assertEqual(widget.max_results, 50)
        self.assertIsNone(widget.ajax_url)
        self.assertTrue(widget.allow_clear)
        self.assertFalse(widget.allow_create)
    
    def test_init_with_custom_values(self):
        """Testa inicialização com valores customizados"""
        widget = SearchableDropdownWidget(
            dropdown_type='custom',
            placeholder='Selecione',
            search_placeholder='Buscar...',
            no_results_text='Nada encontrado',
            min_search_length=2,
            max_results=20,
            ajax_url='/api/search/',
            allow_clear=False,
            allow_create=True
        )
        
        self.assertEqual(widget.dropdown_type, 'custom')
        self.assertEqual(widget.placeholder, 'Selecione')
        self.assertEqual(widget.search_placeholder, 'Buscar...')
        self.assertEqual(widget.no_results_text, 'Nada encontrado')
        self.assertEqual(widget.min_search_length, 2)
        self.assertEqual(widget.max_results, 20)
        self.assertEqual(widget.ajax_url, '/api/search/')
        self.assertFalse(widget.allow_clear)
        self.assertTrue(widget.allow_create)
    
    def test_init_with_config_from_type(self):
        """Testa inicialização usando configuração do tipo"""
        # Registrar configuração
        dropdown_config.register_type('test_type', {
            'placeholder': 'Config Placeholder',
            'search_placeholder': 'Config Search',
            'no_results_text': 'Config No Results',
            'min_search_length': 3,
            'max_results': 15
        })
        
        widget = SearchableDropdownWidget(dropdown_type='test_type')
        
        self.assertEqual(widget.placeholder, 'Config Placeholder')
        self.assertEqual(widget.search_placeholder, 'Config Search')
        self.assertEqual(widget.no_results_text, 'Config No Results')
        self.assertEqual(widget.min_search_length, 3)
        self.assertEqual(widget.max_results, 15)
    
    def test_render_basic(self):
        """Testa renderização básica"""
        choices = [
            ('1', 'Opção 1'),
            ('2', 'Opção 2'),
            ('3', 'Opção 3')
        ]
        
        widget = SearchableDropdownWidget(choices=choices)
        html = widget.render('test_field', '2')
        
        # Verifica se contém elementos essenciais
        self.assertIn('searchable-dropdown', html)
        self.assertIn('dropdown-display', html)
        self.assertIn('dropdown-menu', html)
        self.assertIn('search-input', html)
        self.assertIn('options-container', html)
        self.assertIn('Opção 1', html)
        self.assertIn('Opção 2', html)
        self.assertIn('Opção 3', html)
        
        # Verifica se o select está oculto
        self.assertIn('style="display: none;"', html)
    
    def test_render_with_attrs(self):
        """Testa renderização com atributos adicionais"""
        widget = SearchableDropdownWidget()
        attrs = {'class': 'custom-class', 'id': 'custom-id'}
        
        html = widget.render('test_field', '', attrs)
        
        self.assertIn('custom-id', html)
        self.assertIn('searchable-dropdown', html)
        self.assertIn('data-type="default"', html)
    
    def test_render_with_ajax_url(self):
        """Testa renderização com URL AJAX"""
        widget = SearchableDropdownWidget(ajax_url='/api/search/')
        html = widget.render('test_field', '')
        
        self.assertIn('data-ajax-url="/api/search/"', html)
    
    def test_render_with_boolean_attrs(self):
        """Testa renderização com atributos booleanos"""
        widget = SearchableDropdownWidget(
            allow_clear=False,
            allow_create=True
        )
        html = widget.render('test_field', '')
        
        self.assertIn('data-allow-clear="false"', html)
        self.assertIn('data-allow-create="true"', html)
    
    def test_get_context(self):
        """Testa obtenção do contexto"""
        widget = SearchableDropdownWidget(
            dropdown_type='test',
            placeholder='Teste'
        )
        
        context = widget.get_context('test_field', 'value', {})
        
        self.assertEqual(context['name'], 'test_field')
        self.assertEqual(context['value'], 'value')
        self.assertEqual(context['dropdown_type'], 'test')
        self.assertEqual(context['placeholder'], 'Teste')
        self.assertIn('widget', context)
    
    def test_render_with_selected_value(self):
        """Testa renderização com valor selecionado"""
        choices = [
            ('1', 'Opção 1'),
            ('2', 'Opção 2')
        ]
        
        widget = SearchableDropdownWidget(choices=choices)
        html = widget.render('test_field', '2')
        
        # Verifica se o valor selecionado está marcado no select oculto
        self.assertIn('selected', html)
        self.assertIn('value="2"', html)


class TestSearchableDropdownMultipleWidget(TestCase):
    """Testes para o widget SearchableDropdownMultipleWidget"""
    
    def setUp(self):
        self.widget = SearchableDropdownMultipleWidget()
    
    def test_init_inheritance(self):
        """Testa herança da classe pai"""
        widget = SearchableDropdownMultipleWidget(
            dropdown_type='multiple',
            max_selections=5
        )
        
        self.assertEqual(widget.dropdown_type, 'multiple')
        self.assertEqual(widget.max_selections, 5)
    
    def test_render_multiple_attributes(self):
        """Testa renderização com atributos de múltipla seleção"""
        widget = SearchableDropdownMultipleWidget(max_selections=3)
        html = widget.render('test_field', ['1', '2'])
        
        # Verifica atributos de múltipla seleção
        self.assertIn('multiple', html)
        self.assertIn('data-max-selections="3"', html)
        self.assertIn('searchable-dropdown-multiple', html)
    
    def test_render_multiple_selected_values(self):
        """Testa renderização com múltiplos valores selecionados"""
        choices = [
            ('1', 'Opção 1'),
            ('2', 'Opção 2'),
            ('3', 'Opção 3')
        ]
        
        widget = SearchableDropdownMultipleWidget(choices=choices)
        html = widget.render('test_field', ['1', '3'])
        
        # Verifica se os valores selecionados estão marcados
        self.assertIn('selected', html)
        self.assertIn('selected', html)
        self.assertNotIn('value="2" selected', html)


class TestSearchableDropdownAjaxWidget(TestCase):
    """Testes para o widget SearchableDropdownAjaxWidget"""
    
    def setUp(self):
        self.widget = SearchableDropdownAjaxWidget()
    
    def test_init_ajax_specific(self):
        """Testa inicialização com parâmetros específicos do AJAX"""
        widget = SearchableDropdownAjaxWidget(
            dropdown_type='ajax',
            delay=500
        )
        
        self.assertEqual(widget.dropdown_type, 'ajax')
        self.assertEqual(widget.delay, 500)
    
    def test_render_ajax_attributes(self):
        """Testa renderização com atributos AJAX"""
        widget = SearchableDropdownAjaxWidget(delay=300)
        html = widget.render('test_field', '')
        
        self.assertIn('data-delay="300"', html)
    
    def test_template_name(self):
        """Testa nome do template"""
        widget = SearchableDropdownAjaxWidget()
        self.assertEqual(widget.template_name, 'django_searchable_dropdown/widget_ajax.html')


class TestSearchableDropdownWithInfoWidget(TestCase):
    """Testes para o widget SearchableDropdownWithInfoWidget"""
    
    def setUp(self):
        self.widget = SearchableDropdownWithInfoWidget()
    
    def test_init_info_specific(self):
        """Testa inicialização com parâmetros específicos de informações"""
        widget = SearchableDropdownWithInfoWidget(
            dropdown_type='info',
            info_url='/api/info/{id}/',
            info_container_id='info-container'
        )
        
        self.assertEqual(widget.dropdown_type, 'info')
        self.assertEqual(widget.info_url, '/api/info/{id}/')
        self.assertEqual(widget.info_container_id, 'info-container')
    
    def test_render_info_attributes(self):
        """Testa renderização com atributos de informações"""
        widget = SearchableDropdownWithInfoWidget(
            info_url='/api/info/{id}/',
            info_container_id='info-container'
        )
        html = widget.render('test_field', '')
        
        self.assertIn('data-info-url="/api/info/{id}/"', html)
        self.assertIn('data-info-container="info-container"', html)
    
    def test_template_name(self):
        """Testa nome do template"""
        widget = SearchableDropdownWithInfoWidget()
        self.assertEqual(widget.template_name, 'django_searchable_dropdown/widget_with_info.html')


class TestWidgetIntegration(TestCase):
    """Testes de integração dos widgets"""
    
    def setUp(self):
        self.factory = RequestFactory()
        
        # Limpar configurações
        dropdown_config.configs.clear()
        
        # Registrar configuração de teste
        dropdown_config.register_type('test_type', {
            'placeholder': 'Teste Placeholder',
            'search_placeholder': 'Teste Search',
            'no_results_text': 'Teste No Results',
            'min_search_length': 2,
            'max_results': 10
        })
    
    def test_widget_with_form_integration(self):
        """Testa integração do widget com formulário Django"""
        class TestForm(forms.Form):
            field = forms.ChoiceField(
                choices=[('1', 'Opção 1'), ('2', 'Opção 2')],
                widget=SearchableDropdownWidget(
                    dropdown_type='test_type',
                    placeholder='Custom Placeholder'
                )
            )
        
        form = TestForm()
        html = form.as_p()
        
        # Verifica se o widget foi renderizado corretamente
        self.assertIn('searchable-dropdown', html)
        self.assertIn('Custom Placeholder', html)
        self.assertIn('Opção 1', html)
        self.assertIn('Opção 2', html)
    
    def test_multiple_widget_with_form(self):
        """Testa widget de múltipla seleção com formulário"""
        class MultipleForm(forms.Form):
            field = forms.MultipleChoiceField(
                choices=[('1', 'Opção 1'), ('2', 'Opção 2')],
                widget=SearchableDropdownMultipleWidget(
                    max_selections=3
                )
            )
        
        form = MultipleForm()
        html = form.as_p()
        
        self.assertIn('searchable-dropdown-multiple', html)
        self.assertIn('data-max-selections="3"', html)
    
    def test_widget_with_choices_and_queryset(self):
        """Testa widget com choices e queryset"""
        # Simular queryset
        choices = [('1', 'Item 1'), ('2', 'Item 2')]
        
        widget = SearchableDropdownWidget(choices=choices)
        html = widget.render('test_field', '1')
        
        self.assertIn('Item 1', html)
        self.assertIn('Item 2', html)
        self.assertIn('selected', html)
    
    def test_widget_attributes_preservation(self):
        """Testa preservação de atributos do widget"""
        attrs = {
            'class': 'form-control',
            'id': 'test-id',
            'data-custom': 'custom-value'
        }
        
        widget = SearchableDropdownWidget()
        html = widget.render('test_field', '', attrs)
        
        self.assertIn('test-id', html)
        self.assertIn('test-id', html)
        self.assertIn('data-custom="custom-value"', html)
    
    def test_widget_error_handling(self):
        """Testa tratamento de erros no widget"""
        # Teste com choices vazias
        widget = SearchableDropdownWidget(choices=[])
        html = widget.render('test_field', '')
        
        # Deve renderizar sem erros
        self.assertIn('searchable-dropdown', html)
        self.assertIn('options-container', html)
    
    def test_widget_with_special_characters(self):
        """Testa widget com caracteres especiais"""
        choices = [
            ('1', 'Opção com "aspas"'),
            ('2', 'Opção com & símbolos'),
            ('3', 'Opção com <tags>')
        ]
        
        widget = SearchableDropdownWidget(choices=choices)
        html = widget.render('test_field', '1')
        
        # Verifica se caracteres especiais foram escapados corretamente
        self.assertIn('Opção com &quot;aspas&quot;', html)
        self.assertIn('Opção com &amp; símbolos', html)
        self.assertIn('Opção com &lt;tags&gt;', html)
