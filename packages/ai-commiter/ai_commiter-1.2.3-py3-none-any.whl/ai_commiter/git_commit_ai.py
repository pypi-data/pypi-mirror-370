#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import git
import argparse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import re
from collections import defaultdict
from pathlib import Path
from ai_commiter import __version__
from ai_commiter.config import (
    load_config, get_config_value, set_config_value, 
    unset_config_value, list_config
)

# Language pack definitions with locale support
LANGUAGE_PACKS = {
    'ko': {
        'name': 'Korean (한국어)',
        'locale': 'ko-KR',
        'response_instruction': 'Please respond in Korean. The commit message title must be in English (imperative mood), but the detailed description must be written in Korean. 제목은 영어로, 상세 설명은 반드시 한국어로 작성해주세요.'
    },
    'ko-KR': {
        'name': 'Korean (한국어)',
        'locale': 'ko-KR', 
        'response_instruction': 'Please respond in Korean. The commit message title must be in English (imperative mood), but the detailed description must be written in Korean. 제목은 영어로, 상세 설명은 반드시 한국어로 작성해주세요.'
    },
    'en': {
        'name': 'English',
        'locale': 'en-US',
        'response_instruction': 'Please respond in English. Use imperative mood for the title and provide detailed description in English.'
    },
    'en-US': {
        'name': 'English (US)',
        'locale': 'en-US',
        'response_instruction': 'Please respond in English. Use imperative mood for the title and provide detailed description in English.'
    },
    'en-GB': {
        'name': 'English (UK)',
        'locale': 'en-GB',
        'response_instruction': 'Please respond in British English. Use imperative mood for the title and provide detailed description in British English.'
    },
    'ja': {
        'name': 'Japanese (日本語)',
        'locale': 'ja-JP',
        'response_instruction': 'Please respond in Japanese. The title should be in English (imperative mood), but the detailed description should be in Japanese. タイトルは英語で、詳細説明は日本語で記述してください。'
    },
    'ja-JP': {
        'name': 'Japanese (日本語)',
        'locale': 'ja-JP',
        'response_instruction': 'Please respond in Japanese. The title should be in English (imperative mood), but the detailed description should be in Japanese. タイトルは英語で、詳細説明は日本語で記述してください。'
    },
    'zh': {
        'name': 'Chinese Simplified (简体中文)',
        'locale': 'zh-CN',
        'response_instruction': 'Please respond in Simplified Chinese. The title should be in English (imperative mood), but the detailed description should be in Simplified Chinese. 标题用英语，详细说明请用简体中文。'
    },
    'zh-CN': {
        'name': 'Chinese Simplified (简体中文)',
        'locale': 'zh-CN',
        'response_instruction': 'Please respond in Simplified Chinese. The title should be in English (imperative mood), but the detailed description should be in Simplified Chinese. 标题用英语，详细说明请用简体中文。'
    },
    'zh-TW': {
        'name': 'Chinese Traditional (繁體中文)',
        'locale': 'zh-TW',
        'response_instruction': 'Please respond in Traditional Chinese. The title should be in English (imperative mood), but the detailed description should be in Traditional Chinese. 標題用英語，詳細說明請用繁體中文。'
    }
}

COMMIT_PROMPT_TEMPLATE = '''Analyze the following Git repository changes carefully. Look at the specific lines added (+) and removed (-) in the diff to understand exactly what changed. Please read the given {language_instruction} and create an appropriate Git commit message based on it.

IMPORTANT: Be specific about what was actually changed. Avoid generic phrases like "update file" or "meaningful changes". Instead, describe the concrete changes you see in the diff.

The commit message consists of header and body:
1. header
- Format: 'type: specific description of what changed'
- Be concrete and specific (within 50 characters)
- Examples: "Add multi-language support", "Remove redundant validation", "Fix null pointer exception"

2. body  
- MANDATORY: Leave ONE EMPTY LINE between header and body
- Explain WHAT was changed and WHY (within 72 characters per line)
- Keep it CONCISE and focused (maximum 3-4 lines)
- Group related changes into single points, avoid listing every detail
- Focus on the main purpose and impact, not individual file changes
- MANDATORY: Start each line with a dash (-)
- MANDATORY: Put each sentence on a separate line
- MANDATORY: Do NOT end sentences with periods (.)
- Example format:
  feat: Add multi-language support
  
  - Main change or feature that was implemented
  - Key reason or benefit for this change
  - Important technical detail (if needed)

Select the most appropriate type (even if there are multiple changes, select only the most important change type):
feat: Add new feature or functionality
fix: Fix bug or error
docs: Change documentation, comments, or text content (including prompts)
style: Change code formatting, whitespace, semicolons (NOT content changes)
refactor: Restructure code without changing functionality
test: Add or modify test code
chore: Change build process, dependencies, or auxiliary tools

Change statistics:
- Total {total_files} files changed
- {added_lines} lines added, {removed_lines} lines deleted

{categorized_files}

Changes (diff):
{diff}

{language_instruction}

Output only the commit message:'''

