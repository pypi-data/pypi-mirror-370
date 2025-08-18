"""
Runner de testes para a biblioteca SearchableDropdown
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def setup_django():
    """Configura o Django para execução dos testes"""
    # Configurações básicas do Django para testes
    if not settings.configured:
        # Configurar Django antes de qualquer import
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recoveredperispirit.django.django_searchable_dropdown.tests.test_runner')
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
        )
        django.setup()


def run_tests():
    """Executa todos os testes da biblioteca"""
    setup_django()
    
    # Obter o test runner do Django
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Lista de módulos de teste para executar
    test_modules = [
        'recoveredperispirit.django.django_searchable_dropdown.tests.test_utils',
        'recoveredperispirit.django.django_searchable_dropdown.tests.test_widgets',
        'recoveredperispirit.django.django_searchable_dropdown.tests.test_forms',
        'recoveredperispirit.django.django_searchable_dropdown.tests.test_integration',
    ]
    
    # Executar os testes
    failures = test_runner.run_tests(test_modules)
    
    return failures


if __name__ == '__main__':
    failures = run_tests()
    sys.exit(bool(failures))
