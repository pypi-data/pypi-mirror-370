# ALIGNMENT MEMORY (CLI)

가벼운 **세션 기반 대화 로그** 저장/검색 툴입니다. 각 세션은 **12자리 hex ID**로 생성되며(JSONL 라인 저장), 검색/요약/내보내기 등을 지원합니다.

## Install

```bash
pip install -U alignment_memory
# 실행 명령: alm
alm --help

Class1.filter_events(..., tz='local'|'utc'|'+09:00') 지원

AB_TZ_OFFSET="+09:00" 환경변수로 기본 로컬 오프셋 오버라이드 가능
