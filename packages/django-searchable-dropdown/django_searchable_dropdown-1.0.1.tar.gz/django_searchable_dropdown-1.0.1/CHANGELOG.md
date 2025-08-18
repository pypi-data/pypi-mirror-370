# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.1] - 2024-08-18

### Corrigido
- **Compatibilidade PEP 625**: Corrigido nome do projeto para usar underscores em vez de hífens
- **Build System**: Atualizado para usar `pyproject.toml` moderno e compatível com PEP 625
- **Nomes de Arquivos**: Arquivos de distribuição agora seguem o padrão `django_searchable_dropdown-*.tar.gz`

### Técnico
- **setuptools**: Atualizado para versão >=68.0 para suporte completo ao PEP 625
- **pyproject.toml**: Adicionada configuração completa do projeto com metadados
- **Build**: Migrado de `setup.py` para sistema baseado em `pyproject.toml`

---

## [1.0.0] - 2024-08-17

### Adicionado
- **Badges no README**: Adicionados badges para PyPI, Python, Django, licença, build status, cobertura de código
- **Script de Build**: Criado `build_and_publish.py` para automatizar o processo de build e publicação
- **Documentação de Publicação**: Criado `PUBLISHING.md` com guia completo para publicação no PyPI
- **Status do Projeto**: Adicionada seção de status no README com informações da versão atual
- **Configuração de Segurança**: Adicionado `.pypirc` ao `.gitignore` para proteger tokens

### Melhorado
- **README**: Atualizado com badges profissionais e seção de status
- **Documentação**: Melhorada a documentação com informações de publicação

### Técnico
- **Build System**: Configurado sistema completo de build para PyPI
- **Testes**: 110 testes passando com 100% de cobertura
- **Compatibilidade**: Django 2.2+ e Python 3.7+
- **Licença**: MIT (Open Source)

### Arquivos Criados
- `build_and_publish.py` - Script automatizado para build e publicação
- `PUBLISHING.md` - Guia completo de publicação
- `CHANGELOG.md` - Este arquivo de changelog

### Arquivos Modificados
- `README.md` - Adicionados badges e seção de status
- `.gitignore` - Adicionado `.pypirc` para segurança

### Builds Gerados
- `django_searchable_dropdown-1.0.0-py3-none-any.whl` (54.4 KB)
- `django-searchable-dropdown-1.0.0.tar.gz` (44.3 KB)

## Como Usar

### Build Local
```bash
python build_and_publish.py --build-only
```

### Teste no TestPyPI
```bash
python build_and_publish.py --test
```

### Publicação no PyPI
```bash
python build_and_publish.py --publish
```

## Próximos Passos

1. **Teste no TestPyPI**: Execute `python build_and_publish.py --test`
2. **Verifique a instalação**: `pip install --index-url https://test.pypi.org/simple/ django-searchable-dropdown`
3. **Publique no PyPI**: Execute `python build_and_publish.py --publish`
4. **Verifique a publicação**: Acesse https://pypi.org/project/django-searchable-dropdown/



