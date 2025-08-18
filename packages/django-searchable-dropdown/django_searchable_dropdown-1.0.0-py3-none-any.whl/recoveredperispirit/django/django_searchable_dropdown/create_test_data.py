#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para criar dados de teste para a biblioteca SearchableDropdown
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_app.settings')
django.setup()

from test_app.models import TestCategory, TestProduct, TestTag, TestUser, TestModel


def create_test_data():
    """Cria dados de teste para a biblioteca"""
    print("Criando dados de teste...")
    
    # Criar categorias
    categories = [
        {'name': 'Tecnologia', 'description': 'Produtos e serviços de tecnologia'},
        {'name': 'Esportes', 'description': 'Equipamentos e artigos esportivos'},
        {'name': 'Música', 'description': 'Instrumentos musicais e acessórios'},
        {'name': 'Livros', 'description': 'Livros de diversos gêneros'},
        {'name': 'Casa e Jardim', 'description': 'Produtos para casa e jardim'},
    ]
    
    for cat_data in categories:
        category, created = TestCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Criada categoria: {category.name}")
    
    # Criar produtos
    products = [
        {'name': 'Smartphone Galaxy S21', 'category': 'Tecnologia', 'price': 2999.99, 'stock': 50},
        {'name': 'Notebook Dell Inspiron', 'category': 'Tecnologia', 'price': 4599.99, 'stock': 25},
        {'name': 'Bola de Futebol Profissional', 'category': 'Esportes', 'price': 89.99, 'stock': 100},
        {'name': 'Tênis Nike Air Max', 'category': 'Esportes', 'price': 299.99, 'stock': 75},
        {'name': 'Violão Acústico', 'category': 'Música', 'price': 599.99, 'stock': 30},
        {'name': 'Piano Digital', 'category': 'Música', 'price': 2999.99, 'stock': 10},
        {'name': 'O Senhor dos Anéis', 'category': 'Livros', 'price': 49.99, 'stock': 200},
        {'name': 'Harry Potter e a Pedra Filosofal', 'category': 'Livros', 'price': 39.99, 'stock': 150},
        {'name': 'Vaso Decorativo', 'category': 'Casa e Jardim', 'price': 79.99, 'stock': 60},
        {'name': 'Ferramenta Multiuso', 'category': 'Casa e Jardim', 'price': 129.99, 'stock': 40},
    ]
    
    for prod_data in products:
        category = TestCategory.objects.get(name=prod_data['category'])
        product, created = TestProduct.objects.get_or_create(
            name=prod_data['name'],
            defaults={
                'category': category,
                'price': prod_data['price'],
                'stock': prod_data['stock'],
                'description': f'Descrição do produto {prod_data["name"]}'
            }
        )
        if created:
            print(f"Criado produto: {product.name}")
    
    # Criar tags
    tags = [
        {'name': 'Novo', 'color': '#28a745'},
        {'name': 'Promoção', 'color': '#dc3545'},
        {'name': 'Popular', 'color': '#007bff'},
        {'name': 'Esgotando', 'color': '#ffc107'},
        {'name': 'Premium', 'color': '#6f42c1'},
        {'name': 'Econômico', 'color': '#20c997'},
        {'name': 'Importado', 'color': '#fd7e14'},
        {'name': 'Nacional', 'color': '#6c757d'},
    ]
    
    for tag_data in tags:
        tag, created = TestTag.objects.get_or_create(
            name=tag_data['name'],
            defaults={'color': tag_data['color']}
        )
        if created:
            print(f"Criada tag: {tag.name}")
    
    # Criar usuários
    users = [
        {'name': 'João Silva', 'email': 'joao@example.com', 'username': 'joao_silva'},
        {'name': 'Maria Santos', 'email': 'maria@example.com', 'username': 'maria_santos'},
        {'name': 'Pedro Oliveira', 'email': 'pedro@example.com', 'username': 'pedro_oliveira'},
        {'name': 'Ana Costa', 'email': 'ana@example.com', 'username': 'ana_costa'},
        {'name': 'Carlos Ferreira', 'email': 'carlos@example.com', 'username': 'carlos_ferreira'},
    ]
    
    for user_data in users:
        user, created = TestUser.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'name': user_data['name'],
                'email': user_data['email']
            }
        )
        if created:
            print(f"Criado usuário: {user.name}")
    
    # Criar modelos de teste
    test_models = [
        {'name': 'Item de Teste 1', 'description': 'Primeiro item de teste', 'category': 'tech'},
        {'name': 'Item de Teste 2', 'description': 'Segundo item de teste', 'category': 'sports'},
        {'name': 'Item de Teste 3', 'description': 'Terceiro item de teste', 'category': 'music'},
        {'name': 'Item Inativo', 'description': 'Item inativo para teste', 'category': 'tech', 'active': False},
    ]
    
    for model_data in test_models:
        active = model_data.get('active', True)
        model, created = TestModel.objects.get_or_create(
            name=model_data['name'],
            defaults={
                'description': model_data['description'],
                'category': model_data['category'],
                'active': active
            }
        )
        if created:
            print(f"Criado modelo de teste: {model.name}")
    
    print("\nDados de teste criados com sucesso!")
    print(f"- {TestCategory.objects.count()} categorias")
    print(f"- {TestProduct.objects.count()} produtos")
    print(f"- {TestTag.objects.count()} tags")
    print(f"- {TestUser.objects.count()} usuários")
    print(f"- {TestModel.objects.count()} modelos de teste")


if __name__ == '__main__':
    create_test_data()
