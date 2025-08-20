# iamx - IAM Policy Explainer

A local-first IAM policy analyzer that scans AWS IAM JSON policies, detects risky patterns deterministically, explains them in plain English, assigns severity levels, and suggests least-privilege fixes.

## 🎯 Why iamx?

Copy-pasting IAM policies into ChatGPT is unsafe, inaccurate, and doesn't scale for bulk analysis. Manual policy review is time-consuming and error-prone.

**iamx solves these problems:**
- ✅ **Accuracy first** - Static parser + deterministic rules (no hallucinations)
- ✅ **Human-readable explanations** - Plain English descriptions of risks
- ✅ **Bulk scanning** - Process multiple policies efficiently
- ✅ **CI/CD integration** - GitHub Actions with configurable thresholds
- ✅ **Privacy-first** - Local by default, optional AI summaries
- ✅ **Multiple outputs** - Markdown, JSON, and interactive web reports

## 🚀 Features

### Core Analysis
- **Deterministic pattern detection** - No AI hallucinations, consistent results
- **Risk severity classification** - Critical/High/Medium/Low based on impact
- **Plain English explanations** - Understandable descriptions of each finding
- **Least-privilege suggestions** - Specific recommendations for policy improvements

### Supported Patterns
- Overly permissive actions (`*` permissions)
- Wildcard resources without restrictions
- Cross-account access patterns
- Administrative actions detection
- Data access actions analysis
- Missing resource restrictions
- Sensitive service permissions

### Output Formats
- **CLI** - Terminal output with color-coded results
- **Web UI** - Interactive local web interface
- **Markdown** - Detailed reports for documentation
- **JSON** - Machine-readable output for CI/CD
- **GitHub Actions** - Automated policy reviews in PRs

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/iamx.git
cd iamx

# Install dependencies
pip install -e .

# Or install directly from PyPI (when published)
pip install iamx
```

## 📖 Quick Start

### CLI Usage

```bash
# Analyze a single policy file
iamx analyze policy.json

# Analyze multiple policies
iamx analyze policies/*.json

# Generate detailed report
iamx analyze policy.json --output report.md --format markdown

# Set severity threshold for CI
iamx analyze policy.json --fail-on high
```

### Web UI

```bash
# Start the local web interface
iamx web

# Open http://localhost:8080 in your browser
```

### GitHub Actions Integration

```yaml
name: IAM Policy Review
on: [pull_request]
jobs:
  iamx:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run iamx
        uses: yourusername/iamx-action@v1
        with:
          path: 'policies/'
          fail-on: 'high'
          output: 'iamx-report.md'
```

## 📊 Example Output

```
🔍 Analyzing IAM Policy: admin-policy.json

❌ CRITICAL: Overly Permissive Actions
   The policy grants '*' permissions on all resources for ec2:* actions.
   This allows full EC2 control including instance termination and data access.
   
   Recommendation: Replace with specific actions like:
   - ec2:DescribeInstances
   - ec2:StartInstances
   - ec2:StopInstances

⚠️  HIGH: Missing Resource Restrictions
   The policy allows s3:GetObject on any S3 bucket without restrictions.
   This could expose sensitive data across all buckets.
   
   Recommendation: Add resource ARN restrictions:
   "Resource": "arn:aws:s3:::my-bucket/*"

✅ LOW: Consider Adding Conditions
   The policy doesn't require MFA for administrative actions.
   
   Recommendation: Add MFA condition for sensitive operations.
```

## 🏗️ Architecture

```
iamx/
├── core/           # Core analysis engine
├── cli/            # Command-line interface
├── web/            # Web UI components
├── rules/          # Policy analysis rules
├── reports/        # Report generators
├── github/         # GitHub Actions integration
└── tests/          # Test suite
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/iamx.git
cd iamx
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
flake8 .
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with modern Python tooling and best practices
- Designed for the security and DevOps community
- Inspired by the need for better IAM policy analysis tools
