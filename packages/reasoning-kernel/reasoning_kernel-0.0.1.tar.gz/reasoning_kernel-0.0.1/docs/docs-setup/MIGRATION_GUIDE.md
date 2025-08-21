# Migration Guide: Moving to Dedicated Documentation Repository

This guide will help you migrate the Reasoning Kernel documentation from the main repository to the new dedicated documentation repository.

## 🎯 Overview

We're moving from:

```
reasoning-kernel/docs/  →  qredence-docs/projects/reasoning-kernel/
```

This provides better organization, scalability, and separation of concerns.

## 📋 Step-by-Step Migration

### Step 1: Create New Repository

1. **Create `qredence-docs` repository on GitHub**:

   ```bash
   # On GitHub, create new repository: qredence/qredence-docs
   # Clone locally
   git clone https://github.com/qredence/qredence-docs.git
   cd qredence-docs
   ```

2. **Set up base structure**:

   ```bash
   # Copy the setup files we created
   cp -r /path/to/qredence-docs-setup/* ./
   
   # Create directory structure
   mkdir -p projects/reasoning-kernel/{concepts,api,sdk,examples,guides,integration,research}
   mkdir -p shared/{getting-started,development,deployment,community}
   mkdir -p templates assets/{images,logos,icons}
   mkdir -p .github/workflows
   ```

### Step 2: Copy Configuration Files

```bash
# Main Mintlify configuration
cp qredence-docs-setup/mint.json ./

# Main pages
cp qredence-docs-setup/introduction.mdx ./
cp qredence-docs-setup/projects.mdx ./
cp qredence-docs-setup/README.md ./
```

### Step 3: Migrate Reasoning Kernel Documentation

From your current Reasoning Kernel repository:

```bash
# Navigate to your current reasoning-kernel repo
cd /path/to/reasoning-kernel

# Copy existing documentation to new structure
cp docs/introduction.mdx /path/to/qredence-docs/projects/reasoning-kernel/
cp docs/quickstart.mdx /path/to/qredence-docs/projects/reasoning-kernel/
cp docs/installation.mdx /path/to/qredence-docs/projects/reasoning-kernel/
cp docs/configuration.mdx /path/to/qredence-docs/projects/reasoning-kernel/

# Copy concept files
cp docs/concepts/msa-framework.mdx /path/to/qredence-docs/projects/reasoning-kernel/concepts/
cp docs/concepts/thinking-exploration.mdx /path/to/qredence-docs/projects/reasoning-kernel/concepts/

# Copy API documentation
cp docs/api/overview.mdx /path/to/qredence-docs/projects/reasoning-kernel/api/

# Copy examples
cp docs/examples/basic-usage.mdx /path/to/qredence-docs/projects/reasoning-kernel/examples/

# Copy any existing guides, integration docs, etc.
cp -r docs/guides/ /path/to/qredence-docs/projects/reasoning-kernel/guides/ 2>/dev/null || true
cp -r docs/integration/ /path/to/qredence-docs/projects/reasoning-kernel/integration/ 2>/dev/null || true
cp -r docs/research/ /path/to/qredence-docs/projects/reasoning-kernel/research/ 2>/dev/null || true
```

### Step 4: Update File Paths in Documentation

Since files are now in `projects/reasoning-kernel/`, update internal links:

```bash
cd /path/to/qredence-docs

# Update links to reflect new structure
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/concepts/|href="/projects/reasoning-kernel/concepts/|g' {} \;
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/api/|href="/projects/reasoning-kernel/api/|g' {} \;
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/examples/|href="/projects/reasoning-kernel/examples/|g' {} \;
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/guides/|href="/projects/reasoning-kernel/guides/|g' {} \;
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/installation|href="/projects/reasoning-kernel/installation|g' {} \;
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/quickstart|href="/projects/reasoning-kernel/quickstart|g' {} \;
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|href="/configuration|href="/projects/reasoning-kernel/configuration|g' {} \;
```

### Step 5: Update Asset Paths

Move and update image/asset references:

