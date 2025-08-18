# -*- coding: utf-8 -*-  
"""
基于FastMCP框架的TypeScript服务器实现。
提供了验证码生成和其他实用工具功能。
"""
from mcp.server.fastmcp import FastMCP
import random
import string
import asyncio
import json
import os
import logging
from typing import Dict, Any, Optional, List, Union

class MCPTSServer:
    """
    验证码生成服务器类
    
    提供基于FastMCP框架的服务器实现，支持多种验证码生成功能。
    """
    
    def __init__(self, name: str = None, description: str = None, config_path: str = None):
        """
        初始化MCP TypeScript服务器
        
        参数:
            name: 服务器名称，如果为None则从配置文件加载
            description: 服务器描述，如果为None则从配置文件加载
            config_path: 配置文件路径，默认为包目录下的config.json
        """
        # 加载配置文件
        self.config = self._load_config(config_path)
        
        # 设置日志
        self._setup_logging()
        
        # 设置服务器名称和描述
        self.name = name or self.config['server']['name']
        self.description = description or self.config['server']['description']
        
        # 创建FastMCP实例
        self.mcp = FastMCP(self.name)
        
        # 注册工具、资源和提示词
        self._register_tools()
        self._register_resources()
        self._register_prompts()
        
        logging.info(f"MCP服务器 '{self.name}' 初始化完成")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        参数:
            config_path: 配置文件路径，如果为None则使用默认路径
            
        返回:
            配置字典
        """
        if config_path is None:
            # 默认配置文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'config.json')
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logging.debug(f"配置文件加载成功: {config_path}")
                return config
        except Exception as e:
            logging.warning(f"加载配置文件失败: {e}，使用默认配置")
            # 返回默认配置
            return {
                "server": {
                    "name": "VerificationCodeServer",
                    "description": "验证码生成服务器",
                    "default_transport": "stdio",
                    "sse": {"host": "127.0.0.1", "port": 8000}
                },
                "tools": {
                    "verification_code": {"enabled": True, "default_length": 6},
                    "typescript": {"enabled": True}
                },
                "resources": {"templates": {"enabled": True}},
                "prompts": {"enabled": True},
                "logging": {"level": "info", "console": True}
            }
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_level_name = log_config.get('level', 'info').upper()
        log_level = getattr(logging, log_level_name, logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler() if log_config.get('console', True) else None,
                logging.FileHandler(log_config.get('file', 'mcp_ts_server.log')) 
                if 'file' in log_config else None
            ]
        )
    
    def _register_tools(self):
        """注册所有工具函数"""
        logging.info("注册工具函数...")
        
        # 验证码工具
        if self.config['tools']['verification_code']['enabled']:
            self._register_verification_code_tools()
        
        # TypeScript工具
        if self.config['tools']['typescript']['enabled']:
            self._register_typescript_tools()
    
    def _register_verification_code_tools(self):
        """注册验证码生成工具"""
        default_length = self.config['tools']['verification_code'].get('default_length', 6)
        logging.debug(f"注册验证码工具，默认长度: {default_length}")
        
        @self.mcp.tool()
        def generate_numeric_verification_code(digits: int = default_length) -> str:
            """
            生成一个数字验证码。
            如果未指定位数，默认生成指定位数的数字验证码。
            
            参数:
                digits: 验证码位数，默认为配置的默认长度
                
            返回:
                生成的数字验证码
            """
            return ''.join(random.choices(string.digits, k=digits))
        
        @self.mcp.tool()
        def generate_alphabetic_verification_code(length: int = default_length) -> str:
            """
            生成一个纯字母验证码（包含大小写）。
            如果未指定长度，默认生成指定位数的字母验证码。
            
            参数:
                length: 验证码长度，默认为配置的默认长度
                
            返回:
                生成的字母验证码
            """
            return ''.join(random.choices(string.ascii_letters, k=length))
        
        @self.mcp.tool()
        def generate_mixed_verification_code(length: int = default_length) -> str:
            """
            生成一个字母和数字混合的验证码。
            如果未指定长度，默认生成指定位数的混合验证码。
            
            参数:
                length: 验证码长度，默认为配置的默认长度
                
            返回:
                生成的混合验证码
            """
            characters = string.ascii_letters + string.digits
            return ''.join(random.choices(characters, k=length))
    
    def _register_typescript_tools(self):
        """注册TypeScript相关工具"""
        formatter_config = self.config['tools']['typescript'].get('formatter', {})
        indent_size = formatter_config.get('indent_size', 2)
        use_tabs = formatter_config.get('use_tabs', False)
        single_quotes = formatter_config.get('single_quotes', True)
        logging.debug(f"注册TypeScript工具，缩进大小: {indent_size}, 使用制表符: {use_tabs}")
        
        @self.mcp.tool()
        def format_typescript_code(code: str) -> str:
            """
            格式化TypeScript代码
            
            参数:
                code: 需要格式化的TypeScript代码
                
            返回:
                格式化后的代码
            """
            lines = code.split('\n')
            formatted_lines = []
            indent_level = 0
            
            # 缩进字符
            indent_char = '\t' if use_tabs else ' '
            indent_unit = 1 if use_tabs else indent_size
            
            for line in lines:
                stripped = line.strip()
                
                # 空行处理
                if not stripped:
                    formatted_lines.append('')
                    continue
                
                # 处理缩进减少
                if stripped.startswith('}') or stripped.startswith(']'):
                    indent_level = max(0, indent_level - 1)
                
                # 添加当前行（带缩进）
                formatted_lines.append(indent_char * indent_level * indent_unit + stripped)
                
                # 处理缩进增加
                if stripped.endswith('{') or stripped.endswith('['):
                    indent_level += 1
            
            # 处理引号
            result = '\n'.join(formatted_lines)
            if single_quotes:
                # 将双引号替换为单引号（简单实现，不处理转义情况）
                result = result.replace('"', "'")
            
            return result
        
        @self.mcp.tool()
        def analyze_typescript_code(code: str) -> Dict[str, Any]:
            """
            分析TypeScript代码，提取关键信息
            
            参数:
                code: 需要分析的TypeScript代码
                
            返回:
                包含代码分析结果的字典
            """
            # 简单实现，实际应用中可以使用AST解析
            analysis = {
                "classes": [],
                "interfaces": [],
                "functions": [],
                "imports": [],
                "exports": [],
                "lines_of_code": len(code.split('\n'))
            }
            
            lines = code.split('\n')
            for line in lines:
                line = line.strip()
                
                # 检测类
                if line.startswith('class '):
                    class_name = line.split(' ')[1].split('{')[0].split('extends')[0].split('implements')[0].strip()
                    analysis["classes"].append(class_name)
                
                # 检测接口
                elif line.startswith('interface '):
                    interface_name = line.split(' ')[1].split('{')[0].split('extends')[0].strip()
                    analysis["interfaces"].append(interface_name)
                
                # 检测函数
                elif line.startswith('function '):
                    func_name = line.split(' ')[1].split('(')[0].strip()
                    analysis["functions"].append(func_name)
                
                # 检测导入
                elif line.startswith('import '):
                    analysis["imports"].append(line)
                
                # 检测导出
                elif line.startswith('export '):
                    analysis["exports"].append(line)
            
            return analysis
    
    def _register_resources(self):
        """注册所有资源"""
        logging.info("注册资源...")
        
        # 模板资源
        if self.config['resources']['templates']['enabled']:
            self._register_template_resources()
    
    def _register_template_resources(self):
        """注册模板资源"""
        cache_templates = self.config['resources']['templates'].get('cache_templates', True)
        logging.debug(f"注册模板资源，缓存模板: {cache_templates}")
        
        # 模板缓存
        template_cache = {}
        
        @self.mcp.resource("ts-template://{template_name}")
        def get_typescript_template(template_name: str) -> str:
            """
            获取TypeScript模板代码
            
            参数:
                template_name: 模板名称
                
            返回:
                模板代码
            """
            # 如果启用缓存且模板已缓存，则直接返回
            if cache_templates and template_name in template_cache:
                return template_cache[template_name]
            
            templates = {
                "class": """
