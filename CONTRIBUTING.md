# Contributing to Headscale Installation Guide

Thank you for your interest in contributing! This guide is community-driven and we welcome improvements.

## How to Contribute

### Reporting Issues

If you encounter any problems with the guide:
1. Check if the issue already exists in [Issues](../../issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Your environment (OS, VPS provider, etc.)
   - Any error messages

### Suggesting Improvements

Have an idea to improve the guide?
1. Open an issue describing your suggestion
2. Explain why this improvement would be valuable
3. If possible, provide examples

### Submitting Changes

1. **Fork the repository**
2. **Create a branch** for your changes:
   ```bash
   git checkout -b improvement/short-description
   ```
3. **Make your changes**:
   - Update both README.md (English) and README-FR.md (French)
   - Keep the style consistent
   - Test your instructions if possible
4. **Commit your changes**:
   ```bash
   git commit -m "Brief description of changes"
   ```
5. **Push to your fork**:
   ```bash
   git push origin improvement/short-description
   ```
6. **Open a Pull Request**

## Guidelines

### Documentation Style

- Use clear, concise language
- Provide code examples when relevant
- Include explanations for complex steps
- Keep both English and French versions in sync

### Code Examples

- Test all commands before submitting
- Use generic examples (avoid personal information)
- Include comments for clarity
- Specify which user should run the command (root, regular user)

### Privacy & Security

- **Never** include:
  - Personal domain names
  - IP addresses
  - API keys or passwords
  - Any personally identifiable information
- Use placeholder values like:
  - `vpn.example.com`
  - `YOUR_VPS_IP`
  - `YOUR_API_KEY`

## Questions?

If you have questions about contributing, feel free to open an issue!

---

Thank you for helping make this guide better! 🎉
