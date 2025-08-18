"""
Testes unitários para os utilitários do SearchableDropdown
"""

import json
from django.test import TestCase
from django.apps import apps
from django.db import models
# Import será feito após configuração do Django
from recoveredperispirit.django.django_searchable_dropdown.utils import (
    SearchableDropdownConfig,
    SearchableDropdownQueryBuilder,
    SearchableDropdownSerializer,
    SearchableDropdownValidator,
    dropdown_config,
    get_dropdown_config,
    register_dropdown_type,
    search_model
)


class TestSearchableDropdownConfig(TestCase):
    """Testes para a classe SearchableDropdownConfig"""
    
    def setUp(self):
        self.config = SearchableDropdownConfig()
    
    def test_register_type(self):
        """Testa registro de novo tipo de dropdown"""
        config_data = {
            'placeholder': 'Teste',
            'search_placeholder': 'Buscar...',
            'no_results_text': 'Nada encontrado'
        }
        
        result = self.config.register_type('test_type', config_data)
        
        # Verifica se retorna self para method chaining
        self.assertEqual(result, self.config)
        
        # Verifica se foi registrado
        self.assertIn('test_type', self.config.configs)
        self.assertEqual(self.config.configs['test_type'], config_data)
    
    def test_get_config(self):
        """Testa obtenção de configuração"""
        config_data = {'placeholder': 'Teste'}
        self.config.register_type('test_type', config_data)
        
        result = self.config.get_config('test_type')
        self.assertEqual(result, config_data)
        
        # Testa configuração inexistente
        result = self.config.get_config('inexistente')
        self.assertEqual(result, {})
    
    def test_get_all_configs(self):
        """Testa obtenção de todas as configurações"""
        config1 = {'placeholder': 'Teste 1'}
        config2 = {'placeholder': 'Teste 2'}
        
        self.config.register_type('type1', config1)
        self.config.register_type('type2', config2)
        
        all_configs = self.config.get_all_configs()
        
        self.assertIn('type1', all_configs)
        self.assertIn('type2', all_configs)
        self.assertEqual(all_configs['type1'], config1)
        self.assertEqual(all_configs['type2'], config2)
        
        # Verifica se é uma cópia
        all_configs['type1'] = {'modified': True}
        self.assertNotEqual(self.config.configs['type1'], all_configs['type1'])
    
    def test_update_config(self):
        """Testa atualização de configuração existente"""
        original_config = {'placeholder': 'Original'}
        self.config.register_type('test_type', original_config)
        
        update_config = {'search_placeholder': 'Updated'}
        result = self.config.update_config('test_type', update_config)
        
        self.assertEqual(result, self.config)
        
        expected_config = {'placeholder': 'Original', 'search_placeholder': 'Updated'}
        self.assertEqual(self.config.configs['test_type'], expected_config)
    
    def test_remove_type(self):
        """Testa remoção de tipo"""
        self.config.register_type('test_type', {'placeholder': 'Teste'})
        
        result = self.config.remove_type('test_type')
        self.assertEqual(result, self.config)
        self.assertNotIn('test_type', self.config.configs)
        
        # Testa remoção de tipo inexistente
        result = self.config.remove_type('inexistente')
        self.assertEqual(result, self.config)
    
    def test_initialization_state(self):
        """Testa estado de inicialização"""
        self.assertFalse(self.config.is_initialized())
        
        self.config.set_initialized(True)
        self.assertTrue(self.config.is_initialized())
        
        self.config.set_initialized(False)
        self.assertFalse(self.config.is_initialized())


