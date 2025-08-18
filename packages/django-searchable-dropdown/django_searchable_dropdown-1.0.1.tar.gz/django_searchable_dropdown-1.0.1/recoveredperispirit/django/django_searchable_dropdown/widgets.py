"""
Widgets Django para SearchableDropdown
"""

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .utils import get_dropdown_config


class SearchableDropdownWidget(forms.Select):
    """
    Widget Django para SearchableDropdown
    
    Substitui o select padrão do Django por um dropdown pesquisável
    """
    
    template_name = 'django_searchable_dropdown/widget.html'
    
    def __init__(self, attrs=None, choices=(), dropdown_type=None, 
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False):
        # Usar Select para seleção única
        super().__init__(attrs, choices)
        
        self.dropdown_type = dropdown_type or 'default'
        self.placeholder = placeholder
        self.search_placeholder = search_placeholder
        self.no_results_text = no_results_text
        self.min_search_length = min_search_length
        self.max_results = max_results
        self.ajax_url = ajax_url
        self.allow_clear = allow_clear
        self.allow_create = allow_create
        
        # Obter configurações padrão do tipo
        config = get_dropdown_config(self.dropdown_type)
        
        # Usar configurações padrão se não fornecidas
        if self.placeholder is None:
            self.placeholder = config.get('placeholder', 'Selecione uma opção')
        if self.search_placeholder is None:
            self.search_placeholder = config.get('search_placeholder', 'Digite para buscar...')
        if self.no_results_text is None:
            self.no_results_text = config.get('no_results_text', 'Nenhum resultado encontrado')
        if self.min_search_length is None:
            self.min_search_length = config.get('min_search_length', 1)
        if self.max_results is None:
            self.max_results = config.get('max_results', 50)
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Renderiza o widget
        """
        if attrs is None:
            attrs = {}
        
        # Adicionar classes CSS padrão
        if 'class' in attrs:
            attrs['class'] += ' searchable-dropdown-widget'
        else:
            attrs['class'] = 'searchable-dropdown-widget'
        
        # Adicionar atributos de dados para JavaScript
        attrs.update({
            'data-dropdown-type': self.dropdown_type,
            'data-placeholder': self.placeholder,
            'data-search-placeholder': self.search_placeholder,
            'data-no-results-text': self.no_results_text,
            'data-min-search-length': self.min_search_length,
            'data-max-results': self.max_results,
            'data-allow-clear': str(self.allow_clear).lower(),
            'data-allow-create': str(self.allow_create).lower(),
        })
        
        if self.ajax_url:
            attrs['data-ajax-url'] = self.ajax_url
        
        context = self.get_context(name, value, attrs)
        
        return mark_safe(render_to_string(self.template_name, context))
    
    def get_context(self, name, value, attrs):
        """
        Retorna o contexto para renderização do template
        """
        if attrs is None:
            attrs = {}
        
        context = {
            'widget': self,
            'name': name,
            'value': value,
            'attrs': attrs,
            'dropdown_type': self.dropdown_type,
            'placeholder': self.placeholder,
            'search_placeholder': self.search_placeholder,
            'no_results_text': self.no_results_text,
            'min_search_length': self.min_search_length,
            'max_results': self.max_results,
            'ajax_url': self.ajax_url,
            'allow_clear': self.allow_clear,
            'allow_create': self.allow_create,
        }
        
        return context


class SearchableDropdownMultipleWidget(forms.SelectMultiple):
    """
    Widget para múltipla seleção
    """
    
    template_name = 'django_searchable_dropdown/widget_multiple.html'
    
    def __init__(self, attrs=None, choices=(), dropdown_type=None, 
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, max_selections=None):
        # Garantir que o atributo multiple seja definido
        if attrs is None:
            attrs = {}
        attrs['multiple'] = 'multiple'
        
        # Usar SelectMultiple como classe base
        super().__init__(attrs, choices)
        
        self.dropdown_type = dropdown_type or 'default'
        self.placeholder = placeholder
        self.search_placeholder = search_placeholder
        self.no_results_text = no_results_text
        self.min_search_length = min_search_length
        self.max_results = max_results
        self.ajax_url = ajax_url
        self.allow_clear = allow_clear
        self.allow_create = allow_create
        self.max_selections = max_selections
        
        # Obter configurações padrão do tipo
        config = get_dropdown_config(self.dropdown_type)
        
        # Usar configurações padrão se não fornecidas
        if self.placeholder is None:
            self.placeholder = config.get('placeholder', 'Selecione opções')
        if self.search_placeholder is None:
            self.search_placeholder = config.get('search_placeholder', 'Digite para buscar...')
        if self.no_results_text is None:
            self.no_results_text = config.get('no_results_text', 'Nenhum resultado encontrado')
        if self.min_search_length is None:
            self.min_search_length = config.get('min_search_length', 1)
        if self.max_results is None:
            self.max_results = config.get('max_results', 50)
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Renderiza o widget de múltipla seleção
        """
        if attrs is None:
            attrs = {}
        
        attrs['multiple'] = 'multiple'
        
        # Adicionar classes CSS padrão
        if 'class' in attrs:
            attrs['class'] += ' searchable-dropdown-widget'
        else:
            attrs['class'] = 'searchable-dropdown-widget'
        
        # Adicionar atributos de dados para JavaScript
        attrs.update({
            'data-dropdown-type': self.dropdown_type,
            'data-placeholder': self.placeholder,
            'data-search-placeholder': self.search_placeholder,
            'data-no-results-text': self.no_results_text,
            'data-min-search-length': self.min_search_length,
            'data-max-results': self.max_results,
            'data-allow-clear': str(self.allow_clear).lower(),
            'data-allow-create': str(self.allow_create).lower(),
        })
        
        if self.max_selections:
            attrs['data-max-selections'] = self.max_selections
        
        if self.ajax_url:
            attrs['data-ajax-url'] = self.ajax_url
        
        context = self.get_context(name, value, attrs)
        context['max_selections'] = self.max_selections
        
        return mark_safe(render_to_string(self.template_name, context))
    
    def get_context(self, name, value, attrs):
        """
        Retorna o contexto para renderização do template
        """
        if attrs is None:
            attrs = {}
        
        context = {
            'widget': self,
            'name': name,
            'value': value,
            'attrs': attrs,
            'dropdown_type': self.dropdown_type,
            'placeholder': self.placeholder,
            'search_placeholder': self.search_placeholder,
            'no_results_text': self.no_results_text,
            'min_search_length': self.min_search_length,
            'max_results': self.max_results,
            'ajax_url': self.ajax_url,
            'allow_clear': self.allow_clear,
            'allow_create': self.allow_create,
            'max_selections': self.max_selections,
        }
        
        return context