```bash
# Create assets directory structure
mkdir -p assets/images/reasoning-kernel assets/logos assets/icons

# Copy existing images (if any)
cp docs/images/* assets/images/reasoning-kernel/ 2>/dev/null || true

# Update image paths in documentation
find projects/reasoning-kernel/ -name "*.mdx" -exec sed -i '' 's|src="/images/|src="/assets/images/reasoning-kernel/|g' {} \;
```

### Step 6: Create Shared Resources

Create shared documentation that applies to all projects:

```bash
# Create shared getting started guide
cat > shared/getting-started/overview.mdx << 'EOF'
---
title: "Getting Started with Qredence"
description: "Universal getting started guide for all Qredence projects and technologies."
---

# Getting Started with Qredence

Welcome to Qredence! This guide will help you get started with any of our projects and technologies.

## Choose Your Project

<CardGroup cols={2}>
  <Card title="Reasoning Kernel" icon="brain" href="/projects/reasoning-kernel/introduction">
    Advanced AI reasoning system with Model Synthesis Architecture
  </Card>
  <Card title="Browse All Projects" icon="folder" href="/projects">
    Explore all available Qredence projects and tools
  </Card>
</CardGroup>

## Universal Setup

### Prerequisites
- **Python 3.12+** for Python-based projects
- **Node.js 18+** for JavaScript-based projects
- **Git** for version control
- **Docker** (optional) for containerized deployment

### Development Environment
[Include common setup instructions here]
EOF

# Create development standards
cat > shared/development/standards.mdx << 'EOF'
---
title: "Development Standards"
description: "Shared development standards and best practices across all Qredence projects."
---

# Development Standards

Common standards and practices used across all Qredence projects.

## Code Quality
- Follow PEP 8 for Python projects
- Use type hints for all public APIs
- Maintain 90%+ test coverage
- Use Black for code formatting

## Documentation
- Write clear, concise documentation
- Include practical examples
- Keep documentation up-to-date with code changes
- Use consistent terminology

[Continue with full standards...]
EOF
```

### Step 7: Create Templates

Create templates for future project documentation:

```bash
cat > templates/project-template.mdx << 'EOF'
---
title: "Project Name"
description: "Brief description of what this project does and its main value proposition."
---

# Project Name

Brief introduction to the project, its purpose, and key benefits.

## Key Features

<CardGroup cols={2}>
  <Card title="Feature 1" icon="icon-name">
    Description of first key feature
  </Card>
  <Card title="Feature 2" icon="icon-name">
    Description of second key feature
  </Card>
</CardGroup>

## Quick Start

[Basic getting started steps]

## Next Steps

<CardGroup cols={2}>
  <Card title="Installation" href="/projects/project-name/installation">
    Complete installation guide
  </Card>
  <Card title="Examples" href="/projects/project-name/examples/basic-usage">
    Real-world usage examples
  </Card>
</CardGroup>
EOF
```

### Step 8: Set Up CI/CD

Create GitHub workflow for automatic deployment:

```bash
mkdir -p .github/workflows

cat > .github/workflows/deploy.yml << 'EOF'
name: Deploy Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install Mintlify
        run: npm install -g mintlify

      - name: Deploy to Mintlify (on main)
        if: github.ref == 'refs/heads/main'
        run: mintlify deploy
        env:
          MINTLIFY_API_KEY: ${{ secrets.MINTLIFY_API_KEY }}

      - name: Build (on PR)
        if: github.event_name == 'pull_request'
        run: mintlify build
EOF
```

### Step 9: Test Migration

```bash
# Install Mintlify CLI
npm install -g mintlify

# Test the documentation locally
cd /path/to/qredence-docs
mintlify dev

# Open browser to http://localhost:3000
# Verify all links work and content displays correctly
```

### Step 10: Update Original Repository

In your original Reasoning Kernel repository:

