from enum import Enum, unique


class NetworkTypeEnum(Enum):
    """
    Enumeration of network types
    """
    input = "input"
    output = "output"

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DeviceModificationTypeEnum(Enum):
    """
    Enumeration of modification types for devices
    """
    smart_meter = "smart_meter"
    modem = "modem"

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class NetworkSysTypeEnum(Enum):  # TODO: move to reception sdk
    """
    Enumeration of system types for application networks
    """
    OUTPUT_OLD_LK = "OUTPUT_OLD_LK"
    OUTPUT_NEW_LK = "OUTPUT_NEW_LK"
    OUTPUT_DATA_LOGGER_DEVICE_DATA = "OUTPUT_DATA_LOGGER_DEVICE_DATA"
    OUTPUT_DATA_AGGREGATOR_DEVICE_DATA = "OUTPUT_DATA_AGGREGATOR_DEVICE_DATA"
    INPUT_NBIOT = "INPUT_NBIOT"
    INPUT_LORA = "INPUT_LORA"
    INPUT_KAFKA_BS0 = "INPUT_KAFKA_BS0"
    INPUT_HTTP_BS = "INPUT_HTTP_BS"
    INPUT_NEW_LK = "INPUT_NEW_LK"
    INPUT_EXTERNAL_API = "INPUT_EXTERNAL_API"
    INPUT_UNIVERSAL_API = "INPUT_UNIVERSAL_API"

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class ProtocolEnum(Enum):
    """
    Enumeration of protocols for packets
    """
    WATER5_V_NERO_V0 = 'WATER5_V_NERO_V0'
    NCP_SMP_V0 = 'NCP_SMP_V0'
    SMP_V0 = 'SMP_V0'
    SMP_M_GAS_METER_V0 = 'SMP_M_GAS_METER_V0'
    SMP_M_ENERGY_METER_V0 = 'SMP_M_ENERGY_METER_V0'
    SMP_M_ENERGY_METER_V1 = 'SMP_M_ENERGY_METER_V1'
    SMP_M_JUPITER_08B_V0 = 'SMP_M_JUPITER_08B_V0'
    SMP_M_JUPITER_12B_V0 = 'SMP_M_JUPITER_12B_V0'
    SMP_M_JUPITER_16B_V0 = 'SMP_M_JUPITER_16B_V0'
    SMP_M_WATER_METER_04B_V0 = 'SMP_M_WATER_METER_04B_V0'
    SMP_M_WATER_METER_08B_V0 = 'SMP_M_WATER_METER_08B_V0'
    SMP_M_WATER_METER_12B_V0 = 'SMP_M_WATER_METER_12B_V0'
    SMP_M_WATER_METER_16B_V0 = 'SMP_M_WATER_METER_16B_V0'
    SMP_M_HEAT_PROXY_METER_16B_V0 = 'SMP_M_HEAT_PROXY_METER_16B_V0'
    SMP_M_HEAT_GROUP_METER_V0 = 'SMP_M_HEAT_GROUP_METER_V0'
    WATER5_V_JUPITER_FREESCALE_V0 = 'WATER5_V_JUPITER_FREESCALE_V0'
    WATER5_V_JUPITER_STM_V0 = 'WATER5_V_JUPITER_STM_V0'
    WATER5_V_FLUO_STM_V0 = 'WATER5_V_FLUO_STM_V0'
    WATER5_V_FLUO_FREESCALE_V0 = 'WATER5_V_FLUO_FREESCALE_V0'
    WATER5_V_FLUO_A_V0 = 'WATER5_V_FLUO_A_V0'
    WATER5_V_FLUO_S_V0 = 'WATER5_V_FLUO_S_V0'
    WATER5_V_GAS_V0 = 'WATER5_V_GAS_V0'
    WATER5_V_JUPITER_LORA_V0 = 'WATER5_V_JUPITER_LORA_V0'
    WATER5_V_FLUO_LORA_V0 = 'WATER5_V_FLUO_LORA_V0'
    SMP_M_INTERNAL_INFO_DATA = 'SMP_M_INTERNAL_INFO_DATA'
    ARVAS_API_V0 = 'ARVAS_API_V0'
    UNIVERSAL_API_V0 = 'UNIVERSAL_API_V0'
    SMP_M_DOWNLINK_V0 = 'SMP_M_DOWNLINK_V0'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class IntegrationV0MessageErrorType(Enum):
    """
    Enumeration of error types
    """
    none = 'none'
    device_unidentified = 'device_unidentified'
    data_undecryptable = 'data_undecryptable'
    data_unparsable = 'data_unparsable'
    mac_duplicated = 'mac_duplicated'
    packet_from_the_future = 'packet_from_the_future'
    packet_from_the_past = 'packet_from_the_past'
    error_unidentified = 'error_unidentified'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class EncryptionType(Enum):  # DO NOT CHANGE, DEPENDENCY BY RECEPTION INTERFACE!!!!!!!
    """
    Enumeration of encryption types
    """
    NO_ENCRYPTION = 'NO_ENCRYPTION'
    XTEA_V_NERO_V0 = 'XTEA_V_NERO_V0'
    AES_ECB_V_NERO_V0 = 'AES_ECB_V_NERO_V0'
    KUZNECHIK_V_NERO_V0 = 'KUZNECHIK_V_NERO_V0'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class ResourceKind(Enum):
    """
    Enumeration of resource kinds for devices
    """
    COMMON_CONSUMED = 'COMMON_CONSUMED'
    COMMON_GENERATED = 'COMMON_GENERATED'
    COMMON_ACTIVE_GENERATED = 'COMMON_ACTIVE_GENERATED'
    COMMON_ACTIVE_CONSUMED = 'COMMON_ACTIVE_CONSUMED'
    COMMON_REACTIVE_GENERATED = 'COMMON_REACTIVE_GENERATED'
    COMMON_REACTIVE_CONSUMED = 'COMMON_REACTIVE_CONSUMED'
    PHASE_A_ACTIVE_CONSUMED = 'PHASE_A_ACTIVE_CONSUMED'
    PHASE_A_ACTIVE_GENERATED = 'PHASE_A_ACTIVE_GENERATED'
    PHASE_A_REACTIVE_CONSUMED = 'PHASE_A_REACTIVE_CONSUMED'
    PHASE_A_REACTIVE_GENERATED = 'PHASE_A_REACTIVE_GENERATED'
    PHASE_B_ACTIVE_CONSUMED = 'PHASE_B_ACTIVE_CONSUMED'
    PHASE_B_ACTIVE_GENERATED = 'PHASE_B_ACTIVE_GENERATED'
    PHASE_B_REACTIVE_CONSUMED = 'PHASE_B_REACTIVE_CONSUMED'
    PHASE_B_REACTIVE_GENERATED = 'PHASE_B_REACTIVE_GENERATED'
    PHASE_C_ACTIVE_CONSUMED = 'PHASE_C_ACTIVE_CONSUMED'
    PHASE_C_ACTIVE_GENERATED = 'PHASE_C_ACTIVE_GENERATED'
    PHASE_C_REACTIVE_CONSUMED = 'PHASE_C_REACTIVE_CONSUMED'
    PHASE_C_REACTIVE_GENERATED = 'PHASE_C_REACTIVE_GENERATED'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class SensorType(Enum):
    """
    Enumeration of sensor types for devices
    """
    ENERGY_METER_VOLTAGE = 'ENERGY_METER_VOLTAGE'
    ENERGY_METER_VOLTAGE_LINEAR = 'ENERGY_METER_VOLTAGE_LINEAR'
    ENERGY_METER_VOLTAGE_NEUTRAL = 'ENERGY_METER_VOLTAGE_NEUTRAL'
    ENERGY_METER_VOLTAGE_PHASE_A = 'ENERGY_METER_VOLTAGE_PHASE_A'
    ENERGY_METER_VOLTAGE_PHASE_B = 'ENERGY_METER_VOLTAGE_PHASE_B'
    ENERGY_METER_VOLTAGE_PHASE_C = 'ENERGY_METER_VOLTAGE_PHASE_C'
    ENERGY_METER_CURRENT = 'ENERGY_METER_CURRENT'
    ENERGY_METER_CURRENT_LINEAR = 'ENERGY_METER_CURRENT_LINEAR'
    ENERGY_METER_CURRENT_NEUTRAL = 'ENERGY_METER_CURRENT_NEUTRAL'
    ENERGY_METER_CURRENT_PHASE_A = 'ENERGY_METER_CURRENT_PHASE_A'
    ENERGY_METER_CURRENT_PHASE_B = 'ENERGY_METER_CURRENT_PHASE_B'
    ENERGY_METER_CURRENT_PHASE_C = 'ENERGY_METER_CURRENT_PHASE_C'
    ENERGY_METER_FREQUENCY = 'ENERGY_METER_FREQUENCY'
    ENERGY_METER_FREQUENCY_LINEAR = 'ENERGY_METER_FREQUENCY_LINEAR'
    ENERGY_METER_FREQUENCY_NEUTRAL = 'ENERGY_METER_FREQUENCY_NEUTRAL'
    ENERGY_METER_FREQUENCY_PHASE_A = 'ENERGY_METER_FREQUENCY_PHASE_A'
    ENERGY_METER_FREQUENCY_PHASE_B = 'ENERGY_METER_FREQUENCY_PHASE_B'
    ENERGY_METER_FREQUENCY_PHASE_C = 'ENERGY_METER_FREQUENCY_PHASE_C'
    ENERGY_METER_POWER_FACTOR = 'ENERGY_METER_POWER_FACTOR'
    ENERGY_METER_POWER_FACTOR_LINEAR = 'ENERGY_METER_POWER_FACTOR_LINEAR'
    ENERGY_METER_POWER_FACTOR_NEUTRAL = 'ENERGY_METER_POWER_FACTOR_NEUTRAL'
    ENERGY_METER_POWER_FACTOR_PHASE_A = 'ENERGY_METER_POWER_FACTOR_PHASE_A'
    ENERGY_METER_POWER_FACTOR_PHASE_B = 'ENERGY_METER_POWER_FACTOR_PHASE_B'
    ENERGY_METER_POWER_FACTOR_PHASE_C = 'ENERGY_METER_POWER_FACTOR_PHASE_C'
    TEMPERATURE = 'TEMPERATURE'
    BATTERY = 'BATTERY'
    UPTIME = 'UPTIME'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class JournalDataType(Enum):
    """
    Enumeration of journal data types
    """
    END_OF_DAY = 'END_OF_DAY'
    END_OF_MONTH = 'END_OF_MONTH'
    END_OF_YEAR = 'END_OF_YEAR'
    CURRENT = 'CURRENT'