def get_language_instruction(lang):
    """Get language-specific response instruction."""
    return LANGUAGE_PACKS.get(lang, LANGUAGE_PACKS['ko'])['response_instruction']


def get_git_diff(repo_path='.', staged=True, exclude_files=None):
    """
    Git 저장소에서 변경 내용을 가져옵니다.
    
    Args:
        repo_path (str): Git 저장소 경로
        staged (bool): 스테이지된 변경사항만 포함할지 여부
        exclude_files (list): 제외할 파일 목록
    
    Returns:
        str: Git diff 출력
    """
    try:
        repo = git.Repo(repo_path)
        if staged:
            # 스테이지된 변경사항
            diff = repo.git.diff('--staged')
        else:
            # 모든 변경사항
            diff = repo.git.diff()
        
        # 제외할 파일이 있는 경우 필터링
        if exclude_files:
            diff_lines = diff.split('\n')
            filtered_lines = []
            skip_file = False
            
            for line in diff_lines:
                # diff 파일 헤더 확인
                if line.startswith('diff --git'):
                    # 파일 경로 추출 (a/path/to/file b/path/to/file 형태)
                    parts = line.split()
                    if len(parts) >= 4:
                        file_path = parts[2][2:]  # a/ 제거
                        skip_file = any(file_path == exclude_file or file_path.endswith('/' + exclude_file) 
                                      for exclude_file in exclude_files)
                
                if not skip_file:
                    filtered_lines.append(line)
            
            diff = '\n'.join(filtered_lines)
        
        return diff
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        sys.exit(1)
    except Exception as e:
        print(f"Git diff error: {str(e)}")
        return diff

def get_changed_files(repo_path='.', staged=True, exclude_files=None):
    """
    변경된 파일 목록을 가져옵니다.
    
    Args:
        repo_path (str): Git 저장소 경로
        staged (bool): True면 스테이지된 변경사항, False면 모든 변경사항
        exclude_files (list): 제외할 파일 목록
    
    Returns:
        list: 변경된 파일 목록
    """
    try:
        repo = git.Repo(repo_path)
        
        if staged:
            # 스테이지된 변경사항만 가져오기
            changed_files = repo.git.diff('--cached', '--name-only').split('\n')
        else:
            # 모든 변경사항 가져오기
            changed_files = repo.git.diff('--name-only').split('\n')
        
        # 빈 문자열 제거
        changed_files = [f for f in changed_files if f]
        
        # 제외할 파일이 있는 경우 필터링
        if exclude_files:
            changed_files = [f for f in changed_files 
                           if not any(f == exclude_file or f.endswith('/' + exclude_file) 
                                    for exclude_file in exclude_files)]
        
        return changed_files
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting changed files: {str(e)}")
        sys.exit(1)

