# Reporting Issues

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Contribute](../README.md) → Reporting Issues*

Found a bug or problem with Watchgate? This guide will help you report issues effectively so we can fix them quickly. Good issue reports help us understand the problem, reproduce it, and develop a solution.

## Before Reporting an Issue

### Check if it's Already Reported
Search existing issues to avoid duplicates:

1. **Visit the GitHub repository**
2. **Search open and closed issues** using relevant keywords
3. **Check recent discussions** in case it's been discussed
4. **Look at the troubleshooting guide** to see if there's a known solution

### Verify the Issue
Make sure you've encountered a genuine issue:

1. **Try with a minimal configuration** to isolate the problem
2. **Check the documentation** to ensure you're using Watchgate correctly
3. **Test with verbose logging** to get more information
4. **Try the latest version** to see if it's already fixed

## Types of Issues to Report

### Bugs
Unexpected behavior or errors in Watchgate:

- **Crashes or exceptions**: Watchgate stops working unexpectedly
- **Incorrect behavior**: Watchgate doesn't work as documented
- **Performance problems**: Slow response times or high resource usage
- **Configuration issues**: Valid configurations that don't work as expected

### Security Issues
**⚠️ Important**: For security vulnerabilities, use responsible disclosure:

- **Email first**: Contact the maintainers privately for security issues
- **Don't publish**: Don't create public issues for security vulnerabilities
- **Provide details**: Include impact assessment and reproduction steps
- **Wait for fix**: Allow time for fixes before public disclosure

### Documentation Issues
Problems with guides, tutorials, or reference materials:

- **Incorrect information**: Documentation that doesn't match actual behavior
- **Missing information**: Important details that aren't documented
- **Unclear explanations**: Confusing or ambiguous instructions
- **Broken links**: Links that don't work or point to wrong locations

### Installation and Setup Issues
Problems getting Watchgate running:

- **Installation failures**: Problems installing Watchgate
- **Dependency issues**: Problems with required dependencies
- **Configuration errors**: Issues with initial setup
- **Platform-specific problems**: Issues on specific operating systems

## Bug Report Template

Use this template for bug reports:

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Configuration
```yaml
# Your Watchgate configuration (remove sensitive information)
proxy:
  transport: stdio
  upstream:
    command: "your-mcp-server-command"

plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
```

## Error Messages
```
Paste any error messages here
```

## Logs
```
Paste relevant log entries here (use --verbose for detailed logs)
```

