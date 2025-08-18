"""
Campos de formulário Django para SearchableDropdown
"""

from django import forms
from django.db.models import QuerySet
from .widgets import (
    SearchableDropdownWidget, 
    SearchableDropdownMultipleWidget,
    SearchableDropdownAjaxWidget,
    SearchableDropdownWithInfoWidget
)
from .utils import search_model


class SearchableDropdownField(forms.ChoiceField):
    """
    Campo de formulário Django para SearchableDropdown
    """
    
    widget = SearchableDropdownWidget
    
    def __init__(self, choices=(), queryset=None, dropdown_type=None,
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, required=True,
                 widget=None, label=None, initial=None, help_text='',
                 error_messages=None, show_hidden_initial=False,
                 validators=(), localize=False, disabled=False,
                 label_suffix=None, empty_label="---------"):
        
        # Se um queryset foi fornecido, converter para choices
        if queryset is not None:
            if isinstance(queryset, QuerySet):
                choices = [(obj.pk, str(obj)) for obj in queryset]
            else:
                choices = queryset
        
        # Configurar widget
        if widget is None:
            widget = self.widget(
                dropdown_type=dropdown_type,
                placeholder=placeholder,
                search_placeholder=search_placeholder,
                no_results_text=no_results_text,
                min_search_length=min_search_length,
                max_results=max_results,
                ajax_url=ajax_url,
                allow_clear=allow_clear,
                allow_create=allow_create,
            )
        
        super().__init__(
            choices=choices,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            error_messages=error_messages,
            show_hidden_initial=show_hidden_initial,
            validators=validators,
            localize=localize,
            disabled=disabled,
            label_suffix=label_suffix,
        )
        
        self.empty_label = empty_label
        self.queryset = queryset
        self.dropdown_type = dropdown_type


class SearchableDropdownMultipleField(SearchableDropdownField):
    """
    Campo para múltipla seleção
    """
    
    widget = SearchableDropdownMultipleWidget
    
    def __init__(self, choices=(), queryset=None, dropdown_type=None,
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, max_selections=None,
                 required=True, widget=None, label=None, initial=None, 
                 help_text='', error_messages=None, show_hidden_initial=False,
                 validators=(), localize=False, disabled=False,
                 label_suffix=None, empty_label="---------"):
        
        # Configurar widget para múltipla seleção
        if widget is None:
            widget = self.widget(
                dropdown_type=dropdown_type,
                placeholder=placeholder,
                search_placeholder=search_placeholder,
                no_results_text=no_results_text,
                min_search_length=min_search_length,
                max_results=max_results,
                ajax_url=ajax_url,
                allow_clear=allow_clear,
                allow_create=allow_create,
                max_selections=max_selections,
            )
        
        super().__init__(
            choices=choices,
            queryset=queryset,
            dropdown_type=dropdown_type,
            placeholder=placeholder,
            search_placeholder=search_placeholder,
            no_results_text=no_results_text,
            min_search_length=min_search_length,
            max_results=max_results,
            ajax_url=ajax_url,
            allow_clear=allow_clear,
            allow_create=allow_create,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            error_messages=error_messages,
            show_hidden_initial=show_hidden_initial,
            validators=validators,
            localize=localize,
            disabled=disabled,
            label_suffix=label_suffix,
            empty_label=empty_label,
        )
        
        self.max_selections = max_selections
    
    def clean(self, value):
        """
        Valida múltiplas seleções
        """
        # Converter string para lista se necessário
        if isinstance(value, str):
            try:
                import ast
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                value = [value] if value else []
        
        # Validar cada valor individualmente
        if value:
            for v in value:
                if not self.valid_value(v):
                    raise forms.ValidationError(
                        f'"{v}" não é uma opção válida.'
                    )
        
        if self.max_selections and value:
            if len(value) > self.max_selections:
                raise forms.ValidationError(
                    f'Você pode selecionar no máximo {self.max_selections} opção(ões).'
                )
        
        return value


