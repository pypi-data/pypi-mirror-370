from django.apps import AppConfig
from django.conf import settings


class SearchableDropdownConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recoveredperispirit.django.django_searchable_dropdown'
    verbose_name = 'Searchable Dropdown'

    def ready(self):
        """Configurações iniciais quando a app é carregada"""
        # Importar configurações padrão
        try:
            from .utils import dropdown_config
            
            # Configurações padrão do sistema
            default_configs = getattr(settings, 'SEARCHABLE_DROPDOWN_CONFIG', {})
            
            # Registrar tipos padrão se não estiverem configurados
            if not dropdown_config.get_all_configs():
                # Configuração padrão para atividades
                dropdown_config.register_type('activity', {
                    'placeholder': 'Selecione uma atividade',
                    'search_placeholder': 'Digite o nome da atividade...',
                    'no_results_text': 'Nenhuma atividade encontrada',
                    'min_search_length': 2,
                    'max_results': 20,
                })
                
                # Configuração padrão para agendamentos
                dropdown_config.register_type('schedule', {
                    'placeholder': 'Selecione um agendamento',
                    'search_placeholder': 'Digite o nome do agendamento...',
                    'no_results_text': 'Nenhum agendamento encontrado',
                    'min_search_length': 2,
                    'max_results': 20,
                })
                
                # Configuração padrão genérica
                dropdown_config.register_type('default', {
                    'placeholder': default_configs.get('default_placeholder', 'Selecione uma opção'),
                    'search_placeholder': default_configs.get('default_search_placeholder', 'Digite para buscar...'),
                    'no_results_text': default_configs.get('default_no_results_text', 'Nenhum resultado encontrado'),
                    'min_search_length': default_configs.get('min_search_length', 1),
                    'max_results': default_configs.get('max_results', 50),
                })
        except ImportError:
            # Se não conseguir importar, não faz nada
            pass
