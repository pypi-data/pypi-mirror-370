import pandas as pd
from typing import Any

"""ODI에 사용되는 함수들"""

# 특정 인덱스를 기준으로 offset 값 가져오기
def get_index_with_offset(index:pd.Index, target_index, offset):
    try:
        # 해당 인덱스의 위치 찾기
        position = index.get_loc(target_index)
        # offset 만큼 이동한 인덱스 반환
        new_position = position + offset
        
        # 범위를 벗어났는지 확인
        if new_position < 0 or new_position >= len(index):
            raise IndexError("Offset이 인덱스 범위를 벗어났습니다.")
        
        return index[new_position]
    except KeyError:
        raise KeyError(f"Index {target_index} not found in index.")

def get_value_with_index(df:pd.DataFrame, target_index, offset):
    index = df.index
    new_index = get_index_with_offset(index, target_index, offset)
    return df.loc[new_index]

def get_offset_value_with_target(sorted_source, target: Any, offset:int=1):
        # source에서 target으로부터 offset만큼 떨어진 값을 반환
        # target이 없을 수도 있다.
        if offset > 0:
            try:
                new_value = sorted_source[sorted_source > target][offset-1]
                return new_value
            except IndexError:
                raise IndexError(f"Index {offset} out of range.")
        elif offset < 0:
            try:
                new_value = sorted_source[sorted_source < target][offset]
                return new_value
            except IndexError:
                raise IndexError(f"Index {offset} out of range.")
        elif offset == 0:
            if target in sorted_source:
                return target
            else:
                raise ValueError("Offset is 0 and Target is not in source.")