## Environment
- **Operating System**: (e.g., macOS 12.0, Ubuntu 20.04, Windows 11)
- **Python Version**: (output of `python --version`)
- **Watchgate Version**: (output of `watchgate --version`)
- **MCP Server**: (which MCP server you're using)
- **AI Client**: (Claude Desktop, custom client, etc.)

## Additional Context
Add any other context about the problem here.
```

## Effective Issue Reporting

### Provide Clear Descriptions
- **Use descriptive titles**: "Configuration validation fails with nested plugins" not "It doesn't work"
- **Explain the impact**: How does this affect your use of Watchgate?
- **Be specific**: Exact error messages, specific tools or files involved

### Include Reproduction Steps
The most helpful issues include clear steps to reproduce the problem:

```markdown
## Steps to Reproduce
1. Create a configuration file with content access control plugin
2. Set mode to "allowlist" with resources: ["public/*"]
3. Start Watchgate with: `watchgate --config config.yaml`
4. Try to access a file outside the public directory
5. Expected: Access denied message
6. Actual: Watchgate crashes with stack trace
```

### Provide Complete Context
Include all relevant information:

- **Full configuration files** (remove sensitive information like API keys)
- **Complete error messages** (not just the last line)
- **Relevant log entries** (use `--verbose` for detailed logs)
- **Environment details** (OS, Python version, etc.)

### Simplify When Possible
Try to create a minimal reproduction:

- **Start with basic configuration** and add complexity
- **Remove unnecessary plugins** to isolate the issue
- **Use simple test cases** rather than complex real-world scenarios
- **Test with sample data** instead of production data

## Issue Severity Guidelines

### Critical (P0)
- **Security vulnerabilities**: Could be exploited to cause harm
- **Data loss bugs**: Could cause data corruption or loss
- **Complete failure**: Watchgate doesn't start or work at all
- **Regression bugs**: Previously working features that now fail

### High (P1)
- **Major functionality broken**: Core features don't work as designed
- **Performance regressions**: Significant performance degradation
- **Incorrect security decisions**: Allow/deny decisions are wrong
- **Documentation critical errors**: Major inaccuracies in documentation

### Medium (P2)
- **Minor functionality issues**: Edge cases or less common scenarios
- **Usability problems**: Difficult to use but workarounds exist
- **Performance issues**: Noticeable but not severe slowdowns
- **Documentation improvements**: Clarity or completeness issues

### Low (P3)
- **Cosmetic issues**: UI or output formatting problems
- **Feature requests**: New functionality suggestions
- **Minor documentation**: Small typos or formatting issues
- **Enhancement suggestions**: Improvements to existing features

## What Happens After You Report

### Initial Response
- **Acknowledgment**: We'll acknowledge your issue within a few days
- **Triage**: We'll assign severity and priority labels
- **Clarification**: We may ask for additional information or clarification

### Investigation
- **Reproduction**: We'll try to reproduce the issue using your steps
- **Analysis**: We'll investigate the root cause
- **Impact assessment**: We'll determine who else might be affected

### Resolution
- **Fix development**: We'll develop and test a solution
- **Testing**: We'll verify the fix works and doesn't break other functionality
- **Release**: The fix will be included in the next appropriate release
- **Verification**: We'll ask you to verify the fix resolves your issue

## Common Issue Types and Tips

### Configuration Issues
- **Validate your YAML**: Use a YAML validator to check syntax
- **Check file paths**: Ensure all paths are correct and accessible
- **Test step by step**: Start with minimal config and add complexity
- **Use debug commands**: Try `watchgate debug config --validate`

### Plugin Issues
- **Check plugin names**: Ensure you're using correct plugin policy names
- **Verify priorities**: Make sure plugin priorities don't conflict
- **Test individually**: Try each plugin separately to isolate issues
- **Check plugin logs**: Look for plugin-specific error messages

### Performance Issues
- **Measure baseline**: Test without Watchgate to establish baseline
- **Profile configuration**: Try simpler configurations to identify bottlenecks
- **Check resource usage**: Monitor CPU, memory, and disk usage
- **Review log verbosity**: High verbosity can impact performance

### Connection Issues
- **Test upstream server**: Verify your MCP server works independently
- **Check command paths**: Ensure MCP server commands are correct
- **Verify permissions**: Check file and directory permissions
- **Try simple servers**: Test with basic MCP servers first

## Issue Lifecycle

### Open Issues
- **New**: Recently reported, awaiting triage
- **Triaged**: Priority assigned, awaiting investigation
- **In Progress**: Being actively worked on
- **Needs Info**: Waiting for additional information from reporter

### Closed Issues
- **Fixed**: Issue resolved and fix released
- **Duplicate**: Same as another issue
- **Invalid**: Not actually an issue with Watchgate
- **Won't Fix**: Issue acknowledged but won't be addressed

## Getting Help with Issues

### If You're Stuck
- **Ask in discussions**: The community might be able to help
- **Simplify your setup**: Try the most basic configuration first
- **Check similar issues**: See if others have reported similar problems
- **Review troubleshooting guide**: Common issues and solutions

### Following Up
- **Respond to questions**: Help us help you by answering clarification questions
- **Test proposed fixes**: Try beta releases or patches when available
- **Confirm resolution**: Let us know when fixes work for you
- **Close issues**: Close issues when they're resolved for you

Thank you for helping make Watchgate better by reporting issues! Your bug reports are essential for improving Watchgate's quality and reliability.