class DeviceValueMarker(Enum):
    """
    Enumeration of markers for device values
    """
    NO_DOUBT = 'NO_DOUBT'
    OVERFLOW = 'OVERFLOW'
    OVERFLOW_SUSPICIOUS = 'OVERFLOW_SUSPICIOUS'
    NOT_CHECKED = 'NOT_CHECKED'
    REJECTED_OVERFLOW = 'REJECTED_OVERFLOW'
    REJECTED_VALUE = 'REJECTED_VALUE'
    VALUE_INVALID = 'VALUE_INVALID'
    VALUE_MISSING = 'VALUE_MISSING'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DeviceEventLevelEnum(Enum):
    """
    Enumeration of event levels for devices
    """
    CRITICAL = 'CRITICAL'    # Критические события
    WARNING = 'WARNING'      # Предупреждение
    INFO = 'INFO'            # Информационные события
    SYSTEM = 'SYSTEM'        # Системные события

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


@unique
class IntegrationV0MessageEvent(Enum):
    """
    Enumeration of events for devices
    """
    SYS_NO_DATA = 'SYS_NO_DATA'  # отсутствуют данные за прошедшие сутки по одному из измерителей устройства

    # WATER5 event items (water)
    BATTERY_IS_LOW = 'BATTERY_IS_LOW'  # Указывает на критический уровень заряда батареи
    MAGNET_WAS_DETECTED = 'MAGNET_WAS_DETECTED'  # Указывает на наличие магнита при отправке сообщения (флаг)
    CASE_WAS_OPENED = 'CASE_WAS_OPENED'  # Указание что было открытие корпуса
    TEMPERATURE_LIMIT = 'TEMPERATURE_LIMIT'  # Выход за рамки эксплуатационных норм по температуре

    FLOW_REVERSE = 'FLOW_REVERSE'  # Обратный ход (превышение лимита объема обратного хода за интервал времени, конфигурируется прибором)
    FLOW_SPEED_OVER_LIMIT = 'FLOW_SPEED_OVER_LIMIT'  # Указание что было превышение лимитов скорости потока (для ультразвуковых приборов)
    CONTINUES_CONSUMPTION = 'CONTINUES_CONSUMPTION'  # Событие непрерывного потребления (потенциальная утечка)
    NO_WATER = 'NO_WATER'  # don't use  #   Событие нет воды (для ультразвуковых приборов воды)
    NO_RESOURCE = 'NO_RESOURCE'  # Событие нет ресурса (для ультразвуковых приборов)
    BATTERY_WARNING = 'BATTERY_WARNING'  # Предупреждение о низком заряде (1 порог) батареи (конфигурируется прибором)
    BATTERY_OR_TEMPERATURE_LIMITS = 'BATTERY_OR_TEMPERATURE_LIMITS'  # Выход за рамки эксплуатационных норм по батарее или температуре
    LOW_AMBIENT_TEMPERATURE = 'LOW_AMBIENT_TEMPERATURE'  # Низкая температура окружающей среды

    RESET = 'RESET'  # Была перезагрузка МК по неизвестной причине
    RESET_POWER_ON = 'RESET_POWER_ON'  # POR flag (power on) – подача питания на МК (возможное вскрытие прибора)
    RESET_PIN = 'RESET_PIN'  # Pin reset flag - сброс по сигналу на ножке Reset микроконтроллера (NRST) (внештатная ситуация, сильная электромагнитная наводка ИЛИ кто-то вскрыл прибор и перезагрузил его)
    RESET_LOW_VOLTAGE = 'RESET_LOW_VOLTAGE'  # BOR flag, произошел Reset по причине нехватки заряда батареи
    RESET_SOFTWARE = 'RESET_SOFTWARE'  # Произошла программная ошибка, которую программа не смогла обработать. Или происходит перезагрузка после обновления = штатная ситуация
    RESET_WATCHDOG = 'RESET_WATCHDOG'  # Сброс микроконтроллера по причине его зависания
    RESET_HARD_FAULT = 'RESET_HARD_FAULT'  # hard fault occurred - произошла ошибка в работе периферии MCU, либо доступ по недопустимому адресу памяти.

    ERROR = 'ERROR'  # известная ошибка
    ERROR_SENSOR = 'ERROR_SENSOR'  # Событие неисправности какого-то сенсора
    ERROR_SYSTEM = 'ERROR_SYSTEM'  # Указание что была внутренняя ошибка ПО. Программа сама обработала сбой
    ERROR_SENSOR_MEASUREMENT = 'ERROR_SENSOR_MEASUREMENT'  # Указание что была ошибка измерителя показаний
    ERROR_SENSOR_TEMPERATURE = 'ERROR_SENSOR_TEMPERATURE'  # Указание что был сбой внешнего датчика температуры
    ERROR_MEASUREMENT = 'ERROR_MEASUREMENT'  # Указание что была ошибка в метрологическом алгоритме или внешнем устройстве
    ERROR_LOW_VOLTAGE = 'ERROR_LOW_VOLTAGE'  # Ошибка внутренних часов
    ERROR_INTERNAL_CLOCK = 'ERROR_INTERNAL_CLOCK'  # Ошибка внутренних часов
    ERROR_FLASH = 'ERROR_FLASH'  # Ошибка связанная с доступом к внутренней флеш-памяти
    ERROR_EEPROM = 'ERROR_EEPROM'  # Ошибка связанная с доступом к внешней флеш-памяти
    ERROR_RADIO = 'ERROR_RADIO'  # Ошибка радиомодуля
    ERROR_DISPLAY = 'ERROR_DISPLAY'  # Ошибка дисплея (флаг)
    ERROR_PLC = 'ERROR_PLC'  # Ошибка работы PLC-модуля (флаг)
    ERROR_RESET = 'ERROR_RESET'  # Ошибка после перезагрузки МК (флаг)
    IMPACT_POWER_LOST = 'IMPACT_POWER_LOST'  # Указание на выключение внешнего питания (флаг)
    IMPACT_MAGNET = 'IMPACT_MAGNET'  # Указание на наличие магнита (флаг)
    IMPACT_CLEAT_TAMPER = 'IMPACT_CLEAT_TAMPER'  # Указание на вскрытие темпера клеммника (флаг)
    IMPACT_RADIO = 'IMPACT_RADIO'  # Указание на воздействие радиосигналом (флаг)
    OTHER = 'OTHER'  # Другое событие которое система не смогла обработать

    # SMP-M event items (heat)
    ERROR_METER_SYNC = 'ERROR_METER_SYNC'  # Ошибка связанная с низким зарядом батареи
    # SMP event items (electricity)
    NONE = 'NONE'  # Событие отсутствует. С кодом не передается вообще никаких данных
    SUCCESSFUL_AUTO_DIAGNOSTIC = 'SUCCESSFUL_AUTO_DIAGNOSTIC'  # Удачная самодиагностика
    SETUP_UPDATE = 'SETUP_UPDATE'  # Перепрошивка счетчика по интерфейсу
    SWITCH_WINTER_DAYLIGHT = 'SWITCH_WINTER_DAYLIGHT'  # Переход на зимнее время
    SWITCH_SUMMER_DAYLIGHT = 'SWITCH_SUMMER_DAYLIGHT'  # Переход на летнее время
    RECORD_DATETIME = 'RECORD_DATETIME'  # Запись времени, даты
    CHANGE_OFFSET_DAILY_CLOCK = 'CHANGE_OFFSET_DAILY_CLOCK'  # Изменение поправки суточного хода часов
    PERMISSION_SWITCH_DAYLIGHT_ON = 'PERMISSION_SWITCH_DAYLIGHT_ON'  # Включение разрешения перехода зима\лето
    PERMISSION_SWITCH_DAYLIGHT_OFF = 'PERMISSION_SWITCH_DAYLIGHT_OFF'  # Отключение разрешения перехода зима\лето
    CHANGE_DATE_TIME_SWITCH_DAYLIGHT = 'CHANGE_DATE_TIME_SWITCH_DAYLIGHT'  # Изменение дат и времени перехода зима\лето\зима
    ERASE_EEPROM = 'ERASE_EEPROM'  # Полная очистка EEPROM
    NULLIFY_TARIFF_ACCUMULATION = 'NULLIFY_TARIFF_ACCUMULATION'  # Обнуление тарифных накопителей
    NULLIFY_INTERVAL_ACCUMULATION = 'NULLIFY_INTERVAL_ACCUMULATION'  # Обнуление накоплений за интервалы
    RESET_PASSWORD = 'RESET_PASSWORD'  # Сброс/изменение паролей
    RESET_POWER_LOST_TIME_COUNTER = 'RESET_POWER_LOST_TIME_COUNTER'  # Сброс счетчика времени отсутствия питания
    RESET_MAGNET_IMPACT_TIME_COUNTER = 'RESET_MAGNET_IMPACT_TIME_COUNTER'  # Сброс счетчика времени возд. магнитом
    RESET_POWER_INCREASE_TIME_COUNTER = 'RESET_POWER_INCREASE_TIME_COUNTER'  # Сброс счетчика времени повыш. питания
    RESET_POWER_DECREASE_TIME_COUNTER = 'RESET_POWER_DECREASE_TIME_COUNTER'  # Сброс счетчика времени пониж. питания
    RESET_MAINTS_FREQ_DIVERGENCE_TIME_COUNTER = 'RESET_MAINTS_FREQ_DIVERGENCE_TIME_COUNTER'  # Сброс счетчика времени отклонения частоты сети за порог
    RESET_POWER_OVER_LIMIT_TIME_COUNTER = 'RESET_POWER_OVER_LIMIT_TIME_COUNTER'  # Сброс счетчика времени сверхлимитной мощности
    CHANGE_CAPACITY_DATA_LCD = 'CHANGE_CAPACITY_DATA_LCD'  # Изменение разрядности данных на ЖКИ
    CHANGE_TARIFF_METHODS = 'CHANGE_TARIFF_METHODS'  # Изменение способа тарификации
    CHANGE_TARIFF_PROGRAMS = 'CHANGE_TARIFF_PROGRAMS'  # Изменение тарифных расписаний
    CHANGE_ACTUAL_SEASON_SCHEDULES = 'CHANGE_ACTUAL_SEASON_SCHEDULES'  # Смена актуальной группы сезонных расписаний
    CHANGE_CONSUMPTION_LIMIT = 'CHANGE_CONSUMPTION_LIMIT'  # Изменение лимитов потребления
    CHANGE_LOW_THRESHOLD_VOLTAGE = 'CHANGE_LOW_THRESHOLD_VOLTAGE'  # Изменение нижнего порога напряжения
    CHANGE_HIGH_THRESHOLD_VOLTAGE = 'CHANGE_HIGH_THRESHOLD_VOLTAGE'  # Изменение верхнего порога напряжения
    CHANGE_MAINTS_FREQ_THRESHOLD = 'CHANGE_MAINTS_FREQ_THRESHOLD'  # Изменение порога частоты сети
    CHANGE_THRESHOLD_LOW_CONSUMPTION = 'CHANGE_THRESHOLD_LOW_CONSUMPTION'  # Изменение порога малого потребления
    RECHARGE_ENERGY_PAYMENT = 'RECHARGE_ENERGY_PAYMENT'  # Пополнение оплаты энергии
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_INTERNAL_CLOCK = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_INTERNAL_CLOCK'  # Неудачная самодиагностика встроенных часов
    ABNORMAL_COUNTER_AUTOSTART = 'ABNORMAL_COUNTER_AUTOSTART'  # Нештатные автостарты счетчика
    EXTERNAL_POWER_LOST = 'EXTERNAL_POWER_LOST'  # Пропало внешнее питание
    EXTERNAL_POWER_DETECTED = 'EXTERNAL_POWER_DETECTED'  # Появилось внешнее питание
    START_POWER_OVER_LIMIT = 'START_POWER_OVER_LIMIT'  # Начало превышения лимитов мощности
    STOP_POWER_OVER_LIMIT = 'STOP_POWER_OVER_LIMIT'  # Окончание превышения лимитов мощности
    ENERGY_OVER_LIMIT_1 = 'ENERGY_OVER_LIMIT_1'  # Превышение лимита энергии 1 (суммарно по трем фазам)
    ENERGY_OVER_LIMIT_2 = 'ENERGY_OVER_LIMIT_2'  # Превышение лимита энергии 2 (суммарно по трем фазам)
    ENERGY_OVER_LIMIT_3 = 'ENERGY_OVER_LIMIT_3'  # Превышение лимита энергии 3
    WRONG_PASSWORD_BLOCK = 'WRONG_PASSWORD_BLOCK'  # Блокировка по неверному паролю (после 3-х попыток авторизации к счетчику с неправильным паролем в течение календарных суток)
    WRONG_PASSWORD_APPEAL = 'WRONG_PASSWORD_APPEAL'  # Обращение по неверному паролю
    EXHAUST_DAILY_BATTERY_LIFE_LIMIT = 'EXHAUST_DAILY_BATTERY_LIFE_LIMIT'  # Исчерпание суточного лимита работы от батареи
    START_MAGNET_IMPACT = 'START_MAGNET_IMPACT'  # Начало воздействия магнитом (воздействия постоянным магнитным полем)
    STOP_MAGNET_IMPACT = 'STOP_MAGNET_IMPACT'  # Окончание воздействия магнитом (воздействия постоянным магнитным полем)
    VIOLATION_TERMINAL_BLOCK_SEAL = 'VIOLATION_TERMINAL_BLOCK_SEAL'  # Нарушение электронной пломбы клеммной крышки, вскрытие
    RECOVERY_TERMINAL_BLOCK_SEAL = 'RECOVERY_TERMINAL_BLOCK_SEAL'  # Восстановление электронной пломбы клеммной крышки
    VIOLATION_CASE_SEAL = 'VIOLATION_CASE_SEAL'  # Нарушение электронной пломбы корпуса
    RECOVERY_CASE_SEAL = 'RECOVERY_CASE_SEAL'  # Восстановление электронной пломбы корпуса
    TIME_OUT_SYNC_LIMIT = 'TIME_OUT_SYNC_LIMIT'  # Превышение лимита рассинхронизации времени
    CRITICAL_DIVERGENCE_TIME = 'CRITICAL_DIVERGENCE_TIME'  # Критическое расхождение времени
    OVERHEAT_COUNTER_START = 'OVERHEAT_COUNTER_START'  # Перегрев счетчика, начало
    OVERHEAT_COUNTER_STOP = 'OVERHEAT_COUNTER_STOP'  # Перегрев счетчика, окончание
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEMORY = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEMORY'  # Неудачная самодиагностика памяти
    LOW_BATTERY_CAPACITY = 'LOW_BATTERY_CAPACITY'  # Низкий ресурс батареи
    RECOVERY_BATTERY_WORKING_VOLTAGE = 'RECOVERY_BATTERY_WORKING_VOLTAGE'  # Восстановление рабочего напряжения батареи
    LOW_CONSUMPTION = 'LOW_CONSUMPTION'  # Низкое потребление
    RESET_FLAG_LOW_CONSUMPTION = 'RESET_FLAG_LOW_CONSUMPTION'  # Сброс признака низкого потребления
    CHANGE_VALIDATION_SETTINGS = 'CHANGE_VALIDATION_SETTINGS'  # Изменение настроек индикации
    CHANGE_TARIFFICATION_PARAMETERS = 'CHANGE_TARIFFICATION_PARAMETERS'  # Изменение параметров тарификации  # NEW
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEASUREMENT_BLOCK = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEASUREMENT_BLOCK'  # Неудачная самодиагностика измерительного блока
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_CALCULATION_BLOCK = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_CALCULATION_BLOCK'  # Неудачная самодиагностика вычислительного блока
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_POWER_BLOCK = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_POWER_BLOCK'  # Неудачная самодиагностика блока питания
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_SCREEN = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_SCREEN'  # Неудачная самодиагностика дисплея
    UNSUCCESSFUL_AUTO_DIAGNOSTIC_RADIO = 'UNSUCCESSFUL_AUTO_DIAGNOSTIC_RADIO'  # Неудачная самодиагностика радио
    MAINS_VOLTAGE_LOST_PHASE_A_START = 'MAINS_VOLTAGE_LOST_PHASE_A_START'  # Пропадание сетевого напряжения в фазе А. Начало.
    MAINS_VOLTAGE_LOST_PHASE_A_STOP = 'MAINS_VOLTAGE_LOST_PHASE_A_STOP'  # Пропадание сетевого напряжения в фазе А. Окончание.
    MAINS_VOLTAGE_LOST_PHASE_B_START = 'MAINS_VOLTAGE_LOST_PHASE_B_START'  # Пропадание сетевого напряжения в фазе B. Начало.
    MAINS_VOLTAGE_LOST_PHASE_B_STOP = 'MAINS_VOLTAGE_LOST_PHASE_B_STOP'  # Пропадание сетевого напряжения в фазе B. Окончание.
    MAINS_VOLTAGE_LOST_PHASE_C_START = 'MAINS_VOLTAGE_LOST_PHASE_C_START'  # Пропадание сетевого напряжения в фазе C. Начало.
    MAINS_VOLTAGE_LOST_PHASE_C_STOP = 'MAINS_VOLTAGE_LOST_PHASE_C_STOP'  # Пропадание сетевого напряжения в фазе C. Окончание.
    VOLTAGE_LAYDOWN_PHASE_A_START = 'VOLTAGE_LAYDOWN_PHASE_A_START'  # Провал напряжения фазы A. Начало.
    VOLTAGE_LAYDOWN_PHASE_A_STOP = 'VOLTAGE_LAYDOWN_PHASE_A_STOP'  # Провал напряжения фазы A. Окончание.
    VOLTAGE_LAYDOWN_PHASE_B_START = 'VOLTAGE_LAYDOWN_PHASE_B_START'  # Провал напряжения фазы B. Начало.
    VOLTAGE_LAYDOWN_PHASE_B_STOP = 'VOLTAGE_LAYDOWN_PHASE_B_STOP'  # Провал напряжения фазы B. Окончание.
    VOLTAGE_LAYDOWN_PHASE_C_START = 'VOLTAGE_LAYDOWN_PHASE_C_START'  # Провал напряжения фазы C. Начало.
    VOLTAGE_LAYDOWN_PHASE_C_STOP = 'VOLTAGE_LAYDOWN_PHASE_C_STOP'  # Провал напряжения фазы C. Окончание.
    OVERVOLTAGE_PHASE_A_START = 'OVERVOLTAGE_PHASE_A_START'  # Перенапряжение в фазе A. Начало.
    OVERVOLTAGE_PHASE_A_STOP = 'OVERVOLTAGE_PHASE_A_STOP'  # Перенапряжение в фазе A. Окончание.
    OVERVOLTAGE_PHASE_B_START = 'OVERVOLTAGE_PHASE_B_START'  # Перенапряжение в фазе B. Начало.
    OVERVOLTAGE_PHASE_B_STOP = 'OVERVOLTAGE_PHASE_B_STOP'  # Перенапряжение в фазе B. Окончание.
    OVERVOLTAGE_PHASE_C_START = 'OVERVOLTAGE_PHASE_C_START'  # Перенапряжение в фазе C. Начало.
    OVERVOLTAGE_PHASE_C_STOP = 'OVERVOLTAGE_PHASE_C_STOP'  # Перенапряжение в фазе C. Окончание.
    OVERCURRENT_PHASE_A_START = 'OVERCURRENT_PHASE_A_START'  # Превышение тока в фазе A. Начало.
    OVERCURRENT_PHASE_A_STOP = 'OVERCURRENT_PHASE_A_STOP'  # Превышение тока в фазе A. Окончание.
    OVERCURRENT_PHASE_B_START = 'OVERCURRENT_PHASE_B_START'  # Превышение тока в фазе B. Начало.
    OVERCURRENT_PHASE_B_STOP = 'OVERCURRENT_PHASE_B_STOP'  # Превышение тока в фазе B. Окончание.
    OVERCURRENT_PHASE_C_START = 'OVERCURRENT_PHASE_C_START'  # Превышение тока в фазе C. Начало.
    OVERCURRENT_PHASE_C_STOP = 'OVERCURRENT_PHASE_C_STOP'  # Превышение тока в фазе C. Окончание.
    CURRENT_SUM_THRESHOLD_LOW_START = 'CURRENT_SUM_THRESHOLD_LOW_START'  # Суммарный ток ниже порога. Начало.
    CURRENT_SUM_THRESHOLD_LOW_STOP = 'CURRENT_SUM_THRESHOLD_LOW_STOP'  # Суммарный ток ниже порога. Окончание.
    FREQ_OUT_PHASE_A_START = 'FREQ_OUT_PHASE_A_START'  # Выход частоты в фазе A за установленный порог. Начало.
    FREQ_OUT_PHASE_A_STOP = 'FREQ_OUT_PHASE_A_STOP'  # Выход частоты в фазе A за установленный порог. Окончание.
    FREQ_OUT_PHASE_B_START = 'FREQ_OUT_PHASE_B_START'  # Выход частоты в фазе B за установленный порог. Начало.
    FREQ_OUT_PHASE_B_STOP = 'FREQ_OUT_PHASE_B_STOP'  # Выход частоты в фазе B за установленный порог. Окончание.
    FREQ_OUT_PHASE_C_START = 'FREQ_OUT_PHASE_C_START'  # Выход частоты в фазе C за установленный порог. Начало.
    FREQ_OUT_PHASE_C_STOP = 'FREQ_OUT_PHASE_C_STOP'  # Выход частоты в фазе C за установленный порог. Окончание.
    PHASE_ORDER_DISTURBANCE_START = 'PHASE_ORDER_DISTURBANCE_START'  # Нарушение порядка чередования фаз. Начало.
    PHASE_ORDER_DISTURBANCE_STOP = 'PHASE_ORDER_DISTURBANCE_STOP'  # Нарушение порядка чередования фаз. Окончание.
    RADIO_IMPACT_START = 'RADIO_IMPACT_START'  # Воздействие радиополем. Начало.
    RADIO_IMPACT_STOP = 'RADIO_IMPACT_STOP'  # Воздействие радиополем. Окончание.
    DAYLIGHT_TIME_SWITCH = 'DAYLIGHT_TIME_SWITCH'  # Переход на зимнее/летнее время
    DAYLIGHT_TIME_MODE_DATES_CHANGE = 'DAYLIGHT_TIME_MODE_DATES_CHANGE'  # Изменение режима или дат перехода зима/лето
    INTERNAL_CLOCK_SYNC = 'INTERNAL_CLOCK_SYNC'  # Синхронизация встроенных часов
    METROLOGY_CHANGE = 'METROLOGY_CHANGE'  # Изменение метрологии
    PROFILE_CONF_CHANGE = 'PROFILE_CONF_CHANGE'  # Изменение конфигурации профиля
    TARIFFICATION_METHOD_CHANGE = 'TARIFFICATION_METHOD_CHANGE'  # Изменение способа тарификации
    PERMISSION_CHANGE_SETTINGS_POWER_CONTROL = 'PERMISSION_CHANGE_SETTINGS_POWER_CONTROL'  # Разрешение и изменение настроек контроля мощности
    CONTROL_LEVEL_MAINS_CHANGE = 'CONTROL_LEVEL_MAINS_CHANGE'  # Изменение уровней контроля сети
    PERMISSION_CHANGE_SETTINGS_CONSUMPTION_CONTROL = 'PERMISSION_CHANGE_SETTINGS_CONSUMPTION_CONTROL'  # Разрешение и изменение контроля потребления
    LOAD_RELAY_CONDITION_SETTINGS_CHANGE = 'LOAD_RELAY_CONDITION_SETTINGS_CHANGE'  # Изменение настроек и условий реле нагрузки
    SIGNALIZATION_RELAY_CONDITION_SETTINGS_CHANGE = 'SIGNALIZATION_RELAY_CONDITION_SETTINGS_CHANGE'  # Изменение настроек и условий реле сигнализации
    INTERFACE_SIGNALIZATION_CONDITION_SETTINGS_CHANGE = 'INTERFACE_SIGNALIZATION_CONDITION_SETTINGS_CHANGE'  # Изменение настроек и условий сигнализации по интерфейсу
    INDICATION_SETTINGS_CHANGE = 'INDICATION_SETTINGS_CHANGE'  # Изменение настроек индикации
    SOUND_SIGNAL_CONDITION_SETTINGS_CHANGE = 'SOUND_SIGNAL_CONDITION_SETTINGS_CHANGE'  # изменение настроек и условий звукового сигнала
    LOAD_RELAY_STATE_CHANGE = 'LOAD_RELAY_STATE_CHANGE'  # Изменение состояния реле нагрузки
    SIGNALIZATION_RELAY_STATE_CHANGE = 'SIGNALIZATION_RELAY_STATE_CHANGE'  # Изменение состояния реле сигнализации
    START_ALTERNATING_MAGNET_IMPACT = 'START_ALTERNATING_MAGNET_IMPACT'  # Начало воздействия магнитом (воздействия постоянным магнитным полем)
    STOP_ALTERNATING_MAGNET_IMPACT = 'STOP_ALTERNATING_MAGNET_IMPACT'  # Окончание воздействия магнитом (воздействия постоянным магнитным полем)
    # Heat event items - system errors
    SYSTEM__CIRCUIT_BREAK_T_SENSOR_1 = 'SYSTEM__CIRCUIT_BREAK_T_SENSOR_1'  # Обрыв/КЗ первого датчика температуры
    SYSTEM__CIRCUIT_BREAK_T_SENSOR_2 = 'SYSTEM__CIRCUIT_BREAK_T_SENSOR_2'  # Обрыв/КЗ второго датчика температуры
    SYSTEM__CIRCUIT_BREAK_T_SENSOR_3 = 'SYSTEM__CIRCUIT_BREAK_T_SENSOR_3'  # Обрыв/КЗ третьего датчика температуры
    SYSTEM__ERROR_DELTA_T = 'SYSTEM__ERROR_DELTA_T'  # Ошибка dT
    SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1 = 'SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1'  # Расход меньше уставки Gmin в первом канале расхода системы
    SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2 = 'SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2'  # Расход меньше уставки Gmin во втором канале расхода системы
    SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3 = 'SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3'  # Расход меньше уставки Gmin в третьем канале расхода системы
    SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1 = 'SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1'  # Расход больше уставки Gmax в первом канале расхода системы
    SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2 = 'SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2'  # Расход меньше уставки Gmax во втором канале расхода системы
    SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3 = 'SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3'  # Расход меньше уставки Gmax в третьем канале расхода системы
    SYSTEM__NO_COOLANT_CHANNEL_RATE_1 = 'SYSTEM__NO_COOLANT_CHANNEL_RATE_1'  # Отсутствует теплоноситель в первом канале расхода системы
    SYSTEM__NO_COOLANT_CHANNEL_RATE_2 = 'SYSTEM__NO_COOLANT_CHANNEL_RATE_2'  # Отсутствует теплоноситель во втором канале расхода системы
    SYSTEM__NO_COOLANT_CHANNEL_RATE_3 = 'SYSTEM__NO_COOLANT_CHANNEL_RATE_3'  # Отсутствует теплоноситель в третьем канале расхода системы
    SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1 = 'SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1'  # Обрыв/КЗ возбуждения первого канала расхода системы
    SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2 = 'SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2'  # Обрыв/КЗ возбуждения второго канала расхода системы
    SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1 = 'SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1'  # Обрыв/КЗ первого датчика давления
    SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2 = 'SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2'  # Обрыв/КЗ второго датчика давления
    SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3 = 'SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3'  # Обрыв/КЗ третьего датчика давления
    SYSTEM__REVERSE = 'SYSTEM__REVERSE'  # Реверс в системе
    # Heat event items - device errors
    DEVICE__POWER_SUPPLY_LOST = 'DEVICE__POWER_SUPPLY_LOST'  # Пропадание электропитания прибора
    DEVICE__POWER_SUPPLY_ENABLED = 'DEVICE__POWER_SUPPLY_ENABLED'  # Возобновление электропитания прибора
    DEVICE__COMMON_SETTINGS_CHANGED = 'DEVICE__COMMON_SETTINGS_CHANGED'  # Изменение общих настроек прибора
    DEVICE__ALARM_DIGITAL_INPUT_1 = 'DEVICE__ALARM_DIGITAL_INPUT_1'  # Сработал цифровой вход №1 (тревога)
    DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_1 = 'DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по превышению порога по расходу
    DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_2 = 'DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по превышению порога по расходу
    DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_1 = 'DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по падению расхода ниже порога
    DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_2 = 'DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по падению расхода ниже порога
    DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_1 = 'DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по превышению порога по температуре
    DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_2 = 'DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по превышению порога по температуре
    DEVICE__ALARM_T_LOW_DIGITAL_INPUT_1 = 'DEVICE__ALARM_T_LOW_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по падению температуры ниже порога
    DEVICE__ALARM_T_LOW_DIGITAL_INPUT_2 = 'DEVICE__ALARM_T_LOW_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по падению температуры ниже порога
    DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_1 = 'DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по превышению порога по разнице температур
    DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_2 = 'DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по превышению порога по разнице температур
    DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_1 = 'DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по падению разницы температуры ниже порога
    DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_2 = 'DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по падению разницы температуры ниже порога
    DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_1 = 'DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по превышению порога по мощности
    DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_2 = 'DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по превышению порога по мощности
    DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_1 = 'DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_1'  # Сработал цифровой выход №1 по падению мощности ниже порога
    DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_2 = 'DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_2'  # Сработал цифровой выход №2 по падению мощности ниже порога
    DEVICE__MEASURE_CHANNELS_SETTINGS_CHANGED = 'DEVICE__MEASURE_CHANNELS_SETTINGS_CHANGED'  # Изменение настроек измерительных каналов
    DEVICE__SYSTEM_SETTINGS_CHANGED_1 = 'DEVICE__SYSTEM_SETTINGS_CHANGED_1'  # Изменение настроек Системы 1
    DEVICE__SYSTEM_SETTINGS_CHANGED_2 = 'DEVICE__SYSTEM_SETTINGS_CHANGED_2'  # Изменение настроек Системы 2
    DEVICE__SYSTEM_SETTINGS_CHANGED_3 = 'DEVICE__SYSTEM_SETTINGS_CHANGED_3'  # Изменение настроек Системы 3
    DEVICE__SYSTEM_SETTINGS_CHANGED_4 = 'DEVICE__SYSTEM_SETTINGS_CHANGED_4'  # Изменение настроек Системы 4
    DEVICE__DIGITAL_I_O_SETTINGS_CHANGED = 'DEVICE__DIGITAL_I_O_SETTINGS_CHANGED'  # Изменение настроек цифровых входов/выходов
    DEVICE__DATETIME_CHANGED = 'DEVICE__DATETIME_CHANGED'  # Изменение даты/времени
    DEVICE__ETHERNET_SETTINGS_CHANGED = 'DEVICE__ETHERNET_SETTINGS_CHANGED'  # Изменение настроек интерфейса Ethernet

    # SPODES (are not included to event levels)
    INCORRECT_PHASE_SEQUENCE_START = 'INCORRECT_PHASE_SEQUENCE_START'  # Неправильная последовательность фаз начало
    INCORRECT_PHASE_SEQUENCE_STOP = 'INCORRECT_PHASE_SEQUENCE_STOP'  # Неправильная последовательность фаз окончание

    EXPORT_PHASE_A_START = 'EXPORT_PHASE_A_START'  # Фаза А - экспорт начало
    EXPORT_PHASE_A_STOP = 'EXPORT_PHASE_A_STOP'  # Фаза А - экспорт окончание
    EXPORT_PHASE_B_START = 'EXPORT_PHASE_B_START'  # Фаза B - экспорт начало
    EXPORT_PHASE_B_STOP = 'EXPORT_PHASE_B_STOP'  # Фаза B - экспорт окончание
    EXPORT_PHASE_C_START = 'EXPORT_PHASE_C_START'  # Фаза C - экспорт начало
    EXPORT_PHASE_C_STOP = 'EXPORT_PHASE_C_STOP'  # Фаза C - экспорт окончание

    POWER_OFF = 'POWER_OFF'  # Выключение питания
    POWER_ON = 'POWER_ON'  # Включение питания
    POWER_OFF_REMOTE = 'POWER_OFF_REMOTE'  # Выключение питания дистанционное
    POWER_ON_REMOTE = 'POWER_ON_REMOTE'  # Выключение питания дистанционное
    PERMISSION_TURN_ON_CLIENT = 'PERMISSION_TURN_ON_CLIENT'  # Получение разрешения на включение абоненту
    LOCAL_POWER_OFF_POWER_OVER_LIMIT = 'LOCAL_POWER_OFF_POWER_OVER_LIMIT'  # Выключение локальное по превышению лимита мощности
    LOCAL_POWER_OFF_VOLTAGE_OVER_LIMIT = 'LOCAL_POWER_OFF_VOLTAGE_OVER_LIMIT'  # Bыключение локальное по превышению напряжения
    LOCAL_POWER_ON_VOLTAGE_NORMAL_LEVEL_RETURN = 'LOCAL_POWER_ON_VOLTAGE_NORMAL_LEVEL_RETURN'  # Включение локальное при возвращение напряжения в норму
    LOCAL_POWER_OFF_TEMPERATURE_OVER_LIMIT = 'LOCAL_POWER_OFF_TEMPERATURE_OVER_LIMIT'  # Выключение локальное по температуре
    BACKUP_POWER_ON = 'BACKUP_POWER_ON'  # Включение резервного питания
    BACKUP_POWER_OFF = 'BACKUP_POWER_OFF'  # Отключение резервного питания

    SET_DATETIME = 'SET_DATETIME'  # Установка времени
    CLEAN_MONTH_JOURNAL = 'CLEAN_MONTH_JOURNAL'  # Очистка месячного журнала
    CLEAN_DAY_JOURNAL = 'CLEAN_DAY_JOURNAL'  # Очистка суточного журнала
    CLEAN_VOLTAGE_JOURNAL = 'CLEAN_VOLTAGE_JOURNAL'  # Очистка журнала напряжения
    CLEAN_CURRENT_JOURNAL = 'CLEAN_CURRENT_JOURNAL'  # Очистка журнала тока
    CLEAN_ON_OFF_JOURNAL = 'CLEAN_ON_OFF_JOURNAL'  # Очистка журнала вкл/выкл
    CLEAN_EXTERNAL_IMPACT_JOURNAL = 'CLEAN_EXTERNAL_IMPACT_JOURNAL'  # Очистка журнала внешних воздействий
    MONTHLY_JOURNAL_RECORD_VALUES = 'MONTHLY_JOURNAL_RECORD_VALUES'  # Фиксация показаний в месячном журнал
    CHANGE_AUTHENTICATION_KEY_LOW_PRIVACY = 'CHANGE_AUTHENTICATION_KEY_LOW_PRIVACY'  # Изменение ключа аутентификации для низкой секретности
    CHANGE_AUTHENTICATION_KEY_HIGH_PRIVACY = 'CHANGE_AUTHENTICATION_KEY_HIGH_PRIVACY'  # Изменение ключа аутентификации для высокой секретности
    UPDATE_SOFTWARE = 'UPDATE_SOFTWARE'  # Обновление ПО
    TIME_CORRECTION = 'TIME_CORRECTION'  # Коррекция времени
    CHANGE_CONNECTION_SCHEME = 'CHANGE_CONNECTION_SCHEME'  # Изменение схемы подключения

    MAGNETIC_FIELD_START = 'MAGNETIC_FIELD_START'  # Магнитное поле - начало
    MAGNETIC_FIELD_STOP = 'MAGNETIC_FIELD_STOP'  # Магнитное поле - окончание
    ACTIVATE_TERMINAL_BLOCK_SEAL = 'ACTIVATE_TERMINAL_BLOCK_SEAL'  # Срабатывание электронной пломбы крышки клеммников
    ACTIVATE_CASE_SEAL = 'ACTIVATE_CASE_SEAL'  # Срабатывание электронной пломбы корпуса

    INTERFACE_DISCONNECT = 'INTERFACE_DISCONNECT'  # Разорвано соединение (интерфейс)
    INTERFACE_CONNECT = 'INTERFACE_CONNECT'  # Установлено соединение (интерфейс)

    INTERFACE_UNAUTHORIZED_ACCESS_ATTEMPT = 'INTERFACE_UNAUTHORIZED_ACCESS_ATTEMPT'  # Попытка несанкционированного доступа (интерфейс)
    PROTOCOL_VIOLATION = 'PROTOCOL_VIOLATION'  # Нарушение требований протокола

    DEVICE_INITIALIZATION = 'DEVICE_INITIALIZATION'  # Инициализация ПУ
    MEASUREMENT_BLOCK_ERROR = 'MEASUREMENT_BLOCK_ERROR'  # Измерительный блок – ошибка
    MEASUREMENT_BLOCK_NORMAL = 'MEASUREMENT_BLOCK_NORMAL'  # Измерительный блок – норма
    CALCULATION_BLOCK_ERROR = 'CALCULATION_BLOCK_ERROR'  # Вычислительный блок – ошибка
    CALCULATION_BLOCK_NORMAL = 'CALCULATION_BLOCK_NORMAL'  # Вычислительный блок – норма
    REAL_TIME_CLOCK_ERROR = 'REAL_TIME_CLOCK_ERROR'  # Часы реального времени – ошибка
    REAL_TIME_CLOCK_NORMAL = 'REAL_TIME_CLOCK_NORMAL'  # Часы реального времени – норма
    POWER_BLOCK_ERROR = 'POWER_BLOCK_ERROR'  # Блок питания – ошибка
    POWER_BLOCK_NORMAL = 'POWER_BLOCK_NORMAL'  # Блок питания – норма
    MEMORY_BLOCK_ERROR = 'MEMORY_BLOCK_ERROR'  # Блок памяти – ошибка
    MEMORY_BLOCK_NORMAL = 'MEMORY_BLOCK_NORMAL'  # Блок памяти – норма

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    # grouping by levels

    @classmethod
    def get_critical(cls) -> list['IntegrationV0MessageEvent']:
        return [
            cls.BATTERY_IS_LOW,
            cls.MAGNET_WAS_DETECTED,
            cls.CASE_WAS_OPENED,
            cls.TEMPERATURE_LIMIT,
            cls.RESET_HARD_FAULT,
            cls.ERROR,
            cls.ERROR_SENSOR,
            cls.ERROR_SYSTEM,
            cls.ERROR_SENSOR_MEASUREMENT,
            cls.ERROR_SENSOR_TEMPERATURE,
            cls.ERROR_MEASUREMENT,
            cls.ERROR_LOW_VOLTAGE,
            cls.ERROR_INTERNAL_CLOCK,
            cls.ERROR_FLASH,
            cls.ERROR_EEPROM,
            cls.ERROR_RADIO,
            cls.ERROR_DISPLAY,
            cls.ERROR_PLC,
            cls.ERROR_RESET,
            cls.IMPACT_POWER_LOST,
            cls.IMPACT_MAGNET,
            cls.IMPACT_CLEAT_TAMPER,
            cls.IMPACT_RADIO,
            cls.ERROR_METER_SYNC,
            cls.WRONG_PASSWORD_BLOCK,
            cls.EXHAUST_DAILY_BATTERY_LIFE_LIMIT,
            cls.VIOLATION_TERMINAL_BLOCK_SEAL,
            cls.VIOLATION_CASE_SEAL,
            cls.CRITICAL_DIVERGENCE_TIME,
            cls.SYSTEM__ERROR_DELTA_T,
            cls.DEVICE__POWER_SUPPLY_LOST,
        ]

    @classmethod
    def get_warning(cls) -> list['IntegrationV0MessageEvent']:
        return [
            cls.FLOW_REVERSE,
            cls.FLOW_SPEED_OVER_LIMIT,
            cls.CONTINUES_CONSUMPTION,
            cls.BATTERY_WARNING,
            cls.BATTERY_OR_TEMPERATURE_LIMITS,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_INTERNAL_CLOCK,
            cls.ABNORMAL_COUNTER_AUTOSTART,
            cls.START_POWER_OVER_LIMIT,
            cls.STOP_POWER_OVER_LIMIT,
            cls.ENERGY_OVER_LIMIT_1,
            cls.ENERGY_OVER_LIMIT_2,
            cls.ENERGY_OVER_LIMIT_3,
            cls.WRONG_PASSWORD_APPEAL,
            cls.START_MAGNET_IMPACT,
            cls.STOP_MAGNET_IMPACT,
            cls.TIME_OUT_SYNC_LIMIT,
            cls.OVERHEAT_COUNTER_START,
            cls.OVERHEAT_COUNTER_STOP,
            cls.LOW_BATTERY_CAPACITY,
            cls.LOW_CONSUMPTION,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEASUREMENT_BLOCK,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_CALCULATION_BLOCK,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_POWER_BLOCK,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_SCREEN,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_RADIO,
            cls.MAINS_VOLTAGE_LOST_PHASE_A_START,
            cls.MAINS_VOLTAGE_LOST_PHASE_A_STOP,
            cls.MAINS_VOLTAGE_LOST_PHASE_B_START,
            cls.MAINS_VOLTAGE_LOST_PHASE_B_STOP,
            cls.MAINS_VOLTAGE_LOST_PHASE_C_START,
            cls.MAINS_VOLTAGE_LOST_PHASE_C_STOP,
            cls.VOLTAGE_LAYDOWN_PHASE_A_START,
            cls.VOLTAGE_LAYDOWN_PHASE_A_STOP,
            cls.VOLTAGE_LAYDOWN_PHASE_B_START,
            cls.VOLTAGE_LAYDOWN_PHASE_B_STOP,
            cls.VOLTAGE_LAYDOWN_PHASE_C_START,
            cls.VOLTAGE_LAYDOWN_PHASE_C_STOP,
            cls.OVERVOLTAGE_PHASE_A_START,
            cls.OVERVOLTAGE_PHASE_A_STOP,
            cls.OVERVOLTAGE_PHASE_B_START,
            cls.OVERVOLTAGE_PHASE_B_STOP,
            cls.OVERVOLTAGE_PHASE_C_START,
            cls.OVERVOLTAGE_PHASE_C_STOP,
            cls.OVERCURRENT_PHASE_A_START,
            cls.OVERCURRENT_PHASE_A_STOP,
            cls.OVERCURRENT_PHASE_B_START,
            cls.OVERCURRENT_PHASE_B_STOP,
            cls.OVERCURRENT_PHASE_C_START,
            cls.OVERCURRENT_PHASE_C_STOP,
            cls.CURRENT_SUM_THRESHOLD_LOW_START,
            cls.CURRENT_SUM_THRESHOLD_LOW_STOP,
            cls.FREQ_OUT_PHASE_A_START,
            cls.FREQ_OUT_PHASE_A_STOP,
            cls.FREQ_OUT_PHASE_B_START,
            cls.FREQ_OUT_PHASE_B_STOP,
            cls.FREQ_OUT_PHASE_C_START,
            cls.FREQ_OUT_PHASE_C_STOP,
            cls.PHASE_ORDER_DISTURBANCE_START,
            cls.PHASE_ORDER_DISTURBANCE_STOP,
            cls.RADIO_IMPACT_START,
            cls.RADIO_IMPACT_STOP,
            cls.START_ALTERNATING_MAGNET_IMPACT,
            cls.STOP_ALTERNATING_MAGNET_IMPACT,
            cls.SYSTEM__CIRCUIT_BREAK_T_SENSOR_1,
            cls.SYSTEM__CIRCUIT_BREAK_T_SENSOR_2,
            cls.SYSTEM__CIRCUIT_BREAK_T_SENSOR_3,
            cls.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_1,
            cls.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_2,
            cls.SYSTEM__CONSUMPTION_LOWER_G_MIN_CHANNEL_RATE_3,
            cls.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_1,
            cls.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_2,
            cls.SYSTEM__CONSUMPTION_LOWER_G_MAX_CHANNEL_RATE_3,
            cls.SYSTEM__NO_COOLANT_CHANNEL_RATE_1,
            cls.SYSTEM__NO_COOLANT_CHANNEL_RATE_2,
            cls.SYSTEM__NO_COOLANT_CHANNEL_RATE_3,
            cls.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_1,
            cls.SYSTEM__CIRCUIT_BREAK_STIMULATION_CHANNEL_RATE_2,
            cls.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_1,
            cls.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_2,
            cls.SYSTEM__CIRCUIT_BREAK_PRESSURE_SENSOR_3,
            cls.DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_T_LOW_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_T_LOW_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_2,
        ]

    @classmethod
    def get_info(cls) -> list['IntegrationV0MessageEvent']:
        return [
            cls.SYS_NO_DATA,
            cls.NO_WATER,
            cls.NO_RESOURCE,
            cls.LOW_AMBIENT_TEMPERATURE,
            cls.OTHER,
            cls.NONE,
            cls.SWITCH_WINTER_DAYLIGHT,
            cls.SWITCH_SUMMER_DAYLIGHT,
            cls.RECORD_DATETIME,
            cls.CHANGE_OFFSET_DAILY_CLOCK,
            cls.PERMISSION_SWITCH_DAYLIGHT_ON,
            cls.PERMISSION_SWITCH_DAYLIGHT_OFF,
            cls.CHANGE_DATE_TIME_SWITCH_DAYLIGHT,
            cls.NULLIFY_TARIFF_ACCUMULATION,
            cls.NULLIFY_INTERVAL_ACCUMULATION,
            cls.RESET_POWER_LOST_TIME_COUNTER,
            cls.RESET_MAGNET_IMPACT_TIME_COUNTER,
            cls.RESET_POWER_INCREASE_TIME_COUNTER,
            cls.RESET_POWER_DECREASE_TIME_COUNTER,
            cls.RESET_MAINTS_FREQ_DIVERGENCE_TIME_COUNTER,
            cls.RESET_POWER_OVER_LIMIT_TIME_COUNTER,
            cls.CHANGE_TARIFF_METHODS,
            cls.CHANGE_TARIFF_PROGRAMS,
            cls.CHANGE_ACTUAL_SEASON_SCHEDULES,
            cls.CHANGE_CONSUMPTION_LIMIT,
            cls.CHANGE_LOW_THRESHOLD_VOLTAGE,
            cls.CHANGE_HIGH_THRESHOLD_VOLTAGE,
            cls.CHANGE_MAINTS_FREQ_THRESHOLD,
            cls.CHANGE_THRESHOLD_LOW_CONSUMPTION,
            cls.RECHARGE_ENERGY_PAYMENT,
            cls.RECOVERY_TERMINAL_BLOCK_SEAL,
            cls.RECOVERY_CASE_SEAL,
            cls.RESET_FLAG_LOW_CONSUMPTION,
            cls.CHANGE_VALIDATION_SETTINGS,
            cls.CHANGE_TARIFFICATION_PARAMETERS,
            cls.DAYLIGHT_TIME_SWITCH,
            cls.DAYLIGHT_TIME_MODE_DATES_CHANGE,
            cls.PROFILE_CONF_CHANGE,
            cls.TARIFFICATION_METHOD_CHANGE,
            cls.PERMISSION_CHANGE_SETTINGS_POWER_CONTROL,
            cls.CONTROL_LEVEL_MAINS_CHANGE,
            cls.PERMISSION_CHANGE_SETTINGS_CONSUMPTION_CONTROL,
            cls.LOAD_RELAY_CONDITION_SETTINGS_CHANGE,
            cls.SIGNALIZATION_RELAY_CONDITION_SETTINGS_CHANGE,
            cls.INTERFACE_SIGNALIZATION_CONDITION_SETTINGS_CHANGE,
            cls.INDICATION_SETTINGS_CHANGE,
            cls.SOUND_SIGNAL_CONDITION_SETTINGS_CHANGE,
            cls.LOAD_RELAY_STATE_CHANGE,
            cls.SIGNALIZATION_RELAY_STATE_CHANGE,
            cls.DEVICE__POWER_SUPPLY_ENABLED,
            cls.DEVICE__ALARM_DIGITAL_INPUT_1,
        ]

    @classmethod
    def get_system(cls) -> list['IntegrationV0MessageEvent']:
        return [
            cls.RESET,
            cls.RESET_POWER_ON,
            cls.RESET_PIN,
            cls.RESET_LOW_VOLTAGE,
            cls.RESET_SOFTWARE,
            cls.RESET_WATCHDOG,
            cls.SUCCESSFUL_AUTO_DIAGNOSTIC,
            cls.SETUP_UPDATE,
            cls.ERASE_EEPROM,
            cls.RESET_PASSWORD,
            cls.CHANGE_CAPACITY_DATA_LCD,
            cls.EXTERNAL_POWER_LOST,
            cls.EXTERNAL_POWER_DETECTED,
            cls.UNSUCCESSFUL_AUTO_DIAGNOSTIC_MEMORY,
            cls.RECOVERY_BATTERY_WORKING_VOLTAGE,
            cls.INTERNAL_CLOCK_SYNC,
            cls.METROLOGY_CHANGE,
            cls.SYSTEM__REVERSE,
            cls.DEVICE__COMMON_SETTINGS_CHANGED,
            cls.DEVICE__MEASURE_CHANNELS_SETTINGS_CHANGED,
            cls.DEVICE__SYSTEM_SETTINGS_CHANGED_1,
            cls.DEVICE__SYSTEM_SETTINGS_CHANGED_2,
            cls.DEVICE__SYSTEM_SETTINGS_CHANGED_3,
            cls.DEVICE__SYSTEM_SETTINGS_CHANGED_4,
            cls.DEVICE__DIGITAL_I_O_SETTINGS_CHANGED,
            cls.DEVICE__DATETIME_CHANGED,
            cls.DEVICE__ETHERNET_SETTINGS_CHANGED,
        ]

    @classmethod
    def get_events_by_level(cls, level: DeviceEventLevelEnum) -> list['IntegrationV0MessageEvent']:
        events_levels_mapping = {
            DeviceEventLevelEnum.CRITICAL: cls.get_critical(),
            DeviceEventLevelEnum.WARNING: cls.get_warning(),
            DeviceEventLevelEnum.INFO: cls.get_info(),
            DeviceEventLevelEnum.SYSTEM: cls.get_system(),
        }
        return events_levels_mapping[level]

    @classmethod
    def get_default(cls)-> list['IntegrationV0MessageEvent']:
        return [
            cls.BATTERY_IS_LOW,
            cls.MAGNET_WAS_DETECTED,
            cls.MAGNET_WAS_DETECTED,
            cls.CASE_WAS_OPENED,
            cls.TEMPERATURE_LIMIT,
            cls.FLOW_REVERSE,
            cls.FLOW_SPEED_OVER_LIMIT,
            cls.BATTERY_WARNING,
            cls.BATTERY_OR_TEMPERATURE_LIMITS,
            cls.RESET_HARD_FAULT,
            cls.ERROR,
            cls.ERROR_SENSOR,
            cls.ERROR_SYSTEM,
            cls.ERROR_SENSOR_MEASUREMENT,
            cls.ERROR_SENSOR_TEMPERATURE,
            cls.ERROR_MEASUREMENT,
            cls.ERROR_LOW_VOLTAGE,
            cls.ERROR_LOW_VOLTAGE,
            cls.ERROR_INTERNAL_CLOCK,
            cls.ERROR_FLASH,
            cls.ERROR_EEPROM,
            cls.ERROR_RADIO,
            cls.ERROR_DISPLAY,
            cls.ERROR_PLC,
            cls.ERROR_RESET,
            cls.IMPACT_POWER_LOST,
            cls.IMPACT_MAGNET,
            cls.IMPACT_CLEAT_TAMPER,
            cls.IMPACT_RADIO,
            cls.ERROR_METER_SYNC,
            cls.START_POWER_OVER_LIMIT,
            cls.STOP_POWER_OVER_LIMIT,
            cls.ENERGY_OVER_LIMIT_1,
            cls.ENERGY_OVER_LIMIT_2,
            cls.ENERGY_OVER_LIMIT_3,
            cls.WRONG_PASSWORD_BLOCK,
            cls.EXHAUST_DAILY_BATTERY_LIFE_LIMIT,
            cls.START_MAGNET_IMPACT,
            cls.STOP_MAGNET_IMPACT,
            cls.VIOLATION_TERMINAL_BLOCK_SEAL,
            cls.VIOLATION_CASE_SEAL,
            cls.CRITICAL_DIVERGENCE_TIME,
            cls.OVERHEAT_COUNTER_START,
            cls.OVERHEAT_COUNTER_STOP,
            cls.MAINS_VOLTAGE_LOST_PHASE_A_START,
            cls.MAINS_VOLTAGE_LOST_PHASE_A_STOP,
            cls.MAINS_VOLTAGE_LOST_PHASE_B_START,
            cls.MAINS_VOLTAGE_LOST_PHASE_B_STOP,
            cls.MAINS_VOLTAGE_LOST_PHASE_C_START,
            cls.MAINS_VOLTAGE_LOST_PHASE_C_STOP,
            cls.OVERVOLTAGE_PHASE_A_START,
            cls.OVERVOLTAGE_PHASE_A_STOP,
            cls.OVERVOLTAGE_PHASE_B_START,
            cls.OVERVOLTAGE_PHASE_B_STOP,
            cls.OVERVOLTAGE_PHASE_C_START,
            cls.OVERVOLTAGE_PHASE_C_STOP,
            cls.OVERCURRENT_PHASE_A_START,
            cls.OVERCURRENT_PHASE_A_STOP,
            cls.OVERCURRENT_PHASE_B_START,
            cls.OVERCURRENT_PHASE_B_STOP,
            cls.OVERCURRENT_PHASE_C_START,
            cls.OVERCURRENT_PHASE_C_STOP,
            cls.CURRENT_SUM_THRESHOLD_LOW_START,
            cls.CURRENT_SUM_THRESHOLD_LOW_STOP,
            cls.FREQ_OUT_PHASE_A_START,
            cls.FREQ_OUT_PHASE_A_STOP,
            cls.FREQ_OUT_PHASE_B_START,
            cls.FREQ_OUT_PHASE_B_STOP,
            cls.FREQ_OUT_PHASE_C_START,
            cls.FREQ_OUT_PHASE_C_STOP,
            cls.SYSTEM__CIRCUIT_BREAK_T_SENSOR_1,
            cls.SYSTEM__CIRCUIT_BREAK_T_SENSOR_2,
            cls.SYSTEM__CIRCUIT_BREAK_T_SENSOR_3,
            cls.SYSTEM__ERROR_DELTA_T,
            cls.DEVICE__POWER_SUPPLY_LOST,
            cls.DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_OVERRATE_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_UNDERRATE_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_T_HIGH_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_T_LOW_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_T_LOW_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_DELTA_T_HIGH_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_DELTA_T_LOW_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_POWER_HIGH_DIGITAL_INPUT_2,
            cls.DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_1,
            cls.DEVICE__ALARM_POWER_LOW_DIGITAL_INPUT_2,
        ]

