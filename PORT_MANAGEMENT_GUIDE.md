# 🔧 Port Management Guide

## Overview

This guide covers all the tools available to manage port conflicts and service startup issues.

---

## 🚀 Quick Solutions

### **Option 1: Automatic Resolution (Recommended)**
```bash
# Just run the startup script - it will detect and resolve conflicts:
start_all.bat
```

The improved startup script now:
- ✅ **Detects port conflicts** automatically
- ✅ **Shows which ports are in use**
- ✅ **Offers 4 resolution options**:
  1. Kill existing services and restart (Recommended)
  2. Start services anyway (will show errors)
  3. Exit and check manually
  4. Show detailed port information

### **Option 2: Quick Conflict Resolver**
```bash
# Run this for immediate port conflict resolution:
resolve_port_conflicts.bat
```

This script:
- 🔍 **Detects all port conflicts**
- 🛑 **Kills processes on conflicting ports**
- ✅ **Verifies ports are now available**
- 💡 **Provides next steps**

### **Option 3: Full Port Management**
```bash
# Advanced port management with menu options:
manage_ports.bat
```

Features:
- 📋 **Check port status**
- 🛑 **Stop all services**
- 🎯 **Stop specific port**
- 📊 **Show detailed information**
- ⚡ **Force kill all Python/Node processes**

---

## 📋 Available Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **`start_all.bat`** | Start all services with conflict detection | Normal startup |
| **`resolve_port_conflicts.bat`** | Quick port conflict resolution | When you get port errors |
| **`manage_ports.bat`** | Full port management | Advanced troubleshooting |
| **`stop_all.bat`** | Stop all services cleanly | Manual service shutdown |
| **`fix_port_conflict.bat`** | Legacy port 8001 fix | Simple port 8001 issues |

---

## 🔍 Port Information

### **Service Ports**
- **Port 8000**: Main Backend (Core API and file management)
- **Port 8001**: Online Agent Service (AI agent workflows)
- **Port 3000**: Frontend (React web interface)

### **Common Port Conflicts**
- **Error 10048**: "Only one usage of each socket address is normally permitted"
- **Cause**: Previous service instance still running
- **Solution**: Use any of the port management tools above

---

## 🛠️ Detailed Usage

### **1. start_all.bat (Enhanced)**

When you run this, it will:

1. **Check all ports** (8000, 8001, 3000)
2. **Count conflicts** and show status
3. **If conflicts found**, show menu:
   ```
   ⚠️ PORT CONFLICTS DETECTED (2 port(s) in use)
   
   🔧 Choose an option:
      1. Kill existing services and restart (Recommended)
      2. Start services anyway (will show errors)
      3. Exit and check manually
      4. Show detailed port information
   ```

4. **Option 1** (Recommended):
   - Kills processes on all conflicting ports
   - Shows detailed kill process
   - Waits for ports to be released
   - Verifies ports are now free
   - Proceeds with startup

### **2. resolve_port_conflicts.bat**

Quick and focused conflict resolution:

1. **Detects conflicts** on ports 8000, 8001, 3000
2. **Shows which ports** are in use
3. **Offers resolution methods**:
   - Kill processes on conflicting ports
   - Force kill all Python/Node processes
   - Show detailed information
4. **Verifies resolution** and reports success

### **3. manage_ports.bat**

Full-featured port management with menu:

```
🔧 Choose an option:
   1. Check port status
   2. Stop all services (kill processes on ports 8000, 8001, 3000)
   3. Stop specific port
   4. Show detailed port information
   5. Force kill all Python/Node processes
   6. Exit
```

**Features**:
- **Check port status**: Shows which ports are in use
- **Stop all services**: Kills all processes on service ports
- **Stop specific port**: Target individual ports
- **Show detailed info**: Complete port and process information
- **Force kill all**: Nuclear option for stubborn processes

---

## 🔧 Manual Commands

If you prefer manual control:

### **Check Port Status**
```bash
# Check specific ports:
netstat -an | findstr ":8000"  # Main Backend
netstat -an | findstr ":8001"  # Online Agent Service
netstat -an | findstr ":3000"  # Frontend

# Check all ports at once:
netstat -an | findstr ":800"
netstat -an | findstr ":3000"
```

### **Kill Processes by Port**
```bash
# Find process ID on port 8001:
netstat -aon | findstr ":8001"

# Kill specific process (replace PID with actual ID):
taskkill /f /pid 1234
```

### **Kill All Python/Node Processes**
```bash
# Kill all Python processes:
taskkill /f /im python.exe

# Kill all Node.js processes:
taskkill /f /im node.exe
```

---

## 🚨 Troubleshooting

### **"Access Denied" When Killing Processes**
**Cause**: Process requires administrator privileges

**Solutions**:
1. **Run as Administrator**: Right-click Command Prompt → "Run as administrator"
2. **Use force kill**: The scripts use `/f` flag for force kill
3. **Restart computer**: Nuclear option if processes are stuck

### **Ports Still in Use After Killing**
**Cause**: Process didn't release port immediately

**Solutions**:
1. **Wait longer**: Scripts wait 2-3 seconds, you may need more
2. **Check for zombie processes**: Use Task Manager to verify
3. **Restart computer**: If all else fails

### **Multiple Python/Node Processes**
**Cause**: Multiple instances running

**Solutions**:
1. **Use force kill all**: `manage_ports.bat` option 5
2. **Check Task Manager**: Look for multiple python.exe or node.exe
3. **Restart computer**: Clean slate approach

---

## 🎯 Best Practices

### **Before Starting Services**
1. **Check for conflicts**: Run `manage_ports.bat` option 1
2. **Clean up if needed**: Use appropriate resolution method
3. **Start with clean slate**: Ensure all ports are available

### **When You Get Port Errors**
1. **Don't panic**: Port conflicts are common and easily fixed
2. **Use the tools**: Don't manually kill processes unless necessary
3. **Follow the prompts**: The scripts guide you through resolution

### **Regular Maintenance**
1. **Stop services properly**: Use `stop_all.bat` when done
2. **Check for zombie processes**: Occasionally run port status check
3. **Keep tools updated**: Use the latest versions of startup scripts

---

## 📞 Quick Reference

### **Emergency Port Cleanup**
```bash
# Quick fix for any port conflict:
resolve_port_conflicts.bat
```

### **Full Service Management**
```bash
# Start everything with conflict detection:
start_all.bat

# Stop everything cleanly:
stop_all.bat
```

### **Advanced Troubleshooting**
```bash
# Full port management:
manage_ports.bat
```

---

## 🎉 Success Indicators

When everything is working correctly:

✅ **All ports available** (8000, 8001, 3000)  
✅ **Services start without errors**  
✅ **No "port already in use" messages**  
✅ **Frontend loads at http://localhost:3000**  
✅ **Backend APIs respond**  
✅ **GitHub auto-upload works**  

**You're ready to use the AI agent system!** 🚀
