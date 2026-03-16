LOG_FILE = 'mission_computer_main.log'
REPORT_FILE = 'log_analysis.md'


def hello_mars():
    print('Hello Mars')
    print()


def read_log_file(filename):
    entries = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            print(f'경고: {filename} 파일이 비어 있습니다.')
            return entries

        header = lines[0].strip().split(',')
        if len(header) < 3:
            print('경고: 로그 파일 헤더 형식이 올바르지 않습니다.')
            return entries

        for line_number, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line:
                continue
            parts = line.split(',', 2)
            if len(parts) < 3:
                print(f'경고: {line_number}번째 줄 형식 오류 - 건너뜁니다.')
                continue
            entry = {
                'timestamp': parts[0],
                'event': parts[1],
                'message': parts[2],
            }
            entries.append(entry)

    except FileNotFoundError:
        print(f'오류: {filename} 파일을 찾을 수 없습니다.')
    except PermissionError:
        print(f'오류: {filename} 파일을 읽을 권한이 없습니다.')
    except UnicodeDecodeError:
        print(f'오류: {filename} 파일의 인코딩을 읽을 수 없습니다. UTF-8인지 확인하세요.')
    except OSError as e:
        print(f'오류: 파일 읽기 중 문제가 발생했습니다 - {e}')

    return entries


def print_log(entries):
    print('=' * 70)
    print('미션 컴퓨터 로그 전체 내용')
    print('=' * 70)
    print(f'{"타임스탬프":<22} {"이벤트":<10} {"메시지"}')
    print('-' * 70)
    for entry in entries:
        print(f'{entry["timestamp"]:<22} {entry["event"]:<10} {entry["message"]}')
    print('=' * 70)
    print(f'총 로그 항목 수: {len(entries)}개')
    print()


def analysis_log(entries):
    analysis = {
        'total': len(entries),
        'info_count': 0,
        'warning_count': 0,
        'error_count': 0,
        'critical_count': 0,
        'warnings': [],
        'errors': [],
        'criticals': [],
        'first_timestamp': '',
        'last_timestamp': '',
    }

    if not entries:
        return analysis

    analysis['first_timestamp'] = entries[0]['timestamp']
    analysis['last_timestamp'] = entries[-1]['timestamp']

    for entry in entries:
        event = entry['event'].upper()
        if event == 'INFO':
            analysis['info_count'] += 1
        elif event == 'WARNING':
            analysis['warning_count'] += 1
            analysis['warnings'].append(entry)
        elif event == 'ERROR':
            analysis['error_count'] += 1
            analysis['errors'].append(entry)
        elif event == 'CRITICAL':
            analysis['critical_count'] += 1
            analysis['criticals'].append(entry)

    return analysis


def find_accident_cause(analysis):
    cause_entries = analysis['warnings'] + analysis['errors'] + analysis['criticals']
    cause_entries.sort(key=lambda x: x['timestamp'])

    accident_sequence = []
    for entry in cause_entries:
        accident_sequence.append(entry)

    first_critical = None
    if analysis['criticals']:
        first_critical = analysis['criticals'][0]

    root_cause = ''
    for entry in cause_entries:
        if 'failure' in entry['message'].lower() or 'failed' in entry['message'].lower():
            root_cause = entry
            break

    if not root_cause and analysis['errors']:
        root_cause = analysis['errors'][0]

    return {
        'sequence': accident_sequence,
        'first_critical': first_critical,
        'root_cause': root_cause,
    }