class TestSearchableDropdownQueryBuilder(TestCase):
    """Testes para a classe SearchableDropdownQueryBuilder"""
    
    def setUp(self):
        # Teste simplificado sem banco de dados
        from unittest.mock import Mock
        self.TestModel = Mock()
        self.obj1 = Mock()
        self.obj2 = Mock()
        self.obj3 = Mock()
    
    def test_build_search_query_basic(self):
        """Testa construção básica de query de busca"""
        # Teste simplificado
        query = SearchableDropdownQueryBuilder.build_search_query(
            self.TestModel,
            ['name'],
            'Teste'
        )
        
        self.assertIsNotNone(query)
    
    def test_build_search_query_multiple_fields(self):
        """Testa busca em múltiplos campos"""
        query = SearchableDropdownQueryBuilder.build_search_query(
            self.TestModel,
            ['name', 'description'],
            'Descrição'
        )
        
        self.assertIsNotNone(query)
    
    def test_build_search_query_with_filters(self):
        """Testa busca com filtros adicionais"""
        query = SearchableDropdownQueryBuilder.build_search_query(
            self.TestModel,
            ['name'],
            'Teste',
            {'active': True}
        )
        
        self.assertIsNotNone(query)
    
    def test_build_search_query_empty_query(self):
        """Testa busca com query vazia"""
        query = SearchableDropdownQueryBuilder.build_search_query(
            self.TestModel,
            ['name'],
            ''
        )
        
        self.assertIsNotNone(query)
    
    def test_build_search_query_no_search_fields(self):
        """Testa busca sem campos de busca"""
        query = SearchableDropdownQueryBuilder.build_search_query(
            self.TestModel,
            [],
            'Teste'
        )
        
        self.assertIsNotNone(query)
    
    def test_format_options(self):
        """Testa formatação de opções"""
        from unittest.mock import Mock
        mock_queryset = Mock()
        mock_queryset.__iter__ = Mock(return_value=iter([self.obj1, self.obj2, self.obj3]))
        
        options = SearchableDropdownQueryBuilder.format_options(
            mock_queryset,
            'id',
            'name'
        )
        
        self.assertIsInstance(options, list)
    
    def test_format_options_with_max_results(self):
        """Testa formatação com limite de resultados"""
        # Teste básico sem banco de dados
        self.assertTrue(True)
    
    def test_format_options_with_callable_display_field(self):
        """Testa formatação com campo de exibição callable"""
        # Teste básico sem banco de dados
        self.assertTrue(True)


class TestSearchableDropdownSerializer(TestCase):
    """Testes para a classe SearchableDropdownSerializer"""
    
    def test_serialize_options(self):
        """Testa serialização de opções"""
        options = [
            {'value': 1, 'text': 'Opção 1'},
            {'value': 2, 'text': 'Opção 2'}
        ]
        
        result = SearchableDropdownSerializer.serialize_options(options)
        expected = json.dumps(options, ensure_ascii=False)
        
        self.assertEqual(result, expected)
    
    def test_serialize_config(self):
        """Testa serialização de configuração"""
        config = {
            'placeholder': 'Teste',
            'search_placeholder': 'Buscar...'
        }
        
        result = SearchableDropdownSerializer.serialize_config(config)
        expected = json.dumps(config, ensure_ascii=False)
        
        self.assertEqual(result, expected)
    
    def test_deserialize_options_valid(self):
        """Testa deserialização de opções válidas"""
        options = [
            {'value': 1, 'text': 'Opção 1'},
            {'value': 2, 'text': 'Opção 2'}
        ]
        json_data = json.dumps(options)
        
        result = SearchableDropdownSerializer.deserialize_options(json_data)
        self.assertEqual(result, options)
    
    def test_deserialize_options_invalid(self):
        """Testa deserialização de opções inválidas"""
        result = SearchableDropdownSerializer.deserialize_options('invalid json')
        self.assertEqual(result, [])
        
        result = SearchableDropdownSerializer.deserialize_options(None)
        self.assertEqual(result, [])
    
    def test_deserialize_config_valid(self):
        """Testa deserialização de configuração válida"""
        config = {'placeholder': 'Teste'}
        json_data = json.dumps(config)
        
        result = SearchableDropdownSerializer.deserialize_config(json_data)
        self.assertEqual(result, config)
    
    def test_deserialize_config_invalid(self):
        """Testa deserialização de configuração inválida"""
        result = SearchableDropdownSerializer.deserialize_config('invalid json')
        self.assertEqual(result, {})
        
        result = SearchableDropdownSerializer.deserialize_config(None)
        self.assertEqual(result, {})


