#!/usr/bin/env python3
"""
datamanager_hjy CLI工具

提供命令行界面来快速体验和使用datamanager_hjy的功能。
"""

import argparse
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

from . import DataManager, create_data_manager


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="datamanager_hjy - 通用的数据管理脚手架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  datamanager --version                    # 显示版本信息
  datamanager --config config.yaml         # 使用指定配置文件
  datamanager --demo                       # 运行演示模式
  datamanager --health-check               # 执行健康检查
  datamanager --metrics                    # 显示性能指标
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='datamanager_hjy v0.0.1'
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        help='配置文件路径'
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true', 
        help='运行演示模式'
    )
    
    parser.add_argument(
        '--health-check', 
        action='store_true', 
        help='执行健康检查'
    )
    
    parser.add_argument(
        '--metrics', 
        action='store_true', 
        help='显示性能指标'
    )
    
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true', 
        help='详细输出'
    )
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            run_demo()
        elif args.health_check:
            run_health_check(args.config)
        elif args.metrics:
            show_metrics(args.config)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run_demo():
    """运行演示模式"""
    print("🚀 datamanager_hjy 演示模式")
    print("=" * 50)
    
    try:
        # 创建数据管理器
        print("1. 创建数据管理器...")
        dm = create_data_manager()
        print("✅ 数据管理器创建成功")
        
        # 演示基本操作
        print("\n2. 演示基本操作...")
        
        # 创建数据
        user_data = {
            'name': '演示用户',
            'email': 'demo@example.com',
            'age': 25
        }
        
        print("   - 创建用户数据...")
        try:
            result = dm.create('users', user_data)
            print(f"   ✅ 用户创建成功: {result}")
        except Exception as e:
            print(f"   ⚠️  用户创建失败 (这是正常的，因为数据库可能未配置): {e}")
        
        # 查询数据
        print("   - 查询用户数据...")
        try:
            users = dm.query('users').filter(name='演示用户').all()
            print(f"   ✅ 查询成功，找到 {len(users)} 个用户")
        except Exception as e:
            print(f"   ⚠️  查询失败 (这是正常的，因为数据库可能未配置): {e}")
        
        # 获取性能指标
        print("   - 获取性能指标...")
        try:
            metrics = dm.get_metrics()
            print("   ✅ 性能指标获取成功")
        except Exception as e:
            print(f"   ⚠️  获取性能指标失败: {e}")
        
        print("\n🎉 演示完成！")
        print("\n要使用完整功能，请:")
        print("1. 配置数据库连接")
        print("2. 创建配置文件 (config.yaml)")
        print("3. 运行: datamanager --config config.yaml")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


def run_health_check(config_path: Optional[str]):
    """执行健康检查"""
    print("🔍 执行健康检查...")
    
    try:
        dm = create_data_manager()
        
        # 检查配置
        print("1. 检查配置...")
        try:
            config = dm.get_config('database.default')
            print("   ✅ 配置检查通过")
        except Exception as e:
            print(f"   ⚠️  配置检查失败: {e}")
        
        # 检查连接
        print("2. 检查数据库连接...")
        try:
            health = dm.health_check()
            if health:
                print("   ✅ 数据库连接正常")
            else:
                print("   ❌ 数据库连接异常")
        except Exception as e:
            print(f"   ⚠️  连接检查失败: {e}")
        
        # 检查连接状态
        print("3. 检查连接状态...")
        try:
            status = dm.get_connection_status()
            print("   ✅ 连接状态检查完成")
            if status:
                print(f"   - 活跃连接: {status.get('active_connections', 0)}")
                print(f"   - 空闲连接: {status.get('idle_connections', 0)}")
        except Exception as e:
            print(f"   ⚠️  连接状态检查失败: {e}")
        
        print("\n✅ 健康检查完成")
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


def show_metrics(config_path: Optional[str]):
    """显示性能指标"""
    print("📊 性能指标")
    print("=" * 30)
    
    try:
        dm = create_data_manager()
        
        # 获取性能指标
        metrics = dm.get_metrics()
        
        if metrics:
            print("性能概览:")
            overview = metrics.get('performance', {}).get('overview', {})
            print(f"  - 总操作数: {overview.get('total_operations', 0)}")
            print(f"  - 平均执行时间: {overview.get('avg_time', 0):.3f}秒")
            print(f"  - 错误率: {overview.get('error_rate', 0):.2%}")
            
            # 慢查询
            slow_queries = dm.get_slow_queries()
            if slow_queries:
                print(f"\n慢查询 ({len(slow_queries)} 个):")
                for i, query in enumerate(slow_queries[:5], 1):
                    print(f"  {i}. {query.get('query', 'N/A')} ({query.get('execution_time', 0):.3f}秒)")
            else:
                print("\n慢查询: 无")
                
        else:
            print("暂无性能数据")
            
    except Exception as e:
        print(f"❌ 获取性能指标失败: {e}")


if __name__ == "__main__":
    main()