class SearchableDropdownAjaxField(SearchableDropdownField):
    """
    Campo para busca AJAX
    """
    
    widget = SearchableDropdownAjaxWidget
    
    def __init__(self, choices=(), queryset=None, dropdown_type=None,
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, delay=300,
                 required=True, widget=None, label=None, initial=None, 
                 help_text='', error_messages=None, show_hidden_initial=False,
                 validators=(), localize=False, disabled=False,
                 label_suffix=None, empty_label="---------"):
        
        # Configurar widget AJAX
        if widget is None:
            widget = self.widget(
                dropdown_type=dropdown_type,
                placeholder=placeholder,
                search_placeholder=search_placeholder,
                no_results_text=no_results_text,
                min_search_length=min_search_length,
                max_results=max_results,
                ajax_url=ajax_url,
                allow_clear=allow_clear,
                allow_create=allow_create,
                delay=delay,
            )
        
        super().__init__(
            choices=choices,
            queryset=queryset,
            dropdown_type=dropdown_type,
            placeholder=placeholder,
            search_placeholder=search_placeholder,
            no_results_text=no_results_text,
            min_search_length=min_search_length,
            max_results=max_results,
            ajax_url=ajax_url,
            allow_clear=allow_clear,
            allow_create=allow_create,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            error_messages=error_messages,
            show_hidden_initial=show_hidden_initial,
            validators=validators,
            localize=localize,
            disabled=disabled,
            label_suffix=label_suffix,
            empty_label=empty_label,
        )
        
        self.delay = delay


class SearchableDropdownWithInfoField(SearchableDropdownField):
    """
    Campo que mostra informações adicionais
    """
    
    widget = SearchableDropdownWithInfoWidget
    
    def __init__(self, choices=(), queryset=None, dropdown_type=None,
                 placeholder=None, search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, info_url=None,
                 info_container_id=None, required=True, widget=None, 
                 label=None, initial=None, help_text='', error_messages=None, 
                 show_hidden_initial=False, validators=(), localize=False, 
                 disabled=False, label_suffix=None, empty_label="---------"):
        
        # Configurar widget com informações
        if widget is None:
            widget = self.widget(
                dropdown_type=dropdown_type,
                placeholder=placeholder,
                search_placeholder=search_placeholder,
                no_results_text=no_results_text,
                min_search_length=min_search_length,
                max_results=max_results,
                ajax_url=ajax_url,
                allow_clear=allow_clear,
                allow_create=allow_create,
                info_url=info_url,
                info_container_id=info_container_id,
            )
        
        super().__init__(
            choices=choices,
            queryset=queryset,
            dropdown_type=dropdown_type,
            placeholder=placeholder,
            search_placeholder=search_placeholder,
            no_results_text=no_results_text,
            min_search_length=min_search_length,
            max_results=max_results,
            ajax_url=ajax_url,
            allow_clear=allow_clear,
            allow_create=allow_create,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            error_messages=error_messages,
            show_hidden_initial=show_hidden_initial,
            validators=validators,
            localize=localize,
            disabled=disabled,
            label_suffix=label_suffix,
            empty_label=empty_label,
        )
        
        self.info_url = info_url
        self.info_container_id = info_container_id


class ModelSearchableDropdownField(SearchableDropdownField):
    """
    Campo que busca diretamente em um modelo Django
    """
    
    def __init__(self, model_class, search_fields, value_field='id', 
                 display_field='name', additional_filters=None,
                 choices=(), dropdown_type=None, placeholder=None, 
                 search_placeholder=None, no_results_text=None,
                 min_search_length=None, max_results=None, ajax_url=None,
                 allow_clear=True, allow_create=False, required=True,
                 widget=None, label=None, initial=None, help_text='',
                 error_messages=None, show_hidden_initial=False,
                 validators=(), localize=False, disabled=False,
                 label_suffix=None, empty_label="---------"):
        
        self.model_class = model_class
        self.search_fields = search_fields
        self.value_field = value_field
        self.display_field = display_field
        self.additional_filters = additional_filters or {}
        self.max_results = max_results or 50
        
        # Gerar choices iniciais se não fornecidas
        if not choices and model_class:
            queryset = model_class.objects.filter(**self.additional_filters)
            choices = [(getattr(obj, value_field), str(getattr(obj, display_field))) 
                      for obj in queryset[:max_results or 50]]
        
        super().__init__(
            choices=choices,
            dropdown_type=dropdown_type,
            placeholder=placeholder,
            search_placeholder=search_placeholder,
            no_results_text=no_results_text,
            min_search_length=min_search_length,
            max_results=max_results,
            ajax_url=ajax_url,
            allow_clear=allow_clear,
            allow_create=allow_create,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            error_messages=error_messages,
            show_hidden_initial=show_hidden_initial,
            validators=validators,
            localize=localize,
            disabled=disabled,
            label_suffix=label_suffix,
            empty_label=empty_label,
        )
    
    def search(self, query):
        """
        Realiza busca no modelo
        """
        return search_model(
            self.model_class,
            self.search_fields,
            query,
            self.value_field,
            self.display_field,
            self.additional_filters,
            self.max_results
        )