class IntegrationV0MessageMetaBSChannelProtocol(Enum):
    """
    Enumeration of base stations channel protocols
    """
    nbfi = 'nbfi'
    unbp = 'unbp'
    unbp2 = 'unbp2'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class IntervalSelectValue(Enum):
    """
    Enumeration of intervals
    """
    half_hour = '30 minute'
    hour = '60 minutes'
    day = '1 day'
    week = '1 week'
    month = '1 month'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DeviceHack(Enum):
    """
    electricity_profile_packets_days_ago_is_zero: change profile window logic when days_ago = 0 when days_ago=0 fill full hours profile values after packet receive

    electricity_daily_packet_overload_value: change overload value of daily packet to 838861.0, bug was fixed in mid-April 2023 firmware 147:14:17:3:1:1

    electricity_phase_packet_generation_total_enrg_overload_value: change overload value for total energy to 33554431 in generated phase packets
    electricity_phase_packet_consumption_total_enrg_overload_value: change overload value for total energy to 33554431 in consumed phase packets
    """

    electricity_profile_packets_days_ago_is_zero = 'electricity_profile_packets_days_ago_is_zero'
    electricity_phase_packet_generated_total_enrg_overload_value = 'electricity_phase_packet_generated_total_enrg_overload_value'
    electricity_phase_packet_consumed_total_enrg_overload_value = 'electricity_phase_packet_consumed_total_enrg_overload_value'
    electricity_daily_packet_overload_value = 'electricity_daily_packet_overload_value'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DeviceTimeTransition(Enum):
    """
    Enumeration of seasons change
    """
    summer = 'summer'
    winter = 'winter'
    unknown = 'unknown'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DeviceClockOutOfSyncType(Enum):
    """
    Enumeration of clock sync states
    """
    synced = 'synced'
    out_of_sync_warning = 'out_of_sync_warning'
    out_of_sync_critical = 'out_of_sync_critical'
    unsynchronized = 'unsynchronized'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DownlinkTaskType(Enum):
    """
    Enumeration of task types for downlink
    """
    time_sync = 'time_sync'
    firmware_update = 'firmware_update'
    unbp_message = 'unbp_message'
    unbp_message_set_relay = 'unbp_message_set_relay'
    unbp_message_get_data = 'unbp_message_get_data'
    unbp_message_set_schedule = 'unbp_message_set_schedule'
    unbp_message_set_clock = 'unbp_message_set_clock'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class BinaryDataFileType(Enum):
    """
    Enumeration of uploaded file types for downlink, but can be used across whole application.
    Whenever you need to add functionality that requires file upload, add new type of files to this enum.
    """
    device_firmware = 'device_firmware'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class UnbpGetDataPacket(Enum):
    UNDEFINED = "UNDEFINED"
    UL_DATA_16B__ENERGY = "UL_DATA_16B__ENERGY"
    NETWORK_PARAMS_PHASE1 = "NETWORK_PARAMS_PHASE1"
    DAILY_ENERGY_ACTIVE_CONSUMED = "DAILY_ENERGY_ACTIVE_CONSUMED"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_1 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_1"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_3 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_3"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_4 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_4"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM"
    DAILY_ENERGY_REACTIVE_CONSUMED = "DAILY_ENERGY_REACTIVE_CONSUMED"
    DAILY_ENERGY_ACTIVE_GENERATED = "DAILY_ENERGY_ACTIVE_GENERATED"
    DAILY_ENERGY_REACTIVE_GENERATED = "DAILY_ENERGY_REACTIVE_GENERATED"
    MONTHLY_ENERGY_ACTIVE_CONSUMED = "MONTHLY_ENERGY_ACTIVE_CONSUMED"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_1 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_1"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_2 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_2"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_3 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_3"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_4 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_4"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM"
    MONTHLY_ENERGY_REACTIVE_CONSUMED = "MONTHLY_ENERGY_REACTIVE_CONSUMED"
    MONTHLY_ENERGY_ACTIVE_GENERATED = "MONTHLY_ENERGY_ACTIVE_GENERATED"
    MONTHLY_ENERGY_REACTIVE_GENERATED = "MONTHLY_ENERGY_REACTIVE_GENERATED"