export class ClassName {
    private property: string;
    
    constructor(property: string) {
        this.property = property;
    }
    
    public getProperty(): string {
        return this.property;
    }
    
    public setProperty(value: string): void {
        this.property = value;
    }
}
                """,
                "interface": """
export interface IExample {
    id: number;
    name: string;
    description?: string;
    getData(): any;
}
                """,
                "react-component": """
import React, { useState, useEffect } from 'react';

interface Props {
    title: string;
}

export const ExampleComponent: React.FC<Props> = ({ title }) => {
    const [count, setCount] = useState<number>(0);
    
    useEffect(() => {
        document.title = `${title} (${count})`;
    }, [count, title]);
    
    return (
        <div>
            <h1>{title}</h1>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>Increment</button>
        </div>
    );
};
                """,
                "next-page": """
import { NextPage } from 'next';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

interface PageProps {
    title: string;
}

const Page: NextPage<PageProps> = ({ title }) => {
    return (
        <div className={styles.container}>
            <Head>
                <title>{title}</title>
                <meta name="description" content="Generated by create next app" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <main className={styles.main}>
                <h1 className={styles.title}>{title}</h1>
                
                <div className={styles.grid}>
                    <div className={styles.card}>
                        <h2>Documentation &rarr;</h2>
                        <p>Find in-depth information about Next.js features and API.</p>
                    </div>
                </div>
            </main>

            <footer className={styles.footer}>
                <p>Powered by Next.js</p>
            </footer>
        </div>
    );
};

