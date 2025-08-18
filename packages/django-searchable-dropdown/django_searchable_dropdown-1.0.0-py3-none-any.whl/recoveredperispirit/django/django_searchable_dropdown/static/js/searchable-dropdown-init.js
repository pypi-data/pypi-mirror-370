/**
 * Utilitário para inicialização automática do SearchableDropdown
 * Este arquivo centraliza a lógica de inicialização para evitar duplicação de código
 */

// Verificar se já foi inicializado para evitar redeclaração
if (typeof window.SEARCHABLE_DROPDOWN_INITIALIZED !== 'undefined') {
    console.log('SearchableDropdown já foi inicializado, pulando...');
} else {
    // Configurações padrão para diferentes contextos
    const SEARCHABLE_DROPDOWN_CONFIGS = {
        // Configuração padrão para atividades
        activity: {
            placeholder: 'Selecione uma atividade',
            searchPlaceholder: 'Digite para buscar atividades...',
            noResultsText: 'Nenhuma atividade encontrada'
        },
        
        // Configuração para agendamentos
        schedule: {
            placeholder: 'Selecione um agendamento',
            searchPlaceholder: 'Digite para buscar agendamentos...',
            noResultsText: 'Nenhum agendamento encontrado'
        },
        
        // Configuração para cidades
        city: {
            placeholder: 'Selecione uma cidade',
            searchPlaceholder: 'Digite para buscar cidades...',
            noResultsText: 'Nenhuma cidade encontrada'
        },
        
        // Configuração para categorias
        category: {
            placeholder: 'Selecione uma categoria',
            searchPlaceholder: 'Digite para buscar categorias...',
            noResultsText: 'Nenhuma categoria encontrada'
        },
        
        // Configuração genérica
        default: {
            placeholder: 'Selecione uma opção',
            searchPlaceholder: 'Digite para buscar...',
            noResultsText: 'Nenhum resultado encontrado'
        }
    };

    /**
     * Inicializa todos os SearchableDropdowns na página
     * @param {Object} customConfigs - Configurações customizadas por tipo
     */
    function initializeSearchableDropdowns(customConfigs = {}) {
        function attemptInitialization() {
            if (typeof SearchableDropdown === 'undefined') {
                setTimeout(attemptInitialization, 100);
                return;
            }
            
            const dropdowns = document.querySelectorAll('.searchable-dropdown');
            
            // Filtrar dropdowns que não são do Bootstrap
            const filteredDropdowns = Array.from(dropdowns).filter(dropdown => {
                // Excluir qualquer elemento dentro do navbar
                if (dropdown.closest('.navbar-nav')) {
                    return false;
                }
                
                // Excluir elementos com data-bs-toggle
                if (dropdown.closest('[data-bs-toggle]')) {
                    return false;
                }
                
                // Excluir elementos com classe dropdown do Bootstrap
                if (dropdown.closest('.dropdown')) {
                    return false;
                }
                
                return true;
            });
            
            if (filteredDropdowns.length === 0) {
                setTimeout(attemptInitialization, 200);
                return;
            }
            
            filteredDropdowns.forEach((dropdownElement, index) => {
                // Verificar se já foi inicializado
                if (dropdownElement.classList.contains('initialized')) {
                    return;
                }
                
                try {
                    // Determinar o tipo de dropdown baseado em atributos ou contexto
                    const dropdownType = dropdownElement.getAttribute('data-type') || 'default';
                    const config = customConfigs[dropdownType] || SEARCHABLE_DROPDOWN_CONFIGS[dropdownType] || SEARCHABLE_DROPDOWN_CONFIGS.default;
                    
                    // Permitir override via data attributes
                    const placeholder = dropdownElement.getAttribute('data-placeholder') || config.placeholder;
                    const searchPlaceholder = dropdownElement.getAttribute('data-search-placeholder') || config.searchPlaceholder;
                    const noResultsText = dropdownElement.getAttribute('data-no-results-text') || config.noResultsText;
                    
                    const dropdown = new SearchableDropdown(dropdownElement, {
                        placeholder,
                        searchPlaceholder,
                        noResultsText
                    });
                    
                    // Marcar como inicializado
                    dropdownElement.classList.add('initialized');
                    
                    // Disparar evento customizado para notificar que o dropdown foi inicializado
                    dropdownElement.dispatchEvent(new CustomEvent('searchable-dropdown:initialized', {
                        detail: { dropdown, config: { placeholder, searchPlaceholder, noResultsText } }
                    }));
                    
                } catch (error) {
                    console.error('Erro ao inicializar dropdown:', error);
                }
            });
        }
        
        // Tentar inicialização imediatamente
        attemptInitialization();
    }

    /**
     * Inicializa um SearchableDropdown específico
     * @param {HTMLElement} element - Elemento do dropdown
     * @param {Object} config - Configuração específica
     */
    function initializeSingleSearchableDropdown(element, config = {}) {
        if (typeof SearchableDropdown === 'undefined') {
            return null;
        }
        
        try {
            const dropdown = new SearchableDropdown(element, config);
            return dropdown;
        } catch (error) {
            return null;
        }
    }

    /**
     * Configura event listeners para integração com formulários Django
     * @param {HTMLElement} dropdownElement - Elemento do dropdown
     * @param {string} selectId - ID do select original
     * @param {Function} onChangeCallback - Callback para mudanças
     */
    function setupDjangoFormIntegration(dropdownElement, selectId, onChangeCallback = null) {
        const selectElement = document.getElementById(selectId);
        
        if (!selectElement) {
            return;
        }
        
        // Event listener para o SearchableDropdown
        dropdownElement.addEventListener('dropdown:change', (e) => {
            const value = e.detail.value;
            const text = e.detail.text;
            
            // Atualizar o select original para manter compatibilidade com Django
            selectElement.value = value;
            
            // Disparar evento change no select para ativar outros listeners
            selectElement.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Executar callback se fornecido
            if (onChangeCallback && typeof onChangeCallback === 'function') {
                onChangeCallback(value, text, e);
            }
        });
        
        // Sincronizar valor inicial se o select já tem um valor
        if (selectElement.value) {
            const selectedOption = selectElement.options[selectElement.selectedIndex];
            if (selectedOption) {
                const selectedTextElement = dropdownElement.querySelector('.selected-text');
                if (selectedTextElement) {
                    selectedTextElement.textContent = selectedOption.textContent;
                }
            }
        }
    }

    /**
     * Configuração específica para a tela de agendamento
     */
    function setupSchedulePageIntegration() {
        const activityDropdown = document.querySelector('.searchable-dropdown');
        const activitySelect = document.getElementById('id_activity');
        
        if (activityDropdown && activitySelect) {
            setupDjangoFormIntegration(activityDropdown, 'id_activity', (value, text) => {
                // Aqui você pode adicionar lógica específica para a tela de agendamento
            });
        }
    }

    // Auto-inicialização quando o DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initializeSearchableDropdowns();
        });
    } else {
        // DOM já está pronto
        initializeSearchableDropdowns();
    }

    // Exportar funções para uso global
    window.SearchableDropdownUtils = {
        initialize: initializeSearchableDropdowns,
        initializeSingle: initializeSingleSearchableDropdown,
        setupDjangoFormIntegration,
        setupSchedulePageIntegration,
        configs: SEARCHABLE_DROPDOWN_CONFIGS
    };
    
    // Marcar como inicializado
    window.SEARCHABLE_DROPDOWN_INITIALIZED = true;
}
