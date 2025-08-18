/**
 * SearchableDropdown - Componente reutilizável de dropdown com busca
 * 
 * Uso:
 * <div class="searchable-dropdown" data-placeholder="Selecione uma opção">
 *     <input type="hidden" name="selected_value" id="selected_value">
 *     <div class="dropdown-display">
 *         <span class="selected-text">Selecione uma opção</span>
 *         <i class="bi bi-chevron-down"></i>
 *     </div>
 *     <div class="dropdown-menu">
 *         <div class="search-container">
 *             <input type="text" class="search-input" placeholder="Digite para buscar...">
 *             <i class="bi bi-search"></i>
 *         </div>
 *         <div class="options-container">
 *             <div class="option" data-value="1">Opção 1</div>
 *             <div class="option" data-value="2">Opção 2</div>
 *             <div class="option" data-value="3">Opção 3</div>
 *         </div>
 *     </div>
 * </div>
 */

// Verificar se a classe já existe para evitar redeclaração
if (typeof SearchableDropdown === 'undefined') {
class SearchableDropdown {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            placeholder: 'Selecione uma opção',
            searchPlaceholder: 'Digite para buscar...',
            noResultsText: 'Nenhum resultado encontrado',
            maxHeight: '300px',
            ...options
        };
        
        this.isOpen = false;
        this.selectedValue = null;
        this.selectedText = null;
        
        // Detectar se é múltipla seleção
        this.isMultiple = this.element.classList.contains('searchable-dropdown-multiple');
        this.selectedValues = this.isMultiple ? [] : null;
        this.selectedTexts = this.isMultiple ? [] : null;
        this.maxSelections = this.isMultiple ? 
            parseInt(this.element.getAttribute('data-max-selections')) || null : null;
        
        // Detectar se é AJAX
        this.isAjax = this.element.classList.contains('searchable-dropdown-ajax');
        this.ajaxUrl = this.isAjax ? this.element.getAttribute('data-ajax-url') : null;
        this.ajaxDelay = this.isAjax ? 
            parseInt(this.element.getAttribute('data-delay')) || 300 : 300;
        this.minSearchLength = this.isAjax ? 
            parseInt(this.element.getAttribute('data-min-search-length')) || 2 : 2;
        this.maxResults = this.isAjax ? 
            parseInt(this.element.getAttribute('data-max-results')) || 20 : 20;
        
        // Variáveis para AJAX
        this.ajaxTimeout = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        // Configurar estrutura básica se não existir
        this.setupStructure();
        
        // Elementos DOM
        this.hiddenInput = this.element.querySelector('select');
        this.displayElement = this.element.querySelector('.dropdown-display');
        this.selectedTextElement = this.element.querySelector('.selected-text');
        this.dropdownMenu = this.element.querySelector('.dropdown-menu');
        this.searchInput = this.element.querySelector('.search-input');
        this.optionsContainer = this.element.querySelector('.options-container');
        this.options = this.element.querySelectorAll('.dropdown-option');
        
        // Verificar se todos os elementos necessários existem
        if (!this.displayElement || !this.dropdownMenu || !this.searchInput || !this.optionsContainer) {
            return;
        }
        
        // Event listeners
        this.bindEvents();
        
        // Configurar valor inicial
        this.updateDisplay();
        
        // Marcar como inicializado
        this.element.classList.add('initialized');
    }
    
    setupStructure() {
        // Não fazer nada se a estrutura já existe (template já fornece)
        // Apenas verificar se os elementos necessários existem
        if (!this.element.querySelector('.dropdown-display')) {
            console.warn('SearchableDropdown: Estrutura básica não encontrada');
        }
    }
    
    bindEvents() {
        // Verificar se os elementos necessários existem antes de adicionar event listeners
        if (!this.displayElement || !this.searchInput || !this.optionsContainer) {
            return;
        }
        
        // Toggle dropdown
        this.displayElement.addEventListener('click', (e) => {
            // Verificar se não é um dropdown do Bootstrap
            if (e.target.closest('.navbar-nav') || 
                e.target.closest('[data-bs-toggle]') ||
                e.target.closest('.dropdown') ||
                e.target.closest('.nav-link')) {
                return; // Não interferir com dropdowns do Bootstrap
            }
            
            e.preventDefault();
            e.stopPropagation();
            this.toggle();
        });
        
        // Busca
        this.searchInput.addEventListener('input', (e) => {
            if (this.isAjax) {
                this.handleAjaxSearch(e.target.value);
            } else {
                this.filterOptions(e.target.value);
            }
        });
        
        // Seleção de opção
        this.optionsContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('dropdown-option')) {
                this.selectOption(e.target);
            }
        });
        
        // Fechar ao clicar fora (versão simplificada)
        if (!this._documentClickHandler) {
            this._documentClickHandler = (e) => {
                // Não interferir com dropdowns do Bootstrap
                if (e.target.closest('.navbar-nav') || 
                    e.target.closest('[data-bs-toggle]') ||
                    e.target.closest('.dropdown') ||
                    e.target.closest('.nav-link')) {
                    return;
                }
                
                // Simples: só fechar se clicou fora do próprio dropdown
                if (!this.element.contains(e.target)) {
                    this.close();
                }
            };
            
            document.addEventListener('click', this._documentClickHandler);
        }
        
        // Navegação com teclado
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // Botões de ação para múltipla seleção
        if (this.isMultiple) {
            const selectAllBtn = this.element.querySelector('.select-all');
            const clearAllBtn = this.element.querySelector('.clear-all');
            
            if (selectAllBtn) {
                selectAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.selectAll();
                });
            }
            
            if (clearAllBtn) {
                clearAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.clearAll();
                });
            }
        }
        
        // Focar no input de busca quando abrir
        this.element.addEventListener('dropdown:open', () => {
            setTimeout(() => {
                if (this.searchInput) {
                    this.searchInput.focus();
                }
            }, 100);
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        if (!this.displayElement || !this.searchInput) {
            return;
        }
        
        this.isOpen = true;
        this.element.classList.add('open');
        
        // Forçar display block no dropdown menu
        if (this.dropdownMenu) {
            this.dropdownMenu.style.display = 'block';
            this.dropdownMenu.style.visibility = 'visible';
            this.dropdownMenu.style.opacity = '1';
            this.dropdownMenu.style.transform = 'translateY(0)';
        }
        
        const chevronDown = this.displayElement.querySelector('.bi-chevron-down');
        if (chevronDown) {
            chevronDown.classList.replace('bi-chevron-down', 'bi-chevron-up');
        }
        
        // Limpar busca
        this.searchInput.value = '';
        this.filterOptions('');
        
        // Disparar evento
        this.element.dispatchEvent(new CustomEvent('dropdown:open'));
    }
    
    close() {
        if (!this.displayElement) {
            return;
        }
        
        this.isOpen = false;
        this.element.classList.remove('open');
        
        // Forçar display none no dropdown menu
        if (this.dropdownMenu) {
            this.dropdownMenu.style.display = 'none';
            this.dropdownMenu.style.visibility = 'hidden';
            this.dropdownMenu.style.opacity = '0';
            this.dropdownMenu.style.transform = 'translateY(-10px)';
        }
        
        const chevronUp = this.displayElement.querySelector('.bi-chevron-up');
        if (chevronUp) {
            chevronUp.classList.replace('bi-chevron-up', 'bi-chevron-down');
        }
        
        // Disparar evento
        this.element.dispatchEvent(new CustomEvent('dropdown:close'));
    }
    
    filterOptions(searchTerm) {
        if (!this.optionsContainer) {
            return;
        }
        
        const options = this.optionsContainer.querySelectorAll('.dropdown-option:not(.no-results)');
        let hasVisibleOptions = false;
        
        options.forEach(option => {
            const text = option.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            
            option.style.display = matches ? 'block' : 'none';
            if (matches) hasVisibleOptions = true;
        });
        
        // Mostrar mensagem de "nenhum resultado" se necessário
        let noResultsElement = this.optionsContainer.querySelector('.no-results');
        if (!hasVisibleOptions) {
            if (!noResultsElement) {
                noResultsElement = document.createElement('div');
                noResultsElement.className = 'dropdown-option no-results';
                noResultsElement.textContent = searchTerm ? 
                    (this.options.noResultsText || 'Nenhum item correspondente') : 
                    'Nenhum item disponível';
                this.optionsContainer.appendChild(noResultsElement);
            } else {
                noResultsElement.textContent = searchTerm ? 
                    (this.options.noResultsText || 'Nenhum item correspondente') : 
                    'Nenhum item disponível';
            }
            noResultsElement.style.display = 'block';
        } else if (noResultsElement) {
            noResultsElement.style.display = 'none';
        }
    }
    
    handleAjaxSearch(searchTerm) {
        if (!this.ajaxUrl || !this.optionsContainer) {
            return;
        }
        
        // Limpar timeout anterior
        if (this.ajaxTimeout) {
            clearTimeout(this.ajaxTimeout);
        }
        
        // Verificar comprimento mínimo
        if (searchTerm.length < this.minSearchLength) {
            this.clearAjaxOptions();
            return;
        }
        
        // Configurar timeout para evitar muitas requisições
        this.ajaxTimeout = setTimeout(() => {
            this.performAjaxSearch(searchTerm);
        }, this.ajaxDelay);
    }
    
    performAjaxSearch(searchTerm) {
        if (this.isLoading) {
            return;
        }
        
        this.isLoading = true;
        this.showLoadingIndicator();
        
        // Construir URL com parâmetros
        const url = new URL(this.ajaxUrl, window.location.origin);
        url.searchParams.set('q', searchTerm);
        
        fetch(url.toString())
            .then(response => {
                return response.json();
            })
            .then(data => {
                this.hideLoadingIndicator();
                this.populateAjaxOptions(data.results || []);
                this.isLoading = false;
            })
            .catch(error => {
                this.hideLoadingIndicator();
                this.showAjaxError();
                this.isLoading = false;
            });
    }
    
    showLoadingIndicator() {
        const loadingIndicator = this.element.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'block';
        }
    }
    
    hideLoadingIndicator() {
        const loadingIndicator = this.element.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
    
    populateAjaxOptions(results) {
        if (!this.optionsContainer) {
            return;
        }
        
        // Limpar opções existentes
        this.clearAjaxOptions();
        
        if (results.length === 0) {
            this.showNoResults();
            return;
        }
        
        // Adicionar novas opções
        results.forEach(result => {
            const optionElement = document.createElement('div');
            optionElement.className = 'dropdown-option';
            optionElement.setAttribute('data-value', result.id);
            optionElement.textContent = result.text;
            
            this.optionsContainer.appendChild(optionElement);
        });
        
        // Atualizar select hidden
        this.updateHiddenSelect(results);
    }
    
    clearAjaxOptions() {
        if (!this.optionsContainer) {
            return;
        }
        
        // Remover apenas opções dinâmicas (não as iniciais)
        const dynamicOptions = this.optionsContainer.querySelectorAll('.dropdown-option:not([data-initial])');
        dynamicOptions.forEach(option => option.remove());
        
        // Limpar select hidden
        if (this.hiddenInput) {
            this.hiddenInput.innerHTML = '';
        }
    }
    
    showNoResults() {
        if (!this.optionsContainer) {
            return;
        }
        
        const noResultsElement = document.createElement('div');
        noResultsElement.className = 'dropdown-option no-results';
        noResultsElement.textContent = this.options.noResultsText || 'Nenhum resultado encontrado';
        this.optionsContainer.appendChild(noResultsElement);
    }
    
    showAjaxError() {
        if (!this.optionsContainer) {
            return;
        }
        
        const errorElement = document.createElement('div');
        errorElement.className = 'dropdown-option error';
        errorElement.textContent = 'Erro ao buscar resultados';
        this.optionsContainer.appendChild(errorElement);
    }
    
    updateHiddenSelect(results) {
        if (!this.hiddenInput) {
            return;
        }
        
        // Limpar opções existentes
        this.hiddenInput.innerHTML = '';
        
        // Adicionar opção vazia
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = this.options.placeholder || 'Selecione uma opção';
        this.hiddenInput.appendChild(emptyOption);
        
        // Adicionar opções dos resultados
        results.forEach(result => {
            const option = document.createElement('option');
            option.value = result.id;
            option.textContent = result.text;
            this.hiddenInput.appendChild(option);
        });
    }
    
    selectOption(optionElement) {
        const value = optionElement.getAttribute('data-value');
        const text = optionElement.textContent.trim();
        
        if (this.isMultiple) {
            // Lógica para seleção múltipla
            const index = this.selectedValues.indexOf(value);
            
            if (index > -1) {
                // Desmarcar se já está selecionado
                this.selectedValues.splice(index, 1);
                this.selectedTexts.splice(index, 1);
                optionElement.classList.remove('selected');
            } else {
                // Verificar limite máximo
                if (this.maxSelections && this.selectedValues.length >= this.maxSelections) {
                    return; // Não permitir mais seleções
                }
                
                // Marcar como selecionado
                this.selectedValues.push(value);
                this.selectedTexts.push(text);
                optionElement.classList.add('selected');
            }
            
            // Atualizar select
            if (this.hiddenInput) {
                // Limpar todas as seleções
                this.hiddenInput.querySelectorAll('option').forEach(option => {
                    option.selected = false;
                });
                
                // Marcar as opções selecionadas
                this.selectedValues.forEach(selectedValue => {
                    const option = this.hiddenInput.querySelector(`option[value="${selectedValue}"]`);
                    if (option) {
                        option.selected = true;
                    }
                });
                
                // Disparar evento change no select para notificar o Django
                this.hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            
            // Atualizar display
            this.updateDisplay();
            
            // Não fechar o dropdown para permitir múltiplas seleções
            // this.close();
            
            // Disparar evento de mudança
            this.element.dispatchEvent(new CustomEvent('dropdown:change', {
                detail: { 
                    values: this.selectedValues, 
                    texts: this.selectedTexts,
                    isMultiple: true
                }
            }));
        } else {
            // Lógica para seleção única
            this.selectedValue = value;
            this.selectedText = text;
            
            // Atualizar select
            if (this.hiddenInput) {
                this.hiddenInput.value = value;
                // Marcar a opção correta como selecionada no select
                const option = this.hiddenInput.querySelector(`option[value="${value}"]`);
                if (option) {
                    option.selected = true;
                }
            }
            
            // Atualizar display
            this.updateDisplay();
            
            // Fechar dropdown
            this.close();
            
            // Disparar evento de mudança
            this.element.dispatchEvent(new CustomEvent('dropdown:change', {
                detail: { value, text }
            }));
        }
    }
    
    updateDisplay() {
        if (this.selectedTextElement) {
            if (this.isMultiple) {
                if (this.selectedTexts.length > 0) {
                    this.selectedTextElement.textContent = this.selectedTexts.join(', ');
                } else {
                    this.selectedTextElement.textContent = this.options.placeholder;
                }
            } else {
                this.selectedTextElement.textContent = this.selectedText || this.options.placeholder;
            }
        }
    }
    
    handleKeyboardNavigation(e) {
        if (!this.optionsContainer) {
            return;
        }
        
        const visibleOptions = Array.from(this.optionsContainer.querySelectorAll('.dropdown-option:not([style*="display: none"])'));
        const currentIndex = visibleOptions.findIndex(option => option.classList.contains('highlighted'));
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.highlightOption(visibleOptions, currentIndex + 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.highlightOption(visibleOptions, currentIndex - 1);
                break;
            case 'Enter':
                e.preventDefault();
                const highlightedOption = this.optionsContainer.querySelector('.dropdown-option.highlighted');
                if (highlightedOption) {
                    this.selectOption(highlightedOption);
                }
                break;
            case 'Escape':
                this.close();
                break;
        }
    }
    
    highlightOption(visibleOptions, newIndex) {
        if (!this.optionsContainer) {
            return;
        }
        
        // Remover highlight anterior
        this.optionsContainer.querySelectorAll('.dropdown-option.highlighted').forEach(option => {
            option.classList.remove('highlighted');
        });
        
        // Adicionar highlight ao novo item
        if (visibleOptions.length > 0) {
            const index = Math.max(0, Math.min(newIndex, visibleOptions.length - 1));
            visibleOptions[index].classList.add('highlighted');
            visibleOptions[index].scrollIntoView({ block: 'nearest' });
        }
    }
    
    // Métodos públicos
    getValue() {
        return this.selectedValue;
    }
    
    getText() {
        return this.selectedText;
    }
    
    setValue(value) {
        const option = this.optionsContainer.querySelector(`[data-value="${value}"]`);
        if (option) {
            this.selectOption(option);
        }
    }
    
    clear() {
        if (this.isMultiple) {
            this.selectedValues = [];
            this.selectedTexts = [];
            // Remover classe selected de todas as opções
            this.optionsContainer.querySelectorAll('.dropdown-option.selected').forEach(option => {
                option.classList.remove('selected');
            });
        } else {
            this.selectedValue = null;
            this.selectedText = null;
        }
        
        if (this.hiddenInput) {
            if (this.isMultiple) {
                // Desmarcar todas as opções no select
                this.hiddenInput.querySelectorAll('option').forEach(option => {
                    option.selected = false;
                });
            } else {
                this.hiddenInput.value = '';
                // Desmarcar todas as opções no select
                this.hiddenInput.querySelectorAll('option').forEach(option => {
                    option.selected = false;
                });
            }
        }
        this.updateDisplay();
    }
    
    selectAll() {
        if (!this.isMultiple) return;
        
        this.selectedValues = [];
        this.selectedTexts = [];
        
        // Selecionar todas as opções visíveis
        const visibleOptions = this.optionsContainer.querySelectorAll('.dropdown-option:not([style*="display: none"])');
        visibleOptions.forEach(option => {
            const value = option.getAttribute('data-value');
            const text = option.textContent.trim();
            
            if (!this.selectedValues.includes(value)) {
                this.selectedValues.push(value);
                this.selectedTexts.push(text);
                option.classList.add('selected');
            }
        });
        
        // Atualizar select
        if (this.hiddenInput) {
            this.hiddenInput.querySelectorAll('option').forEach(option => {
                option.selected = this.selectedValues.includes(option.value);
            });
        }
        
        this.updateDisplay();
        
        // Disparar evento
        this.element.dispatchEvent(new CustomEvent('dropdown:change', {
            detail: { 
                values: this.selectedValues, 
                texts: this.selectedTexts,
                isMultiple: true
            }
        }));
    }
    
    clearAll() {
        this.clear();
        
        // Disparar evento
        if (this.isMultiple) {
            this.element.dispatchEvent(new CustomEvent('dropdown:change', {
                detail: { 
                    values: [], 
                    texts: [],
                    isMultiple: true
                }
            }));
        }
    }
    
    // Adicionar opções dinamicamente
    addOption(value, text) {
        const optionElement = document.createElement('div');
        optionElement.className = 'dropdown-option';
        optionElement.setAttribute('data-value', value);
        optionElement.textContent = text;
        
        this.optionsContainer.appendChild(optionElement);
        this.options = this.element.querySelectorAll('.dropdown-option');
    }
    
    // Remover opção
    removeOption(value) {
        const option = this.optionsContainer.querySelector(`[data-value="${value}"]`);
        if (option) {
            option.remove();
            this.options = this.element.querySelectorAll('.dropdown-option');
        }
    }
    
    // Método para limpar event listeners
    destroy() {
        if (this._documentClickHandler) {
            document.removeEventListener('click', this._documentClickHandler);
            this._documentClickHandler = null;
        }
        
        // Remover classe de inicializado
        this.element.classList.remove('initialized');
    }
}

// Expor a classe globalmente
window.SearchableDropdown = SearchableDropdown;

// Auto-inicialização removida para evitar conflito com searchable-dropdown-init.js
// A inicialização agora é feita pelo searchable-dropdown-init.js

// Função global para criar dropdowns programaticamente
window.createSearchableDropdown = function(element, options) {
    return new SearchableDropdown(element, options);
};
} // Fechamento do if (typeof SearchableDropdown === 'undefined')