class UnbpSetSchedulePacket(Enum):
    UL_DATA_16B__ENERGY = "UL_DATA_16B__ENERGY"
    DAILY_ENERGY_ACTIVE_CONSUMED = "DAILY_ENERGY_ACTIVE_CONSUMED"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_1 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_1"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_2"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_3 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_3"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_4 = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_4"
    DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM = "DAILY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM"
    DAILY_ENERGY_REACTIVE_CONSUMED = "DAILY_ENERGY_REACTIVE_CONSUMED"
    DAILY_ENERGY_ACTIVE_GENERATED = "DAILY_ENERGY_ACTIVE_GENERATED"
    DAILY_ENERGY_REACTIVE_GENERATED = "DAILY_ENERGY_REACTIVE_GENERATED"
    MONTHLY_ENERGY_ACTIVE_CONSUMED = "MONTHLY_ENERGY_ACTIVE_CONSUMED"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_1 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_1"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_2 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_2"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_3 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_3"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_4 = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_4"
    MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM = "MONTHLY_ENERGY_ACTIVE_CONSUMED_TARIFF_SUM"
    MONTHLY_ENERGY_REACTIVE_CONSUMED = "MONTHLY_ENERGY_REACTIVE_CONSUMED"
    MONTHLY_ENERGY_ACTIVE_GENERATED = "MONTHLY_ENERGY_ACTIVE_GENERATED"
    MONTHLY_ENERGY_REACTIVE_GENERATED = "MONTHLY_ENERGY_REACTIVE_GENERATED"


