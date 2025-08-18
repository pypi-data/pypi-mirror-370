#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import os
from pathlib import Path


def get_config_path(use_global=False):
    """설정 파일 경로를 반환합니다."""
    if use_global:
        # 글로벌 설정: ~/.grit/config
        return Path.home() / '.grit' / 'config'
    else:
        # 로컬 설정: 현재 디렉토리의 .grit/config
        return Path.cwd() / '.grit' / 'config'


def load_config(use_global=False):
    """Load configuration from file."""
    config_path = get_config_path(use_global)
    config = configparser.ConfigParser()
    
    if not config_path.exists():
        return {}
    
    try:
        config.read(config_path)
        # ConfigParser를 딕셔너리로 변환
        result = {}
        for section_name in config.sections():
            result[section_name] = dict(config[section_name])
        return result
    except Exception as e:
        print(f"Error reading config file: {e}")
        return {}


def load_merged_config():
    """글로벌과 로컬 설정을 병합하여 로드합니다. 로컬이 우선순위를 가집니다."""
    global_config = load_config(use_global=True)
    local_config = load_config(use_global=False)
    
    # 글로벌 설정을 기본으로 하고 로컬 설정으로 덮어씁니다
    merged = global_config.copy()
    for section, values in local_config.items():
        if section in merged:
            merged[section].update(values)
        else:
            merged[section] = values
    
    return merged


def save_config(config_dict, use_global=False):
    """Save configuration to file."""
    config_path = get_config_path(use_global)
    config = configparser.ConfigParser()
    
    # 중첩 딕셔너리를 섹션별로 저장
    for section_name, section_data in config_dict.items():
        config[section_name] = section_data
    
    # 디렉토리가 없으면 생성
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(config_path, 'w') as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"Error saving config file: {e}")
        return False


def get_config_value(key, use_global=None):
    """Get a configuration value."""
    if use_global is None:
        # 글로벌과 로컬을 병합하여 조회 (로컬 우선)
        config = load_merged_config()
    else:
        config = load_config(use_global)
    
    # section.key 형태로 접근
    if '.' in key:
        section, config_key = key.split('.', 1)
        return config.get(section, {}).get(config_key)
    else:
        # 하위 호환성: core 섹션에서 찾기
        return config.get('core', {}).get(key)


def set_config_value(key, value, use_global=False):
    """Set a configuration value."""
    config = load_config(use_global)
    
    # section.key 형태 파싱
    if '.' in key:
        section, config_key = key.split('.', 1)
    else:
        # 하위 호환성: core 섹션 사용
        section, config_key = 'core', key
    
    # 섹션별 유효한 키 검증
    valid_sections = {
        'core': {
            'lang': ['ko', 'ko-KR', 'en', 'en-US', 'en-GB', 'ja', 'ja-JP', 'zh', 'zh-CN', 'zh-TW'],
            'model': ['gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo'],
            'commit': ['true', 'false'],
            'split': ['true', 'false'],
            'prompt': None  # 파일 경로이므로 별도 검증 없음
        }
    }
    
    if section not in valid_sections:
        print(f"Error: Unknown configuration section '{section}'")
        print(f"Valid sections: {', '.join(valid_sections.keys())}")
        return False
    
    if config_key not in valid_sections[section]:
        print(f"Error: Unknown configuration key '{config_key}' in section '{section}'")
        print(f"Valid keys for [{section}]: {', '.join(valid_sections[section].keys())}")
        return False
    
    # 값 검증
    valid_values = valid_sections[section][config_key]
    if valid_values is not None and value not in valid_values:
        print(f"Error: Invalid value '{value}' for key '{section}.{config_key}'")
        print(f"Valid values: {', '.join(valid_values)}")
        return False
    
    # 섹션이 없으면 생성
    if section not in config:
        config[section] = {}
    
    config[section][config_key] = value
    if save_config(config, use_global):
        scope = "global" if use_global else "local"
        print(f"Configuration set ({scope}): {section}.{config_key} = {value}")
        return True
    return False


def unset_config_value(key, use_global=False):
    """Remove a configuration value."""
    config = load_config(use_global)
    
    # section.key 형태 파싱
    if '.' in key:
        section, config_key = key.split('.', 1)
        if section in config and config_key in config[section]:
            del config[section][config_key]
            # 섹션이 비어있으면 섹션도 제거
            if not config[section]:
                del config[section]
            if save_config(config, use_global):
                scope = "global" if use_global else "local"
                print(f"Configuration unset ({scope}): {section}.{config_key}")
                return True
        else:
            print(f"Configuration key '{section}.{config_key}' not found")
    else:
        # 하위 호환성: core 섹션에서 제거
        if 'core' in config and key in config['core']:
            del config['core'][key]
            # 섹션이 비어있으면 섹션도 제거
            if not config['core']:
                del config['core']
            if save_config(config, use_global):
                scope = "global" if use_global else "local"
                print(f"Configuration unset ({scope}): core.{key}")
                return True
        else:
            print(f"Configuration key 'core.{key}' not found")
    return False


def list_config(use_global=None):
    """List all configuration values."""
    if use_global is None:
        # 글로벌과 로컬을 병합하여 표시 (로컬 우선)
        config = load_merged_config()
        scope_msg = ""
    else:
        config = load_config(use_global)
        scope_msg = " (global)" if use_global else " (local)"
    
    if not config:
        print(f"No configuration settings found{scope_msg}")
        return
    
    print(f"Configuration settings{scope_msg}:")
    for section, values in config.items():
        print(f"  {section} = {values}")