def categorize_file_changes(changed_files, diff):
    """
    변경된 파일들을 카테고리별로 분류합니다.
    
    Args:
        changed_files (list): 변경된 파일 목록
        diff (str): Git diff 내용
    
    Returns:
        dict: 카테고리별로 분류된 파일 변경 정보
    """
    categories = {
        'frontend': [],
        'backend': [],
        'config': [],
        'docs': [],
        'tests': [],
        'assets': [],
        'other': []
    }
    
    # 파일 확장자 및 경로 기반 분류
    file_patterns = {
        'frontend': ['.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte', '.scss', '.sass', '.less'],
        'backend': ['.py', '.java', '.go', '.rs', '.cpp', '.c', '.php', '.rb', '.cs', '.kt', '.scala'],
        'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.config', 'Dockerfile', 'docker-compose', '.env'],
        'docs': ['.md', '.rst', '.txt', '.doc', '.docx', '.pdf'],
        'tests': ['test_', '_test.', '.test.', 'spec_', '_spec.', '.spec.'],
        'assets': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot']
    }
    
    # 변경 유형 분석 (추가, 수정, 삭제)
    change_types = defaultdict(list)
    
    for file_path in changed_files:
        categorized = False
        file_lower = file_path.lower()
        
        # 테스트 파일 우선 확인
        for test_pattern in file_patterns['tests']:
            if test_pattern in file_lower:
                categories['tests'].append(file_path)
                categorized = True
                break
        
        if not categorized:
            # 다른 카테고리 확인
            for category, patterns in file_patterns.items():
                if category == 'tests':  # 이미 확인했으므로 스킵
                    continue
                    
                for pattern in patterns:
                    if file_lower.endswith(pattern) or pattern in file_lower:
                        categories[category].append(file_path)
                        categorized = True
                        break
                
                if categorized:
                    break
        
        if not categorized:
            categories['other'].append(file_path)
    
    # diff에서 변경 유형 분석
    diff_lines = diff.split('\n')
    added_lines = len([line for line in diff_lines if line.startswith('+') and not line.startswith('+++')])
    removed_lines = len([line for line in diff_lines if line.startswith('-') and not line.startswith('---')])
    
    # 새 파일과 삭제된 파일 감지
    file_status = {}
    new_files = []
    deleted_files = []
    for line in diff_lines:
        if line.startswith('diff --git'):
            parts = line.split(' ')
            if len(parts) >= 3:
                file_path = parts[2][2:]  # remove 'a/'
                file_status[file_path] = 'modified'
        elif line.startswith('new file mode'):
            new_files.append(file_path)
            file_status[file_path] = 'added'
        elif line.startswith('deleted file mode'):
            deleted_files.append(file_path)
            file_status[file_path] = 'deleted'
    
    # 분류 정보 구성
    result = {
        'categories': {},
        'stats': {
            'total_files': len(changed_files),
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'new_files': len(new_files),
            'deleted_files': len(deleted_files)
        }
    }
    
    # 각 카테고리에 파일이 있는 경우만 결과에 포함
    for category, files in categories.items():
        if files:
            result['categories'][category] = files
    
    return result

def calculate_complexity_score(diff, files):
    """
    변경 내용의 복잡도를 계산합니다.
    
    Args:
        diff (str): Git diff 내용
        files (list): 변경된 파일 목록
    
    Returns:
        tuple: (복잡도 점수, 점수 세부 사항)
    """
    # 복잡도 점수 초기화
    complexity_score = 0
    score_details = []
    
    # 파일 수에 따른 복잡도 평가
    num_files = len(files)
    if num_files >= 10:
        complexity_score += 4
        score_details.append(f"{num_files} files (+4)")
    elif num_files >= 5:
        complexity_score += 2
        score_details.append(f"{num_files} files (+2)")
    elif num_files > 1:
        complexity_score += 1
        score_details.append(f"{num_files} files (+1)")
    else:
        score_details.append(f"{num_files} files (+0)")
    
    # diff 크기에 따른 복잡도 평가
    diff_lines = len(diff.split('\n'))
    if diff_lines > 1000:
        complexity_score += 4
        score_details.append(f"{diff_lines} diff lines (+4)")
    elif diff_lines > 500:
        complexity_score += 2
        score_details.append(f"{diff_lines} diff lines (+2)")
    elif diff_lines > 100:
        complexity_score += 1
        score_details.append(f"{diff_lines} diff lines (+1)")
    else:
        score_details.append(f"{diff_lines} diff lines (+0)")
        
    return complexity_score, score_details

