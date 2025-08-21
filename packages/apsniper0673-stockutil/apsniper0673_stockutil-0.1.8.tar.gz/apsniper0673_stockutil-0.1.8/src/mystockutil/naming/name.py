import re

class Name:
    """클래스 이름을 자동으로 생성하는 클래스
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        # __init__가 후행 호출되는 경우에도 작동할 수 있도록 설계
        if not hasattr(self, '_comment'):
            self._comment:str = None
        if not hasattr(self, 'version'):
            self.version:str = None
    @property
    def name(self):
        """comment에서 최신 버전을 찾아 name을 리턴"""
        if hasattr(self, '_comment'):
            versions = re.findall(r'v\d+\.\d+', self._comment)  # 모든 vX.XX 패턴 찾기
        else:
            versions = []
        latest_version = versions[-1] if versions else "v0.00"  # 가장 마지막 버전 선택
        if hasattr(self, 'version'):
            self.version = latest_version
        if hasattr(self, '_name'):
            return f'{self._name}{latest_version}'
        return f'{self.__class__.__name__}{latest_version}'