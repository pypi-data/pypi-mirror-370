#!/usr/bin/env python3
"""
Akshare MCP Server - XAUUSD Gold Data
簡化版本，專注於XAUUSD黃金數據獲取和簡單SMTP傳輸
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List
from dataclasses import dataclass
from email.mime.text import MIMEText
import aiosmtplib
import akshare as ak

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xau-mcp-server")

@dataclass
class SMTPConfig:
    """SMTP配置類"""
    host: str
    port: int
    username: str
    password: str
    to_email: str
    use_tls: bool = True
    
    @classmethod
    def from_env(cls) -> "SMTPConfig":
        """從環境變量讀取SMTP配置"""
        return cls(
            host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            to_email=os.getenv("SMTP_TO_EMAIL", ""),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        )

# 全局SMTP配置
smtp_config = SMTPConfig.from_env()

# 創建MCP服務器
app = Server("xau-gold-mcp")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="get_xau_realtime",
            description="獲取XAUUSD黃金實時價格數據",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_xau_daily",
            description="獲取XAUUSD黃金日線歷史數據",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "獲取最近N天的數據，默認30天",
                        "default": 30
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="send_email",
            description="通過SMTP發送郵件（純傳輸通道）",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "郵件主題"
                    },
                    "body": {
                        "type": "string",
                        "description": "郵件正文內容"
                    }
                },
                "required": ["subject", "body"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """調用工具"""
    try:
        if name == "get_xau_realtime":
            return await get_xau_realtime()
        elif name == "get_xau_daily":
            days = arguments.get("days", 30)
            return await get_xau_daily(days)
        elif name == "send_email":
            subject = arguments.get("subject")
            body = arguments.get("body")
            return await send_simple_email(subject, body)
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    except Exception as e:
        logger.error(f"工具調用失敗 {name}: {e}")
        return [TextContent(type="text", text=f"錯誤: {str(e)}")]

async def send_simple_email(subject: str, body: str) -> List[TextContent]:
    """簡單SMTP郵件發送 - 純傳輸通道"""
    try:
        if not smtp_config.username or not smtp_config.password:
            return [TextContent(type="text", text="❌ SMTP配置不完整，請設置環境變量：SMTP_USERNAME, SMTP_PASSWORD")]
        
        if not smtp_config.to_email:
            return [TextContent(type="text", text="❌ 收件人未配置，請設置環境變量：SMTP_TO_EMAIL")]
            
        # 創建郵件消息
        msg = MIMEText(body, "html", "utf-8")
        msg["From"] = smtp_config.username
        msg["To"] = smtp_config.to_email
        msg["Subject"] = subject
        
        # 連接SMTP服務器並發送郵件
        if smtp_config.port == 465:
            # SSL connection for port 465
            async with aiosmtplib.SMTP(
                hostname=smtp_config.host,
                port=smtp_config.port,
                use_tls=True,
                start_tls=False
            ) as smtp:
                await smtp.login(smtp_config.username, smtp_config.password)
                await smtp.send_message(msg)
        else:
            # STARTTLS connection for port 587
            async with aiosmtplib.SMTP(
                hostname=smtp_config.host,
                port=smtp_config.port,
                use_tls=False
            ) as smtp:
                await smtp.starttls()
                await smtp.login(smtp_config.username, smtp_config.password)
                await smtp.send_message(msg)
            
        logger.info(f"郵件發送成功到: {smtp_config.to_email}")
        return [TextContent(type="text", text=f"✅ 郵件發送成功到: {smtp_config.to_email}")]
        
    except Exception as e:
        logger.error(f"郵件發送失敗: {e}")
        return [TextContent(type="text", text=f"❌ 郵件發送失敗: {str(e)}")]

async def get_xau_realtime() -> List[TextContent]:
    """獲取XAUUSD實時價格"""
    try:
        # 使用akshare獲取黃金實時數據
        df = ak.futures_foreign_commodity_realtime(symbol='XAU')
        
        if df.empty:
            return [TextContent(type="text", text="❌ 無法獲取XAUUSD實時數據")]
        
        # 提取數據 - 使用索引避免中文列名編碼問題
        row = df.iloc[0]
        price = float(row.iloc[1])        # 當前價格
        change = float(row.iloc[3])       # 漲跌
        change_pct = float(row.iloc[4])   # 漲跌幅
        time_str = str(row.iloc[12])      # 時間
        date_str = str(row.iloc[13])      # 日期
        
        result = f"""✅ XAUUSD 黃金實時價格

💰 當前價格: ${price:.2f}
📈 漲跌幅: ${change:.2f} ({change_pct:.2f}%)
🕒 更新時間: {date_str} {time_str}
📊 數據來源: AkShare"""
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"獲取實時數據失敗: {e}")
        return [TextContent(type="text", text=f"❌ 獲取實時數據失敗: {str(e)}")]

async def get_xau_daily(days: int = 30) -> List[TextContent]:
    """獲取XAUUSD日線數據"""
    try:
        # 使用akshare獲取黃金歷史數據
        df = ak.futures_foreign_hist(symbol='XAU')
        
        if df.empty:
            return [TextContent(type="text", text="❌ 無法獲取XAUUSD歷史數據")]
        
        # 獲取最近N天的數據
        recent_df = df.tail(days)
        
        # 計算統計信息
        latest = recent_df.iloc[-1]
        highest = recent_df['high'].max()
        lowest = recent_df['low'].min()
        
        result = f"""✅ XAUUSD 黃金日線數據 (最近{days}天)

📅 數據期間: {recent_df.iloc[0]['date']} 至 {latest['date']}
💰 最新收盤: ${latest['close']:.2f}
📈 期間最高: ${highest:.2f}
📉 期間最低: ${lowest:.2f}
📊 數據記錄: {len(recent_df)} 天

最近5天收盤價:"""
        
        # 添加最近5天數據
        recent_5 = recent_df.tail(5)
        for _, row in recent_5.iterrows():
            result += f"\n  {row['date']}: ${row['close']:.2f}"
        
        result += f"\n\n📊 數據來源: AkShare"
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"獲取歷史數據失敗: {e}")
        return [TextContent(type="text", text=f"❌ 獲取歷史數據失敗: {str(e)}")]

async def main():
    """運行服務器"""
    logger.info("啟動XAUUSD Gold MCP服務器...")  
    
    # 檢查SMTP配置
    if smtp_config.username and smtp_config.password and smtp_config.to_email:
        logger.info(f"SMTP配置已加載: {smtp_config.host}:{smtp_config.port} -> {smtp_config.to_email}")
    else:
        logger.warning("SMTP配置未完整，郵件功能將不可用。請設置環境變量：SMTP_USERNAME, SMTP_PASSWORD, SMTP_TO_EMAIL")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

def cli_main():
    """CLI入口點"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()