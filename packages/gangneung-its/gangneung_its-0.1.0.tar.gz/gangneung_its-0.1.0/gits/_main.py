import requests
import ssl
from requests.adapters import HTTPAdapter
import json
from tenacity import retry, stop_after_attempt, wait_fixed

"""
강릉 ITS 데이터 API를 쉽게 사용하기 위한 모듈입니다.
"""

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')  # 암호화 보안 수준 낮추기
        kwargs['ssl_context'] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount('https://', TLSAdapter())

@retry(wait=wait_fixed(3), stop=stop_after_attempt(5))
def _get_data(data_type: str, do_retry: bool = True) -> list[dict[str, str]]:
    response = session.get('https://apis.data.go.kr/4201000/GNitsTrafficInfoService_1.0/' + data_type, params={
        'serviceKey': 'n2adgenGPI8brpT0O3lNBbV/LxAkWVc7l5eRqf4qLKNAxNrMVyJW162Tlc/yq1wDDX4KylyDJmbGrhVnZN6auw==',
        'pageNo': 1,
        'numOfRows': 10000
    })
    
    data = json.loads(response.text)

    if not do_retry:
        try:
            return data['body']['items']['item']
        except KeyError:
            return []
    
    if data['header']['resultCode'] != '00':
        raise ValueError("데이터 못 받음! 에러 코드: " + data['header']['resultCode'])
    
    return data['body']['items']['item']

class _ITSInfo:
    def __init__(self) -> None:
        self.data: list[dict[str, str]] # _get_data() 메서드를 통해 데이터를 가져올 예정입니다.
        raise NotImplementedError('ITSInfo는 추상 클래스입니다. 이 클래스를 상속받아 구체적인 정보를 구현해야 합니다')
    
    def update(self) -> None:
        """
        정보를 업데이트합니다.
        """
        self.__init__()
        
    def find(self, *_, **kwargs) -> list[dict[str, str]]:
        """
        정보에서 특정 필드의 값을 가진 항목을 찾습니다.\n
        
        예: find(flowNo='1')\n
        """
        data = self.data
        
        for key in list(kwargs.keys()):
            data = [item for item in data if item[key] == kwargs[key]]
        
        return data
    

class ParkingLotInfo(_ITSInfo):
    """
    주차장 정보 클래스\n
    
    필드:\n
    prkId: 주차장 ID\n
    prkName: 주차장 이름\n
    prkAddr: 주차장 주소\n
    xCrdn: 주차장 경도\n
    yCrdn: 주차장 위도\n
    weekOpenTime: 주차장 주중 운영 시작 시간\n
    weekEndTime: 주차장 주중 운영 종료 시간\n
    satOpenTime: 주차장 토요일 운영 시작 시간\n
    satEndTime: 주차장 토요일 운영 종료 시간\n
    holiOpenTime: 주차장 공휴일 운영 시작 시간\n
    holiEndTime: 주차장 공휴일 운영 종료 시간\n
    prkType: 주차장 종류\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getParkInfo')
        
class TrafficLightRealTimeInfo(_ITSInfo):
    """
    실시간 신호등 정보 클래스\n
    
    필드:\n
    lcNo: 교차로 번호\n
    ringNo: 신호등 번호\n
    phaseNo: 신호등 단계 번호\n
    flowNo: 신호등 흐름 번호\n
    yellow: 신호등 황색 신호 시간\n
    minSplit: 신호등 최소 녹색 시간\n
    maxSplit: 신호등 최대 녹색 시간\n
    laneCnt: 신호등 차로 수\n
    sfr: 포화교통류율\n
    lcName: 교차로 이름 (신호등 정보에 추가됨)\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getSignalPhase')
        signal_lc = _get_data('getSignalLc')
        
        # 신호등 정보에 신호등 이름 추가
        for item in self.data:
            for i in signal_lc:
                if item['lcNo'] == i['lcNo']:
                    item['lcName'] = i['lcName']
                    break
                
class ParkingLotRealTimeInfo(_ITSInfo):
    """
    실시간 주차장 정보 클래스\n
    
    필드:\n
    prkId: 주차장 ID\n
    prkName: 주차장 이름\n
    totalLots: 총 주차 공간 수\n
    availLots: 빈 주차 공간 수\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getParkRltm')
        
class IntersectionInfo(_ITSInfo):
    """
    교차로 정보 클래스\n
    
    필드:\n
    colDate: 수집 날짜\n
    crossName: 교차로 이름\n
    volume: 교차로 통행량\n
    vphg: 교차로 용량\n
    vs: 포화도\n
    los: 서비스 수준\n
    walker: 보행자 수\n
    crash: 사고 수\n
    delay: 지체 시간\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getSmrtTrff')

class CrosswalkInfo(_ITSInfo):
    """
    횡단보도 정보 클래스\n
    
    필드:\n
    colDate: 수집 날짜\n
    crwkId: 횡단보도 ID\n    
    crwkName: 횡단보도 이름\n
    standby: 대기자 수
    across: 횡단자 수\n
    jaywalking: 무단횡단자 수\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getCrwkTrff')
        
class RoundaboutInfo(_ITSInfo):
    """
    로터리 정보 클래스\n
    
    필드:\n
    colDate: 수집 날짜\n
    crossName: 로터리 이름\n
    volume: 로터리 통행량\n
    speed: 속도\n
    passTime: 통행 시간\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getRondTrff')
        
class RoundaboutEventInfo(_ITSInfo):
    """
    로터리 이벤트 정보 클래스\n
    
    필드:\n
    colDate: 수집 날짜\n
    crossName: 로터리 이름\n
    xCrdn: 로터리 경도\n
    yCrdn: 로터리 위도\n
    speed: 속도\n
    objectId: 이벤트 ID\n
    eventType: 이벤트 유형\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getRondEvnt')
        
class ObjectDetectionInfo(_ITSInfo):
    """
    객체 탐지 정보 클래스\n
    
    필드:\n
    colDate: 수집 날짜\n
    crossName: 교차로 이름\n
    xCrdn: 경도\n
    yCrdn: 위도\n
    signalPhase: 신호등 단계\n
    objectPos: 객체 위치\n
    objectType: 객체 유형\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getObdsSupp')

class TrafficLightInfo(_ITSInfo):
    """
    교차로 정보 클래스\n
    
    필드:\n
    lcNo: 교차로 번호\n
    lcName: 교차로 이름\n
    intType: 교차로 유형\n
    saNo: 교차로 그룹 번호\n
    ringType: 신호등 링 유형\n
    ringTime: 신호등 링 운영 허용 시간\n
    genMain: 일반 제메인 형식 (차량 신호를 어떻게 제어하는지)\n
    spcMain: 시차 제메인 형식 (조건에 따라 시간 바뀜)\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getSignalLc')
        
class IncidentInfo(_ITSInfo):
    """
    돌발상황 정보 클래스\n
    
    필드:\n
    colDate: 수집 날짜\n
    aidsId: 돌발 감지기 ID\n
    aidsName: 돌발 감지기 위치\n
    direction: 방면\n
    incidentId: 돌발 상황 ID\n
    xCrdn: 경도\n
    yCrdn: 위도\n
    bearing: 진행 방위
    sectorNo: 섹터 번호\n
    spd: 속도\n
    detectType: 탐지 유형\n
    warnLevel: 경고 수준\n
    resultDesc: 돌발 분석 설명\n
    """
    
    def __init__(self) -> None:
        self.data = _get_data('getIdscTrff', do_retry=False) #type: ignore