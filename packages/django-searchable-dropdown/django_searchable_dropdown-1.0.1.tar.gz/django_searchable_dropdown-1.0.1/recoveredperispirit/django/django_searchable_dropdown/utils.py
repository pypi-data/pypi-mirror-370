"""
Utilitários para a biblioteca SearchableDropdown
"""

import json
from django.apps import apps
from django.db.models import Q


class SearchableDropdownConfig:
    """Classe para gerenciar configurações do SearchableDropdown"""
    
    def __init__(self):
        self.configs = {}
        self._initialized = False
    
    def register_type(self, dropdown_type, config):
        """Registra um novo tipo de dropdown"""
        self.configs[dropdown_type] = config
        return self
    
    def get_config(self, dropdown_type):
        """Obtém configuração de um tipo específico"""
        return self.configs.get(dropdown_type, {})
    
    def get_all_configs(self):
        """Retorna todas as configurações"""
        return self.configs.copy()
    
    def update_config(self, dropdown_type, config):
        """Atualiza configuração existente"""
        if dropdown_type in self.configs:
            self.configs[dropdown_type].update(config)
        return self
    
    def remove_type(self, dropdown_type):
        """Remove um tipo de dropdown"""
        if dropdown_type in self.configs:
            del self.configs[dropdown_type]
        return self
    
    def is_initialized(self):
        """Verifica se a configuração foi inicializada"""
        return self._initialized
    
    def set_initialized(self, value=True):
        """Define se a configuração foi inicializada"""
        self._initialized = value


# Instância global
dropdown_config = SearchableDropdownConfig()


class SearchableDropdownQueryBuilder:
    """Classe para construir queries de busca para o SearchableDropdown"""
    
    @staticmethod
    def build_search_query(model_class, search_fields, query, additional_filters=None):
        """
        Constrói uma query de busca para um modelo Django
        
        Args:
            model_class: Classe do modelo Django
            search_fields: Lista de campos para buscar
            query: Termo de busca
            additional_filters: Filtros adicionais (dict)
        
        Returns:
            QuerySet filtrado
        """
        if not query or not search_fields:
            return model_class.objects.none()
        
        # Construir query OR para todos os campos de busca
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        
        # Aplicar filtros adicionais se fornecidos
        queryset = model_class.objects.filter(q_objects)
        
        if additional_filters:
            queryset = queryset.filter(**additional_filters)
        
        return queryset
    
    @staticmethod
    def format_options(queryset, value_field, display_field, max_results=None):
        """
        Formata os resultados do queryset para o formato esperado pelo dropdown
        
        Args:
            queryset: QuerySet com os resultados
            value_field: Campo a ser usado como valor
            display_field: Campo a ser usado como texto de exibição
            max_results: Número máximo de resultados
        
        Returns:
            Lista de dicionários com 'value' e 'text'
        """
        if max_results:
            queryset = queryset[:max_results]
        
        options = []
        for obj in queryset:
            # Obter valor e texto
            value = getattr(obj, value_field)
            text = getattr(obj, display_field)
            
            # Se o display_field for um método, chamá-lo
            if callable(text):
                text = text()
            
            options.append({
                'value': value,
                'text': str(text)
            })
        
        return options


class SearchableDropdownSerializer:
    """Classe para serializar dados do SearchableDropdown"""
    
    @staticmethod
    def serialize_options(options):
        """Serializa lista de opções para JSON"""
        return json.dumps(options, ensure_ascii=False)
    
    @staticmethod
    def serialize_config(config):
        """Serializa configuração para JSON"""
        return json.dumps(config, ensure_ascii=False)
    
    @staticmethod
    def deserialize_options(json_data):
        """Deserializa JSON para lista de opções"""
        try:
            return json.loads(json_data)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def deserialize_config(json_data):
        """Deserializa JSON para configuração"""
        try:
            return json.loads(json_data)
        except (json.JSONDecodeError, TypeError):
            return {}


class SearchableDropdownValidator:
    """Classe para validar configurações e dados do SearchableDropdown"""
    
    @staticmethod
    def validate_config(config):
        """Valida configuração do dropdown"""
        required_fields = ['placeholder', 'search_placeholder', 'no_results_text']
        errors = []
        
        for field in required_fields:
            if field not in config:
                errors.append(f"Campo obrigatório '{field}' não encontrado")
        
        if 'min_search_length' in config and not isinstance(config['min_search_length'], int):
            errors.append("'min_search_length' deve ser um número inteiro")
        
        if 'max_results' in config and not isinstance(config['max_results'], int):
            errors.append("'max_results' deve ser um número inteiro")
        
        return errors
    
    @staticmethod
    def validate_search_query(query, min_length=1):
        """Valida query de busca"""
        if not query or not isinstance(query, str):
            return False, "Query deve ser uma string não vazia"
        
        if len(query.strip()) < min_length:
            return False, f"Query deve ter pelo menos {min_length} caractere(s)"
        
        return True, None
    
    @staticmethod
    def validate_model_config(model_config):
        """Valida configuração de modelo"""
        required_fields = ['model', 'search_fields', 'display_field', 'value_field']
        errors = []
        
        for field in required_fields:
            if field not in model_config:
                errors.append(f"Campo obrigatório '{field}' não encontrado na configuração do modelo")
        
        # Validar se o modelo existe
        if 'model' in model_config:
            try:
                app_label, model_name = model_config['model'].split('.')
                apps.get_model(app_label, model_name)
            except (ValueError, LookupError):
                errors.append(f"Modelo '{model_config['model']}' não encontrado")
        
        return errors


# Funções utilitárias de conveniência
def get_dropdown_config(dropdown_type):
    """Obtém configuração de um tipo de dropdown"""
    return dropdown_config.get_config(dropdown_type)


def register_dropdown_type(dropdown_type, config):
    """Registra um novo tipo de dropdown"""
    return dropdown_config.register_type(dropdown_type, config)


def search_model(model_class, search_fields, query, value_field='id', 
                display_field='name', additional_filters=None, max_results=None):
    """
    Função de conveniência para buscar em um modelo
    
    Args:
        model_class: Classe do modelo Django
        search_fields: Lista de campos para buscar
        query: Termo de busca
        value_field: Campo a ser usado como valor
        display_field: Campo a ser usado como texto de exibição
        additional_filters: Filtros adicionais
        max_results: Número máximo de resultados
    
    Returns:
        Lista de opções formatadas
    """
    # Validar query
    is_valid, error = SearchableDropdownValidator.validate_search_query(query)
    if not is_valid:
        return []
    
    # Construir query
    queryset = SearchableDropdownQueryBuilder.build_search_query(
        model_class, search_fields, query, additional_filters
    )
    
    # Formatar resultados
    return SearchableDropdownQueryBuilder.format_options(
        queryset, value_field, display_field, max_results
    )
