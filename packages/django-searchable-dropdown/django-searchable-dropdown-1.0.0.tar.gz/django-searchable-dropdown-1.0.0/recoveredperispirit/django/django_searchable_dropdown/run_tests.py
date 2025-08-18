#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para executar os testes da biblioteca SearchableDropdown
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil


def run_command(command, description):
    """Executa um comando e mostra o resultado"""
    print(f"\n{'='*60}")
    print(f"Executando: {description}")
    print(f"Comando: {command}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ Falhou com código de saída: {result.returncode}")
        return False
    else:
        print(f"✅ Sucesso!")
        return True


def create_test_database_script():
    """Cria um script para configurar o banco de dados de teste"""
    script_content = '''
import os
import sys
import django
from django.conf import settings

# Adicionar o diretório do projeto ao path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
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
    SECRET_KEY='test-secret-key',
    STATIC_URL='/static/',
    USE_TZ=True,
    TIME_ZONE='UTC',
    # Configuração para não usar migrações em testes
    MIGRATION_MODULES={
        'django_searchable_dropdown': None,
    },
)

django.setup()

# Importar os modelos de teste
from recoveredperispirit.django.django_searchable_dropdown.tests.test_models import TestModel, TestCategory, TestProduct
from django.db import connection

# Criar as tabelas
with connection.schema_editor() as schema_editor:
    # Criar tabela para TestModel
    schema_editor.create_model(TestModel)
    print("✅ Tabela TestModel criada")
    
    # Criar tabela para TestCategory
    schema_editor.create_model(TestCategory)
    print("✅ Tabela TestCategory criada")
    
    # Criar tabela para TestProduct
    schema_editor.create_model(TestProduct)
    print("✅ Tabela TestProduct criada")

print("✅ Todas as tabelas de teste foram criadas com sucesso!")
'''
    
    script_path = "setup_test_db.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path


def main():
    parser = argparse.ArgumentParser(description='Executar testes da biblioteca SearchableDropdown')
    parser.add_argument('--install-deps', action='store_true', help='Instalar dependências primeiro')
    parser.add_argument('--lint', action='store_true', help='Executar linting')
    parser.add_argument('--format', action='store_true', help='Formatar código')
    parser.add_argument('--coverage', action='store_true', help='Executar com cobertura')
    parser.add_argument('--all', action='store_true', help='Executar todos os checks')
    parser.add_argument('--setup-db', action='store_true', help='Configurar banco de dados de teste')
    
    args = parser.parse_args()
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('setup.py'):
        print("❌ Erro: Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    success = True
    setup_script_path = None
    
    try:
        if args.install_deps or args.all:
            print("📦 Instalando dependências...")
            success &= run_command("pip install -r requirements-dev.txt", "Instalar dependências de desenvolvimento")
        
        if args.format or args.all:
            print("🎨 Formatando código...")
            success &= run_command("black .", "Formatar código com Black")
            success &= run_command("isort .", "Organizar imports com isort")
        
        if args.lint or args.all:
            print("🔍 Executando linting...")
            success &= run_command("flake8 .", "Verificar estilo com flake8")
            success &= run_command("bandit -r .", "Verificar segurança com bandit")
        
        # Configurar banco de dados de teste se necessário
        if args.setup_db or args.all:
            print("🔧 Configurando banco de dados de teste...")
            setup_script_path = create_test_database_script()
            success &= run_command(f"python {setup_script_path}", "Configurar banco de dados de teste")
        
        # Executar testes
        print("🧪 Executando testes...")
        if args.coverage or args.all:
            success &= run_command("pytest --cov=recoveredperispirit.django.django_searchable_dropdown --cov-report=html --cov-report=term-missing", "Executar testes com cobertura")
        else:
            success &= run_command("pytest", "Executar testes")
    
    finally:
        # Limpar script temporário
        if setup_script_path and os.path.exists(setup_script_path):
            os.remove(setup_script_path)
    
    if success:
        print("\n🎉 Todos os checks passaram!")
        sys.exit(0)
    else:
        print("\n❌ Alguns checks falharam!")
        sys.exit(1)


if __name__ == '__main__':
    main()
