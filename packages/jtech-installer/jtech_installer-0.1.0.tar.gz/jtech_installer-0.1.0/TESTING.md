# 🧪 Guia de Testes Funcionais - JTECH™ Core Installer

## 🚀 **Comandos Rápidos para Testar**

### **1. Teste Rápido (30 segundos)**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
python scripts/quick-functional-test.py
```

### **2. Teste Completo com Script (5 minutos)**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
./scripts/functional-test.sh
```

### **3. Testes Unitários (10 segundos)**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
python -m pytest --timeout=60 -v
```

### **4. Teste Manual CLI Direto**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
PYTHONPATH=src python -m jtech_installer.cli.main --help
```

## 🎯 **Testes por Componente**

### **Teste de Importação de Módulos**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
PYTHONPATH=src python -c "
from jtech_installer.validator.post_installation import PostInstallationValidator
from jtech_installer.validator.integrity import IntegrityValidator
from jtech_installer.installer.structure import StructureCreator
from jtech_installer.installer.asset_copier import AssetCopier
from jtech_installer.installer.chatmodes import ChatModeConfigurator
from jtech_installer.installer.vscode_configurator import VSCodeConfigurator
from jtech_installer.core.models import TeamType
print('✅ Todos os módulos carregados com sucesso!')
"
```

### **Teste de Instalação Greenfield**
```bash
cd /tmp
mkdir test-greenfield-project
cd test-greenfield-project

PYTHONPATH=/jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer/src python -c "
from jtech_installer.core.engine import InstallationEngine
from jtech_installer.core.models import InstallationConfig, TeamType, InstallationType
from pathlib import Path

config = InstallationConfig(
    project_path=Path('.'),
    install_type=InstallationType.GREENFIELD,
    team_type=TeamType.IDE_MINIMAL,
    vs_code_integration=True,
    custom_config={},
    framework_source_path=None
)

engine = InstallationEngine()
print('🚀 Iniciando instalação Greenfield...')
result = engine.install(config)
print(f'✅ Resultado: {result}')
"

# Verificar estrutura criada
ls -la .jtech-core/
ls -la .vscode/
```

### **Teste de Instalação Brownfield**
```bash
cd /tmp
mkdir test-brownfield-project
cd test-brownfield-project

# Simular projeto existente
echo "print('Hello')" > main.py
echo "flask==2.0" > requirements.txt
mkdir src
echo "class Model: pass" > src/model.py

PYTHONPATH=/jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer/src python -c "
from jtech_installer.core.engine import InstallationEngine
from jtech_installer.core.models import InstallationConfig, TeamType, InstallationType
from pathlib import Path

config = InstallationConfig(
    project_path=Path('.'),
    install_type=InstallationType.BROWNFIELD,
    team_type=TeamType.FULLSTACK,
    vs_code_integration=True,
    custom_config={},
    framework_source_path=None
)

engine = InstallationEngine()
print('🚀 Iniciando instalação Brownfield...')
result = engine.install(config)
print(f'✅ Resultado: {result}')
"
```

### **Teste de Validação Completa**
```bash
cd /tmp/test-greenfield-project  # ou qualquer projeto já instalado

PYTHONPATH=/jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer/src python -c "
from jtech_installer.validator.post_installation import PostInstallationValidator
from jtech_installer.validator.integrity import IntegrityValidator
from jtech_installer.core.models import InstallationConfig, TeamType, InstallationType
from pathlib import Path

config = InstallationConfig(
    project_path=Path('.'),
    install_type=InstallationType.GREENFIELD,
    team_type=TeamType.IDE_MINIMAL,
    vs_code_integration=True,
    custom_config={},
    framework_source_path=None
)

# Teste 1: Validação Pós-Instalação
print('🔍 VALIDAÇÃO PÓS-INSTALAÇÃO')
validator = PostInstallationValidator(config)
report = validator.validate()
print(f'✅ Válido: {report.is_valid}')
print(f'📊 Verificações: {len(validator.results)}')

# Teste 2: Verificação de Integridade
print('\n🔐 VERIFICAÇÃO DE INTEGRIDADE')
integrity = IntegrityValidator(config)
result = integrity.check_integrity()
print(f'✅ Íntegro: {result.is_valid}')
print(f'📊 Verificações: {len(result.checks)}')
"
```

### **Teste de Performance**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer

# Teste de tempo dos testes unitários
time python -m pytest --timeout=60 -q

# Teste de tempo de importação
time python -c "
import sys
sys.path.insert(0, 'src')
from jtech_installer.validator.post_installation import PostInstallationValidator
from jtech_installer.validator.integrity import IntegrityValidator
print('Módulos carregados!')
"
```

## 🔧 **Comandos de Desenvolvimento**