def select_model_by_complexity(complexity_score):
    """
    복잡도 점수를 기반으로 최적의 AI 모델을 선택합니다.
    
    Args:
        complexity_score (int): 계산된 복잡도 점수
    
    Returns:
        tuple: (선택된 모델명, 선택 이유)
    """
    # 점수에 따른 모델 선택 (속도와 성능 균형 고려)
    if complexity_score >= 5:
        selected_model = "gpt-5"
        reason = "복잡한 변경사항 (최고 성능)"
    elif complexity_score >= 2:
        selected_model = "gpt-5-mini"
        reason = "중간 복잡도 변경사항 (균형적 성능)"
    else:
        selected_model = "gpt-4o-mini"
        reason = "간단한 변경사항 (빠르고 안정적)"
    
    return selected_model, reason

def generate_commit_message(diff, files, prompt_template=None, openai_model="gpt-4o-mini", enable_categorization=True, lang='ko', complexity_score=0):
    """
    변경 내용을 기반으로 커밋 메시지를 생성합니다.
    
    Args:
        diff (str): Git diff 내용
        files (list): 변경된 파일 목록
        prompt_template (str, optional): 커스텀 프롬프트 템플릿
        openai_model (str, optional): 사용할 OpenAI 모델
        enable_categorization (bool, optional): 파일 분류 기능 사용 여부
        lang (str, optional): 응답 언어 코드
    
    Returns:
        tuple: (생성된 커밋 메시지, 토큰 사용량 정보)
    """
    # API 키 확인
    # AI_COMMITER_API_KEY를 우선 확인하고, 없으면 OPENAI_API_KEY 확인
    api_key = os.getenv("AI_COMMITER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is not set.")
        print("Please set AI_COMMITER_API_KEY or OPENAI_API_KEY environment variable.")
        print("Example: export AI_COMMITER_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # OPENAI_API_KEY 환경 변수가 없는 경우, 임시로 설정 (라이브러리가 확인하는 변수명)
    if not os.getenv("OPENAI_API_KEY") and api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # 파일 변경 내용 분류 (여러 파일이 변경된 경우)
    change_summary = None
    if enable_categorization:
        change_summary = categorize_file_changes(files, diff)
    
    # 기본 프롬프트 템플릿 설정 (새로운 언어팩 시스템 사용)
    if prompt_template is None:
        prompt_template = COMMIT_PROMPT_TEMPLATE
    
    # 프롬프트 변수 준비
    prompt_vars = {
        "diff": diff,
        "language_instruction": get_language_instruction(lang)
    }

    # 카테고리 정보가 있는 경우 추가 변수 설정
    if change_summary:
        stats = change_summary['stats']
        # 카테고리별 파일 목록 영어로 포맷팅
        categorized_files_str = "\n".join([
            f"- {category.title()}: {', '.join(files)}" 
            for category, files in change_summary['categories'].items() if files
        ])
        
        prompt_vars.update({
            "total_files": stats['total_files'],
            "added_lines": stats['added_lines'],
            "removed_lines": stats['removed_lines'],
            "categorized_files": categorized_files_str if categorized_files_str else "No categorized files"
        })
        
        # 카테고리별 프롬프트용 변수명 설정
        input_variables = ["diff", "total_files", "added_lines", "removed_lines", 
                          "categorized_files", "language_instruction"]
    else:
        # 분류 정보가 없는 경우 기본값 설정
        prompt_vars.update({
            "total_files": len(files),
            "added_lines": "Unknown",
            "removed_lines": "Unknown",
            "categorized_files": "No categorization"
        })
        input_variables = ["diff", "total_files", "added_lines", "removed_lines", 
                          "categorized_files", "language_instruction"]
    
    # LangChain 설정 (토큰 사용량 추적을 위해 callbacks 활용)
    # GPT-5 시리즈는 temperature 제약이 있을 수 있음
    if 'gpt-5' in openai_model.lower():
        llm = ChatOpenAI(model_name=openai_model)  # GPT-5는 기본값 사용
    else:
        llm = ChatOpenAI(temperature=0.5, model_name=openai_model)  # 이전 모델은 0.5 사용
    chain_prompt = PromptTemplate(input_variables=input_variables, template=prompt_template)
    chain = chain_prompt | llm
    
    # 항상 전체 diff 사용 (복잡도에 따른 제한 없음)
    
    # 커밋 메시지 생성 및 토큰 사용량 추적
    try:
        result = chain.invoke(prompt_vars)
        # AIMessage 객체에서 content 속성 추출
        commit_message = result.content if hasattr(result, 'content') else str(result)
        
        # 토큰 사용량 정보 추출 (response_metadata에서)
        token_usage = None
        if hasattr(result, 'response_metadata') and 'token_usage' in result.response_metadata:
            token_usage = result.response_metadata['token_usage']
        elif hasattr(result, 'usage_metadata'):
            # 새로운 LangChain 버전의 경우
            token_usage = result.usage_metadata
        
        return commit_message.strip(), token_usage
        
    except Exception as e:
        print(f"Error generating commit message: {e}")
        return None, None

def make_commit(repo_path='.', message=None):
    """
    생성된 메시지로 커밋을 수행합니다.
    
    Args:
        repo_path (str): Git 저장소 경로
        message (str): 커밋 메시지
        
    Returns:
        bool: 커밋 성공 여부
    """
    if message is None:
        print("No commit message provided.")
        return False
        
    try:
        repo = git.Repo(repo_path)
        repo.git.commit('-m', message)
        print("✅ Commit successful!")
        return True
    except Exception as e:
        print(f"❌ Commit failed: {str(e)}")
        return False


def split_and_commit_changes(repo_path='.', changed_files=None, diff=None, custom_prompt=None, model="gpt-4o-mini", lang='ko', exclude_files=None):
    """
    변경사항을 카테고리별로 분할하여 순차적으로 커밋합니다.
    
    Args:
        repo_path (str): Git 저장소 경로
        changed_files (list): 변경된 파일 목록
        diff (str): 전체 Git diff 내용
        custom_prompt (str, optional): 커스텀 프롬프트 템플릿
        model (str): 사용할 OpenAI 모델
        lang (str): 커밋 메시지 언어
        exclude_files (list): 제외할 파일 목록
    
    Returns:
        bool: 모든 커밋 성공 여부
    """
    if not changed_files or not diff:
        print("No files to commit.")
        return False
    
    # 스킵된 파일들을 추적하기 위한 집합 초기화
    skipped_files = set()
    
    repo = git.Repo(repo_path)
    
    # 현재 스테이징된 모든 파일 목록 저장
    staged_files = changed_files.copy()
    
    # 스테이징 영역 초기화
    try:
        repo.git.reset()
    except Exception as e:
        print(f"Failed to reset staging area: {str(e)}")
        return False
    
    # 파일을 카테고리별로 분류
    change_summary = categorize_file_changes(changed_files, diff)
    categories = change_summary['categories']
    
    # 카테고리가 없는 경우 모든 파일을 하나의 커밋으로 처리
    if not categories:
        try:
            for file in staged_files:
                repo.git.add(file)
            
            commit_diff = get_git_diff(repo_path, staged=True, exclude_files=exclude_files)
            result = generate_commit_message(commit_diff, staged_files, custom_prompt, model, 
                                         enable_categorization=True, lang=lang)
            
            if result[0] is None:
                print("❌ Failed to generate commit message")
                return False
            
            commit_message, _ = result
            print(f"📝 Generated message:\n{commit_message}\n")
            
            # 사용자에게 커밋 여부 확인
            confirm = input(f"Proceed with this commit? (y/n): ").strip().lower()
            
            if confirm == 'y':
                return make_commit(repo_path, commit_message)
            else:
                print(f"⏭️ Commit skipped")
                return False
        except Exception as e:
            print(f"❌ Commit failed: {str(e)}")
            return False
    
    # 카테고리별로 순차적으로 커밋
    successful_commits = 0
    total_categories = len(categories)
    
    print(f"\n🔄 Auto-splitting changes into {total_categories} logical commits...\n")
    
    for idx, (category, files) in enumerate(categories.items()):
        try:
            # 현재 카테고리의 파일들만 스테이징 (-A 옵션으로 파일 이동/이름변경 전환 유지)
            for file in files:
                repo.git.add('-A', file)
            
            # 현재 스테이지된 파일들의 diff 가져오기
            commit_diff = get_git_diff(repo_path, staged=True, exclude_files=exclude_files)
            
            # 각 카테고리별 변경사항에 맞는 복잡도 계산 및 모델 선택
            category_complexity_score, score_details = calculate_complexity_score(commit_diff, files)
            category_model, model_reason = select_model_by_complexity(category_complexity_score)
            
            # 커밋 메시지 생성
            print(f"COMMIT {idx+1}/{total_categories} - {category.title()} changes:")
            print(f" - Modified: {', '.join(files)}")
            print(f" - Complexity: {category_complexity_score} ({', '.join(score_details)})")
            print(f" - Using {category_model} model: {model_reason}")
            
            result = generate_commit_message(commit_diff, files, custom_prompt, category_model, 
                                         enable_categorization=True, lang=lang)
            
            if result[0] is None:
                print("❌ Failed to generate commit message for this category")
                continue
            
            commit_message, _ = result
            print(f"📝 Generated message:\n{commit_message}\n")
            
            # 사용자에게 커밋 여부 확인
            confirm = input(f"Proceed with this commit {idx+1}/{total_categories} ({category.title()})? (y/n): ").strip().lower()
            
            if confirm == 'y':
                # 커밋 실행
                if make_commit(repo_path, commit_message):
                    successful_commits += 1
                    print(f"✅ Created commit {idx+1}/{total_categories}\n")
                else:
                    print(f"❌ Failed to create commit {idx+1}/{total_categories}\n")
            else:
                # 해당 카테고리의 파일들을 스테이징에서 해제하고 스킵된 파일 목록에 추가
                for file in files:
                    try:
                        repo.git.reset('HEAD', file)
                        # 스킵된 파일 추적
                        skipped_files.add(file)
                    except Exception as reset_error:
                        print(f"Warning: Could not unstage {file}: {str(reset_error)}")
                print(f"⏭️ Skipped commit {idx+1}/{total_categories}\n")
        except Exception as e:
            print(f"❌ Error in commit {idx+1}/{total_categories}: {str(e)}\n")
    
    # 스킵된 파일들을 다시 스테이징
    if skipped_files:
        print("\n🔄 Restoring skipped files to staging area...")
        for file in skipped_files:
            try:
                repo.git.add('-A', file)
                print(f"✅ Restored: {file}")
            except Exception as e:
                print(f"❌ Failed to restore {file}: {str(e)}")
    
    # 결과 요약
    if successful_commits == total_categories:
        print(f"🎉 Successfully created {successful_commits} logical commits!")
        return True
    else:
        print(f"⚠️ Created {successful_commits}/{total_categories} commits with some errors.")
        return successful_commits > 0

def main():
    # .env 파일 로드
    load_dotenv()
    
    # 최상위 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='AI-powered Git commit message generator with multi-language support')
    parser.add_argument('-v', '--version', action='version', version=f'ai-commiter {__version__}', help='Show version information')
    
    # 서브커맨드 설정
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # commit 서브커맨드 설정
    commit_parser = subparsers.add_parser('commit', help='Generate AI commit message')
    commit_parser.add_argument('-r', '--repo', default='.', help='Git repository path (default: current directory)')
    commit_parser.add_argument('-a', '--all', action='store_false', dest='staged', 
                        help='Include all changes instead of staged changes only')
    commit_parser.add_argument('-m', '--model', help='Manually specify OpenAI model to use (applies to all commits in auto-split mode)')
    commit_parser.add_argument('-c', '--commit', action='store_true', help='Automatically perform commit with generated message')
    commit_parser.add_argument('-p', '--prompt', help='Path to custom prompt template file')
    commit_parser.add_argument('-l', '--lang', 
                        choices=['ko', 'ko-KR', 'en', 'en-US', 'en-GB', 'ja', 'ja-JP', 'zh', 'zh-CN', 'zh-TW'], 
                        default='ko',
                        help='Commit message language (ko/ko-KR: Korean, en/en-US/en-GB: English, ja/ja-JP: Japanese, zh/zh-CN: Chinese Simplified, zh-TW: Chinese Traditional)')
    commit_parser.add_argument('-s', '--split', action='store_true', 
                        help='Enable automatic commit splitting for complex changes')
    commit_parser.add_argument('-e', '--exclude', action='append', metavar='FILE',
                        help='Exclude specific files from commit message generation (can be used multiple times)')
    
    # config 서브커맨드 설정 (git config 스타일)
    config_parser = subparsers.add_parser('config', help='Get and set repository or global options')
    
    # config 플래그들
    config_parser.add_argument('-l', '--list', action='store_true', help='List all configuration settings')
    config_parser.add_argument('--local', action='store_true', help='Use repository config file (default)')
    config_parser.add_argument('--global', action='store_true', dest='global_config', help='Use global config file')
    config_parser.add_argument('--unset', action='store_true', help='Remove a configuration setting')
    
    # config 인자들 (git config 스타일: key [value])
    config_parser.add_argument('key', nargs='?', help='Configuration key (e.g., core.lang)')
    config_parser.add_argument('value', nargs='?', help='Configuration value to set')
    
    # 최상위 레벨에서는 서브커맨드만 허용
    
    args = parser.parse_args()
    
    # 서브커맨드가 없는 경우 처리
    if args.command is None:
        print("Error: Missing required subcommand. See usage below.")
        print("\nFor commit message generation, use: grit commit [options]")
        parser.print_help()
        sys.exit(1)
    
    # 서브커맨드에 따른 처리
    if args.command == 'config':
        # config 명령어 처리 (git config 스타일)
        use_global = getattr(args, 'global_config', False)
        
        if args.list:
            # --list 또는 -l 플래그
            list_config(use_global if use_global else None)
        elif args.unset:
            # --unset 플래그
            if not args.key:
                print("Error: --unset requires a key")
                sys.exit(1)
            if not unset_config_value(args.key, use_global):
                sys.exit(1)
        elif args.key and args.value:
            # key value 형식: 설정
            if not set_config_value(args.key, args.value, use_global):
                sys.exit(1)
        elif args.key:
            # key만 있는 경우: 조회
            value = get_config_value(args.key, use_global if use_global else None)
            if value is not None:
                print(value)
            else:
                print(f"Configuration key '{args.key}' not found")
                sys.exit(1)
        else:
            # 인자가 없는 경우
            print("Error: Missing configuration key or --list option")
            config_parser.print_help()
            sys.exit(1)
    
    elif args.command == 'commit':
        # config 파일에서 기본값 로드 (글로벌 + 로컬 병합)
        from ai_commiter.config import load_merged_config
        config = load_merged_config()
        core_config = config.get('core', {})
        
        # 명령줄 인자가 없는 경우 config 값 사용
        if not hasattr(args, 'lang') or args.lang == 'ko':  # 기본값인 경우
            args.lang = core_config.get('lang', args.lang)
        if not args.model:
            args.model = core_config.get('model')
        if not args.commit and core_config.get('commit') == 'true':
            args.commit = True
        if not args.split and core_config.get('split') == 'true':
            args.split = True
        if not args.prompt:
            args.prompt = core_config.get('prompt')
        
        # 커스텀 프롬프트 템플릿 로드
        custom_prompt = None
        if args.prompt:
            try:
                with open(args.prompt, 'r', encoding='utf-8') as f:
                    custom_prompt = f.read()
            except Exception as e:
                print(f"Prompt file load error: {str(e)}")
                sys.exit(1)
        
        # Git diff 가져오기
        try:
            diff = get_git_diff(args.repo, staged=args.staged, exclude_files=args.exclude)
            changed_files = get_changed_files(args.repo, staged=args.staged, exclude_files=args.exclude)
        except Exception as e:
            print(f"Git diff error: {str(e)}")
            sys.exit(1)
        
        # 변경사항이 없는 경우
        if not diff.strip():
            print("No changes found.")
            sys.exit(0)
    
        # 모델 선택 및 복잡도 분석
        complexity_score = 0  # 기본값
        if args.model:
            # 수동으로 모델 지정된 경우
            selected_model = args.model
            print(f"🎯 Manual selection: Using {selected_model} model")
        else:
            # 자동 모델 선택 (기본값)
            complexity_score, score_details = calculate_complexity_score(diff, changed_files)
            selected_model, model_reason = select_model_by_complexity(complexity_score)
            reason_en = "Complex changes" if "복잡한" in model_reason else "Simple changes"
            print(f"🧠 Complexity analysis: {reason_en} (score: {complexity_score})")
            print(f"   • {', '.join(score_details)}")
            print(f"   → Selected {selected_model} model")
        
        # 파일 분류 정보 출력 (여러 파일 변경 시)
        if len(changed_files) > 1:
            change_summary = categorize_file_changes(changed_files, diff)
            print(f"\n📊 Change statistics: {change_summary['stats']['total_files']} files, "
                  f"+{change_summary['stats']['added_lines']}/-{change_summary['stats']['removed_lines']} lines")
            
            if change_summary['categories']:
                print("📁 Changes by category:")
                for category, files in change_summary['categories'].items():
                    print(f"  - {category.title()}: {', '.join(files)}")
        
        # 복잡도에 따른 커밋 처리 분기
        should_split = complexity_score >= 5 and args.split and len(changed_files) >= 1
        
        if should_split and args.commit:
            print("\n🤔 This is a complex change with multiple files.")
            print("What would you like to do?")
            print("1. Create a single commit")
            print("2. Auto-split into multiple logical commits by category")
            print("3. Cancel")
            
            choice = input("\nEnter your choice (1/2/3): ")
            
            if choice == '2':
                # 자동 분할 커밋 진행
                user_specified_model = args.model is not None
                split_and_commit_changes(args.repo, changed_files, diff, custom_prompt, selected_model, args.lang, args.exclude)
                return  # 분할 커밋 완료 후 종료
            elif choice == '3':
                print("\nCommit cancelled.")
                return  # 취소 시 종료
            # choice == '1'은 아래 코드 계속 실행하여 단일 커밋 진행
        
        # 단일 커밋 메시지 생성
        print("🤖 AI is generating commit message...")
        result = generate_commit_message(diff, changed_files, custom_prompt, selected_model, 
                                       enable_categorization=True, lang=args.lang, 
                                       complexity_score=complexity_score)
        
        if result[0] is None:
            print("❌ Failed to generate commit message")
            sys.exit(1)
        
        commit_message, token_usage = result
        
        print("\n📝 Generated commit message:")
        print("-" * 50)
        print(commit_message)
        print("-" * 50)
        
        # 토큰 사용량 출력
        if token_usage:
            print("\n📊 Token usage:")
            if isinstance(token_usage, dict):
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                total_tokens = token_usage.get('total_tokens', input_tokens + output_tokens)
                print(f"   • Input tokens: {input_tokens:,}")
                print(f"   • Output tokens: {output_tokens:,}")
                print(f"   • Total tokens: {total_tokens:,}")
            else:
                print(f"   • Token usage info: {token_usage}")
        
        # 복잡한 변경사항 알림 (아직 처리되지 않은 경우)
        if should_split and not args.commit:
            print("\n🤔 This is a complex change with multiple files.")
            print("Recommendation: Consider splitting these changes into multiple logical commits.")
            print("To do this, run with 'grit commit --commit --auto-split' flags.")
            print("\nOr run the following command for a single commit:")
            print(f"git commit -m \"{commit_message}\"")
        else:
            # 일반적인 커밋 처리 (복잡도가 낮거나 자동 분할이 비활성화된 경우)
            if args.commit:
                confirm = input("\nDo you want to commit with this message? (y/n): ")
                if confirm.lower() == 'y':
                    make_commit(args.repo, commit_message)
            else:
                print("\nTo commit, run the following command:")
                print(f"git commit -m \"{commit_message}\"")
    else:
        # 알 수 없는 서브커맨드
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)

def cli():
    """패키지의 명령줄 진입점"""
    main()


if __name__ == "__main__":
    main()