```bash
# Remove the docs directory (after confirming migration worked)
rm -rf docs/

# Create a simple README redirect
cat > DOCUMENTATION.md << 'EOF'
# Documentation

📚 **Documentation has moved!**

The comprehensive documentation for the Reasoning Kernel is now available at:

**https://docs.qredence.com/projects/reasoning-kernel**

## Quick Links

- [Quick Start](https://docs.qredence.com/projects/reasoning-kernel/quickstart)
- [Installation Guide](https://docs.qredence.com/projects/reasoning-kernel/installation)
- [API Reference](https://docs.qredence.com/projects/reasoning-kernel/api/overview)
- [Examples](https://docs.qredence.com/projects/reasoning-kernel/examples/basic-usage)

## Local Development

To contribute to the documentation:

1. Visit the [qredence-docs repository](https://github.com/qredence/qredence-docs)
2. Follow the contribution guidelines
3. Submit pull requests for documentation improvements

---

For questions about the documentation, please visit our [Discord community](https://discord.gg/qredence) or create an issue in the [documentation repository](https://github.com/qredence/qredence-docs/issues).
EOF

# Update main README to point to new docs
# Add link to documentation in your main README.md
```

## ✅ Post-Migration Checklist

- [ ] New repository created and cloned
- [ ] All documentation files copied to new structure
- [ ] Internal links updated to reflect new paths
- [ ] Asset paths updated for images and resources
- [ ] Shared resources created
- [ ] Templates created for future projects
- [ ] CI/CD workflow configured
- [ ] Local testing completed successfully
- [ ] Original repository updated with redirect
- [ ] Team notified about new documentation location

## 🔧 Configuration Updates

### Update Mintlify Configuration

Ensure your `mint.json` has the correct navigation structure for the migrated content:

```json
{
  "navigation": [
    {
      "group": "Reasoning Kernel",
      "pages": [
        "projects/reasoning-kernel/introduction",
        "projects/reasoning-kernel/quickstart",
        "projects/reasoning-kernel/installation",
        "projects/reasoning-kernel/configuration",
        {
          "group": "Core Concepts",
          "pages": [
            "projects/reasoning-kernel/concepts/msa-framework",
            "projects/reasoning-kernel/concepts/thinking-exploration"
          ]
        }
        // ... add all migrated pages
      ]
    }
  ]
}
```

### Set Up Analytics

Configure analytics in `mint.json`:

```json
{
  "analytics": {
    "gtag": {
      "measurementId": "G-XXXXXXXXXX"
    },
    "posthog": {
      "apiKey": "your-posthog-api-key"
    }
  }
}
```

## 🚀 Benefits After Migration

### ✅ **Improved Organization**

- Clear separation between code and documentation
- Better scalability for multiple projects
- Consistent documentation structure

### ✅ **Better User Experience**

- Unified documentation hub for all projects
- Improved discoverability and navigation
- Professional appearance and branding

### ✅ **Enhanced Maintenance**

- Centralized documentation management
- Shared templates and standards
- Easier collaboration and review processes

### ✅ **SEO and Analytics**

- Better SEO with dedicated domain
- Comprehensive analytics across all projects
- Improved search functionality

## 🤝 Team Communication

### Notify Your Team

Send a communication like this to your team:

```
📚 Documentation Migration Complete!

We've successfully migrated our documentation to a dedicated repository for better organization and scalability.

🔗 New Documentation URL: https://docs.qredence.com
📖 Reasoning Kernel Docs: https://docs.qredence.com/projects/reasoning-kernel

What changed:
✅ Better organization and navigation
✅ Professional appearance with Mintlify
✅ Improved search and discoverability
✅ Foundation for documenting future projects

For contributors:
- Documentation contributions now go to: github.com/qredence/qredence-docs
- Follow the new contribution guidelines in the repo
- Use templates for consistent documentation

Questions? Join our Discord or create an issue in the docs repository.
```

## 🔄 Ongoing Maintenance

### Regular Tasks

1. **Content Updates**: Keep documentation in sync with code changes
2. **Link Checking**: Verify all internal and external links work
3. **Analytics Review**: Monitor usage and identify popular content
4. **User Feedback**: Collect and act on user suggestions
5. **Template Updates**: Improve templates based on experience

### Quality Assurance

- Set up automated link checking
- Regular content audits for accuracy
- Monitor search queries to identify gaps
- Collect user feedback through surveys

---

Your documentation is now ready for a professional, scalable future! 🎉
