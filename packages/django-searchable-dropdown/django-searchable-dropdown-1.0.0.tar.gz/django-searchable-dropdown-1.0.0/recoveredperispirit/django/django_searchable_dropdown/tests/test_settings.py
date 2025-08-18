"""
Configurações de teste para a biblioteca SearchableDropdown
"""

import os
import tempfile

# Configurações básicas do Django
SECRET_KEY = 'test-secret-key-for-testing'

# Configuração de banco de dados para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Banco em memória para testes
    }
}

# Configuração de aplicações
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recoveredperispirit.django.django_searchable_dropdown',
]

# Configuração de middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração de templates
TEMPLATES = [
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
]

# Configuração de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = tempfile.mkdtemp()

# Configuração de configurações da biblioteca
SEARCHABLE_DROPDOWN_CONFIG = {
    'default_placeholder': 'Selecione uma opção',
    'default_search_placeholder': 'Digite para buscar...',
    'default_no_results_text': 'Nenhum resultado encontrado',
    'ajax_timeout': 5000,
    'min_search_length': 1,
    'max_results': 50,
}

# Configuração de debug
DEBUG = True

# Configuração de timezone
USE_TZ = False
TIME_ZONE = 'UTC'

# Configuração de idioma
LANGUAGE_CODE = 'pt-br'
USE_I18N = True
USE_L10N = True

# Configuração de sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Configuração de autenticação
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configurações específicas para testes
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Configuração para criar tabelas automaticamente
MIGRATION_MODULES = {
    'django_searchable_dropdown': 'recoveredperispirit.django.django_searchable_dropdown.tests.migrations',
}

# Configuração para usar banco de dados em memória
DATABASES['default']['TEST'] = {
    'NAME': ':memory:',
}

# Configuração para não usar migrações em testes (criar tabelas diretamente)
MIGRATION_MODULES = {
    'django_searchable_dropdown': None,
}
