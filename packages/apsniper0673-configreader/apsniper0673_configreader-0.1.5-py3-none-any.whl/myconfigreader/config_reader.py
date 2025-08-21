# ConfigReader 클래스 정의는 동일하게 유지
import configparser
from configparser import SectionProxy
from pathlib import Path
from typing import List
from pathlib import Path
import inspect

def get_config_path(config_file_name: str, caller_path=None) -> Path:
    """
    현재 파일 기준으로 상위 디렉토리를 탐색하여 'credentials' 폴더를 찾고,
    해당 폴더 아래의 config 파일 경로를 반환합니다.
    
    Raises:
        FileNotFoundError: credentials 폴더를 찾지 못한 경우
    """
    # 호출자 파일의 경로를 기준으로 시작
    if caller_path is None:
        current = Path.cwd()  # 현재 작업 디렉토리
    else:    
        # current = caller_path
        current = Path.cwd()  # 현재 작업 디렉토리

    while current != current.parent:  # 루트까지 도달하지 않은 동안
        cred_path = current / "credentials"
        if cred_path.exists() and cred_path.is_dir():
            return cred_path / config_file_name
        current = current.parent

    raise FileNotFoundError("상위 디렉토리에 'credentials' 폴더를 찾을 수 없습니다.")
    
class _ConfigReader:
    """
    ConfigReader 클래스는 설정 파일에서 값을 읽어오는 기능을 제공합니다.
    항상 credentials/config.ini 파일을 참조합니다.
    기본 섹션은 'DEFAULT'입니다.
    """

    def __init__(self, config_file_name: str = 'config.ini', caller_path: Path = None) -> None:
        self.config = configparser.ConfigParser()
        # config_path = Path(__file__).resolve().parent.parent / f"credentials/{config_file_name}"
        config_path = get_config_path(config_file_name=config_file_name, caller_path=caller_path)
        # print(f"설정 파일 경로: {config_path}") # 경로 확인용
        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일 '{config_path}'을(를) 찾을 수 없습니다.")
        self.config.read(config_path, encoding='utf-8')
        self._current_section_name: str = "DEFAULT" # 현재 섹션 이름을 저장
        self.set_section('DEFAULT') # 초기화 시 DEFAULT 섹션으로 설정

    def set_section(self, section_name: str = "DEFAULT") -> None:
        """
        섹션을 설정합니다.
        """
        if section_name not in self.config:
            raise KeyError(f"'{section_name}' 섹션이 config.ini 파일에 없습니다.")
        self._current_section_name = section_name # 현재 섹션 이름 업데이트
        self.section = self.config[section_name]

    def get_section(self, section_name: str = None) -> SectionProxy:
        """
        섹션을 반환합니다.
        지정된 섹션이 없으면 현재 설정된 섹션을 반환합니다.
        """
        if section_name is None:
            return self.section # 이미 set_section에서 설정된 self.section 반환
        try:
            return self.config[section_name]
        except KeyError:
            raise KeyError(f"'{section_name}' 섹션이 config.ini 파일에 없습니다.")
    
    def get_value(self, key: str, default_value=None) -> str:
        """
        지정된 키에 대한 값을 반환합니다.
        """
        if not self.section: # set_section이 호출되지 않았을 경우를 대비
            self.set_section('DEFAULT')
        try:
            return self.section[key]
        except KeyError:
            # 더 명확한 에러 메시지
            print(f"'{key}' 키가 '{self._current_section_name}' 섹션에 없습니다.")
            return default_value
class ConfigReader_manipulation(_ConfigReader):
    def items(self) -> List[tuple]:
        """
        현재 섹션의 모든 키-값 쌍을 반환합니다.
        """
        if not self.section: # set_section이 호출되지 않았을 경우를 대비
            self.set_section('DEFAULT')
        return list(self.section.items())
    
class ConfigReader(ConfigReader_manipulation):
    """
    ConfigReader 클래스는 _ConfigReader 클래스를 상속받아
    설정 파일에서 값을 읽어오는 기능을 제공합니다.
    기본 섹션은 'DEFAULT'입니다.
    """
    def __init__(self, config_file_name: str = 'config.ini'):
        caller_frame = inspect.stack()[1]
        caller_path = Path(caller_frame.filename).resolve().parent
        super().__init__(config_file_name=config_file_name, caller_path=caller_path)
        # 추가적인 초기화가 필요할 경우 여기에 작성