# Version: 0.1.2
import os
import tempfile
import shutil

class Trueflagger:
    """
    Biblioteca simples para manipulação de flags via arquivos.
    """

    def __init__(self, dir=None):
        self.base_dir = dir or tempfile.gettempdir()
        self.stopped_dir = os.path.join(self.base_dir, "Stopped")
        # Criar diretório Stopped se não existir
        if not os.path.exists(self.stopped_dir):
            os.makedirs(self.stopped_dir)

    def _get_flag_path(self, name):
        return os.path.join(self.base_dir, f"{name}.flag")
    
    def _get_stopped_flag_path(self, name):
        return os.path.join(self.stopped_dir, f"{name}.flag")

    def createFlag(self, flagName, value="1"):
        path = self._get_flag_path(flagName)
        with open(path, "w") as f:
            f.write(str(value))

    def readFlag(self, flagName):
        # Primeiro verifica se a flag está ativa
        path = self._get_flag_path(flagName)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        
        # Se não estiver ativa, verifica se está parada
        stopped_path = self._get_stopped_flag_path(flagName)
        if os.path.exists(stopped_path):
            raise RuntimeError(f"Unable to Use Flag: Flag is stopped")
        
        return None

    def updateFlag(self, flagName, value):
        # Primeiro verifica se a flag está ativa
        path = self._get_flag_path(flagName)
        if os.path.exists(path):
            with open(path, "w") as f:
                f.write(value)
            return
        
        # Se não estiver ativa, verifica se está parada
        stopped_path = self._get_stopped_flag_path(flagName)
        if os.path.exists(stopped_path):
            raise RuntimeError(f"Unable to Use Flag: Flag is stopped")
        
        raise FileNotFoundError(f"Flag '{flagName}' não existe.")

    def removeFlag(self, flagName):
        # Remove tanto da pasta ativa quanto da parada
        path = self._get_flag_path(flagName)
        stopped_path = self._get_stopped_flag_path(flagName)
        
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(stopped_path):
            os.remove(stopped_path)
    
    def StopFlag(self, flagName):
        """
        Desabilita uma flag movendo-a para o diretório Stopped.
        A flag não é deletada, apenas movida para um estado "parado".
        """
        path = self._get_flag_path(flagName)
        stopped_path = self._get_stopped_flag_path(flagName)
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Flag '{flagName}' não existe.")
        
        # Move a flag para o diretório Stopped
        shutil.move(path, stopped_path)
    
    def StartFlag(self, flagName):
        """
        Reativa uma flag movendo-a de volta do diretório Stopped para o diretório ativo.
        """
        path = self._get_flag_path(flagName)
        stopped_path = self._get_stopped_flag_path(flagName)
        
        if not os.path.exists(stopped_path):
            raise FileNotFoundError(f"Flag '{flagName}' não está parada.")
        
        if os.path.exists(path):
            raise FileExistsError(f"Flag '{flagName}' já está ativa.")
        
        # Move a flag de volta para o diretório ativo
        shutil.move(stopped_path, path)
    
    def isFlagActive(self, flagName):
        """
        Verifica se uma flag está ativa (no diretório principal).
        """
        path = self._get_flag_path(flagName)
        return os.path.exists(path)
    
    def listStoppedFlags(self):
        """
        Lista todas as flags que estão paradas.
        """
        if not os.path.exists(self.stopped_dir):
            return []
        
        flags = []
        for file in os.listdir(self.stopped_dir):
            if file.endswith('.flag'):
                flags.append(file[:-5])  # Remove a extensão .flag
        return flags
