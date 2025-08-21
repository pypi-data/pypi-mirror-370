# MSA Reasoning Kernel CLI Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using the MSA Reasoning Kernel CLI. Each section addresses a specific problem with step-by-step instructions for resolution.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [API Connection Errors](#api-connection-errors)
4. [Performance Issues](#performance-issues)
5. [Session and History Problems](#session-and-history-problems)
6. [Export and Batch Processing Issues](#export-and-batch-processing-issues)
7. [Sandbox Execution Problems](#sandbox-execution-problems)
8. [General Troubleshooting Tips](#general-troubleshooting-tips)

## Installation Issues

### Problem: Installation fails with dependency conflicts

**Symptoms:**

- Error messages about conflicting package versions
- Installation process hangs or fails

**Solutions:**

1. Ensure you're using Python 3.10+ (but not 3.13+ yet)
2. Use a virtual environment:

   ```bash
   uv venv && source .venv/bin/activate
   ```

3. Try installing with pip instead of uv:

   ```bash
   pip install -e ".[azure,google]"
   ```

4. Clear pip cache and try again:

   ```bash
   pip cache purge
   pip install -e ".[azure,google]"
   ```

### Problem: CLI command not found

**Symptoms:**

- `reasoning-kernel: command not found`
- Command works in one terminal but not another

**Solutions:**

1. Verify the virtual environment is activated:

   ```bash
   source .venv/bin/activate
   ```

2. Check if the package was installed in development mode:

   ```bash
   pip show reasoning-kernel
   ```

3. Add the virtual environment's bin directory to your PATH:

   ```bash
   export PATH="$PATH:/path/to/your/venv/bin"
   ```

## Configuration Problems

### Problem: Environment variables not recognized

**Symptoms:**

- API key errors despite setting environment variables
- Configuration values not taking effect

**Solutions:**

1. Verify environment variables are set:

   ```bash
   echo $AZURE_OPENAI_API_KEY
   ```

2. Ensure variables are exported in your shell session:

   ```bash
   export AZURE_OPENAI_API_KEY="your-key"
   ```

3. Check for typos in variable names
4. Use the configuration wizard to set values:

   ```bash
   reasoning-kernel wizard run
   ```

### Problem: Configuration file issues

**Symptoms:**

- Configuration changes not taking effect
- Error messages about configuration files

**Solutions:**

1. Check the default configuration file location:

   ```bash
   cat ~/.reasoning_kernel/config.json
   ```

2. Validate JSON syntax in configuration files
3. Reset to default configuration:

   ```bash
   reasoning-kernel config show --verbose
   ```

## API Connection Errors

### Problem: Azure OpenAI API connection fails

**Symptoms:**

- "Authentication failed" or "Invalid API key" errors
- "Endpoint not found" errors
- Connection timeout errors

**Solutions:**

1. Verify your Azure OpenAI credentials:

   ```bash
   echo $AZURE_OPENAI_ENDPOINT
   echo $AZURE_OPENAI_API_KEY
   echo $AZURE_OPENAI_DEPLOYMENT
   ```

2. Test the endpoint directly with curl:

   ```bash
   curl -X GET $AZURE_OPENAI_ENDPOINT/openai/deployments/$AZURE_OPENAI_DEPLOYMENT/completions?api-version=$AZURE_OPENAI_API_VERSION \
   -H "api-key: $AZURE_OPENAI_API_KEY"
   ```

3. Check Azure portal for deployment status
4. Ensure your API key has the correct permissions

### Problem: Google AI API connection fails

**Symptoms:**

- "Invalid API key" errors for Google AI
- Gemini model not accessible

**Solutions:**

1. Verify your Google AI API key:

   ```bash
   echo $GOOGLE_AI_API_KEY
   ```

2. Check that the Gemini model is available in your region
3. Ensure your API key has the correct permissions

## Performance Issues

### Problem: Slow response times

**Symptoms:**

- Long delays between command execution and response
- Timeouts during processing

**Solutions:**

1. Check your internet connection
2. Verify API endpoint responsiveness:

   ```bash
   ping $AZURE_OPENAI_ENDPOINT
   ```

3. Use verbose mode to identify bottlenecks:

   ```bash
   reasoning-kernel --verbose "Your query"
   ```

4. Consider using a faster model deployment if available

### Problem: High memory usage

**Symptoms:**

- System becomes unresponsive during processing
- "Out of memory" errors

**Solutions:**

1. Reduce the complexity of your queries
2. Process large batches in smaller chunks
3. Monitor system resources:

   ```bash
   top
   ```

4. Consider upgrading your system's RAM

## Session and History Problems

### Problem: Sessions not saving or loading

**Symptoms:**

- "Session not found" errors
- Session data appears to be lost

**Solutions:**

1. Check session directory permissions:

   ```bash
   ls -la ~/.reasoning_kernel/sessions/
   ```

2. List available sessions to verify they exist:

   ```bash
   reasoning-kernel session list
   ```

3. Check disk space:

   ```bash
   df -h
   ```

### Problem: History not recording

**Symptoms:**

- History commands return empty results
- Previous queries not showing in history

**Solutions:**

1. Check history file permissions:

   ```bash
   ls -la ~/.reasoning_kernel/history.json
   ```

2. Verify history file is not corrupted:

   ```bash
   cat ~/.reasoning_kernel/history.json | jq .
   ```

3. Reset history if corrupted:

   ```bash
   reasoning-kernel history clear --force
   ```

## Export and Batch Processing Issues

### Problem: Export fails with format errors

**Symptoms:**

- "Export failed" messages
- Output files are empty or corrupted

**Solutions:**

1. Check available disk space:

   ```bash
   df -h
   ```

2. Verify output directory permissions:

   ```bash
   ls -la /path/to/output/directory
   ```

3. For PDF export, ensure weasyprint is installed:

   ```bash
   pip install weasyprint
   ```

4. Check that the session or history data exists:

   ```bash
   reasoning-kernel session list
   ```

### Problem: Batch processing fails

**Symptoms:**

- "Invalid input file" errors
- Batch processing stops partway through

**Solutions:**

1. Validate JSON syntax in batch file:

   ```bash
   cat batch_queries.json | jq .
   ```

2. Check that all required fields are present in batch file
3. Ensure input file encoding is UTF-8
4. Process smaller batches to isolate problematic queries

## Sandbox Execution Problems

### Problem: Daytona sandbox connection fails

**Symptoms:**

- "Sandbox not available" errors
- Sandbox execution timeouts

**Solutions:**

1. Verify Daytona API key and URL:

   ```bash
   reasoning-kernel config daytona --show
   ```

2. Check Daytona service status
3. Test sandbox connectivity:

   ```bash
   reasoning-kernel sandbox status
   ```

4. Check firewall settings that might block sandbox connections

### Problem: Sandbox execution timeouts

**Symptoms:**

- "Execution timeout" errors
- Sandbox processes terminate prematurely

**Solutions:**

1. Increase timeout settings:

   ```bash
   reasoning-kernel config set execution_timeout 300
   ```

2. Optimize code for faster execution
3. Break complex tasks into smaller steps
4. Check resource limits in sandbox configuration

## General Troubleshooting Tips

### Enable Verbose Logging

For detailed information about what the CLI is doing, enable verbose logging:

```bash
reasoning-kernel --verbose "Your query"
# or
reasoning-kernel -v "Your query"
```

### Check CLI Version

Verify you're using the latest version:

```bash
reasoning-kernel --version
```

### Get Help

For help with any command, use the `--help` flag:

```bash
reasoning-kernel --help
reasoning-kernel reason --help
reasoning-kernel analyze --help
```

### Report Issues

If you encounter issues that you cannot resolve:

1. Check the GitHub repository for known issues
2. Include the following information when reporting:
   - CLI version (`reasoning-kernel --version`)
   - Error message
   - Steps to reproduce
   - Environment information (OS, Python version, etc.)
   - Verbose logs if applicable

### Update the CLI

Ensure you're using the latest version:

```bash
git pull
pip install -e ".[azure,google]"
```

### Clear Cache

If experiencing persistent issues, try clearing any cached data:

```bash
# Clear pip cache
pip cache purge

# Clear any application-specific cache
rm -rf ~/.reasoning_kernel/cache/
```

This troubleshooting guide covers the most common issues users may encounter with the MSA Reasoning Kernel CLI. If you continue to experience problems after trying these solutions, please consult the project's GitHub issues or contact support.
