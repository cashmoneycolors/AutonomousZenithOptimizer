# Autonomous Zenith Optimizer - Production Desktop Suite v3.0

## Quick Start

### Launch Methods

#### 1. **Windows (Recommended)**
```bash
# Double-click
launch_desktop.bat

# Or from command line
python launch_desktop.py
```

#### 2. **Python Direct**
```bash
python -m desktop_app
# OR
python launch_desktop.py
```

#### 3. **Linux/macOS**
```bash
python3 launch_desktop.py
```

---

## Features

### Core Capabilities
- **Real-time Mining Management**: Monitor and control GPU/ASIC rigs
- **Live Performance Analytics**: Charts and metrics for 24-hour history
- **Automated Optimization**: Intelligent algorithm switching and parameter tuning
- **Risk Management**: Stop-loss protection and portfolio diversification
- **Alert System**: Real-time notifications via Telegram/Discord
- **Professional Dashboard**: Enterprise-grade UI with multiple monitoring views

### Dashboard Tabs

#### 📊 Overview
- KPI cards: Total Profit, Active Rigs, Efficiency, Risk Level
- 24-hour performance chart
- Real-time system status indicators

#### ⛏️ Mining
- Rig status table with live metrics
- Algorithm, hashrate, temperature, power consumption
- Quick optimization controls
- Individual rig management

#### 📈 Performance
- CPU/GPU/Memory usage charts
- System resource monitoring
- Historical trend analysis
- Performance recommendations

#### 🔔 Alerts
- Alert history and severity levels
- Real-time notifications
- Manual alert testing
- Alert filtering and search

---

## Control Panel

### System Control
- **🚀 START SYSTEM**: Boot all mining components
- **🛑 STOP SYSTEM**: Gracefully shutdown all rigs
- **🔄 RESTART**: Restart all components

### Mining Control
- **▶️ Start**: Begin mining operations
- **⏹️ Stop**: Stop mining
- **🔄 Optimize**: Run optimization algorithms

### Monitoring
- **Live Monitor**: Toggle continuous monitoring
- Real-time metrics display:
  - Daily profit (CHF)
  - Active rigs count
  - Hashrate (MH/s)
  - Average temperature
  - Alert counter

---

## Menu Structure

### File
- 💾 **Export Report**: Save system metrics to JSON
- ⚙️ **Settings**: Configuration management
- 🚪 **Exit**: Close application

### Mining
- ▶️ **Start Mining**: Begin all rigs
- ⏹️ **Stop Mining**: Stop all rigs
- 🔄 **Restart All**: Full system restart

### Tools
- 🔧 **System Diagnostics**: View component status
- 📊 **Analytics**: Advanced analysis dashboard
- 📝 **Logs**: System log viewer

### Help
- 📚 **Documentation**: Reference guide
- ℹ️ **About**: Application information

---

## System Requirements

### Hardware
- Minimum: Intel i5 / AMD Ryzen 5, 8GB RAM, SSD
- Recommended: Intel i7 / AMD Ryzen 7, 16GB RAM, NVMe

### Software
- Python 3.8+
- tkinter (included with Python)
- matplotlib
- psutil
- numpy (optional, for advanced analytics)

### Dependencies Installation
```bash
pip install -r requirements.txt
```

---

## Configuration

### Settings File
Edit `settings.json` for:
- Mining pool configuration
- Alert services (Telegram, Discord)
- Temperature thresholds
- Risk management parameters
- Backup schedules

### Example Configuration
```json
{
  "System": {
    "Name": "AZO Production Suite",
    "Version": "3.0"
  },
  "Mining": {
    "pools": ["pool1.example.com", "pool2.example.com"],
    "algorithm": "ethash"
  },
  "Alerts": {
    "telegram_enabled": true,
    "discord_enabled": false
  }
}
```

---

## Performance Optimization

### Best Practices
1. **Monitor regularly**: Use Live Monitor for continuous oversight
2. **Optimize on schedule**: Run optimization 2-3 times daily
3. **Temperature management**: Keep avg below 80°C
4. **Diversify algorithms**: Rotate between profitable coins
5. **Regular maintenance**: Check logs for warnings

### Troubleshooting

#### App won't start
- Ensure Python 3.8+ is installed
- Run: `pip install -r requirements.txt`
- Check logs in `logs/` directory

#### Charts not displaying
- Verify matplotlib is installed: `pip install matplotlib`
- Check system permissions
- Restart application

#### Rigs not showing
- Verify mining configuration in settings.json
- Check network connectivity
- Review error logs

#### Alerts not sending
- Configure Telegram/Discord in settings.json
- Test alert with "🔔 Alerts" tab button
- Check API keys and permissions

---

## Data Management

### Backup
Automatic backups are created to `backups/` directory every hour.

### Export
Use File → Export Report to save metrics as JSON.

### Logs
System logs are stored in `logs/` with automatic rotation.

---

## Advanced Features

### Predictive Maintenance
- Monitors component health
- Predicts failures before they occur
- Recommends proactive actions

### Risk Management
- Stop-loss protection on losses
- Portfolio rebalancing
- Compliance monitoring

### Algorithm Switching
- Automatic profitability analysis
- Real-time algorithm switching
- Historical performance tracking

---

## Security

### Best Practices
- Keep API keys in settings.json (not in code)
- Use strong passwords for pool accounts
- Enable two-factor authentication where available
- Regularly backup configuration

### Data Privacy
- No data sent to external servers without consent
- All alerts configurable
- Local-only processing option available

---

## Support & Documentation

### Resources
- See `README.txt` for detailed information
- Check `API_SETUP_GUIDE.md` for API configuration
- Review `ALERT_CONFIG.md` for alert setup

### Reporting Issues
Create an issue on the GitHub repository with:
- Error message
- System configuration
- Steps to reproduce
- Recent logs (anonymized)

---

## Version History

### v3.0 (Current - Production Release)
- ✅ Complete UI redesign
- ✅ Real-time metrics and charts
- ✅ Multi-tab dashboard
- ✅ Advanced control panel
- ✅ System diagnostics
- ✅ Professional styling

### v2.0
- Initial desktop implementation
- Basic dashboard

### v1.0
- Console-only interface

---

## License & Credits

Autonomous Zenith Optimizer © 2025

Built for professional cryptocurrency mining operations with enterprise-grade reliability.

---

**Last Updated**: November 16, 2025
**Status**: ✅ Production Ready
