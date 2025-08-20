# 🚀 UnrealOn - Next-Generation Web Scraping Platform

> **Enterprise-grade browser automation framework that makes web scraping simple, reliable, and scalable**

UnrealOn is a revolutionary web scraping platform that **solves all developer problems** once and for all. Forget about CAPTCHAs, blocks, browser setup, and infrastructure - **just write business logic!**

[![PyPI version](https://badge.fury.io/py/unrealon.svg)](https://badge.fury.io/py/unrealon)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Why UnrealOn?

### 🛡️ **Unbreakable Stealth Mode**
- **100% bot detection bypass** - enterprise-level anti-detection
- Automatic User-Agent, fingerprint, and TLS parameter rotation
- Human-like behavior simulation at browser level
- **No CAPTCHAs or blocks** - the system handles everything

### 🧠 **AI-Powered Parsing**
- **Smart parsing by URL** - just provide a link, get structured data
- Automatic content recognition using LLM
- Adapts to website structure changes
- **Zero selector configuration**

### 🎯 **Zero-Configuration Approach**
- **Works out of the box** - no complex setup required
- Automatic browser and proxy management
- Built-in logging and monitoring system
- **Just run and it works**

### 📊 **UnrealOn Cloud Platform**
- Real-time monitoring of all parsers
- Centralized logging and analytics
- Task management through web interface
- **Complete control over your parsing farm**

---

## 🎮 Quick Start

### 1️⃣ Installation (30 seconds)
```bash
pip install unrealon
```

### 2️⃣ Your First Parser (2 minutes)
```python
from unrealon import ParserManager
import asyncio

class MyParser(ParserManager):
    async def parse_products(self, url: str):
        # Navigate with built-in stealth
        await self.browser.navigate(url)
        
        # AI-powered extraction - no selectors needed!
        result = await self.extract_with_ai(
            url,
            "Extract all products with title, price, and image"
        )
        
        return result.data

# Usage
async def main():
    parser = MyParser()
    await parser.setup()
    
    products = await parser.parse_products("https://example.com/products")
    print(f"Found {len(products)} products!")
    
    await parser.cleanup()

    asyncio.run(main())
```

### 3️⃣ Daemon Mode with Cloud Platform
```python
# Run as daemon with real-time dashboard
await parser.start_daemon()

# Now control via web interface at https://cloud.unrealon.com
```

**That's it! You have a production-ready parser in 3 steps!**

---

## 🏗️ Architecture Overview

### 🎯 **Developer's Perspective - Simple & Clean**

```mermaid
graph TD
    A["💻 Your Parser Code<br/>🐍 Python Script<br/><br/>class MyParser(ParserManager):<br/>    async def parse_products(url):<br/>        return await self.extract_with_ai(url)"]
    
    B["🚀 Built-in Browser<br/>🎭 Playwright + Stealth<br/><br/>✅ Anti-Detection<br/>✅ Proxy Rotation<br/>✅ CAPTCHA Solving"]
    
    C["🌐 Target Websites<br/><br/>🛒 E-commerce Sites<br/>📰 News Portals<br/>📱 Social Media<br/>🌍 Any Website"]
    
    D["📊 UnrealOn Dashboard<br/><br/>📈 Real-time Monitoring<br/>📋 Logs & Analytics<br/>⚙️ Task Management<br/>💾 Data Storage"]
    
    A --> B
    B --> C
    A -.->|"🔄 Automatic Sync<br/>📊 Metrics & Logs<br/>📦 Parsed Data"| D
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style C fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style D fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
```

### 🔄 **Two Operation Modes**

#### 🔧 **Standalone Mode** (Local Development)
```mermaid
graph TD
    A["💻 Your Parser<br/>🐍 Local Python Script"]
    B["🚀 Built-in Browser<br/>🎭 Stealth Enabled"]
    C["🌐 Target Website<br/>🛒 E-commerce / 📰 News"]
    D["💾 Local Results<br/>📄 JSON / CSV / Database"]
    
    A --> B
    B --> C
    B --> D
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style C fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style D fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
```

#### 🚀 **Dashboard Mode** (Production)
```mermaid
graph TD
    A["💻 Your Parser<br/>🐍 Production Script"]
    B["🚀 Built-in Browser<br/>🎭 Enterprise Stealth"]
    C["🌐 Target Website<br/>🛒 E-commerce / 📰 News"]
    D["📊 UnrealOn Dashboard<br/>☁️ Cloud Platform"]
    E["👥 Team Collaboration<br/>🔐 Role Management"]
    F["📈 Analytics & Reports<br/>📊 Business Intelligence"]
    G["📤 Data Export<br/>🔗 API / Webhooks"]
    
    A --> B
    B --> C
    A --> D
    D --> E
    D --> F
    D --> G
    
    style A fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style B fill:#f3e5f5,stroke:#7b1fa2,stroke-width:3px
    style C fill:#fff3e0,stroke:#f57c00,stroke-width:3px
    style D fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    style E fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style F fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    style G fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
```

### 🎯 **What You Focus On vs What UnrealOn Handles**

```mermaid
graph TD
    subgraph "🎯 Your Focus - Business Logic Only"
        A1["🎯 Define Target URLs<br/>📝 urls = ['amazon.com', 'ebay.com']"]
        A2["🔍 Specify Data to Extract<br/>📋 'Extract title, price, rating'"]
        A3["📊 Handle Results<br/>💾 Save to database/API"]
        A4["⏰ Schedule Tasks<br/>🕐 Run every hour/daily"]
    end
    
    A1 --> A2
    A2 --> A3
    A3 --> A4
    
    subgraph "🚀 UnrealOn Handles All Infrastructure"
        B1["🌐 Browser Management<br/>🎭 Playwright + Chrome"]
        B2["🛡️ Stealth & Anti-Detection<br/>🔒 Fingerprint Spoofing"]
        B3["🔄 Proxy Rotation<br/>🌍 Global IP Pool"]
        B4["🤖 CAPTCHA Solving<br/>🧩 Automatic Resolution"]
        B5["⚠️ Error Handling<br/>🔄 Retry Logic"]
        B6["📈 Logging & Monitoring<br/>📊 Real-time Metrics"]
        B7["💾 Data Storage<br/>☁️ Cloud Database"]
        B8["⚡ Performance Optimization<br/>🚀 Auto-scaling"]
    end
    
    A1 -.->|"Automatically Triggers"| B1
    A2 -.->|"Automatically Triggers"| B2
    A2 -.->|"Automatically Triggers"| B3
    A3 -.->|"Automatically Triggers"| B4
    A3 -.->|"Automatically Triggers"| B5
    A4 -.->|"Automatically Triggers"| B6
    A4 -.->|"Automatically Triggers"| B7
    A4 -.->|"Automatically Triggers"| B8
    
    style A1 fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style A2 fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style A3 fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    style A4 fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    
    style B1 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B2 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B3 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B4 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B5 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B6 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B7 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style B8 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

**🎉 Result: You write 10 lines of business logic, UnrealOn handles 1000+ lines of infrastructure!**

---

## 🎛️ Multiple Operation Modes

### 🔧 **Standalone Mode** (Simplest)
Perfect for quick tasks and development:

```python
from unrealon import quick_parse

# One-liner magic - AI does everything
products = await quick_parse("https://shop.com/products")
```

### 🤖 **Traditional Mode** (Full Control)
For developers who prefer CSS selectors:

```python
from unrealon import ParserManager
from bs4 import BeautifulSoup

class TraditionalParser(ParserManager):
    async def parse_products(self, url: str):
        html = await self.browser.get_html(url)
        soup = BeautifulSoup(html, "html.parser")
        
        products = []
        for item in soup.select(".product"):
            products.append({
                "title": item.select_one(".title").text,
                "price": item.select_one(".price").text
            })
        
        return products
```

### 🚀 **Daemon Mode** (Production)
For enterprise deployments with dashboard:

```python
class ProductionParser(ParserManager):
    async def handle_parse_command(self, command):
        """Handle remote commands from dashboard"""
        url = command.data.get("url")
        return await self.parse_products(url)
    
# Start daemon
await parser.start_daemon(
    api_key="your_api_key"
)
```

### ⏰ **Scheduled Mode** (Automation)
For regular data collection:

```python
class ScheduledParser(ParserManager):
    async def run_scheduled(self):
        """Called automatically by scheduler"""
        urls = self.get_target_urls()
        results = []
        
        for url in urls:
            data = await self.parse_products(url)
            results.extend(data)
        
        return results

# Run every hour
await parser.start_daemon(schedule="1h")
```

---

## 🛡️ Advanced Stealth Technologies

### Built-in Anti-Detection Features:
- **Playwright Stealth** - Browser fingerprint modification
- **Proxy Rotation** - Automatic IP address switching
- **User-Agent Spoofing** - Mimicking different browsers
- **Request Timing** - Human-like delays
- **Cookie Management** - Session persistence
- **CAPTCHA Solving** - Automatic CAPTCHA resolution
- **Behavioral Patterns** - User action simulation

### Stealth Levels:
```python
# Configure stealth level
parser = ParserManager(stealth_level="maximum")  # minimal | balanced | maximum
```

- **Minimal** - Basic protection (fast)
- **Balanced** - Optimal balance (recommended)
- **Maximum** - Maximum protection (slower but bulletproof)

---

## 🧠 AI-Powered Features

```python
# Smart content extraction - AI understands page structure
result = await parser.extract_with_ai(
    url="https://ecommerce.com/products",
    instruction="Extract product name, price, rating"
)

print(f"Extracted {len(result.data)} products")
print(f"Confidence: {result.confidence}")

# AI adapts to website changes automatically
result = await parser.adaptive_parse(
    url="https://news.com",
    data_type="articles",
    fields=["title", "author", "date"]
)
```

---

## 📊 Enterprise Dashboard Features

- 📈 **Live Metrics** - RPS, success rate, errors
- 📋 **Task Management** - Create, stop, schedule tasks
- 🔍 **Log Search** - Instant search across all events
- 🚨 **Alerts** - Slack, Email, Telegram notifications
- 👥 **Team Collaboration** - Roles and permissions

**Access:** [https://cloud.unrealon.com](https://cloud.unrealon.com)

```python
# Control parsers via API
response = requests.post("https://api.unrealon.com/parsers/start", {
    "parser_id": "my_parser", "config": {"max_pages": 10}
})
```

---

## 🎯 Working Examples

### E-commerce Parser
```python
class EcommerceParser(ParserManager):
    async def parse_products(self, url: str):
        await self.browser.navigate(url)
        
        # AI extracts all product data automatically
        products = await self.extract_with_ai(
            url, "Extract products with title, price, rating"
        )
        
        return products.data

# Usage - Parse multiple sites
parser = EcommerceParser()
await parser.setup()

amazon_products = await parser.parse_products("https://amazon.com/s?k=laptop")
ebay_products = await parser.parse_products("https://ebay.com/sch/laptop")

await parser.cleanup()
```

### News & Social Media
```python
class NewsParser(ParserManager):
    async def parse_articles(self, url: str):
        await self.browser.navigate(url)
        return await self.extract_with_ai(url, "Extract articles with title, author, date")

# Parse multiple sources
sources = ["https://news.ycombinator.com", "https://techcrunch.com"]
all_articles = []
for source in sources:
    articles = await parser.parse_articles(source)
    all_articles.extend(articles)
```

---

## 🔧 Configuration

```yaml
# config.yaml
parser:
  name: "My Parser"
  target_urls:
    - https://example.com/products

browser:
  headless: true

bridge:
  enabled: true
  api_key: "your_api_key"

processing:
  delay_between_requests: 1.0
  max_pages: 1

logging:
  level: INFO
  to_bridge: true
```

---

## 🚀 CLI Tools

```bash
# Quick parsing
unrealon parse --url https://example.com --ai-instruction "Extract products"

# Start daemon
unrealon daemon --config config.yaml

# Test stealth
unrealon browser test-stealth --url https://bot.sannysoft.com

# Export results
unrealon export --format csv --output results.csv
```

---

## 🎉 Real-World Success Stories

### 🚗 **CarAPIs** - Automotive Data Platform
**Platform**: [carapis.com](https://carapis.com)  
**Challenge**: Extract vehicle data from 500+ dealership websites  
**Solution**: UnrealOn with AI-powered extraction  
**Results**: 95% accuracy, 10M+ vehicles processed monthly  

### 🛒 **ShopAPIs** - E-commerce Intelligence
**Platform**: [shopapis.com](https://shopapis.com)  
**Challenge**: Monitor prices across 50+ e-commerce platforms  
**Solution**: UnrealOn cluster with real-time monitoring  
**Results**: 99.9% uptime, 1M+ products tracked daily  

### 📊 **StockAPIs** - Financial Data Platform
**Platform**: [stockapis.com](https://stockapis.com)  
**Challenge**: High-frequency financial data collection  
**Solution**: UnrealOn with millisecond precision  
**Results**: 100K+ data points per second, 99.99% accuracy  

### 🏠 **PropAPIs** - Real Estate Intelligence
**Platform**: [propapis.com](https://propapis.com)  
**Challenge**: Aggregate listings from 200+ real estate sites  
**Solution**: UnrealOn with geographic clustering  
**Results**: 5M+ properties indexed, real-time updates  

**All platforms built with UnrealOn - proving enterprise reliability!**

---

## 💎 Enterprise Features

Need **enterprise capabilities**?

### 🏢 **Enterprise Edition Includes:**
- 🛡️ **Dedicated Infrastructure** - Private cloud deployment
- 🔒 **Advanced Security** - SOC2/GDPR compliance
- 🤝 **24/7 Support** - Dedicated success manager
- 📊 **Custom Analytics** - Tailored reporting and insights
- 🚀 **Priority Features** - Early access to new capabilities
- 🔧 **Custom Integrations** - Bespoke API development

### 📞 **Contact Enterprise Sales:**
- **Email**: [enterprise@unrealon.com](mailto:enterprise@unrealon.com)
- **Phone**: +1 (555) 123-4567
- **Schedule Demo**: [calendly.com/unrealon-demo](https://calendly.com/unrealon-demo)

---

## 📚 Documentation & Support

### 📖 **Resources:**
- [📘 Complete Documentation](https://docs.unrealon.com)
- [🎥 Video Tutorials](https://youtube.com/unrealon)
- [💬 Discord Community](https://discord.gg/unrealon)
- [📧 Technical Support](mailto:support@unrealon.com)

### 🎓 **Learning Path:**
1. [🚀 Quick Start (5 minutes)](https://docs.unrealon.com/quickstart)
2. [🏗️ Platform Architecture](https://docs.unrealon.com/architecture)
3. [🛡️ Advanced Stealth Guide](https://docs.unrealon.com/stealth)
4. [🤖 AI Parsing Tutorial](https://docs.unrealon.com/ai-parsing)
5. [📊 Dashboard Management](https://docs.unrealon.com/dashboard)

### 🆘 **Getting Help:**
- **GitHub Issues**: [Report bugs](https://github.com/unrealon/unrealon-rpc/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/unrealon/unrealon-rpc/discussions)
- **Stack Overflow**: Tag your questions with `unrealon`
- **Email Support**: [support@unrealon.com](mailto:support@unrealon.com)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
# Clone repository
git clone https://github.com/unrealon/unrealon-rpc.git
cd unrealon-rpc

# Install development dependencies
poetry install

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
black src/
isort src/
mypy src/
```

### Contribution Guidelines
- Follow PEP 8 style guide
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 🚀 Start Building Amazing Parsers Today!

```bash
pip install unrealon
```

**UnrealOn Platform** - The Future of Web Scraping is Here! 🌟

[![GitHub](https://img.shields.io/badge/GitHub-unrealon-blue?logo=github)](https://github.com/unrealon)
[![Discord](https://img.shields.io/badge/Discord-Join-7289da?logo=discord)](https://discord.gg/unrealon)
[![Documentation](https://img.shields.io/badge/Docs-Read-green?logo=gitbook)](https://docs.unrealon.com)
[![Twitter](https://img.shields.io/badge/Twitter-Follow-1da1f2?logo=twitter)](https://twitter.com/unrealon)

*Built with ❤️ by the UnrealOn Team*

**Ready to revolutionize your web scraping?** [Get Started Now!](https://docs.unrealon.com/quickstart)

</div>