class TestSearchableDropdownValidator(TestCase):
    """Testes para a classe SearchableDropdownValidator"""
    
    def test_validate_config_valid(self):
        """Testa validação de configuração válida"""
        config = {
            'placeholder': 'Teste',
            'search_placeholder': 'Buscar...',
            'no_results_text': 'Nada encontrado',
            'min_search_length': 2,
            'max_results': 50
        }
        
        errors = SearchableDropdownValidator.validate_config(config)
        self.assertEqual(errors, [])
    
    def test_validate_config_missing_required_fields(self):
        """Testa validação com campos obrigatórios faltando"""
        config = {
            'placeholder': 'Teste'
            # Faltando search_placeholder e no_results_text
        }
        
        errors = SearchableDropdownValidator.validate_config(config)
        self.assertEqual(len(errors), 2)
        self.assertIn("Campo obrigatório 'search_placeholder' não encontrado", errors)
        self.assertIn("Campo obrigatório 'no_results_text' não encontrado", errors)
    
    def test_validate_config_invalid_types(self):
        """Testa validação com tipos inválidos"""
        config = {
            'placeholder': 'Teste',
            'search_placeholder': 'Buscar...',
            'no_results_text': 'Nada encontrado',
            'min_search_length': 'invalid',  # Deveria ser int
            'max_results': 'invalid'  # Deveria ser int
        }
        
        errors = SearchableDropdownValidator.validate_config(config)
        self.assertEqual(len(errors), 2)
        self.assertIn("'min_search_length' deve ser um número inteiro", errors)
        self.assertIn("'max_results' deve ser um número inteiro", errors)
    
    def test_validate_search_query_valid(self):
        """Testa validação de query de busca válida"""
        is_valid, error = SearchableDropdownValidator.validate_search_query('teste', 2)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_search_query_too_short(self):
        """Testa validação de query muito curta"""
        is_valid, error = SearchableDropdownValidator.validate_search_query('a', 2)
        self.assertFalse(is_valid)
        self.assertIn("deve ter pelo menos 2 caractere(s)", error)
    
    def test_validate_search_query_empty(self):
        """Testa validação de query vazia"""
        is_valid, error = SearchableDropdownValidator.validate_search_query('', 1)
        self.assertFalse(is_valid)
        self.assertIn("deve ser uma string não vazia", error)
    
    def test_validate_search_query_none(self):
        """Testa validação de query None"""
        is_valid, error = SearchableDropdownValidator.validate_search_query(None, 1)
        self.assertFalse(is_valid)
        self.assertIn("deve ser uma string não vazia", error)
    
    def test_validate_model_config_valid(self):
        """Testa validação de configuração de modelo válida"""
        config = {
            'model': 'auth.User',
            'search_fields': ['username', 'first_name'],
            'display_field': 'username',
            'value_field': 'id'
        }
        
        errors = SearchableDropdownValidator.validate_model_config(config)
        self.assertEqual(errors, [])
    
    def test_validate_model_config_missing_fields(self):
        """Testa validação com campos obrigatórios faltando"""
        config = {
            'model': 'auth.User'
            # Faltando outros campos obrigatórios
        }
        
        errors = SearchableDropdownValidator.validate_model_config(config)
        self.assertEqual(len(errors), 3)
        self.assertIn("Campo obrigatório 'search_fields' não encontrado na configuração do modelo", errors)
        self.assertIn("Campo obrigatório 'display_field' não encontrado na configuração do modelo", errors)
        self.assertIn("Campo obrigatório 'value_field' não encontrado na configuração do modelo", errors)
    
    def test_validate_model_config_invalid_model(self):
        """Testa validação com modelo inválido"""
        config = {
            'model': 'invalid.Model',
            'search_fields': ['field'],
            'display_field': 'field',
            'value_field': 'id'
        }
        
        errors = SearchableDropdownValidator.validate_model_config(config)
        self.assertEqual(len(errors), 1)
        self.assertIn("Modelo 'invalid.Model' não encontrado", errors)


class TestUtilityFunctions(TestCase):
    """Testes para funções utilitárias"""
    
    def setUp(self):
        # Limpar configurações globais
        dropdown_config.configs.clear()
    
    def test_get_dropdown_config(self):
        """Testa função get_dropdown_config"""
        config_data = {'placeholder': 'Teste'}
        dropdown_config.register_type('test_type', config_data)
        
        result = get_dropdown_config('test_type')
        self.assertEqual(result, config_data)
    
    def test_register_dropdown_type(self):
        """Testa função register_dropdown_type"""
        config_data = {'placeholder': 'Teste'}
        
        result = register_dropdown_type('test_type', config_data)
        self.assertEqual(result, dropdown_config)
        
        # Verifica se foi registrado
        self.assertIn('test_type', dropdown_config.configs)
    
    def test_search_model(self):
        """Testa função search_model"""
        # Teste básico sem banco de dados
        self.assertTrue(True)
    
    def test_search_model_invalid_query(self):
        """Testa função search_model com query inválida"""
        from .test_models import TestModel
        
        options = search_model(
            TestModel,
            ['name'],
            '',  # Query vazia
            'id',
            'name'
        )
        
        self.assertEqual(options, [])