def write_report(entries, analysis, cause, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('# 미션 컴퓨터 로그 분석 보고서\n\n')
            f.write('## 1. 개요\n\n')
            f.write('화성 기지 미션 컴퓨터(Olympus Base Alpha)의 로그 파일을 분석하여 ')
            f.write('시스템 장애 및 사고의 원인을 파악한 보고서입니다.\n\n')
            f.write(f'- **분석 파일**: `{LOG_FILE}`\n')
            f.write(f'- **로그 시작 시각**: {analysis["first_timestamp"]}\n')
            f.write(f'- **로그 종료 시각**: {analysis["last_timestamp"]}\n')
            f.write(f'- **전체 로그 수**: {analysis["total"]}건\n\n')

            f.write('## 2. 로그 이벤트 통계\n\n')
            f.write('| 이벤트 등급 | 건수 |\n')
            f.write('|---|---|\n')
            f.write(f'| INFO | {analysis["info_count"]} |\n')
            f.write(f'| WARNING | {analysis["warning_count"]} |\n')
            f.write(f'| ERROR | {analysis["error_count"]} |\n')
            f.write(f'| CRITICAL | {analysis["critical_count"]} |\n\n')

            f.write('## 3. 경고(WARNING) 이벤트 목록\n\n')
            if analysis['warnings']:
                f.write('| 타임스탬프 | 메시지 |\n')
                f.write('|---|---|\n')
                for entry in analysis['warnings']:
                    f.write(f'| {entry["timestamp"]} | {entry["message"]} |\n')
            else:
                f.write('경고 이벤트가 없습니다.\n')
            f.write('\n')

            f.write('## 4. 오류(ERROR) 이벤트 목록\n\n')
            if analysis['errors']:
                f.write('| 타임스탬프 | 메시지 |\n')
                f.write('|---|---|\n')
                for entry in analysis['errors']:
                    f.write(f'| {entry["timestamp"]} | {entry["message"]} |\n')
            else:
                f.write('오류 이벤트가 없습니다.\n')
            f.write('\n')

            f.write('## 5. 심각(CRITICAL) 이벤트 목록\n\n')
            if analysis['criticals']:
                f.write('| 타임스탬프 | 메시지 |\n')
                f.write('|---|---|\n')
                for entry in analysis['criticals']:
                    f.write(f'| {entry["timestamp"]} | {entry["message"]} |\n')
            else:
                f.write('심각 이벤트가 없습니다.\n')
            f.write('\n')

            f.write('## 6. 사고 경위 (시간 순서)\n\n')
            if cause['sequence']:
                f.write('| 타임스탬프 | 등급 | 메시지 |\n')
                f.write('|---|---|---|\n')
                for entry in cause['sequence']:
                    f.write(
                        f'| {entry["timestamp"]} | {entry["event"]} | {entry["message"]} |\n'
                    )
            else:
                f.write('사고 관련 이벤트가 없습니다.\n')
            f.write('\n')

            f.write('## 7. 사고 원인 분석\n\n')
            if cause['root_cause']:
                f.write('### 근본 원인 (Root Cause)\n\n')
                f.write(f'- **발생 시각**: {cause["root_cause"]["timestamp"]}\n')
                f.write(f'- **등급**: {cause["root_cause"]["event"]}\n')
                f.write(f'- **내용**: {cause["root_cause"]["message"]}\n\n')

            if cause['first_critical']:
                f.write('### 임계 장애 발생 시점\n\n')
                f.write(f'- **발생 시각**: {cause["first_critical"]["timestamp"]}\n')
                f.write(f'- **내용**: {cause["first_critical"]["message"]}\n\n')

            f.write('### 사고 원인 요약\n\n')
            f.write(
                '사고는 단일 원인이 아닌 복합적 요인이 연쇄적으로 작용하여 발생하였습니다.\n\n'
                '**1차 원인 - 수소 연료 저장 장치 미세 균열:**\n'
                '2024-02-18부터 수소 연료 저장 장치 B동의 압력 센서 이상이 감지되었습니다. '
                '당시 재교정 후 정상 범위로 복귀하였으나, 이틀 뒤인 2024-02-19에 미세 균열로 인한 '
                '수소 누출이 확인되었습니다. 긴급 환기 후 수리가 진행되었으나 '
                '누출 경로가 완전히 제거되지 않았을 가능성이 있습니다.\n\n'
                '**2차 원인 - 냉각 펌프 씰 파열:**\n'
                '2024-01-10부터 냉각 펌프 압력 이상 징후가 반복적으로 감지되었으며 임시 수리만 시행되었습니다. '
                '2024-02-20 냉각 펌프 씰이 최종 파열되어 냉각재가 섹터 7로 누출되었고, '
                '이로 인해 원자로 노심 온도가 임계값(450°C)을 초과하여 자동 긴급 정지(SCRAM)가 발동되었습니다.\n\n'
                '**직접 폭발 원인 - 수소 점화:**\n'
                '원자로 SCRAM 이후 기지 전력이 차단되면서 환기 시스템이 일시 정지되었고, '
                '섹터 7에 잔류하던 수소 가스 농도가 폭발 하한계(4.0%)를 초과하였습니다. '
                '원자로 과열 또는 전기 스파크로 인한 점화가 발생하여 '
                '2024-02-20 11:36:50 섹터 7에서 폭발이 일어났습니다. '
                '이 폭발로 거주 모듈의 구조적 손상과 기압 손실이 발생하였으며, '
                '통신 시스템과 다수 센서가 오프라인 상태가 되었습니다.\n\n'
            )

            f.write('## 8. 결론 및 재발 방지 대책\n\n')
            f.write('1. **수소 저장 장치 정기 정밀 검사**: 압력 센서 이상 감지 시 즉각 전면 검사를 실시하고 임시 조치 없이 완전 교체한다.\n')
            f.write('2. **냉각 펌프 씰 예방 교체 주기 단축**: 임시 수리 후 반드시 일정 기간 내 영구 부품 교체를 이행한다.\n')
            f.write('3. **독립적 환기 비상 전원 확보**: 주전력 차단 시에도 수소 위험 구역의 환기가 자동 유지되도록 독립 비상 전원을 구성한다.\n')
            f.write('4. **복합 위험 인터록 시스템 도입**: 냉각 이상 + 수소 농도 상승이 동시에 감지될 경우 자동으로 해당 구역을 격리하는 인터록을 추가한다.\n')
            f.write('5. **수소 농도 모니터링 강화**: 폭발 하한계(4.0%)의 25% 수준(1.0%)에서 즉각 경보 및 강제 환기가 발동되도록 임계값을 재설정한다.\n\n')

            f.write('---\n')
            f.write('*본 보고서는 mission_computer_main.log 파일을 Python으로 자동 분석하여 생성되었습니다.*\n')

        print(f'보고서가 성공적으로 작성되었습니다: {filename}')

    except PermissionError:
        print(f'오류: {filename} 파일에 쓸 권한이 없습니다.')
    except OSError as e:
        print(f'오류: 보고서 작성 중 문제가 발생했습니다 - {e}')


def main():
    hello_mars()
    print('미션 컴퓨터 로그 분석 프로그램을 시작합니다.')
    print()

    entries = read_log_file(LOG_FILE)
    if not entries:
        print('로그 데이터를 불러오지 못했습니다. 프로그램을 종료합니다.')
        return

    print_log(entries)

    analysis = analyze_log(entries)
    cause = find_accident_cause(analysis)

    print('사고 분석 결과 요약:')
    print(f'  - 전체 로그 수    : {analysis["total"]}건')
    print(f'  - INFO 이벤트    : {analysis["info_count"]}건')
    print(f'  - WARNING 이벤트 : {analysis["warning_count"]}건')
    print(f'  - ERROR 이벤트   : {analysis["error_count"]}건')
    print(f'  - CRITICAL 이벤트: {analysis["critical_count"]}건')
    print()

    if cause['root_cause']:
        print('사고 근본 원인:')
        print(f'  [{cause["root_cause"]["timestamp"]}] {cause["root_cause"]["message"]}')
        print()

    write_report(entries, analysis, cause, REPORT_FILE)


if __name__ == '__main__':
    main()
