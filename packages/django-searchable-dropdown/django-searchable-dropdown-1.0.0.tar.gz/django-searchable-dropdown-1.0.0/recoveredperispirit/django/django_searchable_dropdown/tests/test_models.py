"""
Modelos de teste para os testes da biblioteca SearchableDropdown
"""

from django.db import models


class TestModel(models.Model):
    """Modelo de teste para os testes da biblioteca"""
    
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    category = models.CharField(max_length=50, blank=True, verbose_name="Categoria")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        app_label = 'django_searchable_dropdown'
        verbose_name = "Item de Teste"
        verbose_name_plural = "Itens de Teste"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TestCategory(models.Model):
    """Categoria de teste"""
    
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        app_label = 'django_searchable_dropdown'
        verbose_name = "Categoria de Teste"
        verbose_name_plural = "Categorias de Teste"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TestProduct(models.Model):
    """Produto de teste"""
    
    name = models.CharField(max_length=200, verbose_name="Nome")
    category = models.ForeignKey(TestCategory, on_delete=models.CASCADE, verbose_name="Categoria")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    description = models.TextField(blank=True, verbose_name="Descrição")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        app_label = 'django_searchable_dropdown'
        verbose_name = "Produto de Teste"
        verbose_name_plural = "Produtos de Teste"
        ordering = ['name']
    
    def __str__(self):
        return self.name