class SearchableDropdownAjaxWidget(SearchableDropdownWidget):
    """
    Widget para busca AJAX
    """
    
    template_name = 'django_searchable_dropdown/widget_ajax.html'
    
    def __init__(self, attrs=None, choices=(), dropdown_type=None, 
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, delay=300):
        super().__init__(attrs, choices, dropdown_type, placeholder, 
                        search_placeholder, no_results_text, min_search_length,
                        max_results, ajax_url, allow_clear, allow_create)
        
        self.delay = delay
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Renderiza o widget AJAX
        """
        if attrs is None:
            attrs = {}
        
        attrs['data-delay'] = self.delay
        
        context = self.get_context(name, value, attrs)
        context['delay'] = self.delay
        
        return mark_safe(render_to_string(self.template_name, context))


class SearchableDropdownWithInfoWidget(SearchableDropdownWidget):
    """
    Widget que mostra informações adicionais sobre a opção selecionada
    """
    
    template_name = 'django_searchable_dropdown/widget_with_info.html'
    
    def __init__(self, attrs=None, choices=(), dropdown_type=None, 
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, info_url=None,
                 info_container_id=None):
        super().__init__(attrs, choices, dropdown_type, placeholder, 
                        search_placeholder, no_results_text, min_search_length,
                        max_results, ajax_url, allow_clear, allow_create)
        
        self.info_url = info_url
        self.info_container_id = info_container_id
    
    def render(self, name, value, attrs=None, renderer=None):
        """
        Renderiza o widget com informações
        """
        if attrs is None:
            attrs = {}
        
        if self.info_url:
            attrs['data-info-url'] = self.info_url
        
        if self.info_container_id:
            attrs['data-info-container'] = self.info_container_id
        
        context = self.get_context(name, value, attrs)
        context['info_url'] = self.info_url
        context['info_container_id'] = self.info_container_id
        
        return mark_safe(render_to_string(self.template_name, context))