class UnbpSetScheduleAction(Enum):
    REPLACE = "REPLACE"
    ADD = "ADD"
    REPLACE_HOUR = "REPLACE_HOUR"
    REPLACE_DAY = "REPLACE_DAY"


class ScheduleType(Enum):
    """
    Enumeration of schedule types
    """
    on_capture = 'on_capture'
    schedule = 'schedule'
    asap = 'asap'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class ReglamentType(Enum):
    """
    Enumeration of regulation types
    """
    ul_pr_dl_rm_on_capture = 'ul_pr_dl_rm_on_capture'
    ul_pr_dl_rm = 'ul_pr_dl_rm'
    ul_rm_dl_rm = 'ul_rm_dl_rm'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class SignalModulation(Enum):
    """
    Enumeration of signal modulations
    """
    DBPSK = 'DBPSK'
    PSK = 'PSK'
    FSK = 'FSK'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DownlinkTaskStatus(Enum):
    """
    Enumeration of task statuses for downlink
    """
    created = 'created'
    bs_ack = 'bs_ack'
    bs_executed_succeed = 'bs_executed_succeed'
    bs_executed_failed = 'bs_executed_failed'
    bs_skipped = 'bs_skipped'
    canceled = 'canceled'
    bs_deleted = 'bs_deleted'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DeviceDownlinkTaskStatus(Enum):
    """
    Enumeration of device statuses inside task for downlink
    """
    pending = 'pending'
    fully_executed = 'fully_executed'
    partially_executed = 'partially_executed'
    failed = 'failed'

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'


class DataAggregatorApiUserType(Enum):
    """
    Enumeration of ApiUser types for DataAggregator
    """
    base_station = "base_station"
    api_user = "api_user"
    other = "other"
    USPD = "USPD"
    universal_data_input_api = "universal_data_input_api"


class DeltasMonitoringValuesMode(Enum):
    """
    Enumeration of values marker type during calculation deltas
    """
    ONLY_NORMAL = "ONLY_NORMAL"
    WITH_REJECTED = "WITH_REJECTED"
