"""
Configuração do pytest para os testes da biblioteca SearchableDropdown
"""

import os
import sys
import pytest
import django
from django.conf import settings
from django.test.utils import setup_databases, teardown_databases
from django.db import connection


def pytest_configure():
    """Configura o Django para os testes"""
    if not settings.configured:
        # Adicionar o diretório do projeto ao path
        project_root = os.path.dirname(os.path.dirname(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recoveredperispirit.django.django_searchable_dropdown.tests.test_settings')
        
        # Configurações básicas do Django para testes
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'django.contrib.admin',
                'recoveredperispirit.django.django_searchable_dropdown',
            ],
            MIDDLEWARE=[
                'django.middleware.security.SecurityMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.common.CommonMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
                'django.middleware.clickjacking.XFrameOptionsMiddleware',
            ],
            ROOT_URLCONF='recoveredperispirit.django.django_searchable_dropdown.tests.urls',
            SECRET_KEY='test-secret-key',
            STATIC_URL='/static/',
            STATICFILES_DIRS=[
                os.path.join(os.path.dirname(__file__), '..', 'templates', 'searchable_dropdown', 'static'),
            ],
            TEMPLATES=[
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': [
                        os.path.join(os.path.dirname(__file__), '..', 'templates'),
                    ],
                    'APP_DIRS': True,
                    'OPTIONS': {
                        'context_processors': [
                            'django.template.context_processors.debug',
                            'django.template.context_processors.request',
                            'django.contrib.auth.context_processors.auth',
                            'django.contrib.messages.context_processors.messages',
                        ],
                    },
                },
            ],
            USE_TZ=True,
            TIME_ZONE='UTC',
            # Configuração para não usar migrações em testes
            MIGRATION_MODULES={
                'django_searchable_dropdown': None,
            },
        )
        django.setup()


def pytest_collection_modifyitems(config, items):
    """Modifica os itens de teste para adicionar marcadores"""
    for item in items:
        # Adicionar marcador 'django_db' para todos os testes
        item.add_marker('django_db')
        
        # Adicionar marcadores baseados no nome do arquivo
        if 'integration' in item.nodeid:
            item.add_marker('integration')
        elif 'unit' in item.nodeid:
            item.add_marker('unit')


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configura o banco de dados para todos os testes"""
    with django_db_blocker.unblock():
        # Criar as tabelas para os modelos de teste
        from django.core.management import execute_from_command_line
        from django.db import connection
        
        # Importar os modelos de teste
        from .test_models import TestModel, TestCategory, TestProduct
        
        # Criar as tabelas
        with connection.schema_editor() as schema_editor:
            # Criar tabela para TestModel
            schema_editor.create_model(TestModel)
            
            # Criar tabela para TestCategory
            schema_editor.create_model(TestCategory)
            
            # Criar tabela para TestProduct
            schema_editor.create_model(TestProduct)
        
        print("✅ Tabelas de teste criadas com sucesso!")


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Habilita acesso ao banco de dados para todos os testes"""
    pass
