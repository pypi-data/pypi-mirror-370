import pandas as pd
import os
from pathlib import Path
import re

from mydataprovider.frame.odi.df_odi import odi
from mystockutil.etc import get_project_root

from mystockutil.logging.logging_setup import CustomAdapter, logger as original_logger
logger = CustomAdapter(original_logger, {'prefix': 'Feather'})


# essential imports
from mydataprovider.frame.feather.functions.find_feather_path import find_feather_path

class _FeatherManager():
    def __init__(self, base_feather_name:str) -> None:
        self.feather_name = base_feather_name
        self.feather_dir:Path = None
        self._set_feather_dir()

    def _set_feather_dir(self) -> None:
        """
        Feather 파일을 저장할 디렉토리를 설정합니다.
        """
        try:
            self.feather_dir = find_feather_path()
            
            # self.feather_dir = get_project_root().joinpath('feather')
            # self.feather_dir = Path.cwd() / 'feather'
        except:
            try:
                self.feather_dir = get_project_root(marker='feather').joinpath('feather')
            except:
                raise RuntimeError("Cannot find feather directory. Please check your project structure.")
        
    def _get_feather_dir(self) -> Path:
        return self.feather_dir
    def _generate_feather_path(self, date:pd.Timestamp=None) -> str:
        if date is None:
            # 디폴트 값으로 오늘 날짜를 사용
            date = pd.Timestamp.today().normalize()
        return os.path.join(self.feather_dir, date.strftime('%Y%m%d') + '_' + self.feather_name + '.feather')
    def _find_latest_feather_path(self) -> Path | None:
        # 파일 이름 패턴 정의: YYYYMMDD_table_name.feather
        pattern = re.compile(r'(\d{8})_' + re.escape(self.feather_name) + r'\.feather$')
        latest_date = None
        latest_file = None
        
        # base_dir 내의 모든 파일을 순회
        for file in self.feather_dir.iterdir():
            if file.is_file():
                match = pattern.match(file.name)
                if match:
                    date_str = match.group(1)
                    try:
                        file_date = pd.to_datetime(date_str, format='%Y%m%d')
                        if (latest_date is None) or (file_date > latest_date):
                            latest_date = file_date
                            latest_file = file
                    except ValueError:
                        logger.warning(f"Filename '{file.name}' has invalid date format.")
                        continue
        if latest_file is None:
            logger.warning(f"No feather files found for table '{self.feather_name}' in '{self.feather_dir}'.")
        return latest_file
    
    def _load_latest_feather(self) -> pd.DataFrame:
        """
        지정된 테이블 이름에 해당하는 최신 Feather 파일을 로드

        Args:
            table_name (str): 테이블 이름

        Returns:
            pd.DataFrame: 로드된 데이터프레임

        Raises:
            FileNotFoundError: 해당 테이블에 대한 Feather 파일이 존재하지 않을 경우
        """
        latest_file = self._find_latest_feather_path()
        
        if latest_file:
            logger.info(f"Loading latest file: {latest_file}")
            df = pd.read_feather(latest_file)
            return df
        else:
            raise FileNotFoundError(f"No feather files found for table '{self.feather_name}' in '{self.feather_dir}'.")

class FeatherManager_del(_FeatherManager):
    def delete_old_feathers(self, keep:int=3) -> None:
        """
        feather 디렉토리 내에서 가장 최근 `keep`개 파일을 제외하고 모두 삭제합니다.
        
        Args:
            keep (int): 보존할 최신 feather 파일 개수. 그 외는 삭제됨.
        """
        pattern = re.compile(r'(\d{8})_' + re.escape(self.feather_name) + r'\.feather$')
        files_with_dates = []

        for file in self.feather_dir.iterdir():
            if file.is_file():
                match = pattern.match(file.name)
                if match:
                    try:
                        date = pd.to_datetime(match.group(1), format='%Y%m%d')
                        files_with_dates.append((date, file))
                    except ValueError:
                        logger.warning(f"Filename '{file.name}' has invalid date format.")
                        continue
        
        # 날짜 기준으로 정렬
        files_with_dates.sort(reverse=True)

        # 삭제할 파일들 추출
        files_to_delete = files_with_dates[keep:]

        for _, file in files_to_delete:
            try:
                file.unlink()
                logger.info(f"Deleted old feather file: {file}")
            except Exception as e:
                logger.error(f"Failed to delete file {file}: {e}")

class FeatherManager(FeatherManager_del):
    def load_from_feather(self) -> pd.DataFrame:
        return self._load_latest_feather()

    def save_to_feather(self, df:pd.DataFrame):
        last_date = df.index.get_level_values('일자').max()
        df.to_feather(self._generate_feather_path(date=last_date))
        logger.info(f"Data saved to feather file: {self._generate_feather_path(date=last_date)}")

if __name__ == '__main__':
    pass