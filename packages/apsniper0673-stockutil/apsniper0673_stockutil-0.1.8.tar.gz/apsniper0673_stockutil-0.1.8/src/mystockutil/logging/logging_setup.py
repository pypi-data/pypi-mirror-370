import logging
    
# 로거 생성
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

# 중복 핸들러 방지
if logger.hasHandlers():
    logger.handlers.clear()


# 전파 막기 (중복 출력 방지)
logger.propagate = False

# 콘솔 핸들러 생성
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 파일 핸들러 생성
file_handler = logging.FileHandler('stock.log')
file_handler.setLevel(logging.DEBUG)

# 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s - %(asctime)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# LoggerAdapter 사용하여 파일별 접두어 설정
class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra['prefix'], msg), kwargs

# 각 파일마다 'prefix'를 다르게 설정
def get_custom_logger(prefix):
    return CustomAdapter(logger, {'prefix': prefix})