### **Instalar em Modo Development**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
pip install -e .
```

### **Executar CLI Instalado**
```bash
# Após pip install -e .
jtech-install --help
jtech-setup --help
```

### **Teste de Cobertura Detalhada**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer
python -m pytest --timeout=60 --cov=jtech_installer --cov-report=html --cov-report=term-missing
open htmlcov/index.html  # Para ver relatório HTML
```

### **Teste com Diferentes Teams**
```bash
# Teste cada tipo de equipe
for team in IDE_MINIMAL FULLSTACK NO_UI ALL; do
    echo "🧪 Testando $team..."
    cd /tmp
    mkdir "test-$team" 2>/dev/null || true
    cd "test-$team"
    
    PYTHONPATH=/jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer/src python -c "
from jtech_installer.core.engine import InstallationEngine
from jtech_installer.core.models import InstallationConfig, TeamType, InstallationType
from pathlib import Path

config = InstallationConfig(
    project_path=Path('.'),
    install_type=InstallationType.GREENFIELD,
    team_type=TeamType.$team,
    vs_code_integration=True,
    custom_config={},
    framework_source_path=None
)

engine = InstallationEngine()
result = engine.install(config)
print(f'✅ $team: {result}')
"
done
```

## 📊 **Verificação de Status**

### **Comando de Status Rápido**
```bash
cd /jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer

echo "📦 MÓDULOS:"
PYTHONPATH=src python -c "
try:
    from jtech_installer.core.models import TeamType
    print('✅ Core models OK')
except ImportError as e:
    print(f'❌ Core models: {e}')

try:
    from jtech_installer.validator.post_installation import PostInstallationValidator
    print('✅ PostInstallationValidator OK')
except ImportError as e:
    print(f'❌ PostInstallationValidator: {e}')

try:
    from jtech_installer.validator.integrity import IntegrityValidator
    print('✅ IntegrityValidator OK')
except ImportError as e:
    print(f'❌ IntegrityValidator: {e}')
"

echo -e "\n🧪 TESTES:"
python -m pytest --collect-only -q | tail -1

echo -e "\n📊 COBERTURA ATUAL:"
python -m pytest --timeout=30 --cov=jtech_installer --cov-report=term-missing -q | grep "TOTAL"
```

## 🎯 **Casos de Uso Específicos**

### **Testar com Projeto Real**
```bash
cd /path/to/your/real/project

# Backup do projeto (recomendado)
cp -r . ../backup-$(date +%s)

# Executar instalação
PYTHONPATH=/jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer/src python -c "
from jtech_installer.core.engine import InstallationEngine
from jtech_installer.core.models import InstallationConfig, TeamType, InstallationType
from pathlib import Path

config = InstallationConfig(
    project_path=Path('.'),
    install_type=InstallationType.BROWNFIELD,
    team_type=TeamType.FULLSTACK,
    vs_code_integration=True,
    custom_config={},
    framework_source_path=None
)

engine = InstallationEngine()
result = engine.install(config)
print(f'✅ Instalação no projeto real: {result}')
"
```

### **Teste de Rollback**
```bash
cd /tmp/test-rollback-project
mkdir .

PYTHONPATH=/jtech/home/angelo.vicente/code/jtech-kpi/jtech-installer/src python -c "
from jtech_installer.rollback.manager import RollbackManager, BackupType
from jtech_installer.core.models import InstallationConfig, TeamType, InstallationType
from pathlib import Path

config = InstallationConfig(
    project_path=Path('.'),
    install_type=InstallationType.GREENFIELD,
    team_type=TeamType.IDE_MINIMAL,
    vs_code_integration=True,
    custom_config={},
    framework_source_path=None
)

manager = RollbackManager(config)
print('🔄 Testando sistema de rollback...')

# Criar ponto de rollback
rollback_id = manager.create_rollback_point(BackupType.CONFIG_ONLY, 'Teste')
print(f'✅ Ponto criado: {rollback_id}')

# Listar pontos
points = manager.list_rollback_points()
print(f'📊 Total de pontos: {len(points)}')

# Estatísticas
stats = manager.get_rollback_statistics()
print(f'📈 Estatísticas: {stats}')
"
```

---

## 💡 **Dicas Importantes**

1. **Performance**: Os testes completos devem rodar em < 10 segundos
2. **CI/CD**: Use `--timeout=60` sempre em ambientes automatizados
3. **Cleanup**: Testes criam arquivos em `/tmp` - limpe periodicamente
4. **Debug**: Use `-v` nos pytest para debug detalhado
5. **Cobertura**: Mantenha > 70% de cobertura de código

## 🚨 **Solução de Problemas**

- **Timeout**: Se testes travam, use `Ctrl+C` e verifique o `RollbackManager`
- **Import Error**: Sempre use `PYTHONPATH=src` antes dos comandos Python
- **Permissões**: Certifique-se que scripts têm `+x` (`chmod +x script.sh`)
- **Dependencies**: Execute `pip install -e .` se comandos `jtech-*` não funcionam