export default Page;
                """
            }
            
            result = templates.get(template_name, "Template not found")
            
            # 如果启用缓存，则缓存模板
            if cache_templates:
                template_cache[template_name] = result
            
            return result
    
    def _register_prompts(self):
        """注册所有提示词模板"""
        logging.info("注册提示词模板...")
        
        # 如果提示词功能已启用
        if self.config['prompts']['enabled']:
            self._register_typescript_prompts()
    
    def _register_typescript_prompts(self):
        """注册TypeScript相关提示词模板"""
        default_style = self.config['prompts'].get('default_style', 'friendly')
        logging.debug(f"注册TypeScript提示词模板，默认风格: {default_style}")
        
        @self.mcp.prompt()
        def typescript_code_review(code: str, focus_areas: Optional[List[str]] = None) -> str:
            """
            生成TypeScript代码审查提示词
            
            参数:
                code: 需要审查的代码
                focus_areas: 重点关注的领域，如["性能", "安全", "可读性"]
                
            返回:
                代码审查提示词
            """
            areas = focus_areas or ["代码质量", "最佳实践", "可读性"]
            areas_text = ", ".join(areas)
            
            return f"""
请审查以下TypeScript代码，重点关注这些方面: {areas_text}。
提供具体的改进建议和最佳实践推荐。

```typescript
{code}
```

请按以下格式提供反馈:
1. 总体评价
2. 具体问题和改进建议（按严重程度排序）
3. 代码优化建议
4. 最佳实践推荐
            """
        
        @self.mcp.prompt()
        def typescript_project_setup(project_name: str, features: List[str] = None, style: str = default_style) -> str:
            """
            生成TypeScript项目设置提示词
            
            参数:
                project_name: 项目名称
                features: 需要的功能，如["React", "ESLint", "Jest"]
                style: 提示词风格，如"friendly"、"formal"、"detailed"
                
            返回:
                项目设置提示词
            """
            features_list = features or ["TypeScript", "ESLint", "Jest"]
            features_text = ", ".join(features_list)
            
            styles = {
                "friendly": "请以友好的方式",
                "formal": "请以正式的方式",
                "detailed": "请以详细的方式",
                "concise": "请以简洁的方式"
            }
            
            style_text = styles.get(style, styles[default_style])
            
            return f"""
{style_text}指导我如何设置一个名为"{project_name}"的TypeScript项目，包含以下功能: {features_text}。

请包括以下内容:
1. 项目结构建议
2. 必要的依赖包
3. 配置文件示例
4. 开发工作流程建议
5. 最佳实践

请提供具体的命令和代码示例，以便我可以按照指导进行操作。
            """
    
    async def run_async(self, transport: str = "stdio"):
        """
        异步运行MCP服务器
        
        参数:
            transport: 传输方式，默认为"stdio"
        """
        print(f"启动 {self.description}...")
        print("服务器运行中，按Ctrl+C停止...")
        if transport == "stdio":
            # 直接使用self.mcp的run_stdio_async方法，避免嵌套事件循环
            await self.mcp.run_stdio_async()
        else:
            await self.mcp.run_sse_async(host="127.0.0.1", port=8000)
    
    async def run_sse_async(self, host: str = "127.0.0.1", port: int = 8000):
        """
        以SSE方式异步运行MCP服务器
        
        参数:
            host: 主机地址，默认为"127.0.0.1"
            port: 端口号，默认为8000
        """
        print(f"启动 {self.description} (SSE模式)...")
        print(f"服务器地址: http://{host}:{port}")
        print("服务器运行中，按Ctrl+C停止...")
        await self.mcp.run_sse_async(host=host, port=port)
    
    def run(self, transport: str = "stdio"):
        """
        同步运行MCP服务器（便捷方法）
        
        参数:
            transport: 传输方式，默认为"stdio"
        """
        asyncio.run(self.run_async(transport=transport))
    
    def run_sse(self, host: str = "127.0.0.1", port: int = 8000):
        """
        以SSE方式同步运行MCP服务器（便捷方法）
        
        参数:
            host: 主机地址，默认为"127.0.0.1"
            port: 端口号，默认为8000
        """
        asyncio.run(self.run_sse_async(host=host, port=port))


# 便捷函数，直接创建并运行服务器
def create_and_run_server(name: str = "VerificationCodeServer", 
                         description: str = "验证码生成服务器",
                         transport: str = "stdio"):
    """
    创建并运行MCP服务器（便捷函数）
    
    参数:
        name: 服务器名称
        description: 服务器描述
        transport: 传输方式，默认为"stdio"
    """
    server = MCPTSServer(name, description)
    server.run(transport)


def create_and_run_sse_server(name: str = "VerificationCodeServer", 
                             description: str = "验证码生成服务器",
                             host: str = "127.0.0.1", 
                             port: int = 8000):
    """
    创建并以SSE方式运行MCP服务器（便捷函数）
    
    参数:
        name: 服务器名称
        description: 服务器描述
        host: 主机地址，默认为"127.0.0.1"
        port: 端口号，默认为8000
    """
    server = MCPTSServer(name, description)
    server.run_sse(host, port)


if __name__ == "__main__":
    # 如果直接运行此模块，则创建并运行服务器
    create_and_run_server("VerificationCodeServer", "验证码生成服务